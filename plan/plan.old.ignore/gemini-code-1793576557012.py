import math
import struct
import numpy as np

SAMPLE_RATE = 44100

def generar_onda_cuadrada(freq, duracion, duty=0.5, volumen=0.3):
    num_samples = int(SAMPLE_RATE * duracion)
    t = np.linspace(0, duracion, num_samples, False)
    fase = np.mod(t * freq, 1.0)
    onda = np.where(fase < duty, volumen, -volumen)
    # Envolvente suave de ataque y caida (ADSR simplificado)
    env = np.ones(num_samples)
    attack = int(SAMPLE_RATE * 0.01)
    release = int(SAMPLE_RATE * 0.02)
    if attack > 0: env[:attack] = np.linspace(0, 1, attack)
    if release > 0: env[-release:] = np.linspace(1, 0, release)
    return onda * env

def generar_onda_triangular(freq, duracion, volumen=0.4):
    num_samples = int(SAMPLE_RATE * duracion)
    t = np.linspace(0, duracion, num_samples, False)
    fase = np.mod(t * freq, 1.0)
    onda = volumen * (2.0 * np.abs(2.0 * (fase - np.floor(fase + 0.5))) - 1.0)
    return onda

def generar_ruido_percusivo(duracion, volumen=0.2, decaimiento=15.0):
    num_samples = int(SAMPLE_RATE * duracion)
    ruido = np.random.uniform(-volumen, volumen, num_samples)
    t = np.linspace(0, duracion, num_samples, False)
    envolvente = np.exp(-decaimiento * t)
    return ruido * envolvente