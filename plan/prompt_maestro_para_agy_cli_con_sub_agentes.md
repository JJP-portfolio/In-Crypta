# PROMPT DE EJECUCIÓN AUTÓNOMA (`/goal`) PARA `agy-cli` — RENOVACIÓN SENSORIAL DE *IN CRYPTA*

> **Instrucciones de Uso:** Podés pasarle este archivo directamente a `agy-cli` junto con `argon_overhaul_context.xml` (por ejemplo: `agy-cli /goal -f prompt_ejecucion_agy_cli.md -c argon_overhaul_context.xml`). El prompt está optimizado para **Gemini Flash** y diseñado para orquestar **sub-agentes en paralelo/secuencia** con validación estricta por tests.

---

## ROL Y MISIÓN DEL AGENTE ORQUESTADOR

Actúa como **Argon**, Director Técnico de Arte, Ingeniero de Rendimiento en Pygame y Experto en *Game Feel*. Tu misión es ejecutar la **Renovación Sensorial Integral de *IN CRYPTA*** leyendo las especificaciones de `argon_overhaul_context.xml` y aplicándolas sobre el código fuente del repositorio.

**DEBES utilizar sub-agentes especializados** para dividir el trabajo por dominio (Audio, Mundo/Fondos, Entidades/Efectos, HUD y QA/Integración), asegurando que cada cambio mantenga la estética casera/indie (*homebrew* de 8-bits NES, 16-bits SNES y Procedural Gótico) y garantice **60 FPS clavados en una laptop Sony Vaio de bajos recursos** cuando se juega en **Calidad Baja**.

---

## 1. REGLAS DURAS E INQUEBRANTABLES (GUARDRAILS)

Todo sub-agente bajo tu mando tiene **TERMINANTEMENTE PROHIBIDO**:
1. **NO TOCAR FÍSICAS:** No modifiques ninguna constante física ni de balanceo en `config.py` (`GRAVEDAD`, `SALTO`, `VELOCIDAD`, `MAX_CAIDA`, `COYOTE_TIME`, `JUMP_BUFFER`, `CORTE_SALTO`, `INVULNERABILIDAD`, `REBOTE_ENEMIGO`, `DASH_VELOCIDAD`, `DASH_DURACION`, `DASH_COOLDOWN`, `ATAQUE_DURACION`, `ATAQUE_COOLDOWN`, `ATAQUE_ALCANCE`, `ATAQUE_ALCANCE_MEJORADO`, `TOLERANCIA_PISOTON`).
2. **NO TOCAR RECTÁNGULOS NI LÓGICA DE COLISIÓN:** No cambies el tamaño ni el cálculo de `self.rect` ni `rect_ataque()` en ninguna clase de `entidades.py` ni `nivel.py`.
3. **NO TOCAR EL DISEÑO DE NIVELES:** No modifiques las cadenas ASCII en `niveles.py` ni el parseo de símbolos en `nivel.py`.
4. **NO AGREGAR DEPENDENCIAS EXTERNAS:** Solo librería estándar de Python + `pygame` (100% compatible con Pygbag / WebAssembly).
5. **SUITE DE TESTS INTACTA:** Antes de terminar, `pytest tests/` debe arrojar **51 passed** (100% verde) y `HudLayout.construir().solapamientos()` debe seguir devolviendo `[]`.

---

## 2. ARQUITECTURA DE DELEGACIÓN EN SUB-AGENTES

Como Agente Orquestador, ejecuta el siguiente flujo de trabajo paso a paso delegando en **5 Sub-Agentes**:

### PASO 0 — Preparación de Rama y Línea Base (Orquestador)
1. Verifica el estado del repositorio con `git status`.
2. Crea y cambia a la nueva rama de la feature con:
   ```bash
   git checkout -b art/overhaul-sensorial
   ```
