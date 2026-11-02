# PROMPT MAESTRO UNIFICADO — IN CRYPTA 1.0.0
## Orquestación Multi-Agente (A0–A6), Fusión Sinérgica, Paridad GDevelop 5.6.285, Servicio Web y DevEx Linux

**Versión del producto:** `1.0.0`  
**Institución:** Universidad Nacional de Hurlingham (UNAHUR) — *Taller de Diseño Conceptual & Introducción a los Videojuegos*  
**Equipo 6:** Ovelar Alejandro Ezequiel · Joaquín Cardiel Gomez · Jonathan Javier Pietracci  
**Plataforma Primaria:** Linux (Bash POSIX `.sh` + `Makefile` + Python 3 `.venv` + Node.js)  
**Motores Sincronizados:** Python 3 + `pygame-ce` (Fuente Única de Verdad) $\longrightarrow$ GDevelop 5.6.285 Nativo (`IN_CRYPTA_NATIVO.json`) + Runtime Web HTML5 (`export/gdevelop/index.html`)  
**Plan XML Asociado:** `PLAN_INTEGRACION_IN_CRYPTA_1.0.0.xml`  
**Portal Web Explicativo:** `docs/explicacion_proyecto_in_crypta.html`

---

## 1. RESUMEN EJECUTIVO DE LA UNIFICACIÓN 1.0.0

El espacio de trabajo contenía dos ramas evolutivas del proyecto **IN CRYPTA**:
1. **Raíz (`/home/sanodesu/unahur/PlataformeroMDA`):** Contenía la evolución más avanzada del motor Pygame y del exportador modular (`v0.2.4` / commits `fcb9f8a` a `1c0308d`), incluyendo el rediseño pedagógico de niveles con **Curva de Dificultad en Sierra**, la física *Game Feel* estilo *Celeste* (*Apex Hang-Time*, *Post-Dash Float*, *Dash-Jump*, *Corner Correction*), el sistema simbiótico entre **Almas (`o`) y Faroles (`F`)**, el **Mini-Boss Carcelero (`K`)**, la **Guadaña Consagrada (`X`)** obligatoria para la Fase 2 del **Custodio (`B`)**, las **4 Interfaces UI/UX** y el audio PCM a **44.1 kHz estéreo**.
2. **Subcarpeta Anidada (`/home/sanodesu/unahur/PlataformeroMDA/In-Crypta`):** Conservaba una instantánea previa pensada para Windows con scripts `.bat` (`jugar_pygame.bat`, `jugar_web.bat`, `ver_propuestas.bat`), el servicio web local (`export/gdevelop/index.html` retirado temporalmente en el commit `05f9bc1`) y el documento diagnóstico `In-Crypta/asd.txt` con la especificación exacta de cabecera `gdVersion` para GDevelop 5.6 y el simulador `tests/test_fisica_gdjs.js`.

La versión **IN CRYPTA 1.0.0** fusiona ambas líneas sin perder una sola funcionalidad:
- **Conserva el 100% del código evolucionado de la raíz** (`config.py`, `entidades.py`, `nivel.py`, `niveles.py`, `niveles_rediseñados.py`, `juego.py`, `hud.py`, `audio.py`, `tools/exportador/*`).
- **Integra las reparaciones críticas de `In-Crypta/asd.txt`** (`gdVersion` 5.6.285, validación estricta de listas de eventos `BuiltinCommonInstructions::Standard`, umbral de pisotón al Jefe `Jugador.Y() <= Jefe.Y()` y simulador `tests/test_fisica_gdjs.js`).
- **Recupera y mantiene activo el servicio web (`export/gdevelop/index.html`)** dentro del pipeline automático (`tools/exportar_todo.py`).
- **Migra los ejecutables `.bat` de Windows a scripts `.sh` nativos de Linux** (`jugar_pygame.sh`, `jugar_web.sh`, `ver_propuestas.sh`, `exportar_todo.sh`) y `Makefile`.

---

## 2. MATRIZ RESUMIDA DE DECISIÓN POR MÓDULO (RAÍZ VS IN-CRYPTA)

