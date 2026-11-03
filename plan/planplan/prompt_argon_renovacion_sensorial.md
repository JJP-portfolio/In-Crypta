# PROMPT PARA ARGON: Plan Maestro de Renovación Sensorial de IN CRYPTA

> **Destinatario:** Argon (Director Técnico de Arte, Diseñador Audiovisual y Experto en Game Feel)  
> **Insumo Técnico:** Repomix XML adjunto (`repomix/repomix_redisenado_sensorial.xml` con `config.py`, `hud.py`, `audio.py`, `efectos.py`, `particulas.py`, `entidades.py`, `nivel.py`, `juego.py`, `assets_loader.py` y `manifest_assets.json`).  
> **Proyecto:** *IN CRYPTA* (Plataformero de acción gótica en Pygame-ce y WebAssembly/Pygbag).  
> **Objetivo:** Diseñar la estrategia integral para crear una rama nueva (`art/overhaul-sensorial`) con mejoras audiovisuales, corrección de música, contraste visual de enemigos, rediseño de HUD, feedback de hitboxes/hurtboxes, tiles y efectos, para posterior ejecución autónoma en modo `/goal`.

---

## 1. REGLAS DURAS Y RESTRICCIONES ABSOLUTAS (GUARDRAILS)

Para garantizar la integridad del proyecto y la aprobación académica de la entrega, cualquier recomendación debe respetar estrictamente:

1. 🚫 **NO TOCAR FÍSICAS:** Las constantes de aceleración, velocidad, fricción, salto, caída máxima, tiempos de coyote, buffers de salto y cooldowns de ataque/dash en `config.py` y `entidades.py` no se tocan. La respuesta cinética del personaje está aprobada y calibrada.
2. 🚫 **NO TOCAR DISEÑO DE NIVELES:** La matriz de salas, geometría de plataformas `#`, ubicación de puertas, puntos de control, faroles y posiciones iniciales de enemigos en `niveles.py` o `nivel.py` permanecen 100% inalteradas.
3. 🚫 **NO AGREGAR NUEVAS MECÁNICAS:** No se inventan nuevos poderes, combos, árboles de habilidades ni tipos de daño no existentes.
4. ⚡ **EL ENFOQUE ES EXCLUSIVAMENTE SENSORIAL:** Visuales, estética, contraste cromático, siluetas, jerarquía de planos, audio, ambientación musical, feedback de impacto (game feel) y claridad de interfaz.
5. 🌐 **COMPATIBILIDAD CON WEBASSEMBLY (PYGBAG):** Todo renderizado, shader o efecto debe ser capaz de correr de forma fluida a 30-60 FPS en el canvas del navegador (`sys.platform == 'emscripten'`) sin depender de hilos múltiples ni shaders GLSL no soportados.
6. 🧪 **SUITE DE PRUEBAS VERDE:** Todos los tests de la suite (`pytest tests/`) deben seguir pasando (51 pasados).

---

## 2. DIAGNÓSTICO DEL ESTADO ACTUAL (ÁREA POR ÁREA)

### A. Enemigos y Contraste Visual (Problema Crítico de Mimetización)
- **Diagnóstico:** Los moradores y carceleros (`Enemigo`, `EnemigoMelee` en `entidades.py`) se dibujan con polígonos y elipses en tonos oscuros apagados: `(22, 32, 18)` (verde musgo ceniza), `(38, 30, 20)` (marrón oscuro), `VERDE_OSCURO`. A su vez, los fondos de cripta y los bloques de suelo usan `(68, 52, 42)`, `(44, 32, 26)` y `(52, 56, 68)`. El valor de luminancia (Value en HSV) es casi idéntico. En una sala oscura o con el velo de penumbra, los enemigos se camuflan completamente con el fondo hasta que golpean al jugador.
- **Puntos a renovar:**
  - Siluetas claras y legibles desde la visión periférica.
  - Ojos o marcas espectrales con emisión luminosa (ej. resplandor carmesí o turquesa con blend aditivo).
  - Luz de borde (*rim lighting*) para recortar el sprite de la entidad frente a paredes oscuras.
  - Diferenciación visual clara entre el enemigo volador (cuervo/polilla), el patrullero común y el enemigo de choque/jefe.

