#!/usr/bin/env python3
# ============================================================
# tools/hornear_assets_unificados.py
# ============================================================
# Genera y consolida los assets PNG de IN CRYPTA (Pygame-CE):
#   1. Rampas de color estrictas de 4 tonos (Highlight -> Base -> Shadow ->
#      Outline 1px oscuro (12, 10, 16)) coherentes con la paleta gótica de IN CRYPTA.
#   2. Texturas de iluminación con caída cuadrática suave intensity = (1.0 - norm) ** 2.2
#      y borde exactamente en 0 para r >= radius - 1 (evitando bordes cuadrados al blitear)
#      en assets_pixelart/luces/.
#   3. Iconos y paneles del HUD de alto detalle gótico (relicarios biselados,
#      corazones de rubí facetado con engarce de oro, barra_hud.png y barra_pista.png)
#      en assets_pixelart/hud/.
#   4. Spritesheets consolidados en assets_pixelart/spritesheets/
#      (+ manifiesto JSON de coordenadas).
# ============================================================

import json
import math
import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

RAIZ = Path(__file__).resolve().parent.parent
DIR_PIXELART = RAIZ / "assets_pixelart"
DIR_LUCES = DIR_PIXELART / "luces"
DIR_HUD = DIR_PIXELART / "hud"
DIR_SPRITESHEETS = DIR_PIXELART / "spritesheets"

# Outline oscuro universal de 1px (estilo gótico IN CRYPTA)
OUTLINE_OSCURO = (12, 10, 16)

# Rampas de color estrictas de 4 tonos: (Highlight, Base, Shadow, Outline)
RAMPAS_GOTICAS = {
    "rubi_vida": (
        (255, 195, 210),  # Highlight
        (210, 28, 52),    # Base
        (128, 12, 28),    # Shadow
        OUTLINE_OSCURO,   # Outline 1px
    ),
    "piedra_vacia": (
        (115, 100, 128),  # Highlight
        (38, 30, 46),     # Base
        (20, 15, 26),     # Shadow
        OUTLINE_OSCURO,   # Outline 1px
    ),
    "manto_celeste": (
        (225, 250, 255),  # Highlight
        (110, 220, 255),  # Base
        (45, 125, 170),   # Shadow
        OUTLINE_OSCURO,   # Outline 1px
    ),
    "alma_turquesa": (
        (235, 255, 252),  # Highlight
        (98, 215, 198),   # Base
        (38, 110, 104),   # Shadow
        OUTLINE_OSCURO,   # Outline 1px
    ),
    "oro_liturgico": (
        (255, 238, 170),  # Highlight
        (232, 186, 84),   # Base
        (135, 98, 34),    # Shadow
        OUTLINE_OSCURO,   # Outline 1px
    ),
    "amatista_guadana": (
        (248, 195, 255),  # Highlight
        (220, 105, 255),  # Base
        (125, 38, 160),   # Shadow
        OUTLINE_OSCURO,   # Outline 1px
    ),
    "acero_pala": (
        (245, 250, 255),  # Highlight
        (185, 198, 215),  # Base
        (98, 106, 124),   # Shadow
        OUTLINE_OSCURO,   # Outline 1px
    ),
}

LUCES_RADIALES = [
    ("luz_farol_calido.png", 192, 192, (245, 198, 92), 95),
    ("luz_farol_violeta.png", 192, 192, (205, 85, 255), 105),
    ("luz_checkpoint.png", 140, 140, (85, 215, 255), 90),
    ("luz_alma.png", 48, 48, (165, 110, 255), 95),
    ("luz_vela.png", 44, 44, (255, 185, 65), 85),
    ("luz_meta.png", 72, 72, (240, 195, 80), 95),
    ("luz_luna.png", 140, 140, (230, 225, 190), 65),
    ("aura_jefe_carmesi.png", 96, 96, (210, 32, 48), 110),
    ("aura_jefe_oro.png", 96, 96, (235, 190, 75), 105),
]

