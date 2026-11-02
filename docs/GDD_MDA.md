# IN CRYPTA
## Documento de Diseño de Videojuego (GDD) y Matriz MDA — Versión Definitiva 1.0.0

**Equipo 6:** Ovelar Alejandro Ezequiel · Joaquín Cardiel Gomez · Jonathan Javier Pietracci  
**Materias:** Taller de Diseño Conceptual · Introducción a los Videojuegos (UNAHUR)  
**Género:** Plataformas 2D de precisión con combate táctico y estética gótica  
**Motor de juego:** Python 3 + `pygame-ce` (Arquitectura procedimental vectorial, 60 FPS estables)  
**Resolución y Cámara:** Viewport virtual de 1024 × 576 escalado con zoom 1.25× a 1280 × 720 (anclaje inferior de suelo sin vacío negro)  
**Duración estimada:** 12–18 minutos  
**Público objetivo:** Jugadores de plataformas que buscan precisión, atmósfera gótica envolvente y curvas de aprendizaje justas.  
**Tono:** Gótico, opresivo, solitario, ritual y de escape penitente.

---

## 1. High Concept & Visión Creativa

> **IN CRYPTA** es un plataformero gótico 2D de precisión. Un sepulturero queda sepultado en las profundidades de un camposanto profanado al sellarse las rejas tras de él. Armado únicamente con su pala de hierro —que luego consagrará como guadaña mística—, un farol mortuorio y un veloz dash de sombras, deberá atravesar las tumbas del Camposanto, escalar los arcos de La Cripta y superar los abismos del Osario para derrotar al Custodio ancestral y cruzar el portón hacia la redención.

### 1.1 En una frase
*Un plataformero de precisión y combate ágil donde un sepulturero escapa de una necrópolis subterránea dominando el salto de altura variable, el dash espectral, el sablazo de pala y el rebote aéreo por pisotón.*

### 1.2 Referencias artísticas y lúdicas
- **Blasphemous (The Game Kitchen):** Imaginería religiosa gótica, penitencia, relicarios de hierro y oro, la pala/guadaña como herramienta litúrgica y combate contundente.
- **Castlevania: Symphony of the Night / Aria of Sorrow (Konami):** Arquitectura de criptas de piedra tallada, arcos góticos, ventanales de rejas, portones con goznes forjados y combate contra jefes con lectura estricta de patrones.
- **Ender Lilies: Quietus of the Knights / Celeste:** Atmósfera melancólica, partículas espectrales flotantes, zoom cinematográfico, coyote time, jump buffering y control ultra responsivo.

---

## 2. Pilares de Diseño

1. **Aprender mediante la arquitectura (Diseño Invisible):** Los niveles introducen mecánicas orgánicamente a través de su geometría, sin tutoriales intrusivos ni pausas artificiales.
2. **Control responsivo y benévolo:** Asistencias invisibles de entrada (100 ms de coyote time, 120 ms de jump buffer, corner nudge en bordes y caída flotante al cortar salto).
3. **Mundo coherente y diegético:** Fondos multicapa con parallax (cielo nocturno, luna craterizada con halo, tumbas lejanas, arquerías góticas y cadenas oscilantes) anclados al suelo para eliminar espacios vacíos.
4. **Legibilidad y justicia absoluta:** Ningún peligro aparece por sorpresa; cada ataque enemigo y del jefe posee al menos 500 ms de anticipación visual y sonora telegrafiada.
5. **HUD gótico diegético:** Información presentada en relicarios heráldicos de hierro envejecido, filigrana de oro y rubíes carmesí, evitando barras genéricas escolares.

---

## 3. Matriz MDA (Mechanics, Dynamics, Aesthetics)

El marco MDA desglosa el sistema lúdico en tres capas interconectadas:

```
   DISEÑADOR  ──►  [ MECÁNICAS ]  ──►  [ DINÁMICAS ]  ──►  [ ESTÉTICAS ]  ◄──  JUGADOR
                     (Reglas)           (Sistemas)          (Emociones)
```

