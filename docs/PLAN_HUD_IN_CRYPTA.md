# IN CRYPTA — Plan de renovación integral del HUD

> Documento de trabajo. **No se modificó el HUD ni ningún archivo de código.**
> Este documento reemplaza la sección de HUD de `docs/PLAN_UI_UX_ART_AUDIO.md`,
> que fue escrita para la versión 960×540 y quedó desactualizada.
>
> Baseline verificado al documentar:
> `PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_logica.py`
> → `TESTS_INCRYPTA_OK`.
>
> Estado del repo al crear el plan: rama `pygame-v0.2.2-dev`, HEAD `79733e1`;
> solo este documento estaba sin trackear y `juego.py` estaba limpio. Durante la
> revisión aparecieron cambios del usuario en `docs/GDD_MDA.md`, `niveles.py` y
> `tests/test_logica.py`; no son parte de este plan y no deben tocarse. Revisar
> `git status` antes de implementar.
>
> Las capturas de trabajo están en `/tmp/opencode/hud/` (no versionadas) y el
> harness que las genera es `/tmp/opencode/hud/capturar_hud.py`. Si `/tmp` se
> limpió, recrear el harness antes de la Fase 0; no es parte del juego.

---

## 1. Objetivo y alcance

Renovar **solo el HUD** de IN CRYPTA para que:

1. No tape información ni se superponga consigo mismo.
2. Aproveche el ancho disponible sin invadir el área de juego.
3. Muestre **contadores con número** (pedido explícito del usuario).
4. Comunique estados con icono + número + color, no con texto ambiguo.
5. Mantenga la estética gótica de Blasphemous / Castlevania: SOTN / Ender Lilies.
6. Sea verificable con capturas y tests, sin tocar gameplay.

**Fuera de alcance:** fondo, luna, cámara, entidades, niveles, audio, sprites, menús,
export GDevelop y cualquier lógica de almas, vidas, dash o ataque.

---

## 2. Estado actual medido

### 2.1 Layout actual

| Elemento | Medida / posición | Problema |
|---|---|---|
| Panel izquierdo | 344×68 en `(24, 16)` → x 24–368, y 16–84 | Ok solo si no aparece nada en el centro |
| Panel derecho | 542×68 con pala, 404×68 sin pala; x = `ANCHO - ancho - 24` | Cambia de ancho al recoger la pala: todo el HUD salta |
| Barra de jefe | 660×76 en x 310–970, y 16–92 | Tapa 58 px del panel izquierdo y 256 px del derecho |
| Pista | 640 px, x 320–960, y=16 sin jefe / y=98 con jefe | Tapa 48 px del panel izquierdo y 246 px del derecho |
| Aviso de jefe | y=98 durante el jefe | Se superpone con la pista |
| Mensaje de pista | `textwrap.wrap(width=64)` + `lineas_todas[:2]` | Corta por caracteres, no por píxeles; puede truncar texto |

### 2.2 Problemas de UX/UI verificados

| # | Problema | Evidencia en código / captura | Impacto |
|---|---|---|---|
| 1 | Pista tapa “ALMAS” y el rosario | Captura `01_inicio_pista.png`; `dibujar_pista` en `juego.py:1688` | El jugador no ve su progreso al empezar |
| 2 | Barra de jefe tapa ambos relicarios | Captura `05_jefe_fase1.png`; `dibujar_barra_jefe` en `juego.py:1643` | En el momento de más acción, se pierde vida/recurso |
| 3 | Pista y aviso compiten por y=98 | `juego.py:1468` y `juego.py:1699` | Textos superpuestos ilegibles |
| 4 | Panel derecho inestable | `ancho = 542 if tiene_arma else 404` en `juego.py:1559` | Layout shift al recoger la pala |
| 5 | Corazones vacíos casi invisibles | Borde `(78,62,82)` sobre panel `(14,11,18)` en `juego.py:1530` | No se lee cuántas vidas faltan |
| 6 | Dos contadores llamados “ALMAS” | `ALMAS x/42` usa `jugador.almas`; el rosario usa `almas_para_vida` | Ambigüedad semántica |
| 7 | El rosario nunca muestra 10/10 | `actualizar_almas` resetea a 0 en el mismo frame (`juego.py:826`) | Se pierde el feedback de “vida extra lista” |
| 8 | Dash muestra progreso `0.0–1.0` | `1.0 - (dash_cooldown / DASH_COOLDOWN)` en `juego.py:1618` | No se entiende cuánto falta |
| 9 | Arma muestra `...` | `estado_ataque = "LISTO" if ... else "..."` en `juego.py:1639` | Estado ilegible |
| 10 | Tiempo ausente del HUD | Solo en victoria (`juego.py:1442`); `README.md` lo promete | Falta información documentada |
| 11 | `efecto_hud` muerto | Se inicia en `juego.py:833`, nunca se actualiza ni se dibuja | Recoger almas/vida extra se siente plano |
| 12 | Texto renderizado por frame | `font.render()` en `juego.py:1740` y `1748`; `dibujar_pista` crea `Surface` por frame | Costo innecesario a 60 fps |
| 13 | Fuente relativa al cwd | `_ruta_fuente_gotica = "export/..."` en `juego.py:100` | Si se ejecuta desde otra carpeta, cae al fallback |
| 14 | Sin tests de HUD | `tests/test_logica.py` usa `Juego`, pero no mide layout ni contadores | Los solapamientos pueden volver |

### 2.3 Deuda técnica del HUD

- Constantes muertas o mal usadas en `config.py:127–133`:
  `HUD_ANGOSTO_ALTO`, `HUD_PANEL`, `HUD_PANEL_ALTO`, `HUD_NEGRO_X`, `HUD_GRIS_CLARO`,
  `HUD_ESQUINAS_*`. La última `HUD_ESQUINAS_ALTO` usa `HUD_MAX_ANCHO - 14` en vez de un alto.
- Números mágicos repartidos: `344`, `542`, `404`, `660`, `640`, `x + 280`, `x + 412`,
  `y + 42`, etc.
- `dibujar_hud_relicario_derecho` usa `total_almas = 24` como fallback arbitrario
  (`juego.py:1582`).
- `dibujar_hud` accede a `self.jefe.vivo` cuando `aviso_jefe > 0` sin comprobar
  `self.jefe is not None` (`juego.py:1459`). Hoy el flujo lo evita, pero es frágil.
- Código duplicado entre panel izquierdo y derecho (fondo, borde, esquinas góticas).
- Tamaños de fuente 11/13/14/15/16/17 sin escala clara.

---

## 3. Decisiones de diseño

### 3.1 Principios

1. **Jerarquía:** vida > jefe > recursos > tiempo > tutorial.
2. **Agrupación:** cada dato vive en una zona fija; nada comparte píxeles.
3. **Safe area:** riel de 72 px arriba; mensajes debajo; el resto es juego.
4. **Números:** el usuario pidió contadores con número; van icono + número.
5. **Contraste:** texto pequeño a 4.5:1; elementos gráficos a 3:1.
6. **Contexto:** el arma aparece solo cuando existe, pero sin cambiar el ancho.
7. **Consistencia:** un icono = un concepto; un color = un significado; grilla de 4 px.
8. **Feedback:** 150–250 ms, sutil, sin tapar la acción.
9. **Accesibilidad:** no depender solo del color; corazones vacíos visibles.
10. **Solo HUD:** no se toca la lógica del juego.

### 3.2 Defaults recomendados

| Decisión | Default recomendado | Motivo |
|---|---|---|
| Estructura | **Riel superior único full-width** | Elimina paneles flotantes y solapamientos |
| Altura del riel | **72 px** | Entra vida, tiempo, nivel, recursos y jefe |
| Zonas | **336 / 512 / 360 px** con gaps de 12 px | Reparto estable y simétrico |
| Margen | **24 px** laterales, 16 px superior | Safe area consistente |
| Panel derecho | **Ancho fijo** | Evita layout shift al recoger la pala |
| Contadores | **Número + icono** en todos | Pedido explícito |
| Tiempo | **Permanente** en la zona izquierda | `README.md` lo promete; útil para speedrun |
| Barra de jefe | **Dentro de la zona central**, 6 segmentos + `4/6` (Fase I) / `3/6` (Fase II) + fase | No tapa recursos |
| Pista/aviso | **Un solo canal debajo del riel**, máx. 2 líneas | Elimina superposición |
| Tipografía | `NotoSerifDisplay-Bold`, escala **12/14/18**; 22 solo overlays | Consistencia con el export |
| Arquitectura | **`hud.py`** con `HudTheme`, `HudLayout`, `HudModel`, `HudRenderer` | Testeable y desacoplado |
| Feedback | `Tween` con `dt`/`MAX_DT`; `EfectoAnimacion` usa `time.time()` y no se usa para el HUD nuevo | Bajo costo, alto impacto |

### 3.3 Decisiones abiertas

1. ¿El tiempo va permanente en el HUD o solo en pausa/victoria?
   **Recomendación:** permanente en la zona izquierda.
2. ¿Riel único full-width o tres paneles separados?
   **Recomendación:** riel único.
3. ¿Extraer a `hud.py` o mantener todo en `juego.py`?
   **Recomendación:** `hud.py`; si se quiere diff mínimo, mismas piezas dentro de `juego.py`.
4. ¿Mostrar 10/10 en el rosario?
   **Limitación:** requiere tocar la lógica de recogida; fuera de alcance.
   Desde el HUD solo se puede mostrar un flash/toast de “VIDA EXTRA”.

---

## 4. Investigación y referencias

### 4.1 Fuentes externas

- **gamedesign.gg — HUD design principles**  
  `https://gamedesign.gg/articles/hud-design-principles`  
  Aporta: anchoring, grouping, safe areas, legibilidad, numerals tabulares,
  HUD adaptativo, fade/onboarding y accesibilidad.

- **Goldsmiths — “Developing Effective UX Guidelines for HUD Design”**  
  `https://research.gold.ac.uk/id/eprint/39439/1/1187.pdf`  
  Aporta: claridad, legibilidad, smart placement, HUD diegético/no diegético,
  guías para estudios indie. Texto extraído en `/tmp/opencode/research/hud_guidelines.txt`.

- **Caroux & Isbister — HUD and player experience**  
  `https://www.sciencedirect.com/science/article/abs/pii/S1071581915001779`  
  Aporta: las características del HUD influyen en la UX según expertise y género;
  no hay un HUD universal.