NIEBLAS_VERTICALES = [
    ("niebla_camposanto.png", 256, 64, (155, 175, 195), 0, 55),
    ("niebla_osario.png", 256, 64, (175, 150, 190), 0, 55),
]


def crear_luz_radial(ancho: int, alto: int, color: tuple, max_alpha: int) -> pygame.Surface:
    """
    Crea una superficie RGBA con caída cuadrática suave:
        intensity = (1.0 - norm) ** 2.2
    Garantiza que en el borde (r >= radius - 1) tanto RGB como Alpha sean exactamente 0,
    evitando cualquier borde cuadrado al blitear.
    """
    surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    r_col, g_col, b_col = color[:3]
    cx = (ancho - 1) / 2.0
    cy = (alto - 1) / 2.0
    radius = min(ancho, alto) / 2.0
    r_limite = max(1.0, radius - 1.0)

    for y in range(alto):
        dy = y - cy
        for x in range(ancho):
            dx = x - cx
            dist = math.hypot(dx, dy)
            if dist >= r_limite:
                continue
            norm = dist / r_limite
            intensity = (1.0 - norm) ** 2.2
            alpha = int(round(max_alpha * intensity))
            if alpha > 0:
                surf.set_at((x, y), (r_col, g_col, b_col, min(255, alpha)))
    return surf


def crear_niebla_vertical(ancho: int, alto: int, color: tuple, alpha_top: int, alpha_bottom: int) -> pygame.Surface:
    """Crea una textura RGBA de niebla con gradiente vertical suave en el canal Alpha."""
    surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    r, g, b = color[:3]
    denom = max(1, alto - 1)
    for y in range(alto):
        t = y / denom
        s = t * t * (3.0 - 2.0 * t)
        alpha = int(round(alpha_top + (alpha_bottom - alpha_top) * s))
        if alpha > 0:
            pygame.draw.line(surf, (r, g, b, min(255, alpha)), (0, y), (ancho - 1, y))
    return surf


def _aplicar_outline_1px(surf: pygame.Surface, color_outline: tuple = OUTLINE_OSCURO) -> pygame.Surface:
    """Asegura un contorno de 1px oscuro (12, 10, 16) alrededor de los píxeles opacos."""
    w, h = surf.get_size()
    salida = pygame.Surface((w, h), pygame.SRCALPHA)
    opacos = set()
    for y in range(h):
        for x in range(w):
            if surf.get_at((x, y))[3] > 20:
                opacos.add((x, y))
    for x, y in opacos:
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in opacos:
                salida.set_at((nx, ny), (*color_outline[:3], 255))
    salida.blit(surf, (0, 0))
    return salida


def _dibujar_corazon_icono(lleno: bool, manto: bool = False) -> pygame.Surface:
    """Genera el icono de corazón gótico (28x24 RGBA) con engarce de oro y rubí facetado."""
    surf = pygame.Surface((28, 24), pygame.SRCALPHA)
    cx, cy = 14, 10
    r = 6
    top_y = cy - 3
    tip_y = cy + 10

    rampa = RAMPAS_GOTICAS["rubi_vida"] if (lleno or manto) else RAMPAS_GOTICAS["piedra_vacia"]
    c_hi, c_base, c_sh, c_out = rampa
    o_hi, o_base, o_sh, _ = RAMPAS_GOTICAS["oro_liturgico"]

    # Engarce exterior de oro/hierro
    c_engarce = o_base if (lleno or manto) else (92, 82, 102)
    pygame.draw.circle(surf, c_engarce, (cx - 5, top_y), r + 1)
    pygame.draw.circle(surf, c_engarce, (cx + 5, top_y), r + 1)
    pygame.draw.polygon(surf, c_engarce, [(cx - 11, top_y), (cx + 11, top_y), (cx, tip_y + 2)])

    # Cuerpo principal
    pygame.draw.circle(surf, c_base, (cx - 5, top_y), r)
    pygame.draw.circle(surf, c_base, (cx + 5, top_y), r)
    pygame.draw.polygon(surf, c_base, [(cx - 10, top_y), (cx + 10, top_y), (cx, tip_y)])

    # Faceta de sombra derecha (Shadow)
    pygame.draw.polygon(surf, c_sh, [(cx, top_y - 1), (cx + 9, top_y), (cx, tip_y - 1)])
    # Faceta de brillo superior izquierda (Highlight)
    if lleno or manto:
        pygame.draw.line(surf, c_hi, (cx, top_y + 1), (cx, tip_y - 2), 1)
        pygame.draw.line(surf, c_hi, (cx - 7, top_y - 1), (cx, top_y + 2), 1)
        pygame.draw.circle(surf, (255, 240, 245), (cx - 5, top_y - 2), 2)
    else:
        pygame.draw.line(surf, c_hi, (cx - 4, top_y - 2), (cx + 2, top_y + 4), 1)

    surf = _aplicar_outline_1px(surf, c_out)

    if manto:
        m_hi, m_base, m_sh, _ = RAMPAS_GOTICAS["manto_celeste"]
        r_manto = r + 2
        pygame.draw.circle(surf, m_base, (cx - 5, top_y), r_manto, 1)
        pygame.draw.circle(surf, m_base, (cx + 5, top_y), r_manto, 1)
        pygame.draw.line(surf, m_hi, (cx - 11, top_y), (cx, tip_y + 2), 1)
        pygame.draw.line(surf, m_sh, (cx + 11, top_y), (cx, tip_y + 2), 1)

    return surf


