# PROMPT PRIORIDAD 4: Exportador Nativo 1 a 1 de Pygame a GDevelop 5.6

> **Modo de ejecución:** Pegar este documento completo en una instancia de **Gemini 3.8 Flash (Agy)** en modo *Goal Automático* **después** de haber completado las Prioridades 1, 2 y 3.

---

## 1. Rol y Objetivo Crítico

Actuás como **Principal Engine & Pipeline Engineer** especialista en la arquitectura interna de **GDevelop 5.6 (GDJS)**. 
El usuario **debe entregar y subir el juego a la plataforma de GDevelop (`gd.games`)**. Si el proyecto exportado en `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` no refleja $1:1$ las mecánicas, niveles y flujo de Pygame, el trabajo en Python no servirá para la entrega.

Tu objetivo es auditar y actualizar `tools/generar_proyecto_nativo.py`, `tools/exportador/*`, `tools/verificar_paridad.py` y `tools/validar_eventos_gd.py` para que el proyecto nativo de GDevelop sea un espejo funcional exacto del juego rediseñado.

---

## 2. Problemas Actuales Detectados en el Exportador que Debés Corregir

Al inspeccionar `tools/generar_proyecto_nativo.py` y `tools/exportador/`, existen discrepancias críticas entre Pygame y los eventos generados para GDevelop que debés solucionar:

1.  **Bug Crítico de Checkpoints (`FarolCheckpoint`) en GDevelop:**
    *   *Qué pasa hoy:* Cuando el jugador toca `FarolCheckpoint`, se guardan las variables globales `checkpoint_x` y `checkpoint_y`. Sin embargo, en `subeventos_reintento()`, cuando el jugador pierde una vida (`vidas > 0`), se ejecuta `accion("Scene", ["CurrentSceneName()", "no"])`, lo cual recarga toda la escena y **resetea `checkpoint_x` y `checkpoint_y` o devuelve al jugador al spawn inicial** en vez de moverlo al farol.
    *   *Cómo arreglarlo en GDevelop:*
        *   Al iniciar la escena (`SceneJustBegins`), si `GlobalVariable(checkpoint_activo) == 1` y `GlobalVariable(checkpoint_escena) == VariableString(nombre_escena)`, teletransportar inmediatamente a `Jugador` a `(GlobalVariable(checkpoint_x), GlobalVariable(checkpoint_y))` y restaurar `tiene_pala`, `tiene_dash` y `rango_mejorado`.
        *   Mejor aún: cuando el jugador recibe daño y `GlobalVariable(vidas) > 0`, en lugar de recargar toda la escena borrando a los enemigos ya derrotados, si tiene `checkpoint_activo == 1`, reposicionar a `Jugador` en `(GlobalVariable(checkpoint_x), GlobalVariable(checkpoint_y))`, darle `invulnerable = 1.2` s y restaurar sus variables de movimiento! Solo cambiar a la escena `"Derrota"` cuando `GlobalVariable(vidas) <= 0`.
2.  **Bug del Dash Desbloqueado desde el Inicio en GDevelop:**
    *   *Qué pasa hoy:* En `variables_jugador()` (`tools/exportador/gdevelop.py`), no estaba declarada `tiene_dash` en la lista base, y los eventos de Dash en `generar_proyecto_nativo.py` no verificaban la condición `cond("NumberObjectVariable", ["Jugador", "tiene_dash", "=", "1"])`. Por ende, en GDevelop el jugador podía hacer Dash desde el segundo 0 antes de agarrar el `PowerUpDash` (`D`).
    *   *Cómo arreglarlo:* Agregar `{"name": "tiene_dash", "type": "number", "value": 0}` en `variables_jugador()`. Inicializar `tiene_dash = 0` en el Preludio y Nivel 1, y `tiene_dash = 1` en Nivel 2 y Nivel 3. En los dos eventos de Dash (suelo y aire), exigir la condición `cond("NumberObjectVariable", ["Jugador", "tiene_dash", "=", "1"])`.
3.  **Paridad del Pisotón (Stomp) con Rebote y Recarga de Dash:**
    *   *Qué pasa hoy:* En `generar_proyecto_nativo.py`, el evento de pisotón sobre `Enemy` verifica `tiene_pala == 1` y elimina al enemigo, pero **NO impulsa al jugador hacia arriba (rebote)** en GDevelop.
    *   *Cómo arreglarlo:* En el evento de pisotón (`Jugador.Y() < Enemy.Y() - 10` y `Jugador.Variable(tiene_pala) == 1`), agregar las acciones de `PlatformerObject` para que el jugador rebote en el aire:
        *   `accion("PlatformBehavior::SetCanJump", ["Jugador", "PlatformerObject"])`
        *   `accion("PlatformBehavior::SimulateJumpKey", ["Jugador", "PlatformerObject"])`
        *   `accion("SetNumberObjectVariable", ["Jugador", "dash_aire", "=", "1"])`
        *   `accion("SetNumberObjectVariable", ["Jugador", "dash_cd", "=", "0"])`
    *   Así, en GDevelop el jugador rebota físicamente al pisar un enemigo y puede encadenar `Salto + Dash + Pisotón + Dash` igual que en Pygame.
4.  **Exportación del Mini-Boss (`K` - `Carcelero`) y Requisito de Power-Up (`X`) en el Boss Final:**
    *   Agregar el extractor `_minijefes` en `tools/exportador/modelo.py`, el adaptador `"minijefe"` en `tools/exportador/adaptadores.py` (`objeto="MiniJefe"`, `z=5`, `sprite=(36, 48)`), su renderizador en `sprites.py` y sus eventos de patrulla, embestida y daño ($3$ vidas) en `generar_proyecto_nativo.py`.
    *   En `eventos_jefe()` de `generar_proyecto_nativo.py`, asegurar que el Custodio (`Jefe`) tenga sus 2 fases: en Fase 1 recibe daño de `GolpePala` y de pisotón; en Fase 2 (`Jefe.Variable(fase) >= 2`), solo recibe daño si `GlobalVariable(rango_mejorado) == 1` (Power-Up `'X'` recogido) y mediante pisotón o golpe en estado vulnerable.
5.  **Flujo Continuo de Escenas (Preludio $\rightarrow$ Nivel 1 $\rightarrow$ Nivel 2 $\rightarrow$ Nivel 3 $\rightarrow$ Victoria):**
    *   En `tools/exportador/manifiesto.py`, configurar que el botón `"1 · JUGAR"` del menú `"Titulo"` lleve a `"Tutorial"` (El Preludio), y que el atributo `siguiente` de `escena_tutorial()` apunte a `"Nivel 1"` (en vez de volver a `"Titulo"`), para que toda la campaña fluya sin interrupciones de principio a fin.

---

## 3. Verificación de Paridad y Compilación GDevelop

1. Ejecutá el pipeline completo:
```bash
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/exportar_todo.py
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/validar_eventos_gd.py
```
2. Ambos deben devolver `PARIDAD_OK` (0 diferencias) y `EVENTOS_OK` (100% compatible con los metadatos WebAssembly de GDevelop 5.6 en `metadatos_gdevelop_5_6.json`).
3. Si está disponible Node y el compilador headless, corré `node tools/compilar_proyecto_gd.js export/gdevelop_nativo/IN_CRYPTA_NATIVO.json /tmp/gd_build_test` para confirmar $0$ diagnósticos de error en las hojas de eventos.