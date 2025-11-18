# CatLux Scrapper - Descargador Inteligente de PDFs

Descargador automático de exámenes y soluciones de [CatLux](https://www.catlux.de) con:
- ✅ Control de límite mensual (100 PDFs/mes)
- ✅ Preview interactivo antes de descargar
- ✅ Evita duplicados automáticamente
- ✅ Descarga soluciones automáticamente con exámenes
- ✅ Búsqueda global de archivos en todas las carpetas
- ✅ Selección interactiva de categorías (Klasse, Asignatura, Tipo)

## 🚀 Características

- **Preview Interactivo**: Ve todos los PDFs disponibles antes de descargar
- **Evita Duplicados**: Solo descarga si el archivo no existe ya
- **Soluciones Automáticas**: Descarga automáticamente la solución junto con el examen
- **Control de Límite**: Máximo 100 descargas/mes (límite de CatLux)
- **Tracking**: Ve tu saldo disponible en cualquier momento
- **Búsqueda Global**: Detecta PDFs descargados en otras carpetas
- **Categorías Interactivas**: Selecciona Klasse, Asignatura y Tipo de forma interactiva
- **Multiplataforma**: Funciona en Windows, macOS y Linux
- **Logging Detallado**: Archivo de log para auditar descargas
- **Credenciales Seguras**: Usa archivo `.env` (no versionado en git)

## 📋 Requisitos

- Python 3.7+
- Conexión a Internet
- Cuenta activa en [CatLux.de](https://www.catlux.de)

## 🔧 Instalación

### 1. Clonar/Descargar el repositorio

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

### Opción 1: Selección Interactiva de Categorías (RECOMENDADO)

La forma más fácil para usuarios nuevos - selecciona categorías de forma interactiva:

```bash
python catlux_scrapper.py --select-category
```

El script te pedirá:
1. **Klasse** (5-12)
2. **Asignatura** (Deutsch, Englisch, Mathematik, Français, Erdkunde-Geographie, Biologie, Chemie, Physik, Natur-und-Technik, Sonstiges, etc.)
3. **Tipo de Documento** (Aufsatz, Schulaufgabe, Extemporale, etc.)

Luego mostrará preview y preguntará qué descargar.

### Opción 2: URL Directa

Si conoces la URL exacta:

```bash
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/"
```

Esto mostrará preview de forma interactiva y preguntará qué descargar.

### Opción 3: Ver Saldo Disponible

```bash
python catlux_scrapper.py --info
```

Salida:
```
============================================================
📊 ESTADO DE DESCARGAS
============================================================
Mes actual: November 2025
Descargas este mes: 45/100
Descargas disponibles: 55
Total histórico: 247
✅ 55 descargas disponibles
============================================================
```

### Opción 4: Ver Últimas Descargas

```bash
python catlux_scrapper.py --latest
```

## 🎯 Flujo Completo Paso a Paso

### Paso 1: Ejecutar con Selección Interactiva

```bash
python catlux_scrapper.py --select-category
```

### Paso 2: Ver Preview

El script mostrará todos los PDFs disponibles:

```
================================================================================
📋 PREVIEW DE PDFS ENCONTRADOS
================================================================================

📚 Clase: KLASSE-7
📖 Asignatura: DEUTSCH

✓ 48 PDFs encontrados
  - Exámenes: 24
  - Soluciones: 24
  - Ya descargados: 1
  - Nuevos: 47

#   | LOC | TIPO     | ID     | REF      | Categoría                       | Título
----|-----|----------|--------|----------|----------------------------------|---
  1 |     | Exam     | 112399 | #0309    | 0. Schulaufgabe, Aufsatz        | begründete Stellungnahme
  2 |     | Solution | 112399 | #0309    | 0. Schulaufgabe, Aufsatz        | begründete Stellungnahme
  3 |     | Exam     | 112780 | #0272    | 1. Schulaufgabe, Aufsatz        | Erlebnisschilderung
  4 |     | Solution | 112780 | #0272    | 1. Schulaufgabe, Aufsatz        | Erlebnisschilderung
 ...
 47 | ✓   | Exam     | 113132 | #0463    | 4. Schulaufgabe, Aufsatz        | begründete Stellungnahme
 48 |     | Solution | 113132 | #0463    | 4. Schulaufgabe, Aufsatz        | begründete Stellungnahme
================================================================================
Total: 48 PDFs (24 exámenes + 24 soluciones)
Leyenda: LOC=Local (✓=descargado, -=nuevo), TIPO=Exam/Solution, ID=ID descarga, REF=Referencia CatLux
================================================================================
```

**Leyenda:**
- `#` = Número de fila (1-48)
- `LOC` = Local (✓ = ya descargado, espacio = nuevo)
- `TIPO` = Tipo (Exam = examen, Solution = solución)
- `ID` = ID interno de CatLux para descargar
- `REF` = Número de referencia de CatLux (ordenado ascendentemente #0272, #0309, etc.)
- `Categoría` = Tipo de ejercicio (Schulaufgabe, Aufsatz, etc.)
- `Título` = Nombre del documento (hasta 75 caracteres)

### Paso 3: Seleccionar PDFs a Descargar

El script preguntará interactivamente:

```
================================================================================
📥 SELECCIONAR PDFS PARA DESCARGAR
================================================================================

Opciones de descarga:
  0. Descargar TODOS (incluyendo archivos ya descargados)
  1. Descargar solo NUEVOS (archivos que no existen aún)
  2. Seleccionar números específicos (ej: 1,3,5)

Opciones de navegación:
  8. NO descargar nada (salir)
  9. Volver atrás (seleccionar otras categorías)

================================================================================

Selección: _
```

**Ejemplos de selección:**

1. **Descargar todos (incluyendo ya descargados):**
   ```
   Selección: 0
   ```

2. **Solo los nuevos:**
   ```
   Selección: 1
   ```

3. **Específicos (1, 3, 5):**
   ```
   Selección: 2
   Escribe números (ej: 1,3,5): 1,3,5
   ```

4. **No descargar nada (salir):**
   ```
   Selección: 8
   ```

5. **Volver atrás para otra categoría:**
   ```
   Selección: 9
   ```

### Paso 4: Descarga Automática

El script descargará los PDFs seleccionados:

```
🔄 Iniciando descargas...

2025-11-18 14:30:45 - INFO - ⬇ 112399.pdf - descargado (98 restantes)
2025-11-18 14:30:46 - INFO - ⬇ 112399_solution.pdf - descargado (97 restantes)
2025-11-18 14:30:48 - INFO - ✓ 119215.pdf - ya existe
2025-11-18 14:30:50 - INFO - ⬇ 118065.pdf - descargado (96 restantes)
2025-11-18 14:30:52 - INFO - ⬇ 118065_solution.pdf - descargado (95 restantes)
...

🔄 Descarga completada: 4 nuevos PDFs
```

### Paso 5: Estado Final

```
============================================================
📊 ESTADO DE DESCARGAS
============================================================
Mes actual: November 2025
Descargas este mes: 48/100
Descargas disponibles: 52
Total histórico: 247
✅ 52 descargas disponibles
============================================================
```

## 🔄 Descarga Automática de Soluciones

**Característica principal:** Cuando seleccionas un examen, **automáticamente se descarga su solución**.

Ejemplo:
```
Usuario selecciona: 1,3,5 (índices de exámenes)
    ↓
Script procesa índice 1 (examen 112399):
  ⬇ 112399.pdf - descargado
  ⬇ 112399_solution.pdf - descargado (automáticamente)
    ↓
Script procesa índice 3 (examen 112780):
  ⬇ 112780.pdf - descargado
  ⬇ 112780_solution.pdf - descargado (automáticamente)
```

**Conteo inteligente:**
- Cada PDF = 1 descarga
- Seleccionar 5 exámenes ≈ 10 descargas (5 exam + 5 solutions)
- El script es honesto con el contador de CatLux (100/mes)

## 📁 Estructura de Carpetas

Los PDFs se guardan automáticamente así:

```
CATLUX_SAVE_PATH/
├── klasse-7/
│   ├── deutsch/
│   │   ├── 112399.pdf
│   │   ├── 112399_solution.pdf
│   │   ├── 118065.pdf
│   │   ├── 118065_solution.pdf
│   │   └── ...
│   ├── mathematik/
│   │   └── ...
│   └── ...
├── klasse-8/
│   ├── englisch/
│   └── ...
└── ...
```

## 📊 Archivos Generados

### `download_tracker.json`

Registra todas las descargas realizadas:

```json
{
  "downloads": [
    {
      "date": "2025-11-18T14:30:45.123456",
      "filename": "119215.pdf"
    },
    {
      "date": "2025-11-18T14:30:47.654321",
      "filename": "119215_solution.pdf"
    }
  ],
  "total_all_time": 247
}
```

### `catlux_scrapper.log`

Log detallado de todas las operaciones:

```
2025-11-18 14:30:42 - INFO - Iniciando preview desde: https://www.catlux.de/...
2025-11-18 14:30:43 - INFO - ✓ Login exitoso
2025-11-18 14:30:45 - INFO - ⬇ 119215.pdf - descargado (54 restantes)
```

## ⚠️ Límite de Descargas

CatLux limita a **100 descargas por mes calendario**.

- **Mes calendario**: Enero-Enero, Febrero-Febrero, etc.
- **Contador**: Se reinicia automáticamente el 1º de cada mes
- **Recomendación**: Usa `--info` antes de descargar para ver tu saldo

## 🔒 Seguridad

### Credenciales

- Las credenciales se guardan en `.env` (archivo ignorado por git)
- ⚠️ El archivo `.env` contiene datos sensibles - **NUNCA lo commits**
- ⚠️ **NUNCA compartas** el archivo `.env**
- Considera cambiar la contraseña CatLux periódicamente

### Certificados SSL (avanzado)

Si CatLux usa certificados auto-firmados:

```ini
CATLUX_CERT_PATH=/ruta/al/certificado.crt
```

## 🐛 Troubleshooting

### Error: "Login fallido"

1. Verifica credenciales en `.env`
2. Prueba login manual en https://www.catlux.de
3. Verifica que tu cuenta está activa

### Error: "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### Error: "Permission denied"

Asegúrate que `CATLUX_SAVE_PATH` existe y tienes permisos:

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

## 📚 URLs de Ejemplo

```bash
# 7ª Klasse - Deutsch
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/"

# 7ª Klasse - Mathematik
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/mathematik/"

# 7ª Klasse - Englisch
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/englisch/"

# 7ª Klasse - Franzoesisch (nota: sin acentos)
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/franzoesisch/"

# 7ª Klasse - Erdkunde-Geographie
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/erdkunde-geographie/"

# 5ª Klasse - Deutsch
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-5/deutsch/"

# Con filtro por tipo:
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/aufsatz"
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
4. Action: `python C:\path\to\catlux_scrapper.py --select-category`

## 📈 Métricas

Ver total descargado desde el inicio:

```bash
python -c "import json; data=json.load(open('download_tracker.json')); print(f'Total histórico: {data.get(\"total_all_time\", 0)} PDFs')"
```

Descargas este mes:

```bash
python catlux_scrapper.py --info
```

## 📄 Licencia

Uso educativo y personal. Respeta los términos de servicio de CatLux.

## 🤝 Contribuciones

Para reportar bugs o sugerencias, abre un issue en el repositorio.

## 📖 Documentación Completa

Para más detalles, revisa:
- `WORKFLOW.md` - Guía detallada del flujo de trabajo
- `CHANGES_SUMMARY.md` - Resumen técnico de cambios
- `INSTALLATION.md` - Guía de instalación paso a paso

---

**Última actualización**: Noviembre 2025
**Versión**: 3.0 (Versión final con código limpio y documentación completa)
**Estado**: ✅ Producción
