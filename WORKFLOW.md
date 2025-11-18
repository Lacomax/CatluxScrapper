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
================================================================================
📋 PREVIEW DE PDFS ENCONTRADOS
================================================================================

📚 Clase: DEUTSCH
📖 Asignatura: AUFSATZ

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

**Explicación:**
- `#` = Número de fila (1-48, ahora documentos independientes)
- `LOC` = Local (✓ = ya descargado, espacio = nuevo)
- `TIPO` = Tipo (Exam = examen, Solution = solución)
- `ID` = ID interno de CatLux para descargar
- `REF` = Número de referencia de CatLux (ordenado ascendentemente #0272, #0309, etc.)
- `Categoría` = Tipo de ejercicio (Schulaufgabe, Aufsatz, etc.)
- `Título` = Nombre del documento (hasta 75 caracteres)

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

Cuando el usuario selecciona exámenes individuales, el script **automáticamente descarga sus soluciones** si existen:

```
🔄 Iniciando descargas...

2024-11-17 14:30:45 - INFO - ⬇ 113132.pdf - descargado (99 restantes)
2024-11-17 14:30:46 - INFO - ⬇ 113132_solution.pdf - descargado (98 restantes)
2024-11-17 14:30:48 - INFO - ✓ 119215.pdf - ya existe
2024-11-17 14:30:50 - INFO - ⬇ 118065.pdf - descargado (97 restantes)
2024-11-17 14:30:52 - INFO - ⬇ 118065_solution.pdf - descargado (96 restantes)
2024-11-17 14:30:54 - INFO - Descarga completada: 4 nuevos PDFs
```

**Comportamiento automático:**
- Si selecciona: `1,3,5` (examen en 1, solución en 2; examen en 3, solución en 4; etc.)
- El script descarga los exámenes **Y automáticamente sus soluciones**
- ⬇ = PDF descargado (nuevo)
- ✓ = PDF ya existe localmente (saltado)
- Muestra descargas restantes de las 100/mes

**Conteo inteligente:**
- Cada PDF (examen + solución) cuenta como 2 descargas
- Seleccionar 3 exámenes = ~6 descargas (3 exam + 3 solutions)
- El script es honesto con el contador de CatLux

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

### Caso 3: Descargar solo exámenes sin soluciones
```bash
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/"
```
→ Preview muestra todos (examen y solución por separado)
→ Selecciona "1,3,5" (solo los exámenes, no los números pares para soluciones)
→ Script descarga exámenes + **automáticamente sus soluciones**
→ Resultado: Descarga 3 exámenes + 3 soluciones automáticamente

### Caso 4: Descargar exámenes específicos pero no sus soluciones
```bash
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/"
```
→ Preview muestra todos (examen en fila impar, solución en fila par)
→ Selecciona solo números impares: "1,5,9" (los exámenes)
→ Script descarga los exámenes + automáticamente sus soluciones
**Nota:** El script siempre descarga solución con examen, no hay forma de descargar solo examen sin solución

### Caso 5: Ver saldo disponible
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
