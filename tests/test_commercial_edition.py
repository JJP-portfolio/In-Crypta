#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_commercial_edition.py — Pruebas unitarias de los módulos comerciales NextGen.
"""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import numpy as np
from audio_dsp import MotorAudioDSP
from gpu_pipeline import PipelineGPU
from fisica_decorativa import SimuladorFisicaDecorativa, CadenaVerlet


def test_motor_dsp_chimes_y_reverb():
    dsp = MotorAudioDSP(sample_rate=44100)
    assert dsp.disponible is True

    # Generación de chime estéreo C5 (523 Hz)
    chime = dsp.generar_chime_estereo_gotico(523.25, duracion_s=0.2, decay_s=0.15)
    assert chime is not None
    assert chime.shape[1] == 2  # Estéreo (L, R)
    assert chime.dtype == np.int16

    # Aplicación de reverberación de catedral
    reverb = dsp.aplicar_reverb_catedral(chime, decay=0.5, mezcla_wet=0.3)
    assert reverb.shape == chime.shape
    assert reverb.dtype == np.int16

    # Filtro paso-bajo de agonía
    filtrado = dsp.filtro_paso_bajo_agonia(chime, frecuencia_corte_hz=800.0)
    assert filtrado.shape == chime.shape


def test_gpu_pipeline_fallback_seguro():
    pygame.init()
    surf_origen = pygame.Surface((1280, 720))
    surf_destino = pygame.Surface((1280, 720))
    pipeline = PipelineGPU(1280, 720)

    # Debe ejecutarse sin lanzar excepciones tanto con ModernGL activo como en fallback
    pipeline.renderizar_cuadro(surf_origen, surf_destino, tiempo=1.0, aberracion=0.002)


def test_fisica_decorativa_verlet_e_impulso():
    pygame.init()
    sim = SimuladorFisicaDecorativa()
    cadena = sim.crear_cadena(100.0, 50.0, eslabones=5)
    assert len(cadena.eslabones) == 5

    # Simular 10 frames
    for _ in range(10):
        sim.actualizar(1.0 / 60.0)

    # Reacción a onda expansiva
    sim.reaccionar_onda_expansiva(x_onda=90.0, y_onda=50.0, radio=100.0, fuerza=10.0)
    sim.actualizar(1.0 / 60.0)

    # Comprobar dibujo a superficie dummy
    pantalla = pygame.Surface((320, 240))
    sim.dibujar(pantalla, camara_x=0.0, camara_y=0.0)