3. Ejecuta `pytest tests/` para confirmar que la línea base está en verde antes de delegar.
4. Actualiza `config.py` añadiendo las constantes globales del bloque `<file path="config.py">` de `argon_overhaul_context.xml`:
   - Selectores de estilo: `ESTILO_HUD = "AUTO"`, `ESTILO_MUNDO = "AUTO"`, `ESTILO_ENEMIGOS = "AUTO"`, `ESTILO_EFECTOS = "AUTO"`, `CALIDAD_GLOBAL_ACTIVA`.
   - Paleta calibrada por luminancia ($Y = 0.299R + 0.587G + 0.114B$): `BG_NOCHE_PROFUNDA`, `BG_PIEDRA_NIEBLA`, `BG_SILUETA_FRIA`, `TILE_CUERPO_SOMBRA`, `TILE_MAMPOSTERIA`, `TILE_BISEL_LUZ`, `TILE_SOMBRA_CORTE`, `ENEMIGO_MORTAJA`, `ENEMIGO_PURPURA`, `ENEMIGO_RIM_LUZ`, `ENEMIGO_OJO_FUEGO`, `MELEE_ACERO_CLARO`, `FX_IMPACTO_BLANCO`.
   - Función `resolver_estilo(preferencia: str, calidad_idx: int = None) -> str` que mapea `"AUTO"` según la calidad activa:
     - `0` (Alta) $\rightarrow$ `"PROC"` (Procedural Gótico completo).
     - `1` (Media) $\rightarrow$ `"SNES"` (16-Bit biselado).
     - `2` (Baja / Modo Vaio) $\rightarrow$ `"NES"` (8-Bit ortogonal ultra ligero, cero transparencias pesadas).

---

### SUB-AGENTE 1 — Especialista en Audio y Orquestación Musical (`audio.py` y `juego.py`)
**Objetivo:** Reparar la desconexión de las 10 pistas `.ogg` en `assets_in_crypta/entrega/musica/` y equilibrar la mezcla sonora.
1. En `audio.py`:
   - Añade `self.musica_actual = None` en `Audio.__init__`.
   - En `Audio._construir_banco`, reduce el volumen de síntesis de `dron_catacumbas` de `0.08` a `0.045` para que actúe como cama atmosférica sin tapar la música.
   - En `Audio.reproducir_musica(id_musica, bucle=True, fade_ms=800)`, verifica si `self.musica_actual == id_musica and pygame.mixer.music.get_busy()`: si es así, retorna sin reiniciar la pista. Fija `pygame.mixer.music.set_volume(0.45)` antes de `play()` y guarda `self.musica_actual = id_musica`.
   - En `Audio.detener_musica(fade_ms=800)`, limpia `self.musica_actual = None`.
2. En `juego.py`:
   - En `Juego.__init__` (al arrancar en estado `"titulo"`) y en `abrir_menu()`: invoca `self.audio.reproducir_musica("titulo", bucle=True, fade_ms=600)`.
   - En `cargar_nivel()`: invoca `self.audio.reproducir_musica(self.nivel.tema, bucle=True, fade_ms=800)` (mapea automáticamente `"camposanto"`, `"cripta"`, `"osario"`).
   - En `iniciar_tutorial()`: invoca `self.audio.reproducir_musica("camposanto", bucle=True, fade_ms=800)`.
   - En `actualizar_minijefes()`: cuando un `MiniJefe` vivo esté a menos de `450px` del jugador (o en estado de combate), reproduce `"carcelero"`. Al morir (`_comprobar_muerte_minijefe`), vuelve a reproducir `self.nivel.tema`.
   - En `actualizar_jefe()`: al activar el checkpoint de la antesala del Custodio, reproduce `"custodio_f1"`. Cuando `self.jefe.estado == "cambio"` (paso a Fase 2), cambia a `"custodio_f2"` con `fade_ms=400`.
   - Al pasar a `"victoria"`, reproduce `"victoria"` (`bucle=False, fade_ms=500`). Al pasar a `"derrota"` en `perder_vida()`, reproduce `"derrota"` (`bucle=False, fade_ms=400`). En `abrir_creditos()`, reproduce `"creditos"` (`bucle=True, fade_ms=600`).

