# IN CRYPTA
## Documento de diseño (GDD) y matriz MDA

**Equipo 6:** Ovelar Alejandro Ezequiel · Joaquín Cardiel Gomez · Jonathan Javier Pietracci  
**Materias:** Taller de Diseño Conceptual · Introducción a los Videojuegos  
**Género:** plataformas 2D de precisión, con estética gótica  
**Motor de prototipo:** Pygame (Python)  
**Motor de presentación:** GDevelop 5 (proyecto nativo de objetos y eventos)  
**Resolución:** diseño de 960 × 540 · build nativo de 1920 × 1080 · **Duración:** 8–12 minutos  
**Público:** estudiantes y jugadores con poca experiencia en plataformas, que aceptan un desafío de precisión creciente.  
**Tono:** gótico, nocturno, solitario y de escape.

---

## 1. High concept

> **IN CRYPTA** es un plataformero gótico 2D. Un sepulturero baja a la cripta a cumplir su jornada; la puerta se cierra detrás de él y la oscuridad despierta. Con su pala, su farol y un dash de sombra, debe cruzar el camposanto, la cripta y el osario para alcanzar el portón y escapar.

En una frase: **un plataformero de precisión donde un sepulturero escapa de su propia cripta usando salto, dash y pala.**

### Pitch breve

IN CRYPTA es un plataformero 2D de tres niveles hecho primero en Pygame y presentado en GDevelop. El jugador controla a un sepulturero atrapado entre la muerte y la oscuridad. Tiene tres acciones: salto de altura variable, dash de sombra y golpe descendente con la pala. Cada nivel enseña una combinación distinta y sube la dificultad en forma de sierra. La estética buscada es **Desafío** (dominio de la precisión) y **Sensación** (oscuridad, velocidad, partículas y sacudida de cámara). El prototipo está en Pygame; la versión de presentación es un proyecto nativo de GDevelop con objetos, eventos y comportamientos propios, renderizado a 1920 × 1080.

### Referencias

- **Blasphemous:** imaginería gótica, penitencia, pala como arma y mundo hostil.
- **Castlevania:** plataformas de precisión, criptas, velas, esqueletos y portones.
- **Ender Lilies:** atmósfera melancólica, siluetas oscuras, luz escasa y exploración lineal.

No es un *metroidvania*: no hay mapa interconectado ni habilidades que desbloqueen zonas. Es un plataformero lineal de tres niveles que homenajea esa estética y concentra el diseño en el movimiento.

---

## 2. Objetivos de diseño

1. Que el jugador **aprenda haciendo**, sin tutoriales largos.
2. Que las mecánicas se presenten escalonadas: salto y dash en el nivel 1, recogida de pala y ataque en el nivel 2, y las tres combinadas en el nivel 3.
3. Que fallar sea **legible y justo**: el jugador debe saber por qué perdió.
4. Que la experiencia se sienta **rápida y responsive** (coyote time, buffer de salto, dash con cooldown corto).
5. Que la oscuridad y la muerte se sientan **como una atmósfera**, no como una excusa para ocultar información.
6. Que el juego sea **presentable y verificable**: GDD, matriz MDA, pruebas automatizadas y una versión jugable en GDevelop.

---

## 3. Matriz MDA

MDA separa el juego en **Mecánicas** (reglas y acciones), **Dinámicas** (comportamiento que emerge al jugar) y **Estéticas** (respuestas emocionales). El diseñador trabaja de mecánicas hacia estéticas; el jugador vive el camino inverso.

### 3.1 Matriz principal: 3 mecánicas → 2 estéticas

| Mecánica | Dinámica fomentada | Estética principal | Cómo se manifiesta |
|---|---|---|---|
| **Salto de precisión** | Medir distancias, elegir el momento, corregir en el aire. | **Desafío** | Pozos de 3 tiles, plataformas escalonadas y saltos con altura variable. |
| **Dash de sombra** | Decidir cuándo gastar el impulso; cruzar pozos anchos; encadenar con el salto. | **Desafío + Sensación** | Estela turquesa, cooldown visible, sacudida leve y sonido de impulso en ambos builds. |
| **Golpe de pala (pisotón)** | Convertir al morador en recurso: atacar, rebotar, recuperar el dash y encadenar. | **Sensación + Desafío** | La pala se recoge en el nivel 2; `A` activa el sablazo y el pisotón elimina al morador. Partículas, rebote y sonido de impacto. |