### 3.1 Mecánicas Fundamentales

| Mecánica | Entrada | Propiedades del Sistema | Feedback Audiovisual |
|---|---|---|---|
| **Salto de Precisión** | `ESPACIO` / `W` / `↑` | Altura variable (impulso inicial -420 px/s; gravedad 980 px/s²; corte a 0.5× al soltar). Coyote time: 0.10 s; Jump buffer: 0.12 s. | Chispas de polvo blanquecino en los pies; tono sonoro ascendente. |
| **Dash de Sombra** | `SHIFT` / `X` | Desplazamiento horizontal instantáneo a 520 px/s durante 0.16 s. Cooldown de 0.60 s. Un solo uso aéreo recargable al tocar suelo o pisar enemigo. | Estela espectral turquesa con clones residuales (`ghosting`), zumbido eólico y sacudida leve de cámara. |
| **Golpe de Pala / Guadaña** | `Z` / `J` | Sablazo frontal (rango 46 px con pala; 72 px con Guadaña Mística en Nivel 3). Cooldown de 0.28 s. Destruye moradores melee, cuervos y arañas. | Arco cortante relampagueante (plateado o púrpura místico), chispas doradas/carmesí, sacudida media y sonido de impacto. |
| **Pisotón Aéreo (Stomp)** | Caer sobre un enemigo | Al impactar la cabeza de un enemigo desde arriba mientras `vy > 0`, se elimina la entidad, se otorga rebote vertical ascendente (-360 px/s) y se restaura el dash aéreo. | Explosión radial de esquirlas, sacudida de pantalla y sonido de percusión ósea. |
| **Relicario de Ánimas** | Recoger gemas celestes | Cada 10 almas espectrales se consagra un corazón extra de salud (máximo 5 vidas). Contador se reinicia al morir para evitar farmeo abusivo. | Destello lumínico celeste, partícula estelar y repique litúrgico ascendente. |
| **Pacto del Farol (3 Tiers)** | Contacto con Farol (`F`) | Consagra las almas del tramo acumuladas. Tier 1 (1 alma): Checkpoint fijado. Tier 2 (3 almas): **Manto del Farol** (aura celeste que absorbe 1 impacto letal). Tier 3 (6 almas): **Filo de Ánima** (+12 px alcance de ataque) + Manto. | Llama azul progresiva en el farol; destello periférico celeste; acordes litúrgicos ascendentes. |
| **Losa Quebradiza (`~`)** | Pisar baldosa inestable | Baldosa de roca húmeda que vibra con advertencia táctil y sonora durante 0.40 s antes de colapsar. Permanece destruida por 2.5 s y se reconstruye sola. | Vibración vertical oscilante (`bobbing`); crujido de piedra fracturada y partículas de esquirlas. |
| **Campana de Resonancia (`I`)** | Golpe aéreo de pala/guadaña | Incensario o campana suspendida. Al golpearla en el aire genera rebote vertical ascendente (`vy = -440 px/s`) y **recarga instantáneamente el dash aéreo**. | Tañido broncíneo profundo, destello de ondas concéntricas y chispas doradas en el punto de impacto. |

### 3.2 Dinámicas Emergentes
- **Encadenamiento Aéreo Pogo-Dash:** El jugador salta un abismo con pinchos, ejecuta un dash horizontal, cae con pisotón sobre un cuervo espectral, rebota ganando altura, recupera su dash aéreo y cruza un segundo abismo inalcanzable de otra forma.
- **Riesgo vs. Recompensa en Rutas de Ánimas:** Rutas alternativas elevadas y angostas ofrecen almas para ganar vidas adicionales antes del combate del Custodio, desafiando al jugador experimentado a medir sus saltos.
- **Castigo Telegrafiado en Combate:** En la fase 2 del Custodio, la pala rebota con chispas metálicas sin dañarlo; el jugador debe memorizar el patrón de carga furiosa, saltar la triple onda expansiva y caer en pisotón justo sobre su corona.

