# IN CRYPTA

> *«Los límites entre la Vida y la Muerte son borrosos e indefinidos.»* — Edgar Allan Poe

**IN CRYPTA** es un videojuego de plataformas gótico y de acción 2D desarrollado en **Python / Pygame-CE**, inspirado en la estética fúnebre decimonónica, *Shovel Knight* y los clásicos de *Castlevania*.

Encarnás al **Sepulturero de la Cripta**, armado únicamente con su farol litúrgico y una pala oxidada. Deberás descender por los tres círculos del osario, consagrar las ánimas errantes, sortear fosos de espinas y losas quebradizas, y quebrar la coraza espectral de los custodios para escapar de la oscuridad.

---

## 🎮 Controles

El juego cuenta con soporte para teclado con dos configuraciones disponibles en el menú de pausa:

| Acción | Preset Estándar (Recomendado) | Preset Retro (Consola) |
|---|---|---|
| **Moverse** | `A` / `D` o `Flechas` | `Flechas` o `A` / `D` |
| **Salto Variable** | `Espacio` o `W` | `Z` o `Espacio` |
| **Dash de Sombras** | `Shift` o `X` | `X` o `Shift` |
| **Ataque de Pala** | `J` o `Z` o `Click Izquierdo` | `C` o `J` o `Click Izquierdo` |
| **Pisotón Aéreo (Stomp)** | `Abajo + Ataque` en el aire | `Abajo + Ataque` en el aire |
| **Pausa / Menú** | `Escape` o `P` | `Escape` o `P` |

* **Salto Variable:** Tap corto para saltos rasantes de precisión; mantener presionado para saltos altos de elevación completa.
* **Pisotón Aéreo:** Saltar y golpear hacia abajo sobre enemigos, incensarios o losas para rebotar y recargar instantáneamente el Dash en el aire.
* **El Pacto del Farol:** Al consagrar ánimas en los Faroles de Reposo (`F`), purificás tu avance y desbloqueás el *Manto Protector* (escudo que absorbe un impacto letal).

---

## 🚀 Cómo Jugar

### En Windows
Simplemente hacé doble click en **`jugar_windows.bat`** o ejecutalo desde la consola:
```cmd
jugar_windows.bat
```
El script autodetectará tu instalación de Python, verificará `pygame-ce` y lanzará el juego inmediatamente.

### En Linux
Ejecutá el script lanzador con permisos de ejecución:
```bash
./jugar_pygame.sh
```

### Ejecución Manual (Cualquier Sistema)
Requiere **Python 3.10 o superior**:
```bash
# 1. Crear y activar entorno virtual (opcional pero recomendado)
python -m venv .venv
source .venv/bin/activate   # En Linux / macOS
# .venv\Scripts\activate    # En Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar el juego
python main.py
```

---

## ⚔️ Características Técnicas y Diseño

* **Física y Game Feel:** Coyote time (80 ms), jump buffer (120 ms), amortiguación cinemática post-dash y rebotes elásticos.
* **Iluminación Procedural y Claroscuro:** Penumbra gótica con caída cuadrática, halos translúcidos volumétricos y luz diegética a contraluz sobre el sepulturero.
* **HUD Gótico Integral:** Riel de interfaz con corazones de rubí, contador de almas volátiles y consagradas, dial rúnico de cooldown de dash, pips de vida extra y canal de mensajes con animación suave.
* **Campaña Completa:**
  1. *El Preludio:* El Ritual del Sepulturero (aprendizaje de movimiento y salto).
  2. *Nivel 1:* El Camposanto Bajo la Tormenta (fosos, altar de sombras y cuervos).
  3. *Nivel 2:* La Cripta de los Péndulos (altar de la pala, pisotón y plataformas móviles).
  4. *Nivel 3:* El Osario de los Herejes (encuentro con el Carcelero, Guadaña Consagrada y el Custodio).
  5. *Salas de Prueba:* Entornos de testeo técnico para aislar cada mecánica.

---

## 📜 Créditos

* **Desarrollo:** Equipo 6 — Taller de Diseño Conceptual / Introducción a los Videojuegos
* **Institución:** Universidad Nacional de Hurlingham (UNAHUR)
* **Licencia:** MIT License
