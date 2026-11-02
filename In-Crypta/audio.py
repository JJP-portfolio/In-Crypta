# ============================================================
# audio.py — Sonidos procedurales de IN CRYPTA
# ============================================================
# No hay archivos de audio externos: cada efecto se genera como
# una onda PCM int16 estéreo 44.1 kHz en memoria en tiempo de ejecución.
# Así el proyecto queda 100% autocontenido, liviano y procedural.
# ============================================================

import array
import math
import random

import pygame


FRECUENCIA_MUESTREO = 44100
CANALES = 2
FACTORES_MICROTONALES = (-0.025, 0.025)


def obtener_init_audio():
    init = pygame.mixer.get_init()
    if init:
        return init[0], init[2]
    return FRECUENCIA_MUESTREO, CANALES


# --- Función generar_pcm --- #
def generar_pcm(frecuencia, duracion, volumen=0.25, forma="seno", barrido=0.0, freq=None, canales=None):
    """Genera un buffer PCM int16 mono o estéreo a partir de parámetros sinusoidales o ruidosos."""
    if freq is None or canales is None:
        f_actual, c_actual = obtener_init_audio()
        freq = freq or f_actual
        canales = canales or c_actual

    cantidad = int(freq * duracion)
    muestras = array.array("h", [0]) * (cantidad * canales)
    inv_cant = 1.0 / max(1, cantidad - 1)
    tau = math.tau
    fase = 0.0

    for i in range(cantidad):
        progreso = i * inv_cant
        frecuencia_actual = frecuencia + barrido * progreso
        fase += tau * frecuencia_actual / freq

        if forma == "cuadrada":
            onda = 1.0 if math.sin(fase) >= 0 else -1.0
        elif forma == "sierra":
            onda = 2.0 * ((fase / tau) % 1.0) - 1.0
        elif forma == "triangulo":
            onda = 2.0 * abs(2.0 * ((fase / tau) % 1.0) - 1.0) - 1.0
        elif forma == "ruido":
            onda = random.uniform(-1.0, 1.0)
        elif forma in ("bell", "campana"):
            onda = (
                math.sin(fase)
                + 0.35 * math.sin(fase * 2.0)
                + 0.15 * math.sin(fase * 3.0)
                + 0.08 * math.sin(fase * 4.2)
            )
        else:
            onda = math.sin(fase)

        ataque = min(1.0, progreso / 0.06)
        caida = max(0.0, 1.0 - progreso)
        envolvente = ataque * (caida ** 1.8)
        valor = int(32767 * volumen * envolvente * onda)
        clamped = max(-32768, min(32767, valor))

        if canales == 2:
            idx = i * 2
            muestras[idx] = clamped
            muestras[idx + 1] = clamped
        else:
            muestras[i] = clamped

    return muestras.tobytes(), freq, canales


# --- Función crear_tono --- #
def crear_tono(frecuencia, duracion, volumen=0.25, forma="seno", barrido=0.0):
    pcm_bytes, _, _ = generar_pcm(frecuencia, duracion, volumen, forma, barrido)
    return pygame.mixer.Sound(buffer=pcm_bytes)


# --- Síntesis de Campana Litúrgica --- #
def generar_campana_liturgica(
    frecuencia, duracion=0.22, volumen=0.18, barrido=0.0, freq=None, canales=None
):
    """Síntesis aditiva de campana tubular eclesiástica con armónicos enriquecidos
    y decaimiento diferenciado por frecuencia (sobretonos metálicos efímeros
    y fundamental resonante prolongado).
    """
    if freq is None or canales is None:
        f_actual, c_actual = obtener_init_audio()
        freq = freq or f_actual
        canales = canales or c_actual

    cantidad = int(freq * duracion)
    muestras = array.array("h", [0]) * (cantidad * canales)
    inv_cant = 1.0 / max(1, cantidad - 1)
    tau = math.tau
    fase = 0.0

    for i in range(cantidad):
        prog = i * inv_cant
        f_act = frecuencia + barrido * prog
        fase += tau * f_act / freq

        # Ataque percusivo metálico ultra-rápido (~3 ms)
        atq = min(1.0, prog / 0.015)
        caida = max(0.0, 1.0 - prog)

        # Decaimientos diferenciados: armónicos superiores mueren antes
        env_f0 = atq * (caida ** 1.5)
        env_f1 = atq * (caida ** 2.5)
        env_f2 = atq * (caida ** 3.6)

        onda = (
            math.sin(fase) * env_f0
            + 0.35 * math.sin(fase * 2.0) * env_f1
            + 0.15 * math.sin(fase * 3.0) * env_f2
            + 0.08 * math.sin(fase * 4.2) * env_f2
        )

        valor = int(32767 * volumen * onda)
        clamped = max(-32768, min(32767, valor))

        if canales == 2:
            idx = i * 2
            muestras[idx] = clamped
            muestras[idx + 1] = clamped
        else:
            muestras[i] = clamped

    return muestras.tobytes(), freq, canales


