#!/usr/bin/env python3
"""
Script para debugear estructura HTML de páginas de CatLux
"""

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

# URL a investigar
url = "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/aufsatz"
username = os.getenv("CATLUX_USERNAME")
password = os.getenv("CATLUX_PASSWORD")

print(f"Investigando: {url}\n")

try:
    # Login primero
    session = requests.Session()

    print("1️⃣ Haciendo login...")
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
    print("   ✓ Login exitoso\n")

    print(f"2️⃣ Descargando página: {url}")
    response = session.get(url, verify=False, timeout=10)
    print(f"   Status: {response.status_code}\n")

    soup = BeautifulSoup(response.content, 'html.parser')

    print("3️⃣ Buscando enlaces con 'pdf'...")
    pdf_links = soup.select('a[href*="pdf"]')
    print(f"   Enlaces encontrados con 'pdf': {len(pdf_links)}")

    for i, link in enumerate(pdf_links[:5], 1):
        print(f"      {i}. href={link.get('href')}")

    print("\n4️⃣ Buscando enlaces con 'probe'...")
    probe_links = soup.select('a[href*="probe"]')
    print(f"   Enlaces encontrados con 'probe': {len(probe_links)}")

    for i, link in enumerate(probe_links[:5], 1):
        print(f"      {i}. href={link.get('href')}")

    print("\n5️⃣ Buscando TODOS los enlaces...")
    all_links = soup.find_all('a', href=True)
    print(f"   Total de enlaces: {len(all_links)}")

    # Filtrar por los que parecen ser PDFs/documentos
    doc_links = [a for a in all_links if 'probe' in a.get('href', '') or 'pdf' in a.get('href', '').lower()]
    print(f"   Enlaces que parecen documentos: {len(doc_links)}")

    for i, link in enumerate(doc_links[:10], 1):
        href = link.get('href', '')
        text = link.get_text(strip=True)[:40]
        print(f"      {i}. href={href:50} text='{text}'")

    print("\n6️⃣ Estructura HTML de los resultados (primeros 2000 caracteres)...")

    # Buscar divs con clase "doc item list row" (documentos)
    containers = soup.find_all('div', class_=lambda x: x and 'doc' in str(x) and 'item' in str(x))

    if containers:
        print(f"   Contenedores encontrados: {len(containers)}")
        for i, container in enumerate(containers[:3], 1):
            print(f"\n   Contenedor {i}:")
            print(f"      HTML completo del contenedor:")
            print(container.prettify()[:1500])

            # Buscar todos los enlaces en este contenedor
            links_in_container = container.find_all('a', href=True)
            print(f"\n      Enlaces en este contenedor: {len(links_in_container)}")
            for j, link in enumerate(links_in_container[:5], 1):
                href = link.get('href')
                text = link.get_text(strip=True)[:40]
                print(f"         {j}. href={href:60} text='{text}'")
    else:
        print("   No se encontraron contenedores de documentos")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
