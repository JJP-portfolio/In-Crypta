# PROMPT PRIORIDAD 3: Aplicación Teórica de UI/UX, los 4 Tipos de Interfaz y Flujo de Menús

> **Modo de ejecución:** Pegar este documento completo en una instancia de **Gemini 3.8 Flash (Agy)** en modo *Goal Automático* **después** de haber completado la Prioridad 2.

---

## 1. Rol y Objetivo del Orquestador

Actuás como **UI/UX Director** aplicando estrictamente el apunte oficial de **Diseño UI/UX de la UNAHUR** (`UIUX.pdf`). Tu misión es lograr que los **5 principios de UX** y los **4 tipos de UI** estén visiblemente plasmados en **IN CRYPTA** (`hud.py`, `juego.py`, `entidades.py`, `nivel.py`) para que el alumno pueda defenderlos y mostrarlos durante la evaluación oral.

---

## 2. Los 4 Tipos de UI a Implementar y Pulir

Cada uno de los 4 tipos de interfaz de la teoría debe tener una implementación clara, limpia y justificable en el juego:

1.  **UI No Diegética (Riel Superior del HUD en `hud.py`):**
    *   *¿El personaje lo ve?* No. *¿Es parte del mundo?* No.
    *   Mantener el riel superior fijo (`1232 x 72` px) sin *layout shifts* (el ancho del panel derecho **no** debe saltar al recoger el Dash o la Pala).
    *   Mostrar con ícono + número:
        *   Izquierda: Vidas (`[HP] 3/5`), corazones (más un contorno celeste en el primer corazón si tiene activo el **Manto del Farol**) y Tiempo (`01:23`).
        *   Centro: Etapa actual (`PRELUDIO`, `NIVEL 1/3 · EL CAMPOSANTO`, etc.) o la **Barra de Salud del Mini-Boss / Boss Final** cuando estén en pantalla.
        *   Derecha (Grilla $2\times2$): `[ALMA] X/Total`, `[DASH] -- / LISTO / 0.4s`, `VIDA EXTRA X/10` (con las 10 cuentas del rosario) y `[ARMA] -- / PALA / GUADAÑA`.
2.  **UI Diegética (El Farol del Sepulturero y los Faroles de Checkpoint en `entidades.py`):**
    *   *¿El personaje lo ve?* Sí. *¿Es parte del mundo?* Sí.
    *   **El farol que lleva el sepulturero en la mano** debe comunicar su estado real dentro de la ficción:
        *   Cuando el Dash está disponible (`dash_listo() == True`), el centro de la llama del farol del jugador tiene una chispa **turquesa brillante**. Cuando está en cooldown o gastado en el aire, la llama es ámbar tenue.
        *   Cuando el jugador recoge el Power-Up `'X'` en el Nivel 3, el farol proyecta un **halo violeta consagrado**.
    *   **Los Faroles de Checkpoint (`F`)** pasan de estar apagados (hierro frío) a encenderse con fuego azul/turquesa al activarlos, indicando diegéticamente que el alma del sepulturero está a salvo allí.
3.  **UI Espacial (Lápidas/Carteles de Enseñanza en el Mundo en `nivel.py` y `juego.py`):**
    *   *¿El personaje lo ve?* No (son indicaciones de controles para el jugador). *¿Está en el espacio del juego?* Sí, anclada a coordenadas del mundo $(x, y)$.
    *   En el **Preludio (Tutorial)** y al encontrar los altares de `'D'` (Nivel 1), `'W'` (Nivel 2) y `'X'` (Nivel 3), cuando el jugador está a menos de $140\text{ px}$ del punto clave, debe flotar suavemente **sobre el escenario** (usando coordenadas transformadas por `camara.aplicar_rect`) un cartel espacial compacto con borde dorado y fondo translúcido que indique la acción exacta:
        *   `[ESPACIO] Mantener para salto alto`
        *   `[SHIFT] Dash en el aire`
        *   `[A / J] Atacar · ¡Saltá sobre enemigos para rebotar y recargar Dash!`
    *   Esto evita obligar al jugador a desviar la vista hacia arriba en medio de un salto.
4.  **UI Meta (Efectos Sensoriales de Pantalla en `juego.py`):**
    *   *¿El personaje lo ve?* No como interfaz. *¿Qué hace?* Simula una sensación física/sensorial del personaje en el plano 2D de la pantalla.
    *   Cuando al jugador le queda **$1\text{ sola vida}$**, la viñeta perimetral carmesí (`vineta_carmesi`) late suavemente en los bordes de la pantalla sincronizada con el sonido del latido cardíaco (`55 Hz`), y al romper el Manto del Farol se produce un destello turquesa protector.

---

## 3. Los 5 Principios de UX y Sistema de Menús (`juego.py`)

Revisar y pulir todos los estados de menú para cumplir los 5 principios del PDF de la cátedra:
1.  **Facilidad para encontrar lo importante:** Jerarquía visual clara (títulos en Dorado Litúrgico, opción seleccionada con indicador `▸` y recuadro iluminado).
2.  **Rapidez para entender qué hacer:** Leyenda constante al pie de cada menú (`[↑/↓] Elegir · [ENTER] Confirmar · [ESC] Volver`).
3.  **Comodidad según la plataforma (PC / Web):** Permitir siempre controles duales cómodos: Flechas o `WASD` para moverse/navegar, `ESPACIO` / `W` / `↑` para saltar, `SHIFT` / `X` para Dash, `A` / `J` / `Z` para atacar, `P` / `ESC` para Pausa.
4.  **Consistencia entre menús y pantallas:** Todos los menús (`Pantalla de Título`, `Menú Principal`, `Selección de Nivel`, `Pausa`, `Derrota`, `Victoria`, `Créditos`) deben compartir la misma paleta, el mismo marco heráldico con esquinas doradas y la fuente `NotoSerifDisplay-Bold`.
5.  **Fluidez entre acciones y menús:**
    *   En el **Menú Principal**, ordenar claramente las opciones:
        1. `JUGAR CAMPAÑA (Preludio + 3 Niveles)` — *Al elegir Jugar, comienza en el Preludio/Tutorial y al cruzar su portón pasa automáticamente al Nivel 1 sin volver al menú, logrando una experiencia narrativa continua!*
        2. `SELECCIÓN DE NIVEL` — *Permite elegir directamente: Preludio, Nivel 1 (El Camposanto), Nivel 2 (La Cripta), Nivel 3 (El Osario) o Salas de Prueba.*
        3. `CRÉDITOS & MARCO TEÓRICO` — *Muestra los integrantes y el resumen MDA.*
    *   En el **Menú de Pausa**, incluir opciones interactivas navegables con flechas (`CONTINUAR`, `REINICIAR DESDE FAROL`, `REINICIAR NIVEL`, `VOLVER AL MENÚ`).

---

## 4. Verificación Automática

Ejecutar y dejar en verde:
```bash
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_hud.py
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_logica.py
```