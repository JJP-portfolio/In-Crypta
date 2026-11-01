# PROMPT PRIORIDAD 2: Rediseño de Niveles, Curva de Dificultad (Sierra) y Duración (7 a 13 min)

> **Modo de ejecución:** Pegar este documento completo en una instancia de **Gemini 3.8 Flash (Agy)** en modo *Goal Automático* **después** de haber completado la Prioridad 1.

---

## 1. Rol y Objetivo del Orquestador

Actuás como **Lead Level Designer** especialista en plataformas 2D de precisión y pedagogía lúdica (*Sierra de Dificultad* y las *5 Etapas de Progresión* de la cátedra de la UNAHUR). Coordinás 3 sub-agentes para rediseñar íntegramente `niveles.py` (Preludio/Tutorial y Niveles 1, 2 y 3) y limpiar `niveles_rediseñados.py`.

---

## 2. Parámetros Físicos Inmutables (Para Cálculos de Saltos)

Todos los mapas ASCII deben diseñarse midiendo las distancias reales del motor (`TILE = 32` px):
*   **Salto puro desde el suelo:** alcanza hasta $6.3\text{ tiles}$ ($204\text{ px}$). Por lo tanto, un salto cómodo sin dash debe medir entre **$3\text{ y }4\text{ tiles}$** (máximo $5\text{ tiles}$ para exigencia aislada). Altura máxima de salto: **$3.5\text{ a }4\text{ tiles}$**.
*   **Salto + Dash desde el suelo:** alcanza hasta $11.4\text{ tiles}$ ($367\text{ px}$). Un foso que obligue a usar Dash debe medir entre **$6\text{ y }8\text{ tiles}$**.
*   **Encadenamiento Salto + Dash + Pisotón en Enemigo + Dash (Nivel 2 y 3):** Permite cruzar fosos de **$12\text{ a }16\text{ tiles}$** colocando enemigos (`E`, `C` o `m`) sobre pequeñas losas o flotando en medio del abismo como "trampolines".

---

## 3. Estructura de Niveles y Pacing (7 a 13 Minutos Humano Promedio)

Para que un jugador humano promedio tarde entre **$7\text{ y }13\text{ minutos}$** en completar la experiencia (contemplando la lectura del escenario, la recolección de almas y $3\text{ a }6$ muertes/reintentos desde los faroles), los niveles deben seguir una progresión creciente de longitud (`Preludio < Nivel 1 < Nivel 2 < Nivel 3`) y aplicar la **Sierra de Dificultad** (cada vez que se entrega un ítem nuevo, la dificultad baja a una zona de *Práctica Segura* antes de volver a subir).

### 3.1. Preludio / Tutorial: "El Umbral del Sepulturero" (`NIVEL_TUTORIAL`, ~80 cols $\times$ 14 filas)
*   **Objetivo:** Enseñar movimiento, sensibilidad del salto (salto corto vs. salto manteniendo barra espaciadora), lectura de las Almas (`o`) como guía espacial y uso del primer Farol (`F`).
*   **Regla de oro:** **Cero muerte instantánea.** Los fosos de práctica tienen piso abajo y escalones para volver a subir si el jugador se cae (*Práctica Segura*).
*   **Flujo:**
    1. Caminar y saltar escalones de $1\text{ tile}$ (salto corto) y $3\text{ tiles}$ (salto mantenido).
    2. Foso con trinchera segura abajo de $4\text{ tiles}$ guiado por un arco de Almas (`o`).
    3. Encender un Farol (`F`) tras juntar $5$ almas para ver cómo se activa el resguardo.
    4. Cruzar el portón (`G`) hacia el Nivel 1.

### 3.2. Nivel 1: "El Camposanto" (`NIVEL_1`, ~150 cols $\times$ 18 filas — Tiempo estimado: 2 a 3 min)
*   **Mecánicas activas:** Salto simple al inicio $\rightarrow$ Desbloqueo del **Dash (`D`)** tras los primeros saltos $\rightarrow$ Esquivar enemigos. (**Aún NO hay arma `W`**).
*   **Flujo de la Sierra de Dificultad:**
    1. **Beat 1 (Presentación y Salto Básico - cols 0 a 30):** El jugador realiza $3$ o $4$ saltos básicos sobre tumbas y huecos de $3\text{ a }4\text{ tiles}$ guiados por almas (`o`). Ve al primer enemigo (`E`) en una zona amplia donde debe aprender a **saltarlo por encima sin tocarlo**.
    2. **Beat 2 (Adquisición del Dash y Práctica Segura - cols 31 a 60):** Altar iluminado con el **Amuleto de Sombras (`D`)**. Inmediatamente después, un hueco de $6\text{ tiles}$ con piso de seguridad abajo (sin pinchos ni vacío mortal): si el jugador no usa Dash, cae en la trinchera y sube por una escalera para volver a intentarlo.
    3. **Beat 3 (Checkpoint 1 y Exigencia Aislada - cols 61 a 105):** Primer **Farol (`F`)**. Ahora los fosos de $6\text{ a }7\text{ tiles}$ tienen peligro real. Se combinan saltos con Dash aéreo para pasar por encima de moradores (`E`) que patrullan plataformas estrechas.
    4. **Beat 4 (Combinación y Dominio del Nivel 1 - cols 106 a 150):** Segundo **Farol (`F`)**. Secuencia rítmica de plataformas, huecos de $4\text{ tiles}$ (salto puro) alternados con huecos de $7\text{ tiles}$ (salto + dash) y enemigos patrullando antes del Portón (`G`).

