# 📜 PROMPT PARA ARGON — ESTADO VISUAL, MENÚS, SISTEMA DE CALIDAD Y FEATURE DE EXPORT WEB

> **Contexto Técnico:** Este documento describe el estado del código visual y de audio tras la ejecución de la Renovación Sensorial de *IN CRYPTA* en la rama `art/overhaul-sensorial`. Se acompaña del archivo empaquetado por Repomix:  
> `repomix/repomix_overhaul_sensorial_y_calidad.xml` (131k tokens, 8 archivos completos: `config.py`, `audio.py`, `hud.py`, `nivel.py`, `entidades.py`, `particulas.py`, `juego.py` y `COORDINACION_AGENTES.md`).

---

## 1. MISIÓN Y SOLICITUD DEL USUARIO

Actúa como **Argon**, Director Técnico de Arte y Arquitecto de Rendimiento en Pygame / WebAssembly.  
El usuario ha probado la versión actual y desea planificar e implementar la siguiente **Feature de Rendimiento y Bifurcación Visual**:

1. **Calidad Alta (Exclusiva para Desktop / Python Nativo):**  
   Mantener y potenciar todo el pipeline gráfico "pesado y hermoso" que hace único al juego en PC:
   * Bloom místico aditivo (`pygame.transform.smoothscale`).
   * Máscara de penumbra gótica completa con perforación substractiva (`BLEND_RGBA_SUB`) y halos de luz aditivos concéntricos (`BLEND_RGB_ADD`).
   * Micro-scanlines CRT cinematográficas.
   * Partículas al 100% (incluyendo 25 partículas flotantes de bioma).
   * Estilo visual **Procedural Gótico (PROC)**: Modelo A3 en HUD (filigrana y agujas góticas), Modelo B3 en Tiles (raíces, salitre, nichos con calaveras y Walkable Edge Cues), Modelo C3 en Entidades (esqueletos anatómicos con fuego fatuo y halos de color) y Modelo D3 en partículas (estrellas góticas de 4 puntas).

2. **Calidad Baja (Export Único y Optimizado para Web / Pygbag / WASM):**  
   Convertir la Calidad Baja en el **perfil de exportación por defecto y optimizado al extremo para navegadores web**, garantizando **60 FPS estables y fluidos** sin lag de recolección de basura ni caídas de fotogramas:
   * **Cero superficies SRCALPHA de pantalla completa** (eliminar viñetas pesadas, penumbra y bloom que asfixian el fill-rate de WebAssembly en canvas HTML5).
   * Paneles del HUD 100% opacos (`.convert()` directo a 24-bits sin canal alfa) mediante el Modelo A1 (NES).
   * Estilo visual **NES 8-Bit (NES)**: Tiles B1 de relleno plano y división ortogonal, siluetas ectoplásmicas C1 de alto contraste ($\Delta Y > 170$) y cruz ortogonal D1.
   * Reducción drástica o apagado de partículas de bioma innecesarias.

3. **Calidad Media (Intermedia Balanceada):**  
   Perfil SNES 16-Bit con penumbra ligera de un solo halo y mampostería estratificada para máquinas modestas.

---

## 2. QUÉ SE HIZO (LOGROS IMPLEMENTADOS)

* **Orquestación de Audio (`audio.py` y `juego.py`):**
  * Se conectaron las **10 pistas OGG** (`titulo`, `camposanto`, `cripta`, `osario`, `carcelero`, `custodio_f1`, `custodio_f2`, `victoria`, `derrota`, `creditos`).
  * La música transiciona automáticamente sin reinicios redundantes (`self.musica_actual`) y el dron ambiental se rebalanceó a volumen `0.045` (música a `0.45`).
* **Erradicación del Camuflaje de Enemigos (`entidades.py`):**
  * Se implementaron 3 modelos con contraste calibrado ($\Delta Y > 150$):
    * **C1 (NES):** Borde ectoplásmico exterior de +2px en `ENEMIGO_RIM_LUZ = (225, 228, 240)`, cuerpo azul noche `(24, 32, 54)` y ojos de fuego carmesí `(255, 52, 68)`.
    * **C2 (SNES):** Túnica mortaja azul noche `(36, 48, 72)` o púrpura `(52, 28, 64)`, Rim Light cenital de 2px y mandobles en acero claro `(165, 178, 198)`.
    * **C3 (PROC):** Anatomía ósea de marfil con fuego fatuo turquesa pulsante en el pecho.
  * **Damage Flash:** Silueta instantánea en blanco puro `FX_IMPACTO_BLANCO = (250, 248, 240)` de 2 frames (0.06s).
  * **Hit-Sparks (`particulas.py`):** Chispas direccionales en el punto exacto de colisión (`D1` cruz 8-bit, `D2` biseccionado, `D3` estrella gótica).
  * **Alineación 1:1:** El arco de ataque del sepulturero coincide con `rect_ataque()`.
  * **Losas Quebradizas:** Base hueca dentada y grietas diagonales ámbar/turquesa visibles en reposo.
