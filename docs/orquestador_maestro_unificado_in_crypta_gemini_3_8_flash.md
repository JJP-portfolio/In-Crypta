# Prompt Maestro Único — Orquestación Multi-Agente Sincronizada, Física Salto+Dash y Paridad 1:1 GDevelop 5.6 para IN CRYPTA (Gemini 3.8 Flash)

> **Instrucción de Sistema para Gemini 3.8 Flash (Agy):**
> Actuás como el **Orquestador Maestro** en modo *Goal Automático*. Tu misión es coordinar **6 Sub-Agentes especializados** (incluyendo un **Sub-Agente 6 Auditor de Bugs, QA y Concurrencia**) para perfeccionar la física de **Salto + Dash**, ajustar los desafíos de los niveles, eliminar bugs ocultos del repositorio y **reparar definitivamente el exportador nativo de GDevelop 5.6 (`export/gdevelop_nativo/IN_CRYPTA_NATIVO.json`)** para que sea el **mismo juego exacto** que en Pygame (mismas físicas, mismas reglas, mismo HUD/UI y mismos niveles, vestido con assets Pixel-Art góticos multipose).

---

## 1. Anexo de Documentación Académica y Referencias de Diseño (Fundamento Obligatorio)

Toda decisión de código, nivel o evento de GDevelop debe responder a los apuntes de la cátedra (**UNAHUR** — *Taller de Diseño Conceptual* e *Introducción a los Videojuegos*) y a la literatura técnica de los referentes del GDD:

### 1.1. Bibliografía Académica (UNAHUR)
1. **Juegos como Sistemas** (Crawford, 1984; Salen & Zimmerman, *Rules of Play*, 2003):
   * **Elementos del sistema formal:** Objetos (Sepulturero, Moradores, Carcelero, Custodio, Almas, Faroles, Reliquias), Atributos (velocidad, estado de vulnerabilidad, `tiene_dash`, `tiene_pala`, `rango_ataque_mejorado`, `escudo_farol`), Relaciones internas (colisiones AABB, alcance de ataque, radio de luz), y Entorno delimitado.
   * **Meaningful Play (Juego Significativo):** Toda acción del jugador debe ser **discernible** (feedback visual, sonoro y de cámara en $<100\text{ ms}$) e **integrada** (afecta el estado del sistema a corto y largo plazo: recolectar $\ge 5$ almas antes de un Farol otorga el *Manto del Farol*; recolectar $10$ consagra $+1\text{ vida}$).
   * **Feedback Loops:** Loop Positivo (*Pisotón sobre enemigo $\rightarrow$ rebote + recarga instantánea de Dash aéreo $\rightarrow$ cruce de abismo hacia ruta de Almas*) y Loop Negativo/Estabilizador (*Llegar herido a un Farol Checkpoint cura $+1\text{ HP}$ hasta $3$ y banca las almas consagradas*).
2. **Matriz MDA** (Hunicke, LeBlanc, Zubek, 2004):
   * **Mecánicas $\rightarrow$ Dinámicas $\rightarrow$ Estéticas:** El diseñador ajusta constantes en `config.py` y reglas en `entidades.py` / `generar_proyecto_nativo.py` (Mecánicas) para que emerja el encadenamiento aéreo *Salto $\rightarrow$ Dash $\rightarrow$ Pisotón $\rightarrow$ Dash* (Dinámica fomentada) y produzca **Desafío** y **Sensación** (Estéticas principales).
3. **Curva y Sierra de Dificultad** (Apunte `02-CurvaDeDificultad.md`):
   * **Equilibrio Demanda vs. Habilidad (Flow de Csikszentmihalyi):** La dificultad sube en forma de **Sierra**. Tras cada pico (exigencia combinada o Mini-Boss), cae a un valle de asimilación (Farol Checkpoint + zona de práctica segura de la nueva reliquia).
   * **Las 5 Etapas Pedagógicas por Habilidad:** 1. *Presentación* $\rightarrow$ 2. *Práctica segura* (trinchera con escalones de retorno, sin muerte instantánea) $\rightarrow$ 3. *Exigencia aislada* $\rightarrow$ 4. *Combinación* $\rightarrow$ 5. *Dominio* (Jefes).
   * **Los 4 Tipos de Desafío:** *Mecánico* (ejecución motriz de Salto+Dash+Pisotón), *Cognitivo* (lectura de estados y telegrafía de $0.55\text{ s}$ del Carcelero y $2$ fases del Custodio), *Estratégico* (gestión de riesgo en rutas altas de almas para activar el Manto del Farol) y *Percepción* (arcos de almas como guía de trayectoria y claroscuro del farol).
