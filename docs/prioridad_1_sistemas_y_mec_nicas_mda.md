# PROMPT PRIORIDAD 1: Refactorización de Sistemas, Mecánicas MDA, Combate Encadenado y Sistema de Almas/Faroles

> **Modo de ejecución:** Pegar este documento completo en una instancia de **Gemini 3.8 Flash (Agy)** en modo *Goal Automático*.

---

## 1. Rol y Objetivo del Orquestador

Actuás como **Lead System Architect y Game Designer** coordinando 3 sub-agentes especializados para refactorizar el núcleo jugable de **IN CRYPTA** en Python (`config.py`, `entidades.py`, `nivel.py`, `juego.py`) y su suite de pruebas (`tests/test_logica.py`).

Tu objetivo es alinear las reglas del sistema con la **Matriz MDA**, el concepto de **Meaningful Play** (discernible e integrado) y los **Feedback Loops** vistos en la cátedra.

---

## 2. Arquitectura de Sub-Agentes para esta Fase

*   **Sub-Agente 1A (Física, Moveset y Progresión de Habilidades):** Ajusta el salto, el dash, el arma, el power-up y la regla de pisotón (stomp) encadenado en `entidades.py` y `config.py`.
*   **Sub-Agente 1B (Sistema Simbiótico de Almas y Faroles Checkpoint):** Rediseña la relación entre las Almas (`o`) y los Faroles (`F`) en `entidades.py`, `nivel.py` y `juego.py` para que tengan un propósito real en el sistema.
*   **Sub-Agente 1C (Mini-Boss, Boss Final y QA):** Implementa al Mini-Boss en el Nivel 3, ajusta la condición del Power-Up necesario para vencer al Boss Final y actualiza `tests/test_logica.py`.

---

## 3. Especificaciones Técnicas Obligatorias

### 3.1. Moveset Simple, Preciso y Encadenable (Sub-Agente 1A)
No debés agregar mecánicas complicadas. El juego utiliza únicamente estas acciones:
1.  **Salto Simple con Sensibilidad y Asistencias Invisibles:**
    *   Mantener `SALTO = -620.0`, `GRAVEDAD = 1500.0`, `CORTE_SALTO = 0.45` (al soltar la tecla de salto mientras `vy < 0`, se multiplica `vy *= CORTE_SALTO` para permitir saltos bajos y altos según el tiempo de pulsación).
    *   Asistencias invisibles obligatorias: `COYOTE_TIME = 0.18` s y `JUMP_BUFFER = 0.15` s.
2.  **Dash (`DashPowerUp`, símbolo `'D'`):**
    *   El jugador inicia en el Preludio y en el inicio del Nivel 1 con `tiene_dash = False`.
    *   En el **Nivel 1**, tras superar los primeros saltos básicos, el jugador recoge el ítem `'D'` (`DashPowerUp`), que activa `tiene_dash = True`.
    *   A partir del Nivel 2 y Nivel 3, el jugador ya inicia con `tiene_dash = True`.
    *   Un uso en el aire (`DASH_USOS_AIRE = 1`), velocidad `560.0` px/s durante `0.20` s, cooldown `0.60` s.
3.  **Arma (`PalaRecogible`, símbolo `'W'`) y Mecánica de Pisotón Encadenado:**
    *   En el **Nivel 1**, `tiene_pala = False`. El jugador **NO** puede atacar ni matar enemigos saltándoles encima (si los toca desde cualquier ángulo en el Nivel 1, recibe daño; debe esquivarlos o usar el Dash sobre ellos).
    *   En el **Nivel 2**, el jugador recoge el arma `'W'` (`tiene_pala = True`).
    *   **Regla clave de Game Design:** Recoger el arma (`tiene_pala == True`) habilita **dos cosas**:
        1. El ataque frontal cuerpo a cuerpo (`A` / `J` / `Z`).
        2. **El Pisotón (Stomp) sobre enemigos:** Caer sobre la cabeza de un enemigo (`vy > 0` y `rect.bottom <= enemigo.rect.top + 18`) **solo mata al enemigo si `jugador.tiene_pala == True`**.
        3. **Encadenamiento Salto + Dash + Pisotón:** Cada vez que el jugador mata a un enemigo mediante **Pisotón** (o golpe aéreo), el jugador rebota hacia arriba (`vy = -REBOTE_ENEMIGO`) y **recupera instantáneamente su Dash aéreo** (`dash_usos_aire = DASH_USOS_AIRE` y `dash_cooldown = 0.0`). Esto convierte a los enemigos en "trampolines dinámicos" para encadenar `Salto -> Dash -> Pisotón en enemigo -> Rebote -> Nuevo Dash` para cruzar abismos largos.
4.  **Power-Up del Arma (`RangoPowerUp`, símbolo `'X'`) obligatorio para el Boss Final:**
    *   Se obtiene en el **Nivel 3** (tras superar al Mini-Boss).
    *   Aumenta el alcance del arma (`ATAQUE_ALCANCE_MEJORADO = 76`) y consagra el arma (`rango_ataque_mejorado = True`).
    *   **Requisito de victoria contra el Boss Final (`Custodio`):** En la Fase 2 del Jefe Final, la coraza espectral del Custodio **solo puede ser vulnerada si el jugador posee el Power-Up `'X'` (`rango_ataque_mejorado == True`)** al hacerle un pisotón o golpe en su ventana de vulnerabilidad. Si no tiene `'X'`, el ataque/pisotón rebota sin quitarle vida y muestra un aviso claro en el HUD.