### 3.2 Las tres mecánicas, en detalle

#### Mecánica 1: salto de precisión

- **Regla:** el jugador salta con `ESPACIO` en Pygame o `↑` en GDevelop. Si mantiene, sube más; si suelta, el salto se corta.
- **Ayudas invisibles:** `coyote time` (0,10 s) para saltar justo después de dejar una plataforma y `jump buffer` (0,12 s) para registrar un salto pedido un poco antes de aterrizar.
- **Propósito:** que el control se sienta justo y que el desafío esté en la lectura del espacio, no en pelear con el input.
- **Qué aprende el jugador:** distancia, altura y ritmo.

#### Mecánica 2: dash de sombra

- **Regla:** `SHIFT` en GDevelop o `SHIFT` / `X` en Pygame impulsa al sepulturero en la dirección en la que mira. Tiene 0,16 s de duración y 0,60 s de cooldown.
- **Regla adicional:** en el aire solo hay **un** dash disponible; se recupera al aterrizar o al golpear a un morador con la pala.
- **Propósito:** introducir una decisión de recurso y permitir pozos que un salto normal no cruza.
- **Qué aprende el jugador:** administrar el impulso y sincronizarlo con el salto.

#### Mecánica 3: golpe de pala (pisotón)

- **Regla:** la pala se recoge en una sala de La Cripta. Con la pala equipada, `A` ejecuta un sablazo; un pisotón desde arriba elimina al morador y recupera el dash aéreo (en Pygame además rebota). Sin pala, tocar a un morador hace daño y no hay pisotón.
- **Propósito:** convertir un obstáculo en una herramienta de movimiento. El morador deja de ser solo “peligro” y pasa a ser “plataforma”.
- **Qué aprende el jugador:** leer la altura, caer con intención y encadenar rebotes.

#### Recurso secundario: almas

- **Regla:** cada 10 almas otorgan **1 vida extra** (máximo 5). Al morir se reinician el contador y las almas del nivel; las vidas extra ya ganadas se conservan.
- **Propósito:** dar valor a la exploración opcional y ofrecer una red de seguridad sin quitar el desafío.
- **Qué aprende el jugador:** decidir si arriesga por una ruta con almas o si prioriza llegar al portón.

### 3.3 Las dos estéticas elegidas

| Estética | Definición de la cátedra | Cómo la construimos | Qué NO buscamos |
|---|---|---|---|
| **Desafío** | El jugador toma decisiones significativas para superar obstáculos y ganar maestría; los retos suben con el tiempo. | Niveles con pozos, plataformas, pinchos y moradores; dificultad en sierra; reinicio rápido. | Castigo arbitrario, muertes por información oculta. |
| **Sensación** | Diversión derivada de los sentidos: respuesta visual, auditiva y táctil. | Partículas, estela de dash, sacudida de cámara, flash de daño, SFX en ambos builds y HUD claro. | Exceso de efectos que tape la lectura del nivel. |

### 3.4 Las otras seis estéticas (cobertura conceptual)

| Estética | Presencia en IN CRYPTA | Comentario |
|---|---|---|
| Compañerismo | Ausente | Es un juego single-player; la soledad es parte del tono. |
| Fantasía | Secundaria | Hay un sepulturero, una cripta y moradores; la ficción sostiene la atmósfera, no una épica extensa. |
| Narrativa | Secundaria | La historia se cuenta con el escenario, los nombres y el portón final; no hay diálogos. |
| Descubrimiento | Secundaria | Almas opcionales en rutas altas y riesgosas; cada 10 se canjean por una vida extra. |
| Expresión | Muy baja | No hay personalización; el jugador se expresa en cómo resuelve. |
| Sumisión | Ausente | El juego pide atención y precisión; no es relajante. |

La decisión de elegir **dos** estéticas principales es deliberada: un juego pequeño y coherente se diseña mejor con pocas emociones fuertes que con ocho emociones tibias.

### 3.5 Dinámicas fomentadas e inesperadas

**Fomentadas**
- Saltar, dashar y golpear con la pala en una misma secuencia.
- Arriesgar para agarrar almas sobre un pozo y canjear 10 por una vida extra.
- Usar al morador como rebote para llegar a una plataforma alta.
- Repetir un tramo para mejorar el tiempo.

