#!/usr/bin/env python3
"""
CatLux PDF Downloader with Download Tracking
=============================================

Script para descargar documentos de exámenes de CatLux (https://www.catlux.de)
con control de límite mensual de descargas (100 PDFs/mes) y evitar duplicados.

Características:
- Trackea el número de descargas (solo cuenta nuevos PDFs)
- Limita a 100 descargas por mes calendario
- Solo descarga examen + solución si no existen ya
- Muestra el saldo de descargas disponibles
- Multiplataforma (Windows, macOS, Linux)
- Credenciales seguras en archivo .env

Requisitos:
    pip install requests beautifulsoup4 python-dotenv

Uso:
    python catlux_scrapper.py
    python catlux_scrapper.py --info
    python catlux_scrapper.py --reset-tracker  # Advertencia: borra el historial

Autor: Mejorado para control de descargas
"""

import json
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, date
from urllib.parse import urljoin
from typing import Dict, Tuple, Optional
import argparse

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

# Cargar variables de entorno
load_dotenv()

# Constantes
DOWNLOADS_PER_MONTH = 100
TRACKER_FILE = Path(__file__).parent / "download_tracker.json"
LOG_FILE = Path(__file__).parent / "catlux_scrapper.log"
LOGIN_URL = "https://www.catlux.de/login"

# Configurar logging
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
# FUNCIONES DE TRACKING
# ============================================================================

class DownloadTracker:
    """Gestiona el seguimiento de descargas mensuales."""

    def __init__(self, tracker_file: Path):
        """
        Inicializa el tracker de descargas.

        Args:
            tracker_file: Ruta del archivo JSON para guardar el historial
        """
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
        """
        Retorna el número de descargas en el mes actual.

        Returns:
            Número de PDFs descargados este mes
        """
        today = date.today()
        current_month = f"{today.year}-{today.month:02d}"

        return sum(
            1 for download in self.data.get("downloads", [])
            if download.get("date", "").startswith(current_month)
        )

    def get_remaining_downloads(self) -> int:
        """
        Retorna el número de descargas disponibles este mes.

        Returns:
            Descargas disponibles (puede ser negativo si ya pasó el límite)
        """
        current = self.get_current_month_downloads()
        return max(0, DOWNLOADS_PER_MONTH - current)

    def record_download(self, filename: str) -> None:
        """
        Registra una descarga nueva.

        Args:
            filename: Nombre del archivo descargado
        """
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

# ============================================================================
# FUNCIONES DE DESCARGA
# ============================================================================

def get_credentials() -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Obtiene las credenciales desde variables de entorno.

    Returns:
        Tupla de (username, password, cert_path, save_base_path)
    """
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
    """
    Realiza login en CatLux.

    Args:
        session: Sesión de requests
        username: Usuario
        password: Contraseña
        cert_path: Ruta al certificado (opcional)

    Returns:
        True si el login fue exitoso
    """
    try:
        # Obtener token de login
        kwargs = {"verify": cert_path} if cert_path else {}
        login_page_req = session.get(LOGIN_URL, **kwargs)
        login_page_req.raise_for_status()

        soup_login = BeautifulSoup(login_page_req.content, 'html.parser')
        token_input = soup_login.find('input', {'name': 'REQUEST_TOKEN'})

        if not token_input:
            logger.error("No se encontró token de login en la página")
            return False

        request_token = token_input['value']

        # Enviar credenciales
        payload = {
            'FORM_SUBMIT': 'tl_login',
            'REQUEST_TOKEN': request_token,
            'username': username,
            'password': password
        }

        login_req = session.post(LOGIN_URL, data=payload, **kwargs)
        login_req.raise_for_status()

        if login_req.status_code != 200:
            logger.error("Login fallido - código de respuesta incorrecto")
            return False

        logger.info("✓ Login exitoso")
        return True

    except Exception as e:
        logger.error(f"Error en login: {e}")
        return False

def download_filtered_pdfs(base_url: str, page_param: str = "p", max_pages: int = 10,
                          tracker: Optional[DownloadTracker] = None) -> int:
    """
    Descarga PDFs de una clase desde CatLux.

    Args:
        base_url: URL base de la clase (ej: .../klasse-7/deutsch/)
        page_param: Parámetro de paginación (default: "p")
        max_pages: Máximo de páginas a procesar
        tracker: DownloadTracker para controlar descargas

    Returns:
        Número de PDFs descargados en esta sesión
    """
    if tracker is None:
        tracker = DownloadTracker(TRACKER_FILE)

    # Obtener credenciales
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

    # Verificar saldo antes de empezar
    remaining = tracker.get_remaining_downloads()
    if remaining == 0:
        logger.error("Límite de descargas alcanzado para este mes")
        tracker.print_status()
        return 0

    downloaded_count = 0
    session = requests.Session()

    try:
        # Login
        if not login_to_catlux(session, username, password, cert_path):
            logger.error("No se pudo completar el login")
            return 0

        # Procesar páginas
        for page_num in range(1, max_pages + 1):
            # Verificar saldo antes de cada página
            if tracker.get_remaining_downloads() == 0:
                logger.warning("Límite de descargas alcanzado durante el proceso")
                break

            url = f"{base_url}?{page_param}={page_num}"
            logger.info(f"Procesando página: {url}")

            kwargs = {"verify": cert_path} if cert_path else {}
            response = session.get(url, **kwargs)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            pdf_links = soup.select('a[href*="pdf"]')

            if not pdf_links:
                logger.info(f"No hay PDFs en página {page_num}, deteniendo")
                break

            for link in pdf_links:
                if tracker.get_remaining_downloads() == 0:
                    logger.warning("Límite alcanzado, deteniendo descargas")
                    break

                pdf_url = link['href']
                full_url = urljoin("https://www.catlux.de/", pdf_url)
                pdf_name = Path(pdf_url).name.replace("?dl=pdf", "")

                # Si es solución, solo descargar si el examen ya existe
                if "_solution" in pdf_name:
                    exam_name = pdf_name.replace("_solution", "")
                    exam_path = full_save_path / (exam_name + ".pdf")

                    if not exam_path.exists():
                        logger.info(f"⊘ {pdf_name} - examen no existe, saltando solución")
                        continue
                else:
                    # Es examen, descargar solo si no existe
                    pdf_save_path = full_save_path / (pdf_name + ".pdf")
                    if pdf_save_path.exists():
                        logger.info(f"✓ {pdf_name}.pdf - ya existe, saltando")
                        continue

                pdf_save_path = full_save_path / (pdf_name + ".pdf")

                if pdf_save_path.exists():
                    logger.info(f"✓ {pdf_name}.pdf - ya existe")
                    continue

                # Descargar
                try:
                    r = session.get(full_url, **kwargs, timeout=30)
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

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Descargador de PDFs de CatLux con control de límite mensual"
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
        "--info",
        action="store_true",
        help="Mostrar estado de descargas sin descargar"
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
            print("  o define CATLUX_DEFAULT_URL en .env")
            return 1

    # Descargar
    logger.info(f"Iniciando descarga desde: {url}")
    download_filtered_pdfs(url, page_param="p", max_pages=args.pages, tracker=tracker)

    return 0

if __name__ == '__main__':
    sys.exit(main())
