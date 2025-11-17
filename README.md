# CatLux Scrapper - Descargador inteligente de PDFs

Descargador automático de exámenes y soluciones de [CatLux](https://www.catlux.de) con control de límite mensual (100 PDFs/mes).

## 🚀 Características

- **Control de límite mensual**: Máximo 100 descargas/mes (limite de CatLux)
- **Evita duplicados**: Solo descarga si el archivo no existe ya
- **Descarga inteligente**: Solo descarga solución si el examen existe
- **Tracking de descargas**: Ve tu saldo disponible en cualquier momento
- **Multiplataforma**: Funciona en Windows, macOS y Linux
- **Logging detallado**: Archivo de log para auditar descargas
- **Credenciales seguras**: Usa archivo `.env` (no versionado en git)

## 📋 Requisitos

- Python 3.7+
- Conexión a Internet
- Cuenta activa en [CatLux.de](https://www.catlux.de)

## 🔧 Instalación

### 1. Clonar/Actualizar el repositorio

```bash
cd CatluxScrapper
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install requests beautifulsoup4 python-dotenv
```

### 3. Configurar credenciales

1. Copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

2. Edita `.env` y completa:

```ini
CATLUX_USERNAME=tu_email@gmail.com
CATLUX_PASSWORD=tu_contraseña
CATLUX_SAVE_PATH=/ruta/donde/guardar/pdfs
```

### Rutas de ejemplo

**Windows:**
```ini
CATLUX_SAVE_PATH=C:\Users\TuUsuario\Documents\Catlux
```

**macOS/Linux:**
```ini
CATLUX_SAVE_PATH=/Users/TuUsuario/Documentos/Catlux
# o
CATLUX_SAVE_PATH=/home/tuUsuario/Documentos/Catlux
```

## 📖 Uso

### 1️⃣ PASO 1: Ver preview de PDFs (RECOMENDADO)

Antes de descargar, ve qué PDFs encontró el script:

```bash
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/" --preview
```

Salida:
```
======================================================================
📋 PREVIEW DE PDFS ENCONTRADOS
======================================================================

📚 Clase: KLASSE-7
📖 Asignatura: DEUTSCH

✓ 28 PDFs encontrados
  - Exámenes: 14
  - Soluciones: 14

----------------------------------------------------------------------
Archivos encontrados:
----------------------------------------------------------------------
  1. [✓] 119215 (solución)
  2. [✓] 118065 (solución)
  3. [✓] 112650 (solución)
  4. [⊘] 113649 (sin solución)
  ...
----------------------------------------------------------------------
Total: 28 PDFs
======================================================================
```

**Símbolos:**
- `[✓]` = Tiene examen Y solución
- `[⊘]` = Solo examen (sin solución)

### 2️⃣ PASO 2: Descargar PDFs

Después de verificar el preview, descarga:

```bash
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/" --download
```

El script:
1. Muestra el preview nuevamente
2. Descarga solo PDFs nuevos (evita duplicados)
3. Solo descarga soluciones si el examen existe
4. Muestra el saldo después de descargar

### 3️⃣ PASO 3: Ver estado de descargas

```bash
python catlux_scrapper.py --info
```

Salida:
```
============================================================
📊 ESTADO DE DESCARGAS
============================================================
Mes actual: November 2024
Descargas este mes: 45/100
Descargas disponibles: 55
Total histórico: 247
✅ 55 descargas disponibles
============================================================
```

### 4️⃣ PASO 4: Ver últimas descargas realizadas

```bash
python catlux_scrapper.py --latest
```

Salida:
```
============================================================
📥 ÚLTIMAS DESCARGAS (máximo 20)
============================================================
 1. [2024-11-17] 119215.pdf
 2. [2024-11-17] 119215_solution.pdf
 3. [2024-11-17] 118065.pdf
 4. [2024-11-17] 118065_solution.pdf
...
============================================================
```

### Opciones

- `--url URL`: URL base de la clase a procesar
- `--pages N`: Número máximo de páginas (default: 10)
- `--preview`: Mostrar preview SIN descargar
- `--download`: Descargar después de preview
- `--info`: Ver estado de descargas este mes
- `--latest`: Ver últimas 20 descargas realizadas
- `--reset-tracker`: ⚠️ Borrar historial (CUIDADO)

### Flujo recomendado

```bash
# 1. Ver saldo disponible
python catlux_scrapper.py --info

# 2. Ver qué PDFs hay en Deutsch
python catlux_scrapper.py --url "...klasse-7/deutsch/" --preview

# 3. Si todo está bien, descargar
python catlux_scrapper.py --url "...klasse-7/deutsch/" --download

# 4. Ver saldo después de descargar
python catlux_scrapper.py --info

# 5. Repetir para otras asignaturas
python catlux_scrapper.py --url "...klasse-7/mathematik/" --preview
python catlux_scrapper.py --url "...klasse-7/mathematik/" --download
```

## 📁 Estructura de carpetas

Los PDFs se guardan automáticamente en esta estructura:

```
CATLUX_SAVE_PATH/
└── klasse-7/
    ├── deutsch/
    │   ├── 119215.pdf
    │   ├── 119215_solution.pdf
    │   ├── 118065.pdf
    │   └── ...
    ├── mathematik/
    │   └── ...
    └── ...
```

## 📊 Archivos generados

### `download_tracker.json`

Registra todas las descargas realizadas:

```json
{
  "downloads": [
    {
      "date": "2024-11-17T14:30:45.123456",
      "filename": "119215.pdf"
    },
    {
      "date": "2024-11-17T14:31:12.654321",
      "filename": "119215_solution.pdf"
    }
  ],
  "total_all_time": 247
}
```

### `catlux_scrapper.log`

Log detallado de todas las operaciones:

```
2024-11-17 14:30:42 - INFO - Iniciando descarga desde: https://www.catlux.de/...
2024-11-17 14:30:43 - INFO - ✓ Login exitoso
2024-11-17 14:30:45 - INFO - ⬇ 119215.pdf - descargado (54 restantes)
```

## ⚠️ Límite de descargas

CatLux limita a **100 descargas por mes calendario**.

- **Mes calendario**: Enero-Enero, Febrero-Febrero, etc.
- **Contador**: Se reinicia automáticamente el 1º de cada mes
- **Recomendación**: Usa `--info` antes de descargar para ver tu saldo

Ejemplo de estrategia para 7a Klasse con 3 asignaturas:

```bash
# Octubre 1-31: Descargar 33 PDFs por asignatura (Deutsch, Mathematik, Englisch)
# - Deutsch: 10 páginas = ~30-35 PDFs
# - Mathematik: 5 páginas = ~20-25 PDFs
# - Englisch: 5 páginas = ~15-20 PDFs

# Ver saldo
python catlux_scrapper.py --info

# Descargar prioridades
python catlux_scrapper.py --url "...klasse-7/deutsch/" --pages 10
python catlux_scrapper.py --url "...klasse-7/mathematik/" --pages 8
python catlux_scrapper.py --url "...klasse-7/englisch/" --pages 8
```

## 🔒 Seguridad

### Credenciales

- Las credenciales se guardan en `.env` (archivo ignorado por git)
- ⚠️ El archivo `.env` contiene datos sensibles - NUNCA lo commits
- ⚠️ NUNCA compartas el archivo `.env`
- Considera cambiar la contraseña CatLux periódicamente

### Certificados SSL (avanzado)

Si CatLux usa certificados auto-firmados:

```ini
CATLUX_CERT_PATH=/ruta/al/certificado.crt
```

En macOS con certificado en Keychain:

```bash
security find-certificate -a -p /Library/Keychains/System.keychain | openssl x509 -outform PEM > catlux.crt
```

## 🐛 Troubleshooting

### Error: "Login fallido"

1. Verifica credenciales en `.env`
2. Prueba login manual en https://www.catlux.de
3. Revisa si tu cuenta está activa

### Error: "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### Error: "Permission denied"

Asegúrate que CATLUX_SAVE_PATH existe y tienes permisos:

```bash
mkdir -p "/ruta/donde/guardar/pdfs"
chmod 755 "/ruta/donde/guardar/pdfs"
```

### Descargas muy lentitas

- CatLux puede estar saturado (típico en hora punta)
- Intenta en otra hora del día
- Reduce `--pages` a 5-10

### Límite alcanzado a mitad del mes

- Revisa `download_tracker.json` para ver qué se descargó
- Las descargas pueden haber sido desde el móvil u otro dispositivo
- Espera al mes siguiente (se reinicia automáticamente)

## 📝 Logs

Revisa los logs para entender qué pasó:

```bash
tail -f catlux_scrapper.log

# O en Windows PowerShell:
Get-Content catlux_scrapper.log -Wait
```

Símbolos en logs:
- `✓` = Ya existe (no se descargó)
- `⬇` = Descargado nuevo
- `⊘` = Saltado (ej: solución sin examen)
- `✗` = Error

## 📚 URL de ejemplo para diferentes clases

```bash
# 7a Klasse
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/"
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/mathematik/"
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/englisch/"

# 5a Klasse (anterior)
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-5/deutsch/"

# 6a Klasse
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-6/deutsch/"

# 8a Klasse
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-8/deutsch/"
```

## 🔄 Automatización (opcional)

### Linux/macOS - Cron

Crear `download_schedule.sh`:

```bash
#!/bin/bash
cd /home/usuario/CatluxScrapper
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/" >> download.log 2>&1
```

Agregar a crontab (1er día del mes a las 8 AM):

```bash
crontab -e

# Agregar línea:
0 8 1 * * /home/usuario/CatluxScrapper/download_schedule.sh
```

### Windows - Tareas programadas

1. Abre Task Scheduler (Programador de tareas)
2. Crear tarea básica
3. Trigger: Monthly (1st day)
4. Action: `python C:\path\to\catlux_scrapper.py --url "..."`

## 📈 Métricas

Ver total descargado desde el inicio:

```bash
python -c "import json; print(json.load(open('download_tracker.json'))['total_all_time'])"
```

Descargas este mes:

```bash
python catlux_scrapper.py --info
```

## 📄 Licencia

Uso educativo y personal. Respeta los términos de servicio de CatLux.

## 🤝 Contribuciones

Para reportar bugs o sugerencias, abre un issue en el repositorio.

---

**Última actualización**: Noviembre 2024
**Versión**: 2.0 (Mejorada con control de límites)