- **Game Accessibility Guidelines**  
  `https://gameaccessibilityguidelines.com/`  
  Aporta: contraste, no depender solo del color, escala de HUD, opciones de accesibilidad.

- **The Wingless — errores comunes de HUD**  
  `https://thewingless.com/index.php/2021/05/12/7-obvious-beginner-mistakes-in-your-video-games-hud-from-a-ui-ux-art-director`  
  Aporta: errores de jerarquía, ruido, iconografía y legibilidad.

- **Hollow Knight — UX/UI and accessibility**  
  `https://teemo.dev/game-design/hollow-knight/systems/ux-ui-and-accessibility`  
  Aporta: HUD always-on mínimo, dos escalas autoradas (`HudScalePositioner`),
  contador de geo que espera 1.5 s antes de aparecer.

- **Celeste — game overview**  
  `https://teemo.dev/game-design/celeste/systems/game-overview`  
  Aporta: el color del pelo como HUD diegético del dash (rojo=1, azul=0, rosa=2).
  En IN CRYPTA no se aplica porque tocaría al personaje; se toma la idea de
  “estado del dash legible sin leer un número”.

- **Three.js game UI patterns**  
  `https://github.com/majidmanzarpour/threejs-game-skills/blob/main/skills/threejs-game-ui-designer/references/ui-patterns.md`  
  Aporta: zonas de HUD, contenedores numéricos de ancho fijo y no apilar banners
  sobre la acción.

- **NN/g — Executing UX Animations: Duration and Motion Characteristics**  
  `https://www.nngroup.com/articles/animation-duration/`  
  Aporta: 100–500 ms para la mayoría de animaciones; entradas más lentas que
  salidas; ease-out al entrar, ease-in al salir; el exceso de movimiento es un
  problema de accesibilidad.

- **Material Design — Duration & easing**  
  `https://m1.material.io/motion/duration-easing.html`  
  Aporta: duraciones por plataforma (desktop 150–200 ms), curvas estándar,
  deceleración y aceleración, y ajuste por distancia recorrida. Es una guía
  clásica (Material 1); se usa como referencia, no como regla absoluta.

- **Returnal — UX design: gameplay-first UI**  
  `https://blog.playstation.com/2021/05/11/unpacking-returnals-ux-design-gameplay-first-ui-retro-futuristic-tech-and-accessibility/`  
  Aporta: jerarquía de información, timings de animación ajustados en combate,
  poca moción direccional y escalada multisensorial en vida baja.

- **Slicker — Game Feel in Pygame: Juice, Screenshake, and Micro-Animations**  
  `https://slicker.me/python/game_feel_pygame.htm`  
  Aporta: screenshake corto (50–300 ms) con decay y easing, micro-animaciones,
  hit flash y la regla de sacudir el mundo/cámara, no el HUD.

- **Accessible Game Design — HUD Guidelines**  
  `https://accessiblegamedesign.com/guidelines/HUD.html`  
  Aporta: salud como porcentaje + gráfico, animación para urgencia, timer legible,
  feedback multisensorial y no depender solo del número.

- **Defold — HUD code sample**  
  `https://defold.com/tutorials/hud/`  
  Aporta: count-up del puntaje con `dt`, pop de escala al sumar, pickups que
  flotan y se desvanecen; receta concreta de feedback acumulativo.

- **Game Accessibility Guidelines — Avoid flickering images and repetitive patterns**  
  `https://gameaccessibilityguidelines.com/avoid-flickering-images-and-repetitive-patterns/`  
  Aporta: evitar secuencias de flashing de más de 5 s y más de 3 flashes por
  segundo cubriendo 25%+ de la pantalla; no usar la etiqueta “epilepsy safe”.

- **W3C — WCAG 2.3.1 Three Flashes or Below Threshold**  
  `https://www.w3.org/WAI/WCAG21/Understanding/three-flashes-or-below-threshold.html`  
  Aporta: límite normativo de flashes generales/rojos y definición de flash rojo.

- **Documentación oficial de pygame**  
  `https://www.pygame.org/docs/ref/time.html`  
  `https://www.pygame.org/docs/ref/transform.html`  
  `https://www.pygame.org/docs/ref/surface.html`  
  `https://www.pygame.org/docs/ref/font.html`  
  `https://www.pygame.org/docs/ref/draw.html`  
  Aporta: `Clock.tick`, `get_ticks`, `smoothscale`, `set_alpha`, `convert_alpha`,
  `font.size` y primitivas de dibujo.

### 4.2 Fuentes internas

- `docs/PLAN_UI_UX_ART_AUDIO.md`: auditoría previa de UI/UX, sprites, efectos y audio.
  Su sección de HUD es de 960×540 y quedó desactualizada.
- `docs/PROMPT_UI_UX_ART_AUDIO.md`: plan viejo de HUD en 4 h.
- `docs/GDD_MDA.md` §7 y §8: tipos de UI, 5 principios UX y tabla de game feel.
- `README.md`: funcionalidad prometida del HUD, incluido el tiempo.
- `docs/DISENO_VISUAL_PYGAME.md`: criterios visuales del prototipo.

### 4.3 Lecciones aplicadas

- **Hollow Knight:** el HUD siempre visible debe ser mínimo; lo contextual aparece
  solo cuando hace falta. Los contadores no deben competir con la acción.
- **Celeste:** el estado del dash se puede leer de un vistazo; en IN CRYPTA se
  traduce a icono + color + segundos, sin tocar al personaje.
- **Blasphemous / SOTN:** marcos góticos, recursos con iconos, pero HUD pequeño;
  la ornamentación no debe tapar el juego.
- **Ender Lilies:** la moneda/recurso tiene identidad propia; en IN CRYPTA las almas
  y la vida extra deben tener contadores separados y claros.
- **Animación:** se anima para comunicar un cambio, no para decorar; duraciones
  cortas, sin loops gratuitos, sin flashes >3 Hz y sin mover el layout.
- **Accesibilidad:** el color solo no alcanza; cada estado necesita forma, texto o número.

---

## 5. Layout propuesto

### 5.1 Riel superior único

Reemplaza los tres paneles flotantes por **una sola barra full-width**, con márgenes
de 24 px y tres zonas separadas por divisores góticos.

```text
+------------------------+---------------------------+------------------------+
| [HP] 3/5  TIEMPO 01:23 | NIVEL 1/3                 | [ALMA] 12/42  [DASH] LISTO |
| ♥ ♥ ♥ ♡ ♡              | LA CRIPTA                 | VIDA EXTRA 7/10 [PALA] --  |
+------------------------+---------------------------+------------------------+
          +-------- pista / aviso (máx. 2 líneas) --------+
```

Los 10 puntos del rosario van dentro de la celda de `VIDA EXTRA`: texto en la
primera línea y pips de 5×3 px con pitch de 6 px en la segunda.

- Riel: `Rect(24, 16, 1232, 72)` → `x=24..1256`, `y=16..88`.
- Zonas exactas: izquierda `Rect(24,16,336,72)`, centro `Rect(372,16,512,72)`,
  derecha `Rect(896,16,360,72)`.
- Gaps: **12 px** entre zonas. No hay padding exterior adicional: el padding de
  **12 px** es interno de cada zona; el contenido vertical vive en `y=28..76`.
- Contenido: izquierda `Rect(36,28,312,48)`, centro `Rect(384,28,488,48)`,
  derecha `Rect(908,28,336,48)`.
- Zona derecha: **grilla 2×2**, celdas de **164×22 px** con gaps de **8 px**
  horizontal y **4 px** vertical. No son cuatro filas.
- Mensajes: `Rect(360,96,560,48)`; padding interno 4 px; cuerpo 14 px con
  line-height 20 px (2 líneas = 40 px + 8 px de padding).
- Área ocupada: **~9.6%** de la pantalla con el riel; **~12.5%** con mensaje.
- El criterio viejo de “≤40% del ancho” ya no aplica: el riel usa todo el ancho,
  pero es bajo y no se superpone.

Constantes nuevas propuestas en `config.py` (no existen todavía):

```python
HUD_MARGEN_X = 24
HUD_MARGEN_Y = 16
HUD_ALTO = 72
HUD_GAP = 12
HUD_PADDING = 12
HUD_ZONA_IZQ = 336
HUD_ZONA_CENTRO = 512
HUD_ZONA_DER = 360
HUD_MENSAJE_ANCHO = 560
HUD_MENSAJE_ALTO = 48
HUD_MENSAJE_Y = 96
```

`HUD_ALTO` no debe confundirse con las constantes muertas `HUD_ANGOSTO_ALTO`,
`HUD_PANEL_ALTO` ni `HUD_ESQUINAS_ALTO`.

### 5.2 Con jefe activo

El centro se transforma; no se agrega otra barra encima.

```text
+------------------------+---------------------------+------------------------+
| [HP] 3/5  TIEMPO 01:23 | EL CUSTODIO · FASE II     | [ALMA] 12/42  [DASH] 0.4s |
| ♥ ♥ ♥ ♡ ♡              | ▮▮▮▯▯▯ 3/6                | VIDA EXTRA 7/10 [PALA] --  |
+------------------------+---------------------------+------------------------+
```

- Barra de jefe: 6 segmentos de **68×12 px** con gap de 4 px; ocupan 428 px.
  A la derecha, separado 12 px, va el slot de **48 px** para `3/6`; total 488 px.
- **Fase II nunca muestra `4/6`:** la fase cambia al tercer golpe, cuando quedan
  3 de 6. El ejemplo correcto es `3/6` + `FASE II`; `4/6` + `FASE I`.
- El texto largo (“LA PALA REBOTA…”) sale de la barra y pasa al canal de mensajes
  cuando cambia la fase.
- El nombre “EL CUSTODIO DEL OSARIO” entra en 488 px a 18 px (mide ~242 px).

### 5.3 Zonas

| Zona | Contenido | Regla |
|---|---|---|
| Izquierda (336) | Vida, corazones, tiempo | 2 filas: HP+tiempo / corazones; vida siempre visible |
| Centro (512) | Nivel / jefe | 2 filas: nivel si no hay jefe; nombre+barra si hay jefe |
| Derecha (360) | Almas, vida extra, dash, pala | Grilla 2×2 de 164×22; ancho fijo |
| Mensajes (560×48) | Pista / aviso | Un solo canal, debajo del riel |

---

## 6. Contadores numéricos

