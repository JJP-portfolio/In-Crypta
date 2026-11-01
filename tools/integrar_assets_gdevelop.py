#!/usr/bin/env python3
"""tools/integrar_assets_gdevelop.py — Integrador de Assets Pixel-Art Góticos para GDevelop 5.6.

Prioridad 5:
1. Genera frames Pixel-Art góticos en alta definición (1x en `assets_pixelart/` y 2x en `export/gdevelop_nativo/assets/`).
   - Jugador (32x32): Idle (4 frames), Run (6 frames), Jump (2 frames), Caida (2 frames), Dash (3 frames), Ataque (3 frames).
   - Variantes del Jugador: dirección izquierda (_izq) y sin pala (_sin_pala).
   - Enemigos (26x26): Enemy (4 frames walk), EnemyMelee (4 frames walk).
   - MiniJefe (36x48): El Carcelero del Osario (4 frames walk).
   - Jefe (48x64): El Custodio de la Cripta (4 frames hover/walk).
   - Alma (24x24): 4 frames levitando.
   - FarolCheckpoint (20x30): 1 frame apagado, 4 frames encendido (fuego azul crepitando).
   - PowerUps (20x30): PowerUpDash (4 frames), PowerUpRango (4 frames), PalaRecogible (4 frames).
   - Elementos de combate y entorno: Pinchos, Puerta, Sólido, GolpePala (6 frames), OndaJefe.
2. Paleta gótica canónica estricta:
   - Obsidian:        #09080d  (9, 8, 13)
   - Crypt Stone:     #3a3d48  (58, 61, 72)
   - Moss:            #485e3e  (72, 94, 62)
   - Bone:            #d7cfb8  (215, 207, 184)
   - Crimson:         #8e202c  (142, 32, 44)
   - Anima Turquoise: #5cbeae  (92, 190, 174)
   - Liturgic Gold:   #c69c3e  (198, 156, 62)
3. Mantiene el 100% de paridad en las proporciones y cajas de colisión para no alterar
   físicas ni saltos (ratio 1.0 para jugador/enemigos/almas, 0.667 para faroles/powerups, 0.75 para jefes).
4. Actualiza `IN_CRYPTA_NATIVO.json` e `In_Crypta_V0.9.9.json` con:
   - "scaleMode": "nearest" en propiedades.
   - "smoothed": False en todos los recursos de imagen.
   - Registro de todos los recursos standalone PNG.
   - Configuración de animaciones multipose con tiempos y loops exactos.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parent.parent
DIR_PIXELART = ROOT / "assets_pixelart"
DIR_GDEVELOP = ROOT / "export" / "gdevelop_nativo"
DIR_ASSETS = DIR_GDEVELOP / "assets"
PROYECTO_JSON = DIR_GDEVELOP / "IN_CRYPTA_NATIVO.json"
PROYECTO_SYNC = DIR_GDEVELOP / "In_Crypta_V0.9.9.json"

# ============================================================
# Paleta Gótica Auténtica
# ============================================================
OBSIDIAN_DEEP     = (9, 8, 13)       # #09080d - Tinta negra/contornos
OBSIDIAN_MID      = (22, 20, 31)     # #16141f - Sombras profundas
CRYPT_STONE_DARK  = (40, 42, 52)     # #282a34 - Pizarra oscura
CRYPT_STONE       = (58, 61, 72)     # #3a3d48 - Piedra de cripta
CRYPT_STONE_LIGHT = (99, 107, 127)   # #636b7f - Destello de piedra/hierro
MOSS_DARK         = (39, 59, 34)     # #273b22 - Musgo de cripta profundo
MOSS              = (72, 94, 62)     # #485e3e - Musgo de cementerio
MOSS_LIGHT        = (103, 131, 89)   # #678359 - Musgo iluminado
BONE_SHADOW       = (155, 141, 120)  # #9b8d78 - Hueso envejecido sombra
BONE              = (215, 207, 184)  # #d7cfb8 - Hueso antiguo / pergamino
BONE_LIGHT        = (236, 228, 208)  # #ece4d0 - Hueso blanqueado / filo
CRIMSON_DARK      = (79, 17, 24)     # #4f1118 - Sangre coagulada / sombra
CRIMSON           = (142, 32, 44)    # #8e202c - Carmesí litúrgico
CRIMSON_BRIGHT    = (196, 51, 67)    # #c43343 - Carmesí vivo / ojos
ANIMA_DARK        = (40, 107, 102)   # #286b66 - Éter espectral sombra
ANIMA_TURQUOISE   = (92, 190, 174)   # #5cbeae - Turquesa de ánima
ANIMA_LIGHT       = (168, 235, 217)  # #a8ebd9 - Núcleo espectral brillante
GOLD_DARK         = (115, 81, 24)    # #735118 - Oro antiguo sombra
LITURGIC_GOLD     = (198, 156, 62)   # #c69c3e - Oro litúrgico
GOLD_LIGHT        = (245, 213, 110)  # #f5d56e - Destello sagrado
WOOD_DARK         = (48, 30, 20)     # Madera vieja de mango de pala
WOOD_MID          = (78, 52, 34)     # Madera veteada


def _surf(ancho: int, alto: int) -> pygame.Surface:
    """Superficie RGBA transparente nativa."""
    return pygame.Surface((ancho, alto), pygame.SRCALPHA)


def _rect(s: pygame.Surface, x: int, y: int, w: int, h: int, color: tuple) -> None:
    pygame.draw.rect(s, color, (x, y, w, h))


def _pixel(s: pygame.Surface, x: int, y: int, color: tuple) -> None:
    if 0 <= x < s.get_width() and 0 <= y < s.get_height():
        s.set_at((x, y), color)


# ============================================================
# 1. RENDERIZADORES DE JUGADOR (Sepulturero de la Cripta, 32x32)
# ============================================================
def render_jugador_base(
    pose: str = "idle",
    frame: int = 0,
    con_pala: bool = True,
    es_guadana: bool = False,
) -> pygame.Surface:
    """Renderiza un frame 32x32 pixel-art del Sepulturero."""
    s = _surf(32, 32)

    # Offset vertical según pose/respiración
    dy = 0
    dx = 0
    falda_drift = 0
    pierna_l = 0
    pierna_r = 0
    brazo_ang = 0

    if pose == "idle":
        # Ciclo de respiración (4 frames)
        if frame == 1:
            dy = -1
        elif frame == 2:
            dy = -1
            falda_drift = 1
        elif frame == 3:
            dy = 0
            falda_drift = 0
    elif pose == "run":
        # Ciclo de zancada (6 frames)
        dx = 1
        if frame == 0:
            pierna_r, pierna_l = 4, -4
            falda_drift = -2
        elif frame == 1:
            dy = 1
            pierna_r, pierna_l = 2, -2
            falda_drift = -3
        elif frame == 2:
            pierna_r, pierna_l = -1, 1
            falda_drift = -2
        elif frame == 3:
            pierna_r, pierna_l = -4, 4
            falda_drift = -2
        elif frame == 4:
            dy = 1
            pierna_r, pierna_l = -2, 2
            falda_drift = -3
        elif frame == 5:
            pierna_r, pierna_l = 1, -1
            falda_drift = -2
    elif pose == "jump":
        # Ascenso (2 frames)
        if frame == 0:
            dy = -2
            pierna_r, pierna_l = -2, -2
            falda_drift = -1
        else:
            dy = -1
            pierna_r, pierna_l = 1, 1
            falda_drift = 0
    elif pose == "caida":
        # Caída (2 frames): abrigo ondeando hacia arriba
        if frame == 0:
            dy = 0
            pierna_r, pierna_l = 2, 2
            falda_drift = 2
        else:
            dy = 1
            pierna_r, pierna_l = 3, 3
            falda_drift = 3
    elif pose == "dash":
        # Dash horizontal rasante (3 frames)
        dx = 2
        dy = 2
        falda_drift = -5
        # Ghosting turquesa detrás
        ghost_color = (*ANIMA_TURQUOISE[:3], 90 - frame * 25)
        _rect(s, 4 - frame * 3, 16 + dy, 14, 10, ghost_color)
        _rect(s, 6 - frame * 3, 11 + dy, 8, 7, ghost_color)
    elif pose == "ataque":
        # Ataque con pala/guadaña (3 frames)
        if frame == 0:
            dx = -1
            dy = 0
            brazo_ang = -1
        elif frame == 1:
            dx = 3
            dy = 1
            brazo_ang = 1
            falda_drift = -2
        elif frame == 2:
            dx = 1
            dy = 0
            brazo_ang = 2

    # Sombra de contacto en suelo
    if pose != "jump" and pose != "caida":
        _rect(s, 10 + dx, 30, 12, 2, OBSIDIAN_DEEP)

    # 1. Piernas y botas
    y_pie = 27 + dy
    # Bota izquierda
    _rect(s, 11 + dx + pierna_l, y_pie, 3, 4, OBSIDIAN_MID)
    _pixel(s, 10 + dx + pierna_l, y_pie + 3, OBSIDIAN_DEEP)
    _pixel(s, 13 + dx + pierna_l, y_pie + 3, OBSIDIAN_DEEP)
    # Bota derecha
    _rect(s, 17 + dx + pierna_r, y_pie, 3, 4, OBSIDIAN_MID)
    _pixel(s, 16 + dx + pierna_r, y_pie + 3, OBSIDIAN_DEEP)
    _pixel(s, 19 + dx + pierna_r, y_pie + 3, OBSIDIAN_DEEP)

    # 2. Abrigo largo andrajoso (Cuerpo y falda)
    y_cuerpo = 14 + dy
    # Falda inferior andrajosa
    for fx in range(9 + dx + falda_drift, 22 + dx):
        alt = 7 if (fx % 2 == 0) else 8
        if pose == "caida":
            alt = 5  # Falda vuela hacia arriba
        _rect(s, fx, y_cuerpo + 6, 1, alt, OBSIDIAN_MID)
    # Contorno andrajoso inferior
    _pixel(s, 9 + dx + falda_drift, y_cuerpo + 12, OBSIDIAN_DEEP)
    _pixel(s, 12 + dx + falda_drift // 2, y_cuerpo + 14, OBSIDIAN_DEEP)
    _pixel(s, 16 + dx, y_cuerpo + 13, OBSIDIAN_DEEP)
    _pixel(s, 20 + dx, y_cuerpo + 14, OBSIDIAN_DEEP)

    # Torso del abrigo
    _rect(s, 11 + dx, y_cuerpo, 9, 8, CRYPT_STONE_DARK)
    _rect(s, 12 + dx, y_cuerpo + 1, 7, 7, OBSIDIAN_MID)
    # Cinturón con hebilla de oro litúrgico
    _rect(s, 11 + dx, y_cuerpo + 6, 9, 2, WOOD_DARK)
    _pixel(s, 15 + dx, y_cuerpo + 6, LITURGIC_GOLD)
    _pixel(s, 15 + dx, y_cuerpo + 7, GOLD_LIGHT)

    # 3. Bufanda / Estola carmesí litúrgica
    y_cuello = 11 + dy
    _rect(s, 12 + dx, y_cuello + 1, 8, 3, CRIMSON)
    _rect(s, 11 + dx, y_cuello + 2, 2, 4, CRIMSON_DARK)
    if pose == "run" or pose == "dash":
        _rect(s, 7 + dx, y_cuello + 1, 4, 2, CRIMSON)
        _pixel(s, 6 + dx, y_cuello + 2, CRIMSON_DARK)
    elif pose == "caida":
        _rect(s, 10 + dx, y_cuello - 2, 2, 4, CRIMSON)
    else:
        _pixel(s, 10 + dx, y_cuello + 4, CRIMSON_DARK)

    # 4. Cabeza, rostro en penumbra y ojos luminosos
    y_cabeza = 5 + dy
    # Silueta de cabeza
    _rect(s, 12 + dx, y_cabeza + 3, 7, 6, OBSIDIAN_MID)
    # Sombra profunda en rostro
    _rect(s, 13 + dx, y_cabeza + 4, 6, 4, OBSIDIAN_DEEP)
    # Ojos fulgurando en turquesa de ánima
    _pixel(s, 17 + dx, y_cabeza + 6, ANIMA_LIGHT)
    _pixel(s, 18 + dx, y_cabeza + 6, ANIMA_TURQUOISE)
    _pixel(s, 14 + dx, y_cabeza + 6, ANIMA_TURQUOISE)

    # 5. Sombrero de ala ancha caído
    y_sombrero = y_cabeza
    # Copa
    _rect(s, 12 + dx, y_sombrero, 7, 4, OBSIDIAN_MID)
    _rect(s, 13 + dx, y_sombrero - 1, 5, 2, CRYPT_STONE_DARK)
    # Cinta carmesí
    _rect(s, 12 + dx, y_sombrero + 3, 7, 1, CRIMSON)
    # Ala ancha curvada
    _rect(s, 8 + dx, y_sombrero + 4, 15, 2, OBSIDIAN_DEEP)
    _pixel(s, 7 + dx, y_sombrero + 5, OBSIDIAN_DEEP)
    _pixel(s, 23 + dx, y_sombrero + 5, OBSIDIAN_DEEP)

    # 6. Pala o Guadaña
    if con_pala:
        if pose == "ataque":
            if frame == 0:
                # Pala alzada hacia atrás lista para golpear
                pygame.draw.line(s, WOOD_MID, (13 + dx, y_cuello + 1), (6 + dx, 5 + dy), 2)
                # Hoja de hierro plateada
                _rect(s, 3 + dx, 2 + dy, 5, 5, CRYPT_STONE_LIGHT)
                _rect(s, 4 + dx, 3 + dy, 3, 3, BONE_LIGHT)
                _pixel(s, 5 + dx, 1 + dy, LITURGIC_GOLD)
            elif frame == 1:
                # Golpe tajante al frente con arco de energía
                pygame.draw.line(s, WOOD_MID, (15 + dx, y_cuello + 2), (26 + dx, 16 + dy), 2)
                # Hoja frontal
                _rect(s, 24 + dx, 14 + dy, 6, 6, CRYPT_STONE_LIGHT)
                _rect(s, 25 + dx, 15 + dy, 4, 4, BONE_LIGHT)
                _pixel(s, 29 + dx, 17 + dy, LITURGIC_GOLD)
                # Gran estela de corte semicircular
                puntos_arco = [
                    (20 + dx, 6 + dy),
                    (27 + dx, 9 + dy),
                    (31 + dx, 16 + dy),
                    (29 + dx, 24 + dy),
                    (23 + dx, 28 + dy),
                ]
                pygame.draw.lines(s, BONE_LIGHT, False, puntos_arco, 2)
                for px, py in puntos_arco:
                    _pixel(s, px - 1, py, LITURGIC_GOLD)
                    _pixel(s, px + 1, py, ANIMA_LIGHT)
            elif frame == 2:
                # Pala abajo en recuperación
                pygame.draw.line(s, WOOD_MID, (16 + dx, y_cuello + 3), (25 + dx, 26 + dy), 2)
                _rect(s, 24 + dx, 24 + dy, 5, 5, CRYPT_STONE_LIGHT)
                _rect(s, 25 + dx, 25 + dy, 3, 3, BONE)
                _pixel(s, 28 + dx, 27 + dy, LITURGIC_GOLD)
        else:
            # Pala portada al hombro o en mano
            x_mango = 18 + dx
            pygame.draw.line(s, WOOD_MID, (x_mango, y_cuerpo + 2), (x_mango - 4, y_cuerpo + 14), 2)
            # Hoja en la espalda
            _rect(s, x_mango - 6, y_cuerpo + 10, 5, 5, CRYPT_STONE_LIGHT)
            _rect(s, x_mango - 5, y_cuerpo + 11, 3, 3, BONE)
            # Cruz de oro litúrgico en el pomo
            _pixel(s, x_mango + 1, y_cuerpo + 1, LITURGIC_GOLD)
            _pixel(s, x_mango, y_cuerpo, GOLD_LIGHT)
            _pixel(s, x_mango + 2, y_cuerpo + 1, LITURGIC_GOLD)
    else:
        # Sin pala: mano libre sosteniendo un pequeño farol de ánima
        x_mano = 20 + dx
        y_mano = y_cuerpo + 4
        _pixel(s, x_mano, y_mano, BONE)
        # Farolito de mano
        _rect(s, x_mano - 1, y_mano + 2, 4, 5, CRYPT_STONE_DARK)
        _pixel(s, x_mano, y_mano + 3, ANIMA_LIGHT)
        _pixel(s, x_mano + 1, y_mano + 4, ANIMA_TURQUOISE)

    return s


# ============================================================
# 2. RENDERIZADORES DE ENEMIGOS
# ============================================================
def render_enemigo(frame: int = 0) -> pygame.Surface:
    """Enemigo patrullero básico (Crawler / Esqueleto gótico, 26x26)."""
    s = _surf(26, 26)
    dy = -1 if frame % 2 == 1 else 0
    p1 = 3 if frame in (0, 1) else -3
    p2 = -p1

    # Sombra
    _rect(s, 6, 24, 14, 2, OBSIDIAN_DEEP)

    # Piernas esqueléticas
    _rect(s, 8 + p1, 17 + dy, 2, 7, BONE_SHADOW)
    _rect(s, 15 + p2, 17 + dy, 2, 7, BONE_SHADOW)
    # Grillete de hierro oxidado en tobillo
    _pixel(s, 8 + p1, 22 + dy, CRYPT_STONE_DARK)

    # Caja torácica y columna
    _rect(s, 9, 11 + dy, 8, 7, BONE)
    # Espacios entre costillas
    _pixel(s, 11, 13 + dy, OBSIDIAN_DEEP)
    _pixel(s, 14, 13 + dy, OBSIDIAN_DEEP)
    _pixel(s, 11, 15 + dy, OBSIDIAN_DEEP)
    _pixel(s, 14, 15 + dy, OBSIDIAN_DEEP)
    # Hombros con musgo de cripta
    _pixel(s, 8, 11 + dy, MOSS)
    _pixel(s, 17, 11 + dy, MOSS_DARK)

    # Garras óseas
    _rect(s, 6, 13 + dy, 3, 5, BONE_SHADOW)
    _pixel(s, 5, 17 + dy, OBSIDIAN_DEEP)
    _rect(s, 17, 13 + dy, 3, 5, BONE_SHADOW)
    _pixel(s, 20, 17 + dy, OBSIDIAN_DEEP)

    # Calavera antigua con cuerno astillado
    _rect(s, 9, 3 + dy, 8, 8, BONE)
    _rect(s, 10, 2 + dy, 6, 2, BONE_LIGHT)
    # Cuerno de hueso
    _pixel(s, 8, 2 + dy, BONE_SHADOW)
    _pixel(s, 7, 1 + dy, BONE)
    # Cuencas vacías con fuego carmesí
    _rect(s, 11, 6 + dy, 2, 3, OBSIDIAN_DEEP)
    _rect(s, 15, 6 + dy, 2, 3, OBSIDIAN_DEEP)
    _pixel(s, 12, 7 + dy, CRIMSON_BRIGHT)
    _pixel(s, 16, 7 + dy, CRIMSON_BRIGHT)
    # Dientes
    _pixel(s, 11, 10 + dy, BONE_LIGHT)
    _pixel(s, 13, 10 + dy, BONE_LIGHT)
    _pixel(s, 15, 10 + dy, BONE_LIGHT)

    return s


def render_enemigo_melee(frame: int = 0) -> pygame.Surface:
    """Enemigo Melee (Caballero de la Cripta / Ejecutor, 26x26)."""
    s = _surf(26, 26)
    dy = -1 if frame % 2 == 1 else 0
    stride = 3 if frame in (0, 1) else -2

    # Sombra
    _rect(s, 5, 24, 16, 2, OBSIDIAN_DEEP)

    # Capa rasgada carmesí
    _rect(s, 4, 12 + dy, 5, 10, CRIMSON_DARK)
    _pixel(s, 3, 19 + dy, CRIMSON)

    # Piernas blindadas
    _rect(s, 8 + stride, 17 + dy, 4, 7, CRYPT_STONE_DARK)
    _rect(s, 14 - stride, 17 + dy, 4, 7, CRYPT_STONE_DARK)

    # Coraza de hierro pizarra
    _rect(s, 8, 10 + dy, 10, 8, CRYPT_STONE)
    _rect(s, 9, 11 + dy, 8, 6, CRYPT_STONE_LIGHT)
    _pixel(s, 13, 13 + dy, LITURGIC_GOLD)

    # Yelmo con hendidura y cuernos de hierro
    _rect(s, 9, 3 + dy, 8, 7, CRYPT_STONE_DARK)
    _rect(s, 10, 2 + dy, 6, 2, CRYPT_STONE)
    # Cuernos del yelmo
    _pixel(s, 8, 2 + dy, CRYPT_STONE_LIGHT)
    _pixel(s, 17, 2 + dy, CRYPT_STONE_LIGHT)
    # Visor carmesí
    _rect(s, 11, 6 + dy, 5, 2, CRIMSON_BRIGHT)

    # Gran espada de ejecutor mellada
    y_espada = 5 + dy if frame in (0, 2) else 8 + dy
    pygame.draw.line(s, BONE_LIGHT, (20, y_espada), (20, y_espada + 15), 3)
    _pixel(s, 20, y_espada, LITURGIC_GOLD)
    _pixel(s, 19, y_espada + 10, CRIMSON_DARK)  # Mancha de sangre
    _pixel(s, 21, y_espada + 14, CRIMSON_DARK)

    return s


def render_minijefe(frame: int = 0) -> pygame.Surface:
    """MiniJefe: El Carcelero del Osario (36x48)."""
    s = _surf(36, 48)
    dy = -1 if frame % 2 == 1 else 0
    st = 4 if frame in (0, 1) else -4

    # Sombra
    _rect(s, 6, 45, 24, 3, OBSIDIAN_DEEP)

    # Piernas acorazadas macizas
    _rect(s, 10 + st, 32 + dy, 6, 14, CRYPT_STONE_DARK)
    _rect(s, 20 - st, 32 + dy, 6, 14, CRYPT_STONE_DARK)

    # Faldón de cadenas y calaveras
    _rect(s, 8, 26 + dy, 20, 8, OBSIDIAN_MID)
    for cx in (10, 14, 18, 22, 26):
        _pixel(s, cx, 33 + dy, BONE_SHADOW)
        _pixel(s, cx, 34 + dy, BONE)

    # Torso colosal con cadenas cruzadas
    _rect(s, 8, 14 + dy, 20, 14, CRYPT_STONE)
    _rect(s, 10, 15 + dy, 16, 12, CRYPT_STONE_LIGHT)
    # Cadenas de hierro cruzadas
    pygame.draw.line(s, OBSIDIAN_DEEP, (9, 15 + dy), (26, 27 + dy), 2)
    pygame.draw.line(s, OBSIDIAN_DEEP, (26, 15 + dy), (9, 27 + dy), 2)

    # Hombreras con púas de hueso
    _rect(s, 4, 12 + dy, 6, 6, CRYPT_STONE_DARK)
    _pixel(s, 4, 10 + dy, BONE_LIGHT)
    _pixel(s, 6, 9 + dy, BONE_LIGHT)
    _rect(s, 26, 12 + dy, 6, 6, CRYPT_STONE_DARK)
    _pixel(s, 29, 9 + dy, BONE_LIGHT)
    _pixel(s, 31, 10 + dy, BONE_LIGHT)

    # Máscara de jaula de hierro
    _rect(s, 12, 4 + dy, 12, 10, CRYPT_STONE_DARK)
    # Barrotes
    for bx in (14, 17, 20):
        _rect(s, bx, 5 + dy, 1, 9, CRYPT_STONE_LIGHT)
    # Ojos al rojo vivo en la penumbra
    _pixel(s, 15, 8 + dy, CRIMSON_BRIGHT)
    _pixel(s, 19, 8 + dy, CRIMSON_BRIGHT)

    # Cuchilla de verdugo ensangrentada
    _rect(s, 28, 8 + dy, 7, 26, CRYPT_STONE_LIGHT)
    _rect(s, 29, 9 + dy, 5, 24, BONE_LIGHT)
    _rect(s, 30, 20 + dy, 4, 10, CRIMSON)

    return s


def render_jefe(frame: int = 0) -> pygame.Surface:
    """El Custodio de la Cripta (Jefe final, 48x64)."""
    s = _surf(48, 64)
    # Levitación armónica suave
    dy = int(math.sin(frame * math.pi / 2) * 2)

    # Sombra espectral flotante
    _rect(s, 12, 59, 24, 3, OBSIDIAN_DEEP)

    # Zarcillos sombríos ondulantes bajo la túnica
    for tx in range(12, 36, 2):
        drift = int(math.sin((frame + tx) * 0.8) * 3)
        _rect(s, tx + drift, 52 + dy, 2, 8, OBSIDIAN_MID)
        _pixel(s, tx + drift, 59 + dy, OBSIDIAN_DEEP)

    # Túnica sacerdotal de terciopelo carmesí y obsidiana
    _rect(s, 12, 22 + dy, 24, 32, CRIMSON)
    _rect(s, 14, 24 + dy, 20, 28, CRIMSON_DARK)
    # Estola central de oro litúrgico
    _rect(s, 21, 22 + dy, 6, 30, LITURGIC_GOLD)
    _rect(s, 22, 23 + dy, 4, 28, GOLD_LIGHT)
    for ry in range(26, 50, 6):
        _pixel(s, 23, ry + dy, OBSIDIAN_DEEP)
        _pixel(s, 24, ry + dy, OBSIDIAN_DEEP)

    # Capa de los hombros con broches de cráneos
    _rect(s, 10, 18 + dy, 28, 7, OBSIDIAN_MID)
    _pixel(s, 11, 21 + dy, BONE)
    _pixel(s, 36, 21 + dy, BONE)

    # Cráneo / Rostro espectral del Custodio
    _rect(s, 18, 12 + dy, 12, 10, BONE)
    _rect(s, 20, 15 + dy, 3, 4, OBSIDIAN_DEEP)
    _rect(s, 25, 15 + dy, 3, 4, OBSIDIAN_DEEP)
    # Fuego turquesa en cuencas oculares
    _pixel(s, 21, 16 + dy, ANIMA_LIGHT)
    _pixel(s, 26, 16 + dy, ANIMA_LIGHT)

    # Gran Mitra papal de la Cripta
    _rect(s, 18, 2 + dy, 12, 11, LITURGIC_GOLD)
    _rect(s, 20, 0 + dy, 8, 4, GOLD_LIGHT)
    _pixel(s, 23, 0 + dy, BONE_LIGHT)
    _pixel(s, 24, 0 + dy, BONE_LIGHT)
    # Cruz central en la mitra
    _rect(s, 23, 4 + dy, 2, 7, OBSIDIAN_DEEP)
    _rect(s, 21, 6 + dy, 6, 2, OBSIDIAN_DEEP)

    # Báculo de las Ánimas (Staff of the Crypt)
    bx = 38
    pygame.draw.line(s, LITURGIC_GOLD, (bx, 6 + dy), (bx, 58 + dy), 2)
    # Cabeza del báculo: calavera coronada con llama turquesa
    _rect(s, bx - 3, 6 + dy, 7, 7, BONE)
    _pixel(s, bx - 1, 8 + dy, OBSIDIAN_DEEP)
    _pixel(s, bx + 1, 8 + dy, OBSIDIAN_DEEP)
    # Llama de ánima pulsante
    flama_r = 3 + (frame % 2)
    pygame.draw.circle(s, ANIMA_LIGHT, (bx, 2 + dy), flama_r)
    pygame.draw.circle(s, ANIMA_TURQUOISE, (bx, 2 + dy), flama_r + 1, 1)

    return s


# ============================================================
# 3. RENDERIZADORES DE ELEMENTOS INTERACTIVOS Y POWERUPS
# ============================================================
def render_alma(frame: int = 0) -> pygame.Surface:
    """Ánima / Fuego Fatuo (24x24)."""
    s = _surf(24, 24)
    # Levitación
    dy = int(math.sin(frame * math.pi / 2) * 2)

    # Aura espectral externa turquesa
    radio = 6 + (frame % 2)
    pygame.draw.circle(s, (*ANIMA_DARK, 140), (12, 12 + dy), radio + 3)
    pygame.draw.circle(s, ANIMA_TURQUOISE, (12, 12 + dy), radio)

    # Núcleo sagrado de cristal / cráneo espiritual
    _rect(s, 9, 9 + dy, 6, 6, ANIMA_LIGHT)
    _rect(s, 10, 8 + dy, 4, 2, BONE_LIGHT)
    # Ojos de ánima
    _pixel(s, 10, 11 + dy, ANIMA_DARK)
    _pixel(s, 13, 11 + dy, ANIMA_DARK)

    # Chispas orbitales de ánima
    ang = frame * (math.pi / 2)
    ox1 = int(12 + math.cos(ang) * 9)
    oy1 = int(12 + dy + math.sin(ang) * 7)
    _pixel(s, ox1, oy1, ANIMA_LIGHT)
    _pixel(s, ox1 + 1, oy1, ANIMA_TURQUOISE)

    ox2 = int(12 - math.cos(ang) * 8)
    oy2 = int(12 + dy - math.sin(ang) * 6)
    _pixel(s, ox2, oy2, ANIMA_LIGHT)

    return s


def render_farol(encendido: bool = False, frame: int = 0) -> pygame.Surface:
    """Farol Checkpoint gótico (20x30)."""
    s = _surf(20, 30)

    # Base de piedra labrada
    _rect(s, 5, 27, 10, 3, CRYPT_STONE_DARK)
    _rect(s, 6, 26, 8, 2, CRYPT_STONE)
    _pixel(s, 7, 28, MOSS)

    # Poste de hierro forjado
    _rect(s, 9, 14, 2, 12, OBSIDIAN_MID)
    _rect(s, 8, 23, 4, 2, CRYPT_STONE_DARK)

    # Jaula del farol
    _rect(s, 5, 5, 10, 9, CRYPT_STONE_DARK)
    _rect(s, 6, 6, 8, 7, OBSIDIAN_DEEP if not encendido else (*ANIMA_DARK, 180))
    # Corona / Aguja gótica superior
    _rect(s, 4, 4, 12, 2, CRYPT_STONE)
    _rect(s, 7, 2, 6, 2, CRYPT_STONE_DARK)
    _pixel(s, 9, 1, LITURGIC_GOLD)
    _pixel(s, 10, 1, LITURGIC_GOLD)

    if encendido:
        # Fuego azul de ánima crepitando
        f_alt = 4 + (frame % 3)
        _rect(s, 8, 12 - f_alt, 4, f_alt, ANIMA_TURQUOISE)
        _rect(s, 9, 11 - f_alt, 2, f_alt - 1, ANIMA_LIGHT)
        # Resplandor exterior en cristales
        _pixel(s, 6, 7, ANIMA_LIGHT)
        _pixel(s, 13, 7, ANIMA_LIGHT)
        _pixel(s, 6, 11, ANIMA_TURQUOISE)
        _pixel(s, 13, 11, ANIMA_TURQUOISE)
        # Chispas elevándose
        _pixel(s, 8 + (frame % 4), 2 - (frame % 2), ANIMA_LIGHT)
    else:
        # Apagado: mecha fría y cenizas
        _pixel(s, 9, 11, BONE_SHADOW)
        _pixel(s, 10, 11, OBSIDIAN_MID)

    return s


def render_powerup_dash(frame: int = 0) -> pygame.Surface:
    """Power-Up de Dash (Talismán del Cuervo / Botas Espectrales, 20x30)."""
    s = _surf(20, 30)
    dy = int(math.sin(frame * math.pi / 2) * 2)

    # Pedestal de piedra
    _rect(s, 5, 24, 10, 6, CRYPT_STONE_DARK)
    _rect(s, 6, 23, 8, 2, CRYPT_STONE)
    _pixel(s, 6, 27, MOSS)

    # Reliquia flotante: alas de cuervo y gema turquesa
    # Alas
    _rect(s, 4, 12 + dy, 4, 5, OBSIDIAN_MID)
    _rect(s, 12, 12 + dy, 4, 5, OBSIDIAN_MID)
    # Gema central
    _rect(s, 8, 10 + dy, 4, 6, ANIMA_LIGHT)
    _rect(s, 7, 11 + dy, 6, 4, ANIMA_TURQUOISE)
    _pixel(s, 9, 12 + dy, BONE_LIGHT)

    # Destellos
    _pixel(s, 3, 9 + dy + (frame % 2), ANIMA_LIGHT)
    _pixel(s, 16, 10 + dy - (frame % 2), ANIMA_LIGHT)

    return s


def render_powerup_rango(frame: int = 0) -> pygame.Surface:
    """Power-Up de Rango (Guadaña Mística, 20x30)."""
    s = _surf(20, 30)
    dy = int(math.sin(frame * math.pi / 2) * 2)

    # Pedestal de cripta
    _rect(s, 5, 24, 10, 6, CRYPT_STONE_DARK)
    _rect(s, 6, 23, 8, 2, CRYPT_STONE)
    _pixel(s, 12, 26, LITURGIC_GOLD)

    # Hoja curvada de guadaña en oro y amatista
    puntos = [
        (6, 18 + dy),
        (13, 8 + dy),
        (16, 12 + dy),
        (11, 19 + dy),
    ]
    pygame.draw.polygon(s, LITURGIC_GOLD, puntos)
    pygame.draw.lines(s, GOLD_LIGHT, False, puntos[:3], 2)
    # Mango
    pygame.draw.line(s, WOOD_DARK, (6, 20 + dy), (15, 7 + dy), 2)
    _pixel(s, 14, 6 + dy, GOLD_LIGHT)

    return s


def render_pala_recogible(frame: int = 0) -> pygame.Surface:
    """Pala Recogible clavada en túmulo consagrado (20x30)."""
    s = _surf(20, 30)
    # Túmulo de tierra consagrada
    _rect(s, 4, 25, 12, 5, WOOD_DARK)
    _rect(s, 6, 23, 8, 3, (38, 25, 18))
    _pixel(s, 5, 27, MOSS)
    _pixel(s, 14, 26, MOSS)

    # Mango clavado verticalmente
    pygame.draw.line(s, WOOD_MID, (10, 5), (10, 24), 2)
    # Pomo con cruz de oro litúrgico
    _pixel(s, 9, 5, LITURGIC_GOLD)
    _pixel(s, 11, 5, LITURGIC_GOLD)
    _pixel(s, 10, 4, GOLD_LIGHT)

    # Hoja de hierro clavada
    _rect(s, 8, 17, 5, 7, CRYPT_STONE_LIGHT)
    _rect(s, 9, 18, 3, 5, BONE)

    # Brillo sagrado deslizándose por la hoja
    brillo_y = 16 + (frame % 4) * 2
    _pixel(s, 9, brillo_y, GOLD_LIGHT)

    return s


# ============================================================
# 4. ELEMENTOS DE ENTORNO Y COMBATE
# ============================================================
def render_pinchos() -> pygame.Surface:
    """Pinchos / Abrojos de hierro forjado (24x20)."""
    s = _surf(24, 20)
    # Base de piedra con musgo
    _rect(s, 0, 17, 24, 3, CRYPT_STONE_DARK)
    _pixel(s, 4, 18, MOSS)
    _pixel(s, 18, 18, MOSS)

    # 4 picos de hierro afilados
    picos_x = (3, 9, 15, 21)
    for px in picos_x:
        pts = [(px - 2, 17), (px, 2), (px + 2, 17)]
        pygame.draw.polygon(s, CRYPT_STONE, pts)
        pygame.draw.polygon(s, CRYPT_STONE_LIGHT, [(px - 1, 17), (px, 2), (px, 17)])
        # Sangre seca en la punta
        _pixel(s, px, 2, CRIMSON_BRIGHT)
        _pixel(s, px, 3, CRIMSON)

    return s


def render_puerta() -> pygame.Surface:
    """Portón de cripta con arco apuntado gótico (42x58)."""
    s = _surf(42, 58)

    # Fondo abisal del portal (negro con niebla turquesa/oro lejana)
    _rect(s, 6, 10, 30, 48, OBSIDIAN_DEEP)
    _rect(s, 12, 18, 18, 38, (18, 14, 26))

    # Arco apuntado de piedra
    for y in range(0, 58):
        # Pilares laterales
        _rect(s, 0, y, 6, 1, CRYPT_STONE_DARK)
        _rect(s, 36, y, 6, 1, CRYPT_STONE_DARK)
        _pixel(s, 5, y, CRYPT_STONE_LIGHT)
        _pixel(s, 36, y, CRYPT_STONE_LIGHT)

    # Ojiva superior
    puntos_arco = [
        (0, 20), (6, 10), (14, 3), (21, 0), (28, 3), (36, 10), (42, 20),
        (36, 18), (28, 10), (21, 8), (14, 10), (6, 18)
    ]
    pygame.draw.polygon(s, CRYPT_STONE, puntos_arco)
    pygame.draw.polygon(s, CRYPT_STONE_LIGHT, puntos_arco, 1)

    # Reja levadiza de hierro forjado
    for gx in (11, 16, 21, 26, 31):
        _rect(s, gx, 14, 2, 44, OBSIDIAN_MID)
        _pixel(s, gx, 12, LITURGIC_GOLD)  # Puntas de lanza
    for gy in (22, 34, 46):
        _rect(s, 6, gy, 30, 2, OBSIDIAN_MID)

    # Cerradura dorada y runas litúrgicas
    _rect(s, 19, 36, 4, 6, LITURGIC_GOLD)
    _pixel(s, 20, 38, OBSIDIAN_DEEP)

    return s


def render_solido() -> pygame.Surface:
    """Bloque de mampostería de cripta (32x32)."""
    s = _surf(32, 32)
    s.fill(CRYPT_STONE)

    # Bisel de piedra tallada
    _rect(s, 0, 0, 32, 2, CRYPT_STONE_LIGHT)
    _rect(s, 0, 0, 2, 32, CRYPT_STONE_LIGHT)
    _rect(s, 0, 30, 32, 2, OBSIDIAN_DEEP)
    _rect(s, 30, 0, 2, 32, OBSIDIAN_DEEP)

    # Juntas de mortero (3 ladrillos)
    _rect(s, 0, 15, 32, 2, OBSIDIAN_MID)
    _rect(s, 16, 0, 2, 16, OBSIDIAN_MID)
    _rect(s, 8, 16, 2, 16, OBSIDIAN_MID)
    _rect(s, 24, 16, 2, 16, OBSIDIAN_MID)

    # Musgo en hendiduras
    _pixel(s, 3, 14, MOSS)
    _pixel(s, 4, 14, MOSS_LIGHT)
    _pixel(s, 17, 3, MOSS)
    _pixel(s, 9, 28, MOSS)
    _pixel(s, 10, 28, MOSS_DARK)

    return s


def render_golpe(frame: int = 1, direccion: int = 1) -> pygame.Surface:
    """Efecto de tajo de pala / golpe (32x32)."""
    s = _surf(32, 32)
    # Arco relampagueante en forma de medialuna plateada con filo de oro
    cx, cy = 16, 16
    r = 8 + frame * 4

    puntos = []
    for ang_deg in range(-60, 60, 15):
        rad = math.radians(ang_deg)
        px = int(cx + math.cos(rad) * r * direccion)
        py = int(cy + math.sin(rad) * r)
        puntos.append((px, py))

    if len(puntos) >= 2:
        pygame.draw.lines(s, BONE_LIGHT, False, puntos, 3)
        pygame.draw.lines(s, LITURGIC_GOLD, False, puntos, 1)

    # Chispas turquesas
    for i, (px, py) in enumerate(puntos):
        if i % 2 == 0:
            _pixel(s, px + direccion * 2, py, ANIMA_LIGHT)
            _pixel(s, px + direccion * 3, py, ANIMA_TURQUOISE)

    return s


def render_onda_jefe() -> pygame.Surface:
    """Onda de choque del Jefe (20x22)."""
    s = _surf(20, 22)
    # Medialuna de escombros de cripta y fuego fatuo
    puntos = [(2, 20), (8, 12), (16, 6), (18, 1), (15, 8), (8, 16), (4, 21)]
    pygame.draw.polygon(s, CRYPT_STONE_DARK, puntos)
    pygame.draw.lines(s, ANIMA_TURQUOISE, False, puntos, 2)
    for px, py in puntos[::2]:
        _pixel(s, px - 1, py, ANIMA_LIGHT)
    return s


# ============================================================
# EXPORTACIÓN DE ARCHIVOS STANDALONE
# ============================================================
def guardar_png(superficie: pygame.Surface, ruta_1x: Path, ruta_2x: Path) -> None:
    """Guarda en 1x (assets_pixelart) y en 2x nearest-neighbor (gdevelop assets)."""
    ruta_1x.parent.mkdir(parents=True, exist_ok=True)
    ruta_2x.parent.mkdir(parents=True, exist_ok=True)

    # 1x
    pygame.image.save(superficie, str(ruta_1x))

    # 2x nearest neighbor (conserva el pixel art nítido)
    w, h = superficie.get_width() * 2, superficie.get_height() * 2
    surf_2x = pygame.transform.scale(superficie, (w, h))
    pygame.image.save(surf_2x, str(ruta_2x))


def generar_todos_los_assets() -> list[str]:
    """Genera todos los PNGs pixel art de IN CRYPTA."""
    generados: list[str] = []

    # 1. Paleta de muestra
    paleta_surf = _surf(7 * 16, 24)
    colores = [
        OBSIDIAN_DEEP, CRYPT_STONE, MOSS, BONE,
        CRIMSON, ANIMA_TURQUOISE, LITURGIC_GOLD,
    ]
    for i, c in enumerate(colores):
        _rect(paleta_surf, i * 16, 0, 16, 24, c)
    guardar_png(paleta_surf, DIR_PIXELART / "paleta.png", DIR_ASSETS / "paleta_gothica.png")
    generados.append("paleta_gothica.png")

    # 2. Jugador (Multipose)
    # Poses: Idle (4), Run (6), Jump (2), Caida (2), Dash (3), Ataque (3)
    poses_config = [
        ("idle", 4),
        ("run", 6),
        ("jump", 2),
        ("caida", 2),
        ("dash", 3),
        ("ataque", 3),
    ]

    for pose_nombre, cant_frames in poses_config:
        for f in range(cant_frames):
            # Normal (Derecha, con pala)
            surf_der = render_jugador_base(pose_nombre, f, con_pala=True)
            nom_der = f"jugador_{pose_nombre}_{f+1}.png"
            guardar_png(surf_der, DIR_PIXELART / "jugador" / nom_der, DIR_ASSETS / nom_der)
            generados.append(nom_der)

            # Izquierda (con pala)
            surf_izq = pygame.transform.flip(surf_der, True, False)
            nom_izq = f"jugador_{pose_nombre}_izq_{f+1}.png"
            guardar_png(surf_izq, DIR_PIXELART / "jugador" / nom_izq, DIR_ASSETS / nom_izq)
            generados.append(nom_izq)

            # Normal (Sin pala)
            surf_sin_pala = render_jugador_base(pose_nombre, f, con_pala=False)
            nom_sin = f"jugador_{pose_nombre}_sin_pala_{f+1}.png"
            guardar_png(surf_sin_pala, DIR_PIXELART / "jugador" / nom_sin, DIR_ASSETS / nom_sin)
            generados.append(nom_sin)

            # Izquierda (Sin pala)
            surf_sin_izq = pygame.transform.flip(surf_sin_pala, True, False)
            nom_sin_izq = f"jugador_{pose_nombre}_izq_sin_pala_{f+1}.png"
            guardar_png(surf_sin_izq, DIR_PIXELART / "jugador" / nom_sin_izq, DIR_ASSETS / nom_sin_izq)
            generados.append(nom_sin_izq)

    # Alias de compatibilidad directa para que los nombres existentes sigan funcionando:
    shutil.copy2(DIR_ASSETS / "jugador_idle_1.png", DIR_ASSETS / "jugador.png")
    shutil.copy2(DIR_ASSETS / "jugador_idle_izq_1.png", DIR_ASSETS / "jugador_izq.png")
    shutil.copy2(DIR_ASSETS / "jugador_idle_sin_pala_1.png", DIR_ASSETS / "jugador_sin_pala.png")
    shutil.copy2(DIR_ASSETS / "jugador_idle_izq_sin_pala_1.png", DIR_ASSETS / "jugador_izq_sin_pala.png")
    generados.extend(["jugador.png", "jugador_izq.png", "jugador_sin_pala.png", "jugador_izq_sin_pala.png"])

    # 3. Enemigos
    # Enemy (4 frames)
    for f in range(4):
        surf = render_enemigo(f)
        nom = f"enemy_walk_{f+1}.png"
        guardar_png(surf, DIR_PIXELART / "enemigos" / nom, DIR_ASSETS / nom)
        generados.append(nom)
    shutil.copy2(DIR_ASSETS / "enemy_walk_1.png", DIR_ASSETS / "enemy.png")
    generados.append("enemy.png")

    # EnemyMelee (4 frames)
    for f in range(4):
        surf = render_enemigo_melee(f)
        nom = f"enemymelee_walk_{f+1}.png"
        guardar_png(surf, DIR_PIXELART / "enemigos" / nom, DIR_ASSETS / nom)
        generados.append(nom)
    shutil.copy2(DIR_ASSETS / "enemymelee_walk_1.png", DIR_ASSETS / "enemymelee.png")
    generados.append("enemymelee.png")

    # MiniJefe (4 frames)
    for f in range(4):
        surf = render_minijefe(f)
        nom = f"minijefe_walk_{f+1}.png"
        guardar_png(surf, DIR_PIXELART / "enemigos" / nom, DIR_ASSETS / nom)
        generados.append(nom)
    shutil.copy2(DIR_ASSETS / "minijefe_walk_1.png", DIR_ASSETS / "minijefe.png")
    generados.append("minijefe.png")

    # Jefe (4 frames)
    for f in range(4):
        surf = render_jefe(f)
        nom = f"jefe_walk_{f+1}.png"
        guardar_png(surf, DIR_PIXELART / "enemigos" / nom, DIR_ASSETS / nom)
        generados.append(nom)
    shutil.copy2(DIR_ASSETS / "jefe_walk_1.png", DIR_ASSETS / "jefe.png")
    generados.append("jefe.png")

    # 4. Alma (4 frames)
    for f in range(4):
        surf = render_alma(f)
        nom = f"alma_{f+1}.png"
        guardar_png(surf, DIR_PIXELART / "interactivos" / nom, DIR_ASSETS / nom)
        generados.append(nom)
    shutil.copy2(DIR_ASSETS / "alma_1.png", DIR_ASSETS / "alma.png")
    generados.append("alma.png")

    # 5. FarolCheckpoint (1 off, 4 on)
    surf_off = render_farol(encendido=False)
    guardar_png(surf_off, DIR_PIXELART / "interactivos" / "farolcheckpoint_off.png", DIR_ASSETS / "farolcheckpoint_off.png")
    shutil.copy2(DIR_ASSETS / "farolcheckpoint_off.png", DIR_ASSETS / "farolcheckpoint.png")
    generados.extend(["farolcheckpoint_off.png", "farolcheckpoint.png"])

    for f in range(4):
        surf_on = render_farol(encendido=True, frame=f)
        nom = f"farolcheckpoint_on_{f+1}.png"
        guardar_png(surf_on, DIR_PIXELART / "interactivos" / nom, DIR_ASSETS / nom)
        generados.append(nom)

    # 6. PowerUps (4 frames cada uno)
    for f in range(4):
        s_dash = render_powerup_dash(f)
        n_dash = f"powerupdash_{f+1}.png"
        guardar_png(s_dash, DIR_PIXELART / "interactivos" / n_dash, DIR_ASSETS / n_dash)
        generados.append(n_dash)

        s_rango = render_powerup_rango(f)
        n_rango = f"poweruprango_{f+1}.png"
        guardar_png(s_rango, DIR_PIXELART / "interactivos" / n_rango, DIR_ASSETS / n_rango)
        generados.append(n_rango)

        s_pala = render_pala_recogible(f)
        n_pala = f"pala_{f+1}.png"
        guardar_png(s_pala, DIR_PIXELART / "interactivos" / n_pala, DIR_ASSETS / n_pala)
        generados.append(n_pala)

    shutil.copy2(DIR_ASSETS / "powerupdash_1.png", DIR_ASSETS / "powerupdash.png")
    shutil.copy2(DIR_ASSETS / "poweruprango_1.png", DIR_ASSETS / "poweruprango.png")
    shutil.copy2(DIR_ASSETS / "pala_1.png", DIR_ASSETS / "pala.png")
    generados.extend(["powerupdash.png", "poweruprango.png", "pala.png"])

    # 7. Escenario y combate
    surf_pinchos = render_pinchos()
    guardar_png(surf_pinchos, DIR_PIXELART / "escenario" / "pinchos.png", DIR_ASSETS / "pinchos.png")
    generados.append("pinchos.png")

    surf_puerta = render_puerta()
    guardar_png(surf_puerta, DIR_PIXELART / "escenario" / "puerta.png", DIR_ASSETS / "puerta.png")
    generados.append("puerta.png")

    surf_solido = render_solido()
    guardar_png(surf_solido, DIR_PIXELART / "escenario" / "solido.png", DIR_ASSETS / "solido.png")
    generados.append("solido.png")

    surf_onda = render_onda_jefe()
    guardar_png(surf_onda, DIR_PIXELART / "escenario" / "onda_jefe.png", DIR_ASSETS / "onda_jefe.png")
    generados.append("onda_jefe.png")

    for f in range(3):
        # Golpe derecha
        s_gder = render_golpe(f + 1, 1)
        n_gder = f"golpe_der_{f+1}.png"
        guardar_png(s_gder, DIR_PIXELART / "escenario" / n_gder, DIR_ASSETS / n_gder)
        generados.append(n_gder)

        # Golpe izquierda
        s_gizq = render_golpe(f + 1, -1)
        n_gizq = f"golpe_izq_{f+1}.png"
        guardar_png(s_gizq, DIR_PIXELART / "escenario" / n_gizq, DIR_ASSETS / n_gizq)
        generados.append(n_gizq)

    return generados


# ============================================================
# ACTUALIZACIÓN DEL PROYECTO GDEVELOP (JSON)
# ============================================================
# Máscara de colisión 24x30 en coordenadas 2x (textura 64x64) para paridad exacta con Pygame
MASK_COLISION_JUGADOR = [[
    {"x": 8, "y": 4},
    {"x": 56, "y": 4},
    {"x": 56, "y": 64},
    {"x": 8, "y": 64},
]]


def _animacion_dict(
    nombre: str,
    imagenes: list[str],
    looping: bool,
    tiempo: float,
    custom_mask: list[list[dict]] | None = None,
) -> dict:
    has_custom = custom_mask is not None
    return {
        "name": nombre,
        "useMultipleDirections": False,
        "directions": [
            {
                "looping": looping,
                "timeBetweenFrames": tiempo,
                "sprites": [
                    {
                        "hasCustomCollisionMask": has_custom,
                        "customCollisionMask": custom_mask or [],
                        "image": imagen,
                        "points": [],
                        "originPoint": {"name": "origine", "x": 0, "y": 0},
                        "centerPoint": {"automatic": False, "name": "centre", "x": 0, "y": 0},
                    }
                    for imagen in imagenes
                ],
            }
        ],
    }


def actualizar_proyecto_gdevelop(ruta_json: Path) -> bool:
    """Actualiza recursos y animaciones multipose en el archivo JSON de GDevelop."""
    if not ruta_json.exists():
        print(f"Error: no existe {ruta_json}")
        return False

    with open(ruta_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Propiedades del proyecto: scaleMode nearest para nitidez absoluta
    data.setdefault("properties", {})["scaleMode"] = "nearest"

    # 2. Asegurar que todos los recursos tengan smoothed=False
    recursos = data.setdefault("resources", {}).setdefault("resources", [])
    recursos_map = {r["name"]: r for r in recursos}

    # Función para registrar un recurso de imagen si no está
    def registrar_img(nombre: str, archivo: str):
        if nombre not in recursos_map:
            nuevo = {
                "file": archivo,
                "kind": "image",
                "metadata": "",
                "name": nombre,
                "smoothed": False,
                "userAdded": True,
            }
            recursos.append(nuevo)
            recursos_map[nombre] = nuevo
        else:
            recursos_map[nombre]["smoothed"] = False
            recursos_map[nombre]["file"] = archivo

    # Registrar todos los frames de jugador
    for pose, cnt in [("idle", 4), ("run", 6), ("jump", 2), ("caida", 2), ("dash", 3), ("ataque", 3)]:
        for f in range(1, cnt + 1):
            registrar_img(f"Jugador_{pose.capitalize()}_{f}", f"assets/jugador_{pose}_{f}.png")
            registrar_img(f"Jugador_{pose.capitalize()}_Izq_{f}", f"assets/jugador_{pose}_izq_{f}.png")
            registrar_img(f"Jugador_{pose.capitalize()}_SinPala_{f}", f"assets/jugador_{pose}_sin_pala_{f}.png")
            registrar_img(f"Jugador_{pose.capitalize()}_Izq_SinPala_{f}", f"assets/jugador_{pose}_izq_sin_pala_{f}.png")

    # Registrar frames de enemigos
    for f in range(1, 5):
        registrar_img(f"EnemyWalk{f}", f"assets/enemy_walk_{f}.png")
        registrar_img(f"EnemyMeleeWalk{f}", f"assets/enemymelee_walk_{f}.png")
        registrar_img(f"MiniJefeWalk{f}", f"assets/minijefe_walk_{f}.png")
        registrar_img(f"JefeWalk{f}", f"assets/jefe_walk_{f}.png")
        registrar_img(f"Alma{f}", f"assets/alma_{f}.png")
        registrar_img(f"FarolOn{f}", f"assets/farolcheckpoint_on_{f}.png")
        registrar_img(f"PowerUpDash{f}", f"assets/powerupdash_{f}.png")
        registrar_img(f"PowerUpRango{f}", f"assets/poweruprango_{f}.png")
        registrar_img(f"PalaRecogible{f}", f"assets/pala_{f}.png")

    registrar_img("FarolOff", "assets/farolcheckpoint_off.png")

    # 3. Actualizar animaciones de objetos en todas las escenas
    for layout in data.get("layouts", []):
        for obj in layout.get("objects", []):
            name = obj.get("name")
            if name == "Jugador":
                # Respetamos el orden de índices para que los ChangeAnimation de eventos funcionen:
                # 0: Idle (4 frames)
                # 1: Caida (2 frames)
                # 2: Ataque (3 frames)
                # 3: IdleIzq (4 frames)
                # 4: CaidaIzq (2 frames)
                # 5: AtaqueIzq (3 frames)
                # 6: IdleSinPala (4 frames)
                # 7: CaidaSinPala (2 frames)
                # 8: IdleIzqSinPala (4 frames)
                # 9: CaidaIzqSinPala (2 frames)
                # 10+: Run, Jump, Dash
                obj["animations"] = [
                    _animacion_dict("Idle", [f"Jugador_Idle_{i}" for i in range(1, 5)], True, 0.14, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("Caida", [f"Jugador_Caida_{i}" for i in range(1, 3)], True, 0.12, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("Ataque", [f"Jugador_Ataque_{i}" for i in range(1, 4)], False, 0.06, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("IdleIzq", [f"Jugador_Idle_Izq_{i}" for i in range(1, 5)], True, 0.14, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("CaidaIzq", [f"Jugador_Caida_Izq_{i}" for i in range(1, 3)], True, 0.12, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("AtaqueIzq", [f"Jugador_Ataque_Izq_{i}" for i in range(1, 4)], False, 0.06, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("IdleSinPala", [f"Jugador_Idle_SinPala_{i}" for i in range(1, 5)], True, 0.14, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("CaidaSinPala", [f"Jugador_Caida_SinPala_{i}" for i in range(1, 3)], True, 0.12, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("IdleIzqSinPala", [f"Jugador_Idle_Izq_SinPala_{i}" for i in range(1, 5)], True, 0.14, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("CaidaIzqSinPala", [f"Jugador_Caida_Izq_SinPala_{i}" for i in range(1, 3)], True, 0.12, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("Run", [f"Jugador_Run_{i}" for i in range(1, 7)], True, 0.09, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("RunIzq", [f"Jugador_Run_Izq_{i}" for i in range(1, 7)], True, 0.09, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("Jump", [f"Jugador_Jump_{i}" for i in range(1, 3)], False, 0.10, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("JumpIzq", [f"Jugador_Jump_Izq_{i}" for i in range(1, 3)], False, 0.10, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("Dash", [f"Jugador_Dash_{i}" for i in range(1, 4)], False, 0.06, custom_mask=MASK_COLISION_JUGADOR),
                    _animacion_dict("DashIzq", [f"Jugador_Dash_Izq_{i}" for i in range(1, 4)], False, 0.06, custom_mask=MASK_COLISION_JUGADOR),
                ]
            elif name == "Enemy":
                obj["animations"] = [
                    _animacion_dict("Idle", [f"EnemyWalk{i}" for i in range(1, 5)], True, 0.12),
                    _animacion_dict("Walk", [f"EnemyWalk{i}" for i in range(1, 5)], True, 0.12),
                ]
            elif name == "EnemyMelee":
                obj["animations"] = [
                    _animacion_dict("Idle", [f"EnemyMeleeWalk{i}" for i in range(1, 5)], True, 0.12),
                    _animacion_dict("Walk", [f"EnemyMeleeWalk{i}" for i in range(1, 5)], True, 0.12),
                ]
            elif name == "MiniJefe":
                obj["animations"] = [
                    _animacion_dict("Idle", [f"MiniJefeWalk{i}" for i in range(1, 5)], True, 0.12),
                    _animacion_dict("Walk", [f"MiniJefeWalk{i}" for i in range(1, 5)], True, 0.12),
                ]
            elif name == "Jefe":
                obj["animations"] = [
                    _animacion_dict("Idle", [f"JefeWalk{i}" for i in range(1, 5)], True, 0.14),
                    _animacion_dict("Walk", [f"JefeWalk{i}" for i in range(1, 5)], True, 0.14),
                ]
            elif name == "Alma":
                obj["animations"] = [
                    _animacion_dict("Idle", [f"Alma{i}" for i in range(1, 5)], True, 0.12),
                ]
            elif name == "FarolCheckpoint":
                # 0: Apagado, 1: Encendido
                obj["animations"] = [
                    _animacion_dict("Apagado", ["FarolOff"], False, 0.1),
                    _animacion_dict("Encendido", [f"FarolOn{i}" for i in range(1, 5)], True, 0.12),
                ]
            elif name == "PowerUpDash":
                obj["animations"] = [
                    _animacion_dict("Idle", [f"PowerUpDash{i}" for i in range(1, 5)], True, 0.12),
                ]
            elif name == "PowerUpRango":
                obj["animations"] = [
                    _animacion_dict("Idle", [f"PowerUpRango{i}" for i in range(1, 5)], True, 0.12),
                ]
            elif name == "PalaRecogible":
                obj["animations"] = [
                    _animacion_dict("Idle", [f"PalaRecogible{i}" for i in range(1, 5)], True, 0.12),
                ]

    # Guardar JSON actualizado
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✔ GDevelop JSON actualizado exitosamente: {ruta_json}")
    return True


# ============================================================
# CLI MAIN
# ============================================================
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solo-assets", action="store_true", help="solo genera los PNGs")
    parser.add_argument("--solo-json", action="store_true", help="solo actualiza el JSON de GDevelop")
    parser.add_argument("--check", action="store_true", help="solo verifica existencia de assets")
    args = parser.parse_args()

    pygame.init()

    if args.check:
        faltantes = []
        esperados = [
            DIR_ASSETS / "jugador.png",
            DIR_ASSETS / "enemy.png",
            DIR_ASSETS / "alma.png",
            DIR_ASSETS / "farolcheckpoint.png",
            DIR_ASSETS / "puerta.png",
            DIR_ASSETS / "pinchos.png",
            DIR_ASSETS / "solido.png",
        ]
        for p in esperados:
            if not p.exists():
                faltantes.append(str(p))
        if faltantes:
            print("✘ Faltan assets:")
            for f in faltantes:
                print(f"  - {f}")
            return 1
        print("✔ Todos los assets verificados correctamente.")
        return 0

    if not args.solo_json:
        print("▶ Generando assets pixel-art góticos en 1x y 2x...")
        generados = generar_todos_los_assets()
        print(f"✔ {len(generados)} archivos de sprites generados.")

    if not args.solo_assets:
        print("▶ Actualizando proyectos GDevelop...")
        if PROYECTO_JSON.exists():
            actualizar_proyecto_gdevelop(PROYECTO_JSON)
        if PROYECTO_SYNC.exists():
            actualizar_proyecto_gdevelop(PROYECTO_SYNC)

    print("★ INTEGRACIÓN DE ASSETS GDEVELOP COMPLETADA CON ÉXITO.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