**Inesperadas posibles**
- Usar el dash para “cancelar” la caída y llegar a lugares no previstos.
- Encadenar golpes de pala para mantener el dash aéreo y saltar secciones.
- Descubrir que el dash también sirve para cruzar un pozo sin saltar (si se toma impulso desde el borde).

---

## 4. Bucle de juego

```
Explorar → leer el obstáculo → saltar / dashar → golpear o recoger almas
   ↑                                                    ↓
   └────── feedback (partículas, sacudida, sonido) ←──────┘
                          ↓
                 llegar al portón → siguiente nivel
```

**Bucle de 30 segundos:** saltar una lápida, cruzar un pozo, golpear a un morador y recoger un alma.  
**Bucle de nivel:** aprender la mecánica nueva, practicarla segura, juntar 10 almas para una vida extra y llegar al portón.  
**Bucle de juego:** tres niveles, dificultad en sierra, victoria al escapar de la cripta.

---

## 5. Niveles y curva de dificultad

| Nivel | Nombre | Mecánica que enseña | Reto principal | Enemigos | Almas | Pinchos | Estética dominante |
|---|---|---|---|---|---|---|---|
| 1 | **El Camposanto** | Salto y dash | Pozos cortos (3 tiles), pinchos y moradores; todavía no hay pala. | 3 | 17 | 4 | Desafío suave |
| 2 | **La Cripta** | Dash + recogida de pala | Abismos anchos, primer ataque y plataformas móviles horizontales/verticales. | 5 | 18 | 4 | Desafío + Sensación |
| 3 | **El Osario** | Combinación de las tres | Pozos, pinchos, plataformas móviles y moradores en el camino; la pala ya está equipada. | 11 | 25 | 5 | Desafío + Sensación |

Todos los niveles miden 18 filas de alto. El Camposanto mide 80 columnas; La Cripta, 100; El Osario, 184. La Cripta y El Osario refuerzan la sensación de encierro con arcos, muros y plataformas suspendidas.

### 5.1 Curva en sierra

```
Dificultad
    │        ╱╲ nivel 2        ╱╲ nivel 3
    │   ╱╲  ╱  ╲      ╱╲     ╱  ╲
    │  ╱  ╲╱    ╲    ╱  ╲   ╱    ╲
    │ ╱ nivel 1  ╲  ╱    ╲ ╱      ╲
    │╱             ╲╱      ╲        ╲
    └──────────────────────────────── Tiempo
      presentar  practicar  exigir  combinar  dominio
```

Cada nivel baja un poco la presión al presentar la mecánica nueva y después la sube. El nivel 2 enseña el dash con pozos anchos y una pista visible; el nivel 3 ya no explica: combina.

### 5.2 Progresión de las cinco etapas

| Etapa | Nivel 1 | Nivel 2 | Nivel 3 |
|---|---|---|---|
| Presentación | Salto y dash; sin pala. | Dash, recogida de pala y ataque. | Las tres mecánicas juntas; pala equipada. |
| Práctica segura | Plataformas bajas, moradores aislados. | Primer abismo con pista y almas guía. | Tramos conocidos con más altura. |
| Exigencia aislada | Pozos de 3 tiles. | Abismos anchos y plataformas móviles. | Pozos, pinchos y plataformas con moradores. |
| Combinación | Salto + dash. | Dash + pala + plataformas. | Salto + dash + pala + plataformas. |
| Dominio | Llegar al portón sin pala. | Recoger la pala y cruzar sin caer. | Escapar del osario. |

### 5.3 Tipos de desafío

| Tipo | Presencia | Ejemplo |
|---|---|---|
| **Mecánico** | Alta | Timing del salto y del dash; golpe de pala. |
| **Cognitivo** | Media | Leer la altura de una plataforma y decidir si conviene el dash. |
| **Estratégico** | Media | Gastar el único dash aéreo antes o después del salto. |
| **Percepción** | Media | Ver la estela del dash, el HUD y la posición de los moradores. |

### 5.4 Desafío justo vs. injusto