| Elemento | Formato propuesto | Cuándo | Nota |
|---|---|---|---|
| Vida | `[HP] 3/5` + 5 corazones | Siempre | Corazones llenos/vacíos bien contrastados |
| Almas | `[ALMA] 12/42` | Siempre | Total recolectado en el nivel / total del nivel |
| Vida extra | `VIDA EXTRA 7/10` + 10 cuentas | Siempre | Reemplaza el segundo “ALMAS”; si está en 0, se ve gris |
| Dash | `[DASH] LISTO`, `[DASH] 0.4s` o `[DASH] SIN USO` | Siempre | Prioridad: cooldown > 0 → segundos; si no, aire sin uso → `SIN USO`; si no, `LISTO` |
| Pala / guadaña | `[PALA] LISTO` / `[GUADAÑA] LISTO` (o `0.2s`) | Siempre | Sin arma: `[PALA] --`; el slot queda reservado |
| Tiempo | `TIEMPO 01:23` | Siempre | `MM:SS`; en victoria, `MM:SS.d` |
| Jefe | `4/6` + `FASE I`, o `3/6` + `FASE II` | Solo jefe | 6 segmentos, sin texto instructivo permanente |
| Pista | Texto, no contador | Contextual | Máximo 2 líneas, con elipsis si no entra |

### 6.1 Semántica

- **ALMAS:** almas recolectadas en el nivel actual / total del nivel (`nivel.total_almas`).
- **VIDA EXTRA:** progreso del rosario (`almas_para_vida` / `ALMAS_POR_VIDA`).
- **VIDAS:** corazones actuales / máximo (`VIDAS_MAXIMAS`).
- **DASH:** estado del dash; si no está listo, segundos restantes.
- **PALA / GUADAÑA:** estado del ataque; si no está listo, segundos restantes.
- **TIEMPO:** `tiempo_total`; en victoria se puede mostrar con décimas.

### 6.2 Limitación conocida

El rosario **nunca muestra 10/10** porque `actualizar_almas` resetea a 0 en el mismo
frame en que llega a 10. Desde el HUD se puede mostrar un flash/toast de “VIDA EXTRA”
solo si `vidas` aumentó. Si el jugador ya está en `VIDAS_MAXIMAS`, el rosario se
resetea sin dar vida: no mostrar “VIDA EXTRA”; opcionalmente, “ROSARIO COMPLETO”
si se agrega un evento de HUD, sin tocar la lógica de recogida.

### 6.3 Formatos exactos y prioridades

Constantes actuales que fijan los formatos: `DASH_COOLDOWN=0.60`,
`ATAQUE_COOLDOWN=0.35`, `VIDAS_MAXIMAS=5`, `ALMAS_POR_VIDA=10`, `JEFE_VIDA=6`.

```python
import math


def fmt_cooldown(restante: float) -> str:
    if restante <= 0:
        return "LISTO"
    decimas = math.ceil(restante * 10) / 10
    return f"{decimas:.1f}s"


def fmt_dash(jugador) -> str:
    if jugador.dash_cooldown > 0:
        return f"[DASH] {fmt_cooldown(jugador.dash_cooldown)}"
    if not jugador.en_suelo and jugador.dash_usos_aire <= 0:
        return "[DASH] SIN USO"
    return "[DASH] LISTO"


def fmt_arma(jugador) -> str:
    if not jugador.tiene_pala:
        return "[PALA] --"
    etiqueta = "GUADAÑA" if jugador.rango_ataque_mejorado else "PALA"
    if jugador.ataque_cooldown > 0:
        return f"[{etiqueta}] {fmt_cooldown(jugador.ataque_cooldown)}"
    return f"[{etiqueta}] LISTO"


def fmt_tiempo(segundos: float) -> str:
    total = max(0, int(segundos))
    return f"{total // 60:02d}:{total % 60:02d}"


def fmt_tiempo_dec(segundos: float) -> str:
    segundos = max(0.0, segundos)
    total = int(segundos)
    decima = int((segundos - total) * 10)
    return f"{total // 60:02d}:{total % 60:02d}.{decima}"
```

Reglas:

- `ALMAS`: `f"{jugador.almas}/{nivel.total_almas}"`; sin espacios alrededor de `/`.
- `VIDA EXTRA`: `f"VIDA EXTRA {jugador.almas_para_vida}/{ALMAS_POR_VIDA}"`.
- `NIVEL`: `f"NIVEL {nivel_indice + 1}/{len(NIVELES)}"`.
- `JEFE`: `f"{jefe.vida}/{JEFE_VIDA}"` + `FASE I` o `FASE II`.
- Un cooldown nunca se muestra como `0.0s`: se redondea hacia arriba a la décima.
- Los segundos usan siempre un decimal; el tiempo usa `MM:SS` (o `MM:SS.d` en victoria).
- Los textos de ancho variable van en slots fijos y alineados a la derecha.

---

## 7. Barra de jefe

- Vive en la zona central del riel, no en una barra flotante.
- 6 segmentos de 68×12 px, gap 4 px; número en slot de 48 px; fase `I/II`.
- **Fase II solo puede mostrar `3/6` o menos:** el cambio ocurre al tercer golpe.
  No usar `4/6` + `FASE II` como ejemplo ni como caso de test.
- Borde rojo en fase II; dorado en fase I.
- Sin texto instructivo permanente dentro de la barra.
- Al cambiar de fase, el mensaje “¡FASE II! LA PALA REBOTA — SOLO EL PISOTÓN LO DAÑA”
  aparece en el canal de mensajes, no encima de la barra.
- Nombre: “EL CUSTODIO DEL OSARIO” a 18 px; si no entra, “EL CUSTODIO”.
- El daño diferido usa `vida_mostrada` y `vida_objetivo`: al recibir daño,
  `vida_objetivo = jefe.vida`; cada frame, `vida_mostrada += (objetivo - mostrada) *
  (1 - exp(-14 * dt))`; si la diferencia es <0.01, igualar. La estela se dibuja
  entre ambos valores, no con una animación por segmento.

---

## 8. Mensajes: un solo canal

Hoy `dibujar_pista` y `aviso_jefe` compiten por el mismo espacio. Propuesta:

### 8.1 Especificación exacta

- Un único canal debajo del riel: `Rect(360,96,560,48)`.
- Padding vertical 4 px, horizontal 8 px; icono de 16×16 en `x+8`; texto en
  `x+32`; ancho útil de texto 520 px.
- Cuerpo 14 px, line-height 20 px, máximo 2 líneas (40 px + 8 px de padding).
- Sin etiqueta permanente “GUÍA DEL SEPULTURERO”; un icono pequeño alcanza.
- Entrada 150–200 ms (fade + slide de 8 px desde `y=88` a `y=96`); salida
  120–150 ms (fade); hold según prioridad.
- Solo se muestra un mensaje a la vez. Si llega otro de **mayor** prioridad,
  reemplaza al actual; si es de menor o igual prioridad y el actual sigue visible,
  se ignora. No se encola.
- El canal solo se dibuja con `estado == "jugando"`; los overlays de pausa,
  victoria y derrota tapan el HUD.
- Al pausar, los timers se congelan; no acumular `dt`.

### 8.2 Prioridad, duración y origen

| Prioridad | Tipo | Origen actual | Hold | Trigger |
|---:|---|---|---:|---|
| 3 | Jefe / fase | `aviso_jefe` y `jefe.estado == "cambio"` | 3.2 s | Aviso de salida sellada, fase II o muerte del jefe |
| 2 | Objeto | `texto_ayuda` al recoger pala/guadaña; vida extra | 3.5 s | `tiene_pala`/`rango_ataque_mejorado` cambiaron; `vidas` subió |
| 1 | Checkpoint | `texto_ayuda` de “PUNTO DE CONTROL” | 4.0 s | Se activa `punto_reintento` |
| 0 | Pista | `nivel.pista` / `texto_ayuda` inicial | 4.0 s | `cargar_nivel` o inicio de partida |

Reglas:

- Todos los holds caen dentro de 2.5–4 s.
- El mensaje de fase II se dispara una sola vez por cambio de fase; no en cada
  frame mientras `jefe.fase >= 2`.
- La pista inicial no debe reaparecer al volver de pausa si ya fue consumida.
- El wrap se mide con `fuente.size()`; una palabra que no entra se parte por
  caracteres; si aun así no entran 2 líneas, se aplica elipsis sin cortar la
  última palabra a la mitad.

---

## 9. Sistema visual

- **Panel:** `(14,11,18,240)` con sombra exterior y borde dorado; más opaco que hoy
  para que la luna no lave el texto.
- **Texto:** `HUD_TEXTO`; secundario `(170,158,146)` en vez de `(150,139,129)`.
- **Corazón vacío:** relleno `(40,32,44)`, borde `(120,100,125)`, interior oscuro;
  visible sin gritar.
- **Fuente:** `NotoSerifDisplay-Bold` con ruta absoluta desde `Path(__file__)`;
  fallback actual.
- **Escala:** 12 (labels), 14 (contadores y cuerpo), 18 (nombre de nivel/jefe);
  22 queda reservado para overlays de victoria/derrota, no para el riel.
- **Números:** slots de ancho fijo y alineación derecha; si la fuente no tiene cifras
  tabulares, igual no salta el layout.
- **Iconos:** corazón, rombo de alma, cuenta, ala de dash, pala/guadaña, reloj,
  calavera de jefe; todo con `pygame.draw`, sin assets nuevos. Tamaño base 16×16;
  corazones con radio 7 y pitch 28.
- **Colores:** dorado = recurso; turquesa = dash listo; rojo = peligro/fase II;
  violeta = guadaña; verde = listo.
- **Contraste:** texto pequeño a 4.5:1; elementos gráficos a 3:1.

### 9.1 Tipografía y slots

| Elemento | Tamaño | Slot / medida |
|---|---:|---|
| `[HP] 3/5` | 14 | slot 84 px, izquierda |
| `TIEMPO 01:23` | 14 | slot 112 px, derecha |
| `NIVEL 1/3` | 12 | slot 100 px, izquierda |
| `LA CRIPTA` | 18 | slot 300 px, izquierda |
| `EL CUSTODIO DEL OSARIO` | 18 | slot 300 px, izquierda |
| `FASE II` | 12 | slot 72 px, derecha |
| `3/6` | 12 | slot 48 px, derecha |
| Celdas derechas | 14 | 164×22; icono 16 + gap 6 |
| Mensaje | 14 | 520 px de ancho; line-height 20 |

Los slots son anchos máximos: el texto se alinea a la derecha dentro del slot y
nunca empuja a la zona siguiente. `GUADAÑA LISTO` mide ~132 px y entra en la
celda de 164 px con icono de 16 px.

