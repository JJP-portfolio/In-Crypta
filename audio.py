# ============================================================
# audio.py — Sintetizador de audio procedural gótico de IN CRYPTA
# ============================================================
# 100% procedural en Python nativo con array (y aceleración opcional NumPy).
# 44100 Hz, 16 bits, estéreo intercalado.
# Arquitectura ADSR con mezcla multicapa (ruido, senos, sierras, FM).
# Variación tonal (pitch detune ±4%), pulso cardíaco del corazón delator a 55 Hz
# y dron ambiental fúnebre para catacumbas.
# ============================================================

import array
import math
import random

import pygame

FRECUENCIA_MUESTREO = 44100


# --- Generador de sonido multicapa ADSR --- #
def sintetizar_sfx(
    duracion,
    capas,
    adsr=(0.01, 0.05, 0.7, 0.05),
    volumen=0.25,
    detune=1.0,
    pan=0.0,
):
    """Genera un buffer estéreo de 16 bits firmado intercalado a 44100 Hz.

    capas: lista de tuplas (tipo, f0, barrido, peso, extra)
      - tipo: 'seno', 'sierra', 'cuadrada', 'ruido', 'fm'
      - f0: frecuencia base en Hz
      - barrido: cambio total de frecuencia en la duración
      - peso: amplitud relativa (0.0 a 1.0)
      - extra: tupla (mod_frec, mod_indice) para 'fm' o None
    """
    total = max(1, int(FRECUENCIA_MUESTREO * duracion))
    atq, dec, sus, rel = adsr
    n_atq = int(atq * FRECUENCIA_MUESTREO)
    n_dec = int(dec * FRECUENCIA_MUESTREO)
    n_rel = int(rel * FRECUENCIA_MUESTREO)
    n_sus = max(0, total - n_atq - n_dec - n_rel)

    muestras = array.array("h")
    tau = math.tau

    # Panning estéreo (-1.0 izq, 0.0 centro, 1.0 der)
    vol_l = volumen * math.cos((pan + 1.0) * math.pi / 4.0)
    vol_r = volumen * math.sin((pan + 1.0) * math.pi / 4.0)

    # Estado de fase por capa
    fases = [0.0] * len(capas)

    for i in range(total):
        # Envolvente ADSR
        if i < n_atq:
            env = i / max(1, n_atq)
        elif i < n_atq + n_dec:
            env = 1.0 - (1.0 - sus) * ((i - n_atq) / max(1, n_dec))
        elif i < n_atq + n_dec + n_sus:
            env = sus
        else:
            prog_rel = (i - n_atq - n_dec - n_sus) / max(1, n_rel)
            env = sus * max(0.0, 1.0 - prog_rel)

        progreso = i / total
        muestra_mono = 0.0

        for c_idx, (tipo, f0, barrido, peso, extra) in enumerate(capas):
            f_actual = (f0 + barrido * progreso) * detune
            delta_fase = tau * f_actual / FRECUENCIA_MUESTREO
            fases[c_idx] = (fases[c_idx] + delta_fase) % tau
            fase = fases[c_idx]

            if tipo == "seno":
                v = math.sin(fase)
            elif tipo == "ruido":
                v = random.uniform(-1.0, 1.0)
            elif tipo == "fm":
                mod_frec, mod_idx = extra if extra else (f_actual * 2, 1.5)
                fase_mod = (tau * (mod_frec * detune) * (i / FRECUENCIA_MUESTREO)) % tau
                v = math.sin(fase + mod_idx * math.sin(fase_mod))
            elif tipo == "sierra":
                v = 2.0 * ((fase / tau) % 1.0) - 1.0
            elif tipo == "cuadrada":
                v = 1.0 if math.sin(fase) >= 0.0 else -1.0
            else:
                v = math.sin(fase)

            muestra_mono += v * peso

        val_l = int(max(-32767, min(32767, muestra_mono * env * vol_l * 32767)))
        val_r = int(max(-32767, min(32767, muestra_mono * env * vol_r * 32767)))
        muestras.append(val_l)
        muestras.append(val_r)

    return pygame.mixer.Sound(buffer=muestras.tobytes())