### 3.2. Rediseño del Sistema de Almas (`o`) y Faroles Checkpoint (`F`) (Sub-Agente 1B)
Actualmente las almas se sienten desconectadas del checkpoint del farol. Vamos a unificarlos en un **Sistema Formal con Feedback Loops** sin perder la satisfacción de recolectarlas para marcar el camino:
1.  **Función de Percepción (Guía Espacial):** Las Almas (`o`) se colocan dibujando las parábolas de salto y las líneas rectas donde el jugador debe activar el Dash.
2.  **Función Sistémica Dual (Vínculo Alma $\leftrightarrow$ Farol):**
    *   **Loop Positivo 1 (Rosario de Vida):** Recolectar $10$ almas (`ALMAS_POR_VIDA = 10`) otorga $+1$ vida extra inmediata (hasta `VIDAS_MAXIMAS = 5`).
    *   **Loop Positivo 2 (Consagración en el Farol `'F'`):** Cuando el jugador toca un `FarolCheckpoint` (`F`):
        *   El farol se enciende de forma permanente y guarda `self.punto_reintento = (checkpoint.rect.x, checkpoint.rect.y - 4)`.
        *   **Curación y Consagración de Almas:** Encender un farol consume la energía del camino para **restaurar $+1$ vida** si el jugador está herido (por debajo de `VIDAS_INICIALES = 3`) y **asegura (banca) las almas recolectadas** hasta ese momento (`self.almas_consagradas = self.jugador.almas` y `self.almas_vida_consagradas = self.jugador.almas_para_vida`).
        *   Además, otorga un **"Manto del Farol"** (`jugador.escudo_farol = True` si el jugador recolectó al menos $5$ almas en el tramo previo): un aura celeste sutil que absorbe el próximo golpe letal sin perder una vida, premiando explícitamente haber recolectado las almas del camino antes de llegar al checkpoint.
3.  **Loop Negativo / Castigo Justo al Morir:**
    *   Si el jugador pierde una vida (pero le quedan vidas $> 0$), **NO** reinicia el nivel desde el principio si ya activó un farol: reaparece en `self.punto_reintento`, conserva sus vidas restantes, conserva sus armas/power-ups y recupera su contador de almas en el estado exacto que tenía consagrado en ese farol. Solo se reinician las almas posteriores al farol para que sigan sirviendo de guía visual en el tramo que falló.
    *   Si el jugador llega a $0$ vidas (`derrota`), al dar "Reintentar" vuelve a empezar el nivel desde el último Farol activado (o desde el inicio del nivel si no activó ninguno) con `VIDAS_INICIALES = 3`.

### 3.3. Mini-Boss del Nivel 3 (`Carcelero`, símbolo `'K'`) (Sub-Agente 1C)
El Nivel 3 necesita una estructura de ritmo climático con un **Mini-Boss** a mitad del nivel y el **Boss Final (`B`)** al cierre:
1.  Crear la clase `MiniJefe` (El Carcelero del Osario) en `entidades.py` e instanciarla en `nivel.py` al leer el símbolo `'K'`.
2.  **Atributos y Reglas del Mini-Boss:**
    *   Tamaño: `36 x 48` px, `vida = 3`.
    *   Patrulla una arena intermedia custodiando el altar del Power-Up `'X'`.
    *   Patrón claro y justo: Camina hacia el jugador $\rightarrow$ Telegrafía su ataque durante $0.55\text{ s}$ (brillo carmesí y sonido) $\rightarrow$ Lanza una embestida corta o una onda baja única $\rightarrow$ Queda cansado/vulnerable durante $1.3\text{ s}$ para que el jugador lo golpee con la pala o le salte encima (stomp).
    *   Al derrotarlo (`vida <= 0`), suelta una explosión de partículas, otorga $5$ almas y despeja el camino hacia el Power-Up `'X'`.

---

## 4. Criterios de Aceptación y Verificación Automática

Antes de finalizar tu ejecución, corré los siguientes comandos y asegurate de que todos pasen sin errores:

```bash
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_logica.py
```

*   Agregá tests unitarios en `tests/test_logica.py` para:
    1. Verificar que pisar a un enemigo **sin pala** (`tiene_pala = False`) daña al jugador, y **con pala** (`tiene_pala = True`) mata al enemigo, rebota y recarga `dash_usos_aire = 1`.
    2. Verificar que el Farol (`F`) guarda las almas consagradas, cura $1$ punto de vida si está por debajo de $3$ y otorga el escudo si recolectó $\ge 5$ almas.
    3. Verificar que el Mini-Boss (`K`) tiene $3$ de vida y puede ser derrotado con pala o pisotón.
    4. Verificar que la Fase 2 del Jefe Final (`B`) exige `rango_ataque_mejorado == True` (Power-Up `'X'`).