### 3.3 Estéticas Predominantes
1. **Desafío (Challenge):** Satisfacción visceral al dominar saltos de precisión milimétrica, timing de esquivas y el combate del jefe final sin recibir daño.
2. **Sensación (Sensation):** Placer multisensorial provisto por el arte procedural vectorizado, el contraste entre sombras oscuras y destellos carmesí/turquesa, la sacudida de cámara por impactos y el latido del corazón en salud crítica.
3. **Fantasía (Fantasy) & Atmósfera:** El ritual sombrío de un sepulturero penitente abriéndose paso a través de criptas ancestrales iluminadas por antorchas parpadeantes.

---

## 4. Arquitectura de Niveles y Curva de Dificultad

El juego está compuesto por 3 niveles extensos y diseñados meticulosamente en formato ASCII sobre grillas de baldosas de 32 × 32 px:

> [!IMPORTANT]
> **Regla de Progresión de Longitud:** `Longitud(Nivel 1) < Longitud(Nivel 2) < Longitud(Nivel 3)`.  
> El **Nivel 1 (El Camposanto)** marca la extensión y el estándar de escala de la experiencia. A partir de su cierre definitivo, cada nivel subsiguiente debe ser obligatoriamente más largo que el anterior (`Nivel 2` superará en longitud a `Nivel 1`, y `Nivel 3` superará a `Nivel 2`), acentuando la sensación de travesía descendente cada vez más profunda y desafiante.

```
 Dificultad
     │                                                     [FASE II]
     │                                                 ╱╲   Custodio
     │                                   [VENTANA]    ╱  ╲  triple onda
     │                     ╱╲           Pared vertical ╱    ╲
     │        ╱╲          ╱  ╲             con pinchos
     │       ╱  ╲        ╱    ╲          ╱╲
     │      ╱    ╲  ╱╲  ╱      ╲        ╱  ╲
     │     ╱      ╲╱  ╲╱        ╲  ╱╲  ╱    ╲
     │    ╱                      ╲╱  ╲╱      ╲
     └────────────────────────────────────────────── Progresión
          NIVEL 1: CAMPOSANTO    NIVEL 2: LA CRIPTA    NIVEL 3: EL OSARIO
```

### 4.0 Prólogo: El Ritual del Sepulturero (70 columnas × 12 filas)
- **Tema:** Santuario subterráneo ancestral de iniciación (tema Cripta).
- **Propósito:** Aprendizaje guiado y orgánico de las mecánicas esenciales sin interrumpir la inmersión.
- **Estructura en 5 Cámaras:**
  1. *El Despertar (cols 0–14):* Movimiento bidireccional y salto de altura variable con escalón de piedra y ánimas sobre suelo llano.
  2. *El Foso del Dash (cols 15–31):* Foso de 7 baldosas con arco parabólico de almas que exige saltar y ejecutar el Dash de Sombra (`SHIFT`) en el aire.
  3. *El Altar de Hierro (cols 32–46):* Consagración de la Pala (`W`) y combate frontal con golpe de sablazo (`Z` / `J` / Click) contra morador patrullero.
  4. *El Pisotón Aéreo (cols 47–59):* Cornisa elevada sobre morador; enseña el Pisotón (stomp) vertical que destruye al enemigo, genera rebote ascendente y **recarga el dash aéreo** para alcanzar la saliente superior sobre el foso de pinchos.
  5. *El Umbral de Hierro (cols 60–69):* Cruce en plataforma móvil horizontal `MMMM` sobre pinchos hacia el Portón de Hierro (`G`), culminando el rito hacia la campaña principal.