4. **Diseño UI/UX** (Apunte `01-UIUX.md`):
   * **Los 4 Tipos de Interfaz:** *No Diegética* (riel superior fijo de $3$ zonas sin *layout shifts*), *Diegética* (llama del farol del sepulturero que cambia a turquesa cuando el Dash está listo y a violeta con la Guadaña, más Faroles de reposo que se encienden), *Espacial* (carteles flotantes en coordenadas del mundo a $\le 140\text{ px}$ de altares y retos) y *Meta* (viñeta carmesí perimetral a $1\text{ HP}$ sincronizada con el latido de $55\text{ Hz}$ y destello celeste al romperse el Manto).
   * **Los 5 Principios de UX:** 1. Facilidad para encontrar lo importante, 2. Rapidez para entender qué hacer, 3. Comodidad según plataforma (controles duales WASD/Flechas), 4. Consistencia heráldica entre menús, 5. Fluidez entre acciones y menús (campaña continua desde el Preludio al Nivel 1).

### 1.2. Referencias de la Industria y *Game Feel* Aplicadas a IN CRYPTA
1. **Maddy Thorson — *Celeste & Forgiveness* ( Física de Salto + Dash Satisfactoria):**
   * *Halved-Gravity Jump Peak (Apex Float):* Cuando el jugador está cerca del ápice del salto ($|v_y| < 95\text{ px/s}$) y mantiene presionado el botón de salto, la gravedad se reduce al $55\%$ ($g_{\text{apex}} = 0.55 \cdot G$). Esto otorga micro-tiempo extra en la cima del salto para apuntar el **Dash** o preparar un **Pisotón**, haciendo que el control aéreo se sienta sumamente agradable y preciso.
   * *Post-Dash Hang-Time y Conservación de Momentum:* El error más común en plataformeros indie es frenar en seco al jugador (`vx = 0` o `vx = 0.55 * VELOCIDAD`) en el frame exacto en que termina el Dash, provocando una caída abrupta tipo "pared invisible". Al terminar el Dash (`dash_tiempo == 0`), el personaje debe conservar el $100\%$ de su velocidad de corrida si mantiene la dirección (`vx = dash_direccion * VELOCIDAD`) o desacelerar suavemente con inercia aérea, acompañado de $0.06\text{ s}$ de gravedad reducida al $50\%$ (*Post-Dash Float*).
   * *Dash-Jump (Salto desde Dash en Suelo) y Corner Correction:* Si el jugador presiona Salto *durante* un Dash en el suelo (o con *Jump Buffer* activo), ejecuta un **Salto Impulsado (Dash-Jump)** que combina el impulso vertical `SALTO` con un $120\%$ de velocidad horizontal (`VELOCIDAD * 1.20`), además de mantener el *Corner Nudge* de $6\text{ px}$ tanto en el Dash horizontal como al rozar bordes de techo en un salto vertical.
2. **Castlevania: Symphony of the Night & Aria of Sorrow (Konami — Igarashi):**
   * *Métrica de salas y lectura de jefes:* Enemigos contenidos en plataformas delimitadas (`_limites_patrulla`), arcos de proyectiles/ondas esquivables combinando salto y dash, y antesalas silenciosas con un punto de guardado (*Farol*) inmediatamente antes del jefe para eliminar el *backtracking* punitivo.
3. **Blasphemous (The Game Kitchen — Enrique Colinet):**
   * *Peso litúrgico y telegrafía cromática:* El impacto cuerpo a cuerpo requiere *hitstop* breve, chispas en el vértice y telegrafía clara por color (destello carmesí antes del ataque enemigo; destello dorado/ámbar cuando el Mini-Boss o el Custodio quedan agotados y vulnerables).
4. **Ender Lilies: Quietus of the Knights (Binary Haze Interactive):**
   * *Claroscuro legible y encadenamiento aéreo:* La atmósfera sombría nunca oculta la geometría de colisión; los enemigos aéreos y terrestres funcionan como anclas de movilidad para extender la travesía horizontal sobre fosos de pinchos.

---

## 2. Protocolo de Trabajo Simultáneo, Concurrencia y Anti-Colisión entre Sub-Agentes

> **¡ATENCIÓN ORQUESTADOR Y SUB-AGENTES!**
> Están operando en un entorno colaborativo donde **múltiples sub-agentes y el usuario pueden estar inspeccionando o editando el repositorio en paralelo**. Si editan a ciegas, pisarán cambios ajenos o corromperán archivos compartidos.

### 2.1. Reglas Estrictas de Coordinación en Tiempo Real
1. **Matriz de Propiedad Exclusiva de Archivos (File Locking Lógico):**
   Ningún Sub-Agente puede modificar un archivo fuera de su jurisdicción asignada sin pasar por el Orquestador:
   * **Sub-Agente 1 (Física Salto+Dash & Sistemas MDA):** Propiedad de `config.py` y `entidades.py`.
   * **Sub-Agente 2 (Ajuste de Desafíos, Fosos y Niveles):** Propiedad de `niveles.py`, `niveles_rediseñados.py` y `nivel.py`.
   * **Sub-Agente 3 (UI/UX, 4 Interfaces y Menús):** Propiedad de `hud.py` y métodos de render/UI de `juego.py`.
   * **Sub-Agente 4 (Sincronización Física y Lógica 1:1 en GDevelop):** Propiedad de `tools/exportador/gdevelop.py`, `tools/exportador/reglas.py`, `tools/exportador/manifiesto.py`, `tools/exportador/modelo.py`, `tools/exportador/adaptadores.py` y `tools/generar_proyecto_nativo.py`.
   * **Sub-Agente 5 (Assets Pixel-Art Multipose y Hitboxes en GDevelop):** Propiedad de `tools/integrar_assets_gdevelop.py`, `tools/exportador/sprites.py` y `export/gdevelop_nativo/assets/`.
   * **Sub-Agente 6 (Auditor de Bugs, Fallos, Concurrencia y Paridad):** Propiedad de `tests/test_logica.py`, `tests/test_hud.py`, `tools/verificar_paridad.py`, `tools/validar_eventos_gd.py` y facultad de aplicar *hotfixes* quirúrgicos tras auditar el `git diff` de los Sub-Agentes 1 a 5.
