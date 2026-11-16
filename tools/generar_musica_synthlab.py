"""Generador de música gótica-barroca moderna basada en teoría SynthLab (Z12).

Combina armonía barroca extendida (acordes menores con séptima/novena, bajos
descendentes tipo lamento y cadencias frigias), melodía en contrapunto con
cuerda pulsada/clavecín y ritmos contemporáneos de rock y R&B con micro-swing.
"""

from pathlib import Path
import subprocess
import tempfile
import wave

import numpy as np

SR = 44100
RAIZ = Path(__file__).resolve().parent.parent
DIR_MUSICA = RAIZ / "assets" / "audio" / "musica"


#---- Teoría musical Z12 y utilidades de afinación ----#
def midi_a_hz(nota_midi: float) -> float:
    """Convierte una altura MIDI en frecuencia (A4 = 440 Hz)."""
    return 440.0 * (2.0 ** ((nota_midi - 69.0) / 12.0))


def envolvente_adsr(n_muestras: int, ataque: float, decaimiento: float, sostenido: float, relevo: float) -> np.ndarray:
    """Construye una envolvente ADSR suavizada de longitud exacta."""
    env = np.zeros(n_muestras, dtype=np.float32)
    na = max(1, int(ataque * SR))
    nd = max(1, int(decaimiento * SR))
    nr = max(1, int(relevo * SR))
    if na + nd + nr >= n_muestras:
        escala = n_muestras / float(na + nd + nr)
        na = max(1, int(na * escala))
        nd = max(1, int(nd * escala))
        nr = max(1, n_muestras - na - nd)
    ns = max(0, n_muestras - na - nd - nr)

    idx = 0
    env[idx:idx + na] = np.linspace(0.0, 1.0, na, dtype=np.float32)
    idx += na
    env[idx:idx + nd] = np.linspace(1.0, sostenido, nd, dtype=np.float32)
    idx += nd
    if ns > 0:
        env[idx:idx + ns] = sostenido
        idx += ns
    rem = n_muestras - idx
    if rem > 0:
        env[idx:] = np.linspace(sostenido, 0.0, rem, dtype=np.float32) ** 1.5
    return env


#---- Síntesis instrumental (Armonía, Melodía, Bajo y Batería Rock/R&B) ----#
def inst_organo_barroco(freq: float, dur: float, vel: float = 0.8) -> np.ndarray:
    """Órgano cálido tipo Juno/catedral sin estridencia metálica."""
    n = max(64, int(dur * SR))
    t = np.arange(n, dtype=np.float32) / SR
    vib = 1.0 + 0.0022 * np.sin(2.0 * np.pi * 5.2 * t)
    fase = 2.0 * np.pi * freq * np.cumsum(vib) / SR
    onda = (
        0.52 * np.sin(fase)
        + 0.28 * np.sin(fase * 2.0 + 0.3)
        + 0.14 * np.sin(fase * 3.0)
        + 0.10 * np.sin(fase * 0.5)
    )
    brillo = np.exp(-2.8 * t)
    onda = 0.72 * onda + 0.28 * onda * brillo
    env = envolvente_adsr(n, 0.035, 0.14, 0.72, min(0.22, dur * 0.35))
    return (onda * env * vel * 0.36).astype(np.float32)


def inst_clavecin_moderno(freq: float, dur: float, vel: float = 0.85) -> np.ndarray:
    """Punteo barroco híbrido (clavecín FM + guitarra limpia cálida)."""
    n = max(64, int(dur * SR))
    t = np.arange(n, dtype=np.float32) / SR
    mod = (1.8 * np.exp(-10.0 * t)) * np.sin(2.0 * np.pi * freq * 3.0 * t)
    fase = 2.0 * np.pi * freq * t
    cuerpo = np.sin(fase + mod) + 0.35 * np.sin(fase * 2.0) * np.exp(-5.0 * t)
    punteo = np.tanh(cuerpo * 1.35)
    env = envolvente_adsr(n, 0.004, min(0.22, dur * 0.45), 0.28, min(0.18, dur * 0.35))
    return (punteo * env * vel * 0.34).astype(np.float32)


def inst_bajo_rock_rnb(freq: float, dur: float, vel: float = 0.9, overdrive: float = 1.3) -> np.ndarray:
    """Bajo eléctrico / sub-synth con ataque de púa y cuerpo grave."""
    n = max(64, int(dur * SR))
    t = np.arange(n, dtype=np.float32) / SR
    sub = np.sin(2.0 * np.pi * freq * t)
    armonico = np.sin(2.0 * np.pi * freq * 2.0 * t) * np.exp(-6.0 * t)
    clic = np.sin(2.0 * np.pi * freq * 4.0 * t) * np.exp(-26.0 * t)
    mezcla = np.tanh((0.78 * sub + 0.34 * armonico + 0.18 * clic) * overdrive)
    env = envolvente_adsr(n, 0.005, 0.10, 0.68, min(0.10, dur * 0.28))
    return (mezcla * env * vel * 0.46).astype(np.float32)


