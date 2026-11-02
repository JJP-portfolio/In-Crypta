# PROMPT DE ORQUESTACIÓN — PRIORIDAD 1: SISTEMAS EMERGENTES (MDA), PACTO DEL FAROL Y MECÁNICAS AMBIENTALES

> **MODO DE EJECUCIÓN:** Goal Automático / Autónomo con Orquestación de Sub-Agentes (Gemini 3.8 Flash).  
> **OBJETIVO FINAL:** Dotar al motor (`config.py`, `entidades.py`, `nivel.py`, `juego.py`) de una profundidad sistémica digna de *Celeste*, *Hollow Knight* y *Shovel Knight*, **sin agregar ningún botón nuevo**, haciendo que el Moveset básico (Salto, Dash, Pala/Pisotón y Guadaña) interactúe con el sistema de **Almas/Faroles** y con **3 nuevos elementos ambientales reactivos**.

---

## 1. ROL Y DESPLIEGUE DE SUB-AGENTES

Actúas como **Lead Game Systems Architect & Principal Gameplay Programmer** de **IN CRYPTA**.  
Debes orquestar **4 SUB-AGENTES ESPECIALIZADOS**:

1. **Sub-Agente 1 (Ingeniero de Física Cinética y Moveset):** Perfecciona en `config.py` y `entidades.py` el Salto simple variable (Coyote Time, Jump Buffer, Apex Float, Corner Correction), el Dash de Sombra (`D`), el Ataque y el **Pisotón Aéreo (Pogo)** condicionado estrictamente a tener el arma (`W`), y el Power-Up `X` (Guadaña Consagrada).
2. **Sub-Agente 2 (Diseñador de Economía — "El Pacto del Farol"):** Implementa la dualidad **Almas Volátiles vs. Almas Consagradas** y los **3 Grados de Consagración** al encender un Farol (`F`), logrando que cada alma recolectada en el camino se sienta valiosa y tensa.
3. **Sub-Agente 3 (Ingeniero de Mecánicas Ambientales de Plataformeo):** Implementa en `entidades.py` y `nivel.py` tres mecánicas de entorno clásicas del género que usan los mismos controles del jugador: **Losas Quebradizas (`~`)**, **Campanas de Resonancia (`I`)** (nodos aéreos para golpear/pisar y recargar Dash) y **Muros Oscuros Falsos / Secretos**.
4. **Sub-Agente 4 (Especialista en Jefes y QA Headless):** Ajusta los patrones del Mini-Boss (`K` Carcelero) y del Boss Final (`B` Custodio en 2 fases con requerimiento obligatorio de Guadaña `X` en Fase 2) y asegura el 100% de aprobación en `tests/test_logica.py`.

---

## 2. DISEÑO DE SISTEMAS Y REGLAS MECÁNICAS

### 2.1 El Moveset Sagrado (Cero Complejidad Artificial de Botones)
El jugador solo utiliza: **Moverse**, **Saltar**, **Dash** y **Atacar**.
1. **Salto Simple de Precisión (`ESPACIO / W / ↑` o `Z` en Retro):**
   - Impulso `-620.0 px/s`, gravedad `1500.0 px/s²`, corte de salto al soltar tecla (`vy *= 0.45`).
   - `COYOTE_TIME = 0.10 s`, `JUMP_BUFFER = 0.12 s`, `APEX_GRAVEDAD_FACTOR = 0.55` cuando `|vy| < 70.0` manteniendo salto.
2. **Dash Espectral (`SHIFT / X`):**
   - Desbloqueable en el Nivel 1 al tocar el altar `D`.
   - 1 uso en el aire (`DASH_USOS_AIRE = 1`). Se recarga al tocar suelo firme o al ejecutar un Pisotón/Golpe exitoso sobre un enemigo o Campana de Resonancia.
   - Permite **Dash-Jump** desde el suelo (`vx * 1.18` + salto completo) para cruzar tramos rápidos.
3. **La Pala (`W`) y el Pisotón Encadenado (Pogo-Dash):**
   - Desbloqueable en el Nivel 2 al tocar el altar `W`.
   - **Regla Inviolable:** Mientras `tiene_pala == False`, caer encima de un enemigo **daña al jugador**. Cuando `tiene_pala == True`, caer sobre cualquier enemigo (`vy > 0` y `rect.bottom <= enemigo.rect.top + 18`) ejecuta un **Pisotón Aéreo**: mata al enemigo común (o daña a jefes en ventana vulnerable), impulsa al jugador hacia arriba (`vy = -360.0`), activa `0.08 s` de *hitstop* y **recarga inmediatamente el Dash aéreo (`dash_usos_aire = 1`, `dash_cooldown = 0.0`)**.
4. **Guadaña Consagrada (`X` — Power-Up del Nivel 3):**
   - Custodiada por el Mini-Boss (`K`). Aumenta el alcance de `34 px` a `76 px` (`rango_ataque_mejorado = True`) y es **obligatoria** para romper la Coraza Espectral de la Fase 2 del Custodio (`B`).

---