def _crear_barra_hud_relicario(ancho: int = 436, alto: int = 86) -> pygame.Surface:
    """Genera el panel relicario gótico de alto detalle para barra_hud.png."""
    surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pygame.draw.rect(surf, (10, 8, 14, 248), surf.get_rect(), border_radius=10)
    for y in range(3, alto - 3):
        t = y / max(1, alto - 1)
        delta = int(9 * (0.35 - t))
        c = (max(0, 14 + delta), max(0, 12 + delta), max(0, 20 + int(delta * 1.2)), 242)
        pygame.draw.line(surf, c, (3, y), (ancho - 4, y))
    o_hi, o_base, o_sh, _ = RAMPAS_GOTICAS["oro_liturgico"]
    pygame.draw.rect(surf, (12, 10, 16, 255), surf.get_rect(), 2, border_radius=10)
    pygame.draw.rect(surf, (*o_sh, 235), pygame.Rect(2, 2, ancho - 4, alto - 4), 2, border_radius=8)
    pygame.draw.rect(surf, (*o_base, 120), pygame.Rect(5, 5, ancho - 10, alto - 10), 1, border_radius=6)
    pygame.draw.line(surf, (*o_hi, 200), (14, 3), (ancho - 14, 3), 1)
    for cx, cy in ((10, 10), (ancho - 10, 10), (10, alto - 10), (ancho - 10, alto - 10)):
        pygame.draw.polygon(surf, o_base, [(cx, cy - 4), (cx + 4, cy), (cx, cy + 4), (cx - 4, cy)])
        pygame.draw.circle(surf, o_hi, (cx, cy), 1)
    return surf


def _crear_barra_pista_obsidiana(ancho: int = 560, alto: int = 48) -> pygame.Surface:
    """Genera el cartel de aviso de pergamino de obsidiana para barra_pista.png."""
    surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    o_hi, o_base, o_sh, _ = RAMPAS_GOTICAS["oro_liturgico"]
    pygame.draw.rect(surf, (10, 8, 14, 252), surf.get_rect(), border_radius=9)
    pygame.draw.rect(surf, (18, 15, 24, 246), pygame.Rect(2, 2, ancho - 4, alto - 4), border_radius=7)
    pygame.draw.line(surf, (*o_hi, 190), (12, 3), (ancho - 12, 3), 1)
    pygame.draw.rect(surf, (10, 8, 14, 255), surf.get_rect(), 2, border_radius=9)
    pygame.draw.rect(surf, (*o_base, 235), pygame.Rect(2, 2, ancho - 4, alto - 4), 2, border_radius=7)
    pygame.draw.rect(surf, (*o_base, 245), pygame.Rect(2, 2, 6, alto - 4), border_radius=3)
    return surf


