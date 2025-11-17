#!/usr/bin/env python3
"""
Script de debug para el login de CatLux
Ayuda a identificar qué cambió en el formulario de login
"""

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

LOGIN_URL = "https://www.catlux.de/login"
username = os.getenv("CATLUX_USERNAME")
password = os.getenv("CATLUX_PASSWORD")

print(f"Email: {username}")
print(f"URL de login: {LOGIN_URL}\n")

try:
    print("1️⃣ Intentando obtener la página de login...")
    response = requests.get(LOGIN_URL, timeout=10)
    print(f"   Status: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')

    print("\n2️⃣ Buscando formulario de login...")
    form = soup.find('form')
    if form:
        print(f"   Formulario encontrado: {form.get('action', 'N/A')}")
        print(f"   Método: {form.get('method', 'N/A')}\n")

        print("3️⃣ Inputs del formulario:")
        for input_field in form.find_all('input'):
            name = input_field.get('name', '')
            input_type = input_field.get('type', '')
            value = input_field.get('value', '')[:50]  # Primeros 50 chars
            print(f"   - {name:20} (type: {input_type:10}) = {value}")
    else:
        print("   ❌ No se encontró formulario")

    print("\n4️⃣ HTML completo del formulario:")
    if form:
        print(form.prettify()[:1000])  # Primeros 1000 chars

except Exception as e:
    print(f"❌ Error: {e}")