### 4.1 Nivel 1: El Camposanto (160 columnas × 24 filas)
- **Tema:** Exterior nocturno con luna llena, colinas oscuras, lápidas y árboles secos.
- **Enseñanza:** Salto básico de altura variable y dash de sombras.
- **Estructura en 4 zonas:**
  1. *El Patio de Entrada:* Primeros saltos seguros sobre lápidas y pozos de 2-3 baldosas.
  2. *El Gran Descenso:* Caída vertical controlada entre salientes rocosas y cuervos que enseñan la caída segura.
  3. *Las Criptas Inferiores:* Pozos más profundos donde el dash es indispensable para cruzar hacia los altares.
  4. *La Escalada al Portón:* Ascenso en zigzag entre arañas patrulleras hacia la reja del camposanto.

### 4.2 Nivel 2: La Cripta (190 columnas × 12 filas)
- **Tema:** Galería subterránea de piedra con arquerías de medio punto, cadenas colgantes y antorchas.
- **Enseñanza:** Recogida de la pala, combate frontal contra guardias melee (`L`), plataformas móviles horizontales (`M`) y verticales (`V`), y recuperación de dash aéreo tras asestar golpes.
- **Estructura en 5 Actos:**
  1. *Acto I (El Umbral de Piedra):* Entrada a las catacumbas y el gran foso de 7 baldosas con salto y dash aéreo parabólico obligatorio.
  2. *Acto II (El Altar de la Pala y Primer Duelo):* Adquisición de la Pala de Sepulturero (`W`), combate cerrado contra el primer Guardia Melee (`L`) y cruce sobre foso de pinchos con plataforma horizontal `MMMMM`.
  3. *Acto III (Las Criptas Verticales):* Galerías de doble altura y foso profundo con plataforma móvil vertical (`V`) y guardias coordinados.
  4. *Acto IV (La Galería de los Sepulcros y Combate Aéreo):* Pilares estrechos sobre un lecho de pinchos donde se encadena pisotón y palazo para reiniciar el dash en el aire.
  5. *Acto V (La Gran Pared y el Santuario Interior):* Salto desde la atalaya (col 163), dash rasante a través de la ventana alta de la pared monolítica (cols 170–171) hacia el santuario final con cáliz (`c`), sepulcro (`s`) y portón (`G`) hacia El Osario.

### 4.3 Nivel 3: El Osario y El Custodio (220 columnas × 12 filas)
- **Tema:** Catacumbas profundas de hueso y cráneos, atmósfera rojiza y fuego fatuo.
- **Enseñanza:** Maestría definitiva. Consagración de la Guadaña Mística (`X`, rango 72 px), sincronización de plataformas móviles `M` y `V` sobre lechos de pinchos, encadenamiento de golpes aéreos para restaurar el dash, y el duelo climácico en dos fases contra El Custodio.
- **Estructura en 5 Actos:**
  1. *Acto I (El Descenso al Fuego Fatuo):* Entrada al osario, foso inicial con plataforma móvil horizontal `MMMM` y primeros moradores sobre lápidas óseas.
  2. *Acto II (La Capilla Ósea y la Guadaña Mística):* Foso con plataforma móvil vertical (`V`) hacia el pedestal donde reposa **La Guadaña Mística (`X`)**, seguido de una pasarela de combate cerrado contra dos Guardias Melee (`L`) para dominar el nuevo rango de 72 px.
  3. *Acto III (El Desfiladero de Cadenas y Plataformas Mixtas):* Fosos dobles con plataformas horizontales y verticales sobre un lecho continuo de pinchos (`^^^^`), con sepulcro de guardado (`s`) en col 128.
  4. *Acto IV (El Guantelete de los Guardias de Élite):* Pilares escalonados de hueso sobre un mar de pinchos donde golpear a los guardias en el aire resetea el dash para alcanzar el siguiente apoyo.
  5. *Acto V (La Gran Arena del Custodio):* Checkpoint (`s`) en col 178, cámara monumental de 33 baldosas con cornisas tácticas elevadas para esquivar las ondas de choque del Custodio (`B`, col 196) y lanzarse en pisotón (stomp) en la Fase 2, culminando en la Cámara de la Victoria con el Cáliz (`c`) y el Portón Final (`G`, col 216).