---

### SUB-AGENTE 2 — Especialista en Entidades, Contraste y Feedback de Combate (`entidades.py` y `particulas.py`)
**Objetivo:** Erradicar la mimetización de los enemigos contra el fondo ($\Delta Y > 150$), implementar los 3 modelos visuales (`C1 NES`, `C2 SNES`, `C3 PROC`), alinear el arco de ataque al hitbox real y añadir *Hit-Sparks* y *Damage Flash*.
1. En `particulas.py`:
   - Crea la clase `HitSpark(x, y, direccion=1, mejorado=False)` con duración `0.07s` que consulta `config.resolver_estilo(config.ESTILO_EFECTOS)`:
     - En `"NES"` (Modelo D1): dibuja una cruz ortogonal blanca de 2px con centro cuadrado en `ORO_LITURGICO` o violeta `(215, 80, 255)`.
     - En `"SNES"` / `"PROC"` (Modelos D2/D3): dibuja una estrella gótica de 4 puntas afiladas con núcleo blanco puro.
   - Añade `self.sparks = []` y el método `hit_spark(x, y, direccion=1, mejorado=False)` en `SistemaParticulas`, actualizándolos y dibujándolos en `actualizar()` y `dibujar()`.
2. En `entidades.py`:
   - Añade `self.tiempo_flash = 0.0` en `__init__` y `reiniciar()`, y su decaimiento `if self.tiempo_flash > 0: self.tiempo_flash = max(0.0, self.tiempo_flash - dt)` en `actualizar()` para `Enemigo`, `EnemigoMelee`, `Cuervo`, `Polilla` y `Araña`.
   - En `dibujar()` de `Enemigo` y `EnemigoMelee`:
     - Si `self.tiempo_flash > 0`: dibuja la silueta del enemigo íntegramente en `FX_IMPACTO_BLANCO = (250, 248, 240)` y retorna (efecto *Damage Flash* de costo cero en CPU).
     - Consulta `estilo = config.resolver_estilo(config.ESTILO_ENEMIGOS)`:
       - **Modelo C1 (`"NES"`):** Dibuja primero una silueta exterior expandida `+2px` en `ENEMIGO_RIM_LUZ = (225, 228, 240)`, encima el cuerpo en azul noche `(24, 32, 54)`, cráneo marfil y ojos en `ENEMIGO_OJO_FUEGO = (255, 52, 68)` con destello horizontal de 1px.
       - **Modelo C2 (`"SNES"`):** Cambia el cuerpo de verde musgo a `ENEMIGO_MORTAJA = (36, 48, 72)` (o `ENEMIGO_PURPURA = (52, 28, 64)` en `EnemigoMelee`), añade un arco superior de **Rim Light** de 2px en `ENEMIGO_RIM_LUZ`, costillas con 1px de sombra negra debajo y hoja de mandoble en `MELEE_ACERO_CLARO = (165, 178, 198)` con filo blanco.
       - **Modelo C3 (`"PROC"`):** Añade Rim Light en `TURQUESA_ANIMA`, expone la caja torácica ósea en `HUESO_MARFIL` con un núcleo de fuego fatuo pulsante entre las costillas y ojos con punto focal blanco y halo carmesí.
   - En `Cuervo`, `Polilla` y `Araña`: agrega un borde superior de 1-2px en `ENEMIGO_RIM_LUZ` o `TURQUESA_ANIMA` en alas y patas para despegarlos de los techos oscuros.
   - En `Jugador.dibujar()`: ajusta el dibujo del arco de ataque cuando `atacando == True` para que cubra visualmente la caja exacta de `self.rect_ataque()` (`34x26 px` con pala normal, `76x42 px` con guadaña).

---