def inst_lead_expresivo(freq: float, dur: float, vel: float = 0.9) -> np.ndarray:
    """Solista gótico contemporáneo (fusión violonchelo synth + voz lead)."""
    n = max(64, int(dur * SR))
    t = np.arange(n, dtype=np.float32) / SR
    delay_vib = np.clip((t - 0.08) / 0.12, 0.0, 1.0)
    vib = 1.0 + 0.0048 * delay_vib * np.sin(2.0 * np.pi * 5.6 * t)
    fase = 2.0 * np.pi * freq * np.cumsum(vib) / SR
    diente_suave = (
        np.sin(fase)
        + 0.46 * np.sin(2.0 * fase)
        + 0.22 * np.sin(3.0 * fase)
        + 0.11 * np.sin(4.0 * fase)
    )
    onda = np.tanh(diente_suave * 1.15)
    env = envolvente_adsr(n, 0.018, 0.12, 0.74, min(0.18, dur * 0.35))
    return (onda * env * vel * 0.33).astype(np.float32)


def inst_campana_osario(freq: float, dur: float, vel: float = 0.8) -> np.ndarray:
    """Campana de bronce litúrgica para acentos climáticos."""
    n = max(64, int(dur * SR))
    t = np.arange(n, dtype=np.float32) / SR
    onda = (
        0.55 * np.sin(2.0 * np.pi * freq * t) * np.exp(-2.8 * t)
        + 0.30 * np.sin(2.0 * np.pi * freq * 1.1892 * t) * np.exp(-3.4 * t)
        + 0.25 * np.sin(2.0 * np.pi * freq * 2.0 * t) * np.exp(-4.6 * t)
    )
    return (onda * vel * 0.30).astype(np.float32)


def percusion_bombo(vel: float = 0.95) -> np.ndarray:
    """Bombo rock/R&B con golpe subgrave definido."""
    n = int(0.24 * SR)
    t = np.arange(n, dtype=np.float32) / SR
    freq_inst = 46.0 + 135.0 * np.exp(-34.0 * t)
    fase = 2.0 * np.pi * np.cumsum(freq_inst) / SR
    cuerpo = np.tanh(np.sin(fase) * 1.45) * np.exp(-9.5 * t)
    golpe = np.sin(2.0 * np.pi * 220.0 * t) * np.exp(-65.0 * t) * 0.35
    return ((cuerpo + golpe) * vel * 0.52).astype(np.float32)


def percusion_caja(vel: float = 0.85, rng: np.random.Generator = None) -> np.ndarray:
    """Caja seca contemporánea (cuerpo a 185 Hz + bordonera filtrada)."""
    if rng is None:
        rng = np.random.default_rng(7)
    n = int(0.19 * SR)
    t = np.arange(n, dtype=np.float32) / SR
    cuerpo = np.sin(2.0 * np.pi * (175.0 + 90.0 * np.exp(-35.0 * t)) * t) * np.exp(-18.0 * t)
    ruido = rng.uniform(-1.0, 1.0, n).astype(np.float32)
    # Filtro pasa-alto simple para chispa de bordonera
    ruido_hp = np.diff(ruido, prepend=0.0) * 0.7 + ruido * 0.3
    bordonera = ruido_hp * np.exp(-16.0 * t)
    return (np.tanh((0.55 * cuerpo + 0.65 * bordonera) * 1.2) * vel * 0.42).astype(np.float32)


def percusion_charleston(abierto: bool, vel: float = 0.55, rng: np.random.Generator = None) -> np.ndarray:
    """Hi-hat nítido de estudio para pocket R&B/Rock."""
    if rng is None:
        rng = np.random.default_rng(13)
    dur = 0.22 if abierto else 0.065
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    ruido = rng.uniform(-1.0, 1.0, n).astype(np.float32)
    hp = np.diff(np.diff(ruido, prepend=0.0), prepend=0.0)
    decay = 11.0 if abierto else 58.0
    metal = 0.3 * np.sin(2.0 * np.pi * 6840.0 * t) + 0.7 * hp
    return (metal * np.exp(-decay * t) * vel * 0.24).astype(np.float32)