* **Separación de 3 Planos y Walkable Edge Cues (`nivel.py` y `juego.py`):**
  * Fondos atenuados en contraste y luminancia un 30% usando `BG_NOCHE_PROFUNDA` ($Y=10.6$), `BG_PIEDRA_NIEBLA` ($Y=24.4$) y `BG_SILUETA_FRIA` ($Y=34.0$).
  * Modelos de terreno B1 (NES), B2 (SNES) y B3 (PROC) con losa superior caminable en `c_bisel_top` ($Y > 175$) y corte negro de 2px `(10, 8, 14)`.
* **HUD y Relicarios (`hud.py`):**
  * Modelos A1 (NES opaco sin alpha), A2 (SNES biselado 3D con remaches) y A3 (PROC filigrana gótica).
  * Corazones escalonados pixel-art en NES, gemas octogonales en SNES y Corazón Delator en PROC.
  * Tweens reactivos de feedback: temblor ($\pm 2\text{ px}$) en la barra del jefe en Fase 2 y destello turquesa pulsante al recargar el Dash.
* **Herramientas de Inspección en Vivo:**
  * Tecla **`F3`**: Visualizador de Hitbox/Hurtbox (Verde=Jugador, Naranja=Enemigos/Jefe, Rojo con aspas=Hitbox activa, Violeta=Peligros).
  * Tecla **`F4`**: Selector dinámico de estilos (`AUTO` $\rightarrow$ `NES` $\rightarrow$ `SNES` $\rightarrow$ `PROC`).
* **Coordinación Inter-Agente:** Delimitación formal con el agente de la variante vertical (`COORDINACION_AGENTES.md`).
* **Validación Total:** 51/51 tests en verde en `pytest tests/`, `test_logica.py` 100% OK y cero solapamientos en `HudLayout`.

---

## 3. APARTADO ESPECIAL: CÓDIGO DEL SISTEMA DE CALIDAD Y MENÚS

### A. Selector de Calidad y Resolución de Estilos
En `config.py`:
```python
ESTILO_HUD = "AUTO"       # Modelos A1 ("NES"), A2 ("SNES"), A3 ("PROC")
ESTILO_MUNDO = "AUTO"     # Modelos B1 ("NES"), B2 ("SNES"), B3 ("PROC")
ESTILO_ENEMIGOS = "AUTO"  # Modelos C1 ("NES"), C2 ("SNES"), C3 ("PROC")
ESTILO_EFECTOS = "AUTO"   # Modelos D1 ("NES"), D2 ("SNES"), D3 ("PROC")
CALIDAD_GLOBAL_ACTIVA = PERFIL_WEB_CALIDAD if ES_WEB else 0

def resolver_estilo(preferencia: str, calidad_idx: int = None) -> str:
    """Devuelve 'NES', 'SNES' o 'PROC' según la preferencia o el nivel de calidad."""
    if calidad_idx is None:
        calidad_idx = CALIDAD_GLOBAL_ACTIVA
    if preferencia in ("NES", "SNES", "PROC"):
        return preferencia
    return {0: "PROC", 1: "SNES", 2: "NES"}.get(calidad_idx, "PROC")
```

En `juego.py` (`alternar_calidad_grafica`):
```python
def alternar_calidad_grafica(self, delta=1):
    self.config_calidad_idx = (self.config_calidad_idx + delta) % len(OPCIONES_CALIDAD)
    import config
    config.CALIDAD_GLOBAL_ACTIVA = self.config_calidad_idx
    if hasattr(self, "hud") and hasattr(self.hud, "renderer"):
        self.hud.renderer._paneles_cache.clear()
    self.audio.reproducir("ui")
    factores = {0: 1.0, 1: 0.5, 2: 0.25}
    self.particulas.factor_calidad = factores.get(self.config_calidad_idx, 1.0)
    tema = self.nivel.tema if self.nivel and hasattr(self.nivel, "tema") else "camposanto"
    self.reiniciar_particulas_bioma(tema)
    calidad = OPCIONES_CALIDAD[self.config_calidad_idx]
    self.hud.mostrar_mensaje(f"CALIDAD GRÁFICA: {calidad.upper()}", 1, 3.0)
```