### SUB-AGENTE 3 — Especialista en Entornos, Tiles y Perspectiva Atmosférica (`nivel.py` y `juego.py`)
**Objetivo:** Aplicar la separación de 3 planos de James Gurney (Fondo atenuado vs Terreno con *Walkable Edge Cue*) y los 3 modelos de tiles (`B1 NES`, `B2 SNES`, `B3 PROC`).
1. En `juego.py` (`crear_fondo`, `dibujar_fondo_camposanto`, `dibujar_fondo_cripta`, `dibujar_fondo_osario`):
   - Reduce el contraste y brillo de las colinas, árboles, columnas y arcos de fondo en un 30% usando tonos fríos desaturados (`BG_NOCHE_PROFUNDA`, `BG_PIEDRA_NIEBLA`, `BG_SILUETA_FRIA`) para que nunca compitan con las plataformas reales.
2. En `nivel.py` (`dibujar_solidos` y `dibujar_plataformas`):
   - Consulta `estilo = config.resolver_estilo(config.ESTILO_MUNDO)`.
   - Define el color de bisel superior de alta luminancia ($Y > 175$) por bioma: `(165, 185, 160)` en `camposanto`, `(180, 198, 222)` en `cripta`, y `(218, 208, 186)` en `osario`.
   - Implementa los 3 modelos en `dibujar_solidos`:
     - **Modelo B1 (`"NES"` — Optimizado para Vaio):** Relleno plano sin bucles internos pesados, divisiones verticales cada `TILE` (`32px`), y en todo bloque con `not tiene_arriba` dibuja una **losa superior caminable de 3px** en `c_bisel_top` seguida de una **línea negra de corte de 2px** `(10, 8, 14)`.
     - **Modelo B2 (`"SNES"`):** Sillería estratificada con ladrillos alternados por fila (`(TILE // 2) if fila % 2 == 1 else 0`) con bisel superior/izquierdo iluminado y corona caminable de 5px con corte negro inferior de 2px.
     - **Modelo B3 (`"PROC"`):** Mantiene las raíces, salitre y nichos de calaveras por bioma, pero añade obligatoriamente la corona caminable de alto contraste (`c_bisel_top` de 2px + corte negro de 2px debajo) en todo borde superior pisable.
   - En `LosaQuebradiza.dibujar()` (`entidades.py`): añade grietas diagonales visibles en reposo en tono ámbar/turquesa y base hueca dentada para distinguirla al instante de un bloque `#` normal.

---

### SUB-AGENTE 4 — Especialista en HUD y Relicarios (`hud.py`)
**Objetivo:** Implementar los Modelos `A1 (NES)`, `A2 (SNES)` y `A3 (PROC)` en `HudRenderer` y conectar los eventos del `HudModel` a animaciones `Tween`.
1. En `HudRenderer.__init__` (`hud.py`):
   - Instancia `self.tween_alma = Tween(0.25, 0.25, "out_back")`, `self.tween_dash = Tween(0.30, 0.30, "out_back")`, `self.tween_arma = Tween(0.25, 0.25, "out_back")` y `self.tween_jefe = Tween(0.22, 0.22, "out_cubic")`.
2. En `HudRenderer._panel(ancho, alto, alpha=None)`:
   - Incluir `estilo = config.resolver_estilo(config.ESTILO_HUD)` en la clave de `self._paneles_cache`.
   - **Modelo A1 (`"NES"`):** Superficie 100% opaca (`pygame.Surface((ancho, alto)).convert()`), fondo `(9, 8, 13)`, doble filete rectangular de 1px con esquinas escalonadas (*pixel-chamfer* de 4px) en `HUD_ORO`. Cero costo de alpha-blending para la Vaio.
   - **Modelo A2 (`"SNES"`):** Marco biselado 3D (luz superior/izquierda `(238, 202, 118)`, sombra inferior/derecha `(72, 52, 28)`) con 4 remaches metálicos en las esquinas.
   - **Modelo A3 (`"PROC"`):** Marco gótico con doble filete interno y agujas/filigrana dorada en los 4 vértices.