---

## 10. Feedback y animación

La animación del HUD no es decoración: sirve para que un cambio de estado se
registre sin que el jugador tenga que leer. Regla: **si no comunica un cambio,
no se anima**. El HUD se anima con `dt`, se puede interrumpir y nunca mueve el
layout.

### 10.1 Principios

- **Inmediatez:** el feedback empieza en el mismo frame del evento; si el evento
  se pierde, el jugador cree que no pasó nada.
- **Brevedad:** 80–250 ms para casi todo; los mensajes duran 2.5–4 s.
- **Jerarquía:** el movimiento más fuerte es para lo que cambia la supervivencia
  (daño, vida baja, jefe); el resto es sutil.
- **Estabilidad:** no animar ancho, posición ni tamaño del riel; solo contenido
  interno. El layout no debe saltar.
- **Interrumpible:** un mensaje nuevo reemplaza al anterior; un golpe nuevo
  reinicia el flash; nunca encolar animaciones que tapen la acción.
- **Una cosa a la vez:** no combinar traslación + rotación + escala grande en el
  mismo elemento.
- **Accesibilidad:** nada de flashes >3 Hz ni sacudidas de pantalla completa;
  el HUD se mantiene legible.

### 10.2 Catálogo de animaciones

| Evento | Qué se anima | Duración | Curva | Nota |
|---|---|---|---|---|
| Alma recogida | Número `12 → 13` con pop `1.0 → 1.12 → 1.0` + brillo de la cuenta | 180–220 ms | `ease_out_back` | Si recoge varias seguidas, agrupar en un solo pop; no encadenar tres |
| Daño | Corazón afectado: flash blanco→rojo + escala `1.0 → 1.08 → 1.0` | 120–180 ms | `ease_out_cubic` | Solo el corazón, no todo el riel; la viñeta roja ya existe |
| Vida baja | Latido del corazón restante + `1/5` en rojo | Período 0.9–1.2 s | Seno | Solo con `vidas == 1`; sin estroboscopio |
| Dash listo | Pulso turquesa + `LISTO` | 180–220 ms, una vez | `ease_out_back` | No dejar un loop infinito; el pulso se repite solo si hay una razón |
| Dash cargando | Arco radial + segundos | Igual al cooldown | Lineal | El arco no “rebota”; el texto cambia cada 0.1 s |
| Pala lista | Igual que dash, en violeta | 180–220 ms, una vez | `ease_out_back` | Mismo tratamiento que dash |
| Jefe dañado | Segmento cae + estela blanca/roja | 150–250 ms | `ease_out_cubic` | Sin sacudir la pantalla; el daño diferido se lee mejor |
| Fase de jefe | Borde dorado→rojo + mensaje de fase | 200 ms | `ease_in_out_cubic` | El texto instructivo va al canal de mensajes |
| Mensaje | Fade + slide vertical de 8 px | Entrada 150–200 ms; hold 2.5–4 s; salida 120–150 ms | `ease_out_cubic` al entrar; `ease_in_out_cubic` al salir | Máximo 2 líneas; interrumpible |
| Vida extra | Toast + flash del rosario | 400–600 ms | `ease_out_back` | El contador no salta de 0 a 10; el reset se avisa |
| Tiempo | Sin animación | — | — | Actualizar una vez por segundo; no parpadear |
| Panel | Sin animación idle | — | — | No “respirar” el riel ni moverlo |
| Pista | Fade in al entrar al nivel | 200 ms | `ease_out_cubic` | Sin slide largo; el wrap ya está resuelto |

### 10.3 Duraciones y curvas

| Tipo | Duración | Curva |
|---|---|---|
| Feedback inmediato (daño, pickup, click) | 80–150 ms | `ease_out_cubic` |
| Cambio de estado (contador, dash listo) | 150–250 ms | `ease_out_back` o `ease_out_cubic` |
| Entrada de mensaje | 150–200 ms | `ease_out_cubic` |
| Salida de mensaje | 120–150 ms | `ease_in_out_cubic` |
| Hold de mensaje | 2.5–4 s | — |
| Latido de vida baja | 0.9–1.2 s por latido | Seno |
| Cooldown / progreso | Igual al cooldown restante | Lineal |
| Transición de color de borde | 200 ms | `ease_in_out_cubic` |

Reglas:

- Entradas con **ease-out**; salidas con **ease-in/ease-in-out**; movimientos
  entre dos puntos con **ease-in-out**; progreso/cooldown con **linear**.
- Overshoot solo en pops: `1.12–1.15`, nunca en el layout ni en paneles.
- Si dudás, acortá: es más común que una animación sea demasiado larga que
  demasiado corta (NN/g).
- No usar `time.time()`; usar `dt` y clampearlo con `MAX_DT` (hoy `1/30 ≈
  0.033 s`) para evitar saltos después de una pausa o un frame perdido. No crear
  un segundo clamp de 0.05 s.

### 10.4 Ejemplos y qué tomar

- **Returnal (Housemarque):** la UI es “gameplay first”; ajustaron los tiempos de
  animación, el color y la jerarquía para que la información crítica se lea en
  combate. En vida baja suman viñeta, grietas del visor, glitch, color y audio.
  **Tomar:** timing, jerarquía y escalada de vida baja. **No copiar:** el glitch
  de pantalla completa; en IN CRYPTA el HUD es chico y no debe tapar la acción.
- **Hollow Knight:** el contador de geo espera 1.5 s y después suma de a uno; el
  HUD queda “detrás” de la verdad para que el pickup se lea como evento.
  **Tomar:** contador diferido y legible. **Adaptar:** en IN CRYPTA alcanza con
  un count-up/pop de ~200 ms; 1.5 s sería demasiado para un plataformero rápido.
- **Celeste:** el color del pelo de Madeline es el HUD diegético del dash
  (rojo=1, azul=0, rosa=2). **Tomar:** estado legible de un vistazo; en IN
  CRYPTA se traduce a icono + color + segundos, sin tocar al personaje.
- **Defold HUD sample:** el puntaje sube de a poco, los pickups flotan y el total
  hace un bounce al sumar. **Tomar:** count-up + pop + float como receta, no como
  estética.
- **Accessible Game Design (HUD):** recomienda animación/juice para urgencia
  (timer, vida) y no depender solo de números. **Tomar:** animar solo cuando hay
  un cambio relevante; el HUD no tiene animación idle.

### 10.5 Implementación en pygame

La animación se actualiza **antes** de dibujar y el render solo lee estado. No
se mutan tweens dentro de `dibujar_hud`.

```python
import math
from dataclasses import dataclass

from efectos import ease_out_back, ease_out_cubic, ease_in_out_cubic


@dataclass
class Tween:
    duracion: float
    transcurrido: float = 0.0
    curva: str = "out_cubic"

    def update(self, dt: float) -> None:
        self.transcurrido = min(self.duracion, self.transcurrido + dt)

    @property
    def t(self) -> float:
        if self.duracion <= 0:
            return 1.0
        return self.transcurrido / self.duracion

    def valor(self) -> float:
        t = self.t
        if self.curva == "out_back":
            return ease_out_back(t)
        if self.curva == "in_out_cubic":
            return ease_in_out_cubic(t)
        if self.curva == "linear":
            return t
        return ease_out_cubic(t)
```

En el loop:

```python
dt = min(clock.tick(FPS) / 1000.0, MAX_DT)
juego.actualizar_hud(dt)
juego.dibujar()
```

`actualizar_hud(dt)` debe llamarse también en pausa con el mismo `dt` clampeado
para congelar o avanzar animaciones de forma explícita; no usar el reloj real.
El `dt` que recibe el HUD no debe volver a clampearse a 0.05 si el loop ya usa
`MAX_DT`.

#### Detección de eventos sin tocar gameplay

El HUD no debe modificar `actualizar_almas`, `perder_vida` ni `dañar_jefe`. Guardar
un snapshot anterior en `HudModel` y comparar en `actualizar_hud(dt)`:

- `almas > almas_prev` → pop de alma. Si hubo varias recogidas en el mismo frame,
  un solo pop y actualizar `almas_prev` al valor actual.
- `vidas < vidas_prev` → flash del corazón perdido (`índice = vidas`), no de todo
  el riel.
- `vidas > vidas_prev` → toast de `VIDA EXTRA`; si `vidas == VIDAS_MAXIMAS`, no
  mostrar “VIDA EXTRA” (ver §6.2).
- `dash_cooldown > 0` y luego `<= 0` → pulso `DASH LISTO`; no pulsar al aterrizar
  si solo cambió `dash_usos_aire`.
- `ataque_cooldown > 0` y luego `<= 0` → pulso de arma lista.
- `jefe.vida < jefe_vida_prev` → actualizar `vida_objetivo` y la estela.
- `jefe.fase > jefe_fase_prev` → mensaje de fase una sola vez.
- Al cargar nivel, reiniciar `*_prev` para no disparar eventos falsos.

Recetas concretas:

- **Pop de texto:** cachear la superficie del texto al tamaño final y escalar
  solo esa superficie durante el pop, anclada por centro. Para no re-renderizar,
  cachear 2–3 escalas (`1.0`, `1.08`, `1.12`) o usar
  `pygame.transform.smoothscale` sobre una superficie chica; nunca escalar el
  panel entero.
- **Fade de mensaje:** `copia = base.copy(); copia.set_alpha(alpha)` y blitear la
  copia. No mutar la superficie guardada en el cache. Una copia por frame para
  un solo mensaje es aceptable; si se perfila, cachear 8–16 niveles de alpha.
- **Latido:** `pulso = 0.5 + 0.5 * math.sin(t * math.tau * 1.1)`; escala
  `1.0 + 0.04 * pulso`; solo si `vidas == 1` y `estado == "jugando"`.
- **Cooldown radial:** `pygame.draw.arc` con `start=-math.pi/2` y un `stop` que
  avanza con `progreso = 1 - restante / total`; el sentido se ajusta invirtiendo
  el signo y se verifica en pantalla.
- **Daño diferido del jefe:** `vida_objetivo` se actualiza al recibir daño;
  cada frame `vida_mostrada += (objetivo - mostrada) * (1 - exp(-14 * dt))`;
  si `abs(objetivo - mostrada) < 0.01`, igualar. Dibujar la estela entre ambos
  valores; no animar segmento por segmento.