---

## 5. El Jefe Final: El Custodio del Osario

El Custodio es el guardián eterno de la cripta, una figura colosal de piedra, huesos y faroles votivos.

### 5.1 Especificaciones de Combate (6 Puntos de Vida)
El enfrentamiento se divide en dos fases secuenciales de dificultad creciente:

#### FASE I: Ataque Mixto (Vidas 6 a 4)
- **Comportamiento:** Patrulla la arena a 90 px/s. Al detenerse, levanta su maza-pala y azota el piso, generando **2 ondas de choque** terrestres que avanzan hacia los costados a 190 px/s.
- **Vulnerabilidad:** Puede ser dañado tanto con sablazos de pala/guadaña como con pisotones aéreos en el cráneo.
- **Ventana de castigo:** Queda aturdido de rodillas durante 1.2 segundos tras golpear el suelo.

#### FASE II: Furia Ósea (Vidas 3 a 1)
- **Transformación:** El Custodio ruge; se activa un aura carmesí ardiente en su cuerpo y sus ojos fulguran en rojo sangre.
- **Inmunidad al sablazo:** **La pala y la guadaña rebotan inútilmente** contra su armadura reforzada (generando chispas y sonido metálico de rechazo). **Solo el pisotón aéreo puede infligir daño.**
- **Ataque 1 (Triple Onda Expansiva):** Azota el suelo desatando 3 ondas de choque rápidas con separaciones variables que obligan a saltar y dashar en el aire con timing estricto.
- **Ataque 2 (Embestida Furia):** Tras telegrafiar un agachamiento con temblor de cámara durante 0.7 segundos, carga velozmente a través de la arena a 220 px/s hacia el jugador, estrellándose contra los muros y quedando expuesto.

---

## 6. Sistema de Menús, Configuración y Rejugabilidad Comercial

El flujo de pantallas ha sido completamente depurado de consolas y pruebas temporales:

```
[ ARRANQUE ] ──► [ INTRO GÓTICA ] ──► [ MENÚ PRINCIPAL ]
                                             │
                       ┌─────────────────────┼─────────────────────┬─────────────────────┐
                       ▼                     ▼                     ▼                     ▼
                   [ JUGAR ]       [ SELECCIÓN PANTALLA ]     [ TUTORIAL ]          [ CRÉDITOS ]
                       │                     │                     │                     │
                       ▼                     ▼                     ▼                     ▼
                  (Campaña N1)         (Nivel 1, 2 ó 3)       (Prólogo del          (Equipo y
                                                               Sepulturero)          Referencias)
```

1. **Pantalla de Intro:** Título gótico animado con luna llena, colinas lejanas, subtítulo "La redención del sepulturero" y prompt palpitante "PRESIONA ESPACIO O ENTER".
2. **Menú Principal Diegético:** Opciones navegables con cursor de cruz de hierro y sonido de campana de piedra:
   - `JUGAR`: Inicia la odisea desde el Camposanto.
   - `SELECCIÓN DE PANTALLA`: Selector de 3 niveles con preview de nombre, tema y descripción.
   - `TUTORIAL`: Acceso directo al Prólogo didáctico ("El Ritual del Sepulturero") con remates turquesa.
   - `CONFIGURACIÓN DEL SANTUARIO`: Ajustes en tiempo real de Controles, Calidad Gráfica y Modos de Interfaz.
   - `CRÉDITOS`: Detalle del Equipo 6, tecnología (pygame-ce) y homenajes (Blasphemous, Castlevania, Ender Lilies).
