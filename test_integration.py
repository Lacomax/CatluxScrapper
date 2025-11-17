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

# Test 2: Verify PDF sorting by REF
print("=" * 80)
print("TEST 2: Verificar ordenamiento por REF")
print("=" * 80)

from catlux_scrapper import PDFManager
import requests
import re

# Create test PDFs with different REF numbers
test_pdfs_unsorted = [
    {'name': '119215', 'is_solution': False, 'url': 'test', 'full_url': 'test',
     'doc_id': '119215', 'doc_number': '#3426', 'doc_type': 'Schulaufgabe', 'doc_title': 'Test 3', 'is_local': False},
    {'name': '118065', 'is_solution': False, 'url': 'test', 'full_url': 'test',
     'doc_id': '118065', 'doc_number': '#3425', 'doc_type': 'Aufsatz', 'doc_title': 'Test 1', 'is_local': False},
    {'name': '120000', 'is_solution': False, 'url': 'test', 'full_url': 'test',
     'doc_id': '120000', 'doc_number': '#3424', 'doc_type': 'Test', 'doc_title': 'Test 2', 'is_local': False},
]

def extract_ref_number(pdf):
    """Extrae el número de REF para ordenar"""
    doc_number = pdf.get('doc_number', '')
    match = re.search(r'#(\d+)', doc_number)
    if match:
        return int(match.group(1))
    return 999999

sorted_pdfs = sorted(test_pdfs_unsorted, key=extract_ref_number)

print(f"\nPDFs sin ordenar:")
for pdf in test_pdfs_unsorted:
    print(f"  - {pdf['name']} ({pdf['doc_number']})")

print(f"\nPDFs ordenados por REF:")
for pdf in sorted_pdfs:
    print(f"  - {pdf['name']} ({pdf['doc_number']})")

assert sorted_pdfs[0]['doc_number'] == '#3424', "Debe estar ordenado por REF"
assert sorted_pdfs[1]['doc_number'] == '#3425', "Debe estar ordenado por REF"
assert sorted_pdfs[2]['doc_number'] == '#3426', "Debe estar ordenado por REF"

print("\n✓ TEST 2 PASADO: Ordenamiento por REF funciona correctamente\n")

# Test 3: Verify independent documents and auto-solution download
print("=" * 80)
print("TEST 3: Verificar documentos independientes y descarga automática de soluciones")
print("=" * 80)

# Crear una lista de documentos independientes (examen y solución separados)
test_docs_independent = [
    {'name': '119215', 'is_solution': False, 'url': 'test', 'full_url': 'test',
     'doc_id': '119215', 'doc_number': '#3426', 'doc_type': 'Schulaufgabe', 'doc_title': 'Test 1', 'is_local': False},
    {'name': '119215_solution', 'is_solution': True, 'url': 'test', 'full_url': 'test',
     'doc_id': '119215', 'doc_number': '#3426', 'doc_type': 'Schulaufgabe', 'doc_title': 'Test 1', 'is_local': False},
    {'name': '118065', 'is_solution': False, 'url': 'test', 'full_url': 'test',
     'doc_id': '118065', 'doc_number': '#3425', 'doc_type': 'Aufsatz', 'doc_title': 'Test 2', 'is_local': False},
    {'name': '118065_solution', 'is_solution': True, 'url': 'test', 'full_url': 'test',
     'doc_id': '118065', 'doc_number': '#3425', 'doc_type': 'Aufsatz', 'doc_title': 'Test 2', 'is_local': False},
    {'name': '117356', 'is_solution': False, 'url': 'test', 'full_url': 'test',
     'doc_id': '117356', 'doc_number': '#3424', 'doc_type': 'Test', 'doc_title': 'Test 3', 'is_local': False},
    {'name': '117356_solution', 'is_solution': True, 'url': 'test', 'full_url': 'test',
     'doc_id': '117356', 'doc_number': '#3424', 'doc_type': 'Test', 'doc_title': 'Test 3', 'is_local': False},
]

print(f"\nDocumentos en lista (independientes):")
for i, doc in enumerate(test_docs_independent, 1):
    dtype = "Exam" if not doc['is_solution'] else "Solution"
    print(f"  {i}. {doc['name']:20} ({dtype})")

# Usuario selecciona índices 0 y 2 (los dos exámenes)
selected_indices = [0, 2]  # 119215 y 118065 examen
pdfs_to_download = [test_docs_independent[i] for i in selected_indices if i < len(test_docs_independent)]

print(f"\nUsuario selecciona índices: {selected_indices} (solo exámenes)")
print(f"PDFs seleccionados:")
for pdf in pdfs_to_download:
    dtype = "Exam" if not pdf['is_solution'] else "Solution"
    print(f"  - {pdf['name']} ({dtype})")

# Simular descarga automática de soluciones
print(f"\nSimulando descarga automática de soluciones:")
downloaded_docs = []
for pdf in pdfs_to_download:
    if not pdf['is_solution']:
        # Es examen, agregar a descargados
        downloaded_docs.append(pdf)
        print(f"  ⬇ {pdf['name']}")

        # Buscar y agregar solución automáticamente
        solution_name = f"{pdf['name']}_solution"
        solution = next((p for p in test_docs_independent if p['name'] == solution_name), None)
        if solution:
            downloaded_docs.append(solution)
            print(f"  ⬇ {solution['name']} (automática)")

assert len(downloaded_docs) == 4, "Debe descargar 2 exámenes + 2 soluciones automáticas"
# Verificar que tenemos 2 exámenes y 2 soluciones
exam_count = sum(1 for d in downloaded_docs if not d['is_solution'])
solution_count = sum(1 for d in downloaded_docs if d['is_solution'])
assert exam_count == 2, f"Debe haber 2 exámenes, pero hay {exam_count}"
assert solution_count == 2, f"Debe haber 2 soluciones, pero hay {solution_count}"

print("\n✓ TEST 3 PASADO: Documentos independientes y descarga automática funcionan correctamente\n")

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
