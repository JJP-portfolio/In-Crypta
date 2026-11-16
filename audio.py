#---- Importamos librerias ----#
import array
import math
from pathlib import Path
import random
import pygame

# Frecuencia de muestreo estandar
FRECUENCIA_MUESTREO = 44100


#---- Sintesis de efectos de sonido con ADSR ----#
def _valor_envolvente_adsr(i, n_atq, n_dec, n_sus, n_rel, sus):
    if i < n_atq:
        return i / max(1, n_atq)
    if i < n_atq + n_dec:
        return 1.0 - (1.0 - sus) * ((i - n_atq) / max(1, n_dec))
    if i < n_atq + n_dec + n_sus:
        return sus
    prog_rel = (i - n_atq - n_dec - n_sus) / max(1, n_rel)
    return sus * max(0.0, 1.0 - prog_rel)


def _valor_oscilador(tipo, fase, indice_muestra, f_actual, detune):
    if tipo == "ruido":
        return random.uniform(-1.0, 1.0)
    if tipo == "fm":
        return math.sin(fase)
    if tipo == "sierra":
        return 2.0 * ((fase / math.tau) % 1.0) - 1.0
    if tipo == "cuadrada":
        return 1.0 if math.sin(fase) >= 0.0 else -1.0
    return math.sin(fase)


def sintetizar_sfx(
    duracion,
    capas,
    adsr=(0.01, 0.05, 0.7, 0.05),
    volumen=0.25,
    detune=1.0,
    pan=0.0,
):
    """Genera un buffer de audio estereo de 16 bits con envolvente ADSR."""
    total = max(1, int(FRECUENCIA_MUESTREO * duracion))
    atq, dec, sus, rel = adsr
    n_atq = int(atq * FRECUENCIA_MUESTREO)
    n_dec = int(dec * FRECUENCIA_MUESTREO)
    n_rel = int(rel * FRECUENCIA_MUESTREO)
    n_sus = max(0, total - n_atq - n_dec - n_rel)

    muestras = array.array("h")
    tau = math.tau
    vol_l = volumen * math.cos((pan + 1.0) * math.pi / 4.0)
    vol_r = volumen * math.sin((pan + 1.0) * math.pi / 4.0)
    fases = [0.0] * len(capas)

    for i in range(total):
        env = _valor_envolvente_adsr(i, n_atq, n_dec, n_sus, n_rel, sus)
        progreso = i / total
        muestra_mono = 0.0
        for c_idx, (tipo, f0, barrido, peso, extra) in enumerate(capas):
            f_actual = (f0 + barrido * progreso) * detune
            fases[c_idx] = (fases[c_idx] + tau * f_actual / FRECUENCIA_MUESTREO) % tau
            fase = fases[c_idx]
            if tipo == "fm":
                mod_frec, mod_idx = extra if extra else (f_actual * 2, 1.5)
                fase_mod = (tau * (mod_frec * detune) * (i / FRECUENCIA_MUESTREO)) % tau
                v = math.sin(fase + mod_idx * math.sin(fase_mod))
            else:
                v = _valor_oscilador(tipo, fase, i, f_actual, detune)
            muestra_mono += v * peso

        muestras.append(int(max(-32767, min(32767, muestra_mono * env * vol_l * 32767))))
        muestras.append(int(max(-32767, min(32767, muestra_mono * env * vol_r * 32767))))

    return pygame.mixer.Sound(buffer=muestras.tobytes())


#---- Latido de corazon procedural ----#
def sintetizar_corazon_delator(volumen=0.32):
    # Genera el doble pulso sordo del corazon
    duracion = 0.42
    total = int(FRECUENCIA_MUESTREO * duracion)
    muestras = array.array("h")
    tau = math.tau

    t_golpe1 = 0.0
    t_golpe2 = 0.13

    for i in range(total):
        t = i / FRECUENCIA_MUESTREO
        val = 0.0

        dt1 = t - t_golpe1
        if 0.0 <= dt1 < 0.12:
            env1 = math.exp(-dt1 * 28.0) * math.sin(min(1.0, dt1 * 60.0) * math.pi / 2.0)
            val += env1 * math.sin(tau * 55.0 * dt1)

        dt2 = t - t_golpe2
        if 0.0 <= dt2 < 0.14:
            env2 = 0.75 * math.exp(-dt2 * 32.0) * math.sin(min(1.0, dt2 * 60.0) * math.pi / 2.0)
            val += env2 * math.sin(tau * 48.0 * dt2)

        muestra_int = int(max(-32767, min(32767, val * volumen * 32767)))
        muestras.append(muestra_int)
        muestras.append(muestra_int)

    return pygame.mixer.Sound(buffer=muestras.tobytes())