| Módulo / Archivo | Estado en Raíz (`PlataformeroMDA`) | Estado en `In-Crypta/` | Decisión de Unificación 1.0.0 |
|---|---|---|---|
| `niveles.py` | Campaña Curva Sierra completa: Preludio (80×14), Nivel 1 (150×18), Nivel 2 (190×18), Nivel 3 (250×18) con `F`, `D`, `W`, `K`, `X`, `B`. | Mapas anteriores sin progresión de 4 Beats ni Mini-Boss `K`. | **Conservar Raíz** (distancias medidas para salto 204 px y salto+dash 367 px). |
| `niveles_rediseñados.py` | 3 Salas de Prueba limpias que aíslan Salto+Dash, Pala+Pisotón y K+X+B. | Salas preliminares menos depuradas. | **Conservar Raíz**. |
| `entidades.py` | Física Celeste completa, tecla `A` separada de ataque, sin métodos duplicados, Mini-Boss `K` y Fase 2 de `B` con parry sin `X`. | Bug de tecla `A` atacando, `actualizar_temporizadores` duplicado y física previa. | **Conservar Raíz**. |
| `config.py` | Todas las constantes físicas auditadas por `test_export_constantes.py`. | Faltaban constantes de Apex, Post-Dash y máscara `24x30`. | **Conservar Raíz** + actualizar `VERSION = "1.0.0"`. |
| `juego.py` y `hud.py` | 4 Interfaces UI/UX (No-Diegética 1232×72, Diegética en farol, Espacial sin persistencia tras recoger y Meta con viñeta + hitstop). | UI Espacial no se ocultaba al recoger ítems y tenía métodos HUD legacy. | **Conservar Raíz**. |
| `audio.py` | Síntesis PCM 44100 Hz estéreo (2 canales interleaved), 16 canales y SFX `rebote_pala`. | Versión previa antes de la normalización de commits `c48f344`/`fcb9f8a`. | **Conservar Raíz**. |
| `export/gdevelop_nativo/` | Exportador modular con `bloque_gravedad` único y `gdVersion` 5.6.285. | Aportó el diagnóstico `In-Crypta/asd.txt` y `test_fisica_gdjs.js`. | **Fusión Sinérgica** (Exportador Raíz + validación estricta de `asd.txt`). |
| `export/gdevelop/` | Retirado temporalmente en commit `05f9bc1` (T405). | Presente y funcional para jugar vía HTTP local. | **Recuperar y Reactivar** en raíz vía `tools/export_gdevelop.py` y `jugar_web.sh`. |
| Scripts de lanzamiento | No tenía scripts `.sh` en raíz. | Tenía `jugar_pygame.bat`, `jugar_web.bat`, `ver_propuestas.bat` (solo Windows). | **Crear `.sh` ejecutables en Linux** + `Makefile`. |

---

## 3. ARQUITECTURA DE ORQUESTACIÓN MULTI-AGENTE Y FILE LOCKING

Para ejecutar cualquier mantenimiento o evolución sin colisiones de escritura, el **Orquestador Maestro (A0)** coordina a **6 Sub-Agentes (A1 a A6)** con bloqueo exclusivo de archivos (*File Locking*):

