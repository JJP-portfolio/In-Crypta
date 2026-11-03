# ============================================================
# assets_loader.py — Cargador centralizado con caché en memoria
# ============================================================
# Provee acceso cacheado a sprites de entidades, mapas de luz
# e iconos del HUD tanto con display activo como en modo headless
# (SDL_VIDEODRIVER=dummy).
# ============================================================

import json
from pathlib import Path
import pygame

RAIZ = Path(__file__).resolve().parent
DIR_PIXELART = RAIZ / "assets_pixelart"
DIR_LUCES = DIR_PIXELART / "luces"
DIR_HUD = DIR_PIXELART / "hud"
DIR_SPRITESHEETS = DIR_PIXELART / "spritesheets"

_CACHE_ENTIDADES = {}
_CACHE_LUCES = {}
_CACHE_HUD = {}
_CACHE_SHEETS = {}
_MANIFIESTO_SHEETS = None


def _tiene_display() -> bool:
    try:
        return pygame.display.get_init() and pygame.display.get_surface() is not None
    except Exception:
        return False


def _optimizar_superficie(surf: pygame.Surface) -> pygame.Surface:
    if _tiene_display():
        try:
            return surf.convert_alpha()
        except Exception:
            return surf
    return surf


def _normalizar_nombre(nombre: str) -> str:
    limpio = str(nombre).strip()
    if limpio.lower().endswith(".png"):
        limpio = limpio[:-4]
    return limpio


def _cargar_manifiesto() -> dict:
    global _MANIFIESTO_SHEETS
    if _MANIFIESTO_SHEETS is None:
        ruta = DIR_SPRITESHEETS / "spritesheets_manifest.json"
        if ruta.exists():
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    _MANIFIESTO_SHEETS = json.load(f)
            except Exception:
                _MANIFIESTO_SHEETS = {}
        else:
            _MANIFIESTO_SHEETS = {}
    return _MANIFIESTO_SHEETS


def obtener_spritesheet(nombre: str) -> pygame.Surface:
    """Carga y cachea un spritesheet consolidado desde assets_pixelart/spritesheets/."""
    clave_base = _normalizar_nombre(nombre)
    fname = f"{clave_base}.png"
    disp = _tiene_display()
    clave = (fname, disp)
    if clave in _CACHE_SHEETS:
        return _CACHE_SHEETS[clave]

    for carpeta in (DIR_SPRITESHEETS,):
        ruta = carpeta / fname
        if ruta.exists():
            surf = _optimizar_superficie(pygame.image.load(str(ruta)))
            _CACHE_SHEETS[clave] = surf
            return surf

    surf = _optimizar_superficie(pygame.Surface((16, 16), pygame.SRCALPHA))
    _CACHE_SHEETS[clave] = surf
    return surf


def _buscar_superficie_base_entidad(stem: str) -> pygame.Surface:
    fname = f"{stem}.png"
    carpetas = (
        DIR_PIXELART / "jugador",
        DIR_PIXELART / "enemigos",
        DIR_PIXELART / "interactivos",
        DIR_PIXELART / "escenario",
        DIR_HUD,
        DIR_SPRITESHEETS,
    )
    for carpeta in carpetas:
        ruta = carpeta / fname
        if ruta.exists():
            return pygame.image.load(str(ruta))

    # Fallback: extraer recorte desde el manifiesto de spritesheets
    manifiesto = _cargar_manifiesto()
    for sheet_name, frames in manifiesto.items():
        if stem in frames:
            info = frames[stem]
            sheet = obtener_spritesheet(sheet_name)
            sub = pygame.Surface((info["w"], info["h"]), pygame.SRCALPHA)
            sub.blit(sheet, (0, 0), pygame.Rect(info["x"], info["y"], info["w"], info["h"]))
            return sub

    # Fallback seguro transparente para no crashear en headless
    fallback = pygame.Surface((32, 32), pygame.SRCALPHA)
    return fallback


