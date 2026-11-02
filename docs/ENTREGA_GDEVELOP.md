# IN CRYPTA — Guía de Compilación HTML5 GDevelop 5.6 y Publicación en `gd.games`

> **Proyecto:** *IN CRYPTA* (Versión `1.0.0`)  
> **Motor Destino:** GDevelop 5.6 (`GDJS/Runtime` + `libGD.js` WebAssembly Core)  
> **Resolución Nativa:** $1280 \times 720\text{ px}$ (`scaleMode: "nearest"`, Pixel-Art nítido)

---

## 1. Artefactos de Entrega GDevelop 5.6

| Artefacto | Ruta en el Repositorio | Descripción |
| :--- | :--- | :--- |
| **Proyecto Nativo GDevelop 5.6** | `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` | Proyecto completo con las 15 escenas (`Titulo`, `Pausa`, `Derrota`, `Victoria`, `Salas`, `Tutorial`, `Nivel 1`–`3`, `Sala 1`–`6`), hojas de eventos y 194 recursos. |
| **Build Web HTML5 Compilado** | `export/gdevelop_nativo/build/` | Compilación HTML5 lista para navegador con `index.html`, `data.js`, `code0.js`–`code14.js`, `assets/` y el runtime completo `GDJS/Runtime` (`pixi-renderers/`, `Extensions/`, `howler-sound-manager/`, `fontfaceobserver-font-manager/`). |
| **Paquete ZIP HTML5 Autónomo** | `export/IN_CRYPTA_1.0.0_HTML5_GDGAMES.zip` | Archivo ZIP con `index.html` en la raíz del paquete, listo para subir a cualquier hosting web (`itch.io`, GitHub Pages, Netlify) o adjuntar en la entrega. |
| **Script Empaquetador Python** | `tools/empaquetar_gd_games.py` | Localiza GDevelop 5.6 en el sistema, compila `IN_CRYPTA_NATIVO.json` mediante `node tools/compilar_proyecto_gd.js`, sincroniza `GDJS/Runtime` y genera el ZIP con resumen SHA-256. |
| **Lanzador y Validador CLI** | `./publicar_gd_games.sh` | Script ejecutable para verificar la compilación (`--check`), jugar en el navegador (`--play`) o abrir GDevelop 5.6 para publicar en `gd.games` (`--open-ide`). |

---

## 2. Uso de `./publicar_gd_games.sh`

El script `./publicar_gd_games.sh` en la raíz del repositorio automatiza todo el flujo de compilación, validación y publicación:

### A. Verificar compilación, empaquetado ZIP y servidor HTTP (`--check`)
```bash
./publicar_gd_games.sh --check
```
Ejecuta `python3 tools/empaquetar_gd_games.py`, comprueba que existan `export/gdevelop_nativo/build/index.html` y `export/IN_CRYPTA_1.0.0_HTML5_GDGAMES.zip`, y levanta un servidor HTTP temporal verificando que `/index.html`, `/data.js` y `/assets/titulo.png` respondan `HTTP 200 OK`.

### B. Jugar el build HTML5 de GDevelop 5.6 en el navegador (`--play`)
```bash
./publicar_gd_games.sh --play
```
Compila el proyecto nativo de GDevelop 5.6, levanta un servidor HTTP local en `export/gdevelop_nativo/build/` y abre automáticamente `http://localhost:8080/index.html` en el navegador (`xdg-open`).

### C. Abrir en GDevelop 5.6 y publicar en `gd.games` (`--open-ide` o sin argumentos)
```bash
./publicar_gd_games.sh
# o explícitamente:
./publicar_gd_games.sh --open-ide
```
Actualiza la compilación HTML5, abre directamente `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` en GDevelop 5.6 (`flatpak run io.gdevelop.ide ...`, o abre `https://editor.gdevelop.io` si no está instalado localmente) y muestra en consola los pasos para generar el enlace público en `gd.games`.

---

## 3. Cómo Obtener el Link Público en `gd.games` (3 Pasos)

La publicación en `gd.games` requiere la sesión autenticada del autor dentro del IDE de GDevelop 5.6:

1. **Abrir el proyecto en GDevelop 5.6:**  
   Ejecuta `./publicar_gd_games.sh --open-ide` (o abre manualmente `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` en GDevelop 5.6 Desktop / [editor.gdevelop.io](https://editor.gdevelop.io)).
2. **Abrir el panel de publicación:**  
   En la barra superior derecha del IDE, haz clic en **Share** (*Compartir / Exportar*) $\rightarrow$ **gd.games** (*One-click packaging for web*).
3. **Publicar y copiar el enlace:**  
   Inicia sesión con tu cuenta de GDevelop, haz clic en **Publish game** (*Generate link*) y copia la URL pública generada:
   ```text
   https://gd.games/<tu-usuario>/in-crypta
   ```

---

## 4. Uso Directo del Paquete `IN_CRYPTA_1.0.0_HTML5_GDGAMES.zip`

Si deseas publicar el juego en **itch.io**, **GitHub Pages**, **Netlify** o entregarlo como compilación web autónoma sin depender de la nube de GDevelop:

1. El archivo `export/IN_CRYPTA_1.0.0_HTML5_GDGAMES.zip` ya contiene `index.html` en la raíz del archivo comprimido junto con `data.js`, `code0.js`–`code14.js`, `assets/` y el runtime `GDJS`.
2. En **itch.io**: crea un nuevo proyecto con *Kind of project: HTML*, sube `export/IN_CRYPTA_1.0.0_HTML5_GDGAMES.zip`, marca *"This file will be played in the browser"* y configura las dimensiones del viewport en **1280 x 720 px**.
3. Para regenerar manualmente el paquete ZIP en cualquier momento:
   ```bash
   python3 tools/empaquetar_gd_games.py
   ```