def crear_campana(frecuencia, duracion=0.22, volumen=0.18, barrido=0.0):
    pcm_bytes, _, _ = generar_campana_liturgica(frecuencia, duracion, volumen, barrido)
    return pygame.mixer.Sound(buffer=pcm_bytes)


# --- Síntesis de Impacto de Pala/Guadaña Multicapa --- #
def generar_impacto_pala(duracion=0.18, volumen=0.26, freq_res=115, freq=None, canales=None):
    """Síntesis de impacto de pala/guadaña multicapa:
    - Capa A: Transitorio inicial de impacto metálico (ruido blanco modelado decaimiento ~30 ms).
    - Capa B: Resonancia de cuerpo de acero (onda triangular a ~115 Hz con pitch bend descendente).
    """
    if freq is None or canales is None:
        f_actual, c_actual = obtener_init_audio()
        freq = freq or f_actual
        canales = canales or c_actual

    cantidad = int(freq * duracion)
    muestras = array.array("h", [0]) * (cantidad * canales)
    inv_cant = 1.0 / max(1, cantidad - 1)
    tau = math.tau
    fase = 0.0
    muestras_trans = int(freq * 0.032)

    for i in range(cantidad):
        prog = i * inv_cant

        # Capa A: Transitorio de impacto metálico con decaimiento ultra-rápido
        if i < muestras_trans:
            prog_a = i / muestras_trans
            env_a = (1.0 - prog_a) ** 1.8
            capa_a = random.uniform(-1.0, 1.0) * env_a * 0.68
        else:
            capa_a = 0.0

        # Capa B: Resonancia de cuerpo de acero (onda triangular con pitch bend descendente)
        f_act = freq_res * (1.0 - 0.40 * prog)
        fase += tau * f_act / freq
        tri = 2.0 * abs(2.0 * ((fase / tau) % 1.0) - 1.0) - 1.0

        atq_b = min(1.0, i / max(1, int(freq * 0.005)))
        env_b = atq_b * (max(0.0, 1.0 - prog) ** 2.2)
        capa_b = tri * env_b * 0.62

        muestra_float = (capa_a + capa_b) * volumen
        valor = int(32767 * muestra_float)
        clamped = max(-32768, min(32767, valor))

        if canales == 2:
            idx = i * 2
            muestras[idx] = clamped
            muestras[idx + 1] = clamped
        else:
            muestras[i] = clamped

    return muestras.tobytes(), freq, canales


def crear_impacto_pala(duracion=0.18, volumen=0.26, freq_res=115):
    pcm_bytes, _, _ = generar_impacto_pala(duracion, volumen, freq_res)
    return pygame.mixer.Sound(buffer=pcm_bytes)


# --- Síntesis de Tajo / Blandir Pala en el Aire --- #
def generar_ataque_pala(duracion=0.11, volumen=0.18, freq_res=280, freq=None, canales=None):
    """Síntesis de corte o blandir la pala/guadaña en el aire:
    - Capa A: Fricción de aire (ruido filtrado ~45 ms).
    - Capa B: Filo cortante (onda sierra rápida que corta el aire).
    """
    if freq is None or canales is None:
        f_actual, c_actual = obtener_init_audio()
        freq = freq or f_actual
        canales = canales or c_actual

    cantidad = int(freq * duracion)
    muestras = array.array("h", [0]) * (cantidad * canales)
    inv_cant = 1.0 / max(1, cantidad - 1)
    tau = math.tau
    fase = 0.0
    muestras_ruido = int(freq * 0.045)

    for i in range(cantidad):
        prog = i * inv_cant

        if i < muestras_ruido:
            env_a = math.sin(math.pi * (i / muestras_ruido))
            capa_a = random.uniform(-1.0, 1.0) * env_a * 0.40
        else:
            capa_a = 0.0

        f_act = freq_res + 300.0 * math.sin(math.pi * prog)
        fase += tau * f_act / freq
        saw = 2.0 * ((fase / tau) % 1.0) - 1.0
        env_b = math.sin(math.pi * prog)
        capa_b = saw * env_b * 0.60

        muestra_float = (capa_a + capa_b) * volumen
        valor = int(32767 * muestra_float)
        clamped = max(-32768, min(32767, valor))

        if canales == 2:
            idx = i * 2
            muestras[idx] = clamped
            muestras[idx + 1] = clamped
        else:
            muestras[i] = clamped

    return muestras.tobytes(), freq, canales


