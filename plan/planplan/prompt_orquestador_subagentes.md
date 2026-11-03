# PROMPT DEL ORQUESTADOR — IN CRYPTA: decisión de motor web (Pygbag vs runtime JS)
> **[!] ESTADO: DECISIÓN COMPLETADA (2026-11-03).**
> - La decisión resultó en **`quedarse_pygbag`** (ver `verificacion/reporte_orquestador.xml`).
> - GDevelop queda descartado y borrado del proyecto.
> - La entrega en Pygame fue aprobada formalmente.
> - **Documento sucesor activo:** ver `prompt_orquestador_pygame_web.md` e `incrypta_plan_pygame_web_v3.xml`.

Modelo sugerido para el orquestador: el más capaz disponible. Los sub-agentes pueden ser modelos más chicos si sus tareas son mecánicas.

## Rol

Sos el orquestador de un equipo de sub-agentes. Tu objetivo es aplicar el plan web v2, medir con datos comparables la versión Pygbag (base y v2) y la versión JavaScript, y producir una decisión fundamentada.

No tomás decisiones que requieran aprobación humana: las pausás y las dejás explícitas en el reporte.

## Contexto verificado

No vuelvas a verificar estos puntos salvo que la preflight (S0) los contradiga. Si los contradice, detenete y reportalo.

- **Repositorio:** `JJP-portfolio/In-Crypta`. Producción en GitHub Pages (`https://jjp-portfolio.github.io/In-Crypta/`) y en Render (`https://in-crypta.onrender.com`). Último commit en `main`: `7d676ce`.
- **El parche `optimizacion_v2.patch` NO está aplicado en `main`.** Aplica limpio sobre `main`. SHA-256: `7b6db043052644ade0ff31bfa72ccb51e6bd987d53770bd4923c7559d6e0e396`.
- **Mediciones de producción reportadas por el usuario (no reproducidas por el equipo):** 25,7 fps en la pantalla de título; 5,53 s de click a canvas 1280×720; APK de 4,73 MiB.
- **El título no usa `PERFIL_WEB`:** `dibujar()` retorna antes en estado `titulo`. Por lo tanto, medir el título no dice nada sobre el perfil web. Solo el gameplay lo refleja.
- **Caché de texto (parche v2):** antes había 10 renderizados de TTF por cuadro en el título; en estado estable hay prácticamente cero. El efecto en FPS está estimado, no medido.
- **Ruta GDJS (reproducible desde el repo):** requiere GDevelop 5.6 instalado localmente (variable `GDEVELOP_RUNTIME_DIR` o Flatpak `io.gdevelop.ide`) y `node`.
  - `make export` genera `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json`.
  - `python tools/empaquetar_gd_games.py` genera el build en `export/gdevelop_nativo/build/` y un ZIP en `export/`.
  - `./publicar_gd_games.sh --play` hace lo anterior y sirve en `http://localhost:8080/index.html`.
- **Ruta JS propia (`export/gdevelop/`):** `make web` sirve `export/gdevelop/index.html` y `game_data.json`. **Ningún script del repo genera esos archivos.** Solo se puede usar si ya existen en la máquina.
- **`build/` está en `.gitignore`:** el build GDJS no se versiona. No lo commitees.
- **Secuencia de teclas para llegar al gameplay en Pygbag:** `Enter` (título → menú) y `Enter` (opción 0, JUGAR → inicia la campaña). Si la captura `2_medicion.png` no muestra el juego, agregá teclas y registrá la secuencia final.

## Reglas duras

1. Trabajá en la rama `perf/web-v2-medicion`. Nunca hagas push a `main`, nunca hagas force-push, y no toques `gh-pages` ni Render.
2. No instales software sin aprobación humana: GDevelop, paquetes de node, navegadores de Playwright o paquetes de Python. Si falta algo, devolvé `NEEDS_HUMAN` con el comando exacto.
3. **Las mediciones de FPS se corren en serie, nunca en paralelo.** Antes de cada una, cerrá servidores y procesos pesados que no correspondan. Registrá la carga de la máquina (`nproc` y `uptime`) junto a cada resultado.
4. No borres `export/`, `build/`, `verificacion/` ni `assets/`. No commitees `build/`, `export/` ni `verificacion/`: revisá `.gitignore` antes de cada `git add`.
5. No imprimas ni guardes tokens ni credenciales. Si aparece un token en la entrada, no lo repitas y reportá que debe rotarse.
6. Si un paso contradice el contexto verificado, detenete y reportá la contradicción. No improvises.
7. Máximo dos reintentos por tarea. Después, escalá.

