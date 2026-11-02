# PROMPT DE ORQUESTACIÓN — PRIORIDAD 2: ARQUITECTURA DE NIVELES MAGISTRAL (25–30 MINUTOS, SET-PIECES Y RUTAS DE RIESGO/RECOMPENSA)

> **MODO DE EJECUCIÓN:** Goal Automático / Autónomo con Orquestación de Sub-Agentes (Gemini 3.8 Flash).  
> **OBJETIVO FINAL:** Rediseñar y expandir la campaña de **IN CRYPTA** en `niveles.py` para ofrecer **25 a 30 minutos de gameplay inolvidable** para un jugador humano promedio, combinando la estructura japonesa **Kishōtenketsu**, las **5 Etapas de Progresión**, la **Sierra de Dificultad** y rutas opcionales de alto riesgo para el **Pacto del Farol**.

---

## 1. ROL Y DESPLIEGUE DE SUB-AGENTES

Actúas como **Principal Level Designer (Especialista en Plataformeros 2D como Celeste, Hollow Knight y Castlevania)**.  
Orquesta **4 SUB-AGENTES ESPECIALIZADOS**:

1. **Sub-Agente 1 (Diseñador del Preludio y Nivel 1 — "El Camposanto Bajo la Tormenta"):** Construye `NIVEL_TUTORIAL` (100 cols) y `NIVEL_1` (210 cols).
2. **Sub-Agente 2 (Diseñador del Nivel 2 — "La Cripta de los Péndulos"):** Construye `NIVEL_2` (260 cols), respetando las invariantes de los tests existentes y creando secuencias épicas de Pisotón + Dash.
3. **Sub-Agente 3 (Diseñador del Nivel 3 — "El Gran Osario de la Muerte Roja"):** Construye `NIVEL_3` (330 cols), el nivel más largo y desafiante, con 4 Faroles (`F`), el Mini-Boss Carcelero (`K`), el Altar de la Guadaña (`X`), un guantelete de maestría y la Gran Arena del Custodio (`B`).
4. **Sub-Agente 4 (Validador de Geometría, Físicas y Tests):** Audita matemáticamente cada salto y corre `tests/test_logica.py` hasta lograr 0 fallos.

---

## 2. REGLAS MATEMÁTICAS Y RESTRICCIONES DE LOS TESTS (¡CRÍTICO!)

Antes de modificar `niveles.py`, todos los Sub-Agentes deben cumplir estas **5 Reglas Inquebrantables** que son verificadas por `tests/test_logica.py`:

1. **Progresión Estricta de Longitud:**
   $$\text{Columnas}(\text{NIVEL\_TUTORIAL}) < \text{Columnas}(\text{NIVEL\_1}) < \text{Columnas}(\text{NIVEL\_2}) < \text{Columnas}(\text{NIVEL\_3})$$
   - Dimensiones objetivo:
     - `NIVEL_TUTORIAL`: **100 columnas × 14 filas**
     - `NIVEL_1`: **210 columnas × 18 filas**
     - `NIVEL_2`: **260 columnas × 18 filas**
     - `NIVEL_3`: **330 columnas × 18 filas**
2. **Unicidad y Suelo de Entidades:**
   - Exactamente **un `'P'`** (spawn) y **un `'G'`** (meta) por mapa.
   - Ningún alma `'o'` puede estar ubicada a la derecha de la columna de `'G'`.
   - **TODO enemigo terrestre (`'E'`, `'L'`, `'K'`, `'B'`) DEBE tener un bloque `'#'` inmediatamente debajo (`fila + 1`)**. Nunca pongas un enemigo sobre vacío `'.'`, pinchos `'^'`, plataformas `'M'/'V'` ni losas `'~'`.
3. **Invariante 1 de Test (`probar_primer_salto_cripta` en `NIVEL_2`):**
   - En `NIVEL_2`, en la fila del piso principal (`fila 16`, es decir `alto - 2 * TILE`), el **primer hueco** entre el primer tramo de `'#'` y el segundo tramo de `'#'` **DEBE medir exactamente `7 tiles` de ancho** (por ejemplo, `################.......################################`). Esto valida en los tests que el primer pozo de La Cripta exige `Salto + Dash`.
4. **Invariante 2 de Test (`probar_salto_ventana_nivel_2` en `NIVEL_2`):**
   - `tests/test_logica.py` verifica una pared vertical con ventana en las **columnas `170` y `171`** de `NIVEL_2` (donde `filas[2][170:172] == "##"`, `filas[6][170:172] == ".."` y `filas[7][170:172] == ".."`, `filas[9][170:172] == "##"`, y una plataforma de lanzamiento en `col 163, fila 8`).
   - **Cómo resolverlo al expandir `NIVEL_2`:** Si expandes `NIVEL_2` a 260 columnas, o bien colocas ese desafío de la ventana en las columnas 163–172 y continúas el Acto Final desde la columna 175 hasta la 255 (actualizando el test o haciendo que la ventana sea el paso hacia el último acto), o actualizas las coordenadas en `probar_salto_ventana_nivel_2` para que coincidan con la nueva columna de la ventana. *(Verifica que `probar_salto_ventana_nivel_2` pase en verde).*
