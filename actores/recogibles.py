#---- Importamos librerias y configuracion ----#
import math

import pygame

from actores.estampas import obtener_aura_pickup, obtener_halo_alma
from config import (
    BLANCO,
    GRIS,
    MARRON,
    ORO_LITÚRGICO,
    TURQUESA,
)


#---- Clase Alma ----#
class Alma:
    """Alma flotante que se puede recoger una sola vez."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.recogida = False

    def reiniciar(self):
        """Restaura el alma en su posicion original."""
        self.rect = pygame.Rect(self.inicial_rect)
        self.recogida = False

    def actualizar(self, jugador):
        """Recoge el alma si el jugador entra en contacto."""
        if not self.recogida and self.rect.colliderect(jugador.rect):
            self.recogida = True
            jugador.almas += 1
            return True
        return False

    def dibujar(self, surface, camara, tiempo):
        """Dibuja el nucleo luminoso flotante del alma."""
        if self.recogida:
            return
        rect = camara.aplicar_rect(self.rect)
        flotacion = int(math.sin(tiempo * 5 + rect.x * 0.03) * 3)
        centro = (rect.centerx, rect.centery + flotacion)

        pulso = 0.5 + 0.5 * math.sin(tiempo * 6 + rect.x * 0.04)
        halo_alma = obtener_halo_alma(int(pulso * 7))
        surface.blit(halo_alma, (centro[0] - 22, centro[1] - 22))

        pygame.draw.circle(surface, (220, 190, 255), centro, 3)
        rombo = [
            (centro[0], centro[1] - 9),
            (centro[0] + 4, centro[1] - 2),
            (centro[0], centro[1] + 6),
            (centro[0] - 4, centro[1] - 2),
        ]
        pygame.draw.polygon(surface, TURQUESA, rombo)


#---- Clase PowerUpBase ----#
class PowerUpBase:
    """Clase base para reliquias y power-ups de altares."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.recogida = False

    def reiniciar(self):
        """Restaura el pickup sin recoger."""
        self.rect = pygame.Rect(self.inicial_rect)
        self.recogida = False

    def obtener_transformacion_visual(self, camara, tiempo):
        """Calcula el rectangulo con flotacion vertical y pulso."""
        rect = camara.aplicar_rect(self.rect)
        flotacion = int(math.sin(tiempo * 4 + rect.x * 0.02) * 3)
        rect.y += flotacion
        pulso = 0.5 + 0.5 * math.sin(tiempo * 5 + rect.x * 0.03)
        return rect, pulso

    def dibujar_aura_base(self, surface, rect, pulso, color_rgb, radio_circulo=14):
        """Dibuja el resplandor exterior cacheado."""
        brillo = obtener_aura_pickup(color_rgb, int(pulso * 7))
        surface.blit(brillo, (rect.centerx - 32, rect.centery - 32))


#---- Clase PalaRecogible ----#
class PalaRecogible(PowerUpBase):
    """Pala que desbloquea el ataque y el pisoton."""

    def actualizar(self, jugador):
        """Desbloquea la pala al tocar el altar."""
        if not self.recogida and self.rect.colliderect(jugador.rect):
            self.recogida = True
            jugador.tiene_pala = True
            return True
        return False

    def _dibujar_destellos(self, surface, rect, tiempo, pulso):
        # Cuatro destellos orbitando alrededor de la reliquia
        for giro in (0.0, math.pi / 2, math.pi, math.pi * 1.5):
            angulo = tiempo * 1.8 + giro
            x = rect.centerx + int(math.cos(angulo) * (20 + pulso * 4))
            y = rect.centery + int(math.sin(angulo) * (20 + pulso * 4))
            pygame.draw.circle(surface, (255, 225, 150), (x, y), 2)
            pygame.draw.line(surface, (255, 205, 105), (x - 3, y), (x + 3, y), 1)
            pygame.draw.line(surface, (255, 205, 105), (x, y - 3), (x, y + 3), 1)

    def dibujar(self, surface, camara, tiempo):
        """Renderiza la reliquia de la pala con aura y destellos."""
        if self.recogida:
            return
        rect, pulso = self.obtener_transformacion_visual(camara, tiempo)
        self.dibujar_aura_base(surface, rect, pulso, (255, 191, 82), 17)
        pygame.draw.circle(
            surface, (238, 188, 86), (rect.centerx, rect.centery), 17 + int(pulso * 2), 1
        )
        self._dibujar_destellos(surface, rect, tiempo, pulso)
        pygame.draw.line(surface, MARRON, (rect.x + 5, rect.bottom - 3), (rect.x + 13, rect.y + 5), 3)
        hoja = [
            (rect.x + 10, rect.y + 2),
            (rect.x + 18, rect.y + 8),
            (rect.x + 12, rect.y + 14),
            (rect.x + 5, rect.y + 8),
        ]
        pygame.draw.polygon(surface, GRIS, hoja)
        pygame.draw.line(surface, BLANCO, (rect.x + 9, rect.y + 6), (rect.x + 15, rect.y + 9), 1)