| Justo en IN CRYPTA | Injusto (evitado) |
|---|---|
| El pozo se ve antes de saltar. | Enemigo que aparece sin aviso sobre el jugador. |
| El dash tiene estela y barra de estado. | Cooldown invisible. |
| El golpe de pala se puede intentar y fallar. | Muerte instantánea sin feedback. |
| El jugador reaparece en el inicio del nivel; el contador y las almas se reinician, pero conserva las vidas extra ganadas. | Perder todo el progreso por un error. |
| La dificultad sube combinando mecánicas. | Aumentar solo la velocidad o la vida de los enemigos. |
| Los pinchos tienen una base y un brillo rojo. | Trampas invisibles o mimetizadas con el fondo. |

### 5.5 Ajustes invisibles usados

- **Coyote time:** 0,10 s.
- **Jump buffer:** 0,12 s.
- **Hitbox del jugador:** 24 × 30, más chica que la sensación visual.
- **Pisotón:** en Pygame, rebote de 360 px/s; en GDevelop nativo, elimina al morador y restaura el dash aéreo.
- **Dash:** 0,60 s de cooldown, pero se recupera al golpear con la pala.
- **Reaparición:** reinicia el contador y las almas del nivel para evitar farmeo; las vidas extra ya ganadas se conservan.
- **Invulnerabilidad:** breve ventana después del daño para evitar perder todas las vidas en un solo contacto.

---

## 6. Juegos como sistemas

### 6.1 Componentes del sistema IN CRYPTA

| Componente | En IN CRYPTA |
|---|---|
| **Objetos** | Sepulturero, moradores, almas, portón, bloques, pinchos, decoraciones. |
| **Atributos** | Posición, velocidad, vidas, almas, almas para la próxima vida, cooldown de dash, altura, tiempo. |
| **Relaciones** | Colisiones, golpe de pala, recolección, meta, daño, transición de nivel. |
| **Entorno** | Tres mapas ASCII de 80 × 18, 100 × 18 y 184 × 18 tiles; temas camposanto, cripta y osario. |
| **Reglas** | Física, salto, dash, pala, vidas, pinchos, transición de nivel. |
| **Resultados** | Nivel completado, victoria, derrota, cantidad de almas, vidas extra ganadas, tiempo. |

### 6.2 Feedback loops

**Loop positivo (reforzante):**

```
Golpe de pala → rebote → recupero el dash → cruzo un pozo → llego a un alma
   ↑                                                              ↓
   └────────────────────── más confianza y velocidad ←────────────┘
```

El jugador que domina la pala se vuelve más rápido y se anima a arriesgar más.

**Loop negativo (regulador):**

```
Recibir daño → invulnerabilidad breve → retroceder al inicio
   ↑                                           ↓
   └────────── bajar la velocidad y volver a leer ←──┘
```

El daño no expulsa al jugador del juego: lo frena y lo obliga a releer el tramo. Al perder la última vida, el estado de derrota ofrece reiniciar.

### 6.3 Meaningful play

| Criterio | Cómo se cumple |
|---|---|
| **Discernible** | Cada acción tiene feedback inmediato: partículas, rebote, flash, cambio de HUD o sonido. |
| **Integrado** | El dash cambia la posición, la pala elimina un morador y recupera el dash, y cada 10 almas convierten el riesgo en una vida extra. |

Si el jugador aprieta dash y no pasa nada, no hay meaningful play. En IN CRYPTA el dash tiene estela, desplazamiento, estado en el HUD y sonido. El jugador ve que su decisión afectó al sistema.

---

## 7. UI/UX

### 7.1 Tipos de interfaz usados

| Tipo | En IN CRYPTA | Función |
|---|---|---|
| **No diegética** | HUD superior con nivel, almas, progreso a vida extra, vidas, tiempo y dash. | Información que solo ve el jugador. |
| **Diegética** | El portón como meta visible; las velas y el farol del sepulturero. | El objetivo y la luz pertenecen a la ficción. |
| **Espacial** | La estela del dash y las partículas están en el espacio del juego. | Informan sin menús. |
| **Meta** | Flash rojo al recibir daño y sacudida de cámara. | Simulan la sensación del impacto. |

### 7.2 Los cinco principios de UX aplicados