#---- Dron ambiental de fondo ----#
def sintetizar_dron_funebre(duracion=4.0, volumen=0.025):
    """Genera una brisa nocturna filtrada sin subgraves para no cargar la mezcla musical."""
    total = int(FRECUENCIA_MUESTREO * duracion)
    muestras = array.array("h")
    tau = math.tau

    for i in range(total):
        t = i / FRECUENCIA_MUESTREO
        lfo = 0.55 + 0.45 * math.sin(tau * 0.25 * t)
        lfo2 = 0.55 + 0.45 * math.cos(tau * 0.25 * t)

        # Armónicos aireados en registro medio-alto (>= 293 Hz, sin subgraves < 160 Hz)
        f1 = math.sin(tau * 293.66 * t) * 0.45
        f2 = math.sin(tau * 440.0 * t + 0.6) * 0.35
        f3 = math.sin(tau * 659.25 * t + 1.1) * 0.20

        s_left = (f1 * lfo + f2 + f3 * lfo2) * volumen
        s_right = (f1 * lfo2 + f2 * 0.9 + f3 * lfo) * volumen

        edge_env = min(1.0, min(i, total - i) / (FRECUENCIA_MUESTREO * 0.12))

        val_l = int(max(-32767, min(32767, s_left * edge_env * 32767)))
        val_r = int(max(-32767, min(32767, s_right * edge_env * 32767)))
        muestras.append(val_l)
        muestras.append(val_r)

    return pygame.mixer.Sound(buffer=muestras.tobytes())


