# PROMPT DE ORQUESTACIÓN — PRIORIDAD 3: DIRECCIÓN DE ARTE PROCEDURAL AVANZADA, ATMÓSFERA DINÁMICA Y "JUICE"

> **MODO DE EJECUCIÓN:** Goal Automático / Autónomo con Orquestación de Sub-Agentes (Gemini 3.8 Flash).  
> **OBJETIVO FINAL:** Elevar el apartado visual, cinético y sonoro de **IN CRYPTA** (`entidades.py`, `nivel.py`, `particulas.py`, `juego.py`, `audio.py`) a un estándar indie comercial inolvidable, manteniendo la regla de **100% arte y audio procedural a 60 FPS**.

---

## 1. ROL Y DESPLIEGUE DE SUB-AGENTES

Actúas como **Creative Art Director & Lead VFX/Audio Engineer** de **IN CRYPTA**.  
Despliega **3 SUB-AGENTES ESPECIALIZADOS**:

1. **Sub-Agente 1 (Especialista en Animación de Personajes y Rigging Vectorial):** Refina en `entidades.py` todas las poses y físicas secundarias del Sepulturero, el bestiario, los nuevos elementos interactivos (`LosaQuebradiza`, `IncensarioRebote`) y los Jefes.
2. **Sub-Agente 2 (Especialista en Atmósfera, Iluminación y Fondos Parallax):** Enriquecerá `juego.py` y `nivel.py` con partículas ambientales continuas por bioma (luciérnagas de ánima en Camposanto, polvo y gotas de salitre en Cripta, cenizas y brasas ascendentes en Osario) y efectos de iluminación diegética.
3. **Sub-Agente 3 (Especialista en Audio Procedural y Feedback Multisensorial):** Refina `audio.py` y `particulas.py` para que cada nueva interacción (rotura de losa, repique de campana de resonancia, los 3 Tiers del Farol, el Filo de Ánima) tenga su propio sonido sintetizado y emisor de partículas.

---

## 2. MEJORAS VISUALES Y DE ANIMACIÓN A IMPLEMENTAR

### 2.1 Rigging y Expresividad del Sepulturero (`entidades.py`)
1. **Squash & Stretch con Memoria Temporal:**
   - Agrega un atributo `self.squash_timer = 0.0` y `self.squash_tipo = None` en `Jugador`.
   - Cuando `salto_recien == True`: activa estiramiento vertical (`escala_y = 1.15`, `escala_x = 0.87`) durante `0.10 s`.
   - Cuando aterriza en el suelo (pasa de `en_suelo == False` a `True`): activa compresión de aterrizaje (`escala_y = 0.85`, `escala_x = 1.18`) durante `0.09 s` y emite 4 partículas de polvo suave en los pies.
2. **Postura de Pisotón Aéreo (Readability):**
   - Cuando el jugador está en el aire cayendo (`vy > 60`) y tiene la Pala o Guadaña (`tiene_pala == True`), dibuja el arma apuntando verticalmente hacia abajo bajo sus botas con un destello en la punta. Así el jugador **sabe visualmente** que puede aplastar enemigos como en *Shovel Knight*.
3. **Evolución Visual del Farol y del Arma según el Pacto del Farol:**
   - **Normal:** Farol con halo cálido (`FAROL_CALIDO`) y llama turquesa cuando el Dash está listo.
   - **Con Manto del Farol (`escudo_farol == True`):** Halo protector doble con runas celestes orbitando lentamente alrededor del Sepulturero.
   - **Con Filo de Ánima (`filo_anima == True`):** La hoja de la pala/guadaña desprende una estela dorada/turquesa al atacar.

### 2.2 Atmósfera Viva por Bioma (60 FPS Cero Lag en `juego.py`)
Crea un sistema ligero de **Partículas Ambientales de Bioma** (máximo 25 partículas en pantalla recicladas en el espacio de la cámara) que diferencie radicalmente la sensación de cada nivel:
- **Tema `"camposanto"` (Preludio y Nivel 1):** Niebla rastrera azulada a ras del suelo y pequeñas motas de luz turquesa (fuegos fatuos) que flotan suavemente hacia arriba.
- **Tema `"cripta"` (Nivel 2):** Haz de luz lunar diagonal tenue en los ventanales del fondo y motas de polvo gris/plata suspendidas en el aire.
- **Tema `"osario"` (Nivel 3):** Brasas carmesí y cenizas de hueso que ascienden desde el abismo inferior, intensificándose cuando el jugador entra en la arena del Custodio (`B`).

### 2.3 Feedback Multisensorial de Nuevas Mecánicas (`particulas.py` y `audio.py`)
1. **Losa Quebradiza (`~`):**
   - Mientras tiembla (`0.40 s`): caen piedritas/polvo hacia abajo.
   - Al romperse: sonido seco de fractura ósea y estallido de 8 fragmentos de hueso.
2. **Campana de Resonancia (`I`):**
   - Al golpearla o pisarla: onda circular expansiva turquesa/dorada y sonido armónico de campana tubular (`sintetizar_sfx` con armónicos en quinta justa).
3. **Consagración en Farol (`F`):**
   - Columna vertical de partículas celestes y doradas que sube desde el farol, acompañada de un acorde ascendente según el Tier alcanzado.

---

## 3. CRITERIOS DE ACEPTACIÓN
- [ ] Uso obligatorio de cachés de superficies (`convert_alpha()`) para que ningún efecto de luz o partícula degrade los **60 FPS**.
- [ ] Si `juego.reducir_movimiento == True` (Accesibilidad `F1`), se atenúan los flashes intensos y sacudidas sin perder la claridad de telegrafía.
- [ ] `tests/test_logica.py` y `tests/test_hud.py` pasan al 100%.