### B. Fondos (Backgrounds) y Jerarquía de Planos
- **Diagnóstico:** `juego.py` dibuja los fondos mediante funciones vectoriales procedurales (`dibujar_fondo_camposanto`, `dibujar_fondo_cripta`, `dibujar_fondo_osario`) que dibujan rejas, arcos y lunas. Algunos elementos del fondo tienen líneas y contrastes demasiado duros que compiten visualmente con los bordes de las plataformas reales.
- **Puntos a renovar:**
  - Principio de perspectiva atmosférica (Fondo en tonos desaturados, fríos, con menor detalle y bajo contraste; Plano Medio interactivo con bordes limpios; Primer Plano de acción con mayor saturación y nitidez).
  - Neblina y partículas ambientales que aporten profundidad sin ensuciar la pantalla.

### C. Tiles de Piso y Plataformas
- **Diagnóstico:** `nivel.py` dibuja las plataformas (`dibujar_plataformas`) como sarcófagos suspendidos de cadenas, y los sólidos (`dibujar_solidos`) como sillería de piedra o tierra con lápidas rotas. Aunque tienen detalle procedural, los límites superiores donde el jugador apoya los pies (superficie caminable) se funden con los laterales en ciertas salas.
- **Puntos a renovar:**
  - Bisel de luz superior claro (*walkable edge cue*) que delimite claramente el borde de colisión de las plataformas.
  - Distinción visual inmediata entre piso destructible (`LosaQuebradiza`), plataformas pasables/atravesables y bloques sólidos impenetrables.
  - Variación visual estética entre los tres biomas: *Camposanto* (tierra, lápidas musgosas, raíces), *Cripta* (losas góticas húmedas, argollas de hierro), *Osario* (huesos incrustados, calaveras, piedra caliza carmesí).

### D. Hitboxes, Hurtboxes y Feedback de Combate
- **Diagnóstico:**
  - El juego carece de un sistema de depuración visual de cajas de colisión.
  - El ataque del sepulturero (`rect_ataque()` en `entidades.py`) define un área rectangular que no se corresponde de forma visualmente obvia con la animación del tajo de la pala o la guadaña.
  - No hay efectos de impacto satisfactorios (*hit-sparks*, destello blanco momentáneo en el enemigo dañado (*damage flash*), ni micro-sacudida de cámara graduada).
- **Puntos a renovar:**
  - Implementar un modo de depuración (`F3`) que dibuje con alpha: Hurtbox del jugador (verde), Hurtbox de enemigos (naranja), Hitbox de ataque activo (rojo) y Cajas de peligro/espinas (violeta).
  - Diseñar el feedback visual del impacto: *hit-spark* gótico (chispas doradas/espectrales), parpadeo del sprite del enemigo al recibir daño (*hit flash* en blanco puro durante 2 frames) y estela de ataque diegética alineada con el hitbox.

### E. Música y Audio (Diagnóstico y Reparación de la Falla Actual)
- **Diagnóstico del Fallo:**
  - En `assets_in_crypta/entrega/musica/` existen 10 pistas musicales OGG compuestas y remasterizadas: `titulo.ogg`, `camposanto.ogg`, `cripta.ogg`, `osario.ogg`, `carcelero.ogg`, `custodio_f1.ogg`, `custodio_f2.ogg`, `victoria.ogg`, `derrota.ogg` y `creditos.ogg`.
  - En `audio.py` existen las funciones `reproducir_musica(id_musica, bucle, fade_ms)` y `detener_musica(fade_ms)`.
  - **Sin embargo, `juego.py` NUNCA invoca `reproducir_musica` durante las transiciones de nivel, pantallas de título o batallas de jefes.** El juego solo inicia el zumbido de catacumbas (`iniciar_dron()`), provocando que la música esté completamente ausente o parezca rota.
