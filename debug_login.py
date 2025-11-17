#!/usr/bin/env python3
"""
Script de debug para el login de CatLux
Ayuda a identificar qué cambió en el formulario de login
"""

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import urllib3

# Desactivar advertencia de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

LOGIN_URL = "https://www.catlux.de/login"
username = os.getenv("CATLUX_USERNAME")
password = os.getenv("CATLUX_PASSWORD")

print(f"Email: {username}")
print(f"URL de login: {LOGIN_URL}\n")

try:
    print("1️⃣ Intentando obtener la página de login (sin verificar SSL)...")
    response = requests.get(LOGIN_URL, verify=False, timeout=10)
    print(f"   Status: {response.status_code}\n")

    soup = BeautifulSoup(response.content, 'html.parser')

    print("2️⃣ Buscando TODOS los formularios en la página...")
    forms = soup.find_all('form')
    print(f"   Total de formularios encontrados: {len(forms)}\n")

    for i, form in enumerate(forms, 1):
        print(f"   Formulario {i}:")
        print(f"      Action: {form.get('action', 'N/A')}")
        print(f"      Method: {form.get('method', 'N/A')}")
        print(f"      ID: {form.get('id', 'N/A')}")
        print(f"      Inputs:")
        for input_field in form.find_all('input'):
            name = input_field.get('name', '')
            input_type = input_field.get('type', '')
            value = input_field.get('value', '')[:30]
            print(f"         - {name:20} (type: {input_type:10}) = {value}")
        print()

    print("3️⃣ Buscando token REQUEST_TOKEN en toda la página...")
    request_token = soup.find('input', {'name': 'REQUEST_TOKEN'})
    if request_token:
        print(f"   ✓ REQUEST_TOKEN encontrado: {request_token.get('value', 'N/A')[:50]}")
    else:
        print("   ❌ REQUEST_TOKEN NO encontrado")

    print("\n4️⃣ Buscando otros posibles tokens...")
    for token_name in ['csrf_token', '_token', 'token', 'nonce']:
        token = soup.find('input', {'name': token_name})
        if token:
            print(f"   ✓ {token_name}: {token.get('value', 'N/A')[:50]}")

    print("\n5️⃣ Buscando elementos de login (input con name=username o password)...")
    username_input = soup.find('input', {'name': lambda x: x and 'user' in x.lower()})
    password_input = soup.find('input', {'name': lambda x: x and 'pass' in x.lower()})

    if username_input:
        print(f"   ✓ Usuario input encontrado: {username_input.get('name')}")
    else:
        print(f"   ❌ Usuario input NO encontrado")

    if password_input:
        print(f"   ✓ Password input encontrado: {password_input.get('name')}")
    else:
        print(f"   ❌ Password input NO encontrado")

    print("\n6️⃣ Primeros 2000 caracteres del HTML de la página:")
    print(str(soup)[:2000])

except Exception as e:
    print(f"❌ Error: {e}")
