#---- Importamos librerias y configuracion ----#
import pygame

from config import TURQUESA_ÁNIMA

#---- Cache de superficies de iluminacion ----#
_CACHE_LUCES = {}
_CACHE_GHOSTS = {}
_CACHE_ARCOS = {}
_CACHE_AURAS = {}
_CACHE_HALOS = {}


def obtener_aura_custodio(w, h, color, alfa):
    """Cache de aura translucida con bordes difuminados del Custodio."""
    alfa_q = max(0, min(255, (int(alfa) // 8) * 8))
    clave = (int(w), int(h), tuple(color[:3]), alfa_q)
    surf = _CACHE_AURAS.get(clave)
    if surf is None:
        w_i, h_i = int(w), int(h)
        surf = pygame.Surface((w_i, h_i), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        num_anillos = 6
        for step in range(num_anillos, 0, -1):
            t = step / float(num_anillos)
            cur_w = max(4, int(w_i * t))
            cur_h = max(4, int(h_i * t))
            x_off = (w_i - cur_w) // 2
            y_off = (h_i - cur_h) // 2
            a = int(alfa_q * (1.0 - (t - 1.0 / num_anillos) ** 1.5))
            if a > 0:
                pygame.draw.ellipse(surf, (*color[:3], a), (x_off, y_off, cur_w, cur_h))
        try:
            surf = surf.convert_alpha()
        except (pygame.error, AttributeError):
            # En pruebas sin modo de video activo convert_alpha no es necesario
            pass
        _CACHE_AURAS[clave] = surf
    return surf


def _dibujar_disco_radial_suave(surf, centro, radio, color_rgb, alpha_max, pasos=10):
    cr, cg, cb = color_rgb[:3]
    for i in range(pasos, 0, -1):
        frac = i / float(pasos)
        r = max(1, int(round(radio * frac)))
        norm = (i - 1) / float(pasos)
        alfa = int(alpha_max * ((1.0 - norm * norm) ** 1.8))
        if alfa > 0:
            pygame.draw.circle(surf, (cr, cg, cb, alfa), centro, r)


def obtener_estampa_luz(radio, color, max_alfa):
    """Genera y cachea un halo radial con caida cuadratica para blend aditivo."""
    clave = (int(radio), tuple(color[:3]), int(max_alfa))
    surf = _CACHE_LUCES.get(clave)
    if surf is None:
        diametro = int(radio * 2)
        surf = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        cx, cy = radio, radio
        r_int = int(radio)
        cr, cg, cb = color[:3]
        intensidad = max_alfa / 255.0
        for r in range(r_int, 0, -1):
            norm = r / radio
            factor = max(0.0, (1.0 - norm * norm) ** 2.0)
            rgb = (
                int(cr * factor * intensidad),
                int(cg * factor * intensidad),
                int(cb * factor * intensidad),
            )
            pygame.draw.circle(surf, rgb, (int(cx), int(cy)), r)
        surf = surf.convert_alpha()
        _CACHE_LUCES[clave] = surf
    return surf


def obtener_estampa_fantasma(ancho, alto, alfa, color=TURQUESA_ÁNIMA):
    """Cache de silueta translucida para ghosting del dash."""
    clave = (int(ancho), int(alto), int(alfa), tuple(color[:3]))
    surf = _CACHE_GHOSTS.get(clave)
    if surf is None:
        surf = pygame.Surface((int(ancho), int(alto)), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*color[:3], int(alfa)), (0, 0, ancho, alto), border_radius=6)
        borde = (255, 255, 255, min(255, int(alfa * 0.8)))
        pygame.draw.rect(surf, borde, (0, 0, ancho, alto), 1, border_radius=6)
        surf = surf.convert_alpha()
        _CACHE_GHOSTS[clave] = surf
    return surf


def obtener_arco_guadaña(direccion):
    """Cache del arco espectral de energia de la Guadana Consagrada."""
    signo = 1 if direccion > 0 else -1
    clave = ("guadaña_arco_v2", signo)
    surf = _CACHE_ARCOS.get(clave)
    if surf is None:
        surf = pygame.Surface((84, 56), pygame.SRCALPHA)
        start_ang = -0.15 if signo > 0 else 1.50
        end_ang = 3.15 if signo > 0 else 4.80
        pygame.draw.arc(surf, (175, 58, 232, 165), (2, 2, 80, 52), start_ang, end_ang, 7)
        pygame.draw.arc(surf, (232, 120, 255, 225), (4, 4, 76, 48), start_ang, end_ang, 4)
        pygame.draw.arc(surf, (255, 245, 255, 255), (6, 6, 72, 44), start_ang, end_ang, 2)
        for rx, ry in ((18, 12), (40, 7), (60, 14), (28, 22)):
            pygame.draw.line(surf, (240, 200, 255, 200), (rx, ry), (rx + 4, ry + 4), 1)
            pygame.draw.line(surf, (240, 200, 255, 200), (rx + 4, ry), (rx, ry + 4), 1)
        surf = surf.convert_alpha()
        _CACHE_ARCOS[clave] = surf
    return surf


def obtener_halo_alma(step):
    """Cache de resplandor espectral tenue de Alma."""
    step = max(0, min(7, int(step)))
    clave = ("halo_alma_v2", step)
    surf = _CACHE_HALOS.get(clave)
    if surf is None:
        surf = pygame.Surface((44, 44), pygame.SRCALPHA)
        pulso = step / 7.0
        factor = 0.8 + 0.2 * pulso
        _dibujar_disco_radial_suave(surf, (22, 22), 18, (175, 110, 250), int(42 * factor), pasos=8)
        surf = surf.convert_alpha()
        _CACHE_HALOS[clave] = surf
    return surf


def obtener_aura_pickup(color_base, step):
    """Cache unificada de aura de 64x64 para reliquias y mejoras."""
    step = max(0, min(7, int(step)))
    cr, cg, cb = color_base[:3]
    clave = ("aura_pickup", cr, cg, cb, step)
    surf = _CACHE_HALOS.get(clave)
    if surf is None:
        surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        pulso = step / 7.0
        factor = 0.75 + pulso * 0.25
        _dibujar_disco_radial_suave(surf, (32, 32), 27, (cr, cg, cb), int(68 * factor), pasos=10)
        surf = surf.convert_alpha()
        _CACHE_HALOS[clave] = surf
    return surf


def obtener_halo_vela_farol(step):
    """Cache de halo tenue estilo vela azul para faroles sin consagrar."""
    step = max(0, min(7, int(step)))
    clave = ("vela_azul_farol", step)
    surf = _CACHE_HALOS.get(clave)
    if surf is None:
        pulso = step / 7.0
        radio = 18
        diam = radio * 2 + 2
        surf = pygame.Surface((diam, diam), pygame.SRCALPHA)
        c = diam // 2
        for r in range(radio, 2, -2):
            norm = r / float(radio)
            alfa = int((26 + pulso * 10) * (1.0 - norm * norm))
            pygame.draw.circle(surf, (70, 185, 255, alfa), (c, c), r)
        surf = surf.convert_alpha()
        _CACHE_HALOS[clave] = surf
    return surf


def obtener_aura_farol(tier, step):
    """Cache de resplandor para FarolCheckpoint segun grado de consagracion."""
    step = max(0, min(7, int(step)))
    clave = ("aura_farol", int(tier), step)
    surf = _CACHE_HALOS.get(clave)
    if surf is None:
        pulso = step / 7.0
        if tier >= 3:
            c_ext = (90, 220, 255, int(45 + pulso * 25))
            c_mid = (255, 215, 100, int(70 + pulso * 35))
            c_int = (255, 250, 200, int(100 + pulso * 45))
        elif tier >= 2:
            c_ext = (80, 200, 255, int(40 + pulso * 25))
            c_mid = (160, 235, 255, int(65 + pulso * 35))
            c_int = (220, 250, 255, int(90 + pulso * 40))
        else:
            c_ext = (60, 180, 255, int(30 + pulso * 20))
            c_mid = (140, 220, 255, int(55 + pulso * 30))
            c_int = (200, 245, 255, int(80 + pulso * 40))

        radio_aura = 26 if tier >= 3 else 22
        diam = radio_aura * 2 + 4
        surf = pygame.Surface((diam, diam), pygame.SRCALPHA)
        bc = radio_aura + 2
        pygame.draw.circle(surf, c_ext, (bc, bc), radio_aura)
        pygame.draw.circle(surf, c_mid, (bc, bc), radio_aura // 2 + 2)
        pygame.draw.circle(surf, c_int, (bc, bc), 6)
        surf = surf.convert_alpha()
        _CACHE_HALOS[clave] = surf
    return surf


def obtener_fantasma_losa(width, height, step):
    """Cache de silueta espectral translucida para LosaQuebradiza inactiva."""
    step = max(0, min(7, int(step)))
    clave = ("fantasma_losa", int(width), int(height), step)
    surf = _CACHE_HALOS.get(clave)
    if surf is None:
        surf = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)
        alfa = int(5 + (step / 7.0) * 40)
        pygame.draw.rect(surf, (92, 190, 174, alfa), (0, 0, width, height), 1, border_radius=2)
        surf = surf.convert_alpha()
        _CACHE_HALOS[clave] = surf
    return surf


def obtener_halo_campana(repicando, step):
    """Cache de halo turquesa de campana o incensario."""
    step = max(0, min(7, int(step)))
    clave = ("halo_campana_v2", bool(repicando), step)
    surf = _CACHE_HALOS.get(clave)
    if surf is None:
        pulso = step / 7.0
        radio = 24 if repicando else 16
        surf = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        alfa_halo = int(85 + pulso * 45) if repicando else int(24 + pulso * 12)
        _dibujar_disco_radial_suave(surf, (radio, radio), radio, (110, 215, 200), alfa_halo, pasos=8)
        surf = surf.convert_alpha()
        _CACHE_HALOS[clave] = surf
    return surf


def obtener_onda_campana(progreso_onda):
    """Cache de onda expansiva doble al repicar una campana."""
    prog = max(0, min(10, int(progreso_onda)))
    clave = ("onda_campana_doble", prog)
    surf = _CACHE_HALOS.get(clave)
    if surf is None:
        frac = prog / 10.0
        radio_onda = int(frac * 28) + 4
        alfa_onda = int((1.0 - frac) * 170)
        diam = radio_onda * 2 + 8
        center = diam // 2
        surf = pygame.Surface((diam, diam), pygame.SRCALPHA)
        pygame.draw.circle(surf, (92, 190, 174, alfa_onda), (center, center), radio_onda, 2)
        if radio_onda > 6:
            color_int = (218, 178, 86, int(alfa_onda * 0.75))
            pygame.draw.circle(surf, color_int, (center, center), radio_onda - 4, 1)
        surf = surf.convert_alpha()
        _CACHE_HALOS[clave] = surf
    return surf