5. **Métricas de Salto Justo:**
   - Sin Dash (`NIVEL_TUTORIAL` y primera mitad de `NIVEL_1`): ningún foso obligatorio puede superar **`4 a 5 tiles`**.
   - Con Dash (segunda mitad de `NIVEL_1` y `NIVEL_2`/`NIVEL_3`): fosos de **`6 a 8 tiles`**.
   - Con Pisotón/Trampolín (`E`, `C`, `m`, `I` en medio del foso): fosos de **`10 a 14 tiles`**.

---

## 3. DISEÑO PASO A PASO DE LOS 4 MAPAS (LA SIERRA DE DIFICULTAD)

### 🕯️ MAPA 0: EL PRELUDIO (`NIVEL_TUTORIAL` — 100 cols × 14 filas)
* **Filosofía:** *Show, don't tell* (Estilo *Mega Man X* / *Celeste* Prólogo). Cero daño, cero muertes.
* **Beat 1 (Cols 0–25) — Sensibilidad de Salto:** Escalón bajo de 1 tile (toque corto) seguido de un muro de 3 tiles de alto (mantener presionado `ESPACIO`), con almas (`o`) dibujando la parábola vertical.
* **Beat 2 (Cols 26–50) — El Foso con Trinchera y Coyote Time:** Un foso de 4 tiles y luego uno de 5 tiles. Si el jugador cae, aterriza sobre suelo seguro (`#`) con escalones para volver a subir y reintentar sin perder vida.
* **Beat 3 (Cols 51–78) — El Pacto del Farol (`F`):** Un camino superior fácil y un pequeño desvío con plataformas que suma **6 almas (`o`)**. Al llegar al Farol (`F`), el jugador experimenta cómo se consagran sus almas y recibe su primer **Manto Protector**.
* **Beat 4 (Cols 79–99) — El Portón del Umbral (`G`):** Ascenso solemne entre estatuas (`s`), velas (`c`) y lápidas (`t`) hacia la salida.

---

### 墓 MAPA 1: EL CAMPOSANTO (`NIVEL_1` — 210 cols × 18 filas)
* **Tiempo estimado jugador promedio:** 6 a 8 minutos.
* **Mecánicas protagonistas:** Salto de precisión, esquiva sin armas, obtención del **Amuleto de Sombras (`D` - Dash)**, Losas Quebradizas (`~`) y Campanas de Resonancia (`I`).
* **Acto I (Cols 0–55) — La Ronda Nocturna (Sin Dash, Sin Arma):**
  - Saltos de 3 a 5 tiles. Introducción del primer **Morador (`E`)**: como el sepulturero está desarmado, debe esperar a que patrulle y saltarle por encima.
  - Ruta elevada opcional con 5 almas sobre cornisas angostas.
* **Acto II (Cols 56–105) — El Altar de las Sombras (`D`) y Práctica Segura:**
  - En una cripta abierta, el jugador recoge el **Dash (`D`)**.
  - Inmediatamente después, un foso de `7 tiles` (imposible de cruzar solo saltando) pero con **trinchera segura abajo** y escalera de retorno. Un arco horizontal de almas (`o`) le enseña dónde presionar `SHIFT` en el aire.
  - Primer **Farol de Reposo (`F`)**.
* **Acto III (Cols 106–160) — El Puente Quebradizo y los Cuervos:**
  - Introduce **Losas Quebradizas (`~~~`)** y plataformas móviles (`MMMM`) sobre fosos reales.
  - Enemigos voladores (`C` Cuervos) que obligan a medir la altura del salto + Dash.
  - Segundo **Farol de Reposo (`F`)** con bifurcación de riesgo/recompensa (ruta baja segura vs. ruta alta llena de almas).
* **Acto IV (Cols 161–209) — Clímax del Camposanto:**
  - Secuencia rítmica continua combinando `Salto -> Losa Quebradiza -> Dash -> Campana de Resonancia (I) -> Dash` hasta el Portón de La Cripta (`G`).

---

### ⚔️ MAPA 2: LA CRIPTA PROFUNDA (`NIVEL_2` — 230 a 260 cols × 18 filas)
* **Tiempo estimado jugador promedio:** 8 a 10 minutos.
* **Mecánicas protagonistas:** Obtención de la **Pala de Hierro (`W`)**, Golpe Frontal, **Pisotón Aéreo (Pogo) + Recarga de Dash**, Plataformas Verticales (`VV`) y Guardias Melee (`L`).
* **Acto I (Cols 0–40) — El Salto de Fe y el Altar de Hierro (`W`):**
  - El primer foso del suelo mide **exactamente `7 tiles`** (recall obligatorio de `Salto + Dash`).
  - Llegada al **Altar de la Pala (`W`)**.
