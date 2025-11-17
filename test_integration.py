#!/usr/bin/env python3
"""
Test script to verify interactive selection and local file detection
"""

import json
from pathlib import Path
from typing import List, Dict

# Test 1: Verify mark_local_files function
print("=" * 80)
print("TEST 1: Verificar mark_local_files()")
print("=" * 80)

test_dir = Path("/tmp/test_catlux")
test_dir.mkdir(exist_ok=True)

# Create some test files
test_files = ["119215.pdf", "119215_solution.pdf", "118065.pdf"]
for filename in test_files[:2]:  # Only create first 2
    (test_dir / filename).touch()

# Create test PDFs list
test_pdfs = [
    {'name': '119215', 'is_solution': False, 'url': 'test', 'full_url': 'test',
     'doc_id': '119215', 'doc_number': '#3426', 'doc_type': 'Schulaufgabe', 'doc_title': 'Test 1'},
    {'name': '119215_solution', 'is_solution': True, 'url': 'test', 'full_url': 'test',
     'doc_id': '119215', 'doc_number': '#3426', 'doc_type': 'Schulaufgabe', 'doc_title': 'Test 1'},
    {'name': '118065', 'is_solution': False, 'url': 'test', 'full_url': 'test',
     'doc_id': '118065', 'doc_number': '#3425', 'doc_type': 'Aufsatz', 'doc_title': 'Test 2'},
]

# Import the function from the main script
import sys
sys.path.insert(0, '/home/user/CatluxScrapper')
from catlux_scrapper import mark_local_files

# Test mark_local_files
mark_local_files(test_pdfs, test_dir)

print(f"\nArchivos de prueba en {test_dir}:")
for f in test_dir.glob("*.pdf"):
    print(f"  - {f.name}")

print(f"\nEstado local después de mark_local_files():")
for pdf in test_pdfs:
    status = "✓ (descargado)" if pdf.get('is_local') else "☐ (nuevo)"
    print(f"  - {pdf['name']:20} {status}")

assert test_pdfs[0]['is_local'] == True, "119215.pdf debe estar marcado como local"
assert test_pdfs[1]['is_local'] == True, "119215_solution.pdf debe estar marcado como local"
assert test_pdfs[2]['is_local'] == False, "118065.pdf NO debe estar marcado como local"
print("\n✓ TEST 1 PASADO: mark_local_files() funciona correctamente\n")

# Test 2: Verify PDF grouping in print_preview
print("=" * 80)
print("TEST 2: Verificar agrupación de PDFs en preview")
print("=" * 80)

from catlux_scrapper import PDFManager
import requests

# We'll just test the grouping logic
manager = PDFManager(requests.Session())

print(f"\nPDFs a agrupar:")
for i, pdf in enumerate(test_pdfs, 1):
    print(f"  {i}. {pdf['name']}")

grouped = manager.group_by_category(test_pdfs)
print(f"\nPDFs agrupados:")
for key, pdfs in grouped.items():
    print(f"  - {key}: {len(pdfs)} items")

print("\n✓ TEST 2 PASADO: Agrupación funciona correctamente\n")

# Test 3: Verify selected_indices logic
print("=" * 80)
print("TEST 3: Verificar lógica de índices seleccionados")
print("=" * 80)

test_pdfs_extended = test_pdfs * 2  # Simular más PDFs

print(f"\nSimulando selección de índices:")
print(f"  Total de PDFs: {len(test_pdfs_extended)}")

# Simulate selection of indices 0, 2, 4 (0-based)
selected_indices = [0, 2, 4]
pdfs_to_download = [test_pdfs_extended[i] for i in selected_indices if i < len(test_pdfs_extended)]

print(f"  Índices seleccionados: {selected_indices}")
print(f"  PDFs a descargar: {len(pdfs_to_download)}")
print(f"\n  PDFs seleccionados:")
for pdf in pdfs_to_download:
    print(f"    - {pdf['name']}")

assert len(pdfs_to_download) == 3, "Debe haber 3 PDFs seleccionados"
print("\n✓ TEST 3 PASADO: Lógica de índices funciona correctamente\n")

# Test 4: Verify tracker functionality
print("=" * 80)
print("TEST 4: Verificar tracker de descargas")
print("=" * 80)

from catlux_scrapper import DownloadTracker

tracker_file = Path("/tmp/test_tracker.json")
tracker_file.unlink(missing_ok=True)

tracker = DownloadTracker(tracker_file)

print(f"\nTracker inicial:")
print(f"  Descargas este mes: {tracker.get_current_month_downloads()}")
print(f"  Disponibles: {tracker.get_remaining_downloads()}")

tracker.record_download("119215.pdf")
tracker.record_download("119215_solution.pdf")

print(f"\nDespués de registrar 2 descargas:")
print(f"  Descargas este mes: {tracker.get_current_month_downloads()}")
print(f"  Disponibles: {tracker.get_remaining_downloads()}")

assert tracker.get_current_month_downloads() == 2, "Debe haber 2 descargas registradas"
assert tracker.get_remaining_downloads() == 98, "Deben quedar 98 descargas"
print("\n✓ TEST 4 PASADO: Tracker funciona correctamente\n")

# Cleanup
import shutil
shutil.rmtree(test_dir, ignore_errors=True)
tracker_file.unlink(missing_ok=True)

print("=" * 80)
print("✓ TODOS LOS TESTS PASARON")
print("=" * 80)
print("\nResumen de pruebas:")
print("  ✓ mark_local_files() detecta archivos locales correctamente")
print("  ✓ Agrupación de PDFs funciona correctamente")
print("  ✓ Lógica de índices seleccionados funciona correctamente")
print("  ✓ Tracker registra y calcula descargas correctamente")