3. **Configuración del Santuario (Conexión Real):**
   - **Controles / Teclado:** Alterna entre `Preset 1: WASD Moderno` (Espacio para saltar, Shift/X para Dash, J/Z para atacar) y `Preset 2: Retro Arcada Z-X-C` (Z para saltar, X para dash, C para atacar). Los carteles espaciales actualizan sus glifos en tiempo real.
   - **Calidad Gráfica:**
     - *Alta (0):* Halos de luz aditivos completos, máscara de penumbra suave y 100% de partículas ambientales y de impacto.
     - *Media (1):* Máscara de penumbra activa, halos ligeros y 50% de partículas ambientales.
     - *Baja (2):* Omisión completa de la pesada `mascara_penumbra` y halos complejos; garantiza 60 FPS estables incluso en hardware modesto.
   - **Modo de HUD:**
     - *Completo (0):* Riel superior al 100% de opacidad y canal de mensajes activo.
     - *Compacto (1):* Riel superior translúcido (`alpha = 140`) y canal sutil.
     - *Inmersivo (2):* Oculta el riel durante la exploración tranquila para sumergir al jugador en el mundo; emerge suavemente ante jefes activos o durante 3 segundos tras recibir daño o cosechar almas/ítems.
4. **Relicario de Fin de Nivel (`nivel_completado`):**
   Al cruzar el Portón (`G`) de los Niveles 1 y 2, se despliega un relicario solemne enmarcado en oro que expone:
   - Cita poética de Edgar Allan Poe adaptada al descenso del sepulturero.
   - **Almas Consagradas en el Nivel:** Conteo de almas rescatadas frente al total (`X / Total`).
   - **Vidas Conservadas:** Estado vital preservado (`X / 5`).
   - **Tiempo del Nivel:** Cronómetro de precisión en formato `MM:SS.d`.
   - **Rango del Nivel:** Calificación litúrgica del tramo (`S+`, `S`, `A`, `B`, `C`).
   - Navegación clara: `[ENTER] Descender al siguiente nivel · [ESC] Menú Principal`.
5. **Pantalla de Victoria Litúrgica y Rango de Campaña:**
   Al abatir al Custodio del Osario en el Nivel 3 y cruzar el portón final hacia la superficie, se revela el balance litúrgico global:
   - **Almas Totales Cosechadas** a lo largo de toda la campaña.
   - **Tiempo Total de Campaña** en minutos, segundos y décimas (`MM:SS.d`).
   - **Vidas Conservadas** al culminar la odisea (`X / 5`).
   - **Caídas Totales (`muertes_totales`):** Registro de sacrificios en la cripta.
   - **Rango Litúrgico de Campaña:**
     - `S+ · REQUÍEM SUPREMO`: Tiempo < 240 s (o < 320 s con 0 muertes y $\ge 4$ vidas).
     - `S · MAESTRO DEL OSARIO`: Tiempo < 420 s y $\le 1$ muerte.
     - `A · SEPULTURERO SACRO`: Tiempo < 600 s y $\le 3$ muertes.
     - `B · EXPLORADOR DE CRIPTAS`: Tiempo < 900 s.
     - `C · EL OSARIO TE PUSO A PRUEBA`: Tiempo $\ge 900$ s o persistencia reiterada.

---

## 7. Las 4 Interfaces (Fagerholt & Lorentzon) y 5 Principios UX

Siguiendo la taxonomía de diseño de interfaces de Erik Fagerholt y Mathias Lorentzon, **IN CRYPTA** distribuye su información a través de los cuatro cuadrantes para maximizar la inmersión sin sacrificar la legibilidad táctica:

```
                      EN EL MUNDO (Diegético)
                                ▲
                                │
              DIEGÉTICA         │         ESPACIAL
         · Llama del Farol      │   · Burbujas heráldicas
         · Checkpoints (Tiers)  │     sobre Altares y Faroles
         · Cadenas del Altar X  │   · Glifos de teclas dinámicos
                                │
    ────────────────────────────┼────────────────────────────► EN EL ESPACIO 2D
                                │
                 META           │       NO DIEGÉTICA
         · Viñeta Carmesí 1 HP  │   · Riel superior 1232×72 px
         · Destello Manto Farol │   · Grilla 2×2 panel derecho
         · Flash de daño        │   · Canal de mensajes único
                                │
                                ▼
                    EN LA PANTALLA (No Diegético)
```

