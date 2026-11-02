# PROMPT PARA IA WEB — Reparar export nativo GDevelop 5.6 de IN CRYPTA

Eres un desarrollador senior de GDevelop 5.6 y Python. Repará el export nativo HTML5 del juego IN CRYPTA.

## Contexto

El repositorio está en `/home/sanodesu/unahur/PlataformeroMDA`.

El archivo `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` está roto: tiene 15 layouts (escenas) pero **0 objetos, 0 comportamientos, 0 eventos y 0 instancias iniciales por layout**. No hay Jugador, Enemigo, Plataforma, Alma, Pala, Jefe ni física. Por eso la física y mecánicas están rotas y no se ven las mejoras visuales.

La versión que SÍ funciona es `In-Crypta/export/gdevelop/` (runtime JS `runtime_gdevelop.js` + PixiJS que lee `game_data.json`). Tiene la lógica completa (movimiento, colisiones, combate, almas, pala, gravedad, salto, dash, coyote time).

## Qué hay en el repositorio

- `tools/generar_proyecto_nativo.py` — generador del proyecto GDevelop nativo (156 KB). SÍ contiene código para crear objetos con PlatformBehavior y eventos de juego, pero el JSON de salida no los incluye: en `construir_proyecto()` (~línea 3476) hace `base["objects"] = []` y nunca lo popula con lo que genera `objetos_y_instancias_escena()` (~líneas 2554-2608).
- `tools/empaquetar_gd_games.py` — compila el JSON a `export/gdevelop_nativo/build/` (code0.js–code14.js).
- `tools/exportar_todo.py` — script maestro de exportación.
- `In-Crypta/export/gdevelop/game_data.json` — física y reglas completas (gravedad, salto, dash, ataque, tamaños de entidades, jefe).
- `export/gdevelop_nativo/assets/` — 205 archivos de assets (presentes, no se ven porque no hay objetos que los rendericen).

## Tarea

Repará `tools/generar_proyecto_nativo.py` para que:

1. `construir_proyecto()` popule `base["objects"]` con los objetos que ya sabe construir (Jugador, Enemigo, Solido con comportamiento Platform, Alma, Pala, Puerta, HUD, Jefe, etc.).
2. Cada layout incluya sus `initialInstances` con las instancias correspondientes.
3. Cada layout incluya sus eventos de juego (movimiento, colisiones, combate, almas, jefe, daño, checkpoint).
4. El JSON de salida (`IN_CRYPTA_NATIVO.json`) quede con objetos, comportamientos, eventos e instancias, no vacío.

Luego recompilar con:
```
python3 tools/empaquetar_gd_games.py
./publicar_gd_games.sh --check
```

## Criterios de aceptación

- `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` tiene `"objects"` con al menos los objetos: Jugador, Enemigo, Solido, Alma, Pala, Jefe.
- Cada layout tiene `initialInstances` con al menos una instancia de Jugador y plataformas.
- `build/code0.js`…`code14.js` contienen código de juego real (no vacío).
- `./publicar_gd_games.sh --check` pasa con HTTP 200 en index.html, data.js y assets.
- El juego en el build tiene física (gravedad, salto, colisiones) y mecánicas funcionando.

## Archivos de referencia

Lee primero: `tools/generar_proyecto_nativo.py`, `tools/empaquetar_gd_games.py`, `In-Crypta/export/gdevelop/game_data.json`, `In-Crypta/export/gdevelop/runtime_gdevelop.js`, `REPORTE_EXPORT_ROTO_GDEVELOP.md`.

No modifiques `juego.py`, `entidades.py`, `audio.py` ni el core de Pygame. Solo el exportador de GDevelop nativo.

---

Adjunto va el repomix del estado actual del proyecto para que tengas todo el contexto.