3. En `HudRenderer.dibujar_corazon(pantalla, cx, cy, lleno, escala=1.0)`:
   - Soporta `"NES"` (corazón pixel-art escalonado mediante rectángulos ortogonales), `"SNES"` (gema octogonal facetada con engarce de oro) y `"PROC"` (Corazón Delator con engarce de espina superior).
4. En `HudRenderer._dibujar_centro` y `_dibujar_derecha`:
   - Si `modelo.jefe_vivo` y (`modelo.jefe_fase >= 2` o `self.tween_jefe.esta_activo()`), aplica un temblor vertical sutil ($\pm 2\text{ px}$ si `not reducir_movimiento`) en los segmentos de la barra del jefe y separadores óseos entre cada segmento.
   - Cuando `self.tween_dash.esta_activo()`, dibuja un destello turquesa/blanco alrededor del medallón de `[DASH] LISTO`.

---

### SUB-AGENTE 5 — Integrador de QA, Debug `F3`, Selector `F4` y Optimización Vaio (`juego.py`)
**Objetivo:** Integrar el impacto de combate (`hit_spark` + `tiempo_flash`), añadir las herramientas de inspección en vivo (`F3` y `F4`) y verificar los 51 tests.
1. En `juego.py`:
   - En `actualizar_ataque()`, cada vez que `golpe.colliderect(...)` impacta contra un enemigo, minijefe o jefe:
     - Activa `entidad.tiempo_flash = 0.06`.
     - Calcula `inter = golpe.clip(entidad.rect)` e invoca `self.particulas.hit_spark(inter.centerx, inter.centery, self.jugador.direccion, self.jugador.rango_ataque_mejorado)`.
   - En `alternar_calidad_grafica()`: actualiza `config.CALIDAD_GLOBAL_ACTIVA = self.config_calidad_idx` y limpia `self.hud.renderer._paneles_cache.clear()`.
   - En `procesar_eventos()` (`KEYDOWN`):
     - **Tecla `F3`:** Alterna `self.debug_colisiones = not self.debug_colisiones` y muestra mensaje en el HUD `"DEBUG HITBOX/HURTBOX (F3): ACTIVADO/DESACTIVADO"`.
     - **Tecla `F4`:** Cicla entre `("AUTO", "NES", "SNES", "PROC")`, asigna ese valor a `config.ESTILO_HUD`, `config.ESTILO_MUNDO`, `config.ESTILO_ENEMIGOS` y `config.ESTILO_EFECTOS`, limpia `self.hud.renderer._paneles_cache.clear()` y muestra en el HUD `"MODELO VISUAL (F4): <MODO>"`.
   - Añade el método `dibujar_debug_colisiones(self, destino, camara)` e invócalo en `Juego.dibujar()` sobre `self.superficie_mundo` cuando `self.debug_colisiones` sea `True`:
     - Hurtbox de `jugador.rect`: verde `(40, 255, 120)`.
     - Hurtboxes de enemigos/jefes/ondas vivos: naranja `(255, 165, 30)`.
     - Hitbox activo `jugador.rect_ataque()` (cuando `ataque_tiempo > 0`): rojo `(255, 40, 60)` de 2px con diagonales en cruz.
     - Peligros `nivel.peligros`: violeta `(200, 80, 255)`.
2. **Verificación Final Obligatoria:**
   - Ejecuta `pytest tests/` y verifica que **los 51 tests pasen sin errores**.
   - Ejecuta un test rápido en modo headless (`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -c "import juego; j = juego.Juego(); j.actualizar(0.016); j.dibujar()"`) probando los 4 modos de `F4` (`AUTO`, `NES`, `SNES`, `PROC`) y las 3 calidades (`0`, `1`, `2`) para garantizar cero excepciones en tiempo de ejecución.
   - Deja los cambios listos en la rama `art/overhaul-sensorial` y presenta un resumen de los archivos modificados.