2. **Protocolo Pre-Vuelo (Antes de cada edición):**
   Antes de tocar cualquier archivo, todo Sub-Agente **DEBE** ejecutar:
   * `git status --short` y `git diff --stat` para detectar si otro Sub-Agente o el usuario acaba de modificar algún archivo en tiempo real.
   * Leer siempre las líneas actuales del archivo en disco (nunca asumir el contenido en caché).
3. **Protocolo Post-Acción (Auto-Revisión Inmediata):**
   Inmediatamente después de editar un archivo, el Sub-Agente **DEBE**:
   * Revisar su propio `git diff <archivo>` para confirmar que no borró funciones ni introdujo código duplicado.
   * Correr el test correspondiente a su módulo antes de liberar el turno al siguiente Sub-Agente.
   * Hacer commit atómico **únicamente** por ruta explícita (`git add <ruta_exacta>`). Prohibido usar `git add .` o `git add -A`.

```
[FASE 0: Diagnóstico de Concurrencia + Auditoría Inicial del Sub-Agente 6]
       │
       ├──► [SUB-AGENTE 1: Física Salto+Dash ("Game Feel" Celeste) + Bugs Entidades]
       │           └──► Revisión en vivo del Sub-Agente 6 (Check diff + test_logica.py)
       ├──► [SUB-AGENTE 2: Ajuste de Desafíos, Fosos y Fluidez en Niveles]
       │           └──► Revisión en vivo del Sub-Agente 6 (Simulación física de saltos)
       ├──► [SUB-AGENTE 3: Pulido de las 4 Interfaces UI/UX y Flujo de Menús]
       │           └──► Revisión en vivo del Sub-Agente 6 (Check test_hud.py)
       ├──► [SUB-AGENTE 4: Reparación Total del Exportador GDevelop 5.6 (Físicas y Eventos 1:1)]
       │           └──► Revisión en vivo del Sub-Agente 6 (EVENTOS_OK + Compilación WASM)
       ├──► [SUB-AGENTE 5: Coherencia de Assets Pixel-Art, Animaciones y Hitboxes en GDevelop]
       │           └──► Revisión en vivo del Sub-Agente 6 (PARIDAD_OK + Assets 100% íntegros)
       ▼
[CIERRE DEL SUB-AGENTE 6: Auditoría Final Cero Bugs y Certificación para gd.games]
```

---

## 3. Diagnóstico de Bugs y Fallos Actuales Detectados en el Código (Para Corrección Obligatoria)

La inspección del código actual del repositorio (`repomix-output_3`) reveló **fallos críticos** que explican por qué el salto con dash se siente brusco y por qué **el export de GDevelop tiene físicas distintas y no refleja los cambios de Pygame**:

### 3.1. Bugs en Pygame (`entidades.py` y `juego.py`)
1. **Bug de Tecla `A` rota para moverse a la izquierda (`entidades.py` línea ~329):**
   En `Jugador.actualizar_horizontal(self, teclas)` dice:
   `izquierda = teclas[pygame.K_LEFT]` (¡falta `or teclas[pygame.K_a]`!). Además, en `juego.py` (`TECLAS_ATAQUE = (pygame.K_a, pygame.K_j, pygame.K_z)`), la tecla `K_a` está asignada a atacar, entrando en conflicto con caminar a la izquierda con `WASD`.
   * **Solución:** En `entidades.py`, usar `izquierda = teclas[pygame.K_a] or teclas[pygame.K_LEFT]`. En `juego.py`, definir `TECLAS_ATAQUE = (pygame.K_j, pygame.K_z, pygame.K_k)` (más click izquierdo del mouse) para que `A` y `D` muevan limpiamente al personaje sin disparar ataques accidentales.
2. **Método duplicado en `entidades.py`:**
   `Jugador.actualizar_temporizadores(self, dt)` está definido **dos veces seguidas** (líneas 317 y 341). Eliminar el duplicado.
3. **Frenazo brusco al terminar el Dash (`entidades.py` línea ~315):**
   Al terminar el Dash (`if self.dash_tiempo == 0:`), el código hace `self.vx = self.dash_direccion * VELOCIDAD * 0.55`, reduciendo de golpe la velocidad a casi la mitad en el aire y aplicando $100\%$ de gravedad instantánea. Además, durante el Dash (`if self.dash_tiempo > 0: return`), se bloquea la lectura del *Jump Buffer* y no se permite hacer *Dash-Jump* desde el suelo.
