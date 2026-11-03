# ACUERDO DE COORDINACIÓN ENTRE AGENTES AGY

Este documento establece la delimitación de responsabilidades entre los dos agentes en ejecución para garantizar **cero pisadas ni conflictos de código**:

---

## 1. Agente A (Argon — Renovación Sensorial)
- **Directorio de trabajo:** `/home/sanodesu/unahur/PlataformeroMDA`
- **Rama Git:** `art/overhaul-sensorial`
- **Misión:** Renovación Sensorial Integral (Música OGG, Contraste de Enemigos C1-C3, Tiles B1-B3, HUD A1-A3, HitSparks D1-D3, F3 Debug, F4 Selector).
- **Archivos bajo su responsabilidad:**
  - `config.py` (Paleta de luminancia y función `resolver_estilo`)
  - `audio.py` (Mezcla de pistas OGG y dron)
  - `entidades.py` (Dibujo C1/C2/C3, flash de daño, arco de ataque, losa quebradiza)
  - `particulas.py` (Efectos `HitSpark`)
  - `nivel.py` (`dibujar_solidos`, `dibujar_plataformas` con Walkable Edge Cue)
  - `hud.py` (Modelos de panel A1/A2/A3, tweens reactivos)
  - `juego.py` (Atenuación de fondos, integración de audio, tecla F3, tecla F4)
- **Regla Estricta (Guardrails G1-G3):**
  - **NO toca** `niveles.py` (cadenas ASCII intactas).
  - **NO toca** físicas en `config.py` (gravedad, salto, velocidad, etc.).
  - **NO toca** lógica ni rects de colisión en `entidades.py`.

---

## 2. Agente B (Arquitectura y Variante Vertical de Niveles)
- **Directorio de trabajo:** `/home/sanodesu/unahur/IN_CRYPTA_v1.0.0_Desktop_Release`
- **Misión:** Variante vertical del Osario (`NIVEL_3_VERTICAL` de 36 filas, 2 pisos, caída por pozo y validación formal de invariantes).
- **Archivos bajo su responsabilidad:**
  - `niveles.py` (`NIVEL_3_VERTICAL`, `NIVELES_VERTICALES`)
  - `tools/validar_niveles.py`
  - `tests/test_niveles_verticales.py`
  - `config.py` (`OSARIO_VERTICAL = False` flag opcional)
  - `juego.py` (`_mismo_piso()` y lógica específica de checkpoints verticales)

---

## 3. Estado de Fusión
Ambas líneas de trabajo son **100% ortogonales**:
- Las mejoras de Agente A se centran en el *renderizado, feedback de combate y audio*.
- Las mejoras de Agente B se centran en el *layout ASCII y altura de cámara*.
Cuando ambas tareas finalicen, podrán combinarse sin fricción.
