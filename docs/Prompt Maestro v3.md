# PROMPT MAESTRO UNIFICADO: REFACTORIZACIÓN INTEGRAL, CORRECCIÓN DE BUGS Y PARIDAD 1:1 PYGAME / GDEVELOP 5.6 PARA "IN CRYPTA"

> **Instrucción de Sistema:** Actuás como el **Lead Architect, Game Designer & Pipeline Engineer** en modo Goal Automático. Tu objetivo es corregir todos los bugs de Pygame, refactorizar la física de Salto + Dash (*Game Feel* tipo Celeste), unificar las 4 interfaces UI/UX, garantizar la curva de dificultad en sierra (Preludio + 3 Niveles) y reparar el exportador nativo a GDevelop 5.6 (`export/gdevelop_nativo/IN_CRYPTA_NATIVO.json`) para lograr paridad 1:1 absoluta.

---

## FASE 1: Corrección de Bugs y Refactorización del Núcleo en Pygame

### 1.1. Limpieza de Código y Mapeo de Controles (`entidades.py`, `juego.py`, `audio.py`)
1. **Controles WASD limpios:** En `Jugador.actualizar_horizontal()`, cambiar la detección a `izquierda = teclas[pygame.K_a] or teclas[pygame.K_LEFT]` y `derecha = teclas[pygame.K_d] or teclas[pygame.K_RIGHT]`. En `juego.py`, definir `TECLAS_ATAQUE = (pygame.K_j, pygame.K_z, pygame.K_k)` más Click Izquierdo del mouse para evitar que la tecla 'A' dispare ataques accidentales.
2. **Eliminar Duplicados y Código Muerto:** 
   - Eliminar la segunda definición duplicada de `actualizar_temporizadores` en `entidades.py`.
   - Eliminar de `juego.py` los métodos obsoletos `dibujar_hud_relicario_vidas`, `dibujar_hud_relicario_derecho` y `dibujar_barra_jefe` antiguos, canalizando el renderizado a través de `hud.py`.
   - En `juego.py` (`dibujar_ui_espacial`), corregir la verificación del atributo a `getattr(dp, "recogida", False)`.
3. **Corrección de Audio (`audio.py`):** Ajustar la generación de buffers procedurales para que utilicen la configuración real del mixer de Pygame (`pygame.mixer.get_init()`, $44100\text{ Hz}$, 16-bit, estéreo interleaved).

### 1.2. Refactorización de Física y Moveset ("Game Feel") (`config.py`, `entidades.py`)
1. **Apex Hang-Time (Flotación en el Ápice):** Cuando el jugador no está en el suelo (`not self.en_suelo`), mantiene la tecla de salto y $|v_y| < 95.0\text{ px/s}$, aplicar gravedad reducida al $55\%$ ($0.55 \times \text{GRAVEDAD}$).
2. **Post-Dash Float y Conservación de Momentum:** Al finalizar el Dash (`self.dash_tiempo == 0`), mantener el $100\%$ de la velocidad horizontal (`self.vx = self.dash_direccion * VELOCIDAD`) durante un temporizador `self.post_dash_tiempo = 0.06` segundos con gravedad reducida al $50\%$.
3. **Dash-Jump y Buffer en Suelo:** Permitir que si el jugador presiona Salto (`self.buffer_salto > 0`) durante un Dash en el suelo (`self.en_suelo` o `self.coyote > 0`), se cancele el dash e impulse un *Dash-Jump* (`self.vy = SALTO`, `self.vx = self.dash_direccion * VELOCIDAD * 1.18`).
4. **Encadenamiento por Pisotón (Stomp):** Pisar la cabeza de un enemigo con la pala equipada (`tiene_pala == True`) elimina al enemigo, hace rebotar al jugador (`vy = -REBOTE_ENEMIGO`, $360\text{ px/s}$) y recarga instantáneamente el Dash aéreo (`dash_usos_aire = 1` y `dash_cooldown = 0.0`).

---

## FASE 2: Progresión de Niveles, Curva en Sierra y UI/UX