4. **Código muerto en `juego.py` (`dibujar_hud_relicario_vidas`, `dibujar_hud_relicario_derecho`, `dibujar_barra_jefe`):**
   Quedaron métodos viejos del HUD anterior en `juego.py` que ya no se llaman porque `self.hud.dibujar()` delega en `hud.py`, pero `dibujar_hud()` todavía tiene referencias residuales.

### 3.2. Por Qué el Export de GDevelop (`tools/generar_proyecto_nativo.py` y `tools/exportador/*`) NO Es el Mismo Juego y Tiene las Físicas Cambiadas
1. **Física de Salto Alterada en GDevelop (`jumpSustainTime: 0.20` + falta de `CORTE_SALTO`):**
   * En `tools/exportador/gdevelop.py` (`comportamiento_jugador()`), está configurado `"jumpSustainTime": 0.20`, y en `generar_proyecto_nativo.py` (línea 777) un evento ejecuta `SimulateJumpKey` cada frame mientras se mantiene `Space/Up/W`. En GDevelop 5.6, eso mantiene el empuje vertical durante $200\text{ ms}$ anulando la gravedad inicial y produciendo un salto de **$5.2\text{ tiles}$ de altura (flotante y descontrolado)** en vez de los **$3.84\text{ tiles}$ ($123\text{ px}$)** de Pygame.
   * Además, en `generar_proyecto_nativo.py` **se eliminó el corte de salto al soltar la tecla**, por lo que los saltos cortos precisos no responden igual que en Pygame.
2. **Física de Dash y Pisotón (Stomp) Rota en GDevelop:**
   * En `generar_proyecto_nativo.py` (línea 1061), al terminar el Dash (`dash_time <= 0`), se ejecuta `SetCurrentSpeed = 0`. ¡El personaje se frena a velocidad $0$ en medio del aire al terminar el Dash! En lugar de `0`, debe conservar `Jugador.Variable(dir) * 250` ($100\%$ de `VELOCIDAD`).
   * En el **Pisotón (Stomp)** en GDevelop (línea 1198), se llama a `SimulateJumpKey` con `JumpSpeed = 620`, lo que lanza al jugador con la fuerza de un salto completo ($620\text{ px/s}$) contra los pinchos del techo, en vez del `REBOTE_ENEMIGO = 360` de Pygame.
3. **Zoom y Cámara Desincronizados (`GAME_ZOOM = 1.0` vs `1.25`):**
   * En Pygame (`config.py`), el mundo visible es `VIRTUAL_ANCHO = 1024`, `VIRTUAL_ALTO = 576` escalado con `CAMARA_ZOOM = 1.25` a `1280x720`.
   * En `generar_proyecto_nativo.py` (línea 115), pusieron `GAME_ZOOM = 1.0` con ventana `1280x720`. Como los niveles miden $18\text{ filas} \times 32\text{ px} = 576\text{ px}$ de alto, en GDevelop sobran $144\text{ px}$ verticales y se ve un $25\%$ más de mapa que en Pygame, cambiando toda la percepción de velocidad y escala.
4. **Hitbox del Jugador Deformada (`32x32` en GDevelop vs `24x30` en Pygame):**
   * En Pygame el jugador colisiona con un rectángulo de `24 x 30` px. En GDevelop se instancia de `32 x 32` px con `hasCustomCollisionMask: False`. Esos $8\text{ px}$ extra de ancho hacen que el jugador choque contra los bordes de la ventana alta del Nivel 2 (`cols 170-171`) y muera con pinchos que en Pygame esquiva limpiamente.
5. **Animaciones Pixel-Art que Nunca se Reproducen en GDevelop:**
   * Aunque `integrar_assets_gdevelop.py` inyecta las animaciones `Run` (índices 10 y 11), `Jump` (12 y 13) y `Dash` (14 y 15) en el objeto `Jugador`, los eventos en `generar_proyecto_nativo.py` (líneas 900–963) solo cambian entre `0/3/6/8` (`Idle`), `1/4/7/9` (`Caida`) y `2/5` (`Ataque`). ¡Por eso en GDevelop el personaje se desliza estático sin animar al correr ni al hacer Dash!
6. **Mecánicas Nuevas Ausentes o Incompletas en los Eventos de GDevelop:**
   * En GDevelop, el altar de la Guadaña (`PowerUpRango` / `'X'`) se puede agarrar sin derrotar al Mini-Boss (`MiniJefe` / `'K'`).
   * En GDevelop, `MiniJefe` no tiene su máquina de estados (`patrulla -> telegrafo -> ataque -> cansado/vulnerable`) y recibe daño en cualquier momento.
   * En GDevelop, tocar un `FarolCheckpoint` (`'F'`) no cambia su animación a `Encendido` (`1`), no cura $+1\text{ HP}$ cuando `vidas < 3`, ni otorga el `Manto del Farol` (`escudo_farol = 1` al juntar $\ge 5$ almas).
   * En GDevelop, falta agregar `checkpoint_activo` y `checkpoint_escena` a la lista inicial `base["variables"]` en `construir_proyecto()`.

