#!/usr/bin/env python3
"""
Setup interactivo para configurar CatLux Scrapper

Este script te ayuda a crear el archivo .env con tu configuración.
"""

import os
import sys
from pathlib import Path

def setup_config():
    """Configura el archivo .env de forma interactiva."""

    print("\n" + "="*60)
    print("⚙️  CONFIGURACIÓN DE CATLUX SCRAPPER")
    print("="*60 + "\n")

    # Verificar si ya existe .env
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print("⚠️  Ya existe un archivo .env")
        response = input("¿Deseas sobrescribir la configuración? (s/n): ").lower()
        if response != 's':
            print("Configuración cancelada")
            return 1

    print("\n📧 CREDENCIALES CATLUX")
    print("-" * 60)

    # Email
    email = input("Tu email de CatLux: ").strip()
    if not email or "@" not in email:
        print("❌ Email inválido")
        return 1

    # Contraseña
    import getpass
    password = getpass.getpass("Tu contraseña: ")
    if not password:
        print("❌ Contraseña vacía")
        return 1

    print("\n📁 RUTA DE DESCARGA")
    print("-" * 60)
    print("Ejemplos:")
    print("  Windows: C:\\Users\\TuUsuario\\Documents\\Catlux")
    print("  Linux: /home/tuUsuario/Documentos/Catlux")
    print("  macOS: /Users/TuUsuario/Documentos/Catlux")

    save_path = input("\nRuta donde guardar los PDFs: ").strip()
    if not save_path:
        print("❌ Ruta vacía")
        return 1

    # Crear carpeta si no existe
    Path(save_path).mkdir(parents=True, exist_ok=True)

    print("\n🔒 CERTIFICADO SSL (opcional)")
    print("-" * 60)
    print("¿Necesitas usar un certificado SSL específico? (responde con Enter si no)")

    cert_path = input("Ruta del certificado (.crt): ").strip()

    # Generar contenido del .env
    env_content = f"""# CatLux Scrapper - Configuración
# Generado automáticamente por setup_config.py

# Credenciales
CATLUX_USERNAME={email}
CATLUX_PASSWORD={password}

# Ruta de descarga
CATLUX_SAVE_PATH={save_path}
"""

    if cert_path:
        env_content += f"\n# Certificado SSL\nCATLUX_CERT_PATH={cert_path}\n"

    # Guardar archivo
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)

    # Permisos restrictivos (solo propietario puede leer)
    os.chmod(env_file, 0o600)

    print("\n" + "="*60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("="*60)
    print(f"\n✓ Archivo .env creado: {env_file}")
    print(f"✓ Ruta de descarga: {save_path}")
    print(f"✓ Usuario: {email}")
    print("\n📝 Próximos pasos:")
    print("  1. Verifica que la configuración sea correcta")
    print("  2. Ejecuta: python catlux_scrapper.py --info")
    print("  3. Descarga: python catlux_scrapper.py --url 'https://...'")
    print("\n⚠️  Recuerda:")
    print("  - Nunca compartas el archivo .env")
    print("  - El archivo .env está en .gitignore (seguro)")
    print("  - Cambia tu contraseña CatLux periódicamente")

    return 0

if __name__ == '__main__':
    try:
        sys.exit(setup_config())
    except KeyboardInterrupt:
        print("\n\n❌ Configuración cancelada")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