def generar_iconos_hud() -> dict:
    """Genera los iconos individuales y barras del HUD usando rampas de 4 tonos + outline 1px."""
    DIR_HUD.mkdir(parents=True, exist_ok=True)

    iconos = {}
    iconos["corazon_lleno"] = _dibujar_corazon_icono(True, False)
    iconos["corazon_vacio"] = _dibujar_corazon_icono(False, False)
    iconos["corazon_manto"] = _dibujar_corazon_icono(True, True)

    # icono_alma (16x16) — Medallón con gema de alma facetada
    s_alma = pygame.Surface((16, 16), pygame.SRCALPHA)
    c_hi, c_base, c_sh, c_out = RAMPAS_GOTICAS["alma_turquesa"]
    o_hi, o_base, o_sh, _ = RAMPAS_GOTICAS["oro_liturgico"]
    pygame.draw.circle(s_alma, (24, 20, 32), (8, 8), 6)
    pygame.draw.circle(s_alma, o_sh, (8, 8), 6, 1)
    pygame.draw.polygon(s_alma, c_sh, [(8, 2), (13, 8), (8, 14), (3, 8)])
    pygame.draw.polygon(s_alma, c_base, [(8, 3), (12, 8), (8, 13), (4, 8)])
    pygame.draw.polygon(s_alma, c_hi, [(8, 5), (10, 8), (8, 11), (6, 8)])
    iconos["icono_alma"] = _aplicar_outline_1px(s_alma, c_out)

    # icono_dash (16x16) — Medallón rúnico con doble ala
    s_dash = pygame.Surface((16, 16), pygame.SRCALPHA)
    c_hi, c_base, c_sh, c_out = RAMPAS_GOTICAS["alma_turquesa"]
    pygame.draw.circle(s_dash, (22, 20, 30), (8, 8), 6)
    pygame.draw.circle(s_dash, c_base, (8, 8), 6, 1)
    pygame.draw.polygon(s_dash, c_base, [(3, 12), (7, 6), (13, 4), (10, 9), (12, 9), (6, 13)])
    pygame.draw.line(s_dash, c_hi, (5, 10), (12, 5), 1)
    iconos["icono_dash"] = _aplicar_outline_1px(s_dash, c_out)

    # icono_pala (16x16) — Medallón labrado de Pala de Sepulturero
    s_pala = pygame.Surface((16, 16), pygame.SRCALPHA)
    o_hi, o_base, o_sh, c_out = RAMPAS_GOTICAS["oro_liturgico"]
    a_hi, a_base, a_sh, _ = RAMPAS_GOTICAS["acero_pala"]
    pygame.draw.circle(s_pala, (24, 20, 32), (8, 8), 6)
    pygame.draw.circle(s_pala, o_base, (8, 8), 6, 1)
    pygame.draw.line(s_pala, o_base, (4, 12), (10, 6), 2)
    pygame.draw.polygon(s_pala, a_base, [(8, 7), (12, 3), (14, 5), (10, 9)])
    pygame.draw.line(s_pala, a_hi, (9, 6), (12, 3), 1)
    iconos["icono_pala"] = _aplicar_outline_1px(s_pala, c_out)

    # icono_guadana (16x16) — Medallón labrado de Guadaña Consagrada
    s_guadana = pygame.Surface((16, 16), pygame.SRCALPHA)
    g_hi, g_base, g_sh, c_out = RAMPAS_GOTICAS["amatista_guadana"]
    pygame.draw.circle(s_guadana, (24, 20, 32), (8, 8), 6)
    pygame.draw.circle(s_guadana, g_base, (8, 8), 6, 1)
    pygame.draw.line(s_guadana, (185, 150, 95), (4, 13), (11, 5), 2)
    pygame.draw.arc(s_guadana, g_hi, (3, 3, 10, 10), 0.3, 3.0, 2)
    iconos["icono_guadana"] = _aplicar_outline_1px(s_guadana, c_out)

    # icono_reloj (16x16) — Reloj de bolsillo gótico
    s_reloj = pygame.Surface((16, 16), pygame.SRCALPHA)
    o_hi, o_base, o_sh, c_out = RAMPAS_GOTICAS["oro_liturgico"]
    pygame.draw.circle(s_reloj, (26, 22, 32), (8, 9), 5)
    pygame.draw.circle(s_reloj, o_base, (8, 9), 5, 1)
    pygame.draw.rect(s_reloj, o_base, (6, 2, 4, 2))
    pygame.draw.line(s_reloj, o_hi, (8, 9), (8, 5), 2)
    pygame.draw.line(s_reloj, o_base, (8, 9), (11, 9), 2)
    iconos["icono_reloj"] = _aplicar_outline_1px(s_reloj, c_out)

    # icono_calavera (16x16) — Calavera coronada de jefe
    s_calavera = pygame.Surface((16, 16), pygame.SRCALPHA)
    r_hi, r_base, r_sh, c_out = RAMPAS_GOTICAS["rubi_vida"]
    o_hi, o_base, _, _ = RAMPAS_GOTICAS["oro_liturgico"]
    pygame.draw.polygon(s_calavera, o_base, [(4, 5), (4, 2), (6, 4), (8, 1), (10, 4), (12, 2), (12, 5)])
    pygame.draw.circle(s_calavera, r_base, (8, 9), 4)
    pygame.draw.rect(s_calavera, r_base, (5, 11, 6, 3))
    pygame.draw.circle(s_calavera, c_out, (6, 9), 1)
    pygame.draw.circle(s_calavera, c_out, (10, 9), 1)
    iconos["icono_calavera"] = _aplicar_outline_1px(s_calavera, c_out)

    for nombre, surf in iconos.items():
        fname = f"{nombre}.png"
        pygame.image.save(surf, str(DIR_HUD / fname))

    # También hornear barra_hud.png y barra_pista.png actualizados
    barra_hud = _crear_barra_hud_relicario(436, 86)
    pygame.image.save(barra_hud, str(DIR_HUD / "barra_hud.png"))

    barra_pista = _crear_barra_pista_obsidiana(560, 48)
    pygame.image.save(barra_pista, str(DIR_HUD / "barra_pista.png"))

    return iconos