#---- Clase RangoPowerUp ----#
class RangoPowerUp(PowerUpBase):
    """Power-up que consagra la guadana; bloqueado mientras viva el Carcelero."""

    def __init__(self, rect):
        super().__init__(rect)
        self.sellado = False

    def actualizar(self, jugador):
        """Otorga la guadana consagrada si el altar ya no esta sellado."""
        if self.sellado:
            return False
        if not self.recogida and self.rect.colliderect(jugador.rect):
            self.recogida = True
            jugador.rango_ataque_mejorado = True
            return True
        return False

    def _dibujar_sellado(self, surface, rect):
        # Altar apagado con cadenas cruzadas y candado runico
        cx, cy = rect.centerx, rect.centery
        pygame.draw.circle(surface, (55, 38, 68), (cx, cy), 15, 1)
        pygame.draw.line(surface, (70, 50, 82), (cx - 8, cy + 10), (cx + 5, cy - 8), 3)
        pygame.draw.arc(surface, (115, 82, 140), (cx - 4, cy - 14, 16, 14), 0.2, 3.0, 3)
        pygame.draw.line(surface, (130, 125, 140), (cx - 12, cy - 12), (cx + 12, cy + 12), 2)
        pygame.draw.line(surface, (130, 125, 140), (cx + 12, cy - 12), (cx - 12, cy + 12), 2)
        pygame.draw.rect(surface, (165, 130, 62), (cx - 4, cy - 2, 8, 7), border_radius=1)

    def dibujar(self, surface, camara, tiempo):
        """Renderiza el altar sellado o la Guadana Consagrada."""
        if self.recogida:
            return
        rect = camara.aplicar_rect(self.rect)
        if self.sellado:
            self._dibujar_sellado(surface, rect)
            return

        rect, pulso = self.obtener_transformacion_visual(camara, tiempo)
        self.dibujar_aura_base(surface, rect, pulso, (200, 100, 255), 16)
        pygame.draw.circle(
            surface, (230, 150, 255), (rect.centerx, rect.centery), 15 + int(pulso * 2), 1
        )
        cx, cy = rect.centerx, rect.centery
        pygame.draw.line(surface, (58, 38, 68), (cx - 8, cy + 10), (cx + 6, cy - 9), 3)
        pygame.draw.circle(surface, ORO_LITÚRGICO, (cx + 6, cy - 9), 2)
        hoja = [
            (cx + 2, cy - 10),
            (cx + 12, cy - 11),
            (cx + 14, cy - 3),
            (cx + 10, cy + 3),
            (cx + 6, cy - 4),
            (cx, cy - 6),
        ]
        pygame.draw.polygon(surface, (195, 85, 248), hoja)
        pygame.draw.lines(surface, (255, 240, 255), False, hoja[:4], 2)


#---- Clase DashPowerUp ----#
class DashPowerUp(PowerUpBase):
    """Power-up que desbloquea el dash espectral."""

    def actualizar(self, jugador):
        """Desbloquea el dash al recoger el amuleto."""
        if not self.recogida and self.rect.colliderect(jugador.rect):
            self.recogida = True
            jugador.tiene_dash = True
            return True
        return False

    def dibujar(self, surface, camara, tiempo):
        """Renderiza las alas espectrales del Amuleto de Sombras."""
        if self.recogida:
            return
        rect, pulso = self.obtener_transformacion_visual(camara, tiempo)
        self.dibujar_aura_base(surface, rect, pulso, (70, 210, 255), 14)
        pygame.draw.circle(
            surface, (140, 230, 255), (rect.centerx, rect.centery), 14 + int(pulso * 2), 1
        )
        cx, cy = rect.centerx, rect.centery
        ala_izq = [
            (cx - 2, cy + 3), (cx - 9, cy - 2), (cx - 13, cy - 8), (cx - 6, cy - 6), (cx - 2, cy - 1)
        ]
        ala_der = [
            (cx + 2, cy + 3), (cx + 9, cy - 2), (cx + 13, cy - 8), (cx + 6, cy - 6), (cx + 2, cy - 1)
        ]
        pygame.draw.polygon(surface, (140, 230, 255), ala_izq)
        pygame.draw.polygon(surface, (140, 230, 255), ala_der)
        pygame.draw.polygon(surface, (230, 250, 255), [(p[0], p[1] + 1) for p in ala_izq[:3]])
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 3)
        pygame.draw.circle(surface, (50, 180, 240), (cx, cy), 2)
