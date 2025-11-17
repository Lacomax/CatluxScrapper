#!/usr/bin/env python3
"""
CatLux PDF Downloader with Download Tracking & Preview
=======================================================

Script para descargar documentos de exámenes de CatLux (https://www.catlux.de)
con control de límite mensual de descargas (100 PDFs/mes), preview de categorías
y evitar duplicados.

Características:
- Preview de PDFs encontrados ANTES de descargar (modo dry-run)
- Categorías de PDFs: Schulart, Klasse, Fach, Dokument-Art
- Trackea el número de descargas (solo cuenta nuevos PDFs)
- Limita a 100 descargas por mes calendario
- Solo descarga examen + solución si no existen ya
- Muestra el saldo de descargas disponibles
- Multiplataforma (Windows, macOS, Linux)
- Credenciales seguras en archivo .env

Requisitos:
    pip install requests beautifulsoup4 python-dotenv

Uso:
    python catlux_scrapper.py --url "..." --preview  # Ver qué se descargará
    python catlux_scrapper.py --url "..." --download  # Descargar
    python catlux_scrapper.py --info  # Ver saldo
    python catlux_scrapper.py --latest-downloads  # Ver últimas descargas en CatLux

Autor: Mejorado para control de descargas y preview
"""

import json
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, date
from urllib.parse import urljoin, urlparse, parse_qs
from typing import Dict, Tuple, Optional, List
import argparse
from collections import defaultdict
import re

try:
    import requests
    from bs4 import BeautifulSoup
    from dotenv import load_dotenv
    # Desactivar advertencias de SSL (CatLux usa certificado auto-firmado)
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    print("Error: Dependencias faltantes. Ejecuta:")
    print("  pip install requests beautifulsoup4 python-dotenv urllib3")
    sys.exit(1)

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

load_dotenv()

DOWNLOADS_PER_MONTH = 100
TRACKER_FILE = Path(__file__).parent / "download_tracker.json"
LOG_FILE = Path(__file__).parent / "catlux_scrapper.log"
LOGIN_URL = "https://www.catlux.de/login"
PROFILE_URL = "https://www.catlux.de/mein-profil"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CLASES DE TRACKING Y GESTIÓN
# ============================================================================

class DownloadTracker:
    """Gestiona el seguimiento de descargas mensuales."""

    def __init__(self, tracker_file: Path):
        """Inicializa el tracker de descargas."""
        self.tracker_file = tracker_file
        self.data = self._load_tracker()

    def _load_tracker(self) -> Dict:
        """Carga el archivo de tracking o crea uno nuevo."""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Error cargando tracker: {e}. Creando nuevo.")
                return {"downloads": [], "total_all_time": 0}
        return {"downloads": [], "total_all_time": 0}

    def _save_tracker(self) -> None:
        """Guarda el estado actual del tracker."""
        self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tracker_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_current_month_downloads(self) -> int:
        """Retorna el número de descargas en el mes actual."""
        today = date.today()
        current_month = f"{today.year}-{today.month:02d}"
        return sum(
            1 for download in self.data.get("downloads", [])
            if download.get("date", "").startswith(current_month)
        )

    def get_remaining_downloads(self) -> int:
        """Retorna el número de descargas disponibles este mes."""
        current = self.get_current_month_downloads()
        return max(0, DOWNLOADS_PER_MONTH - current)

    def record_download(self, filename: str) -> None:
        """Registra una descarga nueva."""
        self.data["downloads"].append({
            "date": datetime.now().isoformat(),
            "filename": filename
        })
        self.data["total_all_time"] = self.data.get("total_all_time", 0) + 1
        self._save_tracker()

    def print_status(self) -> None:
        """Imprime el estado actual del tracker."""
        today = date.today()
        current = self.get_current_month_downloads()
        remaining = self.get_remaining_downloads()
        total = self.data.get("total_all_time", 0)

        print("\n" + "=" * 60)
        print("📊 ESTADO DE DESCARGAS")
        print("=" * 60)
        print(f"Mes actual: {today.strftime('%B %Y')}")
        print(f"Descargas este mes: {current}/{DOWNLOADS_PER_MONTH}")
        print(f"Descargas disponibles: {remaining}")
        print(f"Total histórico: {total}")

        if remaining == 0:
            print("\n⚠️  LÍMITE ALCANZADO - No se puede descargar más este mes")
        elif remaining <= 10:
            print(f"\n⚠️  Cuidado: Solo quedan {remaining} descargas")
        else:
            print(f"\n✅ {remaining} descargas disponibles")
        print("=" * 60 + "\n")


