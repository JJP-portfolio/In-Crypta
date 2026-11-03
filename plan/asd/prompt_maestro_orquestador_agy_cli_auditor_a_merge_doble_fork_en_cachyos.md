# PROMPT MAESTRO DE ORQUESTACIÓN (`/goal`) PARA `agy-cli` — AUDITORÍA, UNIFICACIÓN A `main` (ENTREGA 15 DÍAS) Y FORK COMERCIAL CON LIBRERÍAS EN CACHYOS

> **Entorno de ejecución:** Arch Linux / CachyOS (Rolling Release)  
> **Modelo Orquestador:** Gemini 3.8 Flash con delegación obligatoria en **Sub-Agentes**  
> **Comando de lanzamiento en terminal:**  
> `agy-cli /goal -f prompt_orquestador_doble_fork_cachyos.md -c incrypta_auditoria_y_doble_fork.xml`

---

## ROL Y MISIÓN DEL ORQUESTADOR

Actúa como **Argon**, Arquitecto Principal de Sistemas y Director Técnico de *IN CRYPTA* corriendo sobre **CachyOS (Arch Linux)**. Tu misión se divide en **dos grandes etapas encadenadas** ejecutadas mediante **Sub-Agentes especializados**:

1. **ETAPA A (Recolección y Diagnóstico Total):** Antes de tocar una sola línea de código, un sub-agente auditará todos los repositorios locales en `/home/sanodesu/unahur` (`PlataformeroMDA`, `IN_CRYPTA_v1.0.0_Desktop_Release`, `in-crypta-base`, backups y `.garbage/`) y generará el archivo `/home/sanodesu/unahur/REPORTE_AUDITORIA_PARA_FORK.xml` con todos los commits, ramas, diffs y rastros de GDevelop.
2. **ETAPA B (Purga de GDevelop, Merge a `main` para la Entrega en 15 días, y Creación del Fork Comercial en Paralelo):**
   - Purgar **el 100% de GDevelop** (queda totalmente descartado del proyecto).
   - Unificar lo mejor de todas las versiones en la rama `main` (`v1.0.3-entrega`) dejando listo el **Proyecto 1 (`/home/sanodesu/unahur/IN_CRYPTA_v1.0.3_Entrega`)** para la entrega académica en 15 días.
   - Crear en paralelo el **Proyecto 2 (`/home/sanodesu/unahur/IN_CRYPTA_Commercial_Edition`)**, un fork independiente en plena producción comercial que integra **`numpy`**, **`scipy`**, **`moderngl`** y **`pymunk`** con soporte de degradación elegante (*Fallback* a 8-bit NES para la laptop Sony Vaio).

---

## 1. MATRIZ DE UNIFICACIÓN: QUÉ DEJAMOS Y CON QUÉ NOS QUEDAMOS

Todo sub-agente debe respetar rigurosamente esta tabla de decisión al consolidar `main`:

| Componente / Versión | Decisión | Detalle Técnico |
| :--- | :--- | :--- |
| **GDevelop / GDJS / PixiJS** | ❌ **DESCARTADO 100%** | Mover a `/home/sanodesu/unahur/.garbage/slop_gdevelop/` los scripts `tools/generar_proyecto_redisenado.py`, `tools/previsualizar_nativo.py`, `jugar_web.bat` y limpiar `DIR_GD_ASSETS` en `assets_loader.py`, `hornear_assets_unificados.py` e `importar_assets_ia.py`. |
| **Overhaul Sensorial Argon** (`PlataformeroMDA` @ `2af109a`) | ✅ **SE QUEDA EN AMBOS** | Modelos visuales conmutables con `F4` (`AUTO`, `NES` 8-bit para Vaio/Web, `SNES` 16-bit, `PROC` Gótico), inspector de Hitboxes/Hurtboxes con `F3`, Walkable Edge Cues en pisos, Rim Lighting en enemigos ($\Delta Y > 150$) y Hit-Sparks D1..D3. |
| **Chimes Escalonados Pentatónicos** (`audio.py` @ `2af109a`) | ✅ **SE QUEDA EN AMBOS** | Escala pentatónica cristalina procedural (`523.25` a `1046.50` Hz en `alma_1..alma_6`), combo timer de `2.2s`, estallido dorado en combo x6, buffer de mixer a `2048` sin dron superpuesto en el título y las 10 pistas `.ogg` conectadas. |
| **Menús Limpios Cero Slop y Caché LRU** (`juego.py` @ `2af109a`) | ✅ **SE QUEDA EN AMBOS** | Menús minimalistas centrados sin texto académico de relleno, sin glifos Unicode rotos (*tofu*) y con `renderizar_texto_cacheado` (LRU de 256 entradas). |
| **Nivel 3 Vertical (36 filas) y Cámara Modular** (`Desktop_Release` @ `eb4dd0a`) | ✅ **SE INTEGRA A `main`** | `NIVEL_3_VERTICAL` de 2 pisos en `niveles.py`, cámara modular por bandas de 18 tiles (`camara.py`), filtro `_mismo_piso()`, paralaje Y continuo en Osario y validador `tools/validar_niveles.py` + `tests/test_niveles_verticales.py`. |
| **Build Web Pygbag Autónoma** (`exportar_web_pygame.py`) | ✅ **SE QUEDA EN AMBOS** | Perfil Web por defecto en Calidad Baja (`PERFIL_WEB_CALIDAD = 2`, 60 FPS sin penumbra pesada) y suministro local del wheel `pygame_ce-2.5.7-cp312-cp312-wasm32_bi_emscripten.whl` para evitar HTTP 404. |
| **Librerías Comerciales (`numpy`, `scipy`, `moderngl`, `pymunk`)** | 🚀 **EXCLUSIVO DEL FORK COMERCIAL** | Se instalan y activan únicamente en `/home/sanodesu/unahur/IN_CRYPTA_Commercial_Edition` para mantener la entrega de 15 días libre de dependencias externas. |