---

## 4. Plan de Ejecución Secuencial y Coordinado por Sub-Agente

### SUB-AGENTE 1 — Mejora de Física Salto+Dash (*Game Feel*) y Sistemas en Pygame
**Archivos asignados:** `config.py`, `entidades.py`, `juego.py`.

1. **Perfeccionar la Física de Salto + Dash en `entidades.py` y `config.py`:**
   * **Apex Hang-Time (Flotación en el Ápice del Salto):** En `Jugador.actualizar()`, cuando el jugador está en el aire (`not self.en_suelo`), manteniendo la tecla de salto y cerca del punto más alto de la parábola ($|v_y| < 95.0\text{ px/s}$), aplicar gravedad reducida ($0.55 \times \text{GRAVEDAD}$). Esto hace que el momento exacto de encadenar `Salto -> Dash` se sienta fluido, cómodo y predecible.
   * **Transición Suave Post-Dash (Fin del Frenazo Brusco):** Agregar en `Jugador` un temporizador `self.post_dash_tiempo = 0.0`. Cuando `self.dash_tiempo` llega a $0$, en lugar de cortar `self.vx = self.dash_direccion * VELOCIDAD * 0.55`, establecer `self.vx = self.dash_direccion * VELOCIDAD` ($100\%$ de velocidad horizontal) e iniciar `self.post_dash_tiempo = 0.06` segundos durante los cuales la gravedad es $0.5 \times \text{GRAVEDAD}$.
   * **Dash-Jump (Salto desde Dash en Suelo) y Buffer Durante Dash:** En `Jugador.actualizar()`, actualizar siempre `self.actualizar_temporizadores(dt)` **antes** del `if self.dash_tiempo > 0:`. Si el jugador presiona Salto (`self.buffer_salto > 0`) mientras está haciendo un Dash en el suelo (`self.en_suelo` o `self.coyote > 0`), cancelar `self.dash_tiempo = 0.0` e impulsar un **Dash-Jump** satisfactorio (`self.vy = SALTO`, `self.vx = self.dash_direccion * VELOCIDAD * 1.18`, `self.en_suelo = False`, `self.salto_recien = True`).
   * **Jump Corner Correction (Tolerancia de Esquinas en Techo):** En `Jugador.mover_y()`, si el jugador sube (`dy < 0`) y choca la esquina de un bloque sólido por $\le 5\text{ px}$ laterales, deslizarlo suavemente $1\text{ a }5\text{ px}$ hacia el hueco libre sin anular su velocidad vertical `vy`.
2. **Corregir Controles y Duplicados:**
   * En `Jugador.actualizar_horizontal()`, habilitar `izquierda = teclas[pygame.K_a] or teclas[pygame.K_LEFT]`.
   * Eliminar la definición duplicada de `actualizar_temporizadores` en `entidades.py`.
   * En `juego.py`, separar `K_a` de `TECLAS_ATAQUE` si se está presionando para caminar, o usar `J`, `Z`, `K` y Click Izquierdo para atacar, garantizando que moverse a la izquierda con `A` nunca sea bloqueado.

> **Revisión del Sub-Agente 6 tras Sub-Agente 1:** Auditar `git diff config.py entidades.py juego.py` y correr `tests/test_logica.py`.

---

### SUB-AGENTE 2 — Ajuste de Desafíos, Fosos y Curva de Dificultad en Niveles
**Archivos asignados:** `niveles.py`, `niveles_rediseñados.py`, `nivel.py`.

1. **Calibración de Fosos y Plataformas con la Física Mejorada de Salto + Dash:**
   * Revisar tramo por tramo `NIVEL_TUTORIAL`, `NIVEL_1`, `NIVEL_2`, `NIVEL_3` y las 3 salas de `niveles_rediseñados.py`.
   * **Métrica de oro:**
     * Saltos sin Dash (Preludio y Beat 1 de Nivel 1): Huecos de $3\text{ a }4\text{ tiles}$ con plataformas de aterrizaje amplias (mínimo $4\text{ a }6\text{ tiles}$ de ancho) para que el jugador no sienta frustración artificial.
     * Saltos con Dash obligatorio (Beats 2–4 de Nivel 1 y Nivel 2): Huecos de $6\text{ a }7\text{ tiles}$ claramente señalizados con un **arco o línea horizontal de Almas (`o`)** a la altura exacta donde conviene activar `SHIFT`.
     * Secuencias de **Pisotón + Recarga de Dash** (Nivel 2 y Nivel 3): Asegurar que los enemigos (`E`) que actúan como "trampolines" sobre fosos de $10\text{ a }12\text{ tiles}$ tengan al menos $3\text{ tiles}$ de plataforma debajo para no quedar estáticos de forma antinatural, y que la altura del techo sobre ellos deje margen amplio ($\ge 4\text{ tiles}$ libres arriba) para el rebote del pisotón.
     * **Ventana de la Gran Pared en Nivel 2 (`cols 170-171`):** Verificar que la apertura de la ventana tenga $2\text{ a }3\text{ filas}$ libres de alto y que la parábola desde la plataforma de lanzamiento (`col 163`) con `Salto + Dash` sea holgada y satisfactoria tanto en Pygame como en GDevelop.

