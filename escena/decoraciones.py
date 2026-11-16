#---- Importamos librerias y configuracion ----#
import math

import pygame

import config
from config import (
    AMARILLO,
    MARFIL_XILOGRAFICO,
    MARRON_OSCURO,
    MUSGO,
    NARANJA,
    NEGRO,
    PIEDRA,
    PIEDRA_OSCURA,
    TILE,
    TINTA_ABISMO,
)

_HALO_VELA = None
_HALO_BRASERO_ESPECTRAL = None


def _construir_halo_radial(diametro, radio_max, color_rgb, alpha_max):
    """Genera una superficie circular con caida cuadratica de opacidad."""
    halo = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
    centro = diametro // 2
    for r in range(radio_max, 1, -2):
        norm = r / float(radio_max)
        alfa = int(alpha_max * (1.0 - norm * norm))
        pygame.draw.circle(halo, (*color_rgb, alfa), (centro, centro), r)
    return halo.convert_alpha()


def _obtener_halo_brasero():
    """Halo calido y tenue para braseros en segundo plano."""
    global _HALO_BRASERO_ESPECTRAL
    if _HALO_BRASERO_ESPECTRAL is None:
        _HALO_BRASERO_ESPECTRAL = _construir_halo_radial(36, 15, (235, 145, 58), 14)
    return _HALO_BRASERO_ESPECTRAL


def _obtener_halo_vela():
    """Halo translucido calido atenuado para velas decorativas de fondo."""
    global _HALO_VELA
    if _HALO_VELA is None:
        _HALO_VELA = _construir_halo_radial(36, 15, (255, 185, 65), 16)
    return _HALO_VELA


