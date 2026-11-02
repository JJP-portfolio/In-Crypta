# IN CRYPTA en GDevelop 5

Esta carpeta contiene el puente entre el prototipo Pygame y GDevelop:

- `game_data.json`: los tres niveles, reglas, paleta, almas, moradores, pinchos y decoraciones.
- `runtime_gdevelop.js`: el juego completo dibujado con PixiJS y ejecutado como evento JavaScript.

GDevelop **no ejecuta Python**. El runtime recibe los datos del JSON y reproduce la misma lógica del prototipo. No es un proyecto nativo de objetos y eventos: es una capa de presentación jugable.

## Requisitos

- GDevelop 5.6 o superior.
- Un proyecto GDevelop **ya guardado** con al menos una escena.
- La escena en **960 × 540**.
- Python del proyecto (`.venv`) para ejecutar el exportador y el instalador.
- Node.js solo si querés correr la prueba headless del runtime.

## Instalación rápida

Desde la raíz del proyecto:

```bash
# 1. Exportar los datos actuales
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python tools/export_gdevelop.py

# 2. Probar el runtime sin abrir GDevelop
node tests/test_runtime_gdevelop.js

# 3. Simular la instalación
.venv/bin/python tools/instalar_gdevelop.py \
  "$HOME/Documentos/GDevelop projects/My project/Space Wars.json" \
  --dry-run

# 4. Instalar de verdad (crea backups)
.venv/bin/python tools/instalar_gdevelop.py \
  "$HOME/Documentos/GDevelop projects/My project/Space Wars.json"
```

Después:

1. Abrí el proyecto en GDevelop.
2. Verificá que la escena tenga el evento **JavaScript** con el marcador `INCRYPTA_GDEVELOP_RUNTIME_V1`.
3. Verificá que el recurso JSON se llame `game_data` y apunte a `game_data.json`.
4. Ejecutá la vista previa.
5. Probá: mover, saltar, dash, pala, pausa, reinicio y silencio.

## Qué hace el instalador

- Busca una escena (la primera o la indicada con `--layout`).
- Inserta el evento JS al inicio de la escena.
- Si ya existe un evento con el marcador `INCRYPTA_GDEVELOP_RUNTIME_V1` o el viejo `LUMEN_GDEVELOP_RUNTIME_V1`, lo reemplaza.
- Agrega o actualiza el recurso JSON `game_data`.
- Copia `game_data.json` junto al proyecto.
- Crea backups del proyecto y del JSON antes de escribir.

## Opciones

```bash
.venv/bin/python tools/instalar_gdevelop.py PROYECTO.json \
  --layout "Nombre de la escena" \
  --data export/gdevelop/game_data.json \
  --js export/gdevelop/runtime_gdevelop.js \
  --recurso game_data \
  --dry-run
```

- `--layout`: elige una escena por nombre. Si se omite, usa la primera.
- `--data`: otro JSON exportado.
- `--js`: otro runtime.
- `--recurso`: otro nombre de recurso (debe coincidir con el runtime).
- `--dry-run`: valida y muestra el resultado sin modificar el proyecto.

## Controles

| Tecla | Acción |
|---|---|
| `A` / `D` o flechas | Mover |
| `ESPACIO` | Saltar |
| `SHIFT` o `X` | Dash |
| `P` | Pausa |
| `R` | Reiniciar |
| `ENTER` | Empezar / avanzar / reintentar |
| `M` | Silenciar |

## Problemas frecuentes

### “El proyecto no tiene escenas”

Abrí GDevelop, creá una escena, guardá el proyecto y volvé a ejecutar el instalador. El instalador no puede inventar una escena válida sin arriesgar el formato interno del proyecto.

### “JSON inesperado”

El runtime espera `format: "incrypta.gdevelop-levels"`. Volvé a exportar:

```bash
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python tools/export_gdevelop.py
```

### “No JsonManager” o “JSON inesperado” en la vista previa

Verificá que el recurso se llame `game_data`, que sea de tipo JSON y que esté en la carpeta del proyecto. El instalador lo agrega automáticamente.

### La pantalla se ve negra o fuera de escala

La escena debe medir 960 × 540. El runtime dibuja en ese espacio y mueve la cámara con `setCameraX/Y`.

### No hay sonido

El navegador puede bloquear el audio hasta que haya una interacción. Empezá con `ENTER`; si sigue sin sonido, `M` alterna el silencio. El feedback visual no depende del audio.

### Ya había una versión anterior instalada

El instalador reconoce el marcador viejo `LUMEN_GDEVELOP_RUNTIME_V1` y reemplaza ese evento por el nuevo. No deberían quedar dos runtimes en la misma escena. Si ves dos, revisá que ambos eventos estén en la misma escena y eliminá el viejo.

## Validación

```bash
node tests/test_runtime_gdevelop.js
```

Salida esperada:

```text
INCRYPTA_GDEVELOP_OK levels=3
TESTS_GDEVELOP_OK levels=3
```

La validación cubre carga del JSON, pantalla de título, movimiento, salto, dash, meta, transición de niveles, victoria, reinicio y derrota. La vista previa visual dentro de GDevelop queda pendiente de una prueba humana.