- **Mensaje:** máquina de estados `OCULTO → ENTRANDO → VISIBLE → SALIENDO`;
  al recibir uno nuevo, reiniciar el estado y el timer, no encolar.
- **`efecto_hud`:** hoy usa `time.time()` y nunca se actualiza. Reemplazarlo por
  un `Tween` con `dt` o agregarle `actualizar(dt)`; no usarlo para animaciones
  nuevas sin migrarlo.

### 10.6 Accesibilidad y límites

- **Flashes:** no más de 3 flashes generales/rojos por segundo; evitar secuencias
  de más de 5 s; no usar rojo saturado en flashes grandes (WCAG 2.3.1; Game
  Accessibility Guidelines). El HUD es chico, pero la regla aplica igual.
- **Sin pantalla completa (solo HUD):** el HUD no agrega flashes de pantalla
  completa ni sacudidas de cámara; como mucho, el corazón afectado y 2 px del
  panel izquierdo. El `flash` de `perder_vida` y `camara.sacudir` ya existen en
  el juego y quedan **fuera de alcance**: no modificarlos.
- **Movimiento reducido:** dejar `HUD_REDUCIR_MOVIMIENTO` (constante o setting
  futuro). Si está activo: reemplazar slide/scale por fade o cambio instantáneo,
  acortar duraciones, desactivar latido/pulso; mantener arco y números.
- **No depender del color:** cada estado tiene icono + número + texto.
- **Sin mareo:** nada de zoom, parallax ni desplazamientos largos; los mensajes
  se mueven como máximo 8 px.
- **Probar a 30 y 60 fps:** la animación debe verse igual; si se pausa, no debe
  acumular `dt`.
- **No usar la etiqueta “epilepsy safe”** para un setting; describir el efecto
  (“intensidad de efectos”, “movimiento reducido”).

### 10.7 Checklist de animación

- [ ] Cada animación tiene trigger, propiedad, duración y curva.
- [ ] No hay animación idle en el riel.
- [ ] El layout no cambia durante la animación.
- [ ] Las animaciones se interrumpen y reemplazan sin encolarse.
- [ ] `dt` usa `MAX_DT`; no se usa `time.time()`.
- [ ] No hay flashes >3 Hz ni sacudidas nuevas de pantalla completa desde el HUD.
- [ ] Existe `HUD_REDUCIR_MOVIMIENTO` o equivalente.
- [ ] Tests determinísticos de tweens y estados de mensaje.
- [ ] HUD <1 ms y 60 fps estables.

---

## 11. Arquitectura propuesta

Recomiendo extraer el HUD a `hud.py`, sin tocar gameplay:

- `HudTheme`: colores, tamaños, espaciado.
- `HudLayout`: rectángulos de las 3 zonas, mensajes y barra de jefe.
- `HudModel`: snapshot de solo lectura (`vidas`, `vidas_max`, `almas`,
  `almas_total`, `almas_para_vida`, `dash_cooldown`, `dash_usos_aire`,
  `en_suelo`, `ataque_cooldown`, `tiene_pala`, `rango_ataque_mejorado`,
  `jefe`, `jefe_vida`, `jefe_fase`, `tiempo`, `nivel_indice`, `estado`,
  `pista`, `aviso`) y los `*_prev` para detectar eventos.
- `HudRenderer`: dibuja el modelo; no conoce `Juego`.
- `TextoCache`: caché por `(texto, tamaño, color, sombra)`.
- `MensajeHUD`: texto, prioridad, duración y tipo.

`Juego.dibujar_hud` solo arma el `HudModel` y llama al renderer. Si se prefiere el
diff mínimo, se puede hacer todo dentro de `juego.py` con las mismas piezas; la
recomendación es `hud.py` para poder testearlo.

### 11.1 Tests propuestos

`tests/test_hud.py` (headless, sin ventana real):

- No hay intersección entre las 3 zonas, la barra de jefe y el canal de mensajes.
- Las 4 celdas derechas son 164×22 y no se solapan; el ancho total no cambia
  con/sin pala.
- La barra de jefe tiene 6 segmentos de 68×12, gap 4 y slot de 48 para `3/6`.
- Los formatos son exactos: `3/5`, `12/42`, `7/10`, `LISTO`, `0.4s`, `4/6`,
  `[PALA] --`, `[GUADAÑA] LISTO`, `SIN USO`.
- `fmt_cooldown(0.35) == "0.4s"`, `fmt_cooldown(0) == "LISTO"`.
- `fmt_dash` prioriza cooldown sobre `SIN USO`; en el aire sin uso da `SIN USO`.
- `fmt_tiempo(59.9) == "00:59"`, `fmt_tiempo(60) == "01:00"`,
  `fmt_tiempo_dec(83.27) == "01:23.2"`.
- La pista no supera 2 líneas, no corta palabras y la elipsis entra en el ancho.
- La prioridad de mensajes funciona: jefe > objeto > checkpoint > pista; uno de
  menor prioridad no reemplaza al visible.
- El mensaje no se dibuja fuera de `estado == "jugando"`.
- Los corazones vacíos usan un color con contraste mínimo.
- El render de texto cacheado no vuelve a llamar a `font.render` para la misma clave.
- `Tween(0.2)` con `dt=0.1` da `t=0.5`; con otro `dt=0.2` queda en `t=1.0`;
  `linear` no supera 1; `out_back` puede superar 1 solo en el pop.
- `HUD_REDUCIR_MOVIMIENTO` desactiva slide/latido y mantiene números/arco.
- `dibujar_hud` no crashea con `jefe is None` y `aviso_jefe > 0`.
- La vida extra solo dispara toast si `vidas` aumentó; con vidas al máximo no
  muestra “VIDA EXTRA”.
- El daño diferido de jefe converge a `vida_objetivo` y no queda oscilando.

### 11.2 Herramientas pygame y recetas de dibujo

Esta es la parte técnica que faltaba: cómo llevar las decisiones visuales a
**pygame-ce 2.5.8** sin pelear con el motor. No hace falta cambiar de librería ni
usar assets externos; todo se resuelve con `pygame.Surface`, `pygame.draw`,
`pygame.font` y `pygame.transform`.

#### Superficies y capas

- El HUD se dibuja en `self.pantalla`, **después** de escalar el mundo con
  `pygame.transform.scale`. Nunca en `self.superficie_mundo`: si se dibuja ahí,
  se escala y se mueve con la cámara.
- Los paneles se construyen en una `Surface` aparte con `pygame.SRCALPHA`:
  fondo, borde, línea dorada y esquinas. Se hace **una vez** y se cachea.
- `pygame.SRCALPHA` permite transparencia por píxel; `Surface.set_alpha()` aplica
  alpha global. No mezclar ambos sin entender el resultado: para paneles con
  esquinas redondeadas y alpha, usar `SRCALPHA` y colores RGBA.
- `Surface.convert_alpha()` acelera el blit, pero necesita que el display esté
  inicializado. En tests headless, crear el display dummy antes.
- Para glow/chispas: `pantalla.blit(superficie, pos, special_flags=pygame.BLEND_RGBA_ADD)`.
  Usarlo con moderación; 2–3 capas alcanzan. No hacer glow de pantalla completa
  por frame.
- Para sombras de panel: 2–3 rectángulos redondeados semitransparentes desplazados,
  o una superficie de sombra cacheada. Evitar blur costoso.

#### Primitivas de dibujo

- `pygame.draw.rect(superficie, color, rect, width=0, border_radius=12)` para
  paneles y celdas. `width=1` para bordes.
- `pygame.draw.line` para separadores, esquinas y detalles de 1 px.
- `pygame.draw.aaline` / `pygame.draw.aalines` para diagonales y ornamentos;
  `pygame.draw.line` deja escalones visibles en diagonales.
- `pygame.draw.circle` para corazones, cuentas del rosario y halos.
- `pygame.draw.polygon` para el rombo de alma, la pala, el ala de dash y la calavera.
- `pygame.draw.arc` para curvas góticas; trabaja en radianes y no rellena.
- `pygame.gfxdraw` existe en pygame-ce y sirve para antialias relleno, pero no es
  necesario para este estilo. Si se usa, encapsularlo y probar que no rompa el
  render en el export.
- Los iconos se dibujan en una `Surface` chica con `SRCALPHA`, se cachean por
  `(tipo, tamaño, estado, color)` y se blitean. No redibujar el corazón 5 veces
  por frame si no cambió.

#### Texto y números

- `pygame.font.Font(ruta, tamano)` + `font.render(texto, True, color)`.
  Antialias siempre en `True`.
- `font.size(texto)` devuelve `(ancho, alto)` y es la base para wrap por píxeles
  y para slots de ancho fijo. `font.get_height()` sirve para line-height.
- Cachear por `(texto, tamano, color, sombra)`. La posición se calcula al dibujar;
  no se cachea el `Rect` final.
- Sombra: renderizar el texto dos veces con offset de 2–3 px, o cachear la versión
  con sombra. No usar blur.
- Números: formatear con `f"{vidas}/{VIDAS_MAXIMAS}"`,
  `f"{max(0, cooldown):.1f}s"`, `f"{minutos:02d}:{segundos:02d}"`.
  Alinear a la derecha en un slot fijo para que no baile el layout.
- Para cifras tabulares: si la fuente no las tiene, usar un ancho de celda fijo
  (`max(font.size("00/00")[0], ...)`) y alinear a la derecha.
- Wrap: **no** usar `textwrap.wrap(width=64)`; medir palabras con `font.size()`.
  Si una palabra sola no entra, partirla por caracteres; si el total supera 2
  líneas, aplicar elipsis.
- Fuente: ruta absoluta con `Path(__file__).resolve().parent / "export/..."`;
  fallback a `pygame.font.Font(None, tamano)` si no existe.

#### Layout y rectángulos

- Usar `pygame.Rect` para las tres zonas, el canal de mensajes y la barra de jefe.
  `Rect.colliderect` es la base de los tests de solapamiento.
- Anclajes útiles: `rect.midleft`, `rect.midright`, `rect.center`,
  `rect.topleft`, `rect.move()`, `rect.inflate()`.
- Para recortar texto o barras: `Surface.set_clip(rect)` / `Surface.get_clip()`,
  o `pantalla.blit(surf, pos, area=rect)`.
- No hardcodear `960×540` ni `1280×720` en cada función: usar `ANCHO`, `ALTO`,
  `HUD_MARGEN_X`, `HUD_MARGEN_Y`, `HUD_GAP`, `HUD_ALTO`.
