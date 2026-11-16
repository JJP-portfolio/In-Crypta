# IN CRYPTA

### TRABAJO PRÁCTICO INTEGRADOR
* **Equipo:** Equipo 6
* **Integrantes y roles:**
  * **Jonathan Javier Pietracci** (DNI 36.798.847) — Programación, arquitectura, audio, herramientas y documentación.
  * **Ovelar Alejandro Ezequiel** — Diseño de niveles, dirección artística y pruebas de juego.
  * **Joaquín Cardiel Gomez** — Diseño de niveles, ambientación visual y pruebas de juego.
* **Carrera:** Licenciatura en Desarrollo de Videojuegos y Simulaciones
* **Institución:** Universidad Nacional de Hurlingham (UNAHUR)

---

> *«Los límites entre la Vida y la Muerte son borrosos e indefinidos.»* — Edgar Allan Poe

**IN CRYPTA** es un videojuego de plataformas y acción 2D desarrollado en **Python** con **Pygame-CE**, inspirado en la estética gótica literaria y en referentes del género como *Castlevania* y *Shovel Knight*.

Encarnamos al Sepulturero, quien recorre el Umbral, el Camposanto, la Cripta y el Osario armado con su farol y su pala, cosechando almas, sorteando trampas y losas quebradizas, y enfrentando guardianes hasta derrotar al Custodio final.

---

## Controles

El juego admite dos configuraciones de teclado seleccionables desde **Configuración** (`Esc` o `P` en partida, o desde el menú principal):

| Acción | Preset Estándar | Preset Retro (Z-X-C) |
|---|---|---|
| **Desplazamiento** | `A` / `D` o `Flechas` | `Flechas` o `A` / `D` |
| **Salto variable** | `Espacio` o `W` | `Z` o `Espacio` |
| **Dash espectral** | `Shift` o `X` | `X` o `Shift` |
| **Ataque con pala** | `J`, `Z` o `Click Izquierdo` | `C` o `J` |
| **Pisotón aéreo (Pogo)** | `Abajo + Ataque` en el aire | `Abajo + Ataque` en el aire |
| **Pausa / Menú** | `Escape` o `P` | `Escape` o `P` |

* **Salto variable:** Un toque breve ejecuta un salto rasante; mantener presionada la tecla alcanza la altura máxima.
* **Pisotón aéreo y campanas:** Golpear o rebotar desde arriba sobre enemigos, campanas o incensarios recarga inmediatamente el dash aéreo.
* **Faroles de reposo:** Al alcanzar un farol se consagra el avance como punto de control y se otorgan mejoras progresivas (hasta el Manto protector y el Filo de Ánima) según las almas cosechadas en el tramo.

---

## Ejecución y pruebas

### En Windows
Haz doble clic en **`jugar_windows.bat`**. El script verifica Python 3.10+, prepara el entorno virtual `.venv`, instala `pygame-ce` desde `requirements.txt` e inicia el juego.

### En Linux
Ejecuta el lanzador desde la terminal:
```bash
./jugar_pygame.sh
```
O bien utilizando un entorno virtual existente:
```bash
source .venv/bin/activate
python main.py
```

### Validación técnica y pruebas automatizadas
El proyecto cuenta con batería de pruebas y validador estático de mapas:
```bash
pytest -q
python3 tools/validar_niveles.py
```
También se encuentran disponibles los atajos `make run`, `make test` y `make validate` en el `Makefile`. Para instrucciones detalladas consulta [GUIA_JUEGO.md](file:///home/sanodesu/unahur/IN_CRYPTA_v1.0.3_Entrega/GUIA_JUEGO.md).

### Requisitos
* Python 3.10 o superior.
* `pygame-ce>=2.5.0` (definido en `requirements.txt`).

---

## Estructura del proyecto

* `main.py` — Punto de entrada y argumentos de línea de comandos (`--tutorial`, `--nivel`, `--sala`).
* `juego.py` — Orquestador y fachada principal de `Juego`, caché de texto y coordinación de escenas.
* `escena/` — Mixins y utilidades visuales: `constantes.py`, `menus.py`, `fondos.py`, `pantallas.py`, `render_mundo.py`, `render_nivel.py` y `decoraciones.py`.
* `logica/` — Mixins de reglas de juego: `combate.py`, `jefes.py` y `mundo.py`.
* `nivel.py` — Parseo ASCII, colisiones y construcción de entidades del nivel.
* `niveles.py` — Matrices ASCII oficiales del tutorial y de los actos principales.
* `niveles_redisenados.py` — Variantes verticalizadas y salas de prueba jugables.
* `entidades.py` — Fachada de actores que reexporta la API del paquete `actores/`.
* `actores/` — Entidades separadas por responsabilidad: `jugador.py`, `render_jugador.py`, `enemigos.py`, `custodio.py`, `carcelero.py`, `recogibles.py`, `interactivos.py`, `estampas.py` y `utilidades.py`.
* `camara.py` — Seguimiento suave, márgenes de encuadre y sacudida direccional.
* `particulas.py` — Emisores de chispas, plumas, disolución y clima de bioma.
* `hud.py` — Orquestador y fachada del HUD que reexporta la arquitectura de `ui/`.
* `ui/` — Componentes de interfaz: `animacion.py`, `modelos.py` y `renderer.py`.
* `audio.py` — Motor mixto de sonido: combina los 19 archivos WAV base de `assets/audio/sfx/` y música OGG con síntesis procedural en tiempo real (timbres de campana, latido cardíaco y consagración de farol), evitando pistas de audio redundantes en disco.
* `config.py` — Constantes de física, paletas góticas, parámetros de entidades y estilos visuales.
* `tests/` — Suite de pruebas unitarias, integración y huella de regresión (`pytest`).
* `tools/` — Validador de invariantes (`validar_niveles.py`), métricas de estilo (`metricas_estilo.py`), huella de regresión (`huella_regresion.py`), generador musical (`generar_musica_synthlab.py`) y capturas (`capturar.py`).
