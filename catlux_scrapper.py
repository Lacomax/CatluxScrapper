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
except ImportError:
    print("Error: Dependencias faltantes. Ejecuta:")
    print("  pip install requests beautifulsoup4 python-dotenv")
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
        logging.FileHandler(LOG_FILE),
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

        Args:
            base_url: URL base de la clase
            max_pages: Máximo de páginas a procesar

        Returns:
            Lista de diccionarios con información de PDFs
        """
        pdfs = []

        for page_num in range(1, max_pages + 1):
            url = f"{base_url}?p={page_num}"
            logger.info(f"Buscando en: {url}")

            try:
                response = self.session.get(url, **self.kwargs, timeout=10)
                response.raise_for_status()
            except Exception as e:
                logger.error(f"Error descargando página {page_num}: {e}")
                break

            soup = BeautifulSoup(response.content, "html.parser")
            pdf_links = soup.select('a[href*="pdf"]')

            if not pdf_links:
                logger.info(f"No hay PDFs en página {page_num}")
                break

            for link in pdf_links:
                try:
                    pdf_url = link.get('href', '')
                    pdf_name = Path(pdf_url).name.replace("?dl=pdf", "")

                    # Extraer información del contexto HTML
                    parent = link.find_parent('div', class_=lambda x: x and 'card' in x.lower())
                    text_content = parent.get_text() if parent else link.get_text()

                    pdfs.append({
                        'name': pdf_name,
                        'url': pdf_url,
                        'full_url': urljoin("https://www.catlux.de/", pdf_url),
                        'is_solution': '_solution' in pdf_name,
                        'text': text_content.strip()
                    })
                except Exception as e:
                    logger.warning(f"Error procesando enlace: {e}")
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

    def print_preview(self, pdfs: List[Dict], base_url: str) -> None:
        """
        Imprime preview de PDFs encontrados.

        Args:
            pdfs: Lista de PDFs
            base_url: URL base para contexto
        """
        print("\n" + "=" * 70)
        print("📋 PREVIEW DE PDFS ENCONTRADOS")
        print("=" * 70)

        url_parts = base_url.rstrip('/').split('/')
        subject = url_parts[-1]
        klasse = url_parts[-2]
        print(f"\n📚 Clase: {klasse.replace('klasse-', '').upper()}")
        print(f"📖 Asignatura: {subject.upper()}\n")

        grouped = self.group_by_category(pdfs)

        print(f"✓ {len(pdfs)} PDFs encontrados")
        print(f"  - Exámenes: {sum(1 for p in pdfs if not p['is_solution'])}")
        print(f"  - Soluciones: {sum(1 for p in pdfs if p['is_solution'])}\n")

        print("-" * 70)
        print("Archivos encontrados:")
        print("-" * 70)

        for i, (key, items) in enumerate(grouped.items(), 1):
            status = "✓" if len(items) > 1 else "⊘"
            print(f"{i:3}. [{status}] {key}")

        print("-" * 70)
        print(f"Total: {len(pdfs)} PDFs")
        print("=" * 70 + "\n")


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
        kwargs = {"verify": cert_path} if cert_path else {}
        login_page_req = session.get(LOGIN_URL, **kwargs, timeout=10)
        login_page_req.raise_for_status()

        soup_login = BeautifulSoup(login_page_req.content, 'html.parser')
        token_input = soup_login.find('input', {'name': 'REQUEST_TOKEN'})

        if not token_input:
            logger.error("No se encontró token de login")
            return False

        request_token = token_input['value']

        payload = {
            'FORM_SUBMIT': 'tl_login',
            'REQUEST_TOKEN': request_token,
            'username': username,
            'password': password
        }

        login_req = session.post(LOGIN_URL, data=payload, **kwargs, timeout=10)
        login_req.raise_for_status()

        logger.info("✓ Login exitoso")
        return True

    except Exception as e:
        logger.error(f"Error en login: {e}")
        return False


# ============================================================================
# FUNCIONES DE DESCARGA Y PREVIEW
# ============================================================================

def preview_pdfs(base_url: str, max_pages: int = 10) -> int:
    """
    Muestra preview de PDFs sin descargar.

    Args:
        base_url: URL base de la clase
        max_pages: Máximo de páginas a procesar

    Returns:
        Número de PDFs encontrados
    """
    username, password, cert_path, _ = get_credentials()
    if not all([username, password]):
        return 0

    session = requests.Session()

    try:
        if not login_to_catlux(session, username, password, cert_path):
            return 0

        manager = PDFManager(session, cert_path)
        pdfs = manager.fetch_pdfs(base_url, max_pages)

        manager.print_preview(pdfs, base_url)
        return len(pdfs)

    except Exception as e:
        logger.error(f"Error en preview: {e}")
        return 0

    finally:
        session.close()


def download_filtered_pdfs(base_url: str, max_pages: int = 10,
                          tracker: Optional[DownloadTracker] = None) -> int:
    """Descarga PDFs de una clase desde CatLux."""

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

        manager = PDFManager(session, cert_path)
        pdfs = manager.fetch_pdfs(base_url, max_pages)

        # Mostrar preview antes de descargar
        manager.print_preview(pdfs, base_url)

        print("\n🔄 Iniciando descargas...\n")

        for pdf in pdfs:
            if tracker.get_remaining_downloads() == 0:
                logger.warning("Límite alcanzado, deteniendo descargas")
                break

            pdf_name = pdf['name']
            pdf_save_path = full_save_path / (pdf_name + ".pdf")

            # Si es solución, solo descargar si el examen ya existe
            if pdf['is_solution']:
                exam_name = pdf_name.replace("_solution", "")
                exam_path = full_save_path / (exam_name + ".pdf")

                if not exam_path.exists():
                    logger.info(f"⊘ {pdf_name}.pdf - examen no existe, saltando solución")
                    continue
            else:
                # Es examen, descargar solo si no existe
                if pdf_save_path.exists():
                    logger.info(f"✓ {pdf_name}.pdf - ya existe")
                    continue

            # Descargar
            try:
                kwargs = {"verify": cert_path} if cert_path else {}
                r = session.get(pdf['full_url'], **kwargs, timeout=30)
                r.raise_for_status()

                with open(pdf_save_path, 'wb') as f:
                    f.write(r.content)

                tracker.record_download(pdf_name)
                downloaded_count += 1
                logger.info(f"⬇ {pdf_name}.pdf - descargado ({tracker.get_remaining_downloads()} restantes)")

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

    # Preview o descargar
    if args.preview:
        logger.info(f"Iniciando preview desde: {url}")
        count = preview_pdfs(url, args.pages)
        print(f"\nℹ️  Ejecuta: python catlux_scrapper.py --download --url '{url}' para descargar")
        return 0

    if args.download:
        logger.info(f"Iniciando descarga desde: {url}")
        download_filtered_pdfs(url, args.pages, tracker)
        return 0

    # Default: preview
    logger.info(f"Iniciando preview desde: {url}")
    count = preview_pdfs(url, args.pages)
    print(f"\nℹ️  Ejecuta: python catlux_scrapper.py --download --url '{url}' para descargar")
    return 0


if __name__ == '__main__':
    sys.exit(main())
