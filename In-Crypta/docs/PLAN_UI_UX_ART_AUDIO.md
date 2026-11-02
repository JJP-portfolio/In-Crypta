# IN CRYPTA — Propuesta de trabajo: UI/UX, sprites/animaciones, efectos y audio procedural

> Investigación + plan por fases. Base: cátedra `IntroVideoJuegos` + `TallerDeDiseñoConceptual`,
> docs oficiales de pygame, wikis de los juegos de referencia y **medición del código actual**
> (no supuestos: todo lo marcado como "medido" salió de correr el proyecto).

---

## 1. Estado actual medido (línea de base)

### 1.1 HUD (`juego.py:931`)

| Aspecto | Hoy | Problema |
|---|---|---|
| Layout | 3 paneles fijos arriba: 292+324+292 = **908 px de 960** de ancho, 70 px de alto | Tapa ~13% de la pantalla de juego; los paneles casi se tocan entre sí |
| Tipografía | `pygame.font.Font(None, tamano)` → **freesansbold** (default de pygame) | El export GDevelop usa **NotoSerifDisplay-Bold** (`generar_proyecto_nativo.py:91`): los dos builds se ven distintos |
| Iconos | Solo 2 dibujados a mano (`dibujar_icono_alma`, `dibujar_corazon`) | El resto es texto: "VIDA EXTRA 3/10", "DASH", "J GOLPE", "SIN PALA" → el jugador tiene que *leer*, no *mirar* |
| Render | `font.render()` **en cada frame**, sin caché | 0,07 ms/frame por los ~10 textos (medido): poco, pero se paga 60 veces/s |
| Reacción a cambios | Ninguna: las barras y números cambian de golpe | Recoger un alma o perder una vida se siente plano |
| Barra del jefe | Panel de 430 px en `y=90` (encima del área de juego) + `HUD_Pista` de 780 px abajo | Compite con el nivel justo cuando hay que leer la pelea |

### 1.2 Sprites y animaciones (`entidades.py`)

- **No hay sprites**: todo se dibuja con primitivas de `pygame.draw` (rect, ellipse, polygon, line) en el momento.
- El export GDevelop **rasteriza ese mismo código** a PNG 2× (`guardar_2x`, `generar_proyecto_nativo.py:734`) → los sprites del build nativo son una foto de las primitivas. **Fuente única de verdad** ✓ (buena noticia: mejorar el dibujo mejora los dos builds).
- Poses del jugador: `idle`, `salto`, `caida`, `caida2`, `ataque1..3` → **no hay ciclo de caminata** ni pose de dash.
- Enemigos (`Enemigo.dibujar`, `entidades.py:539`): **una sola animación**, un flotón sinusoidal de ±2 px. No hay ciclo de caminar, ni anticipación, ni golpe, ni muerte.

### 1.3 Efectos (`particulas.py`, `juego.py`)

- Hay 7 emisores de partículas (salto, alma, dash, ataque, pala, daño, meta), flash de pantalla completa y sacudida de cámara.
- **No hay**: hitstop (freeze frames), squash & stretch, flash de frame al recibir un golpe, anticipación/telegrafía del enemigo, easing de animaciones, zoom de cámara.

### 1.4 Audio (`audio.py`) — dos hallazgos concretos

**Hallazgo A (bug de formato, medido):** el generador produce buffers **mono a 22050 Hz**, pero el mixer real queda en **(44100, -16, 2) estéreo** (porque `pygame.init()` ya inicializa el mixer y la rama `if get_init() is None` nunca corre). `Sound(buffer=...)` assume el formato del mixer → **cada sonido suena una octava más agudo y dura la mitad**:

| | pedido | realmente suena |
|---|---|---|
| "salto" | 230 Hz, 0,14 s | ~600 Hz, 0,07 s (medido con conteo de cruces cero) |

**Hallazgo B:** banco de 13 sonidos, todos de **una sola forma de onda** (tono puro con envolvente), sin capas, sin variación de tono (suena idéntico cada vez), sin pan, mono, con solo 8 canales y sin verificar `play() is None`. No hay sonido de aterrizaje, doble salto, muerte de enemigo, checkpoint, ni UI differentiate (confirm/deny). **No hay música**.

**Lo bueno:** el banco se genera en código puro (`array`, sin numpy), tarda 43 ms al arrancar (medido) y el proyecto **no depende de ningún asset de audio externo** → es la base ideal para mejorarlo.

### 1.5 Bug estructural que afecta al export (no es de arte, pero hay que arreglarlo)