def crear_ataque_pala(duracion=0.11, volumen=0.18, freq_res=280):
    pcm_bytes, _, _ = generar_ataque_pala(duracion, volumen, freq_res)
    return pygame.mixer.Sound(buffer=pcm_bytes)


# --- Síntesis de Pisotón Aéreo (Stomp) --- #
def generar_stomp(duracion=0.18, volumen=0.25, freq_inicio=140, freq=None, canales=None):
    """Síntesis de pisotón aéreo: crujido de impacto percusivo óseo y sub-grave profundo."""
    if freq is None or canales is None:
        f_actual, c_actual = obtener_init_audio()
        freq = freq or f_actual
        canales = canales or c_actual

    cantidad = int(freq * duracion)
    muestras = array.array("h", [0]) * (cantidad * canales)
    inv_cant = 1.0 / max(1, cantidad - 1)
    tau = math.tau
    fase = 0.0
    muestras_trans = int(freq * 0.028)

    for i in range(cantidad):
        prog = i * inv_cant

        if i < muestras_trans:
            prog_a = i / muestras_trans
            capa_a = random.uniform(-1.0, 1.0) * ((1.0 - prog_a) ** 2) * 0.65
        else:
            capa_a = 0.0

        f_act = freq_inicio * (1.0 - 0.65 * prog)
        fase += tau * f_act / freq
        sub = math.sin(fase)
        env_b = max(0.0, 1.0 - prog) ** 2.0
        capa_b = sub * env_b * 0.65

        muestra_float = (capa_a + capa_b) * volumen
        valor = int(32767 * muestra_float)
        clamped = max(-32768, min(32767, valor))

        if canales == 2:
            idx = i * 2
            muestras[idx] = clamped
            muestras[idx + 1] = clamped
        else:
            muestras[i] = clamped

    return muestras.tobytes(), freq, canales


def crear_stomp(duracion=0.18, volumen=0.25, freq_inicio=140):
    pcm_bytes, _, _ = generar_stomp(duracion, volumen, freq_inicio)
    return pygame.mixer.Sound(buffer=pcm_bytes)


# --- Síntesis de Fanfarria Armónica para Vida Extra --- #
def generar_fanfarria_vida(duracion=0.55, volumen=0.22, freq=None, canales=None):
    """Fanfarria armónica litúrgica arpegiada para vida extra (consagración de 10 almas).
    Tríada mayor eclesiástica arpegiada (C5 -> E5 -> G5 -> C6) con campanas tubulares
    y resonancia armónica celestial.
    """
    if freq is None or canales is None:
        f_actual, c_actual = obtener_init_audio()
        freq = freq or f_actual
        canales = canales or c_actual

    cantidad = int(freq * duracion)
    buffer_acc = [0.0] * cantidad
    tau = math.tau

    notas = [
        (0.00, 523.25, 0.24),
        (0.08, 659.25, 0.24),
        (0.16, 783.99, 0.26),
        (0.24, 1046.50, 0.35),
    ]

    for t_inicio, f_nota, dur_nota in notas:
        idx_ini = int(t_inicio * freq)
        cant_nota = int(dur_nota * freq)
        idx_fin = min(cantidad, idx_ini + cant_nota)
        fase = 0.0
        d_fase = tau * f_nota / freq
        inv_cant = 1.0 / max(1, cant_nota - 1)

        for k in range(idx_fin - idx_ini):
            prog = k * inv_cant
            fase += d_fase
            atq = min(1.0, prog / 0.025)
            env_fund = atq * (max(0.0, 1.0 - prog) ** 1.8)
            env_arm = atq * (max(0.0, 1.0 - prog) ** 2.8)
            onda = (
                math.sin(fase) * env_fund
                + 0.35 * math.sin(fase * 2.0) * env_arm
                + 0.15 * math.sin(fase * 3.0) * env_arm
            )
            buffer_acc[idx_ini + k] += onda * 0.30

    muestras = array.array("h", [0]) * (cantidad * canales)
    for i in range(cantidad):
        valor = int(32767 * volumen * buffer_acc[i])
        clamped = max(-32768, min(32767, valor))
        if canales == 2:
            idx = i * 2
            muestras[idx] = clamped
            muestras[idx + 1] = clamped
        else:
            muestras[i] = clamped

    return muestras.tobytes(), freq, canales


def crear_fanfarria_vida(duracion=0.55, volumen=0.22):
    pcm_bytes, _, _ = generar_fanfarria_vida(duracion, volumen)
    return pygame.mixer.Sound(buffer=pcm_bytes)