> **Revisión del Sub-Agente 6 tras Sub-Agente 2:** Correr todas las pruebas de simulación de salto (`probar_pozo_de_dash`, `probar_primer_salto_cripta`, `probar_salto_ventana_nivel_2`, `probar_mapa_final`) en `tests/test_logica.py`.

---

### SUB-AGENTE 3 — Coherencia UI/UX (Las 4 Interfaces y 5 Principios)
**Archivos asignados:** `hud.py`, `juego.py`.

1. **Limpieza y Sincronización de las 4 Interfaces:**
   * Eliminar de `juego.py` los métodos muertos del HUD viejo (`dibujar_hud_relicario_vidas`, `dibujar_hud_relicario_derecho`, `dibujar_barra_jefe` antiguos) dejando únicamente el sistema limpio de `HudOrquestador` (`hud.py`) más las capas Diegética, Espacial y Meta.
   * En `dibujar_ui_espacial()` (`juego.py`), corregir el chequeo de atributo `getattr(dp, "recogida", False)` (actualmente chequea `"recogido"` con *o* en vez de `"recogida"` con *a*, haciendo que el cartel espacial siga apareciendo después de recoger el Dash o la Guadaña).

> **Revisión del Sub-Agente 6 tras Sub-Agente 3:** Ejecutar `tests/test_hud.py` y `tests/test_logica.py`.

---

### SUB-AGENTE 4 — Reparación Integral del Exportador GDevelop 5.6 (Paridad Física y Funcional 1:1)
**Archivos asignados:** `tools/exportador/gdevelop.py`, `tools/exportador/reglas.py`, `tools/exportador/manifiesto.py`, `tools/generar_proyecto_nativo.py`.

Esta es la tarea más crítica de la entrega. Debés lograr que al abrir `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` en GDevelop 5.6, el juego se sienta, se vea y funcione **idéntico** a Pygame:

1. **Paridad Exacta de Cámara y Viewport (`1024x576` con Zoom `1.25`):**
   * En `tools/generar_proyecto_nativo.py`: Definir `GAME_ZOOM = 1.25` para la capa base `""` (para que la ventana de `1280x720` muestre exactamente `1024x576` unidades de mundo igual que `VIRTUAL_ANCHO x VIRTUAL_ALTO` en Pygame) y mantener zoom `1.0` en la capa `"UI"`.
   * En `eventos_nivel()`, calcular `centro_x`, `max_cam_x`, `centro_y` y `max_cam_y` usando `VIRTUAL_ANCHO` ($1024$) y `VIRTUAL_ALTO` ($576$) en lugar de `1280` y `720`. Así el suelo queda perfectamente anclado abajo sin franjas vacías.
2. **Paridad Exacta de Física de Salto, Corte de Salto, Dash y Pisotón en GDevelop:**
   * **Salto y Gravedad (`tools/exportador/gdevelop.py` y `generar_proyecto_nativo.py`):**
     * En `comportamiento_jugador()`, configurar `"gravity": 1500`, `"jumpSpeed": 620`, `"maxFallingSpeed": 900`, `"maxSpeed": 250`, `"jumpSustainTime": 0` (¡fundamental poner `0` y eliminar el evento que llama a `SimulateJumpKey` cada frame mientras `IsJumping` es verdadero, ya que ese evento deformaba la gravedad de GDevelop!).
     * Implementar el **Corte de Salto Variable (`CORTE_SALTO = 0.45`)** y el **Apex Hang-Time** en GDevelop: cuando `PlatformBehavior::IsJumping` es verdadero y ninguna tecla de salto (`Space`, `Up`, `w`, `W`) está presionada, ejecutar `PlatformBehavior::PlatformerObjectBehavior::AbortJump` sobre `Jugador`.
   * **Dash Fluido con Conservación de Momentum y Post-Dash Float:**
     * Soportar `LShift`, `RShift` y `x` / `X` para iniciar el Dash.
     * Durante el Dash (`dashing == 1` y `dash_time > 0`), bloquear el input normal de caminar (`dashing == 0` en las condiciones de mover izquierda/derecha) para que no compita con `SetCurrentSpeed`.
     * Al terminar el Dash (`dashing == 1` y `dash_time <= 0`), **NO** poner `SetCurrentSpeed = 0`: poner `SetCurrentSpeed = Jugador.Variable(dir) * 250` para conservar la fluidez horizontal igual que en Pygame.
   * **Pisotón (Stomp) con Altura de Rebote Exacta (`REBOTE_ENEMIGO = 360`):**
     * En todos los eventos de pisotón sobre enemigos, Mini-Jefe y Jefe en `generar_proyecto_nativo.py`: antes de llamar a `SetCanJump` y `SimulateJumpKey`, ejecutar `accion("PlatformBehavior::JumpSpeed", ["Jugador", "PlatformerObject", "=", "360"])`, y en el evento de salto normal desde suelo/coyote asegurar `accion("PlatformBehavior::JumpSpeed", ["Jugador", "PlatformerObject", "=", "620"])`. ¡Así el rebote del pisotón tendrá exactamente $360\text{ px/s}$ como en Pygame!