#---- Tabla de sintesis de efectos de sonido ----#
_PRESETS_SFX = {
    "salto": (
        0.14,
        [("seno", 210, 160, 0.7, None), ("ruido", 0, 0, 0.2, None), ("fm", 320, 80, 0.2, (640, 0.6))],
        (0.01, 0.04, 0.5, 0.09),
        0.26,
    ),
    "dash": (
        0.18,
        [("ruido", 0, 0, 0.45, None), ("sierra", 140, 320, 0.4, None), ("seno", 90, 180, 0.35, None)],
        (0.02, 0.06, 0.4, 0.10),
        0.36,
    ),
    "ataque": (
        0.11,
        [("fm", 280, 480, 0.65, (560, 1.2)), ("ruido", 0, 0, 0.35, None)],
        (0.005, 0.03, 0.4, 0.075),
        0.26,
    ),
    "pala": (
        0.20,
        [("ruido", 0, 0, 0.45, None), ("seno", 115, -60, 0.5, None), ("fm", 440, -180, 0.35, (880, 1.8))],
        (0.005, 0.05, 0.3, 0.145),
        0.26,
    ),
    "rebote_pala": (
        0.16,
        [("fm", 880, -320, 0.6, (1420, 2.5)), ("ruido", 0, 0, 0.3, None), ("seno", 220, -90, 0.4, None)],
        (0.004, 0.04, 0.3, 0.116),
        0.24,
    ),
    "stomp": (
        0.18,
        [("ruido", 0, 0, 0.5, None), ("seno", 85, -45, 0.6, None), ("cuadrada", 55, -20, 0.25, None)],
        (0.005, 0.04, 0.4, 0.135),
        0.26,
    ),
    "onda": (
        0.40,
        [("ruido", 0, 0, 0.5, None), ("seno", 65, 50, 0.55, None), ("sierra", 85, 40, 0.25, None)],
        (0.02, 0.10, 0.6, 0.28),
        0.22,
    ),
    "jefe_aviso": (
        0.28,
        [("cuadrada", 180, -50, 0.6, None), ("fm", 360, -100, 0.4, (180, 1.4))],
        (0.02, 0.08, 0.5, 0.18),
        0.18,
    ),
    "jefe_fase": (
        0.55,
        [("cuadrada", 110, -35, 0.6, None), ("seno", 55, 30, 0.5, None), ("ruido", 0, 0, 0.3, None)],
        (0.04, 0.15, 0.6, 0.36),
        0.25,
    ),
    "pala_recoger": (
        0.25,
        [("fm", 540, 260, 0.7, (1080, 1.2)), ("seno", 720, 220, 0.4, None)],
        (0.01, 0.08, 0.6, 0.16),
        0.18,
    ),
    "dash_recoger": (
        0.28,
        [("seno", 340, 380, 0.65, None), ("fm", 680, 420, 0.35, (1360, 1.1))],
        (0.01, 0.08, 0.6, 0.19),
        0.18,
    ),
    "checkpoint": (
        0.32,
        [("seno", 520, 260, 0.6, None), ("fm", 1040, 180, 0.3, (1560, 0.8))],
        (0.01, 0.08, 0.6, 0.23),
        0.18,
    ),
    "vida_extra": (
        0.44,
        [("seno", 680, 480, 0.6, None), ("seno", 850, 420, 0.3, None), ("fm", 1360, 240, 0.25, (2040, 0.6))],
        (0.02, 0.12, 0.6, 0.30),
        0.20,
    ),
    "ui": (
        0.06,
        [("cuadrada", 420, -60, 0.6, None), ("seno", 840, -120, 0.4, None)],
        (0.005, 0.02, 0.3, 0.035),
        0.10,
    ),
    "daño": (
        0.26,
        [("cuadrada", 160, -90, 0.65, None), ("ruido", 0, 0, 0.45, None)],
        (0.005, 0.06, 0.4, 0.195),
        0.24,
    ),
    "muerte": (
        0.65,
        [("cuadrada", 75, -40, 0.7, None), ("seno", 55, -25, 0.5, None), ("ruido", 0, 0, 0.35, None)],
        (0.03, 0.18, 0.6, 0.44),
        0.28,
    ),
    "meta": (
        0.55,
        [("seno", 220, 280, 0.6, None), ("fm", 440, 360, 0.35, (880, 1.0))],
        (0.02, 0.14, 0.6, 0.39),
        0.20,
    ),
    "losa_romper": (
        0.19,
        [("ruido", 0, 0, 0.65, None), ("cuadrada", 95, -50, 0.45, None), ("seno", 60, -30, 0.4, None)],
        (0.003, 0.04, 0.25, 0.147),
        0.46,
    ),
    "compuerta": (
        0.38,
        [
            ("cuadrada", 92, -38, 0.55, None),
            ("ruido", 0, 0, 0.40, None),
            ("seno", 62, -22, 0.50, None),
            ("fm", 210, -45, 0.35, (380, 1.1)),
        ],
        (0.004, 0.09, 0.30, 0.286),
        0.46,
    ),
    "cripta_romper": (
        0.28,
        [("ruido", 0, 0, 0.72, None), ("cuadrada", 84, -44, 0.55, None), ("seno", 52, -26, 0.50, None)],
        (0.003, 0.06, 0.22, 0.197),
        0.48,
    ),
    "jefe_caida": (
        0.72,
        [("seno", 320, -245, 0.55, None), ("fm", 190, -135, 0.45, (140, 1.4)), ("ruido", 0, 0, 0.35, None)],
        (0.010, 0.14, 0.45, 0.57),
        0.50,
    ),
}

# Realce moderado para efectos en disco con menor sonoridad media respecto a la música (0.45)
_GANANCIA_SFX_DISCO = {
    "ataque": 1.25,
    "checkpoint": 1.50,
    "dash": 1.38,
    "dash_recoger": 1.35,
    "meta": 1.28,
    "pala": 1.45,
    "pala_recoger": 1.35,
    "salto": 1.22,
    "stomp": 1.45,
    "ui": 1.45,
}

