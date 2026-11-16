#---- Importamos librerias y configuracion ----#
import math

import pygame

from actores.estampas import obtener_aura_custodio
from actores.utilidades import limitar
from config import (
    MINIJEFE_TELEGRAFO,
    MINIJEFE_VELOCIDAD,
    MINIJEFE_VIDA,
    MINIJEFE_VULNERABLE,
    TILE,
)


#---- Clase MiniJefe ----#
class MiniJefe:
    """Mini-Boss del Nivel 3: El Carcelero del Osario (36x48 px, 3 vidas).
    Custodia el pedestal del Power-Up 'X' (Guadaña Consagrada).
    Patrón: Patrulla -> Telegrafía ataque (0.55s) -> Embestida corta -> Cansado/Vulnerable (1.3s).
    Al morir otorga 5 almas y despeja el camino al power-up.
    """

    def __init__(self, rect, minimo_x, maximo_x):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.minimo_x = int(minimo_x)
        self.maximo_x = int(maximo_x)
        self.vida = MINIJEFE_VIDA
        self.max_vida = MINIJEFE_VIDA
        self.vivo = True
        self.direccion = -1
        self.estado = "patrulla"
        self.temporizador = 1.0
        self.vulnerable = False
        self.invulnerable = 0.0
        self.tiempo_flash = 0.0
        self.almas_otorgadas = False
        self.vx = 0.0
        self.aviso_recien = False
        self.choque_recien = False
        self.punto_choque = None
        self.activado = False

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vida = MINIJEFE_VIDA
        self.vivo = True
        self.direccion = -1
        self.estado = "patrulla"
        self.temporizador = 1.0
        self.vulnerable = False
        self.invulnerable = 0.0
        self.tiempo_flash = 0.0
        self.almas_otorgadas = False
        self.vx = 0.0
        self.aviso_recien = False
        self.choque_recien = False
        self.punto_choque = None
        self.activado = False

    def _aplicar_dano_vertical(self):
        # El Carcelero porta blindaje pesado: solo es vulnerable cuando queda aturdido tras embestir.
        if not self.vivo or self.invulnerable > 0 or not self.vulnerable:
            return False
        self.vida -= 1
        self.tiempo_flash = 0.12
        self.invulnerable = 0.40
        if self.vida <= 0:
            self.vivo = False
            self.estado = "muerto"
            self.vulnerable = False
        else:
            self.estado = "recuperacion"
            self.temporizador = 0.50
            self.vulnerable = False
        return True

    def recibir_golpe_pala(self):
        # Escudo de hierro frontal: los ataques laterales rebotan siempre; debe ser vencido desde arriba.
        return False

    def recibir_pisaton(self):
        return self._aplicar_dano_vertical()

    def actualizar(self, dt, jugador, muros=None):
        self.aviso_recien = False
        self.choque_recien = False
        if not self.vivo:
            return

        if self.invulnerable > 0:
            self.invulnerable = max(0.0, self.invulnerable - dt)
        if self.tiempo_flash > 0:
            self.tiempo_flash = max(0.0, self.tiempo_flash - dt)

        dist_x = jugador.rect.centerx - self.rect.centerx
        dist_y = jugador.rect.centery - self.rect.centery
        dir_jugador = 1 if dist_x > 0 else -1
        jugador_dentro_arena = (
            (self.minimo_x - 8) <= jugador.rect.centerx <= (self.maximo_x + self.rect.width + 8)
            and abs(dist_y) <= 5 * TILE
        )
        if muros is None:
            self.activado = True
        elif jugador_dentro_arena:
            self.activado = True

        if not self.activado and self.estado == "patrulla":
            # Vigilia en el fondo derecho de la arena (cerca de su posición inicial) sin pegarse al muro izquierdo
            self.vulnerable = False
            self.temporizador = 0.85
            lim_vigilia_izq = max(self.minimo_x + 6 * TILE, self.inicial_rect.x - 4 * TILE)
            lim_vigilia_der = min(self.maximo_x, self.inicial_rect.x + 2 * TILE)
            self.vx = self.direccion * (MINIJEFE_VELOCIDAD * 0.65)
            self.x += self.vx * dt
            if self.x <= lim_vigilia_izq:
                self.x = float(lim_vigilia_izq)
                self.direccion = 1
            elif self.x >= lim_vigilia_der:
                self.x = float(lim_vigilia_der)
                self.direccion = -1
            self.rect.x = int(self.x)
            return

        self.temporizador -= dt

        if self.estado == "patrulla":
            self.vulnerable = False
            if not jugador_dentro_arena and muros is not None:
                # Si el jugador salió a la cornisa previa, regresar hacia el centro-derecha de la arena
                objetivo_x = (self.minimo_x + self.maximo_x) * 0.58
                self.direccion = 1 if objetivo_x >= self.x else -1
            elif (self.x <= self.minimo_x + 2 and dir_jugador < 0) or (self.x >= self.maximo_x - 2 and dir_jugador > 0):
                if self.x <= self.minimo_x + 2:
                    self.direccion = 1
                elif self.x >= self.maximo_x - 2:
                    self.direccion = -1
            else:
                self.direccion = dir_jugador
            self.vx = self.direccion * MINIJEFE_VELOCIDAD
            self.x = max(float(self.minimo_x), min(float(self.maximo_x), self.x + self.vx * dt))
            self.rect.x = int(self.x)

            if (jugador_dentro_arena or muros is None) and (abs(dist_x) < 210 or self.temporizador <= 0):
                self.estado = "telegrafo"
                self.temporizador = MINIJEFE_TELEGRAFO
                self.vx = 0.0
                if self.x <= self.minimo_x + 36:
                    self.direccion = 1
                elif self.x >= self.maximo_x - 36:
                    self.direccion = -1
                else:
                    self.direccion = dir_jugador
                self.aviso_recien = True

        elif self.estado == "telegrafo":
            self.vulnerable = False
            self.vx = 0.0
            if self.temporizador <= 0:
                self.estado = "ataque"
                self.temporizador = 1.25 if muros is not None else 0.42
                vel_embestida = (320.0 if muros is not None else 220.0) + max(0, MINIJEFE_VIDA - self.vida) * 45.0
                self.vx = self.direccion * vel_embestida

        elif self.estado == "ataque":
            self.vulnerable = False
            self.x += self.vx * dt
            self.rect.x = int(self.x)
            choco_muro = False

            if muros:
                for m in muros:
                    r_m = m.rect if hasattr(m, "rect") else m
                    es_solido = getattr(m, "es_solido", lambda: True)()
                    if es_solido and r_m.height >= 16 and self.rect.colliderect(r_m):
                        if self.direccion > 0:
                            self.rect.right = r_m.left
                            px_choque = r_m.left
                        else:
                            self.rect.left = r_m.right
                            px_choque = r_m.right
                        self.x = float(self.rect.x) - self.direccion * 10.0
                        self.rect.x = int(self.x)
                        self.punto_choque = (px_choque, self.rect.centery)
                        if hasattr(m, "recibir_impacto"):
                            m.recibir_impacto()
                        choco_muro = True
                        break

            # Límites laterales de la arena: si hay muros móviles, el borde de la sala lo frena sin aturdirlo
            if not choco_muro and muros is not None:
                if self.x <= self.minimo_x and self.direccion < 0:
                    self.x = float(self.minimo_x) + 6.0
                    self.rect.x = int(self.x)
                    self.direccion = 1
                    self.estado = "recuperacion"
                    self.temporizador = 0.40
                    self.vulnerable = False
                    self.vx = 0.0
                    return
                if self.x >= self.maximo_x and self.direccion > 0:
                    self.x = float(self.maximo_x) - 6.0
                    self.rect.x = int(self.x)
                    self.direccion = -1
                    self.estado = "recuperacion"
                    self.temporizador = 0.40
                    self.vulnerable = False
                    self.vx = 0.0
                    return

            if choco_muro:
                self.estado = "cansado"
                self.temporizador = MINIJEFE_VULNERABLE
                self.vulnerable = True
                self.vx = 0.0
                self.choque_recien = True
            elif self.temporizador <= 0:
                if muros is None:
                    # Compatibilidad con pruebas unitarias aisladas sin muros de arena
                    self.estado = "cansado"
                    self.temporizador = MINIJEFE_VULNERABLE
                    self.vulnerable = True
                    self.vx = 0.0
                    self.choque_recien = True
                else:
                    # Si termina la carrera en espacio abierto sin chocar contra muro, mantiene su guardia
                    self.estado = "recuperacion"
                    self.temporizador = 0.45
                    self.vulnerable = False
                    self.vx = 0.0

        elif self.estado == "cansado":
            self.vulnerable = True
            self.vx = 0.0
            if self.temporizador <= 0:
                self.estado = "patrulla"
                self.temporizador = 1.4
                self.vulnerable = False

        elif self.estado == "recuperacion":
            self.vulnerable = False
            self.vx = 0.0
            if self.temporizador <= 0:
                self.estado = "patrulla"
                self.temporizador = 1.0

        # Limitar dentro de su arena
        self.x = limitar(self.x, self.minimo_x, self.maximo_x)
        self.rect.x = int(self.x)

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return

        rect = camara.aplicar_rect(self.rect)
        cx = rect.centerx
        base_y = rect.bottom

        # Sombra en el suelo
        pygame.draw.ellipse(surface, (10, 8, 14), (rect.x - 2, base_y - 6, rect.width + 4, 10))

        # Aura de telegrafiado carmesí translúcida
        if self.estado == "telegrafo":
            pulso = 0.5 + 0.5 * math.sin(tiempo * 18)
            radio_alerta = int(24 + pulso * 6)
            alerta = pygame.Surface((radio_alerta * 2, radio_alerta * 2), pygame.SRCALPHA)
            pygame.draw.circle(alerta, (180, 20, 36, int(70 + pulso * 60)), (radio_alerta, radio_alerta), radio_alerta, 3)
            surface.blit(alerta, (cx - radio_alerta, rect.centery - radio_alerta))

        # Aura de cansancio / vulnerabilidad dorada + estrellas de aturdimiento
        if self.vulnerable:
            pulso_v = 0.5 + 0.5 * math.sin(tiempo * 10)
            alerta_v = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
            pygame.draw.ellipse(alerta_v, (240, 200, 70, int(60 + pulso_v * 50)), (0, 0, rect.width + 12, rect.height + 12), 2)
            surface.blit(alerta_v, (rect.x - 6, rect.y - 6))
            for i_st in range(3):
                ang_st = tiempo * 5.0 + i_st * 2.094
                sx_st = cx + int(math.cos(ang_st) * 14)
                sy_st = rect.y - 5 + int(math.sin(ang_st) * 4)
                pygame.draw.circle(surface, (255, 230, 110), (sx_st, sy_st), 2)
        else:
            # Escudo dorsal de hierro remachado (indica invulnerabilidad frontal/superior mientras patrulla o embiste)
            arco_esc = (rect.x - 1, rect.y - 4, rect.width + 2, 16)
            pygame.draw.arc(surface, (140, 152, 170), arco_esc, 0.15, math.pi - 0.15, 3)
            pygame.draw.arc(surface, (215, 225, 240), (rect.x + 1, rect.y - 2, rect.width - 2, 12), 0.3, math.pi - 0.3, 1)

        # Cuerpo del Carcelero: Túnica pesada de hierro y cuero oscuro
        cuerpo = pygame.Rect(rect.x + 3, rect.y + 12, rect.width - 6, rect.height - 12)
        pygame.draw.rect(surface, (26, 22, 30), cuerpo, border_radius=5)
        pygame.draw.rect(surface, (45, 38, 52), (cuerpo.x + 3, cuerpo.y + 4, cuerpo.width - 6, cuerpo.height - 8), border_radius=3)
        pygame.draw.rect(surface, (15, 12, 18), cuerpo, 2, border_radius=5)

        # Cadenas y grilletes colgando del torso
        pygame.draw.line(surface, (130, 125, 140), (cuerpo.x + 2, cuerpo.y + 14), (cuerpo.right - 2, cuerpo.y + 22), 2)
        pygame.draw.line(surface, (130, 125, 140), (cuerpo.x + 2, cuerpo.y + 22), (cuerpo.right - 2, cuerpo.y + 14), 2)

        # Cabeza: Capucha puntiaguda con máscara de verdugo de hierro
        cabeza_y = rect.y + 2
        pygame.draw.polygon(
            surface,
            (20, 16, 24),
            [
                (cx, cabeza_y),
                (rect.x + 4, cabeza_y + 14),
                (rect.right - 4, cabeza_y + 14),
            ],
        )
        # Ranuras oculares carmesí incandescentes
        ojo_x = cx + self.direccion * 3
        pygame.draw.circle(surface, (220, 30, 45), (ojo_x - 3, cabeza_y + 10), 2)
        pygame.draw.circle(surface, (220, 30, 45), (ojo_x + 3, cabeza_y + 10), 2)

        # Arma: Gran cuchilla carcelera / gancho oxidado
        arma_x = cx + self.direccion * 16
        arma_y = rect.y + 22
        pygame.draw.line(surface, (70, 60, 50), (cx, arma_y), (arma_x, arma_y + 6), 3)
        pygame.draw.polygon(
            surface,
            (170, 160, 150),
            [
                (arma_x, arma_y + 2),
                (arma_x + self.direccion * 10, arma_y + 8),
                (arma_x + self.direccion * 4, arma_y + 16),
                (arma_x, arma_y + 8),
            ],
        )

        # Mini barra de salud encima de la cabeza (3 segmentos)
        bx = cx - 18
        by = rect.y - 10
        pygame.draw.rect(surface, (15, 12, 18), (bx - 1, by - 1, 38, 7), border_radius=2)
        for i in range(self.max_vida):
            seg_color = (220, 38, 52) if i < self.vida else (40, 30, 36)
            pygame.draw.rect(surface, seg_color, (bx + i * 12 + 1, by + 1, 10, 4), border_radius=1)

        # Destello al recibir daño
        if self.tiempo_flash > 0:
            flash_overlay = obtener_aura_custodio(rect.width, rect.height, (180, 180, 180), 160)
            surface.blit(flash_overlay, rect.topleft, special_flags=pygame.BLEND_RGB_ADD)