`tools/generar_proyecto_nativo.py` y `tools/generar_proyecto_rediseñado.py` **escriben en la misma carpeta `export/gdevelop_nativo/assets/`**. Correr el generador de room tests **pisa los fondos del proyecto principal** (y al revés). Es la causa más probable de lo que se vio en GDevelop: un `fondo_nivel_1.png` de 160×18 tiles (10240×1152) contra una instancia de 120×12 tiles (3840×384) → el fondo se deforma, el piso no calza con las colisiones y aparecen "plataformas" donde no las hay.

---

## 2. Marco conceptual (lo que ya define la cátedra y el GDD)

Del material de la cátedra (`~/unahur/TallerDeDiseñoConceptual/markdown/01-UIUX.md`):

- **UI** = elementos gráficos con los que el jugador interactúa; **UX** = la experiencia total desde que empieza hasta que termina.
- **5 principios de UX**: (1) facilidad para encontrar lo importante, (2) rapidez para entender qué hacer, (3) comodidad según la plataforma, (4) consistencia entre menús, (5) fluidez entre acciones y menús.
- **4 tipos de UI**: no diegética, diegética, espacial y **meta** (la que simula una sensación: oscurecimiento, flash, aturdimiento).

El GDD del proyecto (`docs/GDD_MDA.md` §7 y §8) **ya mapeó todo esto**: la tabla de tipos de UI, los 5 principios aplicados y una tabla de *game feel* con una fila por acción (feedback visual / sonoro / de cámara). El trabajo no es inventar un marco: es **cerrar la brecha entre lo documentado y lo implementado**, y esa tabla §8 es el contrato de verificación.

---

## 3. Referencia: qué se toma de cada juego

### 3.1 Castlevania: Symphony of the Night (PS1, 1997)

- **HUD**: en la versión de PS1 la interfaz vive en una **franja inferior separada** de la ventana de juego, no superpuesta: corazones (HP), una barra vertical chica de MP, el sub-arma equipada, oro y EXP. Es **mínima**: fuera de combate no hay nada que tapar. El mapa, el inventario y el bestiario son **pantallas completas** con tipografía gótica y marcos, no widgets flotantes.
- **Niveles**: salas encadenadas con el checkpoint al inicio de cada sala; los enemigos son legibles por silueta y telegrafían antes de atacar (se paran y "cargan").
- **Qué tomar**: **el HUD como franja propia que no compite** + **iconos en vez de cifras largas** + **menú a pantalla completa en vez de panel flotante**.

### 3.2 Blasphemous (The Game Kitchen, 2019)

- **No hay barra de HP tradicional**: hay un medidor de **Bleeding** y un estado de **Penitence** que se comunica como **UI meta** (el mundo entero se tiñe y se desatura) → el feedback de estado no está *en la UI*, está *en la pantalla*.
- El **Relicario** (menú de objetos) es a pantalla completa, con marco ornamentado, no un menú flotante.
- Enemigos y jefes: **telegrafía por color** (rojo = vulnerable) y **animaciones de ejecución "pixel-perfect"** (el wiki destaca las "beautifully rendered, pixel-perfect execution animations").
- **Qué tomar**: **el estado crítico como efecto de pantalla completa** (el daño y la poca vida se sienten en el mundo, no en un widget) + **un color que significa "ahora sí, golpeá"**.

### 3.3 Ender Lilies

- HUD compacto con barras de HP/MP, la **currency** (Lily) y los **Shields**; menú con estética de pergamino; el **Farol** como objeto diegético del mundo.
- **Qué tomar**: **la moneda y los recursos como elementos propios del HUD** (en IN CRYPTA ya existe: las almas) y **un objeto diegético que muestre el estado** (en IN CRYPTA: el farol del sepulturero, que el GDD ya nombra como motivo visual).

### 3.4 Reglas transferibles (las que gobiernan la propuesta)

1. El HUD muestra **lo accionable**, no todo lo medible: vida, recurso y estado de la mecánica actual.
2. **Icono > texto**: un símbolo se lee en 100 ms, una etiqueta en 1 s.
3. **El estado crítico se siente en el mundo** (UI meta), no solo en un panel.
4. **Un color = un significado**: rojo = vulnerable, turquesa = dash listo, oro = recurso.
5. **Silueta y contraste**: el personaje se separa del fondo por **valor**, no por detalle.
6. **Todo telegrafía**: 1 tell por ataque (color, pose o sonido), ~200 ms de anticipación.

---

## 4. Propuesta por fases

Cada fase deja el juego testeable y se puede parar sin dejar nada roto.
Esforzos en **horas de trabajo efectivo** (no incluye implementación, es planificación).

