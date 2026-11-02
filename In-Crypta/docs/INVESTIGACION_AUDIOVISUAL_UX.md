# INVESTIGACIÓN, BITÁCORA Y DECISIONES TÉCNICAS: UI/UX, GAME FEEL Y PROCEDURALIDAD

**Proyecto:** IN CRYPTA (Plataformero Gótico 2D de Precisión)  
**Motor:** Python 3 + `pygame-ce` · Export nativo a GDevelop 5  
**Fecha de inicio:** Octubre 2026  
**Documento rector:** [`docs/PROMPT_MEJORA_AUDIOVISUAL_UX_PROCEDURAL.md`](file:///C:/Users/sanol/OneDrive/Escritorio/In-Crypta-main/In-Crypta-main/docs/PROMPT_MEJORA_AUDIOVISUAL_UX_PROCEDURAL.md)

---

## 1. Fuentes Académicas y de Industria Consultadas

1. **Fagerholt, E., & Lorentzon, M. (2009).** *Beyond the HUD: User Interfaces for Increased Player Immersion in First-Person Shooter Games*. Master's Thesis, Chalmers University of Technology.
   - *Aplicación en In-Crypta:* Migración del modelo puramente no-diegético a una matriz cuádruple:
     - **Diegético:** El farol mortuorio del sepulturero (indica dash y almas), velas de checkpoint.
     - **Espacial:** Arcos de sablazo, trayectorias de pisotón y estelas espectrales en el espacio del nivel.
     - **Meta:** Viñeteado de sangre y desaturación en salud crítica (1 corazón), sacudida y flash de pantalla.
     - **No diegético:** El riel superior del HUD desacoplado y optimizado.

2. **Swink, S. (2008).** *Game Feel: A Game Designer's Guide to Virtual Sensation*. Morgan Kaufmann / CRC Press.
   - *Aplicación en In-Crypta:* Curvas ADSR para las mecánicas cinéticas:
     - Salto: Ataque instantáneo (-620 px/s), sostén amortiguado por corte de salto (0.45x) y decaimiento elástico.
     - Dash: Envolvente rápida a 560 px/s con duración 0.20s y recarga predecible de 0.60s.
     - Telegrafía previa a cada ataque enemigo $\ge 200\text{ ms}$.

3. **Jonasson, M., & Purho, P. (2012).** *"Juice it or lose it"*. Game Developers Conference (GDC) Europe 2012.
   - *Aplicación en In-Crypta:* Principio de preservación estricta de volumen en *Squash & Stretch* ($\text{scale}_X \cdot \text{scale}_Y = 1.0$), redundancia multisensorial (partícula + sonido + cámara + HUD simultáneos).

4. **Eiserloh, S. (2016).** *"Juicing Your Cameras With Math"*. GDC 2016 (Math for Game Programmers).
   - *Aplicación en In-Crypta:* Implementación de sacudida por trauma cuadrático ($T^2$). Desplazamiento máximo ponderado por trauma acumulado con decaimiento lineal continuo.

5. **Norman, D. (2013).** *The Design of Everyday Things*. Basic Books. & Heurísticas PLAY (Desurvire et al.).
   - *Aplicación en In-Crypta:* Reducción de los Golfos de Ejecución y Evaluación en el HUD; eliminación de leyendas textuales redundantes en favor de iconografía universal clara.

6. **W3C (2018).** *Web Content Accessibility Guidelines (WCAG) 2.1*.
   - *Aplicación en In-Crypta:* Relación de contraste de luminancia $\ge 7:1$ para indicadores vitales sobre fondos de piedra oscura.

---

## 2. Registro de Fases, Sub-Agentes y Decisiones Técnicas Implementadas

### Fase 1: Arquitectura y Configuración de Estilos (`config.py`)
- **Implementado:** Diccionario `ESTILOS_GOTICOS` con las 4 variantes estéticas góticas completas:
  - `monastico`: Oro viejo, carmesí litúrgico, marfil de altar.
  - `hierro`: Acero forjado, óxido, chispas de fragua y manómetros de vapor.
  - `espectral`: Cian ectoplásmico, fulgor lavanda, niebla etérea.
  - `osario`: Hueso pulido, púrpura cardenalicio, sangre seca.
- Variable rectora `ESTILO_VISUAL_ACTUAL = "monastico"`.

### Fase 2: Cinemática y Animación Procedural Vectorial (`entidades.py`)
- **Sub-Agente 2 (Especialista en Animación Procedural):**
  - **Rigging Articular de Piernas y Botas:** Desfasaje trigonométrico en contrafase ($\phi$ y $\phi + \pi$) para piernas anterior y posterior en capas de profundidad separadas. Flexión anatómica de rodilla hacia adelante $\max(0, -\cos(\phi))$ y zancada elástica $\sin(\phi)$.
  - **Balanceo Vertical y Torso:** Transferencia elástica de peso $cadera\_bob = -|\sin(\phi)| \times 2.4$, respiración armónica en reposo e inclinación inercial $lean\_x$ proporcional a la velocidad horizontal $vx$.
  - **Inercia Elástica de la Capa:** Arrastre aerodinámico dinámico en $vx$ (con extensión violenta de 16 px durante el dash), viento ascendente (*updraft*) que infla la capa hacia arriba al descender ($vy > 0$), y arrugas de tela con armónicos sinusoidales dobles. Polígono bicapa con terciopelo gótico interior.
  - **Péndulo Mortuorio del Farol con Halo Circular:** Oscilación pendular armónica, cadena eslabonada articulada y emisión de halo circular translúcido con canal alfa (`pygame.SRCALPHA`) con 4 capas concéntricas y parpadeo de vela (*candle flicker*).
  - **Squash & Stretch con Preservación Estricta de Volumen:** Fórmula exacta de conservación de área:
    $$\text{escala}_X \cdot \text{escala}_Y = 1.0 \implies \text{escala}_X = \frac{1.0}{\text{escala}_Y}$$
    Amortiguación armónica elástica amortiguada al aterrizar ($progreso \in [0, 1]$, oscilación $\sin(p \cdot \pi \cdot 2.2)$) y estiramiento en salto/caída. Hitbox $24 \times 30$ completamente intacta.
  - **Telegrafía Visual Anticipada en Enemigos:**
    - `EnemigoMelee`: Telegrafía $\ge 200$ ms (configurada a 300 ms) al detectar al jugador a rango melee (70 px horizontal, 20 px vertical). Ignición de ojos en haz amenazante y elevación cinemática del alfanje por encima de la cabeza (*wind-up*).
    - `TotemProyectil`: Obelisco monolítico de piedra arcana facetada con runas grabadas y plasma flotante.

### Fase 3: Game Feel, Shaders Procedurales y Hitstop (`efectos.py`, `camara.py`, `juego.py`)
- **HitstopManager (`efectos.py` & `juego.py`):** Congelamiento de impacto quirúrgico de 3 cuadros ($0.05$ s en enemigos, $0.06$ s en jefe) al golpear con pala o realizar stomps. Integrado en el bucle principal `run()` permitiendo que partículas y cámara sigan vibrando durante la pausa temporal.
- **Trauma Cuadrático ($T^2$) en Cámara (`camara.py`):** Conforme a Squirrel Eiserloh (GDC 2016), el desplazamiento de la pantalla escala con el cuadrado del trauma ($desplazamiento = D_{max} \cdot T^2$), logrando sacudidas orgánicas y no lineales con decaimiento temporal continuo.
- **Viñeta de Peligro Crítico (`juego.py`):** Viñeta periférica escarlata pulsante con modulación armónica ($\sin(5t)$) cuando $jugador.vidas == 1$, advirtiendo al jugador sin oscurecer el centro de la acción (WCAG 2.1 AAA).

### Fase 4: Micro-Interacciones del HUD y Estilos Góticos (`hud.py`)
- **Geometrías Procedurales Vectoriales según Estilo:**
  - `monastico`: Esquinas con Cruz Paté gótica (`_dibujar_cruz_pate`), cirio litúrgico con llama titilante para dash, cuentas de rosario doradas para vida extra, y segmentos de barra del Custodio modelados como **rubíes facetados biselados** con reflejo especular blanco-rosado y marco de oro.
  - `hierro`: Remaches metálicos de hierro negro con brillo especular (`_dibujar_remache`), manómetro de presión de vapor para dash, pips de vapor y placas de acero forjado con núcleo incandescente.
  - `espectral`: Glifos rúnicos etéreos (`_dibujar_runa_espectral`), llamas votivas turquesas y barras de ectoplasma translúcido.
  - `osario`: Cráneos góticos tallados (`_dibujar_craneo_miniatura`), fémur cruzado para dash, y vértebras óseas con médula carmesí.
- **Desacoplamiento y Foco Visual (Norman 2013):** Atenuación automática de la opacidad de los paneles laterales ($alpha = 160$) durante el combate contra el Custodio para focalizar la atención en la arena.
- **Entrada Suave de Barra de Jefe:** Transición animada mediante `ease_out_cubic` al despertar el jefe.
- **Selector Dinámico:** Método `HudOrquestador.cambiar_estilo(nombre)` para alternar en caliente entre las 4 identidades visuales.

### Fase 5: Audio Procedural Sintético PCM (`audio.py`)
- **Sub-Agente 1 (Especialista en Audio Procedural):**
  - Ampliación del mezclador a 16 canales polifónicos independientes.
  - **Campanas Litúrgicas Additive Synthesis:** Serie armónica litúrgica ($f_0 \cdot [1, 2, 3, 4.2]$) con decaimiento exponencial para la recolección de almas (`alma_1` a `alma_6`), construyendo un acorde ascendente en combo.
  - **Fanfarria de Vida Extra:** Arpegio triádico ascendente triunfal con armónicos dorados.
  - **Impacto de Pala:** Doble capa de transitorio de impacto (ruido de arena/piedra con envolvente de 8 ms) + resonancia metálica/ósea.
  - **Micro-Variación de Tonalidad ($\pm 2.5\%$):** Jitter acústico aleatorio en cada llamada a `reproducir()` para evitar la habituación auditiva del jugador.

### Fase 6: Aseguramiento de Calidad y Verificación de Paridad
- **Pruebas de Lógica de Juego:** `tests/test_logica.py` $\implies$ **32/32 tests OK** (`TESTS_INCRYPTA_OK`).
- **Pruebas de HUD:** `tests/test_hud.py` $\implies$ **26/26 tests OK** (`TESTS_HUD_OK`).
- **Verificación de Paridad GDevelop 5:** `tools/verificar_paridad.py` $\implies$ **53/53 comprobaciones OK** (`PARIDAD_OK`).
- **Rendimiento:** 60 FPS estables sin texturas ni librerías de assets externas. Zero regressions.

