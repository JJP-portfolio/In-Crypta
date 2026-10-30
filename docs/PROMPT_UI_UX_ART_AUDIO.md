# Prompt de trabajo — IN CRYPTA: UI/UX, sprites/animaciones, efectos y audio procedural

> Copiar desde "## Contexto" hasta el final y pegar como primer mensaje de la sesión/agente
> que va a ejecutar el plan.

---

## Contexto

- **Proyecto:** `/home/sanodesu/unahur/PlataformeroMDA` — IN CRYPTA, plataformero gótico 2D
  (equipo 6, MDA / Programación 1 UNLP). Tres builds: prototipo **pygame** (960×540),
  export **GDevelop 5** (`export/gdevelop_nativo/IN_CRYPTA_NATIVO.json`) y export
  **web/JS** (`export/gdevelop/`).
- **Repositorio git:** ya existe, con commit base `IN CRYPTA v1.0.0 - Estado base para UI/UX improvements`.
  **El usuario edita el proyecto en paralelo**: antes de commitear, revisar `git status` y
  commitear **por path**, nunca con `git add -A` a ciegas (ya pasó una vez y se arrastraron
  cambios ajenos a un commit).
- **Documentos clave:**
  - `docs/PLAN_UI_UX_ART_AUDIO.md` → la propuesta completa con el detalle técnico, las
    mediciones y las fuentes. **Leerlo antes de tocar nada.**
  - `docs/GDD_MDA.md` → §7 (UI/UX: tipos de interfaz y 5 principios) y §8 (game feel: una
    fila por acción con feedback visual / sonoro / de cámara). Esa tabla §8 es el contrato
    de verificación de la Fase 3.
  - `docs/referencias/castlevania_ps1/diseno_niveles_referencia.md` → investigación de
    diseño de niveles ya hecha (no repetirla).
  - `~/unahur/TallerDeDiseñoConceptual/markdown/01-UIUX.md` → material de la cátedra:
    los 5 principios de UX y los 4 tipos de interfaz (no diegética, diegética, espacial, meta).

## Decisiones ya tomadas (no re-discutir)

1. **Se hacen TODAS las fases, en orden secuencial: 0 → 1 → 2 → 3 → 4 → 5.** No hay recortes.
2. **numpy: SÍ.** Ya está en `requirements.txt` (`numpy>=2`) y en el `.venv`
   (numpy 2.5.4 + pygame-ce 2.5.8, verificado funcionando). **Con fallback obligatorio**:
   el sintetizador tiene dos renderizadores para la misma ficha de sonido
   (`pygame.sndarray.make_sound` con numpy / `Sound(buffer=array.tobytes())` sin numpy).
   Si numpy no está, el juego arranca igual y suena igual.
3. El **export es un artefacto generado**: nunca editar el JSON de GDevelop a mano.
4. Los sprites del build nativo se **rasterizan desde el mismo código de dibujo** del
   prototipo (`guardar_2x` en `tools/generar_proyecto_nativo.py`): mejorar el dibujo mejora
   los dos builds. Es la fuente única de verdad y hay que mantenerla.
5. Estilo del proyecto: español rioplatense en textos y comentarios; código con secciones
   comentadas como el resto; `config.py` concentra las constantes (no hardcodear números);
   `pygame.draw` y primitivas, sin assets externos de audio.

## Hallazgos medidos (reproducir antes de "arreglar")

### A. El audio suena una octava arriba y dura la mitad
`audio.py` genera buffers **mono a 22050 Hz**, pero el mixer real queda en
**(44100, −16, 2) estéreo** (porque `pygame.init()` ya inicializa el mixer y la rama
`if pygame.mixer.get_init() is None` nunca corre). `Sound(buffer=...)` asume el formato del
mixer → el buffer se interpreta al doble de velocidad. **Medido:** el salto pedido a 230 Hz
suena ~600 Hz y dura 0,07 s en vez de 0,14 s (conteo de cruces cero sobre el buffer).
Además: 13 sonidos de una sola forma de onda, sin capas, sin variación de tono, sin música,
8 canales y sin verificar `play() is None`.