| Principio | Aplicación |
|---|---|
| **Facilidad para encontrar lo importante** | El HUD está siempre arriba; el dash tiene barra propia; las almas se leen en dorado. |
| **Rapidez para entender qué hacer** | La pista inicial aparece 5 segundos y desaparece; el nivel se lee solo; el portón brilla. |
| **Comodidad según la plataforma** | GDevelop: flechas, `SHIFT`, `A` (tras recoger la pala), `ENTER`, `ESC`. Pygame: flechas/A-D, `ESPACIO`, `SHIFT`/`X`, `P`, `R`, `M`. |
| **Consistencia** | Mismo HUD, mismos colores y mismos overlays en los tres niveles. |
| **Fluidez** | Pausa inmediata con `ESC` en GDevelop o `P` en Pygame; menú de reinicio sin pasos profundos. |

### 7.3 Decisiones de UI/UX

- El HUD usa **barra superior semitransparente** para no tapar el juego.
- La pista se muestra **arriba**, debajo del HUD, para no tapar al jugador.
- El dash se comunica con **texto + barra**: “DASH LISTO” o “DASH…”.
- Las vidas se muestran como **hasta cinco corazones**; las almas, como contador con progreso a vida extra cada 10.
- Al quedar una sola vida, aparece un aviso pulsante de **última vida**; no bloquea la acción ni tapa el juego.
- La pantalla de título presenta el nombre, el subtítulo, el equipo, las referencias y la acción principal.
- Los overlays de pausa, derrota y victoria son claros y ofrecen una sola acción principal.
- El estado de invulnerabilidad se comunica con parpadeo, no con texto.

---

## 8. Sensación y game feel

| Acción | Feedback visual | Feedback sonoro | Feedback de cámara |
|---|---|---|---|
| Salto | Polvo y chispas blancas | Tono ascendente | Ninguno |
| Dash | Estela turquesa y fantasmas | Barrido cuadrado | Sacudida leve |
| Golpe de pala | Explosión roja/amarilla | Golpe grave | Sacudida media |
| Daño | Flash rojo y partículas | Tono descendente | Sacudida fuerte |
| Alma | Destello dorado y estela | Tono agudo | Ninguno |
| Recoger pala | Destello de la pala | Tono metálico ascendente | Ninguno |
| Vida extra | Destello dorado y aviso en el HUD | Arpegio ascendente | Ninguno |
| Pausa / UI | Cambio de overlay o menú | Click seco | Ninguno |
| Portón | Explosión multicolor | Acorde ascendente | Ninguno |

La estética **Sensación** no es decoración: cada efecto confirma una acción y ayuda a leer el estado del juego. Ambos builds suman sonido; el nativo usa SFX WAV y el prototipo Pygame, sonidos procedurales.

---

## 9. Narrativa y fantasía

El sepulturero baja a la cripta a cumplir su jornada. La puerta se cierra detrás de él; la oscuridad despierta y los moradores ocupan el camposanto. No hay diálogos ni cinemáticas: la historia se cuenta con el título, los nombres de los niveles, las lápidas, las velas, los huesos y el portón final. Es una **fantasía mínima** al servicio del desafío y la sensación.

- **El Camposanto:** el mundo exterior, la luna y las tumbas; todavía hay cielo.
- **La Cripta:** el encierro, las columnas, las velas y los primeros pinchos.
- **El Osario:** el descenso final; huesos, costillas y la salida.

El farol del sepulturero es el motivo visual de la luz que se resiste a apagarse. El portón es la promesa de escape.

---

## 10. Público y accesibilidad

- **Público primario:** estudiantes que están aprendiendo diseño y jugadores ocasionales.
- **Público secundario:** jugadores de plataformas que buscan un reto corto y una atmósfera gótica.
- **Accesibilidad:** controles simples, sin combinaciones de botones; pausa; reinicio desde el menú; feedback visual redundante y SFX. El prototipo Pygame permite silenciar el audio con `M`.
- **Dificultad:** no hay selector. La curva está diseñada para que el nivel 1 sea accesible y el nivel 3 exija dominio. El objetivo es que cualquier persona pueda terminar el nivel 1 y que un jugador con experiencia disfrute el 3.
- **Límites:** no hay remapeo de teclas ni opciones de contraste; la paleta oscura es parte de la propuesta. Son mejoras posibles, no promesas de esta entrega.

---

## 11. Producción

### 11.1 Alcance

