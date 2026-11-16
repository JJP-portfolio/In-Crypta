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
    """Mini-boss del osario con embestida y escudo frontal."""

    def __init__(self, rect, minimo_x, maximo_x):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.minimo_x = int(minimo_x)
        self.maximo_x = int(maximo_x)
        self.vida = MINIJEFE_VIDA
        self.max_vida = MINIJEFE_VIDA
        self.reiniciar()

    def reiniciar(self):
        """Restaura posicion, vida y banderas de combate al estado inicial."""
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
        # Solo recibe danio cuando queda aturdido tras embestir un muro
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
        """El escudo frontal rechaza golpes laterales de pala."""
        return False

    def recibir_pisaton(self):
        """Aplica danio si el carcelero esta vulnerable al pisoton."""
        return self._aplicar_dano_vertical()

    def _actualizar_vigilia(self, dt):
        # Patrulla tranquila en el sector derecho antes de detectar al jugador
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

    def _actualizar_patrulla(self, dt, dist_x, dir_jugador, dentro_arena, muros):
        # Avanza hacia el jugador o regresa a la arena y dispara telegrafo si corresponde
        self.vulnerable = False
        if not dentro_arena and muros is not None:
            objetivo_x = (self.minimo_x + self.maximo_x) * 0.58
            self.direccion = 1 if objetivo_x >= self.x else -1
        elif self.x <= self.minimo_x + 2 and dir_jugador < 0:
            self.direccion = 1
        elif self.x >= self.maximo_x - 2 and dir_jugador > 0:
            self.direccion = -1
        else:
            self.direccion = dir_jugador

        self.vx = self.direccion * MINIJEFE_VELOCIDAD
        self.x = max(float(self.minimo_x), min(float(self.maximo_x), self.x + self.vx * dt))
        self.rect.x = int(self.x)

        if (dentro_arena or muros is None) and (abs(dist_x) < 210 or self.temporizador <= 0):
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

    def _actualizar_telegrafo(self, muros):
        # Espera el fin del aviso antes de lanzar la embestida
        self.vulnerable = False
        self.vx = 0.0
        if self.temporizador <= 0:
            self.estado = "ataque"
            self.temporizador = 1.25 if muros is not None else 0.42
            vel_base = 320.0 if muros is not None else 220.0
            vel_embestida = vel_base + max(0, MINIJEFE_VIDA - self.vida) * 45.0
            self.vx = self.direccion * vel_embestida

    def _resolver_choque_muro(self, muros):
        # Comprueba impacto contra compuertas o muros de la arena
        if not muros:
            return False
        for m in muros:
            r_m = m.rect if hasattr(m, "rect") else m
            es_solido = getattr(m, "es_solido", lambda: True)()
            if not (es_solido and r_m.height >= 16 and self.rect.colliderect(r_m)):
                continue
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
            return True
        return False

    def _rebotar_borde_arena(self):
        # Con muros moviles presentes, el borde lateral frena sin aturdirlo
        if self.x <= self.minimo_x and self.direccion < 0:
            self.x = float(self.minimo_x) + 6.0
            self.direccion = 1
        elif self.x >= self.maximo_x and self.direccion > 0:
            self.x = float(self.maximo_x) - 6.0
            self.direccion = -1
        else:
            return False
        self.rect.x = int(self.x)
        self.estado = "recuperacion"
        self.temporizador = 0.40
        self.vulnerable = False
        self.vx = 0.0
        return True

    def _actualizar_ataque(self, dt, muros):
        # Ejecuta la embestida y transiciona segun choque o fin de carrera
        self.vulnerable = False
        self.x += self.vx * dt
        self.rect.x = int(self.x)
        choco_muro = self._resolver_choque_muro(muros)

        if not choco_muro and muros is not None and self._rebotar_borde_arena():
            return True

        if choco_muro or (self.temporizador <= 0 and muros is None):
            self.estado = "cansado"
            self.temporizador = MINIJEFE_VULNERABLE
            self.vulnerable = True
            self.vx = 0.0
            self.choque_recien = True
        elif self.temporizador <= 0:
            self.estado = "recuperacion"
            self.temporizador = 0.45
            self.vulnerable = False
            self.vx = 0.0
        return False

    def _actualizar_cansado(self):
        # Ventana de aturdimiento donde el jugador puede daniarlo desde arriba
        self.vulnerable = True
        self.vx = 0.0
        if self.temporizador <= 0:
            self.estado = "patrulla"
            self.temporizador = 1.4
            self.vulnerable = False

    def _actualizar_recuperacion(self):
        # Recupera la guardia luego de recibir golpe o frenar en un borde
        self.vulnerable = False
        self.vx = 0.0
        if self.temporizador <= 0:
            self.estado = "patrulla"
            self.temporizador = 1.0

    def actualizar(self, dt, jugador, muros=None):
        """Actualiza la maquina de estados y posicion del Carcelero."""
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
        lim_der = self.maximo_x + self.rect.width + 8
        dentro_arena = (
            (self.minimo_x - 8) <= jugador.rect.centerx <= lim_der
            and abs(dist_y) <= 5 * TILE
        )
        if muros is None or dentro_arena:
            self.activado = True

        if not self.activado and self.estado == "patrulla":
            self._actualizar_vigilia(dt)
            return

        self.temporizador -= dt
        if self.estado == "patrulla":
            self._actualizar_patrulla(dt, dist_x, dir_jugador, dentro_arena, muros)
        elif self.estado == "telegrafo":
            self._actualizar_telegrafo(muros)
        elif self.estado == "ataque":
            if self._actualizar_ataque(dt, muros):
                return
        elif self.estado == "cansado":
            self._actualizar_cansado()
        elif self.estado == "recuperacion":
            self._actualizar_recuperacion()

        self.x = limitar(self.x, self.minimo_x, self.maximo_x)
        self.rect.x = int(self.x)

    def _dibujar_auras_estado(self, surface, rect, cx, tiempo):
        # Dibuja telegrafia carmesi, vulnerabilidad dorada o escudo dorsal
        if self.estado == "telegrafo":
            pulso = 0.5 + 0.5 * math.sin(tiempo * 18)
            radio = int(24 + pulso * 6)
            alerta = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
            color_al = (180, 20, 36, int(70 + pulso * 60))
            pygame.draw.circle(alerta, color_al, (radio, radio), radio, 3)
            surface.blit(alerta, (cx - radio, rect.centery - radio))

        if self.vulnerable:
            pulso_v = 0.5 + 0.5 * math.sin(tiempo * 10)
            alerta_v = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
            color_v = (240, 200, 70, int(60 + pulso_v * 50))
            elipse_v = (0, 0, rect.width + 12, rect.height + 12)
            pygame.draw.ellipse(alerta_v, color_v, elipse_v, 2)
            surface.blit(alerta_v, (rect.x - 6, rect.y - 6))
            for i_st in range(3):
                ang_st = tiempo * 5.0 + i_st * 2.094
                sx_st = cx + int(math.cos(ang_st) * 14)
                sy_st = rect.y - 5 + int(math.sin(ang_st) * 4)
                pygame.draw.circle(surface, (255, 230, 110), (sx_st, sy_st), 2)
        else:
            arco_esc = (rect.x - 1, rect.y - 4, rect.width + 2, 16)
            pygame.draw.arc(surface, (140, 152, 170), arco_esc, 0.15, math.pi - 0.15, 3)
            arco_brillo = (rect.x + 1, rect.y - 2, rect.width - 2, 12)
            pygame.draw.arc(surface, (215, 225, 240), arco_brillo, 0.3, math.pi - 0.3, 1)

    def _dibujar_cuerpo_y_arma(self, surface, rect, cx):
        # Dibuja tunica pesada, cadenas, capucha, ojos y cuchilla
        cuerpo = pygame.Rect(rect.x + 3, rect.y + 12, rect.width - 6, rect.height - 12)
        pygame.draw.rect(surface, (26, 22, 30), cuerpo, border_radius=5)
        interior = (cuerpo.x + 3, cuerpo.y + 4, cuerpo.width - 6, cuerpo.height - 8)
        pygame.draw.rect(surface, (45, 38, 52), interior, border_radius=3)
        pygame.draw.rect(surface, (15, 12, 18), cuerpo, 2, border_radius=5)

        izq_c, der_c = cuerpo.x + 2, cuerpo.right - 2
        pygame.draw.line(surface, (130, 125, 140), (izq_c, cuerpo.y + 14), (der_c, cuerpo.y + 22), 2)
        pygame.draw.line(surface, (130, 125, 140), (izq_c, cuerpo.y + 22), (der_c, cuerpo.y + 14), 2)

        cabeza_y = rect.y + 2
        capucha = [(cx, cabeza_y), (rect.x + 4, cabeza_y + 14), (rect.right - 4, cabeza_y + 14)]
        pygame.draw.polygon(surface, (20, 16, 24), capucha)
        ojo_x = cx + self.direccion * 3
        pygame.draw.circle(surface, (220, 30, 45), (ojo_x - 3, cabeza_y + 10), 2)
        pygame.draw.circle(surface, (220, 30, 45), (ojo_x + 3, cabeza_y + 10), 2)

        arma_x = cx + self.direccion * 16
        arma_y = rect.y + 22
        pygame.draw.line(surface, (70, 60, 50), (cx, arma_y), (arma_x, arma_y + 6), 3)
        hoja = [
            (arma_x, arma_y + 2),
            (arma_x + self.direccion * 10, arma_y + 8),
            (arma_x + self.direccion * 4, arma_y + 16),
            (arma_x, arma_y + 8),
        ]
        pygame.draw.polygon(surface, (170, 160, 150), hoja)

    def _dibujar_barra_vida(self, surface, rect, cx):
        # Barra de 3 segmentos sobre la capucha y destello de golpe
        bx = cx - 18
        by = rect.y - 10
        pygame.draw.rect(surface, (15, 12, 18), (bx - 1, by - 1, 38, 7), border_radius=2)
        for i in range(self.max_vida):
            seg_color = (220, 38, 52) if i < self.vida else (40, 30, 36)
            pygame.draw.rect(surface, seg_color, (bx + i * 12 + 1, by + 1, 10, 4), border_radius=1)

        if self.tiempo_flash > 0:
            flash_overlay = obtener_aura_custodio(rect.width, rect.height, (180, 180, 180), 160)
            surface.blit(flash_overlay, rect.topleft, special_flags=pygame.BLEND_RGB_ADD)

    def dibujar(self, surface, camara, tiempo):
        """Renderiza al Carcelero con sus auras, armadura y barra de vida."""
        if not self.vivo:
            return
        rect = camara.aplicar_rect(self.rect)
        cx = rect.centerx
        base_y = rect.bottom
        pygame.draw.ellipse(surface, (10, 8, 14), (rect.x - 2, base_y - 6, rect.width + 4, 10))
        self._dibujar_auras_estado(surface, rect, cx, tiempo)
        self._dibujar_cuerpo_y_arma(surface, rect, cx)
        self._dibujar_barra_vida(surface, rect, cx)