def empaquetar_spritesheet(items: list, cols: int = 8, padding: int = 2) -> tuple:
    """
    Empaqueta una lista de (nombre, Surface) en un spritesheet RGBA.
    Retorna (Surface, dict_frames) donde dict_frames[nombre] = {"x", "y", "w", "h"}.
    """
    if not items:
        return pygame.Surface((1, 1), pygame.SRCALPHA), {}

    max_w = max(s.get_width() for _, s in items)
    max_h = max(s.get_height() for _, s in items)
    celda_w = max_w + padding * 2
    celda_h = max_h + padding * 2

    n = len(items)
    cols_efectivas = min(cols, n)
    filas = math.ceil(n / cols_efectivas)

    sheet = pygame.Surface((cols_efectivas * celda_w, filas * celda_h), pygame.SRCALPHA)
    meta = {}

    for idx, (nombre, surf) in enumerate(items):
        col = idx % cols_efectivas
        fila = idx // cols_efectivas
        x = col * celda_w + padding
        y = fila * celda_h + padding
        sheet.blit(surf, (x, y))
        meta[nombre] = {
            "x": x,
            "y": y,
            "w": surf.get_width(),
            "h": surf.get_height(),
        }

    return sheet, meta


def cargar_sprites_categoria(rutas: list) -> list:
    """Carga una lista de rutas Path y devuelve [(stem, Surface)]."""
    items = []
    vistos = set()
    for p in rutas:
        if p.exists() and p.stem not in vistos:
            vistos.add(p.stem)
            items.append((p.stem, pygame.image.load(str(p))))
    return items


