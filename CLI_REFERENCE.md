# CLI Reference - Argumentos y Opciones

Referencia completa de todos los argumentos y opciones de línea de comandos disponibles.

## Sintaxis General

```bash
python catlux_scrapper.py [OPCIONES]
```

## Argumentos Principales

### `--url URL`

**Descripción:** URL base de la clase a procesar

**Tipo:** Cadena (string)

**Ejemplo:**
```bash
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/"
```

**URLs válidas:**
- `https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/` - Todos los documentos de Deutsch
- `https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/aufsatz` - Solo Aufsatz
- `https://www.catlux.de/proben/gymnasium/klasse-7/mathematik/` - Todos los de Mathematik
- `https://www.catlux.de/proben/gymnasium/klasse-8/englisch/schulaufgabe` - Específico

**Nota:** Se puede omitir si usas `--select-category`

---

### `--select-category`

**Descripción:** Abre un menú interactivo para seleccionar la categoría

**Tipo:** Bandera (no requiere valor)

**Ejemplo:**
```bash
python catlux_scrapper.py --select-category
```

**Qué hace:**
1. Te pregunta por Klasse (5-12)
2. Te pregunta por Asignatura (Deutsch, Englisch, Mathematik, etc.)
3. Te pregunta por Tipo de Documento (Aufsatz, Schulaufgabe, etc.)
4. Construye la URL automáticamente

**Nota:** Permite seleccionar múltiples categorías en una sola sesión

---

### `--pages N`

**Descripción:** Número máximo de páginas a procesar

**Tipo:** Número entero

**Valor por defecto:** 10

**Ejemplo:**
```bash
python catlux_scrapper.py --url "..." --pages 5
python catlux_scrapper.py --select-category --pages 20
```

**Rango recomendado:** 5-50

**Notas:**
- Más páginas = más PDFs encontrados = más tiempo
- CatLux generalmente tiene 1-50 PDFs por página
- Si quieres TODOS los documentos, usa `--pages 100`

---

### `--info`

**Descripción:** Muestra el estado actual de descargas

**Tipo:** Bandera (no requiere valor)

**Ejemplo:**
```bash
python catlux_scrapper.py --info
```

**Salida:**
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

**Información que muestra:**
- Mes actual
- Descargas realizadas este mes (X/100)
- Descargas todavía disponibles
- Total de descargas realizadas en toda la historia

**Nota:** No realiza descargas, solo muestra información

---

### `--latest`

**Descripción:** Muestra las últimas descargas realizadas

**Tipo:** Bandera (no requiere valor)

**Ejemplo:**
```bash
python catlux_scrapper.py --latest
```

**Salida:**
```
============================================================
📥 ÚLTIMAS DESCARGAS (máximo 20)
============================================================
 1. [2025-11-18] 119215.pdf
 2. [2025-11-18] 119215_solution.pdf
 3. [2025-11-17] 118065.pdf
 4. [2025-11-17] 118065_solution.pdf
...
============================================================
```

**Información que muestra:**
- Número de descarga
- Fecha
- Nombre del PDF

**Nota:** Muestra máximo 20 descargas más recientes

---

### `--reset-tracker`

**Descripción:** Borra el historial de descargas (⚠️ CUIDADO)

**Tipo:** Bandera (no requiere valor)

**Ejemplo:**
```bash
python catlux_scrapper.py --reset-tracker
```

**Qué hace:**
1. Pide confirmación (s/n)
2. Si confirmas, borra TODO el historial
3. El contador de descargas vuelve a 0

**⚠️ ADVERTENCIA:**
- Es una acción irreversible
- Solo úsalo si realmente lo necesitas
- Normalmente NO lo necesitas (el contador se reinicia automáticamente cada mes)

**Casos de uso:**
- Cambio de periodo de facturación
- Sincronización entre dispositivos
- Resetear después de error

---

### `--preview`

**Descripción:** Mostrar preview SIN descargar

**Tipo:** Bandera (no requiere valor)

**Ejemplo:**
```bash
python catlux_scrapper.py --url "..." --preview
```

⚠️ **NOTA IMPORTANTE:** Este parámetro es heredado. Actualmente el script SIEMPRE muestra preview de forma interactiva.

---

### `--download`

**Descripción:** Descargar PDFs después de preview

**Tipo:** Bandera (no requiere valor)

**Ejemplo:**
```bash
python catlux_scrapper.py --url "..." --download
```

⚠️ **NOTA IMPORTANTE:** Este parámetro es heredado. Actualmente el script pregunta interactivamente qué descargar después del preview.

---

## Ejemplos de Uso

### Ejemplo 1: Selección Interactiva (RECOMENDADO)

```bash
python catlux_scrapper.py --select-category
```