### 7.1 Matriz de las 4 Interfaces

1. **Interfaz Diegética (Existe en la ficción y el mundo físico del personaje):**
   - **El Farol del Sepulturero:** Su llama conmuta de color e intensidad: fulgor turquesa cuando el Dash está listo y ámbar apagado durante el enfriamiento. Exhibe auras místicas al portar el *Manto del Farol* (halo celeste) y el *Filo de Ánima* (chispas doradas).
   - **Faroles de Checkpoint (`F`):** Encienden su fuego azul con tres alturas e intensidades distintas según el Tier alcanzado (Tier 1 tenue, Tier 2 brillante, Tier 3 fuego fatuo celestial).
   - **Cadenas del Altar de la Guadaña (`X`):** Cadenas físicas de hierro rodean el pedestal de la guadaña en el Nivel 3 mientras el Carcelero (`K`) permanezca con vida; al derrotarlo, las cadenas caen al vacío pulverizándose.

2. **Interfaz Espacial (Existe en las coordenadas 2D del mundo, visible al jugador):**
   - **Burbujas Heráldicas Contextuales (`dibujar_ui_espacial`):** Aparecen suavemente mediante interpolación alfa cuando el sepulturero se aproxima a $\le 140\text{ px}$ de altares (`D`, `W`, `X`), faroles (`F`), campanas (`I`) y puntos clave.
   - **Adaptación Dinámica de Presets:** Los textos instructivos leen en tiempo real el mapeo de teclas (`[SHIFT / X]` vs `[X / SHIFT]`, `[ESPACIO / W]` vs `[Z / ESPACIO]`).

3. **Interfaz Meta (Existe en la lente de la cámara / plano de visión):**
   - **Viñeta Carmesí Reactiva:** Al quedar a 1 punto de vida, los bordes de la pantalla proyectan una viñeta roja profunda pulsando rítmicamente en sincronía con el latido cardíaco de 55 Hz.
   - **Destello del Manto del Farol (`destello_manto`):** Al consagrar el manto o absorber un golpe mortal, la periferia de la pantalla destella en cian celeste aditivo, comunicando la protección divina sin tapar la acción central.

4. **Interfaz No Diegética (Riel Superior Gótico en `hud.py`):**
   - Geometría inmutable de $1232 \times 72\text{ px}$ anclada en el borde superior, dividida en:
     - **Zona Izquierda (336 px):** Relicario de corazones de vida y distintivos de bendiciones activas (`MANTO`, `FILO`, `MANTO · FILO`).
     - **Zona Centro (512 px):** Corona y barra segmentada del jefe en combate, o nombre heráldico del nivel en exploración.
     - **Zona Derecha (360 px):** Grilla táctica $2 \times 2$ con celdas de $164 \times 22\text{ px}$ para Almas consagradas, Almas Volátiles en riesgo `(+X)`, estado del Dash y estado del Arma.
     - **Canal Único de Mensajes:** Caja de pergamino de $560 \times 48\text{ px}$ en $y = 96$ con interpolación sinusoidal y desvanecimiento suave.

### 7.2 Los 5 Principios de UX

1. **Principio 1 — Cero Solapamientos e Invarianza:** La geometría del HUD se calcula mediante cálculo estricto de regiones no superpuestas (`layout.solapamientos() == []`).
2. **Principio 2 — Consistencia y Ubicuidad de Feedback:** Prompts universales (`[ENTER] Confirmar · [ESC] Volver`) presentes en todas las pantallas de navegación, relicarios y diálogos.
3. **Principio 3 — Claridad Jerárquica y Semántica Cromática:**
   - **Oro Litúrgico (`#D4AF37`):** Altares, títulos, rango S y divinidad.
   - **Turquesa Ánima (`#48CAE4`):** Almas espectrales, dash de sombras y bendiciones del farol.
   - **Carmesí Rubí (`#E63946`):** Salud, peligro, pulsación crítica y furia del custodio.
   - **Verde Santuario (`#52B788`):** Vidas conservadas y confirmación exitosa.
