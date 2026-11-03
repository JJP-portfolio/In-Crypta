<?xml version="1.0" encoding="UTF-8"?>
<external_libraries_integration_plan project="IN CRYPTA" version="2.0" branch="feat/nextgen-libs-integration">
  <overview>
    Propuesta arquitectónica integral para elevar el apartado visual y sonoro de IN CRYPTA utilizando librerías especializadas del ecosistema Python, manteniendo la estética indie/homebrew (como Dead Cells, Celeste o Blasphemous) y un sistema de Fallback Gracioso (Graceful Degradation) para que el juego siga funcionando en entornos sin GPU o en la Sony Vaio.
  </overview>

  <recommended_libraries>
    <!-- ================================================================= -->
    <!-- 1. AUDIO VECTORIZADO Y DSP EN TIEMPO REAL: NumPy + SciPy          -->
    <!-- ================================================================= -->
    <library name="numpy + scipy" category="Audio Procedural, Síntesis Polifónica y Reverb">
      <pip_install>pip install numpy scipy</pip_install>
      <why_it_improves_300_percent>
        Actualmente `audio.py` genera muestras con un bucle `for i in range(total):` en Python puro, lo que limita la complejidad de los sonidos por tiempo de CPU.
        Con `numpy` vectorizado y `scipy.signal`:
        1. Síntesis 50x más rápida en C.
        2. **Reverberación de Catedral Gótica (Schroeder / Convolución):** Los chimes de las almas (`alma_1..alma_6`), el repique de las campanas (`campana_repique`) y los golpes de pala adquieren una cola de eco espacial de cripta real.
        3. **Filtro Paso-Bajo (Low-Pass Butterworth) reactivo:** Cuando el jugador queda a 1 HP o entra en pausa, se puede aplicar un filtro paso-bajo que ahoga las frecuencias agudas mientras late el corazón a 55 Hz.
        4. **Chimes Armónicos con Chorus Estéreo:** Desfase micro-temporal entre el canal izquierdo y derecho en los chimes de las gemas.
      </why_it_improves_300_percent>
      <implementation_blueprint target_file="audio_dsp.py"><![CDATA[
import math
import pygame

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def aplicar_reverb_cripta(onda_stereo: "np.ndarray", sample_rate: int = 44100, decay: float = 0.42) -> "np.ndarray":
    """Aplica una red de reverberación de catacumba (3 líneas de retardo primos) en estéreo con NumPy."""
    delays_ms = (37.0, 73.0, 113.0)
    out = onda_stereo.astype(np.float32).copy()
    for idx, d_ms in enumerate(delays_ms):
        offset = int((d_ms / 1000.0) * sample_rate)
        ganancia = (decay ** (idx + 1)) * 0.55
        if offset < len(out):
            # Cruce estéreo (ping-pong sutil entre L y R)
            out[offset:, 0] += onda_stereo[:-offset, 1] * ganancia
            out[offset:, 1] += onda_stereo[:-offset, 0] * ganancia
    max_val = np.max(np.abs(out))
    if max_val > 1.0:
        out /= max_val
    return out


def sintetizar_chime_dsp(frecuencia: float, duracion: float = 0.48, sample_rate: int = 44100) -> pygame.mixer.Sound:
    """Sintetiza un chime cristalino estéreo con chorus y reverberación de cripta usando NumPy."""
    t = np.linspace(0.0, duracion, int(sample_rate * duracion), endpoint=False, dtype=np.float32)
    tau = 2.0 * np.pi
    # Envolvente exponencial de campana de cristal
    env = np.exp(-t * 6.5) * np.minimum(1.0, t / 0.004)
    # Ligero detune estéreo (+1.5 Hz en R) para amplitud espacial
    mod = np.sin(tau * (frecuencia * 3.0) * t) * np.exp(-t * 12.0) * 0.8
    canal_l = (0.60 * np.sin(tau * frecuencia * t + mod) + 0.30 * np.sin(tau * (frecuencia * 2.0) * t) + 0.15 * np.sin(tau * (frecuencia * 4.0) * t)) * env
    canal_r = (0.60 * np.sin(tau * (frecuencia * 1.003) * t + mod) + 0.30 * np.sin(tau * (frecuencia * 2.004) * t) + 0.15 * np.sin(tau * (frecuencia * 4.0) * t)) * env

    stereo = np.column_stack((canal_l, canal_r)) * 0.35
    stereo = aplicar_reverb_cripta(stereo, sample_rate, decay=0.45)
    pcm16 = np.clip(stereo * 32767.0, -32767, 32767).astype(np.int16)
    return pygame.mixer.Sound(buffer=pcm16.tobytes())
]]></implementation_blueprint>
    </library>

    <!-- ================================================================= -->
    <!-- 2. SHADERS GLSL Y LUCES DINÁMICAS EN GPU: ModernGL                -->
    <!-- ================================================================= -->
    <library name="moderngl" category="Iluminación Dinámica 2D por GPU, Normal Maps Procedurales y CRT">
      <pip_install>pip install moderngl</pip_install>
      <why_it_improves_300_percent>
        En Pygame estándar, hacer Bloom (`smoothscale`) o máscaras de penumbra (`BLEND_RGBA_SUB`) consume CPU.
        Al subir `self.superficie_mundo` como una textura a `moderngl` (OpenGL 3.3+):
        1. **Costo 0 en CPU:** El escalado, el Bloom gótico, la aberración cromática al recibir daño, la niebla volumétrica por ruido Perlin/Simplex y las scanlines CRT ocurren en un único Fragment Shader de GPU en menos de 0.2ms.
        2. **Point Lights Dinámicas Reales:** Hasta 16 luces simultáneas (farol del jugador, cada alma flotante, velas, ojos de enemigos y chispas de la pala) iluminando los píxeles de las paredes con caída cuadrática real sin usar superficies `SRCALPHA`.
      </why_it_improves_300_percent>
      <implementation_blueprint target_file="gpu_pipeline.py"><![CDATA[
FRAGMENT_SHADER_GOTICO = """
#version 330 core
in vec2 uv;
out vec4 fragColor;

uniform sampler2D tex_mundo;
uniform sampler2D tex_ui;
uniform vec2 u_farol_pos;
uniform float u_tiempo;
uniform float u_trauma_aber;
uniform int u_modo_shader; // 0: Completo, 1: Suave, 2: Puro

void main() {
    // Aberración cromática sutil al recibir daño o en Fase 2 del Custodio
    vec2 shift = vec2(u_trauma_aber * 0.003, 0.0);
    float r = texture(tex_mundo, uv + shift).r;
    float g = texture(tex_mundo, uv).g;
    float b = texture(tex_mundo, uv - shift).b;
    vec3 col = vec3(r, g, b);

    if (u_modo_shader != 2) {
        // Luz puntual cálida en GPU alrededor del farol del sepulturero
        float dist_farol = distance(uv, u_farol_pos);
        float atten = clamp(1.0 - smoothstep(0.0, 0.28, dist_farol), 0.0, 1.0);
        col *= mix(0.72, 1.18, atten * atten);

        // Scanlines CRT suaves y viñeta periférica en un solo paso de GPU
        if (u_modo_shader == 0) {
            float scanline = sin(uv.y * 720.0 * 3.14159) * 0.04;
            col -= scanline;
        }
        float dist_centro = distance(uv, vec2(0.5, 0.5));
        col *= smoothstep(0.95, 0.38, dist_centro);
    }

    // Superponer capa de UI/HUD con alpha-blending nativo en GPU
    vec4 ui = texture(tex_ui, uv);
    fragColor = vec4(mix(col, ui.rgb, ui.a), 1.0);
}
"""
]]></implementation_blueprint>
    </library>

    <!-- ================================================================= -->
    <!-- 3. FÍSICA SECUNDARIA DECORATIVA: Pymunk (o Verlet Vectorizado)    -->
    <!-- ================================================================= -->
    <library name="pymunk" category="Cadenas Físicas, Candelabros Reactivos y Escombros de Osario">
      <pip_install>pip install pymunk</pip_install>
      <why_it_improves_300_percent>
        Permite que las cadenas colgantes de la Cripta y del Osario, las campanas de resonancia (`IncensarioRebote`) y los fragmentos de cráneos al romper una `LosaQuebradiza` reaccionen físicamente al paso del jugador, al viento del Dash y a las ondas de choque del Custodio, sin afectar en absoluto las colisiones deterministas del plataformeo (`jugador.rect`).
      </why_it_improves_300_percent>
    </library>
  </recommended_libraries>
</external_libraries_integration_plan>