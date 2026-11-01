# Instrucciones del repositorio PlataformeroMDA (para Repomix)

Este archivo contiene instrucciones personalizadas que Repomix incluirá en la sección `<instruction>` del output empaquetado. Está dirigido a asistentes de IA (LLMs) que analicen este código base.

## Propósito del repositorio

PlataformeroMDA es un videojuego de plataformas desarrollado en Python (Pygame). Contiene lógica de juego, entidades, niveles, HUD, partículas, audio, cámara y herramientas de exportación/integración con GDevelop.

## Directrices para el análisis de IA

1. **Enfócate en el código fuente principal** bajo los directorios raíz (`*.py`) y `tools/`. Los archivos de audio, imágenes y builds de GDevelop son assets y no deben ser el foco de refactorización.
2. **Archivos clave:**
   - `juego.py` — bucle principal del juego.
   - `nivel.py` / `niveles.py` / `niveles_rediseñados.py` — lógica y definición de niveles.
   - `entidades.py` — entidades del juego (jugador, enemigos, objetos).
   - `hud.py` — interfaz de usuario en pantalla.
   - `audio.py`, `camara.py`, `efectos.py`, `particulas.py` — subsistemas de audio, cámara, efectos visuales y partículas.
   - `config.py` — configuración centralizada.
   - `main.py` — punto de entrada.
   - `tools/` — utilidades de exportación, generación de proyectos e integración con GDevelop.
3. **Ignora archivos de prueba, caches y assets binarios** (`tests/`, `__pycache__/`, `.venv/`, `*.png`, `*.wav`, etc.) a menos que se pida específicamente.
4. **El proyecto usa Pygame.** Asume dependencias listadas en `requirements.txt`.
5. **No proporciones cambios destructivos** sin advertir explícitamente sobre el impacto en la jugabilidad.

## Casos de uso recomendados con Repomix

- Revisión de arquitectura y refactorización del motor de plataformas.
- Generación de documentación técnica del flujo de juego.
- Propuesta de pruebas unitarias para lógica de niveles y entidades.
- Búsqueda de patrones de colisión, física o estado de juego.

## Formato de salida esperado

El output de Repomix para este repositorio debe incluir:
- Resumen de archivos y estructura de directorios.
- Contenido de todos los archivos Python relevantes.
- Esta sección de instrucciones al final.