### Fase 0 — Higiene y bugs (1,5 h) — **prioridad máxima**

| # | Tarea | Archivo | Verificación |
|---|---|---|---|
| 0.1 | Separar assets por proyecto (`assets/` y `assets_room_tests/`) + flag `--assets` | `tools/generar_proyecto_nativo.py`, `tools/generar_proyecto_rediseñado.py` | Correr los dos generadores en cualquier orden y comparar el hash de `fondo_nivel_1.png` con el tamaño esperado |
| 0.2 | Corregir el formato del audio: generar con `pygame.mixer.get_init()` (o `pre_init` antes de `init`) | `audio.py` | Test que mida la frecuencia fundamental del buffer y la compare con la especificada (±2%) |
| 0.3 | Unificar tipografía: cargar NotoSerifDisplay-Bold en pygame (ya está en `/usr/share/fonts/noto/`) | `juego.py` | Captura: HUD igual en ambos builds |
| 0.4 | Caché de render de texto + helper `dibujar_icono()` | `juego.py` | Test: 0 llamadas a `font.render` repetidas por frame |
| 0.5 | `git init` + primer commit (el proyecto **no tiene control de versiones**: hoy no hay red de seguridad) | repo | `git log` con un commit |

> Por qué 0.5 es prioritaria: el usuario está editando el proyecto en paralelo y no hay forma de volver atrás.

### Fase 1 — HUD (4 h)

**Objetivo:** que en una captura de 1 segundo se identifiquen vida, recurso y estado del dash, sin tapar el juego.

1. **Barra angosta (36 px) en vez de 3 paneles (70 px)** y esquinas: nivel/tiempo arriba-izq, vidas+alma arriba-der, dash+pala abajo-izq.
2. **Cero texto donde haya icono**: alma, corazón, reloj, hoja de pala, flecha de dash. Etiqueta solo donde no haya un objeto reconocible.
3. **HUD contextual**: la barra de "vida extra" (0/10) solo aparece con ≥1 alma; la de golpe solo cuando tenés pala; la del jefe solo en Nivel 3 ✓ (ya lo hace).
4. **UI meta**: cuando te quedan 1 vida → viñeta roja pulsante en los bordes (no el texto "¡ÚLTIMA!").
5. **Reacciones animadas**: pop al recoger un alma (escala 1→1,25→1 con easing), flash de la barra del dash al recargarse, sacudida al perder vida, latido cuando el dash está a punto de volver.
6. **Diegético**: el farol del sepulturero (ya está en el GDD) muestra el estado del dash como halo turquesa → el jugador mira el personaje, no el HUD.
7. **Tipografía**: escala de 3 tamaños (12/16/22), mayúsculas, grilla de 4 px, contraste AA contra el fondo.

### Fase 2 — Sprites y animaciones (8 h) — la fase más cara

**Decisión de arquitectura (importante):** *no* se dibujan PNG a mano. Se mantiene el pipeline actual —el código procedural **es** el sprite— y se lo convierte en un **sistema de frames con caché**:

1. **Pipeline**: `dibujar(pose) → Surface → cache[(entidad, pose, frame)] → blit`. Hoy se redibuja todo por frame; con caché se dibuja una vez y se reutiliza (y el export sigue igual, porque ya rasteriza a PNG).
2. **Jugador**: agregar **ciclo de caminata de 4 frames** (contacto/paso/contacto/paso) con squash & stretch; **poses de dash** (anticipación, agachado, estela); **aterrizaje** con squash (4 frames) + polvo; la **invisibilidad** pasa a parpadeo de alpha (hoy el jugador desaparece medio frame).
3. **Enemigos**: 3 estados con **tell explícito** → idle (patrulla) → **wind-up** (temblor + destello rojo, 200 ms) → golpe → recovery; **muerte por disolución** en partículas.
4. **Lectura de silueta**: contorno de 1 px generado con `pygame.mask.from_surface()` + `Mask.outline()` → separa al personaje del fondo (técnica clásica, está en la doc oficial).
5. **Secundario**: capa/farol con inercia (historia de 3 puntos) → el personaje respira aunque esté quieto.
6. **Paleta**: 3 valores por entidad (oscuro/medio/claro) para que el valor, no el detalle, defina la lectura.

### Fase 3 — Efectos y game feel (5 h)

Cada punto es una fila de la tabla §8 del GDD, convertida en código:

1. **Hitstop**: 4–8 frames de congelación al conectar un golpe / matar / recibir daño (flag `hitstop` en el loop) → el impacto se *siente*.
2. **Flash de frame**: el enemigo se dibuja blanco 1 frame al recibir el golpe (superficie con máscara de color).
3. **Anticipación**: el enemigo telegrafía (color + pose + sonido) 200 ms antes de golpear.
4. **Zoom de cámara** breve en el golpe al jefe y **sacudida direccional** (hoy aleatoria) según el vector del impacto.
5. **BLEND_ADD** para chispas, estela del dash y el halo del farol (glow real) → `Surface(..., flags=pygame.BLEND_ADD)`.
6. **Easing**: tabla de `ease_out_back` / `ease_out_cubic` en un `efectos.py` (sin librerías externas) para pops, barras y poses.
7. **Viñeta reactiva**: se oscurece con la vida baja; pulso rojo al recibir daño.

### Fase 4 — Audio procedural (5 h)

**Arranca de lo que ya existe** (`audio.py`, sin numpy, sin assets) y lo lleva a un sintetizador con capas.

1. **Motor de síntesis** (`audio_sintetizador.py`): ADSR, barrido exponencial, FM, ruido con filtro de un polo, mezcla con normalización y clip-free. **numpy es opcional**: si está, se usa (BSD-3, sin fricción); si no, el fallback con `array` mantiene el juego funcionando. Decisión: agregar `numpy` a `requirements.txt` **con fallback obligatorio**.
2. **Banco nuevo (18–20 SFX)**: salto, **doble salto**, **aterrizaje**, dash, pala, **impacto**, **muerte de enemigo**, alma, vida extra, daño, **checkpoint**, portón, rugido del jefe, **click / confirm / deny de UI**, **paso**, **recogida**.
3. **Capas**: cada sonido = 2–3 capas (p. ej. salto = barrido sinusoidal + chispa de ruido filtrado) → deja de sonar a "bip".
4. **Variación**: detune aleatorio ±5% por reproducción + pool de 2–3 variantes → nada suena dos veces igual.
5. **Mezcla**: `set_num_channels(16)`, `set_reserved(2)` para UI y sonidos críticos, chequear `play() is None`, volumen por canal.
6. **Paridad entre builds**: **exportar el banco a WAV** con el módulo `wave` de la stdlib y hacer que el export GDevelop use esos mismos WAV (hoy el nativo genera sus propios WAV aparte) → los dos builds suenan igual.
7. **Capa ambiental**: un drone de 2 osciladores + ruido filtrado en loop de 8 s (canal dedicado) → el silencio absoluto hoy resta la atmósfera gótica.

### Fase 5 — Verificación y documentación (2 h)

1. **Tests nuevos** (`tests/test_logica.py`): (a) la frecuencia fundamental de cada SFX coincide con su ficha; (b) el HUD no cubre más del 40% del ancho ni 36 px de alto; (c) paridad export↔prototipo (los PNG del export coinciden píxel a píxel con lo que dibuja pygame); (d) frame time < 16 ms con 200 partículas.
2. **Capturas antes/después** de cada fase (`tools/capturar.py` ya existe) → material de la presentación.
3. **Actualizar el GDD** §7 y §8 con lo implementado + los números medidos.
4. **Video corto (30–60 s)** del antes/después (la cátedra evalúa la presentación).

---

## 5. Orden, dependencias y qué recortar si falta tiempo

```
Fase 0 (bugs)  ──►  Fase 1 (HUD)  ──┐
                     Fase 2 (sprites) ├─►  Fase 3 (efectos)  ──►  Fase 4 (audio)  ──►  Fase 5 (verificar)
                     Fase 4 (audio)  ─┘
```

- **Fase 0 bloquea a todas**: sin el fix de formato el audio no se puede evaluar; sin los assets separados cada export rompe al anterior.
- **1 y 2 son independientes** → se pueden hacer en paralelo.
- **Fase 3 depende de 2** (los efectos acoplan con las poses nuevas).
- **Fase 4 es independiente** de lo visual.

**Si hay poco tiempo, el orden de retorno por hora es:**
`0.2 (audio mal) → 0.1 (assets) → 3.1 hitstop + 3.2 flash de frame → 1.2 iconos → 4.2/4.3 banco con capas y variación → 2.3 tell de enemigos`.
Es decir: primero lo que está **roto**, después lo que más **se siente**, después lo que más **se ve**.

---

## 6. Riesgos