Flujo:
1. Selecciona Klasse
2. Selecciona Asignatura
3. Selecciona Tipo
4. Ve preview
5. Elige qué descargar

---

### Ejemplo 2: URL Directa

```bash
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/"
```

Flujo:
1. Ve preview
2. Pregunta qué descargar

---

### Ejemplo 3: Ver Saldo Antes de Descargar

```bash
python catlux_scrapper.py --info
python catlux_scrapper.py --select-category
```

---

### Ejemplo 4: Ver Últimas Descargas

```bash
python catlux_scrapper.py --latest
```

---

### Ejemplo 5: Muchas Páginas

```bash
python catlux_scrapper.py --select-category --pages 50
```

Busca en las primeras 50 páginas (máximo posible)

---

### Ejemplo 6: Poca Conexión (Pocas Páginas)

```bash
python catlux_scrapper.py --url "..." --pages 3
```

Solo busca en las primeras 3 páginas (más rápido)

---

## Flujo Interactivo del Script

Después de ejecutar cualquier comando con URL o `--select-category`, el script te pedirá interactivamente:

### Paso 1: Preview

Muestra todos los PDFs encontrados con:
- `✓` = Descargado
- ` ` (vacío) = Nuevo

### Paso 2: Selección

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

**Respuestas válidas:**

| Opción | Qué Hace |
|--------|----------|
| `0` | Descarga TODOS los PDFs encontrados (incluyendo los ya descargados) |
| `1` | Descarga SOLO los PDFs que no existen localmente |
| `2` | Te pide números específicos (ej: `1,5,9`) |
| `8` | NO descarga nada y cancela |
| `9` | Vuelve a `--select-category` (si la usaste) o cancela |

---

## Variables de Entorno (.env)

El script lee estas variables desde `.env`:

| Variable | Requerida | Ejemplo |
|----------|-----------|---------|
| `CATLUX_USERNAME` | Sí | `tu_email@gmail.com` |
| `CATLUX_PASSWORD` | Sí | `tu_contraseña` |
| `CATLUX_SAVE_PATH` | Sí | `/home/usuario/Catlux` |
| `CATLUX_CERT_PATH` | No | `/path/to/cert.crt` |
| `CATLUX_DEFAULT_URL` | No | `https://www.catlux.de/proben/...` |

---

## Códigos de Salida

El script retorna estos códigos:

| Código | Significado |
|--------|------------|
| `0` | Éxito (descarga completada o cancelada normalmente) |
| `1` | Error (faltan credenciales, URL inválida, etc.) |

---

## Tips y Trucos

### Combinar Opciones

```bash
# Ver saldo, luego descargar categoría específica
python catlux_scrapper.py --info
python catlux_scrapper.py --url "..."

# Ver últimas descargas, luego seleccionar nueva categoría
python catlux_scrapper.py --latest
python catlux_scrapper.py --select-category --pages 20
```

### Automatización

```bash
# En scripts bash (Linux/macOS)
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/" > download.log 2>&1

# En Windows
python catlux_scrapper.py --url "..." > download.log
```

### Múltiples Descargas en una Sesión

Con `--select-category` puedes:
1. Descargar categoría 1
2. Seleccionar opción 9 (volver)
3. Descargar categoría 2
4. Repetir infinitas veces

---

## Ayuda

Para ver la ayuda integrada:

```bash
python catlux_scrapper.py --help
python catlux_scrapper.py -h
```

---

## Limitaciones Conocidas

- Máximo 100 descargas por mes (límite de CatLux)
- Máximo 50 páginas por búsqueda (por rendimiento)
- Máximo 20 descargas mostradas en `--latest`
- No soporta descargar desde múltiples URLs a la vez

---

## Problemas Comunes

**P: ¿Qué significa "Selección: 2 / Escribe números..."?**

R: Primero escribes `2` (opción "Seleccionar números específicos"), luego te pide que especifiques qué números quieres:
```
Selección: 2
Escribe números (ej: 1,3,5): 1,5,9
```

---

**P: ¿Puedo descargar solo exámenes sin soluciones?**

R: No. El script descarga automáticamente la solución junto con el examen para conveniencia.

---

**P: ¿Puedo descargar desde múltiples URLs a la vez?**

R: No, pero puedes hacerlo secuencialmente:
```bash
python catlux_scrapper.py --url "..."  # Descarga categoría 1
python catlux_scrapper.py --url "..."  # Descarga categoría 2
```

---

**P: ¿Qué pasa si llego a 100 descargas?**

R: El script se detiene y muestra un error. Debes esperar al próximo mes (se reinicia automáticamente el 1º).

---

## Versión

Para ver la versión del script:

```bash
head -n 5 catlux_scrapper.py | grep -i version
```

---

**Última actualización:** Noviembre 2025
