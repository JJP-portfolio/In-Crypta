# IN CRYPTA — Guía de Entrega y Publicación GDevelop 5.6

> **Proyecto:** *IN CRYPTA* (Plataformero Gótico 2D)  
> **Versión Nativa:** 1.0.0 (`IN_CRYPTA_NATIVO.json` / `In_Crypta_V0.9.9.json`)  
> **Estética:** Gothicvania 16-bit Pixel-Art con Paleta Canónica y Animaciones Multipose  

---

## 1. Paso a Paso Express (1 Minuto)

Podés abrir y jugar el proyecto inmediatamente tanto en la aplicación instalada de GDevelop como directamente desde el navegador web sin instalar nada.

### Opción A: En GDevelop Desktop (Linux / Windows / Mac)
1. Abrí **GDevelop 5.6**.
2. En la pantalla de bienvenida, hacé clic en **Open a project** (*Abrir un proyecto*).
3. Navegá hasta la carpeta `export/gdevelop_nativo/` del repositorio y seleccioná:
   ```
   export/gdevelop_nativo/IN_CRYPTA_NATIVO.json
   ```
4. Presioná el botón **Preview** (ícono de reproducir ▶ en la barra superior).
5. ¡Listo! El juego inicia en la pantalla de título a **1280x720** con Pixel-Art nítido.