#---- Mixin de decoraciones del nivel ----#
class DecoracionesNivelMixin:
    """Renderizado procedural de tumbas, velas, estatuas, cadenas, gargolas y urnas."""

    def dibujar_decoraciones(self, surface, camara):
        tiempo = pygame.time.get_ticks() / 1000.0
        for decoracion in self.decoraciones:
            if not camara.is_on_screen(decoracion["rect"]):
                continue
            rect = camara.aplicar_rect(decoracion["rect"])
            tipo = decoracion["tipo"]

            if tipo == "t":
                self._dibujar_tumba(surface, rect)
            elif tipo == "c":
                self._dibujar_vela(surface, rect)
            elif tipo == "r":
                self._dibujar_raiz(surface, rect)
            elif tipo == "b":
                self._dibujar_brasero_y_osamenta(surface, rect, tiempo)
            elif tipo == "s":
                self._dibujar_estatua(surface, rect)
            elif tipo == "j":
                self._dibujar_cadena_colgante(surface, rect, tiempo)
            elif tipo == "g":
                self._dibujar_gargola(surface, rect)
            elif tipo == "u":
                self._dibujar_urna_cineraria(surface, rect)

    def _dibujar_tumba(self, surface, rect):
        base = rect.bottom - 2
        pygame.draw.rect(
            surface,
            PIEDRA,
            (rect.x + 8, rect.y + 8, 16, 22),
            border_radius=5,
        )
        pygame.draw.rect(
            surface,
            PIEDRA_OSCURA,
            (rect.x + 8, rect.y + 8, 16, 22),
            2,
            border_radius=5,
        )
        pygame.draw.line(
            surface,
            MUSGO,
            (rect.x + 9, rect.y + 25),
            (rect.x + 23, rect.y + 25),
            3,
        )
        pygame.draw.line(surface, PIEDRA_OSCURA, (rect.x + 16, rect.y + 12), (rect.x + 16, rect.y + 22), 2)
        pygame.draw.line(surface, PIEDRA_OSCURA, (rect.x + 12, rect.y + 16), (rect.x + 20, rect.y + 16), 2)
        pygame.draw.line(surface, (36, 38, 46), (rect.x + 10, base), (rect.x + 22, base), 2)

    def _dibujar_vela(self, surface, rect):
        x = rect.centerx
        estilo = config.resolver_estilo(getattr(config, "ESTILO_MUNDO", "AUTO"))
        if estilo != "NES":
            surface.blit(_obtener_halo_vela(), (x - 20, rect.y + 12 - 20))
        pygame.draw.rect(surface, (198, 188, 158), (x - 3, rect.y + 14, 6, 14), border_radius=2)
        pygame.draw.line(surface, NEGRO, (x, rect.y + 13), (x, rect.y + 9), 1)
        pygame.draw.polygon(
            surface,
            AMARILLO,
            [
                (x, rect.y + 2),
                (x + 4, rect.y + 9),
                (x, rect.y + 13),
                (x - 4, rect.y + 9),
            ],
        )
        pygame.draw.circle(surface, NARANJA, (x, rect.y + 10), 2)

    def _dibujar_raiz(self, surface, rect):
        x = rect.centerx
        pygame.draw.line(surface, MARRON_OSCURO, (x, rect.y), (x + 4, rect.y + 16), 4)
        pygame.draw.line(surface, MARRON_OSCURO, (x + 4, rect.y + 16), (x - 4, rect.y + 28), 3)
        pygame.draw.line(surface, MARRON_OSCURO, (x + 2, rect.y + 11), (x + 13, rect.y + 19), 2)
        pygame.draw.line(surface, MARRON_OSCURO, (x + 5, rect.y + 22), (x + 14, rect.y + 29), 2)

    def _dibujar_estatua(self, surface, rect):
        x = rect.centerx
        pygame.draw.rect(surface, PIEDRA, (x - 7, rect.y + 8, 14, 24), border_radius=4)
        pygame.draw.rect(surface, PIEDRA_OSCURA, (x - 7, rect.y + 8, 14, 24), 2, border_radius=4)
        pygame.draw.circle(surface, PIEDRA, (x, rect.y + 7), 6)
        pygame.draw.rect(surface, PIEDRA_OSCURA, (x - 10, rect.bottom - 4, 20, 4))
        pygame.draw.line(surface, MUSGO, (x - 5, rect.y + 12), (x + 4, rect.y + 26), 2)

    def _dibujar_cadena_colgante(self, surface, rect, tiempo):
        """'j': Cadena de hierro forjado colgante con oscilación pendular sutil."""
        x_base = rect.centerx
        balanceo = int(math.sin(tiempo * 1.8 + rect.x * 0.05) * 2)
        for idx, y_off in enumerate(range(0, TILE, 7)):
            cx = x_base + int((idx / 4.0) * balanceo)
            cy = rect.y + y_off
            # Sombra de eslabón
            pygame.draw.rect(surface, TINTA_ABISMO, (cx - 3, cy, 6, 8), border_radius=2)
            # Cuerpo de hierro forjado
            pygame.draw.rect(surface, (88, 86, 102), (cx - 2, cy + 1, 4, 6), 1, border_radius=2)
            # Brillo especular xilográfico
            if idx % 2 == 0:
                pygame.draw.line(surface, MARFIL_XILOGRAFICO, (cx - 1, cy + 2), (cx - 1, cy + 5), 1)
        # Gancho o grillete inferior
        pygame.draw.circle(surface, (120, 118, 134), (x_base + balanceo, rect.bottom - 2), 3, 1)

    def _dibujar_gargola(self, surface, rect):
        """'g': Acrotera / gárgola arquitectónica de piedra erosionada en segundo plano (sin rasgos de enemigo)."""
        cx = rect.centerx
        base_y = rect.bottom
        # Zócalo escalonado de piedra pizarra oscura
        pygame.draw.rect(surface, (16, 18, 24), (cx - 11, base_y - 7, 22, 7))
        pygame.draw.rect(surface, (30, 32, 42), (cx - 9, base_y - 6, 18, 5))
        pygame.draw.line(surface, (44, 48, 60), (cx - 9, base_y - 6), (cx + 9, base_y - 6), 1)
        # Musgo húmedo en la junta del pedestal
        pygame.draw.line(surface, (38, 54, 44), (cx - 7, base_y - 2), (cx + 5, base_y - 2), 2)

        # Contrafuerte alado tallado en bajorrelieve pétreo (bajo contraste, fundido al fondo)
        pts_piedra = [
            (cx - 10, base_y - 19),
            (cx - 6, base_y - 25),
            (cx, base_y - 22),
            (cx + 6, base_y - 25),
            (cx + 10, base_y - 19),
            (cx + 7, base_y - 7),
            (cx - 7, base_y - 7),
        ]
        pygame.draw.polygon(surface, (18, 20, 28), pts_piedra)
        pygame.draw.polygon(surface, (28, 30, 40), pts_piedra[1:-1])
        pygame.draw.lines(surface, (42, 46, 58), False, pts_piedra[:5], 1)

        # Busto pétreo erosionado y grietas verticales de cantería (sin ojos ni brillos)
        pygame.draw.rect(surface, (24, 26, 36), (cx - 5, base_y - 21, 10, 14), border_radius=3)
        pygame.draw.line(surface, (16, 18, 24), (cx, base_y - 20), (cx, base_y - 9), 1)
        pygame.draw.line(surface, (38, 54, 44), (cx - 4, base_y - 14), (cx - 1, base_y - 12), 1)

    def _dibujar_urna_cineraria(self, surface, rect):
        """'u': Urna funeraria tallada en piedra y bronce relicario sobre el suelo."""
        cx = rect.centerx
        base_y = rect.bottom - 1
        # Pie de la urna
        pygame.draw.rect(surface, TINTA_ABISMO, (cx - 6, base_y - 4, 12, 4))
        pygame.draw.line(surface, (218, 178, 86), (cx - 5, base_y - 3), (cx + 5, base_y - 3), 1)
        # Cuerpo bulboso con achurado
        cuerpo_rect = pygame.Rect(cx - 8, base_y - 18, 16, 14)
        pygame.draw.ellipse(surface, (44, 42, 54), cuerpo_rect)
        pygame.draw.ellipse(surface, TINTA_ABISMO, cuerpo_rect, 2)
        for hx in range(cx - 4, cx + 5, 3):
            pygame.draw.line(surface, TINTA_ABISMO, (hx, base_y - 15), (hx, base_y - 7), 1)
        # Franja heráldica dorada y cuello
        pygame.draw.line(surface, (218, 178, 86), (cx - 7, base_y - 12), (cx + 7, base_y - 12), 2)
        pygame.draw.rect(surface, (58, 56, 70), (cx - 5, base_y - 22, 10, 4))
        pygame.draw.line(surface, MARFIL_XILOGRAFICO, (cx - 6, base_y - 22), (cx + 6, base_y - 22), 2)
        # Tapa cónica con remate
        pygame.draw.polygon(surface, (218, 178, 86), [(cx - 5, base_y - 22), (cx + 5, base_y - 22), (cx, base_y - 27)])

    def _dibujar_brasero_y_osamenta(self, surface, rect, tiempo):
        """'b': Brasero y fogata tenue de fondo con tonos apagados para no competir con faroles."""
        cx = rect.centerx
        base_y = rect.bottom - 2
        estilo = config.resolver_estilo(getattr(config, "ESTILO_MUNDO", "AUTO"))

        # 1. Osamenta discreta al pie en piedra/ceniza de bajo contraste
        pygame.draw.line(surface, (18, 16, 22), (cx - 8, base_y - 4), (cx + 8, base_y), 3)
        pygame.draw.line(surface, (78, 72, 78), (cx - 7, base_y - 4), (cx + 7, base_y), 2)
        pygame.draw.line(surface, (78, 72, 78), (cx + 7, base_y - 4), (cx - 7, base_y), 2)

        # 2. Cazoleta de hierro envejecido a media altura
        py_copa = rect.y + 16
        pts_copa = [
            (cx - 7, py_copa), (cx + 7, py_copa), (cx + 4, py_copa + 6), (cx - 4, py_copa + 6)
        ]
        pygame.draw.polygon(surface, (20, 18, 26), pts_copa)
        pygame.draw.line(surface, (108, 84, 58), (cx - 7, py_copa), (cx + 7, py_copa), 1)

        # 3. Llama cálida tipo vela de fondo (sin cian intenso ni blanco brillante)
        pulso = int(math.sin(tiempo * 7.0 + rect.x * 0.1) * 1.5)
        if estilo != "NES":
            surface.blit(_obtener_halo_brasero(), (cx - 18, py_copa - 22))
        pts_llama = [
            (cx, rect.y + 7 + pulso),
            (cx + 4, py_copa - 2),
            (cx, py_copa + 1),
            (cx - 4, py_copa - 2),
        ]
        pygame.draw.polygon(surface, (205, 130, 56), pts_llama)
        pygame.draw.circle(surface, (238, 182, 92), (cx, py_copa - 3), 2)
