# PROMPT DE ORQUESTACIÓN — PRIORIDAD 4: UI/UX INTEGRAL (4 INTERFACES + 5 PRINCIPIOS), MENÚS Y REJUGABILIDAD COMERCIAL

> **MODO DE EJECUCIÓN:** Goal Automático / Autónomo con Orquestación de Sub-Agentes (Gemini 3.8 Flash).  
> **OBJETIVO FINAL:** Completar el empaquetado comercial de **IN CRYPTA** en `hud.py`, `juego.py` y `tests/`, asegurando la implementación perfecta de las **4 Interfaces**, los **5 Principios de UX**, la conexión real de todas las opciones de Configuración, y un sistema de **Rango Litúrgico + Estadísticas** al finalizar cada nivel y la campaña.

---

## 1. ROL Y DESPLIEGUE DE SUB-AGENTES

Actúas como **Lead UI/UX Designer & Release Director** de **IN CRYPTA**.  
Despliega **3 SUB-AGENTES ESPECIALIZADOS**:

1. **Sub-Agente 1 (Arquitecto del HUD y las 4 Interfaces):** Perfecciona `hud.py` y la UI Espacial/Meta en `juego.py`, asegurando cero solapamientos (`layout.solapamientos() == []`) y conectando los 3 modos de HUD (`Completo`, `Compacto`, `Inmersivo`).
2. **Sub-Agente 2 (Especialista en Menús, Pantallas de Transición y Rejugabilidad):** Mejora la pantalla de `nivel_completado` (mostrando resumen de Almas Consagradas, Tiempo del Nivel y Secretos antes de pasar al siguiente), el Menú de Pausa, el Selector de Niveles y la Pantalla de Victoria con **Rango Litúrgico (`S+`, `S`, `A`, `B`, `C`)**.
3. **Sub-Agente 3 (Ingeniero de QA Total):** Verifica y amplía `tests/test_hud.py` y `tests/test_logica.py` para garantizar que ningún cambio rompa las invariantes del proyecto.

---

## 2. ESPECIFICACIÓN DE UI/UX Y MENÚS

### 2.1 Matriz de las 4 Interfaces (Fagerholt & Lorentzon)
1. **Diegética (En la ficción del mundo):**
   - El Farol del Sepulturero cambia el color/intensidad de su llama según el estado del Dash y muestra las auras del **Manto del Farol** y **Filo de Ánima**.
   - Los Faroles de Checkpoint (`F`) encienden su llama azul con intensidad proporcional al Tier de almas consagradas.
   - El Altar de la Guadaña (`X`) muestra cadenas físicas mientras el Carcelero (`K`) está vivo.
2. **Espacial (En las coordenadas del mundo 2D):**
   - Carteles contextuales heráldicos (`dibujar_ui_espacial`) que aparecen suavemente a `<= 140 px` de distancia sobre altares (`D`, `W`, `X`), Faroles (`F`), Campanas (`I`) y puntos clave del Preludio.
   - Los textos de teclas se adaptan en tiempo real al Preset elegido por el jugador (`WASD Moderno` vs `Retro Arcada Z-X-C`).
3. **Meta (En el plano de la lente/pantalla):**
   - Viñeta carmesí reactiva en los bordes de la pantalla a `1 HP` sincronizada con el latido de `55 Hz`.
   - Destello celeste periférico cuando se activa o consume el **Manto del Farol**.
4. **No Diegética (Riel Superior Gótico en `hud.py`):**
   - Geometría inmutable de `1232 × 72 px` dividida en Izquierda (`336 px`), Centro (`512 px`) y Derecha (`360 px` con grilla `2×2` de `164×22 px`), más el Canal Único de Mensajes (`560 × 48 px` en `y = 96`).
   - En la zona izquierda o derecha, indicar sutilmente cuántas **Almas Volátiles (en riesgo)** lleva el jugador hacia el próximo Farol o el estado de su bendición activa (`MANTO` / `FILO`).

### 2.2 Conexión Real del Menú de Configuración (`juego.py` y `hud.py`)
Las opciones del menú `CONFIGURACIÓN DEL SANTUARIO` deben tener impacto real e inmediato en el juego:
1. **Controles / Teclado:** Alterna entre `Preset 1: WASD Moderno` y `Preset 2: Retro Arcada (Z-X-C)`.
2. **Calidad Gráfica (`Alta`, `Media`, `Baja`):**
   - `Alta (0)`: Halos de luz completos, máscara de penumbra activa y 100% de partículas.
   - `Media (1)`: Máscara de penumbra activa y 50% de partículas.
   - `Baja (2)`: Omite el blit de `mascara_penumbra` pesada para PCs antiguos, manteniendo 60 FPS garantizados.
3. **Modo de HUD (`Completo`, `Compacto`, `Inmersivo`):**
   - `Completo (0)`: Riel superior completo + canal de mensajes.
   - `Compacto (1)`: Dibuja el riel superior con opacidad reducida (`alpha = 140`).
   - `Inmersivo (2)`: Oculta el riel superior durante la exploración normal (guiando al jugador mediante la UI Diegética y Espacial) y solo lo despliega suavemente si hay un Jefe activo (`modelo.jefe_vivo`) o durante `3 segundos` tras perder vida o recoger un alma/ítem. *(Nota: asegurar que en los tests unitarios de `test_hud.py` el modo por defecto sea `Completo (0)` para no alterar ninguna prueba existente).*

### 2.3 Pantalla de Transición entre Niveles (`nivel_completado`)
Cuando el jugador cruza el Portón (`G`) del Nivel 1 o del Nivel 2, en lugar de un texto plano, muestra un **Relicario de Fin de Nivel** (usando `dibujar_marco_heraldico`) que informe:
- Nombre del Nivel Superado y cita de E. A. Poe.
- **Almas Consagradas en el Nivel:** `X / Total`.
- **Vidas Conservadas:** `X / 5`.
- **Tiempo del Nivel:** `MM:SS.d`.
- Prompt claro: `[ENTER] Descender al siguiente nivel · [ESC] Menú Principal`.

---

## 3. VALIDACIÓN FINAL Y CIERRE DE PROYECTO

El Sub-Agente 3 debe correr la suite completa de validación:
```bash
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tests/test_logica.py
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tests/test_hud.py
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest tests/
./jugar_pygame.sh --headless
```

### Criterios de Éxito:
- [ ] **100% de los tests unitarios y de integración en verde (`OK`).**
- [ ] El juego ofrece una campaña cohesiva, rejugable, justa y desafiante de ~30 minutos.
- [ ] El archivo `docs/GDD_MDA.md` queda actualizado reflejando el sistema del **Pacto del Farol**, las **Losas Quebradizas (`~`)**, las **Campanas de Resonancia (`I`)** y la estructura final de niveles.