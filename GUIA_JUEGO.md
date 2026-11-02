# 🕯️ IN CRYPTA — Guía de Instalación y Juego (Windows y Linux)

Bienvenido a la guía oficial de **IN CRYPTA** para versiones de escritorio (**Windows** y **Linux**).  
Aquí encontrarás las instrucciones paso a paso para ejecutar el juego con un solo doble clic, resolver problemas comunes y configurar la experiencia visual y de controles a tu gusto.

---

## 📋 Requisitos del Sistema

* **Sistema Operativo:**
  * **Windows:** Windows 10 o Windows 11 (64-bit).
  * **Linux:** Cualquier distribución moderna (Ubuntu 20.04+, Debian 11+, Linux Mint, Fedora, Arch, etc.).
* **Python:** Versión **3.10 o superior** (3.11, 3.12, 3.13 o 3.14 compatibles).
* **Tarjeta Gráfica:** Cualquier GPU integrada o dedicada con soporte OpenGL / SDL2 estándar.
* **Espacio en Disco:** ~80 MB libres.
* **FPS:** Diseñado para correr a **60 FPS** estables.

---

## 🪟 Guía para Windows

### 1. Preparación previa (Solo una vez)
Asegúrate de tener **Python** instalado en tu computadora:
1. Si no tienes Python instalado, descárgalo gratis desde [python.org/downloads](https://www.python.org/downloads/).
2. ⚠️ **MUY IMPORTANTE durante la instalación:** En la primera pantalla del instalador de Python, marca la casilla que dice **«Add python.exe to PATH»** (o *Agregar Python al PATH*) antes de pulsar *Install Now*.

### 2. Ejecutar con Doble Clic
1. Si descargaste el archivo comprimido (`.zip`), haz clic derecho y selecciona **Extraer todo...** en una carpeta de tu preferencia *(no lo ejecutes dentro del archivo comprimido)*.
2. Abre la carpeta descomprimida y haz **doble clic** sobre el archivo:
   ```text
   jugar_windows.bat
   ```
   *(También puedes hacer doble clic en `jugar_pygame.bat`, que funciona exactamente igual)*.

### ¿Qué hace el script automáticamente?
* Detecta tu instalación de Python.
* Crea un entorno virtual aislado (`.venv`) en la carpeta del juego para no alterar tu sistema.
* Instala o actualiza automáticamente el motor gráfico (`pygame-ce`).
* Lanza el juego de inmediato.
* Si ocurriera algún error imprevisto, la consola permanecerá abierta mostrándote el mensaje de diagnóstico en lugar de cerrarse abruptamente.

### ⚠️ Advertencia de Windows SmartScreen
Si Windows muestra la pantalla azul de aviso *"Windows protegió su PC"* al ejecutar el archivo `.bat` por primera vez:
1. Haz clic en **«Más información»**.
2. Presiona el botón **«Ejecutar de todas formas»**.

---

## 🐧 Guía para Linux

### 1. Preparación previa (Solo si tu distribución no tiene venv)
En distribuciones basadas en Debian o Ubuntu, asegúrate de tener el módulo de entornos virtuales:
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

### 2. Ejecutar por Doble Clic (Modo Gráfico)
1. Extrae el archivo `.zip` en tu carpeta deseada.
2. Haz **doble clic** sobre:
   ```text
   jugar_pygame.sh
   ```
   * Si tu explorador de archivos te pregunta qué acción tomar, elige **«Ejecutar en terminal»** o **«Ejecutar»**.
   * Si el sistema no tiene activado el permiso de ejecución, abre una terminal en la carpeta y escribe:
     ```bash
     chmod +x jugar_pygame.sh IN_CRYPTA.desktop
     ```
3. También dispones del archivo de escritorio **`IN_CRYPTA.desktop`**, que puedes copiar a tu Escritorio o a `~/.local/share/applications/` para integrarlo con tu lanzador de aplicaciones.

### 3. Ejecutar desde Terminal
Abre tu terminal en el directorio del proyecto y escribe:
```bash
./jugar_pygame.sh
```

#### Parámetros adicionales útiles:
* `./jugar_pygame.sh --check` : Realiza un autodiagnóstico del entorno y dependencias.
* `./jugar_pygame.sh --headless` : Ejecuta una prueba de renderizado sin abrir ventana gráfica.
* `./jugar_pygame.sh --nivel 1` : Salta el prólogo e inicia directo en el Camposanto (niveles 1 a 3 disponibles).

---

## 🛠️ Instalación y Ejecución Manual (Cualquier Sistema)

Si eres desarrollador o prefieres iniciar el juego manualmente sin usar los scripts automáticos:

```bash
# 1. Crear entorno virtual
python3 -m venv .venv

# 2. Activar entorno virtual
# En Linux / macOS:
source .venv/bin/activate
# En Windows (cmd):
.venv\Scripts\activate
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 3. Instalar librerías requeridas
pip install -r requirements.txt

# 4. Iniciar el juego
python main.py
```

---

## 🎨 Opciones de Video y Shaders Góticos

**IN CRYPTA** incluye un pipeline de post-procesamiento visual personalizable para equilibrar fidelidad retro, atmósfera gótica y rendimiento:

Accede a **Configuración** desde el Menú Principal o pausando el juego (`Esc`):
* **Efectos / Shaders:**
  * **Gótico (Bloom + CRT) [Recomendado]:** Añade resplandor místico (bloom) a partículas, almas y luces de farol, junto con una micro-trama de scanlines ópticas retro que amalgama los textos de alta resolución con el pixel art.
  * **Suave (Solo Bloom):** Mantiene el halo luminoso y el suavizado sin las líneas CRT.
  * **Puro (Pixel Art Clásico):** Renderizado directo 1:1 sin filtros ni post-procesado.
* **Calidad Gráfica:**
  * **Alta:** 100% de partículas ambientales, halos volumétricos y penumbra completa.
  * **Media:** 50% de partículas y penumbra optimizada.
  * **Baja:** 60 FPS garantizados para computadoras de muy bajos recursos (sin penumbra pesada).
* **Reducción de Movimiento:**
  * Desactiva el temblor de cámara (screenshake) y suaviza los flashes de daño si eres sensible a efectos visuales intensos.

---

## 🎮 Controles y Guía de Supervivencia

### Tabla de Controles

| Acción | Preset Estándar (Recomendado) | Preset Retro | Mando / Gamepad |
|---|---|---|---|
| **Moverse a los lados** | `A` / `D` o `Flechas` | `Flechas` o `A` / `D` | `D-Pad` o `Stick Izquierdo` |
| **Salto Variable** | `Espacio` o `W` | `Z` o `Espacio` | `Botón Sur (A / Cruz)` |
| **Dash de Sombras** | `Shift` o `X` | `X` o `Shift` | `Gatillo / RB / R1` |
| **Golpe de Pala** | `J` o `Z` o `Click Izquierdo` | `C` o `J` | `Botón Oeste (X / Cuadrado)` |
| **Pisotón Aéreo (Pogo/Stomp)** | `Abajo + Ataque` en el aire | `Abajo + Ataque` en el aire | `Abajo + Ataque` en el aire |
| **Consagrar Farol** | `F` frente al farol | `F` frente al farol | `Botón Norte (Y / Triángulo)` |
| **Pausa / Menú** | `Escape` o `P` | `Escape` o `P` | `Start / Options` |

### Mecánicas Esenciales de Supervivencia:
1. **Salto Variable:**
   - Un toque corto realiza un salto bajo para esquivar techos con pinchos.
   - Mantener presionado alcanza la máxima elevación.
2. **Pisotón de Pala (Pogo):**
   - En el aire, pulsa `Abajo + Ataque` sobre un enemigo, una campana, un incensario o una losa quebradiza para rebotar alto.
   - ¡El rebote en el aire recarga tu **Dash** inmediatamente!
3. **El Farol de Reposo y el Manto Protector:**
   - Recoge **Almas celestes** de los enemigos caídos.
   - Al llegar a un Farol, pulsa `F` para consagrar tu avance (punto de control).
   - Con suficientes almas consagradas, desbloqueas el **Manto del Farol** (un aura defensiva celeste que absorbe un golpe mortal completo sin perder vida).

---

## ❓ Preguntas Frecuentes y Solución de Problemas (FAQ)

### 1. Hago doble clic en `jugar_windows.bat` y se cierra al instante
* **Causa:** No tienes Python instalado o no marcaste la casilla *"Add python.exe to PATH"*.
* **Solución:** Descarga Python desde [python.org](https://www.python.org/downloads/), ejecuta el instalador, selecciona **Modify** o reinstala marcando la casilla de PATH.

### 2. En Linux me dice `Permiso denegado` al correr `jugar_pygame.sh`
* **Solución:** Abre la terminal en la carpeta del juego y dale permisos de ejecución:
  ```bash
  chmod +x jugar_pygame.sh
  ```

### 3. El juego no emite sonido
* **Solución:** Comprueba que tu dispositivo de audio predeterminado esté activo en el sistema antes de abrir el juego. Pygame inicializa el mezclador de audio al arranque.

### 4. El juego funciona con tirones o bajadas de FPS
* **Solución:**
  1. Entra a **Configuración** (`Esc` durante la partida o en el menú).
  2. Ajusta **Calidad Gráfica** a `Media` o `Baja`.
  3. Ajusta **Efectos / Shaders** a `Suave` o `Puro`.

---

> *Que la luz de tu farol guíe tus pasos en las profundidades de la cripta.*
