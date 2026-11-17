# IN CRYPTA — Guia de Instalacion y Ejecucion

Guia paso a paso para ejecutar **IN CRYPTA** en Windows o Linux desde el paquete de entrega, configurar video/controles y resolver los problemas mas habituales al iniciar.

---

## Requisitos

* **Sistema operativo:** Windows 10/11 (64-bit) o cualquier distribucion Linux actual (Ubuntu, Debian, Mint, Fedora, Arch).
* **Python:** 3.10 o superior (probado en 3.10 a 3.14).
* **Graficos:** soporte estandar SDL2 / OpenGL (GPU integrada o dedicada).
* **Espacio en disco:** ~80 MB libres incluyendo el entorno virtual local.

---

## Ejecucion en Windows

1. Si todavia no tenes Python instalado, descargalo desde [python.org/downloads](https://www.python.org/downloads/).
   En la primera pantalla del instalador, marca **"Add python.exe to PATH"** antes de instalar.
2. Descomprime el archivo `.zip` en una carpeta propia (no lo ejecutes desde adentro del ZIP).
3. Hace doble clic en **`jugar_windows.bat`**.

El lanzador detecta Python, crea un entorno virtual `.venv` aislado dentro de la carpeta del juego, instala `pygame-ce` desde `requirements.txt` y abre el juego. Si ocurre algun error, deja la consola abierta para que puedas leer el mensaje.

**Nota sobre Windows SmartScreen:** si Windows muestra el cartel *"Windows protegio su PC"* la primera vez que abris el `.bat`, entra en **"Mas informacion"** y elegi **"Ejecutar de todas formas"**.

---

## Ejecucion en Linux

En distribuciones basadas en Debian o Ubuntu, asegurate de tener instalado el soporte para entornos virtuales:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Luego podes iniciar el juego de dos maneras:

* **Desde el explorador de archivos:** descomprime el `.zip` y ejecuta `jugar_pygame.sh` (o copia `IN_CRYPTA.desktop` a tu escritorio o `~/.local/share/applications/`). Si no tiene permiso de ejecucion, dale permisos una sola vez:
  ```bash
  chmod +x jugar_pygame.sh IN_CRYPTA.desktop
  ```
* **Desde terminal:**
  ```bash
  ./jugar_pygame.sh
  ```

Parametros utiles del lanzador y de `main.py`:

* `./jugar_pygame.sh --check` : verifica imports, carga de `Juego`, un tick de actualizacion y renderizado en modo headless.
* `./jugar_pygame.sh --nivel 1` : salta la introduccion y arranca directo en el nivel elegido (`0` para Tutorial, `1` a `3` para los actos principales).

---

## Instalacion manual (cualquier sistema)

```bash
python3 -m venv .venv

# Linux / macOS:
source .venv/bin/activate
# Windows (cmd):
.venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

---

## Opciones graficas y rendimiento

Desde **Configuracion** (en el menu principal o pausando con `Esc`) se pueden ajustar tres apartados:

* **Shaders:**
  * *Gotico (Bloom + CRT):* resplandor en luces/particulas y scanlines sobre el lienzo.
  * *Suave (Solo Bloom):* conserva el halo luminoso sin scanlines.
  * *Puro (Pixel Art Clasico):* imagen directa sin filtros de pantalla.
* **Calidad grafica:**
  * *Alta:* iluminacion completa, mascara de penumbra y 100% de particulas ambientales.
  * *Media:* reduce a la mitad las particulas de bioma y achica radios de luz.
  * *Baja:* desactiva penumbra, bloom y scanlines para asegurar 60 FPS estables en equipos modestos.
* **Reduccion de movimiento:** desactiva el temblor de camara y atenua destellos en pantalla.

---

## Controles y mecanicas basicas

| Accion | Preset Estandar | Preset Retro |
|---|---|---|
| Moverse | `A` / `D` o `Flechas` | `Flechas` o `A` / `D` |
| Salto variable | `Espacio` o `W` | `Z` o `Espacio` |
| Dash | `Shift` o `X` | `X` o `Shift` |
| Ataque | `J`, `Z` o `Click izquierdo` | `C` o `J` |
| Pisoton aereo (Pogo) | `Abajo + Ataque` en el aire | `Abajo + Ataque` en el aire |
| Pausa / Menu | `Esc` o `P` | `Esc` o `P` |

* **Salto variable:** soltar rapido realiza un salto bajo; mantener sostenido alcanza la altura maxima.
* **Pisoton y recarga de Dash:** golpear desde arriba a un enemigo, una campana o un incensario hace rebotar al personaje y recarga el Dash al instante en el aire.
* **Farol de reposo:** guarda el avance como punto de control y consagra las almas acumuladas para habilitar mejoras del tramo (hasta el Manto protector que absorbe un golpe y el Filo de Anima).

---

## Problemas frecuentes

* **`jugar_windows.bat` se cierra enseguida o dice que falta Python:** asegurate de haber marcado *"Add python.exe to PATH"* al instalar Python.
* **`Permiso denegado` en Linux:** ejecuta `chmod +x jugar_pygame.sh` dentro de la carpeta del proyecto.
* **Sin audio:** verifica que el dispositivo de salida este activo antes de abrir el juego.
* **Tirones en equipos antiguos:** desde Configuracion baja **Calidad** a `Media` o `Baja` y deja **Shaders** en `Puro`.
