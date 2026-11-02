# IN CRYPTA
## Documento de Diseño de Videojuego (GDD) y Matriz MDA — Versión Viva de Producción 1.1.0

> [!NOTE]
> **ESTADO DEL DOCUMENTO: GUÍA VIVA DE PRODUCCIÓN (NO DOGMA ABSOLUTO)**  
> Este GDD no es un contrato pétreo ni inmutable. Al encontrarse el juego en desarrollo y producción activa, este documento actúa como brújula conceptual de orientación. Los parámetros, disposiciones de HUD, valores numéricos, animaciones y respuestas de feedback audiovisual están en continua evolución empírica basada en pruebas de juego, mejoras de game feel y principios de usabilidad UI/UX. Cualquier aspecto puede ser refinado o modificado para elevar la calidad, fluidez y legibilidad del juego.

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

## 6. Sistema de Menús y Navegación

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
   - `CRÉDITOS`: Detalle del Equipo 6, tecnología (pygame-ce) y homenajes (Blasphemous, Castlevania, Ender Lilies).
3. **Flujo In-Game:** `ESC` pausa instantáneamente o regresa al Menú Principal con total solidez de estados.
4. **Pantalla de Victoria Litúrgica:** Al derrotar al Custodio y cruzar el portón final, se despliega el relicario ceremonial de victoria que computa almas totales consagradas, cronómetro de precisión, vidas residuales y calificación de rango litúrgico (`S`, `A`, `B` o `C`).

---

## 7. Rediseño Diegético del HUD

Abandonando los rectángulos genéricos no diegéticos, el nuevo HUD se integra armónicamente como reliquias de la liturgia del sepulturero:

```
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│ ✠ SEPULTURERO · EL CAMPOSANTO        │  │ ❖ ÁNIMAS ESPECTRALES   07/10 │
│  [♥]  [♥]  [♥]  [♡]  [♡]             │  │  ● ● ● ● ● ● ● ○ ○ ○         │
└──────────────────────────────────────┘  └──────────────────────────────┘
  (Relicario de Vidas: Corazones            (Relicario de Ánimas: Rosario
   Góticos con latido de emergencia)         de 10 cuentas para Vida Extra)

┌──────────────────────────────────────┐
│ [ DASH: LISTO ]  │  [ GUADAÑA + ]    │
└──────────────────────────────────────┘
  (Sellos Tácticos de Habilidades)
```

1. **Relicario de Vidas (Superior Izquierda):** Marco de hierro forjado con remaches de oro. Corazones carmesí con reflejos especulares de rubí. Si el jugador desciende a 1 vida, el corazón entra en **pulsación de emergencia por latido cardíaco**, generando advertencia visual limpia sin invadir la visión.
2. **Relicario de Ánimas Espectrales (Superior Derecha):** Caja de marfil y obsidiana con 10 cuentas de rosario. Cada alma recogida ilumina una cuenta en fulgor turquesa. Al completar 10 cuentas, se produce una fanfarria y se añade un corazón al relicario de vidas.
3. **Sellos de Habilidades (Inferior Izquierda):**
   - *Sello de Dash:* Glifo turquesa que muestra barra de recarga en tiempo real o el estado "LISTO".
   - *Sello de Arma:* Muestra la Pala de sepulturero plateada en Nivel 1 y 2, y conmuta automáticamente a la **Guadaña Imperial Púrpura** al recoger el artefacto en Nivel 3.
4. **Corona Imperial del Custodio (Superior Centro, Solo Jefe):**
   - Marco de 500 px de ancho con corona de oro.
   - 6 celdas de salud con rubíes que se pulverizan al dañarlo.
   - Indicador de estado dinámico: "FASE I: VULNERABLE A PALA Y PISOTÓN" conmuta a "FASE II: ¡LA PALA REBOTA! SOLO PISOTÓN" en rojo ardiente.

---

## 8. Feedback Audiovisual & Coherencia Multicanal

Para garantizar la estética de **Sensación**, cada interacción física produce retroalimentación cruzada en 4 canales simultáneos:

| Evento | Gráficos Procedurales | Sistema de Partículas | Cámara | Audio |
|---|---|---|---|---|
| **Salto** | Estiramiento vertical del sprite (1.15×) | Nube de polvo y hojas secas | Inerte | Tono tonal ascendente |
| **Dash** | Silueta translúcida con cloning espectral | Estela de cometa turquesa | Sacudida leve (4 px) | Silbido de viento espectral |
| **Pala / Guadaña** | Haz curvo luminoso (oro / violeta) | Chispas metálicas en cono | Sacudida media (7 px) | Impacto seco de metal y hueso |
| **Pisotón Exitoso** | Compresión horizontal de impacto | Explosión radial de esquirlas | Sacudida media (8 px) | Percusión profunda de tumba |
| **Daño Recibido** | Parpadeo de invulnerabilidad (1.2 s) | Salpicadura de sangre carmesí | Sacudida fuerte (14 px) + Flash rojo | Tono grave descendente |
| **Fase 2 Jefe** | Ojos fulgurantes y silueta en llamas | Torbellino de humo rojo constante | Sacudida prolongada | Alarido ritual de ultratumba |

---

## 9. Verificación y Suite de Calidad

El proyecto cuenta con una batería de pruebas de integración continua automatizadas en `tests/test_logica.py` y `tests/test_hud.py` (56 tests unitarios en total):
- `probar_niveles`: Integridad de los mapas de baldosa y dimensiones exactas.
- `probar_salto_ventana_nivel_2`: Simulación física del salto, dash aéreo rasante y aterrizaje a través de la ventana alta sin tocar pinchos.
- `probar_jefe_final`: Verificación de ambas fases del Custodio, absorción de daño, transición de furia e inmunidad a la pala en fase 2.
- `probar_menu_principal_y_navegacion`: Transiciones libres de excepciones entre Intro, Menú Principal, Selección de Niveles, Créditos y Game Loop.
- `probar_tutorial`: Integridad didáctica de "El Ritual del Sepulturero", etiquetas diegéticas del HUD y reinicio limpio.
- `probar_juego_headless`: Renderizado exhaustivo de frames, overlays de victoria y HUD sin dispositivos gráficos reales.
- `tests/test_hud.py`: Verificación de la arquitectura modular del HUD, renderizado 2x2 sin solapamiento, canal de mensajes con fade y formato dinámico de vidas/almas/cooldowns.