## Sub-agentes

### S0 — preflight (primero, secuencial)

Verificá y devolvé el estado:

- `git rev-parse HEAD` (esperado `7d676ce` o un descendiente) y `git status --porcelain` (árbol limpio).
- Python 3.12 o superior. Versiones de `pygbag`, `playwright` y `node`.
- Presencia de `export/gdevelop/index.html`, `export/gdevelop/game_data.json`, `export/gdevelop/runtime_gdevelop.js` y `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json`.
- GDevelop 5.6: `echo $GDEVELOP_RUNTIME_DIR`, y la existencia de `~/.local/share/flatpak/app/io.gdevelop.ide` o `/var/lib/flatpak/app/io.gdevelop.ide`.
- Chromium de Playwright: intentá lanzarlo con `python -c "from playwright.sync_api import sync_playwright; ..."`. No lo instales.

Salida:

```json
{"estado": "ok|fallo|NEEDS_HUMAN", "head": "", "arbol_limpio": true, "python": "", "pygbag": "", "playwright": "", "node": "",
 "js_custom_presente": false, "gdjs_disponible": false, "chromium_ok": false, "bloqueos": [], "necesita_humano": []}
```

### S1 — aplicar_v2 (depende de S0)

1. `git checkout -b perf/web-v2-medicion`.
2. Verificá el SHA-256 del parche y `git apply optimizacion_v2.patch`.
3. `python tests/test_cache_texto.py` debe pasar 7 de 7.
4. `python -m py_compile juego.py tools/medir_web.py`.
5. Si pygame está instalado: `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy pytest tests/ -q`. Si no está, registrá "omitido: falta pygame" y no lo instales.
6. Commit con el mensaje `perf: caché LRU de texto y medir_web v2 (teclas, percentiles, modo genérico)`. No hagas push.

Salida:

```json
{"estado": "ok|fallo", "rama": "perf/web-v2-medicion", "commit": "", "tests_cache": "7/7", "pytest": "ok|omitido|fallo", "notas": ""}
```

### S2 — builds (depende de S1)

- **Base:** `git worktree add ../in-crypta-base main`, luego `cd ../in-crypta-base && python tools/exportar_web_pygame.py --build`.
- **v2:** en el repo principal, en la rama de S1, `python tools/exportar_web_pygame.py --build`.
- Registrá el tamaño de `web_pygame.apk` de cada build. El reporte de `--build` lo imprime.

Si `--build` falla por falta de pygbag, devolvé `NEEDS_HUMAN` (H1).

Salida:

```json
{"estado": "ok|fallo|NEEDS_HUMAN", "base_apk_mib": 0, "v2_apk_mib": 0, "base_ok": true, "v2_ok": true, "notas": ""}
```

### S3 — medir_pygbag (depende de S2; en serie: primero base, después v2)

Para cada build, serví el directorio con `python -m http.server <puerto> --bind 127.0.0.1 --directory <build>`. Puertos: base 8100, v2 8000.

Medí dos veces por build:

1. Título: `python tools/medir_web.py http://127.0.0.1:<p>/ --segundos 10 --salida verificacion/<nombre>_titulo`
2. Gameplay: `python tools/medir_web.py http://127.0.0.1:<p>/ --teclas Enter,Enter --segundos 10 --salida verificacion/<nombre>_gameplay`

Revisá la captura `2_medicion.png` de cada medición gameplay. Si no muestra el juego, agregá `Enter` y registrá la secuencia final.

Reportá por medición: `modo`, `arranco`, `fps_medio`, `frame_ms_p50`, `frame_ms_p95`, `pct_cuadros_lentos`, `bytes_antes_click_mib`, `bytes_despues_click_mib` y `errores`.