- **Puntos a renovar:**
  - Orquestación musical en `juego.py`: Disparar la pista correspondiente al entrar al menú principal, al cambiar de bioma (Camposanto, Cripta, Osario), al entrar a la sala del jefe (`custodio_f1`, cambio a `custodio_f2` en fase 2) y en pantallas de victoria/derrota con crossfades limpios.
  - Balance de mezcla: Regular el volumen relativo de la música frente al dron y a los efectos de sonido (SFX de pala, dash, latido del corazón y recolección de almas).

### F. HUD (Interfaz de Usuario)
- **Diagnóstico:** `hud.py` cuenta con una arquitectura moderna de 3 zonas y tweens de animación, pero los íconos de corazones, indicador de dash y contador de almas están trazados con primitivas geométricas rígidas.
- **Puntos a renovar:**
  - Estilización gótica: Marcos tipo relicario labrado con filigrana dorada desgastada.
  - Indicador de dash y recarga con pulso o destello cuando vuelve a estar disponible.
  - Contador de almas con iconografía mística y animación suave al incrementar el combo.
  - Barra de salud del Custodio (jefe) con mayor dramatismo, cambio de color y temblor al entrar en Fase 2.

### G. Efectos, Partículas y Post-procesado
- **Diagnóstico:** En la versión nativa de escritorio se usan shaders de Bloom y CRT scanlines que en la versión Web fueron desactivados para evitar pérdidas de FPS.
- **Puntos a renovar:**
  - Crear efectos de resplandor mediante *blend surfaces* de Pygame (`BLEND_ADD` / `BLEND_RGBA_ADD`) pre-renderizadas o cacheadas, logrando un aspecto visual rico en antorchas y faroles tanto en escritorio como en la web sin penalización de rendimiento.
  - Refinar el sistema de partículas (`particulas.py`): Polvo de cripta flotante con movimiento browniano tenue, estelas translúcidas en el dash, salpicadura de ánimas turquesas y chispas metálicas en impactos contra la piedra.

---

## 3. LO QUE DEBES ENTREGAR

Actúa como Argon y genera un **Plan Maestro de Renovación Sensorial** detallado y estructurado en Markdown que contenga:

1. **Investigación y Fundamentos de Game Design:**
   - Cita principios reconocidos de diseño visual de videojuegos aplicados a plataformas 2D (Teoría del Valor/Luminancia de James Gurney, principios de Game Feel de Steve Swink, jerarquía de 3 planos en pixel art, feedback de 3 tiempos: Anticipación/Telegrafiado → Impacto/Clímax → Recuperación).
2. **Definición de Paleta y Contraste (Guía Cromática Gótica):**
   - Especificar códigos exactos de color (RGB/RGBA) para Fondo, Plano Medio, Enemigos (silueta + rim light + puntos focales) y Efectos.
3. **Estrategia de Ramas Git:**
   - Comando exacto para crear y aislar la nueva rama de trabajo (`art/overhaul-sensorial`) a partir del estado actual.
4. **Plan de Trabajo Paso a Paso (Fases 1 a 6):**
   - **Fase 1:** Reparación y conexión del subsistema de música en `juego.py` (Música por bioma, menú, transiciones de jefe con fade-in/fade-out).
   - **Fase 2:** Contraste y visibilidad de enemigos (incorporación de rim lighting, ojos brillantes y diferenciación contra el fondo).
   - **Fase 3:** Legibilidad de plataformas, suelos y profundidad de fondos (biseles superiores, textura de apoyo, capas de fondo atenuadas).
   - **Fase 4:** Modo Debug de Hitboxes/Hurtboxes (`F3`) y feedback de impacto (hit flash, chispas de pala, estelas alineadas).
   - **Fase 5:** Pulido estético del HUD y relicarios de interfaz.
   - **Fase 6:** Optimización y verificación (compatibilidad con WebAssembly en Pygbag y 51/51 tests en pytest).
5. **Directrices para Ejecución en Modo `/goal`:**
   - Guía explícita de "Qué NO hacer" y "Checklist de no-regresión" para que el agente ejecutor trabaje de forma autónoma sin descalibrar físicas ni introducir bugs.
