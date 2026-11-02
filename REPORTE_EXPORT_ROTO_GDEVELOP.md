# REPORTE: Export nativo GDevelop 5.6 roto — IN CRYPTA

## Resumen ejecutivo

El export nativo `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` está **roto porque es un caparazón vacío**: tiene 15 layouts (escenas) pero **0 objetos, 0 comportamientos, 0 eventos y 0 instancias iniciales por layout**. No hay Jugador, Enemigo, Plataforma, Alma, Pala, Jefe ni física definida. Por eso la física y las mecánicas no funcionan y no se ven las mejoras visuales: los assets existen, pero no hay objetos que los rendericen ni eventos que los controlen.

La versión que sí funciona (`In-Crypta/export/gdevelop/`) es una **arquitectura completamente distinta**: un runtime JS personalizado (`runtime_gdevelop.js` + PixiJS) que lee `game_data.json` y ejecuta toda la lógica en JavaScript.

---

## Diferencias concretas nativo (roto) vs funcional

| Aspecto | Nativo (`IN_CRYPTA_NATIVO.json`) | Funcional (`In-Crypta/export/gdevelop/`) |
|---|---|---|
| Formato | Proyecto GDevelop 5.6 JSON | `game_data.json` + `runtime_gdevelop.js` + `index.html` |
| Escenas/layouts | 15 (Titulo, Pausa, Derrota, Victoria, Nivel 1-3, Sala 1-6) | levels + rooms en game_data.json |
| Objetos definidos (`"objects"`) | **0 — vacío** | N/A (JS runtime) |
| Comportamientos Platform / física | **Ausente** | Implementado en runtime_gdevelop.js |
| Instancias iniciales por layout | **0 en cada uno** | N/A |
| Eventos de juego (movimiento, combate, almas, pala) | **Ausentes** | 71 KB de JS en runtime_gdevelop.js |
| Gravedad, salto, dash, ataque, coyote time | No definidos | En game_data.json `rules` |
| Recursos/assets (194) | Presentes en `export/gdevelop_nativo/assets/` | Referencia a assets del nativo |

---

## Hipótesis de causa raíz

El generador `tools/generar_proyecto_nativo.py` (156 KB) **sí contiene el código** para crear objetos con `PlatformBehavior` y eventos de juego (líneas ~2554-2608, ~1195+, ~804+, ~723+), pero el JSON de salida no los refleja: en `construir_proyecto()` (línea ~3476) se inicializa `base["objects"] = []` y **ese array nunca se popula** con los objetos generados por `objetos_y_instancias_escena()`. El empaquetador compila luego ese JSON vacío hacia `build/` (15 archivos code0.js–code14.js con código vacío).

Los documentos `docs/ENTREGA_GDEVELOP.md` y `export/gdevelop_nativo/LEEME_ENTREGA_GDEVELOP.md` afirman que el proyecto está completo, pero están desactualizados.

---

## Evidencia clave (rutas del repositorio)

- `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` — 15 layouts vacíos, `"objects": []`, `"eventsFunctionsExtensions": []`, `"externalEvents": []`, `"externalLayouts": []`
- `export/gdevelop/game_data.json:27-49` — física completa (gravedad, salto, dash, ataque)
- `export/gdevelop/game_data.json:51-73` — tamaños de entidades
- `In-Crypta/export/gdevelop/runtime_gdevelop.js` — motor de juego completo (71 KB)
- `tools/generar_proyecto_nativo.py:3476` — `base["objects"] = []` nunca se popula
- `tools/generar_proyecto_nativo.py:2554-2608` — `objetos_y_instancias_escena()` (código que no llega al JSON)
- `tools/empaquetar_gd_games.py` — compila el JSON vacío a build/
- `docs/ENTREGA_GDEVELOP.md:13` — afirma que el proyecto está completo (desactualizado)

---

## Opciones para publicar

### A) Versión funcional en hosting estático (recomendado)
Subir `In-Crypta/export/gdevelop/` (index.html + game_data.json + runtime_gdevelop.js) a itch.io / GitHub Pages / Netlify. Da un link de alojamiento web inmediato, jugable.

### B) ZIP roto en gd.games (no recomendado)
`export/IN_CRYPTA_1.0.0_HTML5_GDGAMES.zip` compila y levanta HTTP 200, pero el juego adentro está roto.

### C) Arreglar el export nativo (requiere tocar código)
Reparar `tools/generar_proyecto_nativo.py` para que `base["objects"]` sepopule con los objetos e instancias y los layouts incluyan eventos. Luego recompilar con `./publicar_gd_games.sh --check` y publicar en gd.games desde el IDE de GDevelop 5.6.

---

**Estado del reporte:** generado por Goal Mode sin modificar código del repositorio.