---

## 2. PLAN DE EJECUCIÓN PASO A PASO POR SUB-AGENTES

### SUB-AGENTE 1 — Auditor de Repositorios, Historial Git y Entorno CachyOS
**Misión:** Recolectar toda la información de código, commits, ramas y diferencias entre directorios antes de modificar nada, generando `/home/sanodesu/unahur/REPORTE_AUDITORIA_PARA_FORK.xml`.
1. Ejecuta los comandos de `<fase_1_recoleccion_diagnostico>` definidos en `incrypta_auditoria_y_doble_fork.xml`:
   - Registra versión de kernel CachyOS, Python, `pygame-ce`, ramas locales y remotas en `PlataformeroMDA` y en `IN_CRYPTA_v1.0.0_Desktop_Release`.
   - Extrae el `git log --oneline --graph --all -n 30` de ambos repositorios.
   - Genera el diff exacto entre `PlataformeroMDA` e `IN_CRYPTA_v1.0.0_Desktop_Release` para `camara.py`, `niveles.py`, `config.py` y `juego.py`.
   - Lista todos los archivos donde aún aparezca la cadena `gdevelop` o `DIR_GD_ASSETS`.
2. Guarda todo este relevamiento estructurado en `/home/sanodesu/unahur/REPORTE_AUDITORIA_PARA_FORK.xml` y valida que sea XML bien formado.

---

### SUB-AGENTE 2 — Cirujano de Purga GDevelop y Unificación en `release/v1.0.3`
**Misión:** Limpiar definitivamente GDevelop e integrar las gemas verticales en `PlataformeroMDA`.
1. En `/home/sanodesu/unahur`:
   - Crea (si no existen) `/home/sanodesu/unahur/materias_unahur/` y `/home/sanodesu/unahur/IN_CRYPTA_BACKUPS_HISTORICO/` y organiza allí las carpetas de materias universitarias y los `.zip`/`.tar.gz` de backup según el plan de sanitización, dejando el directorio raíz limpio.
2. En `/home/sanodesu/unahur/PlataformeroMDA`:
   - Desvincula el worktree `in-crypta-base` (`git worktree remove ../in-crypta-base --force || true` y `git worktree prune`) para liberar la rama `main`.
   - Crea la rama de integración a partir de `feat/menu-clean-procedural-chimes` (`2af109a`):
     ```bash
     git checkout -b release/v1.0.3
     ```
   - **Purga de GDevelop:** Mueve `tools/generar_proyecto_redisenado.py`, `tools/previsualizar_nativo.py`, `jugar_web.bat`, `optimizacion_v2.patch` y `plan/optimizacion_web.patch` hacia `/home/sanodesu/unahur/.garbage/slop_gdevelop/`. Limpia las referencias a `DIR_GD_ASSETS` y `--gdevelop` en `assets_loader.py`, `tools/hornear_assets_unificados.py` y `tools/importar_assets_ia.py`.
   - **Fusión del Osario Vertical y Cámara Modular:**
     - Copia `camara.py` desde `IN_CRYPTA_v1.0.0_Desktop_Release/camara.py` (cámara por bandas de 18 tiles).
     - Incorpora `NIVEL_3_VERTICAL` y `NIVELES_VERTICALES` en `niveles.py`.
     - Incorpora `OSARIO_VERTICAL = True` y `VERSION = "1.0.3"` en `config.py`.
     - En `juego.py`, integra `_mismo_piso()`, el soporte de `NIVELES_VERTICALES` en `cargar_nivel()`, el paralaje vertical Y en `dibujar_fondo_osario()` y el trigger euclidiano del jefe, **conservando intactos** todos los cambios de `2af109a` (menús sin slop, chimes escalonados, caché LRU, teclas `F3` y `F4` y los 3 niveles de calidad).
     - Copia `tools/validar_niveles.py`, `tests/test_niveles_verticales.py` y la carpeta `wheels/` desde `IN_CRYPTA_v1.0.0_Desktop_Release`.