def hornear_todo():
    pygame.init()
    DIR_LUCES.mkdir(parents=True, exist_ok=True)
    DIR_HUD.mkdir(parents=True, exist_ok=True)
    DIR_SPRITESHEETS.mkdir(parents=True, exist_ok=True)

    # 1. Texturas de iluminación radiales y nieblas
    for fname, w, h, color, max_a in LUCES_RADIALES:
        surf = crear_luz_radial(w, h, color, max_a)
        pygame.image.save(surf, str(DIR_LUCES / fname))

    for fname, w, h, color, a_top, a_bot in NIEBLAS_VERTICALES:
        surf = crear_niebla_vertical(w, h, color, a_top, a_bot)
        pygame.image.save(surf, str(DIR_LUCES / fname))

    # 2. Iconos del HUD
    iconos_hud = generar_iconos_hud()

    # 3. Spritesheets consolidados
    manifiesto = {}

    # 3a. Jugador
    rutas_jugador = sorted((DIR_PIXELART / "jugador").glob("*.png"))
    items_jugador = cargar_sprites_categoria(rutas_jugador)
    sheet_jugador, meta_jugador = empaquetar_spritesheet(items_jugador, cols=8)
    pygame.image.save(sheet_jugador, str(DIR_SPRITESHEETS / "spritesheet_jugador.png"))
    manifiesto["spritesheet_jugador.png"] = meta_jugador

    # 3b. Enemigos (moradores / enemigos básicos)
    rutas_enemigos = sorted(
        p for p in (DIR_PIXELART / "enemigos").glob("*.png")
        if p.stem.startswith("enemy")
    )
    items_enemigos = cargar_sprites_categoria(rutas_enemigos)
    sheet_enemigos, meta_enemigos = empaquetar_spritesheet(items_enemigos, cols=4)
    pygame.image.save(sheet_enemigos, str(DIR_SPRITESHEETS / "spritesheet_enemigos.png"))
    manifiesto["spritesheet_enemigos.png"] = meta_enemigos

    # 3c. Jefes (Custodio del Osario y Carcelero del Osario + onda)
    rutas_jefes = sorted(
        p for p in (DIR_PIXELART / "enemigos").glob("*.png")
        if p.stem.startswith("jefe") or p.stem.startswith("minijefe")
    )
    for extra in ("onda_jefe.png",):
        p_extra = DIR_PIXELART / "escenario" / extra
        if p_extra.exists():
            rutas_jefes.append(p_extra)
    items_jefes = cargar_sprites_categoria(rutas_jefes)
    sheet_jefes, meta_jefes = empaquetar_spritesheet(items_jefes, cols=4)
    pygame.image.save(sheet_jefes, str(DIR_SPRITESHEETS / "spritesheet_jefes.png"))
    manifiesto["spritesheet_jefes.png"] = meta_jefes

    # 3d. Interactivos y escenario
    rutas_inter = sorted((DIR_PIXELART / "interactivos").glob("*.png")) + sorted((DIR_PIXELART / "escenario").glob("*.png"))
    items_inter = cargar_sprites_categoria(rutas_inter)
    sheet_inter, meta_inter = empaquetar_spritesheet(items_inter, cols=6)
    pygame.image.save(sheet_inter, str(DIR_SPRITESHEETS / "spritesheet_interactivos.png"))
    manifiesto["spritesheet_interactivos.png"] = meta_inter

    # 3e. HUD
    items_hud = list(iconos_hud.items())
    sheet_hud, meta_hud = empaquetar_spritesheet(items_hud, cols=5)
    pygame.image.save(sheet_hud, str(DIR_SPRITESHEETS / "spritesheet_hud.png"))
    manifiesto["spritesheet_hud.png"] = meta_hud

    with open(DIR_SPRITESHEETS / "spritesheets_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, indent=2, ensure_ascii=False)

    print(f"[OK] Luces generadas: {len(LUCES_RADIALES) + len(NIEBLAS_VERTICALES)} en {DIR_LUCES}")
    print(f"[OK] Iconos HUD generados: {len(iconos_hud)} (+ barras) en {DIR_HUD}")
    print(f"[OK] Spritesheets generados: {len(manifiesto)} en {DIR_SPRITESHEETS}")


if __name__ == "__main__":
    hornear_todo()