class PDFManager:
    """Gestiona la búsqueda y listado de PDFs."""

    def __init__(self, session: requests.Session, cert_path: Optional[str] = None):
        """
        Inicializa el gestor de PDFs.

        Args:
            session: Sesión de requests autenticada
            cert_path: Ruta al certificado SSL (opcional)
        """
        self.session = session
        self.cert_path = cert_path
        self.kwargs = {"verify": cert_path} if cert_path else {}

    def fetch_pdfs(self, base_url: str, max_pages: int = 10) -> List[Dict]:
        """
        Obtiene la lista de PDFs de una URL.

        Soporta dos tipos de páginas:
        1. Páginas de categoría: /klasse-7/deutsch/
        2. Páginas de búsqueda: /klasse-7/deutsch/aufsatz

        Estrategia: Extraer data-id de cada contenedor doc item list row
        y construir directamente los URLs de descarga

        Args:
            base_url: URL base de la clase
            max_pages: Máximo de páginas a procesar

        Returns:
            Lista de diccionarios con información de PDFs
        """
        pdfs = []
        found_docs = set()  # Para evitar duplicados

        for page_num in range(1, max_pages + 1):
            url = f"{base_url}?p={page_num}"
            logger.info(f"Buscando en: {url}")

            try:
                # Desactivar verificación SSL para CatLux
                response = self.session.get(url, verify=False, timeout=10)
                response.raise_for_status()
            except Exception as e:
                logger.error(f"Error descargando página {page_num}: {e}")
                break

            soup = BeautifulSoup(response.content, "html.parser")

            # Buscar contenedores de documentos (div con clase "doc item list row")
            doc_containers = soup.find_all('div', class_=lambda x: x and 'doc' in str(x) and 'item' in str(x))

            if not doc_containers:
                logger.info(f"No hay documentos en página {page_num}")
                break

            for container in doc_containers:
                try:
                    # Extraer información del contenedor
                    first_link = container.find('a', {'data-id': True})
                    if not first_link:
                        logger.warning(f"No se encontró data-id en contenedor")
                        continue

                    doc_id = first_link.get('data-id')
                    if not doc_id:
                        continue

                    # Extraer metadatos del contenedor
                    # Tipo/Categoría: buscar el label con clase "label label-default pull-right"
                    label_elem = container.find('span', class_=lambda x: x and 'label' in str(x) and 'label-default' in str(x))
                    doc_type = label_elem.get_text(strip=True) if label_elem else "Documento"

                    # ID real del documento (el número con #)
                    id_elem = container.find('span', class_=lambda x: x and 'text-muted' in str(x))
                    doc_number = id_elem.get_text(strip=True) if id_elem else f"#{doc_id}"

                    # Título del documento
                    title_elem = container.find('h2')
                    doc_title = title_elem.get_text(strip=True) if title_elem else ""

                    # Crear PDFs para examen y solución
                    pdf_types = [
                        {'name': doc_id, 'is_solution': False, 'dl_param': 'pdf'},
                        {'name': f"{doc_id}_solution", 'is_solution': True, 'dl_param': 'pdf_solution'}
                    ]

                    for pdf_info in pdf_types:
                        pdf_name = pdf_info['name']

                        # Evitar duplicados
                        if pdf_name in found_docs:
                            continue

                        found_docs.add(pdf_name)

                        # Construir URL de descarga
                        href = f"probe/{doc_id}?dl={pdf_info['dl_param']}"
                        full_url = urljoin("https://www.catlux.de/", href)

                        pdfs.append({
                            'name': pdf_name,
                            'url': href,
                            'full_url': full_url,
                            'is_solution': pdf_info['is_solution'],
                            'doc_id': doc_id,
                            'doc_number': doc_number,
                            'doc_type': doc_type,
                            'doc_title': doc_title,
                            'text': container.get_text(strip=True)[:100]
                        })

                except Exception as e:
                    logger.warning(f"Error procesando contenedor: {e}")
                    continue

        return pdfs

    def group_by_category(self, pdfs: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Agrupa PDFs por tipo (examen/solución).

        Args:
            pdfs: Lista de PDFs

        Returns:
            Diccionario agrupado
        """
        grouped = defaultdict(list)

        for pdf in pdfs:
            if pdf['is_solution']:
                exam_name = pdf['name'].replace('_solution', '')
                key = f"{exam_name} (solución)"
            else:
                key = pdf['name']

            grouped[key].append(pdf)

        return dict(grouped)

    def print_preview(self, pdfs: List[Dict], base_url: str, save_path: Optional[Path] = None) -> None:
        """
        Imprime preview de PDFs encontrados con títulos, categorías y estado local.
        Muestra cada PDF (examen y solución) como documentos independientes, ordenados por REF.

        Args:
            pdfs: Lista de PDFs
            base_url: URL base para contexto
            save_path: Ruta donde se guardarían los PDFs (para mostrar estado local)
        """
        print("\n" + "=" * 165)
        print("📋 PREVIEW DE PDFS ENCONTRADOS")
        print("=" * 165)

        url_parts = base_url.rstrip('/').split('/')
        subject = url_parts[-1]
        klasse = url_parts[-2]
        print(f"\n📚 Clase: {klasse.replace('klasse-', '').upper()}")
        print(f"📖 Asignatura: {subject.upper()}\n")

        # Contar estado
        downloaded = sum(1 for p in pdfs if p.get('is_local', False))
        new = sum(1 for p in pdfs if not p.get('is_local', False))

        print(f"✓ {len(pdfs)} PDFs encontrados")
        print(f"  - Exámenes: {sum(1 for p in pdfs if not p['is_solution'])}")
        print(f"  - Soluciones: {sum(1 for p in pdfs if p['is_solution'])}")
        print(f"  - Ya descargados: {downloaded}")
        print(f"  - Nuevos: {new}\n")

        # Extraer número de REF para ordenar
        def extract_ref_number(pdf: Dict) -> int:
            """Extrae el número de REF para ordenar (#3426 -> 3426)"""
            doc_number = pdf.get('doc_number', '')
            # Buscar patrones como #3426 o #130g
            import re
            match = re.search(r'#(\d+)', doc_number)
            if match:
                return int(match.group(1))
            return 999999  # Si no encuentra número, poner al final

        # Ordenar PDFs por REF (número de referencia)
        sorted_pdfs = sorted(pdfs, key=extract_ref_number)

        print("-" * 165)
        print(f"{'#':3} | {'LOC':3} | {'TIPO':8} | {'ID':7} | {'REF':8} | {'Categoría':35} | {'Título':75}")
        print("-" * 165)

        for i, pdf in enumerate(sorted_pdfs, 1):
            local_status = "✓" if pdf.get('is_local', False) else " "
            doc_type = "Solution" if pdf['is_solution'] else "Exam"

            # Truncar datos para que quepan en columnas
            doc_category = pdf.get('doc_type', 'Documento')[:33]
            doc_title_display = pdf.get('doc_title', 'Sin título')[:73]
            doc_number = pdf.get('doc_number', f"#{pdf['doc_id']}")
            pdf_id = pdf['name'].replace('_solution', '')

            print(f"{i:3} | {local_status:3} | {doc_type:8} | {pdf_id:7} | {doc_number:8} | {doc_category:35} | {doc_title_display:75}")

        print("-" * 165)
        print(f"Total: {len(pdfs)} PDFs ({sum(1 for p in pdfs if not p['is_solution'])} exámenes + {sum(1 for p in pdfs if p['is_solution'])} soluciones)")
        print("Leyenda: LOC=Local (✓=descargado, -=nuevo), TIPO=Exam/Solution, ID=ID descarga, REF=Referencia CatLux")
        print("=" * 165 + "\n")


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def mark_local_files(pdfs: List[Dict], save_path: Path) -> None:
    """
    Marca cuáles PDFs ya existen localmente.

    Args:
        pdfs: Lista de PDFs a marcar
        save_path: Ruta donde buscar los archivos
    """
    for pdf in pdfs:
        pdf_file = save_path / (pdf['name'] + '.pdf')
        pdf['is_local'] = pdf_file.exists()


def ask_download_selection(pdfs: List[Dict]) -> List[int]:
    """
    Pregunta al usuario qué PDFs descargar de forma interactiva.

    Args:
        pdfs: Lista de PDFs disponibles

    Returns:
        Lista de índices (0-basado) de PDFs a descargar
    """
    print("\n" + "=" * 80)
    print("📥 SELECCIONAR PDFS PARA DESCARGAR")
    print("=" * 80)
    print("\nOpciones:")
    print("  - Escribe 'all' para descargar TODOS los PDFs nuevos")
    print("  - Escribe 'none' para NO descargar nada")
    print("  - Escribe números separados por comas: 1,3,5 para descargar esos")
    print("  - Escribe 'new' para descargar solo los NUEVOS (no los ya descargados)")
    print("\n" + "=" * 80)

    while True:
        try:
            user_input = input("\nSelección: ").strip().lower()

            if user_input == 'all':
                return list(range(len(pdfs)))

            elif user_input == 'none':
                return []

            elif user_input == 'new':
                # Agrupar por ID para obtener índices únicos de nuevos
                new_indices = set()
                for i, pdf in enumerate(pdfs):
                    if not pdf.get('is_local', False):
                        # Obtener el índice del PDF sin solución (el grupo)
                        pdf_id = pdf['name'].replace('_solution', '')
                        # Buscar el índice del examen (el primero)
                        for j, p in enumerate(pdfs):
                            if p['name'] == pdf_id:
                                new_indices.add(j)
                                break
                return sorted(list(new_indices))

            else:
                # Parsear números
                indices = [int(x.strip()) - 1 for x in user_input.split(',')]
                # Validar
                if all(0 <= i < len(pdfs) for i in indices):
                    return sorted(list(set(indices)))  # Eliminar duplicados y ordenar
                else:
                    print(f"❌ Números inválidos. Rango válido: 1-{len(pdfs)}")
                    continue

        except (ValueError, IndexError):
            print("❌ Entrada inválida. Intenta de nuevo.")
            continue


# ============================================================================
# FUNCIONES DE AUTENTICACIÓN
# ============================================================================

def get_credentials() -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Obtiene las credenciales desde variables de entorno."""
    username = os.getenv("CATLUX_USERNAME")
    password = os.getenv("CATLUX_PASSWORD")
    cert_path = os.getenv("CATLUX_CERT_PATH", "")
    save_path = os.getenv("CATLUX_SAVE_PATH")

    if not username or not password:
        logger.error("Credenciales faltantes. Configura .env con CATLUX_USERNAME y CATLUX_PASSWORD")
        return None, None, None, None

    if not save_path:
        logger.error("CATLUX_SAVE_PATH no configurado en .env")
        return None, None, None, None

    return username, password, cert_path if cert_path else None, save_path


def login_to_catlux(session: requests.Session, username: str, password: str,
                    cert_path: Optional[str]) -> bool:
    """Realiza login en CatLux."""
    try:
        # Usar verify=False para evitar problemas de SSL
        # (CatLux usa certificado auto-firmado)
        kwargs = {"verify": False, "timeout": 10}

        login_page_req = session.get(LOGIN_URL, **kwargs)
        login_page_req.raise_for_status()

        soup_login = BeautifulSoup(login_page_req.content, 'html.parser')

        # Buscar el formulario de login (el que tiene username y password)
        login_form = None
        for form in soup_login.find_all('form'):
            if form.find('input', {'name': 'username'}) and form.find('input', {'name': 'password'}):
                login_form = form
                break

        if not login_form:
            logger.error("No se encontró formulario de login")
            return False

        # Obtener el ID del formulario (es el FORM_SUBMIT value)
        form_submit_value = login_form.get('id', 'tl_login')

        # Obtener el REQUEST_TOKEN del formulario
        token_input = login_form.find('input', {'name': 'REQUEST_TOKEN'})
        if not token_input:
            logger.error("No se encontró REQUEST_TOKEN")
            return False

        request_token = token_input.get('value', '')

        # Obtener otros campos ocultos
        target_path = ''
        target_path_input = login_form.find('input', {'name': '_target_path'})
        if target_path_input:
            target_path = target_path_input.get('value', '')

        # Construir payload
        payload = {
            'FORM_SUBMIT': form_submit_value,
            'REQUEST_TOKEN': request_token,
            'username': username,
            'password': password
        }

        if target_path:
            payload['_target_path'] = target_path
            payload['_always_use_target_path'] = '0'

        logger.info(f"Login: usando FORM_SUBMIT={form_submit_value}")

        login_req = session.post(LOGIN_URL, data=payload, **kwargs)
        login_req.raise_for_status()

        logger.info("✓ Login exitoso")
        return True

    except Exception as e:
        logger.error(f"Error en login: {e}")
        return False


# ============================================================================
# FUNCIONES DE DESCARGA Y PREVIEW
# ============================================================================

def preview_pdfs(base_url: str, max_pages: int = 10) -> Tuple[List[Dict], List[int]]:
    """
    Muestra preview de PDFs y pregunta cuáles descargar.

    Args:
        base_url: URL base de la clase
        max_pages: Máximo de páginas a procesar

    Returns:
        Tupla de (lista de PDFs, índices a descargar)
    """
    username, password, cert_path, save_base_path = get_credentials()
    if not all([username, password, save_base_path]):
        return [], []

    # Extraer carpeta de destino
    try:
        url_parts = base_url.rstrip('/').split('/')
        subject_folder = url_parts[-1]
        class_folder = url_parts[-2]
        full_save_path = Path(save_base_path) / class_folder / subject_folder
    except (IndexError, ValueError) as e:
        logger.error(f"Error parseando URL: {e}")
        return [], []

    session = requests.Session()

    try:
        if not login_to_catlux(session, username, password, cert_path):
            return [], []

        manager = PDFManager(session, cert_path)
        pdfs = manager.fetch_pdfs(base_url, max_pages)

        # Marcar archivos locales
        mark_local_files(pdfs, full_save_path)

        # Mostrar preview
        manager.print_preview(pdfs, base_url, full_save_path)

        # IMPORTANTE: Reordenar la lista igual que en print_preview()
        # para que los índices seleccionados correspondan a lo que el usuario vio
        def extract_ref_number(pdf: Dict) -> int:
            """Extrae el número de REF para ordenar (#3426 -> 3426)"""
            doc_number = pdf.get('doc_number', '')
            import re
            match = re.search(r'#(\d+)', doc_number)
            if match:
                return int(match.group(1))
            return 999999

        pdfs = sorted(pdfs, key=extract_ref_number)

        # Pedir selección
        selected_indices = ask_download_selection(pdfs)

        return pdfs, selected_indices

    except Exception as e:
        logger.error(f"Error en preview: {e}")
        return [], []

    finally:
        session.close()


def download_filtered_pdfs(base_url: str, max_pages: int = 10,
                          tracker: Optional[DownloadTracker] = None,
                          pdfs: Optional[List[Dict]] = None,
                          selected_indices: Optional[List[int]] = None) -> int:
    """
    Descarga PDFs de una clase desde CatLux.

    Args:
        base_url: URL base de la clase
        max_pages: Máximo de páginas (solo usado si pdfs es None)
        tracker: Rastreador de descargas
        pdfs: Lista pre-obtenida de PDFs (si es None, se obtiene)
        selected_indices: Índices de PDFs a descargar (0-basado)

    Returns:
        Número de PDFs descargados
    """
    if tracker is None:
        tracker = DownloadTracker(TRACKER_FILE)

    username, password, cert_path, save_base_path = get_credentials()
    if not all([username, password, save_base_path]):
        return 0

    # Extraer clase y asignatura de la URL
    try:
        url_parts = base_url.rstrip('/').split('/')
        subject_folder = url_parts[-1]
        class_folder = url_parts[-2]
        full_save_path = Path(save_base_path) / class_folder / subject_folder
    except (IndexError, ValueError) as e:
        logger.error(f"Error parseando URL: {e}")
        return 0

    full_save_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Carpeta de destino: {full_save_path}")

    remaining = tracker.get_remaining_downloads()
    if remaining == 0:
        logger.error("Límite de descargas alcanzado para este mes")
        tracker.print_status()
        return 0

    downloaded_count = 0
    session = requests.Session()

    try:
        if not login_to_catlux(session, username, password, cert_path):
            logger.error("No se pudo completar el login")
            return 0

        # Si no se pasaron PDFs, obtenerlos ahora
        if pdfs is None:
            manager = PDFManager(session, cert_path)
            pdfs = manager.fetch_pdfs(base_url, max_pages)
            # Si no se especificaron índices, descargar todos
            if selected_indices is None:
                selected_indices = list(range(len(pdfs)))

        manager = PDFManager(session, cert_path)

        print("\n🔄 Iniciando descargas...\n")

        # Descargar solo los PDFs seleccionados
        pdfs_to_download = [pdfs[i] for i in selected_indices if i < len(pdfs)]

        # Crear conjunto de IDs ya procesados para evitar descargar dos veces
        processed_ids = set()

        for pdf in pdfs_to_download:
            if tracker.get_remaining_downloads() == 0:
                logger.warning("Límite alcanzado, deteniendo descargas")
                break

            pdf_name = pdf['name']
            pdf_save_path = full_save_path / (pdf_name + ".pdf")

            # Si ya existe localmente, saltarlo (para cualquier tipo de PDF)
            if pdf_save_path.exists():
                logger.info(f"✓ {pdf_name}.pdf - ya existe")
                continue

            # Descargar
            try:
                r = session.get(pdf['full_url'], verify=False, timeout=30)
                r.raise_for_status()

                with open(pdf_save_path, 'wb') as f:
                    f.write(r.content)

                tracker.record_download(pdf_name)
                downloaded_count += 1
                logger.info(f"⬇ {pdf_name}.pdf - descargado ({tracker.get_remaining_downloads()} restantes)")

                # Si es examen, buscar y descargar automáticamente su solución
                if not pdf['is_solution']:
                    base_id = pdf['name']
                    if base_id not in processed_ids:
                        processed_ids.add(base_id)
                        # Buscar la solución en la lista de PDFs
                        solution_name = f"{base_id}_solution"
                        solution = next((p for p in pdfs if p['name'] == solution_name), None)

                        if solution:
                            solution_path = full_save_path / (solution_name + ".pdf")

                            # Descargar solución si no existe
                            if not solution_path.exists():
                                try:
                                    r_sol = session.get(solution['full_url'], verify=False, timeout=30)
                                    r_sol.raise_for_status()

                                    with open(solution_path, 'wb') as f:
                                        f.write(r_sol.content)

                                    tracker.record_download(solution_name)
                                    downloaded_count += 1
                                    logger.info(f"⬇ {solution_name}.pdf - descargado ({tracker.get_remaining_downloads()} restantes)")

                                except Exception as e:
                                    logger.error(f"Error descargando solución {solution_name}: {e}")
                            else:
                                logger.info(f"✓ {solution_name}.pdf - ya existe")

            except Exception as e:
                logger.error(f"Error descargando {pdf_name}: {e}")

        logger.info(f"Descarga completada: {downloaded_count} nuevos PDFs")

    except Exception as e:
        logger.error(f"Error en descarga: {e}")

    finally:
        session.close()

    tracker.print_status()
    return downloaded_count


def show_latest_downloads(tracker: Optional[DownloadTracker] = None) -> None:
    """Muestra las últimas descargas registradas."""
    if tracker is None:
        tracker = DownloadTracker(TRACKER_FILE)

    downloads = tracker.data.get("downloads", [])
    if not downloads:
        print("\n📥 No hay descargas registradas\n")
        return

    # Últimas 20 descargas
    recent = downloads[-20:]

    print("\n" + "=" * 60)
    print("📥 ÚLTIMAS DESCARGAS (máximo 20)")
    print("=" * 60)

    for i, download in enumerate(reversed(recent), 1):
        date_str = download.get("date", "unknown")[:10]
        filename = download.get("filename", "unknown")
        print(f"{i:2}. [{date_str}] {filename}")

    print("=" * 60 + "\n")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Descargador de PDFs de CatLux con preview de categorías"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="URL base de la clase (ej: https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/)"
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=10,
        help="Número máximo de páginas a procesar (default: 10)"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Mostrar preview de PDFs SIN descargar"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Descargar PDFs (después de verificar con preview)"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Mostrar estado de descargas"
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Mostrar últimas descargas realizadas"
    )
    parser.add_argument(
        "--reset-tracker",
        action="store_true",
        help="⚠️  ADVERTENCIA: Borra el historial de descargas"
    )

    args = parser.parse_args()
    tracker = DownloadTracker(TRACKER_FILE)

    # Mostrar estado
    if args.info:
        tracker.print_status()
        return 0

    # Mostrar últimas descargas
    if args.latest:
        show_latest_downloads(tracker)
        return 0

    # Reset tracker
    if args.reset_tracker:
        print("⚠️  ¿Estás seguro que quieres borrar el historial? (s/n)")
        if input().lower() == 's':
            tracker.data = {"downloads": [], "total_all_time": 0}
            tracker._save_tracker()
            print("✓ Historial borrado")
        return 0

    # Obtener URL
    url = args.url
    if not url:
        url = os.getenv("CATLUX_DEFAULT_URL", "").strip()
        if not url:
            print("Uso: python catlux_scrapper.py --url 'https://www.catlux.de/proben/...'")
            print("      python catlux_scrapper.py --preview --url '...'")
            print("      python catlux_scrapper.py --info")
            return 1

    # Preview (siempre interactivo - pregunta qué descargar)
    logger.info(f"Iniciando preview desde: {url}")
    pdfs, selected_indices = preview_pdfs(url, args.pages)

    if not pdfs:
        logger.error("No se encontraron PDFs")
        return 1

    # Si se seleccionaron PDFs para descargar, ejecutar descarga
    if selected_indices:
        logger.info(f"Descargando {len(selected_indices)} PDFs seleccionados...")
        download_filtered_pdfs(url, args.pages, tracker, pdfs, selected_indices)
    else:
        print("\n✓ No se descargará nada (seleccionaste 'none')")

    return 0


if __name__ == '__main__':
    sys.exit(main())
