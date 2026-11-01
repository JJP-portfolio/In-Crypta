# PROMPT PRIORIDAD 5: Integración de Assets Pixel-Art Gratuitos (itch.io / CC0) y Animaciones en GDevelop

> **Modo de ejecución:** Pegar este documento completo en una instancia de **Gemini 3.8 Flash (Agy)** en modo *Goal Automático* **después** de haber completado la Prioridad 4.

---

## 1. Rol y Objetivo del Orquestador

Actuás como **Technical Artist & GDevelop Integration Specialist**.
El usuario indicó explícitamente: *"Con respecto al de GDevelop podés obviar los procedurales de Python y usar directamente Assets gratuitos que encuentres en itch.io o cualquier web de assets para hacer una versión mejor... tiene que tener una congruencia el juego tanto en la estética como en la animación"*.

Tu misión es reemplazar los sprites estáticos/procedurales exportados a `export/gdevelop_nativo/assets/` por un **paquete cohesivo de Assets Pixel-Art Góticos 2D (CC0 / Free Assets)** con **animaciones multipose reales** dentro del proyecto de GDevelop (`IN_CRYPTA_NATIVO.json`), manteniendo el $100\%$ de paridad en las cajas de colisión (`Rect` / Hitboxes) para no alterar la física ni los saltos.

---

## 2. Estrategia de Assets y Coherencia Estética (Estilo Gothicvania 16-bit / 32x32)

Coordiná 3 sub-agentes para dotar al proyecto GDevelop de una estética Pixel-Art gótica unificada:

### 2.1. Sub-Agente 5A: Descarga / Empaquetado de Assets Libres (CC0 / OpenGameArt / Kenney / Itch.io)
1. Creá un directorio `assets_pixelart/` en la raíz del proyecto y un script `tools/integrar_assets_gdevelop.py`.
2. Si el entorno tiene acceso a red, el script puede descargar packs Pixel-Art góticos CC0 verificados (de repositorios públicos en GitHub de *Gothicvania* / *Pixel Frog* / *Anokolisa* / *0x72 DungeonTileset II* CC0 / *OpenGameArt*), **y como respaldo infalible offline**, debe incluir un generador de **Pixel-Art Spritesheets detallados (con paleta indexada de 16 colores, dithering, sombreado pixel-perfect y contorno oscuro)** para que nunca falle por falta de conexión.
3. Todos los assets deben compartir una **única paleta de color gótica** (Obsidiana `#09080d`, Piedra Cripta `#3a3d48`, Musgo `#485e3e`, Hueso `#d7cfb8`, Carmesí `#8e202c`, Ánima Turquesa `#5cbeae` y Oro `#c69c3e`) y el mismo tamaño de píxel aparente ($1\times$ escalado con `scaleMode: "nearest"` en GDevelop para que el Pixel-Art se vea nítido y no borroso).
    * **IMPORTANTE en `generar_proyecto_nativo.py`:** Cambiar `"scaleMode": "linear"` a `"scaleMode": "nearest"` y `"smoothed": False` en todos los `recurso_imagen()` para que GDevelop renderice el Pixel-Art con bordes perfectos.

### 2.2. Sub-Agente 5B: Animaciones Multipose en GDevelop (`tools/exportador/gdevelop.py` y `sprites.py`)
Configurar secuencias de frames reales (mínimo $4$ a $6$ frames por acción) en los objetos de GDevelop:
1.  **Objeto `Jugador` (`32 x 32` px visual, máscara de colisión centrada de `24 x 30` px):**
    *   `Idle` ($4$ frames en loop, $0.14\text{ s}$/frame): respiración del sepulturero y oscilación de la llama del farol.
    *   `Run` / `Caminata` ($6$ frames en loop, $0.09\text{ s}$/frame): ciclo de pasos con movimiento de capa.
    *   `Jump` / `Salto` ($2$ frames, $0.10\text{ s}$/frame): impulso ascendente con capa hacia abajo.
    *   `Caida` ($2$ frames en loop, $0.12\text{ s}$/frame): caída con abrigo flotando hacia arriba.
    *   `Dash` ($3$ frames, $0.06\text{ s}$/frame): silueta horizontal rasante envuelta en sombra turquesa.
    *   `Ataque` ($3$ frames, $0.06\text{ s}$/frame): arco completo de tajo con la pala/guadaña.
    *   *Evento en GDevelop:* Diferenciar `Idle` (cuando no se mueve en el piso) de `Run` (cuando `PlatformBehavior::IsMovingEvenALittle` es verdadero en el piso) para que el personaje tenga animación real de correr.
2.  **Enemigos (`Enemy`, `EnemyMelee`, `MiniJefe`, `Jefe`):**
    *   Cada enemigo debe tener una animación `Walk`/`Patrol` de $4$ frames en loop ($0.12\text{ s}$/frame) en lugar de un único PNG estático, más su orientación horizontal (`FlipX`) automática según su variable `dir` (`dir == -1` voltea el sprite, `dir == 1` normal).
3.  **Elementos Interactivos Animados (`Alma`, `FarolCheckpoint`, `PowerUpDash`, `PalaRecogible`, `PowerUpRango`):**
    *   `Alma`: animación en loop de $4$ frames ($0.12\text{ s}$) donde la gema/llama espiritual flota y brilla.
    *   `FarolCheckpoint`: animación `Apagado` ($1$ frame) y animación `Encendido` ($4$ frames en loop con fuego azul crepitando). Cuando el jugador toca el farol (`FarolCheckpoint.Variable(activo) == 1`), cambiar su animación a `Encendido` (`ChangeAnimation` a `1`).

### 2.3. Sub-Agente 5C: Empaquetado Final para Subir a GDevelop (`gd.games`)
1. Asegurar que todos los archivos `.png`, `.wav` y `.ttf` referenciados en `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` estén dentro de `export/gdevelop_nativo/assets/` con rutas relativas limpias (`assets/...`) y sin archivos huérfanos.
2. Documentar en `export/gdevelop_nativo/LEEME_ENTREGA_GDEVELOP.md` los pasos exactos de 1 minuto para que el alumno:
    * Abra `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` en GDevelop 5.
    * Pruebe el juego con el botón *Preview*.
    * Haga clic en *Publish $\rightarrow$ Share on gd.games* (o exporte el ZIP HTML5) para entregar el link a la cátedra.

---

## 3. Verificación Final

Correr todos los chequeos del repositorio:
```bash
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/exportar_todo.py
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/validar_eventos_gd.py
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_logica.py
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_hud.py
```
Todos deben pasar en verde (`TESTS_INCRYPTA_OK`, `PARIDAD_OK`, `EVENTOS_OK`).