### 2.1. Rediseño de Niveles y Curva de Dificultad (`niveles.py`, `nivel.py`)
1. **Preludio / Tutorial:** Cero muerte instantánea. Fosos de práctica con trinchera segura abajo para intentar saltos y dash.
2. **Nivel 1 (El Camposanto):** Se otorga el `DashPowerUp` ('D'). Los saltos puros miden $3\text{ a }4\text{ tiles}$ y los de Dash $6\text{ a }7\text{ tiles}$. No hay arma 'W'.
3. **Nivel 2 (La Cripta):** Se recoge el Arma ('W'). Se introducen plataformas móviles ('M', 'V') y pisotones sobre enemigos como trampolines para cruzar fosos de $10\text{ a }12\text{ tiles}$.
4. **Nivel 3 (El Osario):** Incluye al Mini-Boss ('K' - El Carcelero), el Power-Up de alcance de Guadaña ('X') y el Boss Final ('B' - El Custodio) con 2 fases (Fase 2 solo vulnerable con el Power-Up 'X').
5. **Salas de Prueba (`niveles_rediseñados.py`):** Limpiar para que contengan 3 salas independientes hechas a mano, con exactamente 1 spawn 'P' y 1 portón 'G'.

### 2.2. Implementación de las 4 Interfaces UI/UX (`hud.py`, `entidades.py`, `juego.py`)
1. **No Diegética (Riel HUD Fijo):** Panel superior de $1232\times72\text{ px}$ sin *layout shifts*. Grilla $2\times2$ en el panel derecho (`[ALMA]`, `[DASH]`, `VIDA EXTRA`, `[ARMA]`).
2. **Diegética (Farol del Sepulturero):** Llama con núcleo turquesa cuando el Dash está listo; halo violeta al obtener la Guadaña ('X'). Faroles de checkpoint ('F') que se encienden al activarlos.
3. **Espacial (Carteles de Control):** Texto flotante en coordenadas de mundo sobre altares ('D', 'W', 'X') que desaparece tras recoger el ítem.
4. **Meta (Viñeta Carmesí):** Borde perimetral pulsante cuando al jugador le queda 1 sola vida.

---

## FASE 3: Exportador Nativo a GDevelop 5.6 y Paridad 1:1

### 3.1. Sincronización de Paridad y Eventos Nativo (`tools/generar_proyecto_nativo.py`, `tools/exportador/*`)
1. **Cámara y Viewport:** Fijar `GAME_ZOOM = 1.25` para la capa base y `1.0` para la capa UI, garantizando la visión exacta de $1024\times576$ unidades virtuales.
2. **Hitbox Exacta:** En `tools/integrar_assets_gdevelop.py`, inyectar `hasCustomCollisionMask: True` en el objeto `Jugador` con un polígono de $24\times30\text{ px}$ centrado en el sprite de $32\times32\text{ px}$.
3. **Física de Salto y Dash en GDevelop:**
   - Configurar `jumpSustainTime: 0` y simular el corte de salto mediante `PlatformBehavior::PlatformerObjectBehavior::AbortJump` al soltar la tecla.
   - Al finalizar el Dash (`dash_time <= 0`), establecer `SetCurrentSpeed = Jugador.Variable(dir) * 250` para conservar la velocidad en lugar de frenar a 0.
   - En los pisotones, establecer `JumpSpeed = 360` antes de simular el salto para igualar `REBOTE_ENEMIGO`.
4. **Checkpoints Funcionales:** Al perder una vida con `vidas > 0` y `checkpoint_activo == 1`, mover al `Jugador` a `(checkpoint_x, checkpoint_y)` e impartir $1.2\text{ s}$ de invulnerabilidad sin recargar la escena.
5. **Animaciones Multipose:** Enlazar en las hojas de eventos los índices de animación de GDevelop para `Run` (al moverse en piso), `Jump` (al ascender), `Caida` (al descender), `Dash` (al hacer dash) y `Ataque`.

---

## FASE 4: Barrera de Calidad y Comandos de Certificación

Ejecutar la siguiente secuencia de comandos y asegurar que todos devuelvan 0 errores:

```bash
# 1. Exportar proyecto nativo y assets Pixel-Art
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/exportar_todo.py

# 2. Validar hojas de eventos contra la API WebAssembly de GDevelop 5.6
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/validar_eventos_gd.py

# 3. Verificar paridad física y geométrica
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/verificar_paridad.py

# 4. Ejecutar suite de pruebas de lógica y físicas de Pygame
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_logica.py

# 5. Ejecutar suite de pruebas de HUD e Interfaces UI/UX
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_hud.py