3. **Controles Duales Completos en GDevelop (`WASD` + Flechas):**
   * Izquierda: `Left` o `a` / `A`. Derecha: `Right` o `d` / `D`.
   * Salto: `Space`, `Up`, `w` / `W`.
   * Dash: `LShift`, `RShift`, `x` / `X`.
   * Ataque: `j` / `J`, `z` / `Z`, `k` / `K` o botón izquierdo del mouse (`MouseButtonPressed("Left")`).
4. **Sincronización de Mecánicas de Nivel 1, 2 y 3 en Eventos de GDevelop:**
   * **Variables Globales Completas:** Declarar explícitamente en `base["variables"]` de `construir_proyecto()`: `checkpoint_activo` ($0$), `checkpoint_escena` (`""`), `escudo_farol` ($0$), `almas_consagradas` ($0$), `almas_vida_consagradas` ($0$) y `minijefe_derrotado` ($0$).
   * **Faroles Checkpoint (`FarolCheckpoint`):** Al colisionar con un `FarolCheckpoint` cuyo `Variable(activo) == 0`:
     * Cambiar su variable `activo = 1` y cambiar su animación a `1` (`Encendido`).
     * Guardar `checkpoint_x`, `checkpoint_y`, `checkpoint_activo = 1`, `checkpoint_escena = CurrentSceneName()`.
     * Si `GlobalVariable(vidas) < 3`, sumar $+1$ a `vidas`.
     * Si `GlobalVariable(almas) - GlobalVariable(almas_consagradas) >= 5`, activar `GlobalVariable(escudo_farol) = 1` (Manto del Farol).
     * Actualizar `almas_consagradas = GlobalVariable(almas)`.
   * **Manto del Farol en GDevelop:** Si el jugador recibe daño y `GlobalVariable(escudo_farol) == 1`, consumir `escudo_farol = 0`, otorgar invulnerabilidad breve y **no** descontar vida ni reiniciar posición.
   * **Mini-Boss (`MiniJefe` - El Carcelero) y Altar Sellado (`PowerUpRango`):**
     * Dotar a `MiniJefe` en GDevelop de su ciclo de estados (`0`: patrulla $1.2\text{ s}$ $\rightarrow$ `1`: telegrafía $0.55\text{ s}$ $\rightarrow$ `2`: embestida a $220\text{ px/s}$ durante $0.40\text{ s}$ $\rightarrow$ `3`: cansado/vulnerable durante $1.3\text{ s}$).
     * Impedir que `Jugador` recoja `PowerUpRango` (`'X'`) mientras `SceneInstancesCount(MiniJefe) > 0` (mostrar en `HUD_Aviso`: `"¡ALTAR SELLADO! Derrota al Carcelero"`).
5. **Conectar Todas las Animaciones Multipose en los Eventos de GDevelop:**
   * En `generar_proyecto_nativo.py`, actualizar las reglas de animación de `Jugador` para usar las 16 animaciones reales:
     * Si `dashing == 1`: animación `14` (`Dash` der) o `15` (`DashIzq`).
     * Si `atacando == 1`: animación `2` (`Ataque` der) o `5` (`AtaqueIzq`).
     * Si no está en el piso (`IsOnFloor` invertido) y `IsJumping`: animación `12` (`Jump` der) o `13` (`JumpIzq`).
     * Si no está en el piso y `IsFalling`: animación `1`/`7` (`Caida` der con/sin pala) o `4`/`9` (`CaidaIzq` con/sin pala).
     * Si está en el piso y se mueve (`IsMovingEvenALittle`): animación `10` (`Run` der) o `11` (`RunIzq`).
     * Si está en el piso y quieto: animación `0`/`6` (`Idle` der con/sin pala) o `3`/`8` (`IdleIzq` con/sin pala).
   * Voltear horizontalmente (`FlipX`) a `Enemy`, `EnemyMelee`, `MiniJefe` y `Jefe` según su variable `dir` (`dir == -1` $\rightarrow$ `FlipX = yes`, `dir == 1` $\rightarrow$ `FlipX = no`).

> **Revisión del Sub-Agente 6 tras Sub-Agente 4:** Ejecutar `tools/validar_eventos_gd.py` ($\rightarrow$ `EVENTOS_OK`) y verificar con `node tools/compilar_proyecto_gd.js` si el entorno dispone de Node/WASM.

---

### SUB-AGENTE 5 — Assets Pixel-Art Góticos, Máscaras de Colisión (`24x30`) y UI en GDevelop
**Archivos asignados:** `tools/integrar_assets_gdevelop.py`, `tools/exportador/sprites.py`, `export/gdevelop_nativo/assets/`.