- Modo debug: un flag `DEBUG_HUD` que dibuje los rects en magenta con
  `pygame.draw.rect(pantalla, (255, 0, 255), rect, 1)`. Se apaga en producción.

#### Animación

La especificación completa (principios, catálogo, duraciones, curvas, ejemplos y
accesibilidad) está en **§10**. Reglas técnicas para esta sección:

- `update(dt)` antes de dibujar; `dibujar_hud` solo lee estado. No mutar tweens
  dentro del render.
- `EfectoAnimacion` actual usa `time.time()`; no usarlo para el HUD nuevo. Crear
  un `Tween` con `dt` en `hud.py` o agregarle `actualizar(dt)`.
- `dt` clampeado con `MAX_DT` (hoy `1/30`); no crear otro clamp de 0.05 s.
- Pop de contador: escalar solo la superficie del texto cacheada, no el panel;
  cachear 2–3 escalas o usar `smoothscale` durante 200 ms.
- Fade de mensaje: `copia = base.copy(); copia.set_alpha(alpha)`; no mutar la
  superficie original del cache.
- Latido de corazón: `sin(t * tau * 1.1)` y escala `1.0 → 1.04`; solo con vida
  baja. `sin(t * 9)` son radianes por segundo (~1.43 Hz), no 9 Hz; sirve, pero
  conviene expresarlo con `tau` para que se lea la frecuencia.
- Barra de jefe: 6 `Rect` fijos; llenar/vaciar con `pygame.draw.rect`, sin crear
  superficies nuevas. El daño diferido se calcula con `vida_mostrada` y
  `vida_objetivo`, no con una animación de por segmento.

#### Rendimiento

- Cachear paneles, iconos y texto; `convert_alpha()` después de `set_mode`.
- Evitar `pygame.Surface` por frame; reutilizar las cacheadas. La excepción es
  una copia por frame para el fade de un mensaje; si se perfila, cachear alphas.
- Perfilar con `time.perf_counter()` alrededor de `dibujar_hud()`; objetivo
  **<1 ms** de HUD.
- No escalar texto con `pygame.transform.scale`; renderizar al tamaño final.
- `font.render` es caro; el cache es obligatorio.
- Si se agrega una escala de HUD accesible, cachear por escala y no re-renderizar
  todo en cada frame.

#### Errores comunes a evitar

- Dibujar el HUD en `superficie_mundo` (se escala y se mueve con la cámara).
- Usar `set_alpha()` sobre una superficie con `SRCALPHA` y esperar que se comporte
  como alpha global.
- Llamar `convert_alpha()` antes de `pygame.display.set_mode()`.
- Usar `textwrap` por caracteres: no respeta la fuente ni el ancho real.
- Usar `time.time()` para animaciones: se rompe con pausa, `dt` y tests.
- Hardcodear `960×540` o `1280×720` en todas las funciones.
- Acceder a `self.jefe` sin comprobar `None`.
- Cambiar el ancho del panel derecho al recoger la pala.
- Renderizar texto con `font.render` en cada frame.
- Usar `pygame.gfxdraw` sin fallback o sin testear el export.

#### Recetas mínimas

Panel cacheado:

```python
def crear_panel(ancho, alto, alpha=240):
    panel = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pygame.draw.rect(panel, (14, 11, 18, alpha), panel.get_rect(), border_radius=12)
    pygame.draw.rect(panel, (*HUD_BORDE, 200), panel.get_rect(), 1, border_radius=12)
    pygame.draw.line(panel, (*HUD_ORO, 120), (12, 1), (ancho - 12, 1), 1)
    return panel.convert_alpha()
```

Cache de texto:

```python
class TextoCache:
    def __init__(self, cargar_fuente):
        self.cargar_fuente = cargar_fuente
        self.cache = {}

    def render(self, texto, tamano, color, sombra=False):
        clave = (texto, tamano, tuple(color), sombra)
        if clave not in self.cache:
            fuente = self.cargar_fuente(tamano)
            imagen = fuente.render(texto, True, color)
            if sombra:
                base = pygame.Surface(
                    (imagen.get_width() + 3, imagen.get_height() + 3),
                    pygame.SRCALPHA,
                )
                base.blit(fuente.render(texto, True, (0, 0, 0)), (3, 3))
                base.blit(imagen, (0, 0))
                imagen = base
            self.cache[clave] = imagen
        return self.cache[clave]
```

Wrap por píxeles:

```python
def _partir_palabra(palabra, fuente, ancho_max):
    partes, actual = [], ""
    for caracter in palabra:
        prueba = actual + caracter
        if not actual or fuente.size(prueba)[0] <= ancho_max:
            actual = prueba
        else:
            partes.append(actual)
            actual = caracter
    if actual:
        partes.append(actual)
    return partes


def envolver(texto, fuente, ancho_max, max_lineas=2):
    palabras = texto.split()
    lineas, actual = [], ""
    for palabra in palabras:
        if fuente.size(palabra)[0] > ancho_max:
            if actual:
                lineas.append(actual)
                actual = ""
            partes = _partir_palabra(palabra, fuente, ancho_max)
            lineas.extend(partes[:-1])
            actual = partes[-1]
            continue
        prueba = f"{actual} {palabra}".strip()
        if fuente.size(prueba)[0] <= ancho_max:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    if len(lineas) > max_lineas:
        lineas = lineas[:max_lineas]
        ultima = lineas[-1]
        while ultima and fuente.size(ultima + "…")[0] > ancho_max:
            ultima = ultima[:-1]
        lineas[-1] = ultima.rstrip(".,;: ") + "…"
    return lineas
```

Esta versión parte palabras que no entran y garantiza que la elipsis tampoco
desborde el ancho. No usar `textwrap.wrap(width=64)`.

Los formatos exactos de tiempo, cooldown, dash y arma están en **§6.3**. No
duplicar `fmt_cooldown` con otro redondeo: un cooldown nunca debe mostrar `0.0s`.

Debug de layout:

```python
if DEBUG_HUD:
    for rect in (zona_izq, zona_centro, zona_der, canal_mensajes):
        pygame.draw.rect(pantalla, (255, 0, 255), rect, 1)
```

Test headless:

```python
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((ANCHO, ALTO))
```

---

## 12. Fases

| Fase | Trabajo | Verificación |
|---|---|---|
| 0. Base | Verificar rama/HEAD/`git status`, tests actuales y 6 capturas | `TESTS_INCRYPTA_OK`; 6 capturas del harness |
| 1. Layout | Riel único, 3 zonas, 2×2 derecha, sin solapamientos, ancho fijo, contraste | Capturas de 6 estados; 0 intersecciones de rects |
| 2. Contadores | Vida/almas/vida extra/dash/pala/tiempo/jefe con números | Formatos exactos de §6.3; sin `...` ni `0.0–1.0` |
| 3. Mensajes y feedback | Canal único, wrap por píxeles, prioridad, animaciones de §10, caché | Pista ≤2 líneas; sin superposición; animaciones dentro de §10; 60 fps |
| 4. Cierre | Tests de HUD, capturas antes/después, docs | Tests nuevos + existentes; evidencia visual |

Fase 0: si `/tmp/opencode/hud/capturar_hud.py` no existe, recrearlo antes de
tocar el HUD. El harness no se versiona y no es parte del juego.

Estimación: **8–10 h** de trabajo efectivo, en fases chicas y testeables
(la animación suma ~1 h de implementación y pulido).

---

## 13. Criterios de aceptación

- 0 solapamientos entre las 3 zonas, jefe, pista y aviso en los 6 estados.
- Geometría exacta: riel `1232×72`; zonas `336/512/360`; celdas derechas
  `164×22`; mensaje `560×48`; barra de jefe `6×68×12`.
- El panel derecho mide lo mismo con y sin pala.
- Todos los contadores muestran número y unidad cuando corresponde; ningún
  cooldown se muestra como `0.0s`; el rosario no muestra `10/10`.
- Fase II se muestra con `3/6` o menos, nunca `4/6`.
- La pista nunca se corta a mitad de palabra; máximo 2 líneas con elipsis que
  entra en el ancho.
- Corazones vacíos visibles; texto con contraste verificable.
- Sin `font.render()` repetido por frame para el mismo texto/color/tamaño.
- Cada animación tiene trigger, propiedad, duración y curva documentados en §10.
- Las animaciones usan `dt`/`MAX_DT`, son interrumpibles y no cambian el layout.
- No hay flashes >3 Hz ni sacudidas nuevas de pantalla completa desde el HUD;
  el `flash`/`camara.sacudir` existentes no se modifican. Existe
  `HUD_REDUCIR_MOVIMIENTO` o equivalente.
- `tests/test_logica.py` sigue pasando; se agrega `tests/test_hud.py` con tests
  de tweens, formatos, prioridades, estados de mensaje y casos borde.
- No se modifica fondo, luna, cámara, entidades, niveles, audio ni gameplay.
- Capturas antes/después de los 6 estados:
  inicio con pista, nivel 1 con progreso, nivel 1 crítico, nivel 2 con pala,
  jefe fase 1 y jefe fase 2 con aviso.

---

## 14. Fuera de alcance

- Mover la luna o cambiar el fondo: si molesta el contraste, se resuelve con
  opacidad/sombra del HUD.
- Cambiar la lógica de almas, vidas o dash.
- Mostrar 10/10 en el rosario (requiere tocar la recogida).
- Sprites, animaciones del personaje, farol diegético, audio, menús y export.
- Rediseñar la pantalla de pausa/victoria más allá de mostrar tiempo/almas.

---

## 15. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| El riel full-width tapa demasiado juego | 72 px de alto; mensajes solo contextuales; medir área ocupada |
| La luna lava el texto | Subir opacidad del panel a 240 y agregar sombra exterior |
| El panel derecho se rompe al agregar la pala | Ancho fijo y slot reservado |
| La pista sigue truncando | Wrap por píxeles, partir palabras largas y elipsis que quepa |
| El mensaje de 48 px desborda | Cuerpo 14 px, line-height 20, padding vertical 4; no meter una tercera línea |
| La grilla 2×2 no entra con 10 cuentas | Celdas 164×22; texto 14 px y pips de 5×3 con pitch 6 debajo |
| Se muestra `4/6` en fase II | Test explícito: fase II solo con `vida <= 3`; ejemplo `3/6` |
| Se toca el flash/sacudida existentes | Tratarlos como fuera de alcance; el HUD solo agrega feedback local |
| El harness de capturas desaparece de `/tmp` | Recrearlo en Fase 0; no versionar capturas temporales |
| Los tests de HUD son frágiles | Testear rects, formatos, prioridades y tweens; no píxeles exactos |
| La animación distrae o marea | Duraciones de §10, sin loops fuertes, sin flashes >3 Hz, `HUD_REDUCIR_MOVIMIENTO` |
| El pop escala todo el panel | Escalar solo la superficie del texto cacheada; el layout no se mueve |
| El daño diferido del jefe se siente lento | 150–250 ms y estela clara; testear en los 6 estados |
| Se toca gameplay sin querer | Cambios solo en `hud.py`/`juego.py` (dibujo) y `config.py` (tokens HUD) |
| Se rompe el export | No tocar el export; el HUD nativo es solo pygame |

