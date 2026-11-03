# PROMPT DE EJECUCIÓN AUTÓNOMA (`/goal`) PARA `agy-cli` — REESTRUCTURACIÓN DE MENÚS (CERO SLOP), RECUPERACIÓN DE CHIMES ESCALONADOS Y MEJORA PROCEDURAL

> **Comando sugerido:** `agy-cli /goal -f prompt_ejecucion_agy_cli.md -c argon_overhaul_context.xml`  
> **Modelo objetivo:** Gemini 3.8 Flash con delegación obligatoria en **Sub-Agentes**.

---

## ROL Y MISIÓN DEL AGENTE ORQUESTADOR

Actúa como **Argon**, Director Técnico de Arte e Ingeniero Principal de *IN CRYPTA*. Tu misión es coordinar un equipo de **Sub-Agentes especializados** para:
1. **Investigar en `.git` y restaurar los *chimes* pentatónicos escalonados** que sonaban al recoger gemas/almas y que fueron accidentalmente sobrescritos.
2. **Reestructurar visual y estructuralmente todos los menús**, eliminando el *slop* (textos largos de cátedra, teoría MDA en créditos, descripciones técnicas redundantes de 3 renglones por botón) para dejar una interfaz gótica limpia, directa y centrada.
3. **Potenciar el arte procedural en las 3 áreas** (*Camposanto*, *Cripta*, *Osario*), mejorando fondos, bloques, enemigos y efectos visuales/sonoros.
4. **Blindar los 3 niveles de calidad:**
   * **Calidad Alta (0 - Desktop Nativo):** Pipeline Procedural Gótico completo (`PROC`), Bloom, penumbra substractiva, halos aditivos y 100% partículas.
   * **Calidad Media (1 - Equilibrado):** Pipeline `SNES` 16-bit biselado, penumbra ligera y 50% partículas.
   * **Calidad Baja (2 - Export Web / Modo Sony Vaio):** Pipeline `NES` 8-bit puro, **cero superficies `SRCALPHA` de pantalla completa** (sin viñeta, sin penumbra, sin bloom, sin scanlines), paneles de HUD `.convert()` 100% opacos y 60 FPS estables.

---

## 1. GUARDRAILS ESTRICTOS (PROHIBICIONES)

1. 🚫 **NO TOCAR FÍSICAS NI COLISIONES:** Prohibido alterar constantes de salto, gravedad, velocidades, timers o `self.rect` / `rect_ataque()` en `config.py`, `entidades.py` o `nivel.py`.
2. 🚫 **NO TOCAR MAPAS:** Prohibido modificar las cadenas ASCII en `niveles.py`.
3. 🧪 **TESTS 100% EN VERDE:** `pytest tests/` debe seguir pasando los 51 tests sin fallos y `HudLayout.construir().solapamientos()` debe ser `[]`.

---

## 2. PLAN DE EJECUCIÓN POR SUB-AGENTES

### PASO 0 — Creación de Rama (Orquestador)
1. Ejecuta `git status` y crea una nueva rama limpia para esta feature:
   ```bash
   git checkout -b feat/menu-clean-procedural-chimes
   ```

### SUB-AGENTE 1 — Arqueólogo Git e Ingeniero de Audio (`audio.py` y `juego.py`)
**Misión:** Recuperar los *chimes* escalonados de las gemas/almas y perfeccionar el audio procedural.
1. Ejecuta en la terminal `git log -S "notas_almas" -p -- audio.py` para verificar el historial del bloque de síntesis de `alma_1..alma_6`.
2. **Corrige el bug en `audio.py`:**
   * Actualmente, cuando existe `alma_ref.wav`, el bucle inicial llena `self.sonidos["alma"]` y luego el `if "alma" in self.sonidos:` sobrescribe `alma_1` a `alma_6` con ese único sonido plano, matando la escala ascendente.
   * Reemplaza la sección `# 6. Almas espectrales y escala pentatónica de ánimas` en `audio.py` por el código de `<file path="audio.py">` de `argon_overhaul_context.xml`: sintetiza siempre `alma_1` a `alma_6` sobre la escala pentatónica `[523.25, 587.33, 659.25, 783.99, 880.00, 1046.50]` Hz con armónicos de octava (`nota * 2.0`), quinta FM (`nota * 1.5`) y brillo (`nota * 3.0`), y elimina `"alma"` de `self.variaciones` para que nunca se elija una nota al azar sino el peldaño exacto del combo.