def obtener_sprite_entidad(nombre: str, ancho: int = None, alto: int = None, flip_x: bool = False) -> pygame.Surface:
    """
    Obtiene un sprite de entidad cacheado en memoria.
    Escala con nearest-neighbor si se especifican ancho/alto y aplica flip_x si se solicita.
    """
    stem = _normalizar_nombre(nombre)
    disp = _tiene_display()
    clave = (stem, ancho, alto, bool(flip_x), disp)
    if clave in _CACHE_ENTIDADES:
        return _CACHE_ENTIDADES[clave]

    clave_base = (stem, None, None, False, disp)
    if clave_base in _CACHE_ENTIDADES:
        surf = _CACHE_ENTIDADES[clave_base]
    else:
        surf = _optimizar_superficie(_buscar_superficie_base_entidad(stem))
        _CACHE_ENTIDADES[clave_base] = surf

    if ancho is not None or alto is not None:
        w_dest = int(ancho) if ancho is not None else surf.get_width()
        h_dest = int(alto) if alto is not None else surf.get_height()
        if (w_dest, h_dest) != surf.get_size() and w_dest > 0 and h_dest > 0:
            surf = pygame.transform.scale(surf, (w_dest, h_dest))

    if flip_x:
        surf = pygame.transform.flip(surf, True, False)

    surf = _optimizar_superficie(surf)
    _CACHE_ENTIDADES[clave] = surf
    return surf


def obtener_textura_luz(nombre: str, ancho: int = None, alto: int = None, alpha_mult: float = 1.0) -> pygame.Surface:
    """
    Obtiene una textura de iluminación o niebla con canal Alfa suave cacheada en memoria.
    """
    stem = _normalizar_nombre(nombre)
    disp = _tiene_display()
    alpha_q = round(max(0.0, min(2.0, float(alpha_mult))), 2)
    clave = (stem, ancho, alto, alpha_q, disp)
    if clave in _CACHE_LUCES:
        return _CACHE_LUCES[clave]

    clave_base = (stem, None, None, 1.0, disp)
    if clave_base in _CACHE_LUCES:
        base = _CACHE_LUCES[clave_base]
    else:
        fname = f"{stem}.png"
        base = None
        for carpeta in (DIR_LUCES,):
            ruta = carpeta / fname
            if ruta.exists():
                base = pygame.image.load(str(ruta))
                break
        if base is None:
            base = pygame.Surface((64, 64), pygame.SRCALPHA)
        base = _optimizar_superficie(base)
        _CACHE_LUCES[clave_base] = base

    surf = base
    if ancho is not None or alto is not None:
        w_dest = int(ancho) if ancho is not None else surf.get_width()
        h_dest = int(alto) if alto is not None else surf.get_height()
        if (w_dest, h_dest) != surf.get_size() and w_dest > 0 and h_dest > 0:
            try:
                surf = pygame.transform.smoothscale(surf, (w_dest, h_dest))
            except Exception:
                surf = pygame.transform.scale(surf, (w_dest, h_dest))

    if alpha_q != 1.0:
        surf = surf.copy()
        factor = max(0, min(255, int(round(255 * alpha_q))))
        surf.fill((255, 255, 255, factor), special_flags=pygame.BLEND_RGBA_MULT)

    surf = _optimizar_superficie(surf)
    _CACHE_LUCES[clave] = surf
    return surf


def obtener_icono_hud(nombre: str, ancho: int = None, alto: int = None) -> pygame.Surface:
    """
    Obtiene un icono del HUD cacheado en memoria desde assets_pixelart/hud/
    o spritesheet_hud.png.
    """
    stem = _normalizar_nombre(nombre)
    disp = _tiene_display()
    clave = (stem, ancho, alto, disp)
    if clave in _CACHE_HUD:
        return _CACHE_HUD[clave]

    clave_base = (stem, None, None, disp)
    if clave_base in _CACHE_HUD:
        surf = _CACHE_HUD[clave_base]
    else:
        fname = f"{stem}.png"
        surf = None
        for carpeta in (DIR_HUD,):
            ruta = carpeta / fname
            if ruta.exists():
                surf = pygame.image.load(str(ruta))
                break
        if surf is None:
            surf = _buscar_superficie_base_entidad(stem)
        surf = _optimizar_superficie(surf)
        _CACHE_HUD[clave_base] = surf

    if ancho is not None or alto is not None:
        w_dest = int(ancho) if ancho is not None else surf.get_width()
        h_dest = int(alto) if alto is not None else surf.get_height()
        if (w_dest, h_dest) != surf.get_size() and w_dest > 0 and h_dest > 0:
            surf = pygame.transform.scale(surf, (w_dest, h_dest))
            surf = _optimizar_superficie(surf)

    _CACHE_HUD[clave] = surf
    return surf


def limpiar_cache_assets() -> None:
    """Limpia todas las cachés en memoria."""
    _CACHE_ENTIDADES.clear()
    _CACHE_LUCES.clear()
    _CACHE_HUD.clear()
    _CACHE_SHEETS.clear()