---

## 16. Prompt para diseñar el HUD

> Copiar desde el inicio del bloque hasta el final. Está pensado para un agente
> de diseño/implementación o para una sesión nueva de opencode.

````text
# Prompt — Diseño e implementación del HUD de IN CRYPTA

## Rol

Sos un diseñador de UI/UX de videojuegos y desarrollador senior de pygame.
Trabajás sobre IN CRYPTA, un plataformero gótico 2D hecho con pygame-ce.
Tu tarea es diseñar y, si se aprueba, implementar una renovación integral del HUD.

## Contexto del proyecto

- Repo: `/home/sanodesu/unahur/PlataformeroMDA`
- Rama de trabajo: `pygame-v0.2.2-dev`. HEAD al crear el plan: `79733e1`.
  Verificar `git status` y `git log -1` antes de empezar; puede haber cambios
  del usuario en `niveles.py`, `tests/test_logica.py` o docs.
- Juego: IN CRYPTA, plataformero gótico 2D, 3 niveles, jefe final.
- Stack: Python 3.14.8, pygame-ce 2.5.8.
- Ventana: 1280×720. Mundo virtual: 1024×576, escalado 1.25×.
- El HUD se dibuja nativo después de escalar el mundo.
- Fuente actual: `export/gdevelop_nativo/assets/NotoSerifDisplay-Bold.ttf`.
- Estilo: Blasphemous, Castlevania: SOTN, Ender Lilies.
- Idioma de textos y comentarios: español rioplatense.
- El proyecto usa `pygame.draw`, sin assets externos de UI.
- **Fuente de verdad:** `docs/PLAN_HUD_IN_CRYPTA.md`. Si este prompt y el
  documento difieren, manda el documento; no inventar medidas.

## Restricciones duras

1. **Solo HUD.** No toques fondo, luna, cámara, entidades, niveles, audio,
   sprites, menús, gameplay ni export GDevelop. El `flash` de pantalla completa
   y `camara.sacudir` existentes en `perder_vida` quedan fuera de alcance.
2. **No cambies la lógica** de almas, vidas, dash, ataque o jefe.
3. **No agregues assets externos** ni librerías de UI.
4. **No cambies el ancho del panel derecho** al recoger la pala.
5. **No uses solo iconos:** el usuario pidió contadores con número.
6. **No apiles pista y aviso:** un solo canal de mensajes.
7. **No uses `...` ni progreso `0.0–1.0`** para estados; usá `LISTO` o segundos.
8. **No toques el HUD sin mostrar primero el plan y esperar aprobación.**
9. Mantené `tests/test_logica.py` en verde.
10. Si el contraste contra la luna es bajo, subí la opacidad/sombra del HUD;
    no muevas la luna.
11. No animes ancho, posición ni tamaño del riel; las animaciones no cambian el
    layout.
12. No uses flashes >3 Hz ni sacudidas nuevas de pantalla completa desde el HUD;
    el HUD debe seguir legible.
13. No commitees ni toques cambios ajenos sin pedido explícito.

## Estado actual que hay que corregir

- Panel izquierdo 344×68 en (24,16).
- Panel derecho 542×68 con pala / 404×68 sin pala; cambia de ancho.
- Barra de jefe 660×76 en x=310–970, y=16–92: tapa ambos paneles.
- Pista 640 px en y=16 o y=98: tapa “ALMAS” y el rosario.
- Aviso de jefe también en y=98: se superpone con la pista.
- Corazones vacíos con borde (78,62,82) sobre panel (14,11,18): casi invisibles.
- Dos contadores llamados “ALMAS”: total del nivel y rosario de vida extra.
- El rosario nunca muestra 10/10 porque se resetea en el mismo frame.
- Dash muestra 0.0–1.0; arma muestra “...”.
- Tiempo solo aparece en victoria; el README lo promete en HUD.
- `efecto_hud` se inicia pero nunca se actualiza ni se dibuja.
- Texto renderizado por frame sin caché.
- No hay tests de HUD.

## Decisiones de diseño que debés respetar

### Layout

- **Riel superior único full-width**, no tres paneles flotantes.
- Riel `Rect(24,16,1232,72)`; zonas exactas `Rect(24,16,336,72)`,
  `Rect(372,16,512,72)`, `Rect(896,16,360,72)`; gaps de 12 px.
- No hay padding exterior adicional; el padding de 12 px es interno y el
  contenido vertical vive en `y=28..76`.
- Contenido: izquierda `Rect(36,28,312,48)`, centro `Rect(384,28,488,48)`,
  derecha `Rect(908,28,336,48)`.
- Mensajes: `Rect(360,96,560,48)`; padding vertical 4, horizontal 8; cuerpo 14,
  line-height 20; ancho útil de texto 520 px.
- Área ocupada: ~9.6% con riel; ~12.5% con mensaje.
- Zona izquierda: 2 filas, HP+tiempo / corazones.
- Zona central: 2 filas; nivel si no hay jefe; nombre+barra si hay jefe.
- Zona derecha: **grilla 2×2**, celdas 164×22, gaps 8×4; almas, vida extra,
  dash y pala. No son cuatro filas.
- Sin etiqueta permanente “SEPULTURERO”.
- Constantes nuevas: `HUD_MARGEN_X=24`, `HUD_MARGEN_Y=16`, `HUD_ALTO=72`,
  `HUD_GAP=12`, `HUD_PADDING=12`, `HUD_ZONA_IZQ=336`, `HUD_ZONA_CENTRO=512`,
  `HUD_ZONA_DER=360`, `HUD_MENSAJE_ANCHO=560`, `HUD_MENSAJE_ALTO=48`,
  `HUD_MENSAJE_Y=96`.

### Contadores

- Vida: `[HP] 3/5` + 5 corazones.
- Almas: `[ALMA] 12/42` (nivel actual / total del nivel).
- Vida extra: `VIDA EXTRA 7/10` + 10 cuentas; si vidas está al máximo, no
  mostrar “VIDA EXTRA”.
- Dash: `[DASH] LISTO`, `[DASH] 0.4s` o `[DASH] SIN USO`. Prioridad: cooldown
  >0 → segundos; si no, aire sin uso → `SIN USO`; si no, `LISTO`.
- Pala / guadaña: `[PALA] LISTO`, `[GUADAÑA] LISTO` o `0.2s`; sin arma:
  `[PALA] --`.
- Tiempo: `TIEMPO 01:23`; en victoria, `MM:SS.d`.
- Jefe: 6 segmentos + `4/6` + `FASE I`, o `3/6` + `FASE II`. **Fase II nunca
  muestra `4/6`.**
- Cooldowns: redondear hacia arriba a la décima; nunca mostrar `0.0s`.
- Formatos exactos y funciones de §6.3 del documento.

### Barra de jefe

- Dentro de la zona central.
- 6 segmentos de 68×12, gap 4; número en slot de 48; fase `I/II`.
- Borde rojo en fase II, dorado en fase I.
- El texto instructivo largo va al canal de mensajes, no a la barra.
- Daño diferido con `vida_mostrada`/`vida_objetivo`; convergencia
  `1 - exp(-14 * dt)`, snap si la diferencia es <0.01.

### Mensajes

- Un solo canal `Rect(360,96,560,48)`; padding vertical 4, horizontal 8; icono
  16×16; texto en `x+32`; cuerpo 14, line-height 20, máximo 2 líneas.
- Prioridad: fase de jefe (3) > objeto (2) > checkpoint (1) > pista (0).
- Holds: jefe 3.2 s; objeto 3.5 s; checkpoint 4.0 s; pista 4.0 s.
- Entrada 150–200 ms (fade + slide 8 px); salida 120–150 ms (fade).
- Si llega menor o igual prioridad, se ignora; si es mayor, reemplaza. No encolar.
- Solo dibujar con `estado == "jugando"`; al pausar, congelar timers.
- Si no entra, elipsis; nunca cortar a mitad de palabra; partir palabras largas.

### Sistema visual

- Panel `(14,11,18,240)`, borde dorado, sombra exterior.
- Texto principal `HUD_TEXTO`; secundario `(170,158,146)`.
- Corazón vacío: relleno `(40,32,44)`, borde `(120,100,125)`.
- Fuente NotoSerifDisplay-Bold con ruta absoluta desde `Path(__file__)`.
- Escala 12 (labels), 14 (contadores/cuerpo), 18 (nivel/jefe); 22 solo overlays.
- Slots: HP 84, tiempo 112, nivel 100, nombre de nivel/jefe 300, fase 72,
  jefe 48. Celdas derechas 164×22; icono 16 + gap 6.
- Números en slots de ancho fijo, alineación derecha.
- Iconos con `pygame.draw`: corazón, rombo, cuenta, ala de dash, pala/guadaña,
  reloj, calavera. Corazón radio 7, pitch 28.
- Dorado = recurso; turquesa = dash listo; rojo = peligro; violeta = guadaña;
  verde = listo.
- Contraste: 4.5:1 para texto; 3:1 para gráficos.

### Feedback y animación

- La especificación completa está en §10 de `docs/PLAN_HUD_IN_CRYPTA.md`;
  respetala.
- Feedback inmediato 80–150 ms; cambios de estado 150–250 ms; mensajes 150–200 ms
  de entrada, 2.5–4 s de hold y 120–150 ms de salida.
- Entradas con ease-out; salidas con ease-in/ease-in-out; progreso/cooldown con
  linear; overshoot solo en pops (`1.12–1.15`), nunca en el layout.
- Alma: pop del contador y brillo de la cuenta; agrupar recogidas seguidas.
  Trigger: `almas > almas_prev`.
- Daño: flash del corazón afectado + escala breve; no sacudir todo el riel ni
  agregar pantalla completa. Trigger: `vidas < vidas_prev`.