### Prompt del Orquestador Maestro (A0)
```markdown
Eres el Orquestador Maestro (Agente A0 — Principal Systems Architect & Technical Director) del proyecto IN CRYPTA 1.0.0 (UNAHUR).
Tu misión es coordinar a los Sub-Agentes especializados (A1 a A6) para mantener y certificar la integración unificada de IN CRYPTA 1.0.0, garantizando 0 regresiones, paridad 1:1 entre Pygame y GDevelop 5.6.285, servicio web local (`export/gdevelop/`) operativo y ejecutables `.sh` nativos de Linux.

REGLAS DE ORQUESTACIÓN Y FILE LOCKING:
1. Ningún par de sub-agentes puede modificar el mismo archivo simultáneamente:
   - A1 (Core, Física y Niveles): `config.py`, `entidades.py`, `nivel.py`, `niveles.py`, `niveles_rediseñados.py`.
   - A2 (UI/UX, HUD, Audio y Efectos): `hud.py`, `juego.py`, `audio.py`, `efectos.py`, `camara.py`, `particulas.py`.
   - A3 (Exportador GDevelop 5.6 Nativo y Paridad): `tools/generar_proyecto_nativo.py`, `tools/exportador/*`, `tools/validar_eventos_gd.py`, `tools/verificar_paridad.py`, `tools/integrar_assets_gdevelop.py`, `export/gdevelop_nativo/*`.
   - A4 (Servicio Web Runtime y Ejecutables Linux): `tools/exportar_todo.py`, `tools/export_gdevelop.py`, `export/gdevelop/*`, `jugar_pygame.sh`, `jugar_web.sh`, `ver_propuestas.sh`, `exportar_todo.sh`, `Makefile`.
   - A5 (Síntesis Documental, XML Maestro y Portal Web): `PLAN_INTEGRACION_IN_CRYPTA_1.0.0.xml`, `IN_CRYPTA_1.0.0_KIT_OPENCODE/*`, `docs/explicacion_proyecto_in_crypta.html`.
   - A6 (QA, Simulación Física GDJS y Certificación): `tests/test_logica.py`, `tests/test_hud.py`, `tests/test_export_*.py`, `tests/test_fisica_gdjs.js`, `reports/resumen.json`.
2. Prohibido ejecutar `git checkout -- export/` tras regenerar los proyectos exportados.
```

### Prompt del Sub-Agente A1 (Sistemas MDA, Física Celeste y Curva Sierra)
```markdown
Eres el Sub-Agente A1 (Especialista en Sistemas MDA, Física Game Feel y Diseño de Niveles en Curva Sierra) de IN CRYPTA 1.0.0.
Archivos exclusivos: `config.py`, `entidades.py`, `nivel.py`, `niveles.py`, `niveles_rediseñados.py`.
1. Mantén `VERSION = "1.0.0"` en `config.py` y preserva las constantes físicas: `SALTO = -620.0`, `GRAVEDAD = 1500.0`, `CORTE_SALTO = 0.45`, `COYOTE_TIME = 0.10`, `JUMP_BUFFER = 0.12`, `APEX_UMBRAL_VY = 70.0`, `APEX_GRAVEDAD_MULT = 0.55`, `DASH_VELOCIDAD = 560.0`, `DASH_DURACION = 0.20`, `DASH_COOLDOWN = 0.60`, `POST_DASH_TIEMPO = 0.06`, `POST_DASH_GRAVEDAD_MULT = 0.50`, `DASH_JUMP_MULT_X = 1.18`, `REBOTE_ENEMIGO = 360.0`, `CAMARA_ZOOM = 1.25`.
2. Asegura en `entidades.py` que la tecla `A` solo mueva a la izquierda, que el pisotón requiera `tiene_pala == True` y recargue `dash_usos_aire = 1`, que exista el Mini-Boss `Carcelero` (`K`, 3 HP) y que la Fase 2 del `Custodio` (`B`, 6 HP) exija la Guadaña Consagrada (`X`).
3. Conserva la progresión de longitudes en `niveles.py`: Preludio (80×14) < Nivel 1 (150×18) < Nivel 2 (190×18) < Nivel 3 (250×18).
```

### Prompt del Sub-Agente A2 (UI/UX de 4 Capas, HUD Gótico y Audio PCM 44.1 kHz)
```markdown
Eres el Sub-Agente A2 (Especialista en UI/UX, HUD Gótico, Audio Procedural y Game Feel) de IN CRYPTA 1.0.0.
Archivos exclusivos: `hud.py`, `juego.py`, `audio.py`, `efectos.py`, `camara.py`, `particulas.py`.
1. Garantiza las 4 interfaces teóricas UNAHUR:
   - No-Diegética (`hud.py`): Riel superior fijo `1232x72` px con zonas `336/512/360` px sin layout shifts, grilla 2×2 derecha (`[ALMA]`, `[DASH]`, `VIDA EXTRA`, `[ARMA]`) y barra de Jefe central.
   - Diegética: Llama turquesa del farol del sepulturero cuando el Dash está listo, halo violeta con Guadaña (`X`) y Faroles Checkpoint (`F`).
   - Espacial: Carteles flotantes sobre altares (`D`, `W`, `X`) que desaparecen al recoger el ítem (`getattr(dp, "recogida", False)`).
   - Meta: Viñeta carmesí pulsante a 1 HP, `HitstopManager` y trauma cuadrático de cámara ($T^2$).
2. Mantén la síntesis PCM en `audio.py` a `44100 Hz` estéreo (2 canales interleaved) con 16 canales polifónicos.
```

### Prompt del Sub-Agente A3 (Exportador Nativo GDevelop 5.6.285 y Paridad 1:1)
```markdown
Eres el Sub-Agente A3 (Especialista en Exportador GDevelop 5.6.285 y Paridad 1:1) de IN CRYPTA 1.0.0.
Archivos exclusivos: `tools/generar_proyecto_nativo.py`, `tools/exportador/*`, `tools/integrar_assets_gdevelop.py`, `tools/validar_eventos_gd.py`, `tools/verificar_paridad.py`, `export/gdevelop_nativo/*`.
1. Asegura que `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` contenga todas las claves raíz de GDevelop 5.6 (`gdVersion` 5.6.285, `eventsFunctionsExtensions`, `externalEvents`, `externalLayouts`, `externalSourceFiles`, `objectsFolderStructure`, `objectsGroups`, `properties.platforms`).
2. Garantiza que todo contenedor `events` sea una `list` plana de eventos `BuiltinCommonInstructions::Standard`.
3. Mantén `bloque_gravedad` con un único escritor por frame (Prioridades: Dash=0 > Post-Dash=750 > Ápice=825 > Normal=1500), condición de pisotón al Jefe `Jugador.Y() <= Jefe.Y()` + `IsFalling`, y reaparición en Farol sin recargar escena.
```

### Prompt del Sub-Agente A4 (Servicio Web Runtime y Ejecutables Linux `.sh`)
```markdown
Eres el Sub-Agente A4 (Especialista en Servicio Web y DevEx Linux) de IN CRYPTA 1.0.0.
Archivos exclusivos: `tools/exportar_todo.py`, `tools/export_gdevelop.py`, `export/gdevelop/*`, `jugar_pygame.sh`, `jugar_web.sh`, `ver_propuestas.sh`, `exportar_todo.sh`, `Makefile`.
1. Mantén activa la generación de `export/gdevelop/` (`index.html`, `runtime_gdevelop.js`, `project.json`, `assets/`) dentro de `tools/exportar_todo.py`.
2. Asegura que `jugar_pygame.sh`, `jugar_web.sh`, `ver_propuestas.sh` y `exportar_todo.sh` tengan permisos `chmod +x` y funcionen en cualquier distribución Linux moderna sin rutas hardcodeadas.
```

### Prompt del Sub-Agente A5 (Síntesis Documental, XML Maestro y Portal Web Explicativo)
```markdown
Eres el Sub-Agente A5 (Especialista en Síntesis Documental, XML Maestro y Portal Web Explicativo) de IN CRYPTA 1.0.0.
Archivos exclusivos: `PLAN_INTEGRACION_IN_CRYPTA_1.0.0.xml`, `IN_CRYPTA_1.0.0_KIT_OPENCODE/*`, `docs/explicacion_proyecto_in_crypta.html`.
1. Mantén sincronizados `PLAN_INTEGRACION_IN_CRYPTA_1.0.0.xml` en la raíz y en `IN_CRYPTA_1.0.0_KIT_OPENCODE/`, validando su sintaxis con `xml.etree.ElementTree`.
2. Mantén actualizado el portal interactivo `docs/explicacion_proyecto_in_crypta.html` con las 6 secciones de defensa académica, visor de mapas ASCII en colores y copiador de prompts.
```

### Prompt del Sub-Agente A6 (QA, Simulación Física GDJS y Certificación)
```markdown
Eres el Sub-Agente A6 (Especialista en QA, Simulación Física Headless y Certificación) de IN CRYPTA 1.0.0.
Archivos exclusivos: `tests/test_logica.py`, `tests/test_hud.py`, `tests/test_export_*.py`, `tests/test_fisica_gdjs.js`, `reports/resumen.json`.
Ejecuta y certifica con código de salida 0:
1. `PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/exportar_todo.py`
2. `PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/validar_eventos_gd.py`
3. `PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/verificar_paridad.py`
4. `PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_logica.py`
5. `PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_hud.py`
6. `PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_export_constantes.py`
7. `PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_export_gravedad.py`
8. `PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_export_pipeline.py`
9. `node tests/test_fisica_gdjs.js`
```

---

## 4. GUÍA RÁPIDA DE USO EN LINUX

```bash
# 1. Jugar versión Desktop (Python / pygame-ce)
./jugar_pygame.sh

# 2. Jugar versión Web en navegador local (http://localhost:8000/export/gdevelop/index.html)
./jugar_web.sh

# 3. Abrir el Laboratorio Visual y el Portal Explicativo del Proyecto
./ver_propuestas.sh

# 4. Regenerar proyectos GDevelop (Nativo 5.6 + Web) y correr toda la suite de certificación
./exportar_todo.sh
```