# --- Clase Audio --- #
class Audio:
    """Administrador de sonido procedural de IN CRYPTA.
    Todos los efectos son sintetizados 100% en memoria mediante PCM int16.
    Incluye variaciones micro-tonales aleatorias (+- 2.5%) para evitar la fatiga acústica.
    """

    def __init__(self):
        self.activo = False
        self.sonidos = {}
        self.variaciones = {}
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(
                    frequency=FRECUENCIA_MUESTREO,
                    size=-16,
                    channels=CANALES,
                    buffer=512,
                )
            # Expandir a 16 canales simultáneos para evitar corte de sonidos
            try:
                pygame.mixer.set_num_channels(16)
            except Exception:
                pass

            # 1. Banco canónico de sonidos
            self.sonidos = {
                # Acciones del jugador
                "salto": crear_tono(230, 0.14, 0.18, "seno", 140),
                "dash": crear_tono(150, 0.18, 0.16, "sierra", 380),
                "ataque": crear_ataque_pala(0.11, 0.18, 280),
                "pala": crear_impacto_pala(0.18, 0.26, 115),
                "stomp": crear_stomp(0.18, 0.25, 140),
                "paso": crear_tono(95, 0.05, 0.08, "ruido", -30),
                # Coleccionables litúrgicos (Campanas enriquecidas en escala pentatónica C)
                "alma": crear_campana(659, 0.22, 0.18, 120),
                "alma_1": crear_campana(523, 0.20, 0.18, 80),
                "alma_2": crear_campana(587, 0.20, 0.18, 90),
                "alma_3": crear_campana(659, 0.21, 0.18, 100),
                "alma_4": crear_campana(784, 0.22, 0.18, 110),
                "alma_5": crear_campana(880, 0.23, 0.18, 120),
                "alma_6": crear_campana(1046, 0.25, 0.19, 140),
                "pala_recoger": crear_campana(620, 0.22, 0.18, 180),
                "vida_extra": crear_fanfarria_vida(0.55, 0.22),
                # Jefe y combate
                "onda": crear_tono(70, 0.42, 0.24, "ruido", 90),
                "jefe_aviso": crear_tono(190, 0.28, 0.15, "cuadrada", -55),
                "jefe_fase": crear_tono(110, 0.55, 0.22, "cuadrada", -35),
                # UI y eventos de estado
                "ui": crear_tono(420, 0.06, 0.10, "cuadrada", -40),
                "daño": crear_tono(160, 0.26, 0.22, "cuadrada", -90),
                "muerte": crear_tono(75, 0.65, 0.26, "cuadrada", -40),
                "meta": crear_campana(440, 0.50, 0.22, 220),
            }

            # 2. Variaciones micro-tonales (+- 2% a 3%) para acciones repetitivas
            self.variaciones = {
                "salto": [
                    crear_tono(int(230 * (1 + p)), 0.14, 0.18, "seno", 140 * (1 + p))
                    for p in FACTORES_MICROTONALES
                ] + [self.sonidos["salto"]],
                "pala": [
                    crear_impacto_pala(0.18, 0.26, int(115 * (1 + p)))
                    for p in FACTORES_MICROTONALES
                ] + [self.sonidos["pala"]],
                "ataque": [
                    crear_ataque_pala(0.11, 0.18, int(280 * (1 + p)))
                    for p in FACTORES_MICROTONALES
                ] + [self.sonidos["ataque"]],
                "stomp": [
                    crear_stomp(0.18, 0.25, int(140 * (1 + p)))
                    for p in FACTORES_MICROTONALES
                ] + [self.sonidos["stomp"]],
                "dash": [
                    crear_tono(int(150 * (1 + p)), 0.18, 0.16, "sierra", 380 * (1 + p))
                    for p in FACTORES_MICROTONALES
                ] + [self.sonidos["dash"]],
                "paso": [
                    crear_tono(int(95 * (1 + p)), 0.05, 0.08, "ruido", -30 * (1 + p))
                    for p in FACTORES_MICROTONALES
                ] + [self.sonidos["paso"]],
            }

            self.activo = True
        except pygame.error:
            self.activo = False

    # --- Función reproducir --- #
    def reproducir(self, nombre):
        """Reproduce un efecto de sonido. Si el efecto cuenta con variaciones micro-tonales,
        selecciona aleatoriamente una de ellas para prevenir la fatiga auditiva del jugador.
        """
        if not self.activo:
            return
        variantes = self.variaciones.get(nombre)
        if variantes:
            sonido = random.choice(variantes)
        else:
            sonido = self.sonidos.get(nombre)
        if sonido is not None:
            sonido.play()

    # --- Función alternar --- #
    def alternar(self):
        """Activa o desactiva la reproducción global de audio."""
        self.activo = not self.activo