### B. Los dos generadores se pisan los assets
`tools/generar_proyecto_nativo.py` y `tools/generar_proyecto_rediseñado.py` escriben en la
**misma** carpeta `export/gdevelop_nativo/assets/`. Correr uno pisa los fondos del otro.
**Medido:** `fondo_nivel_1.png` de 10240×1152 (= 160×18 tiles) contra una instancia de
3840×384 (= 120×12 tiles) → fondo deformado, piso desalineado de las colisiones y
"plataformas" donde no las hay.

### C. HUD
`juego.py:dibujar_hud` → 3 paneles de 292+324+292 = **908 px de 960** de ancho × 70 px de
alto; tipografía `pygame.font.Font(None, ...)` (freesansbold) mientras el export GDevelop
usa **NotoSerifDisplay-Bold** (`/usr/share/fonts/noto/NotoSerifDisplay-Bold.ttf`) → los dos
builds se ven distintos; todo el estado se comunica con texto ("VIDA EXTRA 3/10", "DASH",
"J GOLPE") en vez de iconos; `font.render()` se llama en cada frame sin caché.

## Fases (en orden; cada una termina testeada y commiteada)

### Fase 0 — Higiene (1,5 h)
- **0.1** Separar assets por proyecto: `assets/` y `assets_room_tests/`, con la ruta
  parametrizable en `generar_assets()` y ajustando las rutas de recursos del JSON.
  Verificar: correr los dos generadores en cualquier orden y comparar el hash y el tamaño
  de `fondo_nivel_1.png` con lo esperado (7680×768 para 120×12 tiles a 2×).
- **0.2** Corregir `audio.py`: generar al formato real del mixer
  (`pygame.mixer.get_init()` → rate, formato, canales; int16; estéreo interleaved).
  Verificar: test que mida la frecuencia fundamental del buffer y la compare con la
  ficha (±2%).
- **0.3** Unificar tipografía: cargar NotoSerifDisplay-Bold en pygame, con fallback al
  default si el archivo no está.
- **0.4** Caché de render de texto (clave = texto+tamaño+color) + helper `dibujar_icono()`.
- **0.5** Commit por fase.

### Fase 1 — HUD (4 h)
Objetivo: en una captura de 1 s se identifican vida, recurso y estado del dash, sin tapar
el juego.
- Barra angosta (36 px) en vez de 3 paneles de 70 px; esquinas: nivel/tiempo arriba-izq,
  vidas+alma arriba-der, dash+pala abajo-izq.
- **Iconos en vez de texto**: alma, corazón, reloj, pala, flecha de dash.
- HUD contextual: la barra de vida extra solo con ≥1 alma; la de golpe solo con pala.
- **UI meta**: con 1 vida → viñeta roja pulsante en los bordes, en vez del texto "¡ÚLTIMA!".
- Reacciones animadas: pop al recoger un alma (escala con easing), flash de la barra del
  dash al recargarse, sacudida al perder vida.
- Diegético: el farol del sepulturero (ya está en el GDD) muestra el estado del dash.
- Tipografía: 3 tamaños (12/16/22), mayúsculas, grilla de 4 px.

### Fase 2 — Sprites y animaciones (8 h)
- Sistema de frames con **caché de superficies** por (entidad, pose, frame): el dibujo
  procedural actual pasa a ser el sprite, cacheado (hoy se redibuja todo cada frame).
- Jugador: ciclo de caminata de 4 frames con squash & stretch, poses de dash
  (anticipación / agachado / estela), aterrizaje con squash + polvo, parpadeo de la
  invulnerabilidad por alpha en vez de desaparecer medio frame.
- Enemigos: 3 estados con **tell explícito** (patrulla → wind-up con temblor + destello
  rojo ~200 ms → golpe → recovery) y **muerte por disolución** en partículas.
- Contorno de 1 px con `pygame.mask.from_surface()` + `Mask.outline()` → silueta legible.
- Capa/farol con inercia (historia de 3 puntos).
- Paleta por entidad en 3 valores (oscuro/medio/claro) para que defina el volumen.