En `juego.py` (`dibujar` - discriminación de efectos según calidad):
```python
# Penumbra gótica: Alta (0) y Media (1) activas; Baja (2) OMITIDA para 60 FPS
if getattr(self, "config_calidad_idx", 0) != 2:
    self.mascara_penumbra.fill((8, 7, 12, 38))
    # Perforación substractiva centrada en farol
    ...
    destino.blit(self.mascara_penumbra, (0, 0))

# Halos de luz aditivos: Alta (0) completos; Media (1) factor 0.65; Baja (2) OMITIDOS
calidad = getattr(self, "config_calidad_idx", 0)
if calidad in (0, 1):
    ...
    destino.blit(luz_add, (fx - radio_luz, fy - radio_luz), special_flags=pygame.BLEND_RGB_ADD)

# Shaders de pantalla completa (Bloom + CRT scanlines)
shader_modo = getattr(self, "config_shader_idx", 0)
calidad_modo = getattr(self, "config_calidad_idx", 0)
if shader_modo in (0, 1) and calidad_modo != 2:
    self._aplicar_bloom(self.pantalla, self.pantalla, intensidad=0.12 if shader_modo == 0 else 0.08)
if shader_modo == 0 and calidad_modo != 2:
    self.pantalla.blit(self._superficie_scanlines, (0, 0))
```

### B. Código del Menú Principal y Configuración del Santuario
En `juego.py`:
* **Apertura de Menús:** `abrir_menu()`, `abrir_configuracion()`, `abrir_seleccion_nivel()`, `abrir_creditos()`.
* **Procesamiento de Eventos (`procesar_eventos`):**
  * Navegación vertical `[W/S]` o `[↑/↓]`.
  * Confirmación `[ENTER]` o `[ESPACIO]`.
  * Ajustes horizontales `[A/D]` o `[←/→]` en configuración para alternar presets de teclado, shaders, calidad, HUD, accesibilidad y sonido.
  * Teclas directas: `F1` (Accesibilidad), `F3` (Debug Hitboxes), `F4` (Ciclo de Estilos).
* **Renderizado Visual (`dibujar_menu_principal` y `dibujar_configuracion`):**
  * Uso de `dibujar_marco_heraldico()` con remates dorados y esquinas heráldicas.
  * Cajas de selección con resaltador lateral dorado y sombras de texto.
  * Leyenda constante de navegación en el pie de página.

---

## 4. QUÉ NO SE PUDO HACER, LIMITACIONES Y OBSERVACIONES IMPORTANTES

1. **El cuello de botella de Pygame en Web (Canvas 2D / WebAssembly):**  
   En desktop nativo, Pygame vuela a más de 300 FPS porque la CPU de escritorio tiene caché grande y ancho de banda de memoria masivo. En navegadores vía Pygbag (emscripten), cada superficie `SRCALPHA` de `1280x720` que se blitea con `BLEND_RGBA_SUB` o `BLEND_RGB_ADD` implica un bucle de mezcla de píxeles en memoria WebAssembly antes de pasar al canvas del navegador. Por eso, **el modo Web debe ser estrictamente sin penumbra pesada y con paneles `.convert()` opacos**.
2. **Independencia de Físicas y Mapas (Guardrails G1-G3):**  
   Durante todo el overhaul se mantuvieron intactos `niveles.py`, las constantes de física de salto/dash y los tamaños de las cajas de colisión. El juego se siente idéntico al tacto, pero luce y suena como un producto terminado.
3. **Comportamiento en modo `dummy` (Headless):**  
   Los drivers de audio y video `dummy` no cargan canales de música reales ni crean ventanas gráficas físicas; los tests y validadores deben usar siempre bloques `try/except` al invocar `pygame.mixer.music` o `.convert()`.

---

## 5. INSTRUCCIONES DE ACCIÓN PARA ARGON

Diseña e implementa el plan para bifurcar y perfeccionar la experiencia según el entorno de ejecución:

1. **Configurar el export Web exclusivo (`Calidad Baja = Web Build`):**
   * Asegurar que cuando `ES_WEB` sea `True` (o cuando se invoque `jugar_web.sh` / `publicar_gd_games.sh`), el juego fuerce por defecto:
     * `CALIDAD_GLOBAL_ACTIVA = 2` (Baja).
     * `ESTILO_HUD = "NES"`, `ESTILO_MUNDO = "NES"`, `ESTILO_ENEMIGOS = "NES"`, `ESTILO_EFECTOS = "NES"`.
     * Cero cálculo de `mascara_penumbra`, cero `smoothscale` de bloom y cero scanlines.
     * Desactivar o limitar partículas de bioma a 0 o 5 máximo.
2. **Configurar el showcase Desktop nativo (`Calidad Alta = Desktop Full PROC`):**
   * Cuando se ejecute en PC nativo (`ES_WEB = False`), arrancar en Calidad Alta con estilo `PROC`:
     * Procedural completo en biomas (raíces en Camposanto, salitre en Cripta, osamentas en Osario).
     * Fuego fatuo y partículas de bioma (25 flotando con paralaje).
     * Bloom místico enriquecido y penumbra profunda.
3. **Garantizar que la suite `pytest tests/` siga arrojando 51 passed y 100% verde.**