#---- Mezclador estéreo en bucle perfecto ----#
class PistaEstereo:
    """Buffer estéreo con mezcla circular para bucles sin cortes ni clics."""

    def __init__(self, duracion_s: float, en_bucle: bool = True):
        self.n = int(round(duracion_s * SR))
        self.en_bucle = en_bucle
        self.izq = np.zeros(self.n, dtype=np.float32)
        self.der = np.zeros(self.n, dtype=np.float32)

    def mezclar(self, inicio_s: float, muestra: np.ndarray, pan: float = 0.0, ganancia: float = 1.0):
        """Inserta una nota mono con panorama (-1..+1) respetando el borde del bucle."""
        m = muestra * ganancia
        g_l = np.sqrt(0.5 * (1.0 - max(-1.0, min(1.0, pan))))
        g_r = np.sqrt(0.5 * (1.0 + max(-1.0, min(1.0, pan))))
        idx0 = int(round(inicio_s * SR)) % self.n
        fin = idx0 + len(m)
        if fin <= self.n:
            self.izq[idx0:fin] += m * g_l
            self.der[idx0:fin] += m * g_r
        elif self.en_bucle:
            primero = self.n - idx0
            resto = min(self.n, len(m) - primero)
            self.izq[idx0:] += m[:primero] * g_l
            self.der[idx0:] += m[:primero] * g_r
            self.izq[:resto] += m[primero:primero + resto] * g_l
            self.der[:resto] += m[primero:primero + resto] * g_r
        else:
            corte = max(0, self.n - idx0)
            self.izq[idx0:self.n] += m[:corte] * g_l
            self.der[idx0:self.n] += m[:corte] * g_r

    def aplicar_espacio_y_master(self, retardo_s: float, feedback_echo: float = 0.24) -> np.ndarray:
        """Agrega eco estéreo cruzado (ping-pong barroco) y limitador cálido."""
        ret_n = max(1, int(retardo_s * SR))
        l_esp = self.izq.copy()
        r_esp = self.der.copy()
        l_esp += np.roll(self.der, ret_n) * feedback_echo
        r_esp += np.roll(self.izq, int(ret_n * 1.5)) * (feedback_echo * 0.85)
        if not self.en_bucle:
            fade_n = min(int(0.35 * SR), self.n // 4)
            fade = np.linspace(1.0, 0.0, fade_n, dtype=np.float32)
            l_esp[-fade_n:] *= fade
            r_esp[-fade_n:] *= fade

        est = np.stack([l_esp, r_esp], axis=1)
        pico = float(np.max(np.abs(est))) + 1e-6
        est = np.tanh((est / pico) * 1.38) * 0.86
        return (np.clip(est, -1.0, 1.0) * 32767.0).astype(np.int16)


def _mezclar_armonia(
    pista: PistaEstereo,
    acordes: list[list[int]],
    tiempo_paso,
    pasos_por_acorde: int,
    corchea16: float,
    campana_en_1: bool,
    arp_clavecin: bool,
) -> None:
    for i_ac, voces in enumerate(acordes):
        t_ac = tiempo_paso(i_ac * pasos_por_acorde)
        dur_ac = pasos_por_acorde * corchea16 * 0.96
        for idx_v, m_nota in enumerate(voces):
            pan_v = -0.35 + 0.70 * (idx_v / max(1, len(voces) - 1))
            muestra = inst_organo_barroco(midi_a_hz(m_nota), dur_ac, 0.52)
            pista.mezclar(t_ac, muestra, pan=pan_v)
        if campana_en_1 and i_ac % 2 == 0:
            camp = inst_campana_osario(midi_a_hz(voces[0] + 12), 1.4, 0.48)
            pista.mezclar(t_ac, camp, pan=0.12)
        if not arp_clavecin:
            continue
        patron_arp = (0, 2, 1, 3 % len(voces), 2, 1, 3 % len(voces), 0)
        for s in range(0, pasos_por_acorde, 2):
            octava = 12 if (s % 4 == 2) else 0
            nota_arp = voces[patron_arp[(s // 2) % len(patron_arp)]] + octava
            pan_arp = -0.22 if (s % 4 == 0) else 0.26
            arp = inst_clavecin_moderno(midi_a_hz(nota_arp), corchea16 * 2.4, 0.62)
            pista.mezclar(tiempo_paso(i_ac * pasos_por_acorde + s), arp, pan=pan_arp)


def _mezclar_ritmo_y_bajo(
    pista: PistaEstereo,
    pasos_totales: int,
    acordes: list[list[int]],
    pasos_por_acorde: int,
    bajo_patron: list[int],
    ritmos: tuple[str, str, str],
    bateria: tuple[np.ndarray, ...],
    tiempo_paso,
    corchea16: float,
    overdrive_bajo: float,
) -> None:
    ritmo_kick, ritmo_snare, ritmo_hat = ritmos
    bombo, caja, caja_ghost, hat_c, hat_a = bateria
    for p in range(pasos_totales):
        t_p = tiempo_paso(p)
        ch_k = ritmo_kick[p % len(ritmo_kick)]
        ch_s = ritmo_snare[p % len(ritmo_snare)]
        ch_h = ritmo_hat[p % len(ritmo_hat)]
        if ch_k == "x":
            pista.mezclar(t_p, bombo, pan=0.0)
        if ch_s == "X":
            pista.mezclar(t_p, caja, pan=0.05)
        elif ch_s == "g":
            pista.mezclar(t_p, caja_ghost, pan=-0.08)
        if ch_h == "x":
            pista.mezclar(t_p, hat_c, pan=0.28)
        elif ch_h == "o":
            pista.mezclar(t_p, hat_a, pan=0.32)

        semi = bajo_patron[p % len(bajo_patron)]
        if semi is not None:
            ac_actual = acordes[(p // pasos_por_acorde) % len(acordes)]
            nota_bajo = ac_actual[0] - 12 + semi
            muestra_bajo = inst_bajo_rock_rnb(
                midi_a_hz(nota_bajo), corchea16 * 1.85, 0.88, overdrive=overdrive_bajo
            )
            pista.mezclar(t_p, muestra_bajo, pan=-0.04)


def secuenciar_tema(
    nombre: str,
    bpm: float,
    compases: int,
    acordes: list[list[int]],
    bajo_patron: list[int],
    melodia_pasos: list[tuple[int, int, float]],
    ritmo_kick: str,
    ritmo_snare: str,
    ritmo_hat: str,
    swing: float = 0.50,
    en_bucle: bool = True,
    campana_en_1: bool = False,
    overdrive_bajo: float = 1.25,
    arp_clavecin: bool = True,
) -> Path:
    """Compone y exporta a Ogg Vorbis un tema completo (Armonía, Ritmo y Melodía)."""
    corchea16 = (60.0 / bpm) / 4.0
    pasos_totales = compases * 16
    dur_total = pasos_totales * corchea16
    pista = PistaEstereo(dur_total, en_bucle=en_bucle)
    rng = np.random.default_rng(abs(hash(nombre)) % (2**31))
    bateria = (
        percusion_bombo(0.95),
        percusion_caja(0.88, rng),
        percusion_caja(0.34, rng),
        percusion_charleston(False, 0.52, rng),
        percusion_charleston(True, 0.45, rng),
    )

    def tiempo_paso(p: int) -> float:
        offset = (swing - 0.5) * 2.0 * corchea16 if (p % 2 == 1) else 0.0
        return max(0.0, (p * corchea16 + offset) % dur_total)

    pasos_por_acorde = max(8, pasos_totales // len(acordes))
    _mezclar_armonia(
        pista, acordes, tiempo_paso, pasos_por_acorde, corchea16, campana_en_1, arp_clavecin
    )
    _mezclar_ritmo_y_bajo(
        pista,
        pasos_totales,
        acordes,
        pasos_por_acorde,
        bajo_patron,
        (ritmo_kick, ritmo_snare, ritmo_hat),
        bateria,
        tiempo_paso,
        corchea16,
        overdrive_bajo,
    )
    for paso_ini, nota_m, dur_pasos in melodia_pasos:
        if 0 <= paso_ini < pasos_totales:
            lead = inst_lead_expresivo(midi_a_hz(nota_m), dur_pasos * corchea16, 0.86)
            pista.mezclar(tiempo_paso(paso_ini), lead, pan=-0.08)

    audio_i16 = pista.aplicar_espacio_y_master(retardo_s=corchea16 * 3.0, feedback_echo=0.22)
    return _exportar_ogg(audio_i16, DIR_MUSICA / f"{nombre}.ogg")


def _exportar_ogg(audio_i16: np.ndarray, destino: Path) -> Path:
    """Codifica un arreglo estéreo int16 en un archivo .ogg Vorbis mediante ffmpeg."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp_wav:
        with wave.open(tmp_wav.name, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(SR)
            wf.writeframes(audio_i16.tobytes())
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", tmp_wav.name,
                "-c:a", "libvorbis", "-q:a", "4",
                str(destino),
            ],
            check=True,
        )
    return destino


#---- Tabla declarativa de especificaciones musicales ----#
_BAJO_RNB = [0, None, None, 0, None, None, 7, None, 12, None, 10, None, 7, None, 5, None]
_BAJO_ROCK = [0, None, 0, None, 0, None, 7, 10, 12, None, 0, None, 7, None, 10, 7]
_BAJO_FURIA = [0, 0, None, 0, 12, None, 0, 10, 0, 0, None, 0, 7, None, 10, 11]

_KICK_RNB, _SNARE_RNB, _HAT_RNB = "x..x..x...x.....", "....X..g.g..X..g", "x.x.x.o.x.x.x.o."
_KICK_ROCK, _SNARE_ROCK, _HAT_ROCK = "x...x.x.x..x..x.", "....X.......X..g", "x.x.x.x.x.o.x.x."
_KICK_JEFE, _SNARE_JEFE, _HAT_JEFE = "x.x...x.x.x...x.", "....X..g....X.g.", "xxxxxxxxxxxxxxxx"

ESPECIFICACIONES_PISTAS = (
    dict(
        nombre="titulo", bpm=94, compases=8, swing=0.56, campana_en_1=True,
        acordes=[
            [50, 53, 57, 60, 64],
            [48, 52, 55, 59, 62],
            [46, 50, 53, 57, 60],
            [45, 49, 52, 55, 61],
        ],
        bajo_patron=_BAJO_RNB,
        ritmo_kick=_KICK_RNB, ritmo_snare=_SNARE_RNB, ritmo_hat=_HAT_RNB,
        melodia_pasos=[
            (0, 69, 4), (4, 72, 2), (6, 74, 4), (10, 72, 2), (12, 69, 4),
            (16, 67, 4), (20, 71, 4), (24, 72, 6), (30, 69, 2),
            (34, 74, 4), (38, 77, 4), (42, 76, 4), (48, 74, 4),
            (52, 73, 4), (56, 69, 6), (62, 64, 2),
            (64, 69, 4), (68, 72, 4), (72, 76, 4), (76, 74, 4),
            (82, 72, 4), (86, 71, 4), (92, 69, 4),
            (96, 70, 4), (102, 69, 4), (108, 67, 4), (112, 69, 6), (120, 64, 6),
        ],
    ),
    dict(
        nombre="camposanto", bpm=114, compases=8, swing=0.52,
        acordes=[
            [52, 55, 59, 62, 66],
            [48, 52, 55, 59, 62],
            [45, 48, 52, 55, 59],
            [47, 51, 54, 57, 60],
        ],
        bajo_patron=_BAJO_ROCK,
        ritmo_kick=_KICK_ROCK, ritmo_snare=_SNARE_ROCK, ritmo_hat=_HAT_ROCK,
        melodia_pasos=[
            (0, 64, 3), (3, 67, 3), (6, 71, 4), (10, 69, 3), (13, 67, 3),
            (16, 67, 4), (20, 71, 4), (24, 72, 4), (28, 71, 4),
            (32, 69, 4), (36, 67, 3), (39, 66, 3), (42, 64, 4), (46, 66, 2),
            (48, 67, 4), (52, 66, 4), (56, 63, 4), (60, 59, 4),
            (64, 76, 3), (67, 74, 3), (70, 71, 4), (74, 74, 3), (77, 72, 3),
            (80, 71, 4), (84, 72, 4), (88, 74, 4), (92, 76, 4),
            (96, 72, 4), (100, 71, 4), (104, 69, 4), (108, 67, 4),
            (112, 66, 4), (116, 67, 3), (119, 69, 3), (122, 71, 6),
        ],
    ),
    dict(
        nombre="cripta", bpm=100, compases=8, swing=0.55, campana_en_1=True,
        acordes=[
            [54, 57, 61, 64, 68],
            [55, 59, 62, 66, 69],
            [52, 55, 59, 62, 66],
            [49, 53, 56, 59, 62],
        ],
        bajo_patron=_BAJO_RNB,
        ritmo_kick=_KICK_RNB, ritmo_snare=_SNARE_RNB, ritmo_hat=_HAT_RNB,
        melodia_pasos=[
            (2, 73, 4), (6, 74, 2), (8, 73, 4), (12, 71, 4),
            (16, 71, 4), (20, 74, 4), (24, 78, 4), (28, 74, 4),
            (34, 71, 4), (38, 73, 2), (40, 71, 4), (44, 69, 4),
            (48, 68, 4), (52, 69, 4), (56, 73, 4), (60, 68, 4),
            (64, 78, 4), (68, 79, 2), (70, 78, 4), (74, 74, 6),
            (82, 79, 4), (86, 78, 4), (90, 74, 6),
            (96, 76, 4), (100, 74, 4), (104, 73, 4), (108, 71, 4),
            (112, 73, 4), (116, 71, 2), (118, 69, 4), (122, 68, 6),
        ],
    ),
    dict(
        nombre="osario", bpm=128, compases=8, swing=0.50, campana_en_1=True, overdrive_bajo=1.45,
        acordes=[
            [48, 51, 55, 58, 62],
            [46, 50, 53, 56, 60],
            [44, 48, 51, 55, 58],
            [43, 47, 50, 53, 56],
        ],
        bajo_patron=_BAJO_ROCK,
        ritmo_kick=_KICK_ROCK, ritmo_snare=_SNARE_ROCK, ritmo_hat=_HAT_ROCK,
        melodia_pasos=[
            (0, 72, 2), (2, 75, 2), (4, 74, 2), (6, 72, 2), (8, 79, 4), (12, 75, 4),
            (16, 74, 3), (19, 77, 3), (22, 75, 4), (26, 74, 6),
            (32, 72, 2), (34, 74, 2), (36, 75, 4), (40, 79, 4), (44, 80, 4),
            (48, 79, 4), (52, 77, 4), (56, 75, 4), (60, 74, 4),
            (64, 72, 2), (66, 75, 2), (68, 79, 4), (72, 83, 4), (76, 80, 4),
            (80, 79, 4), (84, 77, 4), (88, 74, 4), (92, 75, 4),
            (96, 80, 4), (100, 79, 4), (104, 75, 4), (108, 74, 4),
            (112, 72, 4), (116, 74, 2), (118, 75, 2), (120, 74, 4), (124, 71, 4),
        ],
    ),
    dict(
        nombre="carcelero",
        bpm=138, compases=8, swing=0.50, campana_en_1=True, overdrive_bajo=1.70,
        acordes=[
            [47, 50, 54, 57, 61],
            [48, 52, 55, 59, 62],
            [45, 48, 52, 55, 59],
            [42, 46, 49, 52, 55],
        ],
        bajo_patron=_BAJO_FURIA,
        ritmo_kick=_KICK_JEFE, ritmo_snare=_SNARE_JEFE, ritmo_hat=_HAT_ROCK,
        melodia_pasos=[
            (0, 71, 2), (2, 74, 2), (4, 78, 4), (8, 76, 4), (12, 74, 4),
            (16, 72, 4), (20, 76, 4), (24, 79, 4), (28, 76, 4),
            (32, 74, 4), (36, 72, 4), (40, 71, 4), (44, 69, 4),
            (48, 70, 4), (52, 73, 4), (56, 78, 4), (60, 76, 4),
            (64, 71, 2), (66, 78, 2), (68, 83, 4), (72, 81, 4), (76, 78, 4),
            (80, 79, 4), (84, 76, 4), (88, 74, 4), (92, 72, 4),
            (96, 74, 3), (99, 76, 3), (102, 78, 4), (106, 74, 6),
            (112, 73, 4), (116, 76, 4), (120, 78, 4), (124, 70, 4),
        ],
    ),
    dict(
        nombre="custodio_f1",
        bpm=134, compases=8, swing=0.50, campana_en_1=True, overdrive_bajo=1.55,
        acordes=[
            [45, 48, 52, 55, 59],
            [43, 48, 52, 55, 59],
            [41, 45, 48, 52, 57],
            [40, 44, 47, 50, 56],
        ],
        bajo_patron=_BAJO_ROCK,
        ritmo_kick=_KICK_JEFE, ritmo_snare=_SNARE_JEFE, ritmo_hat=_HAT_JEFE,
        melodia_pasos=[
            (0, 69, 4), (4, 72, 2), (6, 76, 4), (10, 74, 2), (12, 72, 4),
            (16, 71, 4), (20, 74, 4), (24, 79, 4), (28, 76, 4),
            (32, 77, 4), (36, 76, 2), (38, 74, 2), (40, 72, 4), (44, 69, 4),
            (48, 68, 4), (52, 71, 4), (56, 76, 4), (60, 74, 4),
            (64, 81, 4), (68, 79, 2), (70, 77, 2), (72, 76, 4), (76, 72, 4),
            (80, 74, 4), (84, 76, 4), (88, 79, 4), (92, 76, 4),
            (96, 77, 4), (100, 76, 4), (104, 74, 4), (108, 72, 4),
            (112, 71, 4), (116, 74, 4), (120, 76, 4), (124, 68, 4),
        ],
    ),
    dict(
        nombre="custodio_f2",
        bpm=146, compases=8, swing=0.50, campana_en_1=True, overdrive_bajo=1.80,
        acordes=[
            [45, 48, 52, 56, 59],
            [46, 50, 53, 57, 60],
            [42, 45, 48, 51, 57],
            [40, 44, 47, 50, 56],
        ],
        bajo_patron=_BAJO_FURIA,
        ritmo_kick=_KICK_JEFE, ritmo_snare=_SNARE_JEFE, ritmo_hat=_HAT_JEFE,
        melodia_pasos=[
            (0, 81, 2), (2, 83, 2), (4, 84, 2), (6, 83, 2), (8, 81, 4), (12, 76, 4),
            (16, 77, 2), (18, 81, 2), (20, 82, 4), (24, 81, 4), (28, 77, 4),
            (32, 75, 4), (36, 78, 4), (40, 81, 4), (44, 78, 4),
            (48, 76, 4), (52, 80, 4), (56, 83, 4), (60, 80, 4),
            (64, 81, 2), (66, 76, 2), (68, 84, 4), (72, 83, 4), (76, 81, 4),
            (80, 82, 4), (84, 81, 4), (88, 77, 4), (92, 74, 4),
            (96, 75, 2), (98, 78, 2), (100, 81, 4), (104, 84, 4), (108, 81, 4),
            (112, 83, 4), (116, 80, 4), (120, 76, 4), (124, 74, 4),
        ],
    ),
    dict(
        nombre="custodio_f3",
        bpm=154, compases=8, swing=0.50, campana_en_1=True, overdrive_bajo=1.95,
        acordes=[
            [50, 53, 57, 61, 64],
            [49, 52, 55, 58, 64],
            [46, 50, 53, 57, 60],
            [45, 49, 52, 55, 58],
        ],
        bajo_patron=_BAJO_FURIA,
        ritmo_kick="x.x.x.x.x.x.x.x.",
        ritmo_snare="....X..g....X.XX",
        ritmo_hat=_HAT_JEFE,
        melodia_pasos=[
            (0, 74, 2), (2, 77, 2), (4, 81, 2), (6, 86, 4), (10, 85, 2), (12, 81, 4),
            (16, 79, 2), (18, 82, 2), (20, 85, 4), (24, 82, 4), (28, 79, 4),
            (32, 77, 4), (36, 81, 4), (40, 82, 4), (44, 86, 4),
            (48, 85, 4), (52, 81, 4), (56, 79, 4), (60, 76, 4),
            (64, 86, 2), (66, 85, 2), (68, 86, 4), (72, 89, 4), (76, 86, 4),
            (80, 85, 4), (84, 82, 4), (88, 79, 4), (92, 76, 4),
            (96, 77, 2), (98, 79, 2), (100, 81, 4), (104, 82, 4), (108, 84, 4),
            (112, 85, 4), (116, 81, 4), (120, 76, 4), (124, 73, 4),
        ],
    ),
    dict(
        nombre="creditos", bpm=92, compases=8, swing=0.56, campana_en_1=True,
        acordes=[
            [43, 46, 50, 53, 57],
            [51, 55, 58, 62, 65],
            [48, 51, 55, 58, 62],
            [50, 54, 57, 60, 66],
        ],
        bajo_patron=_BAJO_RNB,
        ritmo_kick=_KICK_RNB, ritmo_snare=_SNARE_RNB, ritmo_hat=_HAT_RNB,
        melodia_pasos=[
            (0, 67, 4), (4, 70, 4), (8, 74, 4), (12, 72, 4),
            (16, 70, 4), (20, 74, 4), (24, 75, 6), (30, 74, 2),
            (32, 72, 4), (36, 74, 4), (40, 75, 4), (44, 79, 4),
            (48, 78, 4), (52, 75, 4), (56, 74, 6), (62, 70, 2),
            (64, 74, 4), (68, 77, 4), (72, 79, 4), (76, 74, 4),
            (80, 75, 4), (84, 74, 4), (88, 72, 6), (94, 70, 2),
            (96, 68, 4), (100, 70, 4), (104, 72, 4), (108, 74, 4),
            (112, 75, 4), (116, 74, 4), (120, 71, 8),
        ],
    ),
    dict(
        nombre="victoria", bpm=112, compases=4, swing=0.50, en_bucle=False, campana_en_1=True,
        acordes=[
            [50, 54, 57, 61, 64],
            [47, 50, 54, 57, 61],
            [43, 47, 50, 54, 59],
            [50, 54, 57, 61, 66],
        ],
        bajo_patron=_BAJO_ROCK,
        ritmo_kick=_KICK_ROCK, ritmo_snare=_SNARE_ROCK, ritmo_hat=_HAT_ROCK,
        melodia_pasos=[
            (0, 69, 2), (2, 74, 4), (6, 78, 4), (10, 81, 6),
            (16, 79, 4), (20, 78, 4), (24, 76, 4), (28, 74, 4),
            (32, 71, 4), (36, 74, 4), (40, 78, 4), (44, 81, 4),
            (48, 86, 12),
        ],
    ),
    dict(
        nombre="derrota", bpm=82, compases=4, swing=0.52, en_bucle=False, campana_en_1=True,
        acordes=[
            [50, 53, 57, 60],
            [46, 50, 53, 57],
            [43, 46, 50, 53],
            [45, 49, 52, 57],
        ],
        bajo_patron=[
            0, None, None, None, None, None, None, None,
            7, None, None, None, 0, None, None, None,
        ],
        ritmo_kick="x.......x.......",
        ritmo_snare="........g.......",
        ritmo_hat="x...x...x...x...",
        melodia_pasos=[
            (0, 74, 6), (6, 72, 4), (10, 69, 6),
            (16, 70, 6), (22, 69, 4), (26, 67, 6),
            (32, 69, 6), (38, 67, 4), (42, 65, 6),
            (48, 64, 14),
        ],
    ),
)


def generar_todas_las_pistas():
    """Genera toda la banda sonora adaptada de IN CRYPTA."""
    for spec in ESPECIFICACIONES_PISTAS:
        ruta = secuenciar_tema(**spec)
        print(f"[SynthLab] Generada pista: {ruta.name} ({ruta.stat().st_size // 1024} KB)")


def generar_dron_ambiente() -> Path:
    """Genera un ambiente nocturno filtrado (brisa 320-960 Hz sin subgraves) en assets/audio/sfx/dron_catacumbas.ogg."""
    duracion = 12.0
    n = int(SR * duracion)
    rng = np.random.default_rng(1337)
    ruido_l = rng.standard_normal(n).astype(np.float64)
    ruido_r = rng.standard_normal(n).astype(np.float64)

    # Filtro espectral paso banda aireado (elimina todo < 220 Hz y > 1350 Hz para no competir con la música).
    freqs = np.fft.rfftfreq(n, 1.0 / SR)
    pasa_alto = 1.0 / (1.0 + (320.0 / np.maximum(freqs, 1.0)) ** 4)
    pasa_bajo = 1.0 / (1.0 + (freqs / 980.0) ** 3)
    mascara = pasa_alto * pasa_bajo
    mascara[freqs < 180.0] = 0.0

    brisa_l = np.fft.irfft(np.fft.rfft(ruido_l) * mascara, n=n)
    brisa_r = np.fft.irfft(np.fft.rfft(ruido_r) * mascara, n=n)

    t = np.arange(n, dtype=np.float64) / SR
    lfo_l = 0.62 + 0.38 * np.sin(2.0 * np.pi * (1.0 / duracion) * t)
    lfo_r = 0.62 + 0.38 * np.cos(2.0 * np.pi * (1.0 / duracion) * t)
    res_a = 0.015 * np.sin(2.0 * np.pi * 440.0 * t)
    res_e = 0.010 * np.sin(2.0 * np.pi * 659.25 * t)

    canal_l = brisa_l * lfo_l + res_a + res_e * lfo_r
    canal_r = brisa_r * lfo_r + res_a * 0.9 + res_e * lfo_l

    rms = float(np.sqrt(np.mean(0.5 * (canal_l ** 2 + canal_r ** 2)))) + 1e-12
    escala = 0.032 / rms
    estereo = np.stack([canal_l * escala, canal_r * escala], axis=1)
    estereo = np.clip(estereo, -0.35, 0.35)
    audio_i16 = (estereo * 32767.0).astype(np.int16)
    destino = RAIZ / "assets" / "audio" / "sfx" / "dron_catacumbas.ogg"
    return _exportar_ogg(audio_i16, destino)


if __name__ == "__main__":
    import sys

    if "--solo-dron" in sys.argv:
        ruta_dron = generar_dron_ambiente()
        print(f"[SynthLab] Generado dron limpio: {ruta_dron.name} ({ruta_dron.stat().st_size // 1024} KB)")
    else:
        generar_todas_las_pistas()
        ruta_dron = generar_dron_ambiente()
        print(f"[SynthLab] Generado dron limpio: {ruta_dron.name} ({ruta_dron.stat().st_size // 1024} KB)")