### Fase 3 — Efectos y game feel (5 h)
Cada punto es una fila de la tabla §8 del GDD:
- **Hitstop** de 4–8 frames al golpear / matar / recibir daño.
- **Flash de frame**: el enemigo se dibuja blanco 1 frame al recibir el golpe.
- **Anticipación**: el enemigo telegrafía 200 ms antes de golpear.
- Sacudida de cámara **direccional** según el vector del impacto + zoom punch en el jefe.
- **Glow con `BLEND_ADD`** en chispas, estela del dash y halo del farol.
- Easing en `efectos.py` (ya existe: `ease_out_back`, `ease_out_cubic`, `ease_in_out_cubic`).
- Viñeta reactiva a la vida baja.

### Fase 4 — Audio procedural (5 h)
- `audio_sintetizador.py`: motor con ADSR, barrido exponencial, FM, ruido con filtro de un
  polo, mezcla con normalización y sin clipping. Dos renderizadores (numpy / stdlib) para
  **la misma ficha** de sonido.
- Banco de **18–20 SFX**: salto, doble salto, aterrizaje, dash, pala, impacto, muerte de
  enemigo, alma, vida extra, daño, checkpoint, portón, rugido del jefe, click/confirm/deny
  de UI, paso, recogida.
- **Capas**: cada sonido = 2–3 capas (p. ej. salto = barrido sinusoidal + chispa de ruido).
- **Variación**: detune aleatorio ±5% por reproducción + pool de 2–3 variantes.
- Mezcla: `set_num_channels(16)`, `set_reserved(2)` para UI y sonidos críticos, chequear
  `play() is None`, volumen por canal.
- **Paridad entre builds**: exportar el banco a WAV (módulo `wave` de la stdlib) y que el
  export GDevelop use esos mismos WAV (hoy genera los suyos aparte).
- Capa ambiental: drone de 2 osciladores + ruido filtrado en loop de 8 s, canal dedicado.

### Fase 5 — Verificación y documentación (2 h)
- Tests nuevos: (a) frecuencia fundamental de cada SFX = su ficha ±2%; (b) el HUD no
  cubre >40% del ancho ni >36 px de alto; (c) paridad export↔prototipo píxel a píxel;
  (d) frame time <16 ms con 200 partículas.
- Capturas antes/después de cada fase (`tools/capturar.py`).
- Actualizar `docs/GDD_MDA.md` §7 y §8 con lo implementado y los números medidos.
- Video corto (30–60 s) del antes/después para la presentación.

## Comandos de verificación (correrl en cada fase)

```bash
cd /home/sanodesu/unahur/PlataformeroMDA
.venv/bin/python tests/test_logica.py                 # espera: TESTS_INCRYPTA_OK
node tests/test_runtime_gdevelop.js                   # espera: TESTS_GDEVELOP_OK
python3 tools/generar_proyecto_nativo.py              # export GDevelop
python3 tools/export_gdevelop.py                       # export web/JS
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python tools/capturar.py                    # capturas
```

## Criterios de aceptación (medibles)

- HUD ≤ 40% del ancho, ≤ 36 px de alto, 0 etiquetas donde haya icono.
- ≥6 poses del jugador (incl. caminar y dash); ≥3 estados por enemigo con tell; contorno
  de 1 px; 0 redibujado por frame (caché).
- Hitstop en 3 eventos; flash de frame en el impacto; squash & stretch en salto y
  aterrizaje; viñeta reactiva; glow con BLEND_ADD.
- 18–20 SFX + 1 loop ambiental; 0 sonidos con error de formato; variación ±5%; mismo banco
  en pygame y en GDevelop.
- 60 fps con 200 partículas y el HUD nuevo; arranque del banco < 120 ms.
- `TESTS_INCRYPTA_OK`, `TESTS_GDEVELOP_OK`, export == protótipo.

## Cómo avisar

En español rioplatense y corto. Al terminar cada fase, avisar qué se cambió y que ya se
puede testear; al terminar todo, avisar que está listo para entregar y para el video de
presentación.