| Entregable | Estado |
|---|---|
| Prototipo Pygame de 3 niveles | Completo |
| Documento GDD + MDA | Completo |
| Proyecto GDevelop nativo (6 escenas) | Completo y validado headless; falta vista previa real |
| Build HTML5 de 1920 × 1080 | Completo |
| Runtime JavaScript y export JSON legados | Conservados como versión anterior |
| Pruebas de lógica y runtime | 21 pruebas Python + validación headless con Chromium/CDP |
| Capturas del título y de los 3 niveles | Completo |
| Boss final (diseño) | Documentado en la sección 14; no implementado |

### 11.2 Equipo y tareas (versión de cátedra)

| Rol | Tarea |
|---|---|
| Diseño | MDA, niveles, curva, UI/UX, narrativa. |
| Programación | Física, dash, pala, cámara, partículas, parser. |
| Arte | Paleta gótica, siluetas, decoraciones, HUD, pantalla de título. |
| Audio | Sonidos procedurales en Pygame y SFX WAV en el build nativo. |
| QA | Pruebas headless, pruebas de pozo, pruebas de runtime. |
| Producción | GDD, pitch, guion de presentación, instalador. |

### 11.3 Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| El dash hace trivial el juego | Pozos anchos, cooldown y un solo uso aéreo. |
| El jugador no entiende el dash | Pista, estela, barra y pozo de práctica. |
| La oscuridad oculta obstáculos | Contraste, brillo en pinchos y portón, pista visible. |
| Una instancia abierta de GDevelop exporta el proyecto viejo | Cerrar GDevelop antes de exportar por CLI y revisar `build/data.js`. |
| El navegador bloquea o demora el audio | Los SFX se cargan on demand; el feedback visual sigue funcionando aunque falle el sonido. |
| Pérdida de progreso por muerte | Al reaparecer se reinician el contador y las almas del nivel; las vidas extra ya ganadas se conservan y el farmeo no es posible. |

### 11.4 Pruebas

- `tests/test_logica.py`: **21 pruebas** de niveles, parser, gravedad, salto, dash, pozo de dash, primer salto de La Cripta, almas, vida extra, reset de almas, enemigos, cámara, estados, meta, pala, contacto, límites, plataformas, vidas, reinicio, título, pinchos y juego headless.
- `tools/generar_proyecto_nativo.py`: regenera el proyecto GDevelop nativo, sus assets 2x y las seis escenas.
- Build nativo validado con Chromium/CDP: título, los tres niveles, salto, dash, audio, recogida de pala, ataque, pisotón, daño sin pala, pozo, límites, plataformas móviles, game over y transiciones, a 1920 × 1080. También se verificaron el progreso a vida extra, el aviso de última vida y los SFX `SFX_PalaRecoger`, `SFX_Vida` y `SFX_UI`.
- `tests/test_runtime_gdevelop.js`: prueba del runtime JavaScript legado; no corresponde al build nativo.
- `tools/export_gdevelop.py --check`: valida el JSON y la reconstrucción de los tres niveles para la versión legada.
- `tools/capturar.py`: genera `capturas/titulo.png` y las capturas de los tres niveles del prototipo.

Comandos:

```bash
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python tests/test_logica.py

PYTHONPATH=. .venv/bin/python tools/generar_proyecto_nativo.py

node tests/test_runtime_gdevelop.js
```

---

## 12. Mapa de conceptos — Taller de Diseño Conceptual