| Riesgo | Mitigación |
|---|---|
| **numpy** como dependencia nueva | Fallback obligatorio con `array`; el juego nunca debe romperse por el audio |
| El usuario edita el proyecto en paralelo (hay cambios fuera de la sesión) | `git init` + commit antes de tocar nada; cambios chicos y verificables |
| Regenerar el export y pisar trabajo manual | El export es un artefacto: se regenera, no se edita a mano |
| Que "mejorar el arte" se coma el tiempo y no llegue la entrega | Fases con criterio de aceptación medible; el arte es la fase más caras y la más aplazable |
| Romper el build nativo | Toda fase termina con `tests/test_logica.py` + `node tests/test_runtime_gdevelop.js` + verificación de assets |

---

## 7. Criterios de aceptación (medibles)

- **HUD**: ≤ 40% del ancho, ≤ 36 px de alto, 0 etiquetas donde haya icono, 1 captura de 1 s muestra vida + recurso + estado del dash.
- **Sprites**: ≥ 6 poses del jugador (incl. caminar y dash), ≥ 3 estados por enemigo con tell, contorno de 1 px, caché de frames (0 redibujado por frame).
- **Efectos**: hitstop en 3 eventos, flash de frame en el impacto, squash & stretch en salto y aterrizaje, viñeta reactiva, glow con BLEND_ADD.
- **Audio**: 18–20 SFX + 1 loop ambiental, 0 sonidos con error de formato (frecuencia verificada ±2%), variación de tono ±5%, paridad de banco con el build nativo.
- **Performance**: 60 fps con 200 partículas y el HUD nuevo; banco de audio < 120 ms al arrancar.
- **Verificación**: `TESTS_INCRYPTA_OK`, `TESTS_GDEVELOP_OK`, export == protótipo píxel a píxel.

---

## 8. Fuentes consultadas

**Cátedra (local)**
- `~/unahur/TallerDeDiseñoConceptual/markdown/01-UIUX.md` — UI/UX: definición, 5 principios, 4 tipos de interfaz.
- `~/unahur/TallerDeDiseñoConceptual/markdown/02-CurvaDeDificultad.md`, `03-MatrizMDA.md`, `04-JuegosComoSistemas.md`.
- `~/unahur/IntroVideoJuegos/markdown/05-ProcesoCreativo.md` — concepto → high concept → pitch → GDD → producción; motores (GDevelop entre ellos).
- `~/unahur/IntroVideoJuegos/markdown/03-GenerosVideojuegos.md` — el género plataformas y sus subclases.
- `docs/GDD_MDA.md` §7 (UI/UX) y §8 (game feel) del propio proyecto.

**Docs oficiales de pygame**
- `pygame.mixer` — https://www.pygame.org/docs/ref/mixer.html
- `pygame.sndarray` — https://www.pygame.org/docs/ref/sndarray.html
- `pygame.mask` — https://www.pygame.org/docs/ref/mask.html (verificado: `from_surface(surface, threshold=127)`, `Mask.outline(every=1)`, `to_surface()`)
- `pygame.font` / `pygame.freetype` — https://www.pygame.org/docs/ref/font.html
- `pygame.transform` — https://www.pygame.org/docs/ref/transform.html
- `pygame.draw` — https://www.pygame.org/docs/ref/draw.html
- `Surface` y flags `BLEND_ADD` / `BLEND_RGBA_ADD` / `BLEND_MULT` — https://www.pygame.org/docs/ref/surface.html
- Todo lo anterior viene en la distribución estándar de pygame: **sin dependencias extra** (salvo numpy, opcional, solo para audio).

**Juegos de referencia**
- Castlevania: Symphony of the Night — https://castlevania.fandom.com/wiki/Castlevania:_Symphony_of_the_Night (sección "Levels' layout", "Graphics: Enemies/Environments"; artistas Ayami Kojima y Nobuya Nakazato).
- Blasphemous — https://blasphemous.fandom.com/wiki/Blasphemous (ejecuciones "pixel-perfect", Mea Culpa, Relics/Rosary Beads/Prayers, mundo no lineal).
- Los principios de *game feel* (hitstop, anticipation, squash & stretch, telegrafía) son los canónicos de la literatura de diseño de juegos y de los talks de Vlambeer/Game Maker's Toolkit sobre legibilidad.

**Medido en el proyecto**
- Audio: banco 43 ms para 13 sonidos; mixer real `(44100, -16, 2)` vs generador 22050 mono → **octava arriba y mitad de duración** (frecuencia fundamental medida con conteo de cruces cero).
- HUD: 908/960 px de ancho, 70 px de alto; 0,07 ms/frame de render de texto.
- Assets: `fondo_nivel_1.png` mide 10240×1152 (160×18 tiles) contra una instancia de 3840×384 (120×12) → **assets pisados por el otro generador**.