# --- Sintetizador de doble latido cardíaco (55 Hz - Tell-Tale Heart) --- #
def sintetizar_corazon_delator(volumen=0.32):
    """Genera el latido sordo a 55 Hz de El Corazón Delator ('lub-dub')."""
    duracion = 0.42
    total = int(FRECUENCIA_MUESTREO * duracion)
    muestras = array.array("h")
    tau = math.tau

    # Dos impactos: primer golpe (lub) en t=0.0s a 55Hz, segundo golpe (dub) en t=0.14s a 48Hz
    t_golpe1 = 0.0
    t_golpe2 = 0.13

    for i in range(total):
        t = i / FRECUENCIA_MUESTREO
        val = 0.0

        # Pulso 1
        dt1 = t - t_golpe1
        if 0.0 <= dt1 < 0.12:
            env1 = math.exp(-dt1 * 28.0) * math.sin(min(1.0, dt1 * 60.0) * math.pi / 2.0)
            val += env1 * math.sin(tau * 55.0 * dt1)

        # Pulso 2 (más suave)
        dt2 = t - t_golpe2
        if 0.0 <= dt2 < 0.14:
            env2 = 0.75 * math.exp(-dt2 * 32.0) * math.sin(min(1.0, dt2 * 60.0) * math.pi / 2.0)
            val += env2 * math.sin(tau * 48.0 * dt2)

        # Transitorio de sub-bajos sordo
        muestra_int = int(max(-32767, min(32767, val * volumen * 32767)))
        muestras.append(muestra_int)
        muestras.append(muestra_int)

    return pygame.mixer.Sound(buffer=muestras.tobytes())


# --- Sintetizador de Dron Fúnebre Catacumbal (bucle continuo) --- #
def sintetizar_dron_funebre(duracion=4.0, volumen=0.10):
    """Genera un dron ambiental subterráneo con acordes en 55Hz/110Hz/165Hz con batimento estéreo."""
    total = int(FRECUENCIA_MUESTREO * duracion)
    muestras = array.array("h")
    tau = math.tau

    for i in range(total):
        t = i / FRECUENCIA_MUESTREO
        # LFO lento para batimento orgánico
        lfo = 0.5 + 0.5 * math.sin(tau * 0.25 * t)
        lfo2 = 0.5 + 0.5 * math.cos(tau * 0.18 * t)

        # Fundamental + octava + quinta mística
        f1 = math.sin(tau * 55.0 * t)
        f2 = 0.45 * math.sin(tau * 110.0 * t + 0.4)
        f3 = 0.25 * math.sin(tau * 164.8 * t + 0.8)  # Mi menor tenue
        f4 = 0.15 * math.sin(tau * 220.0 * t)

        # Batimento con leve desfase estéreo
        s_left = (f1 + f2 * (0.8 + 0.2 * lfo) + f3 + f4) * volumen
        s_right = (f1 + f2 * (0.8 + 0.2 * lfo2) + f3 * 1.1 + f4 * 0.9) * volumen

        # Suavizar esquinas de bucle para evitar clicks
        edge_env = min(1.0, min(i, total - i) / (FRECUENCIA_MUESTREO * 0.1))

        val_l = int(max(-32767, min(32767, s_left * edge_env * 32767)))
        val_r = int(max(-32767, min(32767, s_right * edge_env * 32767)))
        muestras.append(val_l)
        muestras.append(val_r)

    return pygame.mixer.Sound(buffer=muestras.tobytes())