### 3.3. Nivel 2: "La Cripta" (`NIVEL_2`, ~190 cols $\times$ 18 filas — Tiempo estimado: 3 a 4 min)
*   **Mecánicas activas:** Salto + Dash (ya aprendido) $\rightarrow$ Desbloqueo del **Arma (`W` - Pala)** $\rightarrow$ **Ataque y Pisotón (Stomp) con recarga de Dash aéreo** $\rightarrow$ Plataformas móviles (`M`, `V`).
*   **Flujo de la Sierra de Dificultad:**
    1. **Beat 1 (Recall de Nivel 1 - cols 0 a 25):** Un salto con Dash inicial para recordar controles, que desemboca en el **Altar de la Pala (`W`)**.
    2. **Beat 2 (Práctica Segura de Arma y Pisotón - cols 26 a 65):**
        *   Primero, un enemigo (`E`) en un pasillo seguro para probar el golpe frontal.
        *   Luego, una cornisa elevada con un enemigo abajo y una plataforma alta a la derecha: un cartel espacial y un arco de almas indican **"SALTÁ ENCIMA DEL ENEMIGO PARA REBOTAR Y RECUPERAR TU DASH"**. El piso debajo es seguro por si falla el primer intento.
    3. **Beat 3 (Checkpoint 1 y Encadenamiento Salto + Pisotón + Dash - cols 66 a 120):** Primer **Farol (`F`)**. Se introducen fosos anchos ($10\text{ a }12\text{ tiles}$) con un enemigo sobre un pilar central o una polilla/cuervo en medio: el jugador debe hacer `Salto -> Dash -> Pisotón sobre el enemigo -> Rebote -> Segundo Dash` para llegar al otro lado.
    4. **Beat 4 (Plataformas Móviles y Dominio - cols 121 a 190):** Segundo **Farol (`F`)**. Se integran plataformas móviles horizontales (`M`) y verticales (`V`), guardias melee (`L`) y un desafío final de encadenar pisotón + dash antes del Portón (`G`).

### 3.4. Nivel 3: "El Osario" (`NIVEL_3`, ~250 cols $\times$ 18 filas — Tiempo estimado: 4 a 6 min)
*   **Mecánicas activas:** Combinación total $\rightarrow$ **Mini-Boss (`K`)** $\rightarrow$ **Power-Up de Arma (`X`)** $\rightarrow$ **Clímax y Boss Final (`B`)**.
*   **Flujo de la Sierra de Dificultad:**
    1. **Acto I (Exigencia Combinada - cols 0 a 65):** Arranca exigiendo salto, dash, plataformas móviles y pisotones encadenados sobre enemigos. Rutas de almas (`o`) que premian con vidas extra y escudo antes del primer **Farol (`F`)** en col ~65.
    2. **Acto II (Arena del Mini-Boss y Power-Up - cols 66 a 125):** El jugador entra a la cámara del **Carcelero (`K` - Mini-Boss)**. Debe esquivar su embestida y matarlo de $3$ golpes/pisotones. Al vencerlo, accede al pedestal con el **Power-Up `'X'` (Guadaña Consagrada)** y activa el segundo **Farol (`F`)**.
    3. **Acto III (Práctica del Power-Up y Ascenso Climático - cols 126 a 195):** Pasarela con guardias (`L`) y enemigos donde el jugador siente el poder del nuevo alcance (`76 px`) de su arma mejorada, seguida de una sección de ascenso/plataformeo intenso con encadenamiento de saltos, pisotones y dashes que construye la tensión del **Clímax**.
    4. **Acto IV (Antesala y Batalla contra El Custodio - cols 196 a 250):**
        *   **Tercer Farol (`F`)** justo antes de entrar a la arena (para que morir contra el Boss nunca obligue a repetir el nivel ni el Mini-Boss).
        *   **Arena del Jefe Final (`B` - El Custodio):** Cámara amplia con dos plataformas laterales elevadas (para facilitar el pisotón en Fase 2).
        *   Fase 1 ($3$ golpes): vulnerable a ataques de la Guadaña (`X`) y pisotones tras lanzar sus ondas.
        *   Fase 2 ($3$ golpes): activa su armadura carmesí; **solo recibe daño de pisotón aéreo teniendo el Power-Up `'X'`**. Al derrotarlo, se abre el Portón Final (`G`).

---

## 4. Validación Automática de Niveles

1. Creá un script o test en `tests/test_logica.py` que valide matemáticamente que:
    * `NIVEL_TUTORIAL`, `NIVEL_1`, `NIVEL_2` y `NIVEL_3` tienen exactamente un `P` y un `G`.
    * `NIVEL_1` contiene `'D'` y `'F'`, pero **NO** contiene `'W'` ni `'X'`.
    * `NIVEL_2` contiene `'W'` y `'F'`.
    * `NIVEL_3` contiene `'K'` (Mini-Boss), `'X'` (Power-Up), `'B'` (Boss) y al menos $3$ `'F'` (Checkpoints).
    * Ningún enemigo (`E`, `L`, `K`, `B`) está flotando en el aire sin suelo `#` debajo.
    * `Longitud(NIVEL_TUTORIAL) < Longitud(NIVEL_1) < Longitud(NIVEL_2) < Longitud(NIVEL_3)`.
2. Limpiá `niveles_rediseñados.py` para que las 3 `SALAS_PRUEBA` sean salas limpias hechas a mano que aíslen: Sala 1 (Salto + Dash), Sala 2 (Arma + Encadenamiento Pisotón-Dash), Sala 3 (Mini-Boss + Power-Up + Boss).