---

### SUB-AGENTE 3 — Guardián de QA, Merge a `main` y Empaquetado de Entrega (15 Días)
**Misión:** Certificar que la versión de entrega pasa todas las pruebas, fusionarla a `main` y dejar listo el Proyecto 1.
1. Ejecuta en `/home/sanodesu/unahur/PlataformeroMDA` (en modo headless `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy`):
   - `.venv/bin/pytest tests/ -q` (deben pasar todos los tests de HUD, caché, audio, assets y niveles verticales).
   - `.venv/bin/python tests/test_logica.py` (debe imprimir `TESTS_INCRYPTA_OK`).
   - `.venv/bin/python tools/validar_niveles.py` (debe reportar 0 errores).
   - `.venv/bin/python tools/exportar_web_pygame.py --sync-only` (verificar sincronización limpia del paquete web).
2. Realiza el commit y el merge a `main`:
   ```bash
   git add -A
   git commit -m "release(v1.0.3): unificacion Argon sensorial, chimes, osario vertical y purga GDevelop"
   git checkout main
   git merge --no-ff release/v1.0.3 -m "Merge release/v1.0.3 into main (Entrega Final en 15 dias)"
   git tag -a v1.0.3-entrega -m "IN CRYPTA v1.0.3 — Entrega Academica Consolidada"
   ```

---

### SUB-AGENTE 4 — Arquitecto del Fork Comercial (`IN_CRYPTA_Commercial_Edition`)
**Misión:** Crear los dos proyectos paralelos forkeados e inyectar el pipeline de librerías avanzadas en el Fork Comercial sobre CachyOS.
1. Bifurca los dos proyectos en `/home/sanodesu/unahur`:
   - Clona el repositorio consolidado hacia `/home/sanodesu/unahur/IN_CRYPTA_Commercial_Edition`.
   - Renombra `/home/sanodesu/unahur/PlataformeroMDA` a `/home/sanodesu/unahur/IN_CRYPTA_v1.0.3_Entrega` (o mantén un symlink `PlataformeroMDA -> IN_CRYPTA_v1.0.3_Entrega` para no romper accesos directos).
2. En `/home/sanodesu/unahur/IN_CRYPTA_Commercial_Edition`:
   - Crea la rama `feat/commercial-nextgen-libs`.
   - Actualiza `requirements.txt` añadiendo `numpy>=2.0`, `scipy>=1.13`, `moderngl>=5.10`, `pymunk>=6.8` e instálalos en `.venv`.
   - Crea e integra los 3 módulos comerciales especificados en `incrypta_auditoria_y_doble_fork.xml` y `propuesta_librerias_visual_audio.xml`:
     1. **`audio_dsp.py`:** Síntesis vectorizada con `numpy` y `scipy.signal`, reverberación estéreo de catedral gótica para los 6 chimes de almas y repiques de campana, y filtro paso-bajo reactivo a 1 HP.
     2. **`gpu_pipeline.py`:** Renderizador opcional `ModernGL` con shader GLSL de luces puntuales dinámicas, aberración cromática de impacto y CRT/Bloom en GPU (con *Fallback* automático al renderizador Pygame si `config_calidad_idx == 2` en la Sony Vaio o en modo headless).
     3. **`fisica_decorativa.py`:** Cadenas y candelabros reactivos por física Verlet/Pymunk que se mecen al paso del jugador o con el viento del Dash.
   - Ejecuta `.venv/bin/pytest tests/ -q` y `.venv/bin/python tests/test_logica.py` en `IN_CRYPTA_Commercial_Edition` para confirmar que todas las pruebas siguen en verde con las nuevas librerías activas.
   - Haz commit de la base comercial en `feat/commercial-nextgen-libs`.

---

## 3. ENTREGABLE FINAL DEL ORQUESTADOR

Al finalizar los 4 Sub-Agentes, presenta un resumen ejecutivo en consola e imprime la ruta de:
1. `/home/sanodesu/unahur/REPORTE_AUDITORIA_PARA_FORK.xml` (con toda la información recolectada de commits, diffs y versiones).
2. `/home/sanodesu/unahur/IN_CRYPTA_v1.0.3_Entrega` (en rama `main`, tag `v1.0.3-entrega`, listo para entregar en 15 días).
3. `/home/sanodesu/unahur/IN_CRYPTA_Commercial_Edition` (en rama `feat/commercial-nextgen-libs`, con las librerías visuales y sonoras integradas para producción comercial).