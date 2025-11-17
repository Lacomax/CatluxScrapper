#!/usr/bin/env python3
"""
Debug avanzado para verificar la búsqueda de PDFs
"""

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import urllib3
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

url = "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/aufsatz?p=1"
username = os.getenv("CATLUX_USERNAME")
password = os.getenv("CATLUX_PASSWORD")

print(f"Investigando: {url}\n")

try:
    # Login
    session = requests.Session()
    login_url = "https://www.catlux.de/login"
    login_page = session.get(login_url, verify=False, timeout=10)
    soup_login = BeautifulSoup(login_page.content, 'html.parser')

    login_form = None
    for form in soup_login.find_all('form'):
        if form.find('input', {'name': 'username'}) and form.find('input', {'name': 'password'}):
            login_form = form
            break

    form_submit_value = login_form.get('id', 'tl_login')
    token_input = login_form.find('input', {'name': 'REQUEST_TOKEN'})
    request_token = token_input.get('value', '')

    payload = {
        'FORM_SUBMIT': form_submit_value,
        'REQUEST_TOKEN': request_token,
        'username': username,
        'password': password
    }

    login_req = session.post(login_url, data=payload, verify=False, timeout=10)
    print("✓ Login exitoso\n")

    # Descargar página
    response = session.get(url, verify=False, timeout=10)
    print(f"Status: {response.status_code}\n")

    soup = BeautifulSoup(response.content, "html.parser")

    print("1️⃣ Buscando contenedores: div.doc.item...")
    doc_containers = soup.find_all('div', class_=lambda x: x and 'doc' in str(x) and 'item' in str(x))
    print(f"   Contenedores encontrados: {len(doc_containers)}\n")

    if doc_containers:
        for i, container in enumerate(doc_containers[:2], 1):
            print(f"2️⃣ Contenedor {i}:")

            print(f"   Clase: {container.get('class')}")

            # Búsqueda método 1: find_all con lambda
            print(f"\n   Método 1: container.find_all('a', href=lambda x: x and '?dl=' in x)")
            pdf_links_1 = container.find_all('a', href=lambda x: x and '?dl=' in x)
            print(f"   Encontrados: {len(pdf_links_1)}")
            for j, link in enumerate(pdf_links_1[:3], 1):
                print(f"      {j}. href={link.get('href')}")

            # Búsqueda método 2: find_all todos los enlaces
            print(f"\n   Método 2: container.find_all('a', href=True)")
            all_links = container.find_all('a', href=True)
            print(f"   Total enlaces: {len(all_links)}")

            # Contar cuántos tienen ?dl=
            dl_count = sum(1 for a in all_links if '?dl=' in a.get('href', ''))
            print(f"   Enlaces con ?dl=: {dl_count}")

            for j, link in enumerate(all_links[:6], 1):
                href = link.get('href', '')
                has_dl = '✓' if '?dl=' in href else ' '
                print(f"      {j}. [{has_dl}] href={href[:60]}")

            print()

    print("\n3️⃣ Búsqueda global de enlaces con ?dl=:")
    all_pdf_links = soup.find_all('a', href=lambda x: x and '?dl=' in x)
    print(f"   Total encontrados: {len(all_pdf_links)}")
    for j, link in enumerate(all_pdf_links[:5], 1):
        print(f"      {j}. {link.get('href')}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
