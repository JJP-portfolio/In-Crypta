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
5. ¡Listo! El juego inicia en la pantalla de título a **1280x720** con fondos ajustados, composición limpia y escala suavizada.

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

**Build nativo actual:** `build/index.html` es la versión jugable del proyecto GDevelop. Para abrirla localmente, iniciá un servidor HTTP desde `export/gdevelop_nativo/build/` (por ejemplo, `python3 -m http.server 8000`) y entrá a `http://localhost:8000`. Para editar el juego, abrí `IN_CRYPTA_NATIVO.json` en GDevelop y mantené junto a él la carpeta `assets/`.

---

## 4. Controles del juego

| Acción | Control |
| :--- | :--- |
| **Moverse** | Flechas izquierda / derecha |
| **Saltar** | Barra espaciadora |
| **Dash espectral** | X, después de obtener el amuleto |
| **Atacar** | J o clic izquierdo, después de obtener la pala |
| **Pausa / volver** | Escape |
| **Reducir sacudida de cámara** | F1 |

Cada acción tiene una asignación primaria. Shift ya no salta ni activa el dash; A/D, W/↑, Z/K/C y P no duplican acciones de juego. Las flechas arriba/abajo y Enter se reservan para navegar menús.

## 5. HUD y estructura de escenas

Las diez escenas jugables enlazan dos hojas de eventos de GDevelop: `IN_CRYPTA_CONTROLES` y `IN_CRYPTA_HUD`. La primera centraliza movimiento, salto, coyote, buffer y dash; la segunda mantiene corazones, avisos, controles contextuales e icono del amuleto con condiciones y acciones nativas. No quedan eventos JavaScript en el proyecto.

Cada hoja y cada nivel incluye comentarios nativos visibles en el editor. Los comentarios de escena resumen el propósito de aprendizaje y el ritmo previsto: presentación, práctica segura, exigencia, combinación y dominio. Los cuatro destinos del menú son únicos: Tutorial, Nivel 1, Nivel 2 y Salas de prueba.

El escenario usa fondos panorámicos propios que ya incluyen la ilustración de las plataformas. `Solido` conserva el comportamiento Platform y sus colisiones, pero se oculta al iniciar cada nivel para que no se dibuje por segunda vez encima del arte.

- Cinco corazones muestran las vidas; el corazón turquesa indica el manto del farol activo.
- El contador de almas muestra el progreso hacia la vida extra.
- El ícono del dash se atenúa cuando todavía está bloqueado y durante la recarga.
- El texto de controles cambia al obtener la pala y el amuleto.
- Los avisos duran 3,2 segundos y no se borran por el aviso de última vida.

## 6. Especificaciones técnicas del export

Todos los sprites de esta versión han sido integrados con estética de **Pixel-Art gótico cohesivo**, sustituyendo figuras procedurales por secuencias de animación multipose completas:

### Paleta Canónica Gótica
* **Obsidiana (#09080d):** Contornos de tinta negra, siluetas y sombras profundas.
* **Piedra de Cripta (#3a3d48):** Mampostería, losas, blindaje y pizarra antigua.
* **Musgo de Cripta (#485e3e):** Musgo seco en fisuras de tumbas y plataformas.
* **Hueso Antiguo (#d7cfb8):** Calaveras, costillares, pergamino y filo de armas.
* **Carmesí Litúrgico (#8e202c):** Estola sacerdotal, terciopelo del Custodio y sangre seca.
* **Turquesa de Ánima (#5cbeae):** Eter bioluminiscente, fuego fatuo y estela de dash.
* **Oro Litúrgico (#c69c3e):** Cruces de pala, mitra papal del jefe y runas sagradas.

### Configuración de Render y activos
* **Modo de escala:** `scaleMode: "linear"` con `pixelsRounding: false`; suaviza los bordes al escalar la ventana y reduce el aspecto excesivamente cuadriculado.
* **Recursos de imagen:** suavizado activado. Los sprites mantienen sus siluetas pixel-art; la interpolación se aplica al presentarlos en tamaños no enteros.
* **Resolución lógica:** $1280 \times 720\text{ px}$.
* **Fondos:** se conservaron las imágenes originales y se agregaron once variantes `_legible.png` con una curva de brillo moderada para recuperar detalle en las zonas oscuras. El proyecto referencia las variantes mejoradas y mantiene los originales como respaldo.
* **Máscara de colisión del jugador:** el sprite se dibuja en $32 \times 32\text{ px}$ y usa una máscara efectiva de $24 \times 30\text{ px}$ para ajustar el contacto con plataformas y obstáculos.
* **Salto nativo:** `PlatformerObject` usa impulso 620, caída máxima 900 y `JumpSustainTime` de 0,12 s. La hoja común añade coyote de 0,10 s y buffer de 0,12 s con eventos `SetCanJump`/`SimulateJumpKey`; no hay puente de gravedad en JS ni ajuste de gravedad en ápice.
* **Dash:** X, desbloqueado por el amuleto; duración 0,20 s, enfriamiento 0,60 s y velocidad 560, todo aplicado al mismo `PlatformerObject`. Un pisotón puede restaurar la carga aérea.
* **Extensiones:** el movimiento usa el comportamiento `PlatformerObject` incorporado en GDevelop y acciones/eventos del motor. El buffer, el coyote y el dash están declarados en la hoja externa; no se agrega la extensión comunitaria AdvancedJump ni hay un simulador de físicas en JavaScript.
* **Movimiento:** flechas izquierda/derecha; las acciones `SimulateLeftKey`, `SimulateRightKey` y `SimulateJumpKey` delegan el movimiento y las colisiones al comportamiento de GDevelop.
* **Tamaños visuales documentados para los demás objetos:**
  - Enemigos y Almas: $26 \times 26\text{ px}$ y $24 \times 24\text{ px}$ ($1:1$)
  - Farol y PowerUps: $20 \times 30\text{ px}$ ($0.667$)
  - MiniJefe: $36 \times 48\text{ px}$ ($0.75$)
  - Jefe Custodio: $48 \times 64\text{ px}$ ($0.75$)
  - Portón: $42 \times 58\text{ px}$ ($0.724$)

**Buenas prácticas GDevelop aplicadas:** controles predeterminados desactivados para no duplicar teclas; una hoja externa para el bloque de controles común a las escenas; comentarios en las hojas para explicar mecánicas y propósito de cada tramo.

**Documentación oficial consultada:** [Platformer behavior](https://wiki.gdevelop.io/gdevelop5/behaviors/platformer/), [referencia de acciones y condiciones](https://wiki.gdevelop.io/gdevelop5/all-features/platform-behavior/reference/), [eventos externos](https://wiki.gdevelop.io/gdevelop5/interface/events-editor/external-events/), [objetos y visibilidad](https://wiki.gdevelop.io/gdevelop5/objects/), [escala del juego](https://wiki.gdevelop.io/gdevelop5/interface/project-manager/properties/) y [suavizado de recursos](https://wiki.gdevelop.io/gdevelop5/interface/project-manager/resources/).

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

## 7. Validación nativa

El proyecto se compiló con el core de GDevelop 5.6.285: 15 escenas y cero diagnósticos. El validador de eventos revisó las instrucciones y objetos de las escenas; el JavaScript generado pasó `node --check`. El build HTML5 usa el runtime incluido de GDevelop y los assets locales.

Para editarlo, abrí `IN_CRYPTA_NATIVO.json` en GDevelop y mantené a su lado la carpeta `assets/`. Para jugar el build, serví la carpeta `build/` por HTTP y abrí `index.html` desde el servidor.