1. **Máscara de Colisión Personalizada Exacta (`customCollisionMask`) para Paridad Física:**
   * En `tools/integrar_assets_gdevelop.py` (`_animacion_dict`), para el objeto `Jugador` (cuya textura 2x mide `64x64` y cuya instancia en escena mide `32x32`), configurar `"hasCustomCollisionMask": True` con el polígono centrado que equivale a los `24 x 30` px de Pygame (en coordenadas del sprite 2x de `64x64`: $x \in [8, 56]$, $y \in [4, 64]$):
     ```python
     "hasCustomCollisionMask": True,
     "customCollisionMask": [[
         {"x": 8, "y": 4},
         {"x": 56, "y": 4},
         {"x": 56, "y": 64},
         {"x": 8, "y": 64},
     ]]
     ```
   * Esto garantiza que la hitbox física del jugador en GDevelop mida exactamente `24 x 30` px en el mundo mientras su arte visual mide `32 x 32` px (cumpliendo el principio de *Hitbox menor que el sprite* tanto en Pygame como en GDevelop).
2. **Coherencia Visual de Fondos, Tiles y las 4 Interfaces en GDevelop:**
   * Asegurar que `tools/exportar_todo.py` ejecute siempre `integrar_assets_gdevelop.py` al final de `generar_proyecto_nativo.py` sin que `limpiar_assets()` borre los frames multipose (`jugador_run_*.png`, `jugador_jump_*.png`, `jugador_dash_*.png`, `enemy_walk_*.png`, `farolcheckpoint_on_*.png`, etc.).
   * Agregar en la escena de GDevelop los objetos visuales para las 4 interfaces: el halo diegético del farol, los carteles espaciales en los altares (`D`, `W`, `X`) y la viñeta Meta carmesí en la capa `"UI"` cuando `GlobalVariable(vidas) == 1`.

---

### SUB-AGENTE 6 — Auditor de Bugs, Fallos, Concurrencia y Certificación Final (Nuevo Rol Transversal)
**Archivos asignados:** `tests/test_logica.py`, `tests/test_hud.py`, `tools/verificar_paridad.py`, `tools/validar_eventos_gd.py`.

Actuás como el **Guardia de Calidad (QA & Bug Hunter)** después de cada Sub-Agente y al cierre del proyecto:

1. **Auditoría de Sincronización entre Sub-Agentes:**
   * Verificar después de cada fase que ningún Sub-Agente haya dejado conflictos de merge, variables no declaradas, imports rotos ni regresiones.
2. **Ampliación de `tools/verificar_paridad.py`:**
   * Mejorar `tools/verificar_paridad.py` para que no solo verifique posiciones de instancias, sino también:
     * Que `GAME_ZOOM == 1.25` coincida con `config.CAMARA_ZOOM`.
     * Que `MiniJefe` esté exportado en el Nivel 3 y en la Sala 3 Rediseñada.
     * Que todas las imágenes referenciadas en las animaciones multipose de `IN_CRYPTA_NATIVO.json` existan físicamente en `export/gdevelop_nativo/assets/`.
     * Que `checkpoint_activo`, `checkpoint_escena` y `escudo_farol` existan en las variables globales del proyecto GDevelop.
3. **Suite de Pruebas de Regresión en `tests/test_logica.py`:**
   * Agregar un test específico `probar_fisica_salto_dash_game_feel()` que verifique:
     * Que la tecla `K_a` mueve al jugador hacia la izquierda (`vx < 0`).
     * Que el *Apex Hang-Time* reduce la gravedad en la cima del salto.
     * Que al terminar un Dash aéreo la velocidad horizontal no cae abruptamente a $0.55 \times \text{VELOCIDAD}$, sino que conserva el impulso y permite cruzar fosos de $7\text{ tiles}$ con amplio margen.
     * Que el *Dash-Jump* desde el suelo funciona correctamente.

---

## 5. Barrera de Calidad Final (Comandos de Certificación Obligatorios)

El Orquestador **NO** puede dar por terminado el objetivo hasta que los siguientes 5 comandos se ejecuten en secuencia y devuelvan $0$ errores:

```bash
# 1. Regenerar ambos exports (Web JS + GDevelop 5.6 Nativo con Assets Pixel-Art Multipose) y verificar paridad
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/exportar_todo.py

# 2. Validar el 100% de las hojas de eventos contra la API WebAssembly de GDevelop 5.6
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/validar_eventos_gd.py

# 3. Verificar integridad de todos los assets PNG Pixel-Art en export/gdevelop_nativo/assets/
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/integrar_assets_gdevelop.py --check

# 4. Ejecutar la suite completa de lógica, físicas Salto+Dash, jefes y niveles
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_logica.py

# 5. Ejecutar la suite completa de UI/UX y las 4 interfaces del HUD
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_hud.py
```

Todos deben imprimir en consola: `EXPORT_OK`, `PARIDAD_OK`, `EVENTOS_OK`, `TESTS_INCRYPTA_OK` y `OK` en `test_hud.py`. Finalizar con un commit atómico limpio por archivo y presentar el reporte de auditoría de los 6 Sub-Agentes.