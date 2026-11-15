#---- Importamos librerias ----#
import array
import math
from pathlib import Path
import random
import pygame

# Frecuencia de muestreo estandar
FRECUENCIA_MUESTREO = 44100


#---- Sintesis de efectos de sonido con ADSR ----#
def sintetizar_sfx(
    duracion,
    capas,
    adsr=(0.01, 0.05, 0.7, 0.05),
    volumen=0.25,
    detune=1.0,
    pan=0.0,
):
    # Genera un buffer de audio estereo de 16 bits
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
        # Envolvente de volumen
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
def sintetizar_dron_funebre(duracion=4.0, volumen=0.10):
    # Genera un zumbido grave continuo para las catacumbas
    total = int(FRECUENCIA_MUESTREO * duracion)
    muestras = array.array("h")
    tau = math.tau

    for i in range(total):
        t = i / FRECUENCIA_MUESTREO
        lfo = 0.5 + 0.5 * math.sin(tau * 0.25 * t)
        lfo2 = 0.5 + 0.5 * math.cos(tau * 0.18 * t)

        f1 = math.sin(tau * 55.0 * t)
        f2 = 0.45 * math.sin(tau * 110.0 * t + 0.4)
        f3 = 0.25 * math.sin(tau * 164.8 * t + 0.8)
        f4 = 0.15 * math.sin(tau * 220.0 * t)

        s_left = (f1 + f2 * (0.8 + 0.2 * lfo) + f3 + f4) * volumen
        s_right = (f1 + f2 * (0.8 + 0.2 * lfo2) + f3 * 1.1 + f4 * 0.9) * volumen

        edge_env = min(1.0, min(i, total - i) / (FRECUENCIA_MUESTREO * 0.1))

        val_l = int(max(-32767, min(32767, s_left * edge_env * 32767)))
        val_r = int(max(-32767, min(32767, s_right * edge_env * 32767)))
        muestras.append(val_l)
        muestras.append(val_r)

    return pygame.mixer.Sound(buffer=muestras.tobytes())