4. **Principio 4 — Asistencias Invisibles y Accesibilidad:**
   - 100 ms de *coyote time* y 120 ms de *jump buffering*.
   - Modo de reducción de sacudidas de pantalla (`F1`), configurable desde el menú.
5. **Principio 5 — Escalabilidad Gráfica y 60 FPS Garantizados:** Presets visuales calibrados para mantener 60 FPS ininterrumpidos en cualquier gama de hardware.

---

## 8. Feedback Audiovisual & Coherencia Multicanal

Para garantizar la estética de **Sensación**, cada interacción física produce retroalimentación cruzada en 4 canales simultáneos:

| Evento | Gráficos Procedurales | Sistema de Partículas | Cámara | Audio |
|---|---|---|---|---|
| **Salto** | Estiramiento vertical del sprite (1.15×) | Nube de polvo y hojas secas | Inerte | Tono tonal ascendente |
| **Dash** | Silueta translúcida con cloning espectral | Estela de cometa turquesa | Sacudida leve (4 px) | Silbido de viento espectral |
| **Pala / Guadaña** | Haz curvo luminoso (oro / violeta) | Chispas metálicas en cono | Sacudida media (7 px) | Impacto seco de metal y hueso |
| **Pisotón Exitoso** | Compresión horizontal de impacto | Explosión radial de esquirlas | Sacudida media (8 px) | Percusión profunda de tumba |
| **Manto Consumido** | Viñeta celeste periférica aditiva | Estallido radial celeste (24 partículas) | Flash celeste sutil | Tono de escudo quebrado |
| **Campana / Incensario** | Onda concéntrica expansiva | Chispas doradas ascendentes | Impulso ascendente | Tañido litúrgico solemne |
| **Losa Fracturada** | Desplazamiento oscilante 0.40s | Esquirlas de roca cayendo | Sacudida micro | Crujido de piedra quebrandose |
| **Daño Recibido** | Parpadeo de invulnerabilidad (1.2 s) | Salpicadura de sangre carmesí | Sacudida fuerte (14 px) + Flash rojo | Tono grave descendente |
| **Fase 2 Jefe** | Ojos fulgurantes y silueta en llamas | Torbellino de humo rojo constante | Sacudida prolongada | Alarido ritual de ultratumba |

---

## 9. Verificación y Suite de Calidad Total

El proyecto cuenta con una batería integral de pruebas unitarias, de integración y de estrés gráfico ejecutables en entornos headless (CI/CD):
- **`tests/test_logica.py` (48 pruebas lógicas exhaustivas):**
  - Físicas de salto, coyote time, jump buffer, dash, corte de gravedad, colisiones, losas quebradizas, incensarios y checkpoints de 3 tiers.
  - Combate con pala, guadaña mística, Carcelero, Custodio (fases I y II) y rebotes por pisotón.
  - Rango Litúrgico de campaña (`S+`, `S`, `A`, `B`, `C`), Relicario de fin de nivel y navegación.
  - Modos de HUD, calidad gráfica y destello periférico del manto.
- **`tests/test_hud.py` (35 pruebas unitarias de UI/UX):**
  - Modos de HUD (Completo, Compacto alpha 140, Inmersivo con despertar por eventos).
  - Cero solapamientos en riel superior e invarianzas de layout.
  - Contadores dinámicos de almas volátiles y distintivos de bendiciones activas.
- **`pytest tests/` (47 pruebas automatizadas en verde):**
  - Carga y verificación de assets de audio, lógica de HUD y módulos auxiliares.
- **`./jugar_pygame.sh --headless`:**
  - Inicialización limpia de la ventana de juego, ciclo de actualización y renderizado de frames sin errores de display.
