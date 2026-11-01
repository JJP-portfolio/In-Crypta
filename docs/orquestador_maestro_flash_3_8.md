# Orquestador Maestro — Refactorización y Rediseño de IN CRYPTA (Gemini 3.8 Flash)

> **Propósito de este archivo:** Servir como índice de control y protocolo de ejecución para instancias de **Gemini 3.8 Flash (Agy)** trabajando en modo *Goal Automático* con sub-agentes.

---

## 1. Visión General del Proyecto y Objetivo Académico

**IN CRYPTA** es un proyecto universitario para las materias *Taller de Diseño Conceptual* e *Introducción a los Videojuegos* (UNAHUR). **No busca ser un juego AAA**, sino una pieza de diseño lúdico ejemplar, clara, justa y congruente donde se evalúa la aplicación práctica de:
1. **Juegos como Sistemas** (Crawford, Salen & Zimmerman): Objetos, atributos, relaciones internas, entorno delimitado, reglas y resultados cuantificables; *Meaningful Play* (discernible e integrado) y *Feedback Loops* (positivos y negativos).
2. **Matriz MDA** (Hunicke, LeBlanc, Zubek): De las Mecánicas a las Dinámicas (fomentadas vs. inesperadas) y a las Estéticas principales (**Desafío**, **Sensación** y **Fantasía/Descubrimiento**).
3. **Curva y Sierra de Dificultad**: Equilibrio entre demanda y habilidad; los 4 tipos de desafío (Mecánico, Cognitivo, Estratégico, Percepción); las 5 etapas de progresión (*Presentación $\rightarrow$ Práctica segura $\rightarrow$ Exigencia aislada $\rightarrow$ Combinación $\rightarrow$ Dominio*); dificultad diseñada vs. artificial; y ajustes invisibles (*Coyote Time*, *Jump Buffer*, hitboxes benévolas).
4. **Diseño UI/UX**: Los 5 principios de UX y los 4 tipos de interfaz (**No diegética**, **Diegética**, **Espacial** y **Meta**).
5. **Entrega obligatoria en GDevelop 5.6 (`gd.games`)**: Todo el prototipo en Python (`pygame-ce`) debe exportarse casi $1:1$ a un proyecto nativo de GDevelop (`export/gdevelop_nativo/IN_CRYPTA_NATIVO.json`), reemplazando los gráficos procedurales por **assets gratuitos de Pixel Art** (estilo *Gothicvania* de itch.io / OpenGameArt / CC0) con animaciones fluidas y coherencia estética.

---

## 2. Orden de Prioridad para Instancias de Agy (Flash 3.8)

Ejecutá cada archivo en una instancia limpia de Gemini 3.8 Flash en este orden estricto:

| Prioridad | Archivo de Prompt | Objetivo Principal | Entregable Verificable |
| :--- | :--- | :--- | :--- |
| **Prioridad 1** | `01_PRIORIDAD_1_SISTEMAS_Y_MECANICAS_MDA.md` | Refactorizar la progresión de mecánicas (Salto $\rightarrow$ Dash en Nivel 1 $\rightarrow$ Arma + Pisotón encadenado en Nivel 2 $\rightarrow$ Power-Up + Mini-Boss + Boss en Nivel 3) y el nuevo sistema simbiótico de Almas y Faroles. | `entidades.py`, `nivel.py`, `juego.py` y `tests/test_logica.py` en verde. |
| **Prioridad 2** | `02_PRIORIDAD_2_REDISEÑO_NIVELES_Y_CURVA_SIERRA.md` | Rediseñar el Preludio (Tutorial) y los 3 niveles aplicando la Sierra de Dificultad, las 5 etapas de aprendizaje y una duración de $7$ a $13$ minutos para un jugador humano promedio. | `niveles.py` validado físicamente sin huecos imposibles ni errores de parser. |
| **Prioridad 3** | `03_PRIORIDAD_3_UI_UX_MENUS_Y_HUD.md` | Plasmar los 4 tipos de UI (Diegética en el farol, Espacial en carteles del tutorial, Meta en salud crítica, No diegética en el riel HUD) y los 5 principios de UX en todos los menús. | `hud.py`, menús de `juego.py` y `tests/test_hud.py` en verde. |
| **Prioridad 4** | `04_PRIORIDAD_4_EXPORTADOR_GDEVELOP_1_A_1_Y_PARIDAD.md` | Lograr paridad $1:1$ en el exportador nativo de GDevelop 5.6 (checkpoints funcionales sin reiniciar escena completa, cadena de pisotón + dash, mini-boss, boss y power-up). | `tools/exportar_todo.py`, `PARIDAD_OK` y `EVENTOS_OK`. |
| **Prioridad 5** | `05_PRIORIDAD_5_ASSETS_ITCHIO_Y_COHERENCIA_VISUAL_GDEVELOP.md` | Integrar un pipeline de assets gratuitos (Pixel Art gótico de itch.io / CC0) con animaciones multipose en GDevelop manteniendo las hitboxes exactas. | Proyecto GDevelop listo para abrir, compilar y subir a `gd.games`. |

---

## 3. Reglas Globales para el Orquestador

1. **No romper los tests:** Ningún sub-agente puede dar por terminada su tarea si `tests/test_logica.py`, `tests/test_hud.py`, `tools/validar_eventos_gd.py` o `tools/verificar_paridad.py` fallan.
2. **Commits atómicos por ruta:** Nunca ejecutar `git add .` ni `git add -A`. Siempre commitear por archivo modificado tras pasar los tests.
3. **Simplicidad sobre complejidad:** No inventar mecánicas nuevas fuera de las pedidas (Salto variable con Coyote Time, Dash, Arma con 1 Power-Up, Pisotón al tener el arma que recarga el Dash, Almas y Faroles Checkpoint).