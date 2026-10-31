# ============================================================
# audio.py — Sonidos procedurales de IN CRYPTA
# ============================================================
# No hay archivos de audio externos: cada efecto se genera como
# una onda corta. Así el proyecto queda autocontenido y liviano.
# ============================================================

import array
import math
import random

import pygame


FRECUENCIA_MUESTREO = 22050


# --- Función crear_tono --- #
def crear_tono(frecuencia, duracion, volumen=0.25, forma="seno", barrido=0.0):
    cantidad = int(FRECUENCIA_MUESTREO * duracion)
    muestras = array.array("h")
    fase = 0.0

    for i in range(cantidad):
        t = i / FRECUENCIA_MUESTREO
        progreso = i / max(1, cantidad - 1)
        frecuencia_actual = frecuencia + barrido * progreso
        fase += math.tau * frecuencia_actual / FRECUENCIA_MUESTREO

        if forma == "cuadrada":
            onda = 1.0 if math.sin(fase) >= 0 else -1.0
        elif forma == "sierra":
            onda = 2.0 * ((fase / math.tau) % 1.0) - 1.0
        elif forma == "ruido":
            onda = random.uniform(-1.0, 1.0)
        else:
            onda = math.sin(fase)

        ataque = min(1.0, progreso / 0.08)
        caida = max(0.0, 1.0 - progreso)
        envolvente = ataque * (caida ** 1.8)
        valor = int(32767 * volumen * envolvente * onda)
        muestras.append(max(-32768, min(32767, valor)))

    return pygame.mixer.Sound(buffer=muestras.tobytes())


# --- Clase Audio --- #
class Audio:
    def __init__(self):
        self.activo = False
        self.sonidos = {}
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(
                    frequency=FRECUENCIA_MUESTREO,
                    size=-16,
                    channels=1,
                    buffer=512,
                )
            self.sonidos = {
                "salto": crear_tono(230, 0.14, 0.18, "seno", 140),
                "alma": crear_tono(660, 0.22, 0.16, "seno", 220),
                "alma_1": crear_tono(523, 0.18, 0.16, "seno", 140),
                "alma_2": crear_tono(587, 0.18, 0.16, "seno", 160),
                "alma_3": crear_tono(659, 0.19, 0.16, "seno", 180),
                "alma_4": crear_tono(784, 0.20, 0.16, "seno", 220),
                "alma_5": crear_tono(880, 0.22, 0.17, "seno", 250),
                "alma_6": crear_tono(1046, 0.24, 0.18, "seno", 300),
                "dash": crear_tono(150, 0.18, 0.16, "sierra", 380),
                "ataque": crear_tono(280, 0.10, 0.16, "sierra", 520),
                "pala": crear_tono(95, 0.20, 0.26, "ruido", -40),
                "stomp": crear_tono(135, 0.18, 0.25, "ruido", -60),
                "onda": crear_tono(70, 0.42, 0.24, "ruido", 90),
                "jefe_aviso": crear_tono(190, 0.28, 0.15, "cuadrada", -55),
                "jefe_fase": crear_tono(110, 0.55, 0.22, "cuadrada", -35),
                "pala_recoger": crear_tono(620, 0.18, 0.14, "cuadrada", 180),
                "vida_extra": crear_tono(740, 0.42, 0.18, "seno", 520),
                "ui": crear_tono(420, 0.06, 0.10, "cuadrada", -40),
                "daño": crear_tono(160, 0.26, 0.22, "cuadrada", -90),
                "muerte": crear_tono(75, 0.65, 0.26, "cuadrada", -40),
                "meta": crear_tono(220, 0.55, 0.20, "seno", 260),
            }
            self.activo = True
        except pygame.error:
            self.activo = False

    # --- Función reproducir --- #
    def reproducir(self, nombre):
        if not self.activo:
            return
        sonido = self.sonidos.get(nombre)
        if sonido is not None:
            sonido.play()

    # --- Función alternar --- #
    def alternar(self):
        self.activo = not self.activo
