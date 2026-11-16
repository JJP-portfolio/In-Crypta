#---- Importamos librerias y configuracion ----#
import math

import pygame

from actores.estampas import (
    obtener_aura_farol,
    obtener_fantasma_losa,
    obtener_halo_campana,
    obtener_halo_vela_farol,
    obtener_onda_campana,
)
from config import (
    BLANCO,
    HUESO_MARFIL,
    INCENSARIO_COOLDOWN,
    LOSA_TIEMPO_QUIEBRE,
    LOSA_TIEMPO_RECONSTRUCCION,
    ORO_LITÚRGICO,
    PIEDRA_FRIA,
    PIEDRA_OSCURA,
    SALITRE_CRIPTA,
    TILE,
    TURQUESA_ÁNIMA,
)


#---- Clase FarolCheckpoint ----#
class FarolCheckpoint:
    """Farol que sirve como punto de control y altar de consagracion."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.reiniciar()

    def reiniciar(self):
        """Apaga el farol y reinicia el tier de consagracion."""
        self.activo = False
        self.tier = 0
        self.tiempo_encendido = 0.0

    def actualizar_dt(self, dt):
        """Avanza el temporizador visual de ignicion del farol."""
        if self.tiempo_encendido > 0:
            self.tiempo_encendido = max(0.0, self.tiempo_encendido - dt)

    def actualizar(self, jugador):
        """Activa el punto de control cuando el sepulturero toca el farol."""
        if not self.activo and self.rect.colliderect(jugador.rect):
            self.activo = True
            self.tiempo_encendido = 0.65
            return True
        return False

    def _dibujar_ignicion(self, surface, cx, flame_y, color_destello):
        # Onda y destello en cruz durante los primeros instantes tras encender
        prog = 1.0 - (self.tiempo_encendido / 0.65)
        r_onda = int(6 + prog * 30)
        alfa_onda = max(0, int(230 * (1.0 - prog)))
        onda_s = pygame.Surface((r_onda * 2 + 6, r_onda * 2 + 6), pygame.SRCALPHA)
        oc = r_onda + 3
        col_ring = (*color_destello, alfa_onda)
        pygame.draw.circle(onda_s, col_ring, (oc, oc), r_onda, 2)
        if r_onda > 10:
            pygame.draw.circle(onda_s, (240, 255, 255, alfa_onda // 2), (oc, oc), r_onda - 5, 1)
        rayo = int(14 * (1.0 - prog) + 4)
        pygame.draw.line(onda_s, (245, 255, 255, alfa_onda), (oc - rayo, oc), (oc + rayo, oc), 2)
        pygame.draw.line(onda_s, col_ring, (oc, oc - rayo), (oc, oc + rayo), 2)
        surface.blit(onda_s, (cx - oc, flame_y - oc))

    def _dibujar_llama_activa(self, surface, cx, flame_y, pulso):
        # Aura de consagracion segun grado y flama central
        brillo = obtener_aura_farol(self.tier, int(pulso * 7))
        bc = brillo.get_width() // 2
        surface.blit(brillo, (cx - bc, flame_y - bc))

        if self.tier >= 3:
            color_nucleo, color_llama, color_destello = (255, 245, 180), (255, 205, 90), (255, 225, 130)
        else:
            color_nucleo, color_llama, color_destello = (240, 255, 255), (120, 220, 255), (130, 235, 255)

        radio_llama = int((4 if self.tier >= 3 else 3) + pulso * 2)
        pygame.draw.circle(surface, color_llama, (cx, flame_y), radio_llama)
        pygame.draw.circle(surface, color_nucleo, (cx, flame_y), max(1, radio_llama - 2))

        if self.tiempo_encendido > 0:
            self._dibujar_ignicion(surface, cx, flame_y, color_destello)

    def _dibujar_vela_apagada(self, surface, cx, base_y, flame_y, pulso):
        # Vela azul tenue previa a consagrar el farol
        halo_vela = obtener_halo_vela_farol(int(pulso * 7))
        hc = halo_vela.get_width() // 2
        surface.blit(halo_vela, (cx - hc, flame_y - hc))
        pygame.draw.rect(surface, (145, 165, 185), (cx - 1, base_y - 25, 2, 3))
        vaiven = int(round((pulso - 0.5) * 2))
        pts_llama = [
            (cx + vaiven, base_y - 32), (cx + 3, base_y - 27), (cx, base_y - 24), (cx - 3, base_y - 27)
        ]
        pygame.draw.polygon(surface, (65, 180, 255), pts_llama)
        pygame.draw.circle(surface, (205, 244, 255), (cx, base_y - 27), 1)

    def dibujar(self, surface, camara, tiempo):
        """Dibuja el poste de hierro y la flama o vela segun estado."""
        rect = camara.aplicar_rect(self.rect)
        cx = rect.centerx
        base_y = rect.bottom

        pygame.draw.rect(surface, (45, 42, 50), (cx - 2, base_y - 24, 4, 24))
        pygame.draw.rect(surface, (60, 56, 68), (cx - 6, base_y - 4, 12, 4))
        pygame.draw.rect(surface, (75, 72, 88), (cx - 7, base_y - 32, 14, 10), 1)
        techo = [(cx - 8, base_y - 32), (cx + 8, base_y - 32), (cx, base_y - 38)]
        pygame.draw.polygon(surface, (80, 75, 92), techo)

        flame_y = base_y - 27
        pulso = 0.5 + 0.5 * math.sin(tiempo * 8 + cx * 0.05)
        if self.activo:
            self._dibujar_llama_activa(surface, cx, flame_y, pulso)
        else:
            self._dibujar_vela_apagada(surface, cx, base_y, flame_y, pulso)


#---- Clase LosaQuebradiza ----#
class LosaQuebradiza:
    """Losa quebradiza que colapsa tras pisarla y se reconstruye luego."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.reiniciar()

    def reiniciar(self):
        """Restaura la losa intacta y sin vibracion."""
        self.rect = pygame.Rect(self.inicial_rect)
        self.activa = True
        self.pisada = False
        self.tiempo_quiebre = 0.0
        self.tiempo_reconstruccion = 0.0
        self.vibracion_offset = 0.0
        self.recien_quebrada = False
        self.recien_reconstruida = False

    def pisar(self):
        """Activa el temporizador de colapso si la losa esta firme."""
        if self.activa and not self.pisada:
            self.pisada = True

    def actualizar(self, dt, jugador=None):
        """Actualiza vibracion, colapso y reconstruccion de la losa."""
        self.recien_quebrada = False
        self.recien_reconstruida = False

        apoyado = (
            jugador is not None
            and self.activa
            and jugador.en_suelo
            and abs(jugador.rect.bottom - self.rect.top) <= 2
            and jugador.rect.right > self.rect.left
            and jugador.rect.left < self.rect.right
        )
        if apoyado:
            self.pisar()

        if self.activa and self.pisada:
            self.tiempo_quiebre += dt
            self.vibracion_offset = math.sin(self.tiempo_quiebre * 50.0) * 2.0
            if self.tiempo_quiebre >= LOSA_TIEMPO_QUIEBRE:
                self.activa = False
                self.pisada = False
                self.tiempo_quiebre = 0.0
                self.tiempo_reconstruccion = LOSA_TIEMPO_RECONSTRUCCION
                self.vibracion_offset = 0.0
                self.recien_quebrada = True
        elif self.activa:
            self.vibracion_offset = 0.0
        else:
            self.vibracion_offset = 0.0
            self.tiempo_reconstruccion -= dt
            if self.tiempo_reconstruccion <= 0:
                self.activa = True
                self.pisada = False
                self.tiempo_quiebre = 0.0
                self.tiempo_reconstruccion = 0.0
                self.recien_reconstruida = True

    def _dibujar_grietas(self, surface, rx, ry, w, h):
        # Grietas telegrafiadas o fisuras en reposo
        if self.pisada:
            avance = min(1.0, self.tiempo_quiebre / LOSA_TIEMPO_QUIEBRE)
            col_g = (30, 25, 35)
            mid_x = rx + w // 2
            p_quiebre = (mid_x - int(5 * avance), ry + int(h * 0.6 * avance))
            p_fin = (mid_x + int(4 * avance), ry + int(h * 0.9 * avance))
            pygame.draw.line(surface, col_g, (mid_x, ry + 2), p_quiebre, 1)
            pygame.draw.line(surface, col_g, p_quiebre, p_fin, 1)
            if w > 32:
                for off in (16, w - 16):
                    gx = rx + off
                    fin_g = (gx + int(3 * avance), ry + int(h * 0.5 * avance))
                    pygame.draw.line(surface, col_g, (gx, ry + 2), fin_g, 1)
            return

        c_aviso, c_sec = (216, 180, 104), (92, 190, 174)
        pygame.draw.line(surface, c_aviso, (rx + 6, ry + 2), (rx + 12, ry + 8), 1)
        pygame.draw.line(surface, c_sec, (rx + 12, ry + 8), (rx + 10, ry + h - 4), 1)
        pygame.draw.line(surface, c_aviso, (rx + w - 8, ry + 2), (rx + w - 14, ry + 10), 1)
        pygame.draw.line(surface, c_sec, (rx + w - 14, ry + 10), (rx + w - 11, ry + h - 4), 1)
        if w > 32:
            pygame.draw.line(surface, c_aviso, (rx + w // 2 - 4, ry + 3), (rx + w // 2 + 2, ry + 9), 1)
            pygame.draw.line(surface, c_sec, (rx + w // 2 + 2, ry + 9), (rx + w // 2, ry + h - 4), 1)

    def dibujar(self, surface, camara, tiempo=0.0):
        """Dibuja la losa intacta o su silueta fantasmal mientras se regenera."""
        if not self.activa:
            rect = camara.aplicar_rect(self.rect)
            step = int((0.5 + 0.5 * math.sin(tiempo * 6.0)) * 7)
            surface.blit(obtener_fantasma_losa(rect.width, rect.height, step), rect.topleft)
            return

        rect = camara.aplicar_rect(self.rect)
        rx = rect.x + int(self.vibracion_offset)
        ry, w, h = rect.y, rect.width, rect.height
        pygame.draw.rect(surface, PIEDRA_FRIA, (rx, ry, w, h), border_radius=2)
        color_borde = HUESO_MARFIL if self.pisada else SALITRE_CRIPTA
        pygame.draw.line(surface, color_borde, (rx + 1, ry), (rx + w - 2, ry), 2)
        pygame.draw.line(surface, PIEDRA_OSCURA, (rx + 1, ry + h - 1), (rx + w - 2, ry + h - 1), 2)

        for dent_x in range(rx + 4, rx + w - 4, 8):
            pygame.draw.rect(surface, (10, 8, 14), (dent_x, ry + h - 3, 4, 3))
        self._dibujar_grietas(surface, rx, ry, w, h)


#---- Clase IncensarioRebote ----#
class IncensarioRebote:
    """Campana de resonancia suspendida que impulsa hacia arriba y recarga dash."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.reiniciar()

    def reiniciar(self):
        """Restaura cooldown y oscilacion de la campana."""
        self.rect = pygame.Rect(self.inicial_rect)
        self.cooldown = 0.0
        self.tiempo_repique = 0.0
        self.activo = True

    def puede_rebotar(self):
        """Indica si ya expiro el tiempo de espera entre rebotes."""
        return self.cooldown <= 0.0

    def activar_rebote(self):
        """Dispara el repique y el cooldown de rebote."""
        self.cooldown = INCENSARIO_COOLDOWN
        self.tiempo_repique = 0.45
        return True

    def actualizar(self, dt):
        """Reduce cooldown de rebote y temporizador de repique."""
        if self.cooldown > 0:
            self.cooldown = max(0.0, self.cooldown - dt)
        if self.tiempo_repique > 0:
            self.tiempo_repique = max(0.0, self.tiempo_repique - dt)

    def _dibujar_cadena_y_yugo(self, surface, c_x, c_y):
        # Cadena vertical de hierro y yugo con remaches dorados
        y_fin = c_y - 14
        y_ini = y_fin - 22
        pygame.draw.line(surface, (28, 24, 34), (c_x, y_ini), (c_x, y_fin), 3)
        pygame.draw.line(surface, (72, 68, 82), (c_x, y_ini), (c_x, y_fin), 1)
        for y_eslabon in range(y_ini, y_fin, 5):
            pygame.draw.circle(surface, (120, 115, 130), (c_x, y_eslabon), 2, 1)

        yugo_rect = (c_x - 9, c_y - 15, 18, 5)
        pygame.draw.rect(surface, (26, 22, 32), yugo_rect, border_radius=2)
        pygame.draw.rect(surface, (88, 82, 98), yugo_rect, 1, border_radius=2)
        pygame.draw.circle(surface, ORO_LITÚRGICO, (c_x - 7, c_y - 13), 2)
        pygame.draw.circle(surface, ORO_LITÚRGICO, (c_x + 7, c_y - 13), 2)
        pygame.draw.rect(surface, (175, 130, 55), (c_x - 4, c_y - 11, 8, 3), border_radius=1)

    def _dibujar_campana_y_badajo(self, surface, c_x, c_y, offset_osc, repicando):
        # Cuerpo de bronce facetado, bisel de luz y cristal badajo
        puntos = [
            (c_x - 4, c_y - 8), (c_x + 4, c_y - 8), (c_x + 10, c_y + 4),
            (c_x + 12, c_y + 8), (c_x - 12, c_y + 8), (c_x - 10, c_y + 4),
        ]
        color_cuerpo = (212, 168, 72) if repicando else (158, 118, 52)
        pygame.draw.polygon(surface, color_cuerpo, puntos)
        pygame.draw.polygon(surface, (72, 48, 22), puntos, 1)

        color_bisel = HUESO_MARFIL if repicando else ORO_LITÚRGICO
        pygame.draw.line(surface, color_bisel, (c_x - 3, c_y - 7), (c_x - 9, c_y + 4), 1)
        c_relieve = ORO_LITÚRGICO if repicando else (98, 72, 34)
        pygame.draw.line(surface, c_relieve, (c_x - 5, c_y - 2), (c_x + 5, c_y - 2), 1)
        pygame.draw.line(surface, c_relieve, (c_x - 8, c_y + 3), (c_x + 8, c_y + 3), 1)
        pygame.draw.line(surface, (40, 26, 16), (c_x - 11, c_y + 8), (c_x + 11, c_y + 8), 2)

        badajo_x = c_x + int(offset_osc * 1.6)
        badajo_y = c_y + 9
        pygame.draw.line(surface, (60, 52, 68), (c_x, c_y + 4), (badajo_x, badajo_y), 2)
        color_cristal = (195, 255, 245) if repicando else TURQUESA_ÁNIMA
        pygame.draw.circle(surface, color_cristal, (badajo_x, badajo_y), 3)
        pygame.draw.circle(surface, BLANCO if repicando else (180, 240, 230), (badajo_x, badajo_y), 1)

    def dibujar(self, surface, camara, tiempo=0.0):
        """Renderiza halo, cadena, campana oscilante y onda al repicar."""
        rect = camara.aplicar_rect(self.rect)
        cx, cy = rect.centerx, rect.centery
        offset_osc = 0.0
        if self.tiempo_repique > 0:
            offset_osc = math.sin(self.tiempo_repique * 30.0) * (4.0 * (self.tiempo_repique / 0.45))

        c_x, c_y = cx + int(offset_osc), cy
        repicando = self.tiempo_repique > 0
        pulso = 0.5 + 0.5 * math.sin(tiempo * 5.0 + cx * 0.1)
        halo = obtener_halo_campana(repicando, int(pulso * 7))
        hr = halo.get_width() // 2
        surface.blit(halo, (c_x - hr, c_y - hr))

        self._dibujar_cadena_y_yugo(surface, c_x, c_y)
        self._dibujar_campana_y_badajo(surface, c_x, c_y, offset_osc, repicando)

        if repicando:
            prog = int((1.0 - (self.tiempo_repique / 0.45)) * 10)
            onda_surf = obtener_onda_campana(prog)
            ow = onda_surf.get_width()
            surface.blit(onda_surf, (c_x - ow // 2, c_y - ow // 2))


#---- Clase BloqueCripta ----#
class BloqueCripta:
    """Bloque de cripta destructible bajo los pies del Custodio en fase 3."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.roto = False

    def reiniciar(self):
        """Restaura el bloque intacto."""
        self.roto = False

    def romper(self):
        """Rompe el bloque al recibir el aplastamiento del Custodio."""
        if self.roto:
            return False
        self.roto = True
        return True

    def dibujar(self, surface, camara, tiempo=0.0):
        """Dibuja la lapida con sello runico si no esta rota."""
        rect = camara.aplicar_rect(self.rect)
        if self.roto:
            return
        pygame.draw.rect(surface, (42, 34, 48), rect)
        pygame.draw.rect(surface, (22, 16, 26), rect, 1)
        pygame.draw.line(surface, (118, 92, 130), (rect.x + 2, rect.y + 1), (rect.right - 3, rect.y + 1), 2)
        pulso = 0.5 + 0.5 * math.sin(tiempo * 4.5 + rect.x * 0.08)
        col_sello = (int(145 + pulso * 60), int(75 + pulso * 35), int(175 + pulso * 55))
        pygame.draw.line(surface, col_sello, (rect.x + 6, rect.y + 6), (rect.centerx, rect.centery + 2), 1)
        pygame.draw.line(surface, col_sello, (rect.right - 6, rect.y + 6), (rect.centerx, rect.centery + 2), 1)
        pygame.draw.line(surface, (24, 18, 28), (rect.centerx, rect.y + 4), (rect.centerx - 3, rect.bottom - 5), 1)
        pygame.draw.line(surface, (24, 18, 28), (rect.x + 4, rect.bottom - 8), (rect.right - 5, rect.bottom - 5), 1)


#---- Clase CompuertaArena ----#
class CompuertaArena:
    """Rastrillo de hierro forjado que sella la camara del Custodio."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.reiniciar()

    def cerrar(self):
        """Sella la compuerta de la camara del jefe."""
        self.cerrada = True

    def abrir(self):
        """Abre la compuerta al caer el jefe."""
        self.cerrada = False

    def reiniciar(self):
        """Restaura la compuerta abierta."""
        self.cerrada = False
        self.progreso = 0.0

    def actualizar(self, dt):
        """Despliega o retrae suavemente las barras del rastrillo."""
        objetivo = 1.0 if self.cerrada else 0.0
        if self.progreso < objetivo:
            self.progreso = min(1.0, self.progreso + dt * 6.5)
        elif self.progreso > objetivo:
            self.progreso = max(0.0, self.progreso - dt * 3.5)

    def dibujar(self, surface, camara, tiempo=0.0):
        """Dibuja marco, barrotes verticales y sello runico si esta cerrada."""
        vis = self.progreso if self.cerrada else max(0.18, self.progreso)
        rect = camara.aplicar_rect(self.rect)
        alto_vis = max(8, int(rect.height * vis))
        barra_rect = pygame.Rect(rect.x + 4, rect.y, rect.width - 8, alto_vis)

        pygame.draw.rect(surface, (36, 30, 42), (rect.x + 2, rect.y, rect.width - 4, 5))
        pygame.draw.rect(surface, (112, 92, 60), (rect.x + 2, rect.y, rect.width - 4, 5), 1)

        for bx in (barra_rect.x + 4, barra_rect.centerx, barra_rect.right - 5):
            pygame.draw.line(surface, (55, 52, 66), (bx, rect.y + 4), (bx, rect.y + alto_vis - 2), 3)
            pygame.draw.line(surface, (140, 146, 165), (bx - 1, rect.y + 4), (bx - 1, rect.y + alto_vis - 4), 1)
        for by in range(rect.y + 14, rect.y + alto_vis - 4, 18):
            pygame.draw.line(surface, (42, 38, 52), (barra_rect.x, by), (barra_rect.right, by), 3)

        if self.cerrada:
            pulso = int(160 + 80 * math.sin(tiempo * 7.0))
            centro = (barra_rect.centerx, rect.y + alto_vis // 2)
            pygame.draw.circle(surface, (pulso, 45, 70), centro, 4)
            pygame.draw.circle(surface, ORO_LITÚRGICO, centro, 4, 1)


#---- Clase MuroMovilCompuerta ----#
class MuroMovilCompuerta:
    """Muro compuerta que emerge por bloques en la arena del Carcelero."""

    def __init__(self, x, base_y, ancho=TILE, alto_max=3 * TILE):
        self.x = int(x)
        self.base_y = int(base_y)
        self.ancho = int(ancho)
        self.alto_max = int(alto_max)
        self.reiniciar()

    def _actualizar_rect(self):
        # Cuantizamos en tercios para marcar la subida de los tres bloques
        if self.progreso <= 0.02:
            alto_vis = 0
        else:
            tercios = self.progreso * 3.0
            bloque_idx = int(min(2.0, math.floor(tercios)))
            frac = tercios - bloque_idx
            progreso_esc = (bloque_idx + min(1.0, frac * 1.25)) / 3.0
            alto_vis = max(6, int(round(self.alto_max * min(1.0, progreso_esc))))
        self.rect = pygame.Rect(self.x, self.base_y - alto_vis, self.ancho, alto_vis)

    def es_solido(self):
        """Indica si el muro emergio lo suficiente para frenar embestidas."""
        return self.estado in ("emergiendo", "armado") and self.rect.height >= 12

    def puede_activarse(self):
        """Indica si el muro esta oculto y disponible para el proximo ciclo."""
        return self.estado == "oculto" and self.enfriamiento <= 0.0 and not self.usado_ciclo

    def activar(self, duracion_aviso=0.16, duracion_armado=1.5):
        """Inicia la emergencia desde el suelo si no esta en enfriamiento."""
        if self.enfriamiento > 0.0 or self.usado_ciclo:
            return False
        if self.estado in ("oculto", "retrayendo"):
            self.estado = "aviso"
            self.temporizador = duracion_aviso
            self.duracion_armado = duracion_armado
            self.recien_aviso = True
            return True
        if self.estado == "armado":
            self.temporizador = max(self.temporizador, duracion_armado)
        return False

    def retraer(self):
        """Comienza a ocultar el muro bajo el piso."""
        if self.estado not in ("oculto", "retrayendo"):
            self.estado = "retrayendo"

    def recibir_impacto(self):
        """Absorbe el choque del Carcelero y entra en enfriamiento."""
        self.tiempo_temblor = 0.30
        self.enfriamiento = 9.0
        self.usado_ciclo = True
        if self.estado in ("emergiendo", "armado"):
            self.progreso = min(1.0, max(0.75, self.progreso))
            self.estado = "retrayendo"
            self._actualizar_rect()

    def reiniciar(self):
        """Oculta la compuerta y limpia temporizadores."""
        self.estado = "oculto"
        self.progreso = 0.0
        self.temporizador = 0.0
        self.duracion_armado = 1.5
        self.tiempo_temblor = 0.0
        self.enfriamiento = 0.0
        self.usado_ciclo = False
        self.recien_aviso = False
        self.recien_armado = False
        self.rect = pygame.Rect(self.x, self.base_y, self.ancho, 0)

    def _desplazar_jugador_al_emerger(self, jugador):
        # Eleva al jugador si pisa la ranura o lo empuja hacia el costado
        if jugador is None or self.rect.height <= 0 or not jugador.rect.colliderect(self.rect):
            return
        if jugador.rect.centery <= self.rect.top + 20:
            jugador.rect.bottom = self.rect.top
            jugador.y = float(jugador.rect.y)
            jugador.vy = min(0.0, jugador.vy)
            jugador.en_suelo = True
        elif jugador.rect.centerx < self.rect.centerx:
            jugador.rect.right = self.rect.left
            jugador.x = float(jugador.rect.x)
        else:
            jugador.rect.left = self.rect.right
            jugador.x = float(jugador.rect.x)

    def actualizar(self, dt, jugador=None):
        """Avanza la maquina de estados de aviso, emergencia y retraccion."""
        self.recien_aviso = False
        self.recien_armado = False
        if self.tiempo_temblor > 0:
            self.tiempo_temblor = max(0.0, self.tiempo_temblor - dt)
        if self.enfriamiento > 0:
            self.enfriamiento = max(0.0, self.enfriamiento - dt)

        if self.estado == "aviso":
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "emergiendo"
        elif self.estado == "emergiendo":
            self.progreso = min(1.0, self.progreso + dt * 3.8)
            self._actualizar_rect()
            self._desplazar_jugador_al_emerger(jugador)
            if self.progreso >= 1.0:
                self.progreso = 1.0
                self.estado = "armado"
                self.temporizador = self.duracion_armado
                self.recien_armado = True
                self._actualizar_rect()
        elif self.estado == "armado":
            self.temporizador -= dt
            self._actualizar_rect()
            if self.temporizador <= 0:
                self.estado = "retrayendo"
        elif self.estado == "retrayendo":
            self.progreso = max(0.0, self.progreso - dt * 3.8)
            self._actualizar_rect()
            if self.progreso <= 0.0:
                self.progreso = 0.0
                self.estado = "oculto"
                self._actualizar_rect()

    def _dibujar_aviso_suelo(self, surface, sx, by, tiempo):
        # Lineas turquesa y destello sobre la ranura antes de emerger
        pulso = 0.5 + 0.5 * math.sin(tiempo * 24.0)
        col_av = (255, int(150 + 80 * pulso), 70)
        pygame.draw.line(surface, col_av, (sx + 2, by - 2), (sx + self.ancho - 3, by - 2), 2)
        for i_b in range(3):
            h_guia = 12 + i_b * 10 + int(pulso * 6)
            gx = sx + 6 + i_b * 10
            pygame.draw.line(surface, (92, 220, 200), (gx, by - 3), (gx, by - h_guia), 1)

    def _dibujar_bloque(self, surface, b_rect, b_top, b_bottom, b_h):
        # Dibuja un modulo acorazado con remaches y runa central
        col_cuerpo = (68, 62, 82) if self.tiempo_temblor <= 0 else (150, 142, 165)
        pygame.draw.rect(surface, col_cuerpo, b_rect, border_radius=3)
        pygame.draw.rect(surface, (32, 28, 42), b_rect, 2, border_radius=3)

        pygame.draw.line(surface, (118, 124, 145), (b_rect.x + 5, b_top + 2), (b_rect.x + 5, b_bottom - 2), 2)
        pygame.draw.line(surface, (118, 124, 145), (b_rect.right - 6, b_top + 2), (b_rect.right - 6, b_bottom - 2), 2)
        pygame.draw.line(surface, ORO_LITÚRGICO, (b_rect.x + 2, b_top + 1), (b_rect.right - 3, b_top + 1), 1)
        if b_h >= 16:
            cy_b = b_top + b_h // 2
            col_runa = (255, 220, 110) if self.tiempo_temblor > 0 else (92, 220, 200)
            pygame.draw.circle(surface, col_runa, (b_rect.centerx, cy_b), 3)
            pygame.draw.circle(surface, (24, 20, 32), (b_rect.centerx, cy_b), 3, 1)

    def dibujar(self, surface, camara, tiempo=0.0):
        """Renderiza la ranura del piso, el aviso o la pila de bloques."""
        base_screen = camara.aplicar_rect(pygame.Rect(self.x, self.base_y - 4, self.ancho, 6))
        sx, by = base_screen.x, base_screen.y + 4
        pygame.draw.rect(surface, (28, 24, 34), (sx - 2, by - 3, self.ancho + 4, 5), border_radius=1)
        zocalo = (sx - 2, by - 3, self.ancho + 4, 5)
        pygame.draw.rect(surface, (112, 92, 60), zocalo, 1, border_radius=1)

        if self.estado == "aviso":
            self._dibujar_aviso_suelo(surface, sx, by, tiempo)
            return
        if self.rect.height <= 2:
            return

        rect_cam = camara.aplicar_rect(self.rect)
        ox = int(math.sin(tiempo * 55.0) * 2) if self.tiempo_temblor > 0 else 0
        rx, ry, rw, rh = rect_cam.x + ox, rect_cam.y, rect_cam.width, rect_cam.height
        n_bloques = max(1, math.ceil(rh / float(TILE)))
        for b_idx in range(n_bloques):
            b_bottom = by - b_idx * TILE
            b_top = max(ry, b_bottom - TILE)
            b_h = max(4, b_bottom - b_top)
            self._dibujar_bloque(surface, pygame.Rect(rx + 2, b_top, rw - 4, b_h), b_top, b_bottom, b_h)