#---- Clase Audio ----#
class Audio:
    DIR_SFX_WAV = Path(__file__).resolve().parent / "assets" / "audio" / "sfx"
    DIR_MUSICA = Path(__file__).resolve().parent / "assets" / "audio" / "musica"

    def _cargar_sfx(self, clave):
        # Carga el archivo de audio pregrabado si existe
        if clave == "daño":
            base = "dano"
        elif clave == "alma":
            base = "alma_ref"
        else:
            base = clave
        for ext in (".ogg", ".wav"):
            ruta = self.DIR_SFX_WAV / f"{base}{ext}"
            if ruta.exists():
                try:
                    return pygame.mixer.Sound(str(ruta))
                except pygame.error:
                    pass
        return None

    def _sonido(self, clave, fn_sintesis):
        # Devuelve el archivo si existe, sino lo sintetiza
        cargado = self._cargar_sfx(clave)
        if cargado is not None:
            return cargado
        return fn_sintesis()

    def __init__(self):
        self.activo = False
        self.sonidos = {}
        self.variaciones = {}
        self._lazy_builders = {}
        self.canal_dron = None
        self.sonido_dron = None
        self.sonido_latido = None
        self.tiempo_ultimo_latido = 0.0
        self.musica_actual = None

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
        # Precargamos los sonidos del juego desde disco
        claves_wav = (
            "salto", "dash", "ataque", "pala", "rebote_pala", "stomp",
            "onda", "jefe_aviso", "jefe_fase", "pala_recoger", "dash_recoger",
            "checkpoint", "vida_extra", "ui", "daño", "muerte", "meta",
            "corazon_latido", "dron_catacumbas", "alma"
        )
        for c_wav in claves_wav:
            snd_disco = self._cargar_sfx(c_wav)
            if snd_disco is not None:
                self.sonidos[c_wav] = snd_disco

        # Salto
        if "salto" not in self.sonidos:
            capas_salto = [
                ("seno", 210, 160, 0.7, None),
                ("ruido", 0, 0, 0.2, None),
                ("fm", 320, 80, 0.2, (640, 0.6)),
            ]
            self.sonidos["salto"] = sintetizar_sfx(0.14, capas_salto, adsr=(0.01, 0.04, 0.5, 0.09), volumen=0.18)
        self.variaciones["salto"] = [self.sonidos["salto"]] * 3

        # Dash
        if "dash" not in self.sonidos:
            capas_dash = [
                ("ruido", 0, 0, 0.45, None),
                ("sierra", 140, 320, 0.4, None),
                ("seno", 90, 180, 0.35, None),
            ]
            self.sonidos["dash"] = sintetizar_sfx(0.18, capas_dash, adsr=(0.02, 0.06, 0.4, 0.10), volumen=0.18)
        self.variaciones["dash"] = [self.sonidos["dash"]] * 3

        # Ataque con la pala o guadana
        if "ataque" not in self.sonidos:
            capas_ataque = [
                ("fm", 280, 480, 0.65, (560, 1.2)),
                ("ruido", 0, 0, 0.35, None),
            ]
            self.sonidos["ataque"] = sintetizar_sfx(0.11, capas_ataque, adsr=(0.005, 0.03, 0.4, 0.075), volumen=0.18)
        self.variaciones["ataque"] = [self.sonidos["ataque"]] * 3

        # Golpe de impacto
        if "pala" not in self.sonidos:
            capas_pala = [
                ("ruido", 0, 0, 0.45, None),
                ("seno", 115, -60, 0.5, None),
                ("fm", 440, -180, 0.35, (880, 1.8)),
            ]
            self.sonidos["pala"] = sintetizar_sfx(0.20, capas_pala, adsr=(0.005, 0.05, 0.3, 0.145), volumen=0.26)
        if "rebote_pala" not in self.sonidos:
            self.sonidos["rebote_pala"] = self.sonidos["pala"]
        self.variaciones["pala"] = [self.sonidos["pala"]] * 3

        # Pisoton
        if "stomp" not in self.sonidos:
            capas_stomp = [
                ("ruido", 0, 0, 0.5, None),
                ("seno", 85, -45, 0.6, None),
                ("cuadrada", 55, -20, 0.25, None),
            ]
            self.sonidos["stomp"] = sintetizar_sfx(0.18, capas_stomp, adsr=(0.005, 0.04, 0.4, 0.135), volumen=0.26)
        self.variaciones["stomp"] = [self.sonidos["stomp"]] * 3

        # Sonidos de almas en escala ascendente
        notas_almas = [523.25, 587.33, 659.25, 783.99, 880.00, 1046.50]
        for idx, nota in enumerate(notas_almas, 1):
            capas_chime = [
                ("seno", nota, 0, 0.65, None),
                ("seno", nota * 2.0, 15, 0.35, None),
                ("fm", nota * 1.5, 0, 0.28, (nota * 3.0, 0.9)),
                ("seno", nota * 3.0, 40, 0.15, None),
            ]
            self.sonidos[f"alma_{idx}"] = sintetizar_sfx(
                0.34,
                capas_chime,
                adsr=(0.004, 0.07, 0.45, 0.266),
                volumen=0.22,
            )
        self.sonidos["alma"] = self.sonidos["alma_1"]
        self.variaciones.pop("alma", None)

        # Onda del jefe
        if "onda" not in self.sonidos:
            capas_onda = [
                ("ruido", 0, 0, 0.5, None),
                ("seno", 65, 50, 0.55, None),
                ("sierra", 85, 40, 0.25, None),
            ]
            self.sonidos["onda"] = sintetizar_sfx(0.40, capas_onda, adsr=(0.02, 0.10, 0.6, 0.28), volumen=0.22)

        # Avisos del jefe
        if "jefe_aviso" not in self.sonidos:
            capas_aviso = [
                ("cuadrada", 180, -50, 0.6, None),
                ("fm", 360, -100, 0.4, (180, 1.4)),
            ]
            self.sonidos["jefe_aviso"] = sintetizar_sfx(0.28, capas_aviso, adsr=(0.02, 0.08, 0.5, 0.18), volumen=0.18)

        if "jefe_fase" not in self.sonidos:
            capas_fase = [
                ("cuadrada", 110, -35, 0.6, None),
                ("seno", 55, 30, 0.5, None),
                ("ruido", 0, 0, 0.3, None),
            ]
            self.sonidos["jefe_fase"] = sintetizar_sfx(0.55, capas_fase, adsr=(0.04, 0.15, 0.6, 0.36), volumen=0.25)

        # Recoleccion de items
        if "pala_recoger" not in self.sonidos:
            capas_pala_recoger = [
                ("fm", 540, 260, 0.7, (1080, 1.2)),
                ("seno", 720, 220, 0.4, None),
            ]
            self.sonidos["pala_recoger"] = sintetizar_sfx(0.25, capas_pala_recoger, adsr=(0.01, 0.08, 0.6, 0.16), volumen=0.18)

        if "dash_recoger" not in self.sonidos:
            capas_dash_recoger = [
                ("seno", 340, 380, 0.65, None),
                ("fm", 680, 420, 0.35, (1360, 1.1)),
            ]
            self.sonidos["dash_recoger"] = sintetizar_sfx(0.28, capas_dash_recoger, adsr=(0.01, 0.08, 0.6, 0.19), volumen=0.18)

        if "checkpoint" not in self.sonidos:
            capas_checkpoint = [
                ("seno", 520, 260, 0.6, None),
                ("fm", 1040, 180, 0.3, (1560, 0.8)),
            ]
            self.sonidos["checkpoint"] = sintetizar_sfx(0.32, capas_checkpoint, adsr=(0.01, 0.08, 0.6, 0.23), volumen=0.18)

        if "vida_extra" not in self.sonidos:
            capas_vida_extra = [
                ("seno", 680, 480, 0.6, None),
                ("seno", 850, 420, 0.3, None),
                ("fm", 1360, 240, 0.25, (2040, 0.6)),
            ]
            self.sonidos["vida_extra"] = sintetizar_sfx(0.44, capas_vida_extra, adsr=(0.02, 0.12, 0.6, 0.30), volumen=0.20)

        # Interfaz de usuario
        if "ui" not in self.sonidos:
            capas_ui = [
                ("cuadrada", 420, -60, 0.6, None),
                ("seno", 840, -120, 0.4, None),
            ]
            self.sonidos["ui"] = sintetizar_sfx(0.06, capas_ui, adsr=(0.005, 0.02, 0.3, 0.035), volumen=0.10)

        # Danio y muerte
        if "daño" not in self.sonidos:
            capas_dano = [
                ("cuadrada", 160, -90, 0.65, None),
                ("ruido", 0, 0, 0.45, None),
            ]
            self.sonidos["daño"] = sintetizar_sfx(0.26, capas_dano, adsr=(0.005, 0.06, 0.4, 0.195), volumen=0.24)

        if "muerte" not in self.sonidos:
            capas_muerte = [
                ("cuadrada", 75, -40, 0.7, None),
                ("seno", 55, -25, 0.5, None),
                ("ruido", 0, 0, 0.35, None),
            ]
            self.sonidos["muerte"] = sintetizar_sfx(0.65, capas_muerte, adsr=(0.03, 0.18, 0.6, 0.44), volumen=0.28)

        # Fin de nivel
        if "meta" not in self.sonidos:
            capas_meta = [
                ("seno", 220, 280, 0.6, None),
                ("fm", 440, 360, 0.35, (880, 1.0)),
            ]
            self.sonidos["meta"] = sintetizar_sfx(0.55, capas_meta, adsr=(0.02, 0.14, 0.6, 0.39), volumen=0.20)

        # Rebote de metal
        if "rebote_pala" not in self.sonidos:
            capas_rebote = [
                ("fm", 880, -320, 0.6, (1420, 2.5)),
                ("ruido", 0, 0, 0.3, None),
                ("seno", 220, -90, 0.4, None),
            ]
            self.sonidos["rebote_pala"] = sintetizar_sfx(0.16, capas_rebote, adsr=(0.004, 0.04, 0.3, 0.116), volumen=0.24)
        self.sonidos["rebote_metalico"] = self.sonidos["rebote_pala"]

        # Latido
        if "corazon_latido" not in self.sonidos:
            self.sonido_latido = self._sonido("corazon_latido", lambda: sintetizar_corazon_delator(volumen=0.34))
            self.sonidos["corazon_latido"] = self.sonido_latido
        else:
            self.sonido_latido = self.sonidos["corazon_latido"]
        self.sonidos["corazon"] = self.sonido_latido

        # Dron ambiental
        if "dron_catacumbas" not in self.sonidos:
            self.sonido_dron = self._sonido("dron_catacumbas", lambda: sintetizar_dron_funebre(duracion=4.0, volumen=0.045))
            self.sonidos["dron_catacumbas"] = self.sonido_dron
        else:
            self.sonido_dron = self.sonidos["dron_catacumbas"]

        # Losa rompiendose
        if "losa_romper" not in self.sonidos:
            capas_losa = [
                ("ruido", 0, 0, 0.65, None),
                ("cuadrada", 95, -50, 0.45, None),
                ("seno", 60, -30, 0.4, None),
            ]
            self.sonidos["losa_romper"] = sintetizar_sfx(0.19, capas_losa, adsr=(0.003, 0.04, 0.25, 0.147), volumen=0.28)
        self.variaciones["losa_romper"] = [self.sonidos["losa_romper"]] * 3

        # Campana
        if "campana_repique" not in self.sonidos:
            capas_campana = [
                ("seno", 660, -20, 0.60, None),
                ("fm", 990, -30, 0.40, (1980, 0.8)),
                ("seno", 1320, -40, 0.25, None),
                ("seno", 330, -10, 0.20, None),
            ]
            self.sonidos["campana_repique"] = sintetizar_sfx(0.55, capas_campana, adsr=(0.004, 0.08, 0.45, 0.466), volumen=0.26)
        self.variaciones["campana_repique"] = [self.sonidos["campana_repique"]] * 3

        # Sonidos del farol segun el tier
        def _build_tier1():
            capas = [
                ("seno", 293.66, 0, 0.45, None),
                ("seno", 349.23, 0, 0.40, None),
                ("seno", 440.00, 0, 0.45, None),
                ("fm", 587.33, 0, 0.25, (1174.66, 0.6)),
            ]
            return sintetizar_sfx(0.48, capas, adsr=(0.02, 0.10, 0.6, 0.36), volumen=0.22)

        def _build_tier2():
            capas = [
                ("seno", 523.25, 0, 0.45, None),
                ("seno", 659.25, 0, 0.40, None),
                ("seno", 783.99, 0, 0.45, None),
                ("fm", 1046.50, 0, 0.35, (2093.0, 0.8)),
            ]
            return sintetizar_sfx(0.58, capas, adsr=(0.015, 0.12, 0.65, 0.445), volumen=0.24)

        def _build_tier3():
            capas = [
                ("seno", 587.33, 0, 0.45, None),
                ("seno", 739.99, 0, 0.40, None),
                ("seno", 880.00, 0, 0.40, None),
                ("fm", 1174.66, 0, 0.35, (2349.32, 1.2)),
                ("seno", 1320.00, -20, 0.25, None),
            ]
            return sintetizar_sfx(0.72, capas, adsr=(0.02, 0.15, 0.7, 0.55), volumen=0.26)

        self._lazy_builders["farol_tier_1"] = _build_tier1
        self._lazy_builders["farol_tier_2"] = _build_tier2
        self._lazy_builders["farol_tier_3"] = _build_tier3

    def reproducir(self, nombre):
        # Reproduce un efecto de sonido
        if not self.activo:
            return
        if nombre not in self.sonidos and nombre in self._lazy_builders:
            try:
                self.sonidos[nombre] = self._lazy_builders[nombre]()
            except Exception:
                pass

        if nombre in self.variaciones:
            variantes = self.variaciones[nombre]
            sonido = random.choice(variantes)
            sonido.play()
            return

        sonido = self.sonidos.get(nombre)
        if sonido is not None:
            sonido.play()

    def iniciar_dron(self):
        # Enciende el sonido de ambiente en bucle
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
        if not self.activo:
            self.musica_actual = id_musica
            return
        if self.musica_actual == id_musica and pygame.mixer.music.get_busy():
            return

        ruta = self._ruta_musica_por_id(id_musica)
        if ruta and ruta.exists():
            try:
                loops = -1 if bucle else 0
                pygame.mixer.music.load(str(ruta))
                pygame.mixer.music.set_volume(0.45)
                pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
                self.musica_actual = id_musica
            except pygame.error:
                pass

    def detener_musica(self, fade_ms=800):
        # Detiene la musica con desvanecimiento
        self.musica_actual = None
        try:
            pygame.mixer.music.fadeout(fade_ms)
        except pygame.error:
            pass
