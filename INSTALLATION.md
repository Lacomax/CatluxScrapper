# Guía de Instalación - CatLux Scrapper

Guía paso a paso para instalar y configurar CatLux Scrapper en tu sistema.

## Índice

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación Completa](#instalación-completa)
3. [Configuración de Credenciales](#configuración-de-credenciales)
4. [Verificación de Instalación](#verificación-de-instalación)
5. [Instalación en Diferentes Sistemas](#instalación-en-diferentes-sistemas)
6. [Solución de Problemas](#solución-de-problemas)

## Requisitos Previos

### Software Requerido

- **Python 3.7 o superior**
  - Windows: Descarga de [python.org](https://www.python.org/downloads/)
  - macOS: `brew install python3` o desde [python.org](https://www.python.org/downloads/)
  - Linux: `sudo apt-get install python3 python3-pip` (Ubuntu/Debian)

- **Git** (opcional, para clonar el repositorio)
  - Windows: [git-scm.com](https://git-scm.com/)
  - macOS: `brew install git`
  - Linux: `sudo apt-get install git`

- **Cuenta activa en CatLux**
  - Email y contraseña para acceder a https://www.catlux.de

### Verificar versión de Python

Abre una terminal/consola y ejecuta:

```bash
python3 --version
```

Debería mostrar algo como: `Python 3.7.x` o superior

## Instalación Completa

### Paso 1: Descargar el Repositorio

#### Opción A: Con Git (Recomendado)

```bash
git clone https://github.com/tu-usuario/CatluxScrapper.git
cd CatluxScrapper
```

#### Opción B: Sin Git

1. Ve a https://github.com/tu-usuario/CatluxScrapper
2. Haz clic en "Code" → "Download ZIP"
3. Extrae el archivo ZIP
4. Abre la carpeta extraída en tu terminal

### Paso 2: Instalar Dependencias

Desde la carpeta del proyecto:

```bash
pip install -r requirements.txt
```

Esto instalará:
- `requests==2.31.0` - Para hacer peticiones HTTP
- `beautifulsoup4==4.12.2` - Para parsear HTML
- `python-dotenv==1.0.0` - Para leer variables de entorno

**Alternativa manual** (sin requirements.txt):

```bash
pip install requests beautifulsoup4 python-dotenv
```

### Paso 3: Crear Archivo de Configuración

1. Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Esto crea un archivo `.env` con la estructura necesaria.

2. Abre el archivo `.env` con tu editor de texto favorito

3. Completa las siguientes variables:

```ini
CATLUX_USERNAME=tu_email@gmail.com
CATLUX_PASSWORD=tu_contraseña
CATLUX_SAVE_PATH=/ruta/donde/guardar/pdfs
```

### Paso 4: Crear Carpeta de Destino

Asegúrate de que la carpeta donde guardarás los PDFs existe:

#### Windows

```cmd
mkdir "C:\Users\TuUsuario\Documents\Catlux"
```

#### macOS/Linux

```bash
mkdir -p ~/Documentos/Catlux
```

## Configuración de Credenciales

### El archivo `.env`

El archivo `.env` contiene tus credenciales. **Es muy importante que:**

1. **NUNCA lo commits a Git**
   - El archivo ya está en `.gitignore`, así que Git lo ignorará automáticamente

2. **NUNCA lo compartas**
   - No lo envíes por email, WhatsApp, etc.

3. **Mantenlo seguro**
   - Guarda un backup en un lugar seguro si necesitas cambiar sistemas

### Ejemplo de `.env` correctamente configurado

**Windows:**
```ini
CATLUX_USERNAME=tu_email@gmail.com
CATLUX_PASSWORD=tu_contraseña_segura
CATLUX_SAVE_PATH=C:\Users\TuUsuario\Documents\Catlux
```

**macOS:**
```ini
CATLUX_USERNAME=tu_email@gmail.com
CATLUX_PASSWORD=tu_contraseña_segura
CATLUX_SAVE_PATH=/Users/TuUsuario/Documents/Catlux
```

**Linux:**
```ini
CATLUX_USERNAME=tu_email@gmail.com
CATLUX_PASSWORD=tu_contraseña_segura
CATLUX_SAVE_PATH=/home/tu_usuario/Documentos/Catlux
```

### Cambiar la Contraseña

Si cambias tu contraseña en CatLux:

1. Edita `.env`
2. Actualiza `CATLUX_PASSWORD` con la nueva contraseña
3. Guarda el archivo

## Verificación de Instalación

### Paso 1: Verificar Python

```bash
python3 --version
```

### Paso 2: Verificar Dependencias

```bash
python3 -c "import requests, bs4, dotenv; print('✅ Todas las dependencias instaladas correctamente')"
```

### Paso 3: Verificar Archivo de Configuración

```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(f'✅ .env cargado: USERNAME={os.getenv(\"CATLUX_USERNAME\")}')"
```

### Paso 4: Primer Uso

Prueba el script:

```bash
python3 catlux_scrapper.py --info
```

Si ves el estado de descargas, ¡la instalación fue exitosa! ✅

## Instalación en Diferentes Sistemas

### Windows

**PowerShell:**

```powershell
# Verificar Python
python --version

# Instalar dependencias
pip install -r requirements.txt

# Copiar .env
Copy-Item .env.example -Destination .env

# Editar .env (abre Notepad)
notepad .env

# Probar
python catlux_scrapper.py --info
```

**CMD (Símbolo del Sistema):**

```cmd
REM Verificar Python
python --version

REM Instalar dependencias
pip install -r requirements.txt

REM Copiar .env
copy .env.example .env

REM Editar .env (abre Notepad)
notepad .env

REM Probar
python catlux_scrapper.py --info
```

### macOS

```bash
# Verificar Python
python3 --version

# Instalar dependencias
pip3 install -r requirements.txt

# Copiar .env
cp .env.example .env

# Editar .env (abre TextEdit o vi)
nano .env

# Probar
python3 catlux_scrapper.py --info
```

### Linux (Ubuntu/Debian)

```bash
# Instalar Python (si no lo tienes)
sudo apt-get update
sudo apt-get install python3 python3-pip

# Clonar repositorio
git clone https://github.com/tu-usuario/CatluxScrapper.git
cd CatluxScrapper

# Instalar dependencias
pip3 install -r requirements.txt

# Copiar .env
cp .env.example .env

# Editar .env
nano .env

# Probar
python3 catlux_scrapper.py --info
```

### Linux (Fedora/RedHat)

```bash
# Instalar Python
sudo dnf install python3 python3-pip

# Resto igual que Ubuntu
```

## Solución de Problemas

### Error: "python: command not found"

**Causa:** Python no está instalado o no está en PATH

**Solución:**
1. Descarga Python desde https://www.python.org/downloads/
2. Durante la instalación, marca "Add Python to PATH"
3. Reinicia tu terminal/consola

### Error: "ModuleNotFoundError: No module named 'requests'"

**Causa:** Las dependencias no están instaladas

**Solución:**
```bash
pip install -r requirements.txt
```

### Error: "cannot open file '.env': [Errno 2]"

**Causa:** El archivo `.env` no existe

**Solución:**
```bash
cp .env.example .env
# Luego edita .env con tus credenciales
```

### Error: "Login fallido"

**Causa:** Credenciales incorrectas o cuenta inactiva

**Solución:**
1. Verifica que tu email y contraseña son correctos
2. Abre https://www.catlux.de y prueba login manual
3. Verifica que tu cuenta está activa (no está suspendida)

### Error: "Permission denied" en carpeta de guardado

**Causa:** No tienes permisos de escritura

**Solución:**

**Windows:**
1. Click derecho en la carpeta → Propiedades
2. Pestaña "Seguridad" → Editar
3. Selecciona tu usuario y marca "Control Total"

**macOS/Linux:**
```bash
mkdir -p ~/Documentos/Catlux
chmod 755 ~/Documentos/Catlux
```

### Error: "SSL: CERTIFICATE_VERIFY_FAILED"

**Causa:** Problema con certificado SSL (raro)

**Solución:**

Si tienes un certificado personalizado:

1. Obtén el certificado `.crt` de tu administrador
2. Agregalo a `.env`:
   ```ini
   CATLUX_CERT_PATH=/ruta/al/certificado.crt
   ```

### El script va muy lento

**Causa:** CatLux sobrecargado o conexión lenta

**Solución:**
- Intenta en otra hora (mejor por la noche/madrugada)
- Reduce el parámetro `--pages` a 5-10
- Verifica tu velocidad de conexión

### "CATLUX_SAVE_PATH not configured"

**Causa:** Falta configurar la ruta de guardado

**Solución:**
1. Abre `.env`
2. Agrega:
   ```ini
   CATLUX_SAVE_PATH=/ruta/valida/a/carpeta
   ```
3. Asegúrate de que la carpeta existe

## Actualizar Instalación

Si en el futuro hay nuevas versiones:

```bash
# Con Git
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Verifica cambios en .env.example
diff .env .env.example
```

## Desinstalación

Si quieres remover el script:

```bash
# Desinstalar dependencias Python
pip uninstall -r requirements.txt

# Eliminar carpeta del proyecto
rm -rf CatluxScrapper
```

**IMPORTANTE:** Guarda tus PDFs descargados antes de eliminar la carpeta.

## Próximos Pasos

Después de la instalación, puedes:

1. Leer `README.md` para entender cómo usarlo
2. Ejecutar con categorías interactivas:
   ```bash
   python3 catlux_scrapper.py --select-category
   ```
3. Revisar `WORKFLOW.md` para casos de uso avanzados

---

**¿Problemas?** Revisa el log en `catlux_scrapper.log`:

```bash
tail -f catlux_scrapper.log
```