* **Acto II (Cols 41–95) — Escuela de Exorcismo (Práctica Segura de Combate y Pogo):**
  - **Lección 1 (Golpe Frontal):** Un Morador (`E`) custodiando un puente plano.
  - **Lección 2 (El Pisotón Trampolín):** Un foso ancho de `9 tiles` con **trinchera segura abajo** (sin pinchos) y un Morador (`E`) o Cuervo (`C`) en una isleta central baja. Las almas (`o`) dibujan una "W" en el aire: `Saltar -> Caer sobre la cabeza del enemigo (Pisotón) -> Rebotar -> Usar el Dash recién recargado` para alcanzar la cornisa alta.
  - Primer **Farol de Reposo (`F`)**.
* **Acto III (Cols 96–160) — Las Galerías Verticales y los Guardias (`L`):**
  - Introduce **Guardias Melee (`L`)** (que telegrafían su estocada `200 ms` antes) y plataformas ascendentes (`VV`).
  - Fosos con pinchos (`^^^^`) donde el jugador aplica de verdad el encadenamiento `Salto + Dash + Pisotón sobre enemigo + Dash`.
  - Segundo **Farol de Reposo (`F`)**.
* **Acto IV (Cols 161–Final) — La Gran Pared Vertical y el Santuario Interior:**
  - El icónico desafío de saltar desde la atalaya y hacer un Dash quirúrgico a través de la ventana de la pared monolítica (manteniendo compatibilidad con `probar_salto_ventana_nivel_2`), seguido de un tramo final de guardias y plataformas sobre espinas hasta el Portón (`G`).

---

### 💀 MAPA 3: EL GRAN OSARIO (`NIVEL_3` — 320 a 340 cols × 18 filas)
* **Tiempo estimado jugador promedio:** 10 a 14 minutos.
* **Mecánicas protagonistas:** Examen integral de todas las habilidades, **Mini-Boss (`K` El Carcelero)**, **Power-Up Guadaña Consagrada (`X`)**, Guantelete de Pogo-Dash Aéreo y **Boss Final (`B` El Custodio en 2 Fases)**.
* **Acto I (Cols 0–75) — El Desfiladero de Cráneos:**
  - Tramo de alta intensidad con plataformas móviles (`MMMM`, `VV`), losas quebradizas (`~~~`), arañas (`A`) y polillas (`m`) sobre abismos de pinchos.
  - Culmina en el **Farol 1 (`F`)**.
* **Acto II (Cols 76–140) — La Celda del Carcelero (`K`) y la Guadaña (`X`):**
  - Arena cerrada donde aguarda **El Carcelero del Osario (`K`)**. El jugador debe esquivar su embestida telegrafiada (saltando o haciendo dash por encima) y castigarlo en su ventana de cansancio de `1.3 s`.
  - Al derrotarlo (+5 almas), se rompen las cadenas del **Altar de la Guadaña Consagrada (`X`)** justo al lado, seguido del **Farol 2 (`F`)**.
* **Acto III (Cols 141–220) — El Cosechador de Ánimas:**
  - Zona diseñada para disfrutar el poder de la nueva Guadaña (`76 px` de alcance violeta): pasillos con Guardias Melee (`L`) y un abismo colosal de `14 tiles` que exige encadenar **dos pisotones seguidos** (sobre un Cuervo `C` y un Morador `E` / Campana `I`) con Dashes intermedios.
  - Ruta secreta superior con 8 almas para llegar cargado al **Farol 3 (`F`)**.
* **Acto IV (Cols 221–265) — La Antesala del Trono:**
  - Ascenso y descenso tenso con Losas Quebradizas y Guardias, desembocando en el **Farol 4 (`F` - Último Punto de Control)** justo frente a la entrada de la arena final, con almas dispuestas para activar el **Manto del Farol** antes del jefe.
* **Acto V (Cols 266–Final) — El Clímax: El Custodio del Osario (`B`):**
  - Arena amplia de `36 tiles` de suelo sólido `#` continuo con dos pequeñas plataformas tácticas elevadas a los lados para ayudar a leer las ondas de choque.
  - Duelo en **2 Fases** contra `B`. Al vencerlo, el Portón Final (`G`) se abre hacia la redención.

---

## 4. CRITERIOS DE ACEPTACIÓN
- [ ] Todos los mapas en `niveles.py` y `niveles_rediseñados.py` tienen filas de longitud idéntica y cumplen las reglas del parser.
- [ ] `PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tests/test_logica.py` pasa al 100% sin un solo error.