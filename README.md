# IN CRYPTA

### TRABAJO PRÁCTICO INTEGRADOR
## ESTUDIANTE:
# Jonathan Javier Pietracci
## CARRERA:
# Licenciatura en Desarrollo de Videojuegos y Simulaciones
## DNI:
# 36.798.847
## INSTITUCIÓN:
# Universidad Nacional de Hurlingham (UNAHUR)

---

> *«Los límites entre la Vida y la Muerte son borrosos e indefinidos.»* — Edgar Allan Poe

**IN CRYPTA** es un videojuego de plataformas y acción 2D desarrollado en **Python** con **Pygame-CE**, inspirado en la estética gótica y mecánicas clásicas de plataformas (*Castlevania*, *Shovel Knight*).

Encarnamos al Sepulturero, armado con su farol y una pala, recorriendo los distintos sectores del cementerio, cripta y osario, recolectando almas, esquivando trampas de pinchos y losas que se quiebran, y enfrentando enemigos hasta vencer al custodio final.

---

## 🎮 Controles

El juego permite configurar los controles en el menú de pausa (`Esc` o `P`):

| Acción | Controles (Teclado) | Alternativa |
|---|---|---|
| **Moverse** | `A` / `D` o `Flechas` | `Flechas` |
| **Salto** | `Espacio` o `W` | `Z` |
| **Dash** | `Shift` o `X` | `X` |
| **Ataque de Pala** | `J` o `Z` o `Click Izquierdo` | `C` |
| **Pisotón Aéreo (Stomp)** | `Abajo + Ataque` en el aire | `Abajo + Ataque` en el aire |
| **Consagrar Farol** | `F` frente al farol | `F` |
| **Pausa / Menú** | `Escape` o `P` | `Escape` |

* **Salto variable:** Un toque corto realiza un salto rasante y mantener presionado da mayor elevación.
* **Pisotón de pala:** Golpear hacia abajo en el aire contra enemigos o campanas permite rebotar y recarga el dash inmediatamente.
* **Faroles de descanso:** Al pulsar `F` en un farol se guardan las almas y se activa un punto de control. Con suficientes almas consagradas se desbloquea el manto protector, que absorbe un golpe sin perder vida.

---

## 🚀 Cómo Jugar

### En Windows
Hacé doble click en **`jugar_windows.bat`** (o `jugar_pygame.bat`).
El script se encarga de verificar Python, armar el entorno virtual `.venv`, instalar `pygame-ce` e iniciar el juego.

### En Linux
Ejecutá el script:
```bash
./jugar_pygame.sh
```
O directamente desde la consola:
```bash
source .venv/bin/activate
python main.py
```

### Requisitos
* Python 3.10 o superior
* `pygame-ce>=2.5.0` (indicado en `requirements.txt`)

---

## 📁 Estructura del Proyecto

* `main.py` - Punto de entrada del juego.
* `juego.py` - Bucle principal, estados y lógica general.
* `nivel.py` - Carga y renderizado de niveles, plataformas y sólidos.
* `niveles.py` - Matrices de los mapas en texto ASCII.
* `niveles_redisenados.py` - Mapas con variantes y tramos ajustados.
* `entidades.py` - Jugador, enemigos, jefes, almas y objetos interactivos.
* `camara.py` - Cámara con seguimiento suave y límites de pantalla.
* `particulas.py` - Sistema de partículas y efectos visuales.
* `efectos.py` - Iluminación procedural, sombras y penumbra.
* `hud.py` - Interfaz de usuario, vidas, almas y estado de habilidades.
* `audio.py` - Efectos de sonido y música.
* `config.py` - Constantes, colores y parámetros de física.
* `tests/` - Pruebas automáticas de lógica, niveles y mecánicas.
* `tools/` - Scripts de validación de niveles y captura de pantallas.

---

## 📜 Créditos

* **Autor:** Jonathan Javier Pietracci
* **Carrera:** Licenciatura en Desarrollo de Videojuegos y Simulaciones
* **Materia:** Taller de Diseño Conceptual / Programación
* **Universidad:** Universidad Nacional de Hurlingham (UNAHUR)