# --- Clase Audio --- #
class Audio:
    def __init__(self):
        self.activo = False
        self.sonidos = {}
        self.variaciones = {}
        self.canal_dron = None
        self.sonido_dron = None
        self.sonido_latido = None
        self.tiempo_ultimo_latido = 0.0

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(
                    frequency=FRECUENCIA_MUESTREO,
                    size=-16,
                    channels=2,
                    buffer=512,
                )
            self._construir_banco()
            self.activo = True
        except pygame.error:
            self.activo = False

    def _construir_banco(self):
        # 1. Salto: swoop ascendente + roce de abrigo
        capas_salto = [
            ("seno", 210, 160, 0.7, None),
            ("ruido", 0, 0, 0.2, None),
            ("fm", 320, 80, 0.2, (640, 0.6)),
        ]
        self.sonidos["salto"] = sintetizar_sfx(0.14, capas_salto, adsr=(0.01, 0.04, 0.5, 0.09), volumen=0.18)
        self.variaciones["salto"] = [
            sintetizar_sfx(0.14, capas_salto, adsr=(0.01, 0.04, 0.5, 0.09), volumen=0.18, detune=0.96),
            self.sonidos["salto"],
            sintetizar_sfx(0.14, capas_salto, adsr=(0.01, 0.04, 0.5, 0.09), volumen=0.18, detune=1.04),
        ]

        # 2. Dash de sombras: torbellino espectral
        capas_dash = [
            ("ruido", 0, 0, 0.45, None),
            ("sierra", 140, 320, 0.4, None),
            ("seno", 90, 180, 0.35, None),
        ]
        self.sonidos["dash"] = sintetizar_sfx(0.18, capas_dash, adsr=(0.02, 0.06, 0.4, 0.10), volumen=0.18)
        self.variaciones["dash"] = [
            sintetizar_sfx(0.18, capas_dash, adsr=(0.02, 0.06, 0.4, 0.10), volumen=0.18, detune=0.96),
            self.sonidos["dash"],
            sintetizar_sfx(0.18, capas_dash, adsr=(0.02, 0.06, 0.4, 0.10), volumen=0.18, detune=1.04),
        ]

        # 3. Ataque sablazo de pala / guadaña
        capas_ataque = [
            ("fm", 280, 480, 0.65, (560, 1.2)),
            ("ruido", 0, 0, 0.35, None),
        ]
        self.sonidos["ataque"] = sintetizar_sfx(0.11, capas_ataque, adsr=(0.005, 0.03, 0.4, 0.075), volumen=0.18)
        self.variaciones["ataque"] = [
            sintetizar_sfx(0.11, capas_ataque, adsr=(0.005, 0.03, 0.4, 0.075), volumen=0.18, detune=0.96),
            self.sonidos["ataque"],
            sintetizar_sfx(0.11, capas_ataque, adsr=(0.005, 0.03, 0.4, 0.075), volumen=0.18, detune=1.04),
        ]

        # 4. Golpe con la pala de hierro (impacto seco de tumba)
        capas_pala = [
            ("ruido", 0, 0, 0.45, None),
            ("seno", 115, -60, 0.5, None),
            ("fm", 440, -180, 0.35, (880, 1.8)),
        ]
        self.sonidos["pala"] = sintetizar_sfx(0.20, capas_pala, adsr=(0.005, 0.05, 0.3, 0.145), volumen=0.26)
        self.variaciones["pala"] = [
            sintetizar_sfx(0.20, capas_pala, adsr=(0.005, 0.05, 0.3, 0.145), volumen=0.26, detune=0.96),
            self.sonidos["pala"],
            sintetizar_sfx(0.20, capas_pala, adsr=(0.005, 0.05, 0.3, 0.145), volumen=0.26, detune=1.04),
        ]

        # 5. Pisotón aéreo (stomp): impacto óseo con quiebre
        capas_stomp = [
            ("ruido", 0, 0, 0.5, None),
            ("seno", 85, -45, 0.6, None),
            ("cuadrada", 55, -20, 0.25, None),
        ]
        self.sonidos["stomp"] = sintetizar_sfx(0.18, capas_stomp, adsr=(0.005, 0.04, 0.4, 0.135), volumen=0.26)
        self.variaciones["stomp"] = [
            sintetizar_sfx(0.18, capas_stomp, adsr=(0.005, 0.04, 0.4, 0.135), volumen=0.26, detune=0.96),
            self.sonidos["stomp"],
            sintetizar_sfx(0.18, capas_stomp, adsr=(0.005, 0.04, 0.4, 0.135), volumen=0.26, detune=1.04),
        ]

        # 6. Almas espectrales y escala pentatónica de ánimas
        notas_almas = [523, 587, 659, 784, 880, 1046]
        for idx, nota in enumerate(notas_almas, 1):
            capas_a = [
                ("seno", nota, 120, 0.7, None),
                ("fm", nota * 2, 80, 0.3, (nota * 3, 0.8)),
            ]
            snd_alma = sintetizar_sfx(0.22, capas_a, adsr=(0.01, 0.06, 0.6, 0.15), volumen=0.16)
            self.sonidos[f"alma_{idx}"] = snd_alma

        self.sonidos["alma"] = self.sonidos["alma_3"]
        self.variaciones["alma"] = [
            self.sonidos["alma_1"],
            self.sonidos["alma_2"],
            self.sonidos["alma_3"],
            self.sonidos["alma_4"],
        ]

        # 7. Onda del Custodio: retumbar de osario
        capas_onda = [
            ("ruido", 0, 0, 0.5, None),
            ("seno", 65, 50, 0.55, None),
            ("sierra", 85, 40, 0.25, None),
        ]
        self.sonidos["onda"] = sintetizar_sfx(0.40, capas_onda, adsr=(0.02, 0.10, 0.6, 0.28), volumen=0.22)

        # 8. Telegrafía y cambio de fase del Custodio
        capas_aviso = [
            ("cuadrada", 180, -50, 0.6, None),
            ("fm", 360, -100, 0.4, (180, 1.4)),
        ]
        self.sonidos["jefe_aviso"] = sintetizar_sfx(0.28, capas_aviso, adsr=(0.02, 0.08, 0.5, 0.18), volumen=0.18)

        capas_fase = [
            ("cuadrada", 110, -35, 0.6, None),
            ("seno", 55, 30, 0.5, None),
            ("ruido", 0, 0, 0.3, None),
        ]
        self.sonidos["jefe_fase"] = sintetizar_sfx(0.55, capas_fase, adsr=(0.04, 0.15, 0.6, 0.36), volumen=0.25)

        # 9. Recolección de Pala / Dash / Vida extra
        capas_pala_recoger = [
            ("fm", 540, 260, 0.7, (1080, 1.2)),
            ("seno", 720, 220, 0.4, None),
        ]
        self.sonidos["pala_recoger"] = sintetizar_sfx(0.25, capas_pala_recoger, adsr=(0.01, 0.08, 0.6, 0.16), volumen=0.18)

        capas_dash_recoger = [
            ("seno", 340, 380, 0.65, None),
            ("fm", 680, 420, 0.35, (1360, 1.1)),
        ]
        self.sonidos["dash_recoger"] = sintetizar_sfx(0.28, capas_dash_recoger, adsr=(0.01, 0.08, 0.6, 0.19), volumen=0.18)

        capas_checkpoint = [
            ("seno", 520, 260, 0.6, None),
            ("fm", 1040, 180, 0.3, (1560, 0.8)),
        ]
        self.sonidos["checkpoint"] = sintetizar_sfx(0.32, capas_checkpoint, adsr=(0.01, 0.08, 0.6, 0.23), volumen=0.18)

        capas_vida_extra = [
            ("seno", 680, 480, 0.6, None),
            ("seno", 850, 420, 0.3, None),
            ("fm", 1360, 240, 0.25, (2040, 0.6)),
        ]
        self.sonidos["vida_extra"] = sintetizar_sfx(0.44, capas_vida_extra, adsr=(0.02, 0.12, 0.6, 0.30), volumen=0.20)

        # 10. UI y Feedback
        capas_ui = [
            ("cuadrada", 420, -60, 0.6, None),
            ("seno", 840, -120, 0.4, None),
        ]
        self.sonidos["ui"] = sintetizar_sfx(0.06, capas_ui, adsr=(0.005, 0.02, 0.3, 0.035), volumen=0.10)

        # 11. Daño y Muerte
        capas_dano = [
            ("cuadrada", 160, -90, 0.65, None),
            ("ruido", 0, 0, 0.45, None),
        ]
        self.sonidos["daño"] = sintetizar_sfx(0.26, capas_dano, adsr=(0.005, 0.06, 0.4, 0.195), volumen=0.24)

        capas_muerte = [
            ("cuadrada", 75, -40, 0.7, None),
            ("seno", 55, -25, 0.5, None),
            ("ruido", 0, 0, 0.35, None),
        ]
        self.sonidos["muerte"] = sintetizar_sfx(0.65, capas_muerte, adsr=(0.03, 0.18, 0.6, 0.44), volumen=0.28)

        # 12. Meta y Victoria
        capas_meta = [
            ("seno", 220, 280, 0.6, None),
            ("fm", 440, 360, 0.35, (880, 1.0)),
        ]
        self.sonidos["meta"] = sintetizar_sfx(0.55, capas_meta, adsr=(0.02, 0.14, 0.6, 0.39), volumen=0.20)

        # 13. Rebote metálico sordo (inmunidad a pala del Custodio en Fase 2)
        capas_rebote = [
            ("fm", 880, -320, 0.6, (1420, 2.5)),
            ("ruido", 0, 0, 0.3, None),
            ("seno", 220, -90, 0.4, None),
        ]
        self.sonidos["rebote_pala"] = sintetizar_sfx(0.16, capas_rebote, adsr=(0.004, 0.04, 0.3, 0.116), volumen=0.24)
        self.sonidos["rebote_metalico"] = self.sonidos["rebote_pala"]

        # 14. Corazón delator a 55 Hz
        self.sonido_latido = sintetizar_corazon_delator(volumen=0.34)
        self.sonidos["corazon_latido"] = self.sonido_latido

        # 15. Dron fúnebre ambiental
        self.sonido_dron = sintetizar_dron_funebre(duracion=4.0, volumen=0.08)
        self.sonidos["dron_catacumbas"] = self.sonido_dron

    # --- Función reproducir --- #
    def reproducir(self, nombre):
        if not self.activo:
            return
        # Variación de pitch ±4% para mitigar fatiga auditiva
        if nombre in self.variaciones:
            variantes = self.variaciones[nombre]
            sonido = random.choice(variantes)
            sonido.play()
            return

        sonido = self.sonidos.get(nombre)
        if sonido is not None:
            sonido.play()

    # --- Función latido_corazon --- #
    def latido_corazon(self):
        """Reproduce el pulso a 55 Hz del corazón delator."""
        if not self.activo:
            return
        if self.sonido_latido:
            self.sonido_latido.play()

    # --- Función iniciar_dron / detener_dron --- #
    def iniciar_dron(self):
        """Inicia el dron fúnebre ambiental en bucle de fondo."""
        if not self.activo or not self.sonido_dron:
            return
        try:
            if self.canal_dron is None:
                self.canal_dron = pygame.mixer.Channel(7)
            if not self.canal_dron.get_busy():
                self.canal_dron.play(self.sonido_dron, loops=-1)
        except pygame.error:
            pass

    def detener_dron(self):
        """Detiene el dron ambiental fúnebre."""
        if self.canal_dron and self.canal_dron.get_busy():
            self.canal_dron.stop()

    # --- Función alternar --- #
    def alternar(self):
        self.activo = not self.activo
        if not self.activo:
            self.detener_dron()