_NOTAS_ALMAS = (523.25, 587.33, 659.25, 783.99, 880.00, 1046.50)
_NOTAS_CAMPANAS = (587.33, 698.46, 783.99, 880.00, 1046.50, 1174.66)

_TIERS_FAROL = {
    "farol_tier_1": (
        0.48,
        [
            ("seno", 293.66, 0, 0.45, None),
            ("seno", 349.23, 0, 0.40, None),
            ("seno", 440.00, 0, 0.45, None),
            ("fm", 587.33, 0, 0.25, (1174.66, 0.6)),
        ],
        (0.02, 0.10, 0.6, 0.36),
        0.40,
    ),
    "farol_tier_2": (
        0.58,
        [
            ("seno", 523.25, 0, 0.45, None),
            ("seno", 659.25, 0, 0.40, None),
            ("seno", 783.99, 0, 0.45, None),
            ("fm", 1046.50, 0, 0.35, (2093.0, 0.8)),
        ],
        (0.015, 0.12, 0.65, 0.445),
        0.42,
    ),
    "farol_tier_3": (
        0.72,
        [
            ("seno", 587.33, 0, 0.45, None),
            ("seno", 739.99, 0, 0.40, None),
            ("seno", 880.00, 0, 0.40, None),
            ("fm", 1174.66, 0, 0.35, (2349.32, 1.2)),
            ("seno", 1320.00, -20, 0.25, None),
        ],
        (0.02, 0.15, 0.7, 0.55),
        0.44,
    ),
}


def _escalar_ganancia_sound(sonido, factor):
    """Aplica ganancia moderada en memoria con limitación suave sobre ±0.85."""
    if abs(factor - 1.0) < 1e-3:
        return sonido
    crudo = array.array("h")
    crudo.frombytes(sonido.get_raw())
    inv = factor / 32767.0
    for idx, muestra in enumerate(crudo):
        escalada = muestra * inv
        if escalada > 0.85 or escalada < -0.85:
            escalada = math.tanh(escalada)
        crudo[idx] = int(max(-32767, min(32767, escalada * 32767.0)))
    return pygame.mixer.Sound(buffer=crudo.tobytes())


def _frecuencias_campana(frecuencia):
    tau = math.tau
    return (
        tau * frecuencia,
        tau * (frecuencia * 2.0),
        tau * (frecuencia * 2.382),
        tau * (frecuencia * 3.014),
        tau * (frecuencia * 4.07),
        tau * (frecuencia * 5.43),
        tau * (frecuencia * 6.83),
        tau * (frecuencia * 8.41),
        tau * 1.1,
    )


def sintetizar_campana_carillon(frecuencia, duracion=0.50, volumen=0.42):
    """Sintetiza una campana metálica de bronce con parciales modales y badajo agudo."""
    total = max(1, int(FRECUENCIA_MUESTREO * duracion))
    muestras = array.array("h")
    inv_sr = 1.0 / FRECUENCIA_MUESTREO
    muestras_cola = int(0.030 * FRECUENCIA_MUESTREO)
    muestras_ataque = int(0.0018 * FRECUENCIA_MUESTREO)
    w1, w2, w_tierce, w3, w4, w5, w_cl1, w_cl2, w_chorus = _frecuencias_campana(frecuencia)

    for i in range(total):
        t = i * inv_sr
        compuerta = min(1.0, i / max(1, muestras_ataque)) * min(
            1.0, (total - i) / max(1, muestras_cola)
        )
        mod_metal = 0.55 * math.exp(-34.0 * t) * math.sin(w_tierce * t)
        parciales = (
            math.sin(w1 * t) * 0.46 * math.exp(-5.4 * t)
            + math.sin(w2 * t + mod_metal) * 0.38 * math.exp(-7.5 * t)
            + math.sin(w_tierce * t) * 0.25 * math.exp(-11.0 * t)
            + math.sin(w3 * t) * 0.22 * math.exp(-13.5 * t)
            + math.sin(w4 * t) * 0.18 * math.exp(-19.0 * t)
            + math.sin(w5 * t) * 0.13 * math.exp(-28.0 * t)
            + (math.sin(w_cl1 * t) * 0.18 + math.sin(w_cl2 * t) * 0.12) * math.exp(-130.0 * t)
        )
        apertura_est = (
            math.sin(w2 * t + 0.18 * math.sin(w_chorus * t)) * 0.08 * math.exp(-6.5 * t)
        )
        base = math.tanh(parciales * 0.92)
        muestra_l = (base + apertura_est) * compuerta * volumen
        muestra_r = (base - apertura_est) * compuerta * volumen
        muestras.append(int(max(-32767, min(32767, muestra_l * 32767))))
        muestras.append(int(max(-32767, min(32767, muestra_r * 32767))))

    return pygame.mixer.Sound(buffer=muestras.tobytes())