### Opción B: En el Navegador Web (Sin Instalar)
1. Abrí [https://editor.gdevelop.io/](https://editor.gdevelop.io/) en Chrome, Firefox o Edge.
2. Hacé clic en **Open a project** $\rightarrow$ **Open a file from your computer**.
3. Seleccioná `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` (o abrí la carpeta completa `export/gdevelop_nativo`).
4. Hacé clic en el botón **Preview** ▶.

---

## 2. Cómo Publicar en `gd.games` (1 Clic)

GDevelop permite publicar el juego en la nube de forma gratuita y generar un link jugable para compartir con los docentes o evaluar online:

1. Con el proyecto abierto en GDevelop, abrí el menú superior:  
   **File** (Archivo) $\rightarrow$ **Export** (Exportar) $\rightarrow$ **Web (HTML5)**.
2. Seleccioná la pestaña **Publish on gd.games** (Publicar en gd.games).
3. Si no iniciaste sesión, creá o vinculá tu cuenta gratuita de GDevelop.
4. Hacé clic en **Publish to gd.games**.
5. Tras unos segundos de empaquetado, GDevelop te proporcionará la URL pública (ejemplo: `https://gd.games/equipo6/in-crypta`).
6. Copiá ese enlace para adjuntarlo en la entrega del trabajo práctico.

---

## 3. Cómo Exportar como ZIP HTML5 (Para Entrega Local)

Si la cátedra solicita un archivo `.zip` con la compilación web para correr en servidor local:

1. En el menú superior de GDevelop, hacé clic en:  
   **File** $\rightarrow$ **Export** $\rightarrow$ **Web**.
2. Seleccioná la opción **Manual export** (o *Local folder / Carpeta local*).
3. Elegí una carpeta de destino en tu disco (por ejemplo `export/gdevelop_nativo/build/html5/`) y hacé clic en **Export**.
4. Una vez finalizada la exportación, comprimí el contenido de esa carpeta en un archivo `IN_CRYPTA_HTML5.zip` que contendrá el `index.html` y todos los assets empaquetados.

---

## 4. Controles del Juego

| Acción | Teclas Primarias | Teclas Alternativas |
| :--- | :--- | :--- |
| **Moverse** | <kbd>Flechas Izq / Der</kbd> | <kbd>A</kbd> / <kbd>D</kbd> |
| **Saltar** | <kbd>Barra Espaciadora</kbd> | <kbd>W</kbd> / <kbd>Flecha Arriba</kbd> |
| **Dash Espectral** | <kbd>Shift Izquierdo</kbd> | <kbd>Shift Derecho</kbd> |
| **Atacar con Pala / Guadaña** | <kbd>J</kbd> | <kbd>Click Izquierdo</kbd> / <kbd>Z</kbd> |
| **Pausa / Menú** | <kbd>Escape</kbd> | <kbd>P</kbd> |
| **Accesibilidad (Reducir Sacudida)** | <kbd>F1</kbd> | En menú de pausa |

---

## 5. Especificaciones de Arte Técnico (Prioridad 5)

Todos los sprites de esta versión han sido integrados con estética de **Pixel-Art gótico cohesivo**, sustituyendo figuras procedurales por secuencias de animación multipose completas:

### Paleta Canónica Gótica
* **Obsidiana (#09080d):** Contornos de tinta negra, siluetas y sombras profundas.
* **Piedra de Cripta (#3a3d48):** Mampostería, losas, blindaje y pizarra antigua.
* **Musgo de Cripta (#485e3e):** Musgo seco en fisuras de tumbas y plataformas.
* **Hueso Antiguo (#d7cfb8):** Calaveras, costillares, pergamino y filo de armas.
* **Carmesí Litúrgico (#8e202c):** Estola sacerdotal, terciopelo del Custodio y sangre seca.
* **Turquesa de Ánima (#5cbeae):** Eter bioluminiscente, fuego fatuo y estela de dash.
* **Oro Litúrgico (#c69c3e):** Cruces de pala, mitra papal del jefe y runas sagradas.

### Configuración de Render Pixel-Perfect
* **Modo de Escala:** `scaleMode: "nearest"` en las propiedades del proyecto.
* **Suavizado:** `smoothed: false` en todos los recursos de imagen para evitar bordes borrosos.
* **Resolución Nativa:** $1280 \times 720\text{ px}$ con zoom $1.0\times$ (coincidencia $1:1$ exacta con Pygame).
* **Paridad de Colisión:** Conservación del 100% en las cajas delimitadoras (`Hitboxes`) sin deformación de aspect-ratio:
  - Jugador: $32 \times 32\text{ px}$ ($1:1$)
  - Enemigos y Almas: $26 \times 26\text{ px}$ y $24 \times 24\text{ px}$ ($1:1$)
  - Farol y PowerUps: $20 \times 30\text{ px}$ ($0.667$)
  - MiniJefe: $36 \times 48\text{ px}$ ($0.75$)
  - Jefe Custodio: $48 \times 64\text{ px}$ ($0.75$)
  - Portón: $42 \times 58\text{ px}$ ($0.724$)

### Animaciones Integradas
1. **Sepulturero (Jugador):**
   - `Idle` ($4$ frames, $0.14\text{ s}$, loop): respiración y llama de farol.
   - `Run` ($6$ frames, $0.09\text{ s}$, loop): ciclo de zancada con arrastre de abrigo.
   - `Jump` ($2$ frames, $0.10\text{ s}$): impulso de salto ascendente.
   - `Caida` ($2$ frames, $0.12\text{ s}$, loop): descenso con capa ondeando hacia arriba.
   - `Dash` ($3$ frames, $0.06\text{ s}$): deslizamiento horizontal con estela turquesa.
   - `Ataque` ($3$ frames, $0.06\text{ s}$): arco completo de tajo con medialuna sagrada.
   - Variantes espejadas hacia la izquierda (`_izq`) y sin pala (`_sin_pala`).
2. **Enemigos:**
   - `Enemy` (Esqueleto / Crawler): caminata de $4$ frames en loop ($0.12\text{ s}$).
   - `EnemyMelee` (Caballero de la Cripta): marcha pesada de $4$ frames en loop ($0.12\text{ s}$).
   - `MiniJefe` (Carcelero del Osario): zancada de $4$ frames con cadenas batientes ($0.12\text{ s}$).
   - `Jefe` (El Custodio de la Cripta): levitación ceremonial de $4$ frames con báculo pulsante ($0.14\text{ s}$).
3. **Interactivos:**
   - `Alma`: fuego fatuo de $4$ frames levitando armónicamente ($0.12\text{ s}$).
   - `FarolCheckpoint`: estado `Apagado` ($1$ frame) y estado `Encendido` ($4$ frames de fuego azul crepitando, $0.12\text{ s}$).
   - `PowerUpDash`, `PowerUpRango` y `PalaRecogible`: animaciones en loop de $4$ frames con destellos mágicos.

---

## 6. Verificación Automática de Paridad

Para certificar la integridad de todos los assets y paridad con Pygame antes de la entrega:
```bash
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/exportar_todo.py
```
Salida esperada:
```
PARIDAD_OK: el export coincide con el modelo del juego pygame
✔ EXPORT COMPLETO
```
