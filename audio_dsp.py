#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audio_dsp.py — Motor de Procesamiento Digital de Señales (DSP) para IN CRYPTA Commercial Edition.
================================================================================================
Implementa efectos acústicos en tiempo real sobre NumPy y SciPy:
  1. Reverberación algorítmica de catedral gótica tipo Schroeder / Comb-Allpass con retardos
     en números primos (37 ms, 73 ms, 113 ms).
  2. Filtro paso-bajo Butterworth reactivo a la agonía del Sepulturero (1 HP restante).
  3. Generador de armónicos y micro-chorus estéreo para los Chimes pentatónicos de almas.
  4. Fallback suave a buffers nativos de pygame.mixer si NumPy/SciPy no estuvieran disponibles.
"""

from __future__ import annotations
import math
from typing import Optional, Tuple

try:
    import numpy as np
    from scipy import signal
    HAS_SCIPY_DSP = True
except ImportError:
    HAS_SCIPY_DSP = False
    np = None
    signal = None


class MotorAudioDSP:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.disponible = HAS_SCIPY_DSP

        # Tiempos de retardo primos (en muestras a 44.1 kHz) para evitar resonancias armónicas
        self.retardos_primos_ms = (37, 73, 113)
        self._comb_buffers = []
        if self.disponible:
            for ms in self.retardos_primos_ms:
                muestras = int(self.sample_rate * (ms / 1000.0))
                self._comb_buffers.append(np.zeros(muestras, dtype=np.float32))

    def aplicar_reverb_catedral(
        self,
        audio_array: np.ndarray,
        decay: float = 0.55,
        mezcla_wet: float = 0.35,
    ) -> np.ndarray:
        """
        Aplica convolución por filtros peine paralelos (Schroeder) emulando
        las reflexiones acústicas de una catedral / nave gótica subterránea.
        """
        if not self.disponible or audio_array is None or len(audio_array) == 0:
            return audio_array

        audio_float = audio_array.astype(np.float32)
        n = len(audio_float)
        salida_reverb = np.zeros_like(audio_float)

        # Filtros peine (comb filters) en paralelo
        for ms in self.retardos_primos_ms:
            delay_samples = int(self.sample_rate * (ms / 1000.0))
            if delay_samples >= n:
                continue
            # IIR Comb filter: y[n] = x[n] + decay * y[n - delay]
            b = np.zeros(delay_samples + 1, dtype=np.float32)
            b[0] = 1.0
            a = np.zeros(delay_samples + 1, dtype=np.float32)
            a[0] = 1.0
            a[-1] = -decay
            canal_filtrado = signal.lfilter(b, a, audio_float, axis=0)
            salida_reverb += canal_filtrado

        salida_reverb = (salida_reverb / len(self.retardos_primos_ms)) * mezcla_wet
        resultado = (1.0 - mezcla_wet) * audio_float + salida_reverb
        return np.clip(resultado, -32767.0, 32767.0).astype(audio_array.dtype)

    def filtro_paso_bajo_agonia(
        self,
        audio_array: np.ndarray,
        frecuencia_corte_hz: float = 850.0,
        orden: int = 4,
    ) -> np.ndarray:
        """
        Filtro Butterworth reactivo cuando el jugador está a 1 punto de vida (efecto asfixia/túnel auditivo).
        """
        if not self.disponible or audio_array is None or len(audio_array) == 0:
            return audio_array

        nyquist = 0.5 * self.sample_rate
        norm_corte = min(0.95, frecuencia_corte_hz / nyquist)
        b, a = signal.butter(orden, norm_corte, btype='low', analog=False)
        audio_filtrado = signal.lfilter(b, a, audio_array.astype(np.float32), axis=0)
        return np.clip(audio_filtrado, -32767.0, 32767.0).astype(audio_array.dtype)

    def generar_chime_estereo_gotico(
        self,
        frecuencia_hz: float,
        duracion_s: float = 0.45,
        decay_s: float = 0.35,
        stereo_spread_hz: float = 2.5,
    ) -> Optional[np.ndarray]:
        """
        Sintetiza un chime procedural estéreo con armónicos acampanados y batimiento microtonal.
        """
        if not self.disponible:
            return None

        total_samples = int(self.sample_rate * duracion_s)
        t = np.linspace(0, duracion_s, total_samples, endpoint=False, dtype=np.float32)
        envolvente = np.exp(-t / max(0.01, decay_s))

        # Canal Izquierdo (frecuencia ligeramente más baja)
        onda_l = (
            0.60 * np.sin(2.0 * np.pi * (frecuencia_hz - stereo_spread_hz) * t) +
            0.25 * np.sin(2.0 * np.pi * (frecuencia_hz * 2.0) * t) +
            0.15 * np.sin(2.0 * np.pi * (frecuencia_hz * 3.0) * t)
        ) * envolvente

        # Canal Derecho (frecuencia ligeramente más alta)
        onda_r = (
            0.60 * np.sin(2.0 * np.pi * (frecuencia_hz + stereo_spread_hz) * t) +
            0.25 * np.sin(2.0 * np.pi * (frecuencia_hz * 2.005) * t) +
            0.15 * np.sin(2.0 * np.pi * (frecuencia_hz * 3.01) * t)
        ) * envolvente

        estereo = np.column_stack((onda_l, onda_r)) * 32767.0 * 0.75
        return np.clip(estereo, -32767.0, 32767.0).astype(np.int16)