- Vida baja: latido de 0.9–1.2 s; `1/5` en rojo; sin estroboscopio; solo en
  `estado == "jugando"`.
- Dash/pala listos: pulso único + `LISTO`; cargando: arco lineal + segundos.
  Trigger: cooldown cruza de >0 a <=0; no pulsar al aterrizar.
- Jefe: segmento con daño diferido de 150–250 ms; fase con borde y mensaje.
- Vida extra: toast + flash del rosario solo si `vidas` aumentó; con vidas al
  máximo no mostrar “VIDA EXTRA”.
- Mensaje: fade + slide máximo 8 px; interrumpible; prioridad jefe > objeto >
  checkpoint > pista; holds 3.2/3.5/4.0/4.0 s.
- Actualizá `efecto_hud` por frame o reemplazalo por un `Tween` con `dt`; no uses
  `time.time()`; usá `MAX_DT`, no un clamp nuevo de 0.05.
- Nada de flashes >3 Hz ni sacudidas nuevas de pantalla completa desde el HUD;
  el `flash`/`camara.sacudir` existentes no se tocan. Respetá
  `HUD_REDUCIR_MOVIMIENTO` si existe.

### Arquitectura

- Crear `hud.py` con `HudTheme`, `HudLayout`, `HudModel`, `HudRenderer`,
  `TextoCache`, `MensajeHUD` y `Tween`.
- `HudModel`: snapshot de solo lectura con `vidas`, `vidas_max`, `almas`,
  `almas_total`, `almas_para_vida`, `dash_cooldown`, `dash_usos_aire`,
  `en_suelo`, `ataque_cooldown`, `tiene_pala`, `rango_ataque_mejorado`, `jefe`,
  `jefe_vida`, `jefe_fase`, `tiempo`, `nivel_indice`, `estado`, `pista`,
  `aviso` y los `*_prev`.
- `Juego.dibujar_hud` solo arma el modelo y llama al renderer; no muta
  `efecto_hud` dentro del dibujo.
- `Juego.actualizar_hud(dt)` actualiza tweens/mensajes antes de dibujar.
- No cambiar la lógica del juego.
- Agregar `tests/test_hud.py` headless.

### Herramientas pygame

Leé §10 y §11.2 de `docs/PLAN_HUD_IN_CRYPTA.md`. Resumen operativo:

- Dibujar en `self.pantalla`, después de escalar el mundo; nunca en
  `superficie_mundo`.
- Paneles en `pygame.Surface(..., pygame.SRCALPHA)`, cacheados y con
  `convert_alpha()` después de `set_mode`.
- Primitivas: `pygame.draw.rect` con `border_radius`, `line`, `aaline`,
  `circle`, `polygon`, `arc`.
- Texto: `pygame.font.Font` + `render(..., True, color)`; medir con
  `font.size()`; cachear por `(texto, tamaño, color, sombra)`.
- Formatos exactos de §6.3: `3/5`, `12/42`, `7/10`, `LISTO`, `0.4s`, `01:23`,
  `3/6`, `[PALA] --`, `[GUADAÑA] LISTO`, `SIN USO`; alinear a la derecha.
- Wrap por píxeles con `font.size()`, no `textwrap` por caracteres; partir
  palabras largas y asegurar que la elipsis quepa.
- Glow con `BLEND_RGBA_ADD`; sombras con 2–3 rects semitransparentes.
- Animaciones con `dt` clampeado con `MAX_DT`, no `time.time()`; actualizar
  `efecto_hud` o reemplazarlo por un `Tween`.
- Pop: escalar solo la superficie del texto cacheada. Fade: copia + `set_alpha`;
  una copia por frame es aceptable. Cooldown: `pygame.draw.arc` lineal.
  Jefe: daño diferido con `vida_mostrada`.
- `pygame.Rect.colliderect` para tests de solapamiento; `DEBUG_HUD` para dibujar
  rects magenta.
- Evitar `Surface` por frame y `font.render` repetido; objetivo <1 ms de HUD.
- Errores a evitar: HUD en el mundo, `convert_alpha()` antes del display,
  `set_alpha()` sobre `SRCALPHA`, hardcodear 960×540, `self.jefe` sin guardia,
  `aviso_jefe > 0` con `jefe is None`, usar `HUD_MARGEN` (muerta) en vez de
  `HUD_MARGEN_X/Y`, y confundir `HUD_ALTO` con `HUD_ANGOSTO_ALTO`.

## Investigación que fundamenta el diseño

- gamedesign.gg — HUD design principles:
  `https://gamedesign.gg/articles/hud-design-principles`
- Goldsmiths — “Developing Effective UX Guidelines for HUD Design”:
  `https://research.gold.ac.uk/id/eprint/39439/1/1187.pdf`
- Caroux & Isbister — HUD and player experience:
  `https://www.sciencedirect.com/science/article/abs/pii/S1071581915001779`
- Game Accessibility Guidelines:
  `https://gameaccessibilityguidelines.com/`
- Hollow Knight UX/UI:
  `https://teemo.dev/game-design/hollow-knight/systems/ux-ui-and-accessibility`
- Celeste game overview:
  `https://teemo.dev/game-design/celeste/systems/game-overview`
- Three.js game UI patterns:
  `https://github.com/majidmanzarpour/threejs-game-skills/blob/main/skills/threejs-game-ui-designer/references/ui-patterns.md`
- NN/g — Executing UX Animations:
  `https://www.nngroup.com/articles/animation-duration/`
- Material Design — Duration & easing:
  `https://m1.material.io/motion/duration-easing.html`
- Returnal — UX design, gameplay-first UI:
  `https://blog.playstation.com/2021/05/11/unpacking-returnals-ux-design-gameplay-first-ui-retro-futuristic-tech-and-accessibility/`
- Slicker — Game Feel in Pygame:
  `https://slicker.me/python/game_feel_pygame.htm`
- Accessible Game Design — HUD Guidelines:
  `https://accessiblegamedesign.com/guidelines/HUD.html`
- Defold — HUD code sample:
  `https://defold.com/tutorials/hud/`
- Game Accessibility Guidelines — flicker:
  `https://gameaccessibilityguidelines.com/avoid-flickering-images-and-repetitive-patterns/`
- W3C WCAG 2.3.1 — Three Flashes:
  `https://www.w3.org/WAI/WCAG21/Understanding/three-flashes-or-below-threshold.html`
- Pygame — time, transform, surface, font, draw:
  `https://www.pygame.org/docs/ref/time.html`
  `https://www.pygame.org/docs/ref/transform.html`
  `https://www.pygame.org/docs/ref/surface.html`
  `https://www.pygame.org/docs/ref/font.html`
  `https://www.pygame.org/docs/ref/draw.html`

Ideas clave: HUD mínimo siempre visible, información contextual, agrupación,
safe areas, números estables, contraste, no depender solo del color, no tapar
la acción, feedback breve. Animación: 80–250 ms para feedback, entradas con
ease-out, salidas más rápidas, progreso lineal, sin flashes >3 Hz ni movimiento
de layout.

## Entregables

1. **Plan de diseño** con wireframes, medidas, contadores, animaciones y
   decisiones.
2. **Implementación** en `hud.py` (o en `juego.py` si se pide diff mínimo).
3. **Tests** `tests/test_hud.py` y `tests/test_logica.py` en verde.
4. **Capturas antes/después** de 6 estados:
   inicio con pista, nivel 1 con progreso, nivel 1 crítico, nivel 2 con pala,
   jefe fase 1, jefe fase 2 con aviso.
5. **Documentación** actualizada en `docs/PLAN_HUD_IN_CRYPTA.md`.

## Proceso

1. Leer `docs/PLAN_HUD_IN_CRYPTA.md`, `juego.py`, `config.py`, `entidades.py`,
   `efectos.py`, `nivel.py`, `niveles.py`, `tests/test_logica.py` y `README.md`.
2. Verificar rama, `git log -1`, `git status`; no tocar cambios ajenos.
3. Confirmar que existen las 6 capturas y
   `/tmp/opencode/hud/capturar_hud.py`; si no, recrearlos antes de tocar el HUD.
4. Mostrar el plan con rects exactos y esperar aprobación.
5. Implementar por fases:
   - Fase 1: layout, riel, zonas, 2×2 derecha, sin solapamientos, ancho fijo,
     contraste.
   - Fase 2: contadores numéricos, tiempo, barra de jefe.
   - Fase 3: canal de mensajes, wrap por píxeles, feedback, animaciones de §10,
     caché.
   - Fase 4: tests, capturas, documentación.
6. Después de cada fase: tests, captura y aviso corto en español.
7. No commitear salvo pedido explícito.

## Comandos de verificación

```bash
cd /home/sanodesu/unahur/PlataformeroMDA
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python tests/test_logica.py

# cuando exista:
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python tests/test_hud.py

# capturas (headless, 6 estados; el script escribe en /tmp/opencode/hud):
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python /tmp/opencode/hud/capturar_hud.py
```

## Criterios de aceptación

- 0 solapamientos en los 6 estados.
- Geometría exacta: riel `1232×72`; zonas `336/512/360`; celdas derechas
  `164×22`; mensaje `560×48`; barra de jefe `6×68×12`.
- Panel derecho de ancho fijo con/sin pala.
- Todos los contadores con número y unidad cuando corresponde; ningún cooldown
  en `0.0s`; el rosario no muestra `10/10`.
- Fase II se muestra con `3/6` o menos, nunca `4/6`.
- Pista máximo 2 líneas, sin cortar palabras y con elipsis que quepa.
- Corazones vacíos visibles; contraste verificable.
- Sin `font.render()` repetido por frame.
- Cada animación tiene trigger, propiedad, duración y curva; usa `dt`/`MAX_DT`,
  es interrumpible y no cambia el layout.
- Sin flashes >3 Hz ni sacudidas nuevas de pantalla completa desde el HUD; el
  `flash`/`camara.sacudir` existentes no se tocan. Existe
  `HUD_REDUCIR_MOVIMIENTO` o equivalente.
- Tests existentes y nuevos en verde, incluidos tweens, formatos, prioridades,
  estados de mensaje y casos borde.
- Nada fuera del HUD modificado.
- Capturas antes/después documentadas.

## Formato de respuesta

- Español rioplatense, corto y directo.
- Primero el plan; no implementes sin aprobación.
- Al terminar cada fase, decí qué cambió y qué se puede testear.
- Al final, entregá el resumen, las capturas y el estado de los tests.
````