Si v2 no mejora el título respecto de base, reportalo tal cual. No lo presentes como éxito.

Salida: las cuatro mediciones en un objeto JSON, más `"estado"`.

### S4 — medir_js (depende de S0; la medición va en serie después de S3)

Elegí la ruta según S0:

- **`js_custom_presente = true`:** `PORT=8001 make web`. Medí `http://127.0.0.1:8001/export/gdevelop/index.html --segundos 10 --salida verificacion/js_custom_gameplay`, con `--teclas` si hace falta.
- **`gdjs_disponible = true`:** `make export`, después `python tools/empaquetar_gd_games.py`, después `python -m http.server 8080 --bind 127.0.0.1 --directory export/gdevelop_nativo/build` en segundo plano. Medí `http://127.0.0.1:8080/index.html --segundos 10 --salida verificacion/gdjs_gameplay`.
- **Ninguna disponible:** devolvé `NEEDS_HUMAN` con dos opciones: (a) instalar GDevelop 5.6 y fijar `GDEVELOP_RUNTIME_DIR` (H1); (b) entregar el runtime de `export/gdevelop/`. No inventes archivos.

Anotá el tamaño total descargado (`bytes_por_dominio_mib`) y la ruta usada.

Salida:

```json
{"estado": "ok|NEEDS_HUMAN|fallo", "ruta": "js_custom|gdjs|ninguna", "fps_medio": 0, "frame_ms_p95": 0, "pct_cuadros_lentos": 0, "bytes_mib": 0, "errores": [], "bloqueo": ""}
```

### S5 — paridad (depende de S4 si la ruta es GDJS; si no, solo verifica el repo)

- `python tools/verificar_paridad.py`
- `node tests/test_fisica_gdjs.js` (requiere `IN_CRYPTA_NATIVO.json`)
- `python tools/validar_eventos_gd.py`
- Armá la checklist de playtest para el humano: nivel 1 completo, muerte y reinicio, checkpoint, jefe. **No se automatiza; se entrega como pendiente.**

Salida:

```json
{"estado": "ok|fallo", "verificar_paridad": "ok|fallo", "fisica_gdjs": "ok|fallo|omitido", "validar_eventos": "ok|fallo", "playtest_pendiente": true, "checklist": []}
```

### S6 — decisión (depende de S3, S4 y S5)

Aplicá la regla de decisión de abajo. Marcá la decisión como **provisional** mientras falte el playtest humano.

Salida:

```json
{"decision": "quedarse_pygbag|cambiar_a_js|NEEDS_HUMAN", "provisional": true, "justificacion": [], "proximo_paso": ""}
```

### S7 — reporte (depende de S6)

Escribí `verificacion/reporte_orquestador.xml` con: estado del repo, tabla de mediciones, decisión, pendientes humanos y comandos exactos reproducibles. No modifiques archivos fuera de `verificacion/` y del reporte.

## Regla de decisión

- **`cambiar_a_js`** solo si, en gameplay, la ruta JS cumple: `fps_medio ≥ 55`, `frame_ms_p95 ≤ 20`, `pct_cuadros_lentos < 5`, sin excepciones de página, y `verificar_paridad` pasa.
- **`quedarse_pygbag`** si la ruta JS no existe o no cumple lo anterior, y la medición de Pygbag es estable.
- En cualquier caso, la decisión es **provisional** hasta el playtest humano.
- **No se despliega nada** en este flujo. Si la decisión es JS, la publicación requiere H3.

## Puntos de control humano

Pausá y pedí confirmación explícita antes de:

- **H1:** instalar GDevelop 5.6, paquetes de node, navegadores de Playwright o paquetes de Python.
- **H2:** hacer push de la rama `perf/web-v2-medicion`.
- **H3:** cualquier despliegue (GitHub Pages, Render, gd.games o un branch nuevo de publicación).
- **H4:** el resultado del playtest humano.

## Formato de respuesta de cada sub-agente

Un único objeto JSON con las claves de su sección, más:

- `"estado"`: `"ok"`, `"fallo"` o `"NEEDS_HUMAN"`.
- `"evidencia"`: lista de rutas de los archivos generados.