def _crear_constructor_sfx(duracion, capas, adsr, volumen):
    return lambda: sintetizar_sfx(duracion, capas, adsr=adsr, volumen=volumen)


#---- Clase Audio ----#
class Audio:
    """Gestiona efectos pregrabados, sintesis procedural y pistas musicales."""

    DIR_SFX_WAV = Path(__file__).resolve().parent / "assets" / "audio" / "sfx"
    DIR_MUSICA = Path(__file__).resolve().parent / "assets" / "audio" / "musica"

    def _cargar_sfx(self, clave):
        """Carga el archivo de audio base si existe en disco."""
        base = "dano" if clave == "daño" else clave
        for ext in (".ogg", ".wav"):
            ruta = self.DIR_SFX_WAV / f"{base}{ext}"
            if ruta.exists():
                try:
                    return pygame.mixer.Sound(str(ruta))
                except pygame.error:
                    pass
        return None

    def __init__(self):
        self.activo = False
        self.sonidos = {}
        self._lazy_builders = {}
        self.canal_dron = None
        self.canal_campana = None
        self.sonido_dron = None
        self.sonido_latido = None
        self.musica_actual = None
        self.musica_bucle = True

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(
                    frequency=FRECUENCIA_MUESTREO,
                    size=-16,
                    channels=2,
                    buffer=2048,
                )
            self._construir_banco()
            self.activo = True
        except pygame.error:
            self.activo = False

    def _construir_banco(self):
        """Carga los efectos base en disco y sintetiza los restantes."""
        claves_wav = (
            "salto", "dash", "ataque", "pala", "rebote_pala", "stomp",
            "onda", "jefe_aviso", "jefe_fase", "pala_recoger", "dash_recoger",
            "checkpoint", "vida_extra", "ui", "daño", "muerte", "meta",
            "corazon_latido", "dron_catacumbas",
        )
        for c_wav in claves_wav:
            snd_disco = self._cargar_sfx(c_wav)
            if snd_disco is not None:
                factor = _GANANCIA_SFX_DISCO.get(c_wav, 1.0)
                self.sonidos[c_wav] = _escalar_ganancia_sound(snd_disco, factor)

        for clave, (dur, capas, adsr, vol) in _PRESETS_SFX.items():
            if clave not in self.sonidos:
                self.sonidos[clave] = sintetizar_sfx(dur, capas, adsr=adsr, volumen=vol)
        self.sonidos["rebote_metalico"] = self.sonidos["rebote_pala"]
        self._construir_escalas_y_ambiente()

    def _construir_escalas_y_ambiente(self):
        for idx, nota in enumerate(_NOTAS_ALMAS, 1):
            capas_chime = [
                ("seno", nota, 0, 0.65, None),
                ("seno", nota * 2.0, 15, 0.35, None),
                ("fm", nota * 1.5, 0, 0.28, (nota * 3.0, 0.9)),
                ("seno", nota * 3.0, 40, 0.15, None),
            ]
            self.sonidos[f"alma_{idx}"] = sintetizar_sfx(
                0.34, capas_chime, adsr=(0.004, 0.07, 0.45, 0.266), volumen=0.40
            )
        self.sonidos["alma"] = self.sonidos["alma_1"]

        for idx, nota in enumerate(_NOTAS_CAMPANAS, 1):
            self.sonidos[f"campana_{idx}"] = sintetizar_campana_carillon(
                nota, duracion=0.50, volumen=0.42
            )
        self.sonidos["campana_repique"] = self.sonidos["campana_1"]

        if "corazon_latido" not in self.sonidos:
            self.sonidos["corazon_latido"] = sintetizar_corazon_delator(volumen=0.34)
        self.sonido_latido = self.sonidos["corazon_latido"]
        self.sonidos["corazon"] = self.sonido_latido

        if "dron_catacumbas" not in self.sonidos:
            self.sonidos["dron_catacumbas"] = sintetizar_dron_funebre(duracion=4.0, volumen=0.025)
        self.sonido_dron = self.sonidos["dron_catacumbas"]
        if self.sonido_dron is not None:
            self.sonido_dron.set_volume(0.26)

        for clave_tier, params in _TIERS_FAROL.items():
            self._lazy_builders[clave_tier] = _crear_constructor_sfx(*params)

    def reproducir(self, nombre):
        """Reproduce el efecto indicado si el mezclador esta activo."""
        if not self.activo:
            return
        if nombre not in self.sonidos and nombre in self._lazy_builders:
            try:
                self.sonidos[nombre] = self._lazy_builders[nombre]()
            except Exception:
                pass

        sonido = self.sonidos.get(nombre)
        if sonido is not None:
            if nombre.startswith("campana"):
                try:
                    if self.canal_campana is None:
                        self.canal_campana = pygame.mixer.Channel(6)
                    self.canal_campana.play(sonido)
                    return
                except pygame.error:
                    pass
            sonido.play()

    def iniciar_dron(self):
        # Enciende el sonido de ambiente en bucle
        if not self.activo or not self.sonido_dron:
            return
        try:
            if self.canal_dron is None:
                self.canal_dron = pygame.mixer.Channel(7)
            self.canal_dron.set_volume(0.26)
            if not self.canal_dron.get_busy():
                self.canal_dron.play(self.sonido_dron, loops=-1)
        except pygame.error:
            pass

    def detener_dron(self):
        # Frena el sonido de ambiente
        if self.canal_dron and self.canal_dron.get_busy():
            self.canal_dron.stop()

    def alternar(self):
        # Activa o silencia el audio general
        self.activo = not self.activo
        if not self.activo:
            self.detener_dron()
            self.detener_musica()

    def _ruta_musica_por_id(self, id_musica):
        # Busca el archivo de musica correspondiente
        for ext in (".ogg", ".wav", ".mp3"):
            cand = self.DIR_MUSICA / f"{id_musica}{ext}"
            if cand.exists():
                return cand
        return None

    def reproducir_musica(self, id_musica, bucle=True, fade_ms=800):
        # Cambia la pista de musica si no estaba sonando ya
        self.musica_bucle = bool(bucle)
        if not self.activo:
            self.musica_actual = id_musica
            return
        if self.musica_actual == id_musica and pygame.mixer.music.get_busy():
            return

        ruta = self._ruta_musica_por_id(id_musica)
        if ruta and ruta.exists():
            try:
                loops = -1 if bucle else 0
                pygame.mixer.music.stop()
                pygame.mixer.music.load(str(ruta))
                pygame.mixer.music.set_volume(0.45)
                pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
                self.musica_actual = id_musica
            except pygame.error:
                pass

    def asegurar_musica_activa(self, id_musica_fallback=None):
        """Relanza la pista en bucle si el mezclador quedó en silencio tras una transición rápida."""
        if not self.activo:
            return
        objetivo = self.musica_actual if self.musica_bucle else id_musica_fallback
        if not objetivo:
            objetivo = id_musica_fallback
        if objetivo and (not pygame.mixer.music.get_busy() or not self.musica_bucle):
            self.reproducir_musica(objetivo, bucle=True, fade_ms=400)

    def detener_musica(self, fade_ms=800):
        # Detiene la musica con desvanecimiento
        self.musica_actual = None
        self.musica_bucle = False
        try:
            pygame.mixer.music.fadeout(fade_ms)
        except pygame.error:
            pass
