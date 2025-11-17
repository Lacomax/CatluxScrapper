# CatLux Scrapper - Flujo de Trabajo Mejorado

## ✨ Características Nuevas

El script ahora integra:
1. **Preview interactivo** - Ve todos los PDFs disponibles
2. **Detección de archivos locales** - Muestra cuáles ya están descargados
3. **Selección interactiva** - Elige qué PDFs descargar antes de descargar
4. **Control de límites** - Respeta el límite de 100 descargas/mes
5. **Evita duplicados** - No descarga si ya existe

## 📋 Flujo Completo

### Paso 1: Ver Preview de PDFs

```bash
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/"
```

**Resultado:**
```
======================================================================
📋 PREVIEW DE PDFS ENCONTRADOS
======================================================================

📚 Clase: KLASSE-7
📖 Asignatura: DEUTSCH

✓ 28 PDFs encontrados
  - Exámenes: 14
  - Soluciones: 14
  - Ya descargados: 2
  - Nuevos: 26

----------------------------------------------------------------------
#  | EST | LOC | ID     | Ref     | Tipo                          | Título
----------------------------------------------------------------------
1  | ✓   | D   | 119215 | #3426   | Schulaufgabe                  | Deutsch Aufsatz Test
2  | ✓   | D   | 118065 | #3425   | Aufsatz                       | Deutsch Essay Practice
3  | ✓   |     | 117356 | #3424   | Schulaufgabe                  | Deutsch Grammar
...
----------------------------------------------------------------------
Total: 28 PDFs (14 exámenes + 14 soluciones)
Leyenda: EST=Estado (✓=par, ⊘=uno), LOC=Local (D=descargado, -=nuevo), ID=ID descarga, Ref=Ref# CatLux
======================================================================
```

**Explicación:**
- `#` = Número de fila (1-28)
- `EST` = Estado (✓ = examen + solución, ⊘ = solo examen)
- `LOC` = Local (D = ya descargado, espacio = nuevo)
- `ID` = ID interno de CatLux para descargar
- `Ref` = Número de referencia de CatLux
- `Tipo` = Categoría (Schulaufgabe, Aufsatz, etc.)
- `Título` = Nombre del documento

### Paso 2: Seleccionar PDFs a Descargar

Después del preview, el script pregunta:

```
================================================================================
📥 SELECCIONAR PDFS PARA DESCARGAR
================================================================================

Opciones:
  - Escribe 'all' para descargar TODOS los PDFs nuevos
  - Escribe 'none' para NO descargar nada
  - Escribe números separados por comas: 1,3,5 para descargar esos
  - Escribe 'new' para descargar solo los NUEVOS (no los ya descargados)

================================================================================

Selección: _
```

**Opciones:**

1. **Descargar todos los nuevos**
   ```
   Selección: all
   ```
   → Descarga todos los 26 PDFs nuevos

2. **No descargar nada**
   ```
   Selección: none
   ```
   → Cancela, no descarga nada

3. **Solo nuevos**
   ```
   Selección: new
   ```
   → Descarga solo los PDFs que no existen localmente (26)

4. **PDFs específicos**
   ```
   Selección: 1,3,5,7
   ```
   → Descarga solo esos 4 PDFs

### Paso 3: Descargas

```
🔄 Iniciando descargas...

2024-11-17 14:30:45 - INFO - ⬇ 119215_solution.pdf - descargado (55 restantes)
2024-11-17 14:30:47 - INFO - ✓ 119215.pdf - ya existe
2024-11-17 14:30:49 - INFO - ⬇ 118065.pdf - descargado (54 restantes)
2024-11-17 14:30:51 - INFO - ⬇ 118065_solution.pdf - descargado (53 restantes)
2024-11-17 14:30:53 - INFO - Descarga completada: 3 nuevos PDFs
```

**Comportamiento:**
- ✓ = PDF ya existe (no se descarga)
- ⬇ = PDF descargado (nuevo)
- ⊘ = Solución saltada (examen no existe)
- Muestra descargas restantes

### Paso 4: Estado Final

```
============================================================
📊 ESTADO DE DESCARGAS
============================================================
Mes actual: November 2024
Descargas este mes: 48/100
Descargas disponibles: 52
Total histórico: 247
✅ 52 descargas disponibles
============================================================
```

## 🔍 Detección de Archivos Locales

El script automáticamente:

1. **Escanea la carpeta local** en `CATLUX_SAVE_PATH/klasse-X/fach/`
2. **Marca con "D"** los PDFs que ya existen
3. **Muestra en gris** los nuevos
4. **En "new" selection**: Solo descarga PDFs que no existen

Ejemplo:
```
Carpeta local: /home/usuario/Documentos/Catlux/klasse-7/deutsch/
  ✓ 119215.pdf (existe)
  ✓ 119215_solution.pdf (existe)
  ☐ 118065.pdf (no existe)
  ☐ 118065_solution.pdf (no existe)
```

## 📊 Estructura de Carpetas

Los PDFs se guardan automáticamente así:

```
CATLUX_SAVE_PATH/
└── klasse-7/
    └── deutsch/
        ├── 119215.pdf
        ├── 119215_solution.pdf
        ├── 118065.pdf
        ├── 118065_solution.pdf
        └── ...
```

## ⚠️ Control de Límites

- **Límite**: 100 PDFs/mes
- **Período**: Mes calendario (1-31)
- **Reinicio**: Automático el 1º de cada mes
- **Tracking**: En `download_tracker.json`

El script:
1. Verifica saldo disponible antes de descargar
2. Detiene si se alcanza el límite (100/100)
3. Muestra descargas restantes en tiempo real
4. Avisa si quedan ≤10 descargas

## 🎯 Casos de Uso

### Caso 1: Primera descarga de una asignatura
```bash
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/"
```
→ Preview muestra 0 descargados, todos son nuevos
→ Selecciona "all" para descargar todos
→ Script descarga todos

### Caso 2: Actualizar con nuevos exámenes
```bash
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/"
```
→ Preview muestra qué está descargado (D) y qué no
→ Selecciona "new" para descargar solo nuevos
→ Script descarga solo los nuevos

### Caso 3: Descargar específicos
```bash
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/"
```
→ Preview muestra todos
→ Selecciona "2,5,7" para descargar solo esos 3
→ Script descarga solo los seleccionados

### Caso 4: Ver saldo
```bash
python catlux_scrapper.py --info
```
→ Muestra descargas este mes, disponibles, y total histórico

## 🐛 Resolución de Problemas

### "No se encontraron PDFs"
1. Verifica la URL es correcta
2. Verifica las credenciales en `.env`
3. Comprueba manualmente en https://www.catlux.de

### "Límite alcanzado"
1. Espera al próximo mes
2. O verifica con `--info` si hay descargas desde móvil
3. Las descargas se sincronizan del mes anterior

### Archivos no descargados después de "all"
1. Comprueba que tienes permiso de escritura en `CATLUX_SAVE_PATH`
2. Comprueba que la carpeta existe: `mkdir -p /ruta/a/carpeta`
3. Revisa el log: `tail -f catlux_scrapper.log`

## 📝 Archivos Generados

- `download_tracker.json` - Registro de todas las descargas
- `catlux_scrapper.log` - Log detallado de operaciones
- Carpeta de PDFs en `CATLUX_SAVE_PATH/klasse-X/fach/`

## 🔐 Seguridad

- Las credenciales se guardan en `.env` (ignorado por git)
- Nunca comparejas el archivo `.env`
- El script usa SSL verify=False (necesario para CatLux)
- Logs se guardan localmente sin exponer credenciales