### 2.2 El Nuevo Sistema de Almas y Faroles: "El Pacto del Farol"
Inspirado en *Hollow Knight* y *Shovel Knight*, las almas (`o`) cumplen tres funciones simultáneas:
1. **Función Pedagógica (Guía Espacial):** Dibujan en el aire el arco parabólico exacto donde el jugador debe saltar o activar el Dash.
2. **Función de Supervivencia Directa (Rosario):** Cada `10 almas` recolectadas otorgan `+1 Corazón de Vida` al instante (hasta `VIDAS_MAXIMAS = 5`).
3. **Función Estratégica (Almas Volátiles y Consagración en Faroles `F`):**
   - Las almas que el jugador junta entre un Farol y el siguiente son **Almas Volátiles** (`almas_tramo = jugador.almas - almas_consagradas`).
   - Si el jugador muere antes de llegar al siguiente Farol, **pierde las almas volátiles de ese tramo** (las cuales reaparecen en el nivel) y revive en el último Farol con sus `almas_consagradas`.
   - Si el jugador llega vivo a un **Farol de Reposo (`F`)**, el checkpoint se activa **gratis** y las almas volátiles que traía se **Consagran en la Llama**, otorgando recompensas según la cantidad entregada en ese tramo:
     - **1 a 4 Almas (Consagración Básica):** Guarda todas las almas permanentemente y, si el jugador tiene menos de `3 vidas`, lo cura **`+1 Vida`**.
     - **5 a 7 Almas (Bendición del Manto):** Todo lo anterior + activa el **Manto del Farol** (`jugador.escudo_farol = True`), una barrera espectral celeste que absorbe el próximo golpe enemigo o caída en pinchos sin perder vida ni retroceder al checkpoint.
     - **8+ Almas (Fuego Fatuo Consagrado):** Todo lo anterior + activa **Filo de Ánima** (`jugador.filo_anima = True`): mientras no reciba daño, el cooldown de su Dash se reduce un 20% y su alcance de ataque gana `+12 px` con chispas doradas/turquesas.

---

### 2.3 Nuevas Mecánicas Ambientales de Plataformeo (Compatibles con Mapas ASCII)
Para que los 30 minutos de juego sean variados, dinámicos y sorprendentes sin complicar los controles, implementa en `nivel.py`, `entidades.py` y `juego.py` dos nuevos elementos de mapa ASCII (retrocompatibles: si un mapa no los usa, todo sigue igual; si los usa, enriquecen el nivel):

1. **Losa Quebradiza de Osario (Símbolo `'~'` en el mapa ASCII):**
   - Funciona como un bloque sólido (`#`) mientras está intacta (`activa == True`), por lo que se incluye en `nivel.solidos_actuales()`.
   - Cuando el jugador se apoya sobre ella (`jugador.en_suelo` y `abs(jugador.rect.bottom - losa.rect.top) <= 2`), inicia una vibración telegrafiada de `0.40 segundos` (desplazamiento visual `±2 px` y polvo cayendo).
   - Al cumplirse los `0.40 s`, la losa se quiebra (`activa = False`, emite partículas de hueso y deja de colisionar durante `2.5 segundos`), tras lo cual se reconstruye con un destello espectral.
   - *Nota para tests:* En `probar_niveles` y `probar_mapa_final`, nunca pongas enemigos (`E`, `L`, `K`, `B`) sobre `'~'`, siempre sobre `'#'`.

2. **Campana de Resonancia / Orbe Espectral (Símbolo `'I'` en el mapa ASCII):**
   - Inspirada en las lámparas de *Hollow Knight* y los faroles de *Castlevania*. Es un incensario/campana suspendida en el aire sobre grandes abismos.
   - **No daña al jugador.** Si el jugador la golpea con la Pala/Guadaña o le cae encima con Pisotón (`vy > 0`), la campana repica (sonido `alma_6`), emite una onda turquesa, hace rebotar al jugador hacia arriba (`vy = -REBOTE_ENEMIGO`) y **recarga su Dash en el aire (`dash_usos_aire = 1`, `dash_cooldown = 0.0`)** sin desaparecer (tiene un breve cooldown visual de `0.5 s`).
   - **Importante:** Las Campanas `'I'` permiten cruzar abismos incluso en el **Nivel 1** (antes de tener la pala) si el jugador simplemente las toca cayendo desde arriba, o en los Niveles 2 y 3 combinadas con enemigos.

---

## 3. CRITERIOS DE ACEPTACIÓN Y VERIFICACIÓN
1. Implementar las clases `LosaQuebradiza` e `IncensarioRebote` en `entidades.py`, integrarlas en `Nivel` (`nivel.py`) y en el loop de `Juego` (`juego.py`).
2. Asegurar que `nivel.reiniciar()` restaure todas las losas e incensarios a su estado inicial.
3. Agregar pruebas unitarias en `tests/test_logica.py` para `LosaQuebradiza`, `IncensarioRebote` y el sistema de 3 Tiers de `FarolCheckpoint`.
4. Ejecutar `PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tests/test_logica.py` y confirmar `TESTS_INCRYPTA_OK`.