| Concepto | Dónde aparece en IN CRYPTA |
|---|---|
| **UI** | HUD, barra de dash, corazones, overlays, pistas. |
| **UX** | Pista breve, controles simples, feedback inmediato, reinicio rápido. |
| **UI no diegética** | HUD superior. |
| **UI diegética** | Portón como objeto del mundo; velas y farol. |
| **UI espacial** | Estela y partículas en el espacio del nivel. |
| **UI meta** | Flash de daño y sacudida de cámara. |
| **Dificultad** | Relación entre lo que el nivel pide y lo que el jugador puede hacer. |
| **Desafío mecánico** | Timing de salto, dash y pala. |
| **Desafío cognitivo** | Leer la altura y elegir la secuencia. |
| **Desafío estratégico** | Administrar el único dash aéreo. |
| **Desafío de percepción** | Leer el HUD, la estela y los moradores. |
| **Público objetivo** | Estudiantes y jugadores ocasionales. |
| **Curva de dificultad** | Tres niveles con subidas y bajadas. |
| **Sierra de dificultad** | Cada nivel presenta una mecánica y luego la exige. |
| **Etapas de progresión** | Presentación, práctica, exigencia, combinación, dominio. |
| **Desafío justo** | Pozos visibles, feedback, reaparición con almas reiniciadas y vidas extra conservadas. |
| **Dificultad artificial vs. diseñada** | No se sube solo la velocidad; se combinan mecánicas. |
| **Ajustes invisibles** | Coyote time, jump buffer, hitbox, rebote generoso. |
| **Feedback audiovisual** | Partículas, sonidos, flash, sacudida, HUD. |
| **MDA: mecánicas** | Salto, dash, pala. |
| **MDA: dinámicas** | Encadenar, arriesgar, rebotar, optimizar. |
| **MDA: estéticas** | Desafío y Sensación. |
| **8 tipos de diversión** | Se eligen 2 principales y se justifican las otras 6. |
| **Juegos como sistemas** | Objetos, atributos, relaciones, entorno, reglas, resultados. |
| **Definiciones de juego** | IN CRYPTA cumple las definiciones de Huizinga, Crawford y Salen/Zimmerman. |
| **Meaningful play** | Discernible e integrado en cada acción. |
| **Feedback loops** | Pala → dash → alma; daño → invulnerabilidad → releer. |

---

## 13. Mapa de conceptos — Introducción a los Videojuegos

| Concepto | Dónde aparece en IN CRYPTA |
|---|---|
| **Definición de juego (RAE)** | Actividad recreativa con objetivo y reglas: escapar de la cripta. |
| **David Jones** | Resolución de problemas con actitud lúdica: leer y resolver cada tramo. |
| **Jesse Schell** | “Físicas del mundo real moldeadas y puestas en una caja”: física de plataformas. |
| **Johan Huizinga** | Actividad libre, separada, incierta, no productiva, regulada y ficticia. |
| **Roger Caillois** | IN CRYPTA entra en **agon** (competencia contra el obstáculo) e **ilinx** (vértigo del dash). |
| **Paidia / ludus** | El juego es más **ludus** que paidia: reglas claras y desafío medido. |
| **Categorías de juego** | Agon por el desafío; ilinx por la velocidad; poca presencia de alea y mimicry. |
| **Género** | Plataformas 2D, subgénero de acción, con estética gótica. |
| **Géneros principales** | Acción y plataformas; se toma la precisión y el avance por escenarios. |
| **Géneros notables** | Se evitan RPG, estrategia, simulación y deportes para mantener el alcance. |
| **Clasificación de géneros** | El juego se reconoce por sus mecánicas básicas: correr, saltar, dashar y llegar a la meta. |
| **Historia: Brown Box / Odyssey** | La paleta y la simplicidad de controles homenajean los primeros videojuegos domésticos. |
| **Spacewar / PDP-1** | El movimiento y el rebote recuerdan la física simple de los primeros arcades. |
| **ARPANET / cultura open source** | El proyecto se distribuye como código y assets abiertos (Pygame, proyecto GDevelop). |
| **Consolas y limitaciones** | La estética pixel art y la paleta reducida dialogan con las limitaciones técnicas de 8 bits. |
| **Género y evolución** | El plataformero evoluciona al agregar dash y pala como mecánicas combinadas. |
| **Proceso creativo** | Idea: “un sepulturero atrapado en su propia cripta”; inspiración en Blasphemous, Castlevania y Ender Lilies. |
| **Concepto** | Se separó en gráficos, interfaz, historia, diseño de niveles, mecánicas y sonido. |
| **High concept** | Un sepulturero cruza tres niveles de una cripta para escapar. |
| **Pitch** | Este documento y el guion de presentación. |
| **GDD** | Este documento. |
| **Proceso de producción** | Lista de componentes, tareas, pruebas y entregables. |
| **Motores gráficos** | Pygame para prototipo; GDevelop para presentación. |
| **GDevelop** | Motor de presentación; proyecto nativo de objetos, eventos y comportamientos. |

---

## 14. Boss final: El Custodio del Osario

> **Diseño propuesto, no implementado en el build actual.** Se documenta como ampliación posible para cerrar la fantasía del juego sin agregar mecánicas nuevas.

### 14.1 Concepto

El **Custodio del Osario** es el primer sepulturero de la cripta: un cuerpo hueco con la pala rota y el farol incrustado entre las costillas. No ataca por maldad; se quedó cuidando una puerta que nunca se animó a cruzar. El jugador debe **enterrar su propio eco** para salir. El boss funciona como el examen final de las tres mecánicas: saltar, dashar y pisar.

### 14.2 Arena y lectura

- Una sola pantalla plana, sin pozos, para que la dificultad sea el patrón y no la caída.
- Dos losas bajas en los extremos; el portón queda sellado detrás del jugador.
- La luz de las velas se apaga por fases: el escenario se vuelve más oscuro, pero nunca ilegible.
- Sin enemigos adicionales: el combate se lee completo en una pantalla.

### 14.3 Fases y ataques

| Fase | Nombre | Patrón | Ventana de castigo |
|---|---|---|---|
| 1 | **La campanada** | Camina lento, levanta la pala y golpea el suelo; una onda de huesos recorre el piso hacia ambos lados. | Tras el golpe queda de rodillas 1,3 s con el cráneo expuesto. |
| 2 | **El cortejo** | Toca la campana, se abalanza dos veces de un extremo al otro y queda aturdido contra el muro. | Al frenar, 0,9 s: se puede saltar y pisar el cráneo. |
| 3 | **La última palada** | El farol se apaga; da tres golpes cada vez más rápidos y uno final en el centro. | Queda de rodillas 1,8 s, con una luz dorada que señala el cráneo. |

Cada fase se anuncia con una campanada grave, polvo y una pausa breve. **Todas las amenazas tienen al menos 0,5 s de anticipación** y se ven antes de golpear.

### 14.4 Cómo se vence

- **Pygame:** saltar o dashar sobre las ondas y caer con pisotón sobre el cráneo expuesto. No hace falta un ataque nuevo.
- **GDevelop nativo:** el pisotón es la vía principal; el ataque con `A` permite un castigo más rápido, pero no es obligatorio.
- El boss no tiene barra de vida convencional: tiene **tres segmentos de voluntad**, uno por fase. Cada fase pide dos o tres castigos limpios.
- Si se implementa, la puerta del boss funciona como punto de reintento para no repetir todo El Osario.

### 14.5 Feedback audiovisual

- **Anticipación:** brillo rojo en la pala y sonido de arrastre.
- **Impacto:** sacudida media, polvo de hueso y un golpe grave.
- **Fase:** campanada descendente, el farol parpadea y el HUD cambia de segmento.
- **Vulnerabilidad:** luz dorada en el cráneo y tono ascendente; el jugador sabe cuándo atacar sin leer texto.
- **Derrota:** el Custodio se deshace en ceniza, el portón se abre y vuelve la luz del amanecer.

### 14.6 Por qué encaja

- **Castlevania:** el boss es un examen de movimiento; se puede vencer sin daño si se leen los patrones.
- **Blasphemous:** la forma comunica la función; la pala, el farol y el cráneo dicen qué va a pasar.
- **Ender Lilies:** la soledad y la melancolía sostienen el combate; no se resuelve con agregados ni con una nube de enemigos.
- **Alcance:** una entidad, tres ataques, una arena y una barra de tres segmentos. No requiere mecánicas nuevas.

---

## 15. Lo que queda afuera

- Multijugador y compañerismo.
- Narrativa extensa o diálogos.
- Personalización y expresión.
- Niveles generados proceduralmente.
- Arte dibujado a mano: se usan formas geométricas y partículas.
- Mapa interconectado tipo metroidvania.

Estas ausencias son decisiones de alcance, no olvidos: permiten terminar un juego coherente y verificable en el marco de la cursada.

---

## 16. Cierre

IN CRYPTA demuestra que un plataformero pequeño puede cubrir MDA, UI/UX, curva de dificultad, sistemas, meaningful play, definiciones de juego, géneros, historia y producción. Las tres mecánicas son pocas, pero se combinan; las dos estéticas son claras, pero se refuerzan; la versión Pygame permite iterar y la versión GDevelop permite presentar. La oscuridad no oculta el diseño: lo vuelve el centro de la experiencia.