3. En `juego.py` (`actualizar_almas`):
   * Aumenta `self.almas_combo_timer = 2.2` (antes `1.3`) para que al recoger gemas/almas seguidas la escala suba claramente de `alma_1` hasta `alma_6`.
   * Cuando `self.almas_combo_count == 6`, emite un destello extra de partículas doradas/turquesas en `alma.rect.center`.

### SUB-AGENTE 2 — Especialista en UI/UX y Eliminación de Slop en Menús (`juego.py`)
**Misión:** Limpiar por completo las pantallas de Título, Menú Principal, Selección de Nivel, Configuración, Pausa y Créditos.
1. Aplica el código del bloque `<file path="juego.py" action="clean_menu_slop_and_upgrade_procedural_backgrounds">` de `argon_overhaul_context.xml`:
   * **Pantalla de Título (`dibujar_titulo`):** Marco compacto centrado (`620x320`), título, subtítulo, línea divisoria dorada y prompt pulsante `"PRESIONÁ [ENTER] PARA ENTRAR"`. Elimina el párrafo largo de introducción.
   * **Menú Principal (`dibujar_menu_principal`):** Elimina el subtítulo académico `"UNAHUR"` y las descripciones secundarias largas debajo de cada botón. Deja 4 botones limpios, centrados y elegantes: `"INICIAR CAMPAÑA"`, `"SELECCIÓN DE CAPÍTULO"`, `"CONFIGURACIÓN"`, `"CRÉDITOS"`.
   * **Selección de Capítulo (`dibujar_seleccion_nivel`):** Elimina el *slop* técnico (`"80 cols"`, `"150 cols"`, etc.) y deja solo la insignia (`0`, `I`, `II`, `III`, `★`), el título del acto y una línea atmosférica breve.
   * **Configuración (`dibujar_configuracion`):** Elimina los subtítulos redundantes dentro de cada fila y el cuadro gigante inferior. Muestra una lista limpia de 2 columnas (`Etiqueta` a la izquierda, `◂ Valor ▸` a la derecha) y una sola línea inferior con el resumen de teclas del preset activo.
   * **Créditos (`dibujar_creditos`):** Borra todas las explicaciones de `"MATRIZ MDA"`, `"LOS 4 TIPOS DE INTERFAZ"` y `"LOS 5 PRINCIPIOS DE UX"`. Deja únicamente el título del juego, los 3 integrantes del equipo y la dedicatoria a Edgar Allan Poe.

### SUB-AGENTE 3 — Artista Procedural de Fondos, Tiles y Biomas (`nivel.py` y `juego.py`)
**Misión:** Elevar la calidad visual procedural de los 3 biomas y garantizar el rendimiento en Calidad Baja (Web/Vaio).
1. En `config.py`, fija `PERFIL_WEB_CALIDAD = 2` para que el export web arranque directamente en el perfil de 60 FPS sin penumbra pesada.
2. En `juego.py` (`dibujar`):
   * En **Calidad Baja (`self.config_calidad_idx == 2`)**: no blitees `self.vineta` ni `self.mascara_penumbra` ni ejecutes `_aplicar_bloom` ni `_superficie_scanlines`.
   * En `dibujar_fondo_camposanto`, `dibujar_fondo_cripta` y `dibujar_fondo_osario`:
     * Añade detalles procedurales deterministas en **Calidad Alta/Media**: siluetas de verjas de hierro forjado y cruces inclinadas en el horizonte del *Camposanto*; arcos góticos con nervaduras y candelabros colgantes en la *Cripta*; pilares de cráneos apilados y brasas ascendentes en el *Osario*.
3. En `nivel.py` (`dibujar_solidos` y `dibujar_decoraciones`):
   * Asegúrate de que el modelo `"PROC"` (Calidad Alta) dibuje musgo colgante, grietas deterministas, argollas de hierro en muros de cripta y nichos de calaveras en el osario, manteniendo siempre el **Walkable Edge Cue** (bisel superior brillante $Y > 175$ + corte negro de 2px debajo).

### SUB-AGENTE 4 — Validador QA y Pruebas (`tests/`)
1. Ejecuta `pytest tests/` y verifica que los **51 tests** pasen en verde.
2. Ejecuta una prueba funcional en modo headless verificando la síntesis de `alma_1..alma_6`, el renderizado de todos los menús reestructurados (`titulo`, `menu`, `seleccion_nivel`, `configuracion`, `creditos`, `pausa`) y los 3 niveles de calidad (`0`, `1`, `2`).
3. Confirma con `git status` y `git diff --stat` que todos los cambios estén limpios en la rama `feat/menu-clean-procedural-chimes`.