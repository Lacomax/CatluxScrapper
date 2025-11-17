#!/usr/bin/env bash
# Ejemplos de uso del CatLux Scrapper mejorado

# ============================================================================
# EJEMPLO 1: Ver qué hay disponible (solo preview, sin descargar)
# ============================================================================
echo "=== EJEMPLO 1: Preview de Deutsch Aufsatz ==="
python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/aufsatz"

# Resultado esperado:
# - Lista ordenada por REF (#0272, #0309, #0463, etc.)
# - Documentos independientes: examen en fila 1, solución en fila 2, etc.
# - Columna TIPO muestra "Exam" o "Solution"
# - Títulos completos (hasta 75 caracteres)
# - Pregunta interactiva: Selección: _


# ============================================================================
# EJEMPLO 2: Descargar TODOS los nuevos (con soluciones automáticas)
# ============================================================================
echo "=== EJEMPLO 2: Descargar todos los nuevos ==="
# Después del preview:
# Selección: new
#
# Resultado:
# - Descarga solo PDFs que no existen localmente
# - Automáticamente descarga soluciones junto con exámenes


# ============================================================================
# EJEMPLO 3: Descargar solo exámenes específicos
# ============================================================================
echo "=== EJEMPLO 3: Descargar exámenes específicos (1, 5, 9) ==="
# Después del preview:
# Selección: 1,5,9
#
# Resultado:
# - Selecciona filas 1, 5, 9
# - Si son exámenes: automáticamente descarga soluciones
# - Si son soluciones: solo descarga esa solución (si examen existe)


# ============================================================================
# EJEMPLO 4: Ver saldo de descargas disponibles
# ============================================================================
echo "=== EJEMPLO 4: Ver saldo disponible ==="
python catlux_scrapper.py --info

# Resultado esperado:
# Mes actual: November 2025
# Descargas este mes: X/100
# Descargas disponibles: Y
# Total histórico: Z


# ============================================================================
# EJEMPLO 5: Ver últimas descargas registradas
# ============================================================================
echo "=== EJEMPLO 5: Últimas descargas ==="
python catlux_scrapper.py --latest

# Resultado esperado:
# Muestra las últimas 20 descargas realizadas con fecha


# ============================================================================
# USO EN SCRIPTS AUTOMATIZADOS
# ============================================================================
# Si quieres descargar automáticamente sin interacción humana,
# puedes encadenar comandos:

#!/bin/bash

# Descargar automáticamente todos los nuevos sin preguntar:
# (Esto requiere agregar una opción --auto-select=new al script)

# Por ahora, para automatizar:
# 1. Usa --preview para ver qué hay
# 2. Luego selecciona números específicos en la interacción
# 3. O modifica el script para agregar --auto-download


# ============================================================================
# ESTRUCTURA DE CARPETAS ESPERADA
# ============================================================================

# Después de descargar, tu carpeta se verá así:
#
# CATLUX_SAVE_PATH/
# ├── klasse-7/
# │   ├── deutsch/
# │   │   ├── 112399.pdf          (Exam)
# │   │   ├── 112399_solution.pdf (Solution)
# │   │   ├── 112780.pdf          (Exam)
# │   │   ├── 112780_solution.pdf (Solution)
# │   │   └── ...
# │   ├── mathematik/
# │   │   ├── 120001.pdf
# │   │   └── ...
# │   └── ...
# └── klasse-8/
#     └── ...


# ============================================================================
# INTEGRACIÓN CON TRABAJO DIARIO
# ============================================================================

# Flujo sugerido:
# 1. Cada semana: ejecuta --preview
# 2. Revisa qué hay nuevo (TIPO=Exam, LOC=espacio)
# 3. Selecciona "new" para descargar solo nuevos
# 4. Soluciones se descargan automáticamente
# 5. Revisa --info para ver saldo

# Ejemplo práctico:
# $ python catlux_scrapper.py --url "https://www.catlux.de/proben/gymnasium/klasse-7/deutsch/"
# [preview mostrado]
# Selección: new
# [descarga automática de nuevos + soluciones]
# [estado final y saldo]


# ============================================================================
# CARACTERES ESPECIALES EN TABLA (para referencia)
# ============================================================================

# Columna LOC:
# ✓ = PDF descargado localmente
#   = PDF nuevo (no descargado)

# Columna TIPO:
# Exam     = Examen/Tarea
# Solution = Solución

# REF (Referencia):
# #0272 = Número de referencia en CatLux
# #0309 = Orden ascendente (#0272 < #0309 < #0463)
# #0463 =

# ============================================================================
EOF
