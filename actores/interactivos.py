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
    # Farol que sirve como punto de control

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.activo = False
        self.tier = 0
        self.tiempo_encendido = 0.0

    def reiniciar(self):
        self.activo = False
        self.tier = 0
        self.tiempo_encendido = 0.0

    def actualizar_dt(self, dt):
        """Avanza el temporizador visual de ignición del farol."""
        if self.tiempo_encendido > 0:
            self.tiempo_encendido = max(0.0, self.tiempo_encendido - dt)

    def actualizar(self, jugador):
        if not self.activo and self.rect.colliderect(jugador.rect):
            self.activo = True
            self.tiempo_encendido = 0.65
            return True
        return False

    def dibujar(self, surface, camara, tiempo):
        rect = camara.aplicar_rect(self.rect)
        cx = rect.centerx
        base_y = rect.bottom

        # Poste de hierro gótico
        pygame.draw.rect(surface, (45, 42, 50), (cx - 2, base_y - 24, 4, 24))
        # Base de piedra
        pygame.draw.rect(surface, (60, 56, 68), (cx - 6, base_y - 4, 12, 4))
        # Jaula del farol con cristal sutilmente iluminado
        pygame.draw.rect(surface, (75, 72, 88), (cx - 7, base_y - 32, 14, 10), 1)
        # Techo piramidal
        pygame.draw.polygon(surface, (80, 75, 92), [(cx - 8, base_y - 32), (cx + 8, base_y - 32), (cx, base_y - 38)])

        flame_y = base_y - 27
        pulso = 0.5 + 0.5 * math.sin(tiempo * 8 + cx * 0.05)
        if self.activo:
            step = int(pulso * 7)
            brillo = obtener_aura_farol(self.tier, step)
            bc = brillo.get_width() // 2
            surface.blit(brillo, (cx - bc, flame_y - bc))

            if self.tier >= 3:
                color_nucleo = (255, 245, 180)
                color_llama = (255, 205, 90)
                color_destello = (255, 225, 130)
            else:
                color_nucleo = (240, 255, 255)
                color_llama = (120, 220, 255)
                color_destello = (130, 235, 255)

            radio_llama = int((4 if self.tier >= 3 else 3) + pulso * 2)
            pygame.draw.circle(surface, color_llama, (cx, flame_y), radio_llama)
            pygame.draw.circle(surface, color_nucleo, (cx, flame_y), max(1, radio_llama - 2))

            if self.tiempo_encendido > 0:
                prog = 1.0 - (self.tiempo_encendido / 0.65)
                r_onda = int(6 + prog * 30)
                alfa_onda = max(0, int(230 * (1.0 - prog)))
                onda_s = pygame.Surface((r_onda * 2 + 6, r_onda * 2 + 6), pygame.SRCALPHA)
                oc = r_onda + 3
                col_ring = (*color_destello, alfa_onda)
                pygame.draw.circle(onda_s, col_ring, (oc, oc), r_onda, 2)
                if r_onda > 10:
                    pygame.draw.circle(onda_s, (240, 255, 255, alfa_onda // 2), (oc, oc), r_onda - 5, 1)
                # Destello vertical y horizontal durante la ignición del farol
                rayo = int(14 * (1.0 - prog) + 4)
                pygame.draw.line(onda_s, (245, 255, 255, alfa_onda), (oc - rayo, oc), (oc + rayo, oc), 2)
                pygame.draw.line(onda_s, col_ring, (oc, oc - rayo), (oc, oc + rayo), 2)
                surface.blit(onda_s, (cx - oc, flame_y - oc))
        else:
            # Vela azul tenue dentro del farol antes de la consagración
            step_p = int(pulso * 7)
            halo_vela = obtener_halo_vela_farol(step_p)
            hc = halo_vela.get_width() // 2
            surface.blit(halo_vela, (cx - hc, flame_y - hc))
            # Cirio interior y flama tipo vela en azul
            pygame.draw.rect(surface, (145, 165, 185), (cx - 1, base_y - 25, 2, 3))
            vaiven = int(round((pulso - 0.5) * 2))
            pts_llama_azul = [
                (cx + vaiven, base_y - 32),
                (cx + 3, base_y - 27),
                (cx, base_y - 24),
                (cx - 3, base_y - 27),
            ]
            pygame.draw.polygon(surface, (65, 180, 255), pts_llama_azul)
            pygame.draw.circle(surface, (205, 244, 255), (cx, base_y - 27), 1)


#---- Clase LosaQuebradiza ----#
class LosaQuebradiza:
    """Losa de osario quebradiza que colapsa tras 0.40s de contacto y reaparece tras 2.5s."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.activa = True
        self.pisada = False
        self.tiempo_quiebre = 0.0
        self.tiempo_reconstruccion = 0.0
        self.vibracion_offset = 0.0
        self.recien_quebrada = False
        self.recien_reconstruida = False

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.activa = True
        self.pisada = False
        self.tiempo_quiebre = 0.0
        self.tiempo_reconstruccion = 0.0
        self.vibracion_offset = 0.0
        self.recien_quebrada = False
        self.recien_reconstruida = False

    def pisar(self):
        """Activa el temporizador de colapso si la losa está firme."""
        if self.activa and not self.pisada:
            self.pisada = True

    def actualizar(self, dt, jugador=None):
        self.recien_quebrada = False
        self.recien_reconstruida = False

        # Si se pasa jugador, comprobar si está apoyado sobre la losa
        if jugador is not None and self.activa:
            if (
                jugador.en_suelo
                and abs(jugador.rect.bottom - self.rect.top) <= 2
                and jugador.rect.right > self.rect.left
                and jugador.rect.left < self.rect.right
            ):
                self.pisar()

        if self.activa:
            if self.pisada:
                self.tiempo_quiebre += dt
                # Vibración telegrafiada ±2 px
                self.vibracion_offset = math.sin(self.tiempo_quiebre * 50.0) * 2.0
                if self.tiempo_quiebre >= LOSA_TIEMPO_QUIEBRE:
                    self.activa = False
                    self.pisada = False
                    self.tiempo_quiebre = 0.0
                    self.tiempo_reconstruccion = LOSA_TIEMPO_RECONSTRUCCION
                    self.vibracion_offset = 0.0
                    self.recien_quebrada = True
            else:
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

    def dibujar(self, surface, camara, tiempo=0.0):
        # Si no está activa, dibujamos una silueta espectral translúcida cacheada
        if not self.activa:
            rect = camara.aplicar_rect(self.rect)
            step = int((0.5 + 0.5 * math.sin(tiempo * 6.0)) * 7)
            fantasma = obtener_fantasma_losa(rect.width, rect.height, step)
            surface.blit(fantasma, rect.topleft)
            return

        rect = camara.aplicar_rect(self.rect)
        rx = rect.x + int(self.vibracion_offset)
        ry = rect.y
        w = rect.width
        h = rect.height

        # Base de losa de piedra gótica / osario
        color_base = PIEDRA_FRIA
        pygame.draw.rect(surface, color_base, (rx, ry, w, h), border_radius=2)
        # Borde superior iluminado (salitre / marfil)
        color_borde = HUESO_MARFIL if self.pisada else SALITRE_CRIPTA
        pygame.draw.line(surface, color_borde, (rx + 1, ry), (rx + w - 2, ry), 2)
        # Borde inferior sombra
        pygame.draw.line(surface, PIEDRA_OSCURA, (rx + 1, ry + h - 1), (rx + w - 2, ry + h - 1), 2)

        # Base hueca dentada para distinguirla al instante de un bloque sólido normal
        c_hueco = (10, 8, 14)
        for dent_x in range(rx + 4, rx + w - 4, 8):
            pygame.draw.rect(surface, c_hueco, (dent_x, ry + h - 3, 4, 3))

        # Grietas telegrafiadas si fue pisada
        if self.pisada:
            avance = min(1.0, self.tiempo_quiebre / LOSA_TIEMPO_QUIEBRE)
            color_grieta = (30, 25, 35)
            mid_x = rx + w // 2
            pygame.draw.line(surface, color_grieta, (mid_x, ry + 2), (mid_x - int(5 * avance), ry + int(h * 0.6 * avance)), 1)
            pygame.draw.line(surface, color_grieta, (mid_x - int(5 * avance), ry + int(h * 0.6 * avance)), (mid_x + int(4 * avance), ry + int(h * 0.9 * avance)), 1)
            if w > 32:
                for off in (16, w - 16):
                    gx = rx + off
                    pygame.draw.line(surface, color_grieta, (gx, ry + 2), (gx + int(3 * avance), ry + int(h * 0.5 * avance)), 1)
        else:
            # Grietas diagonales visibles en reposo (aviso telegrafiado ámbar/turquesa)
            c_grieta_aviso = (216, 180, 104)  # Ámbar litúrgico
            c_grieta_sec = (92, 190, 174)     # Turquesa ánima
            pygame.draw.line(surface, c_grieta_aviso, (rx + 6, ry + 2), (rx + 12, ry + 8), 1)
            pygame.draw.line(surface, c_grieta_sec, (rx + 12, ry + 8), (rx + 10, ry + h - 4), 1)
            pygame.draw.line(surface, c_grieta_aviso, (rx + w - 8, ry + 2), (rx + w - 14, ry + 10), 1)
            pygame.draw.line(surface, c_grieta_sec, (rx + w - 14, ry + 10), (rx + w - 11, ry + h - 4), 1)
            if w > 32:
                pygame.draw.line(surface, c_grieta_aviso, (rx + w // 2 - 4, ry + 3), (rx + w // 2 + 2, ry + 9), 1)
                pygame.draw.line(surface, c_grieta_sec, (rx + w // 2 + 2, ry + 9), (rx + w // 2, ry + h - 4), 1)


#---- Clase IncensarioRebote ----#
class IncensarioRebote:
    """Campana / Incensario de resonancia suspendido en el aire que permite rebotar y recargar Dash."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.cooldown = 0.0
        self.tiempo_repique = 0.0
        self.activo = True

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.cooldown = 0.0
        self.tiempo_repique = 0.0
        self.activo = True

    def puede_rebotar(self):
        return self.cooldown <= 0.0

    def activar_rebote(self):
        """Dispara el repique y el cooldown de rebote."""
        self.cooldown = INCENSARIO_COOLDOWN
        self.tiempo_repique = 0.45
        return True

    def actualizar(self, dt):
        if self.cooldown > 0:
            self.cooldown = max(0.0, self.cooldown - dt)
        if self.tiempo_repique > 0:
            self.tiempo_repique = max(0.0, self.tiempo_repique - dt)

    def dibujar(self, surface, camara, tiempo=0.0):
        rect = camara.aplicar_rect(self.rect)
        cx = rect.centerx
        cy = rect.centery

        # Oscilación visual si está repicando
        offset_osc = 0.0
        if self.tiempo_repique > 0:
            offset_osc = math.sin(self.tiempo_repique * 30.0) * (4.0 * (self.tiempo_repique / 0.45))

        centro_campana_x = cx + int(offset_osc)
        centro_campana_y = cy
        repicando = self.tiempo_repique > 0

        # Halo turquesa pulsante del incensario cacheado
        pulso = 0.5 + 0.5 * math.sin(tiempo * 5.0 + cx * 0.1)
        step = int(pulso * 7)
        halo = obtener_halo_campana(repicando, step)
        hr = halo.get_width() // 2
        surface.blit(halo, (centro_campana_x - hr, centro_campana_y - hr))

        # Cadena de suspensión de hierro que sube hacia el techo
        y_cadena_fin = centro_campana_y - 14
        y_cadena_inicio = y_cadena_fin - 22
        pygame.draw.line(surface, (28, 24, 34), (centro_campana_x, y_cadena_inicio), (centro_campana_x, y_cadena_fin), 3)
        pygame.draw.line(surface, (72, 68, 82), (centro_campana_x, y_cadena_inicio), (centro_campana_x, y_cadena_fin), 1)
        for y_eslabon in range(y_cadena_inicio, y_cadena_fin, 5):
            pygame.draw.circle(surface, (120, 115, 130), (centro_campana_x, y_eslabon), 2, 1)

        # Yugo/soporte arqueado de hierro forjado con remaches de bronce
        yugo_rect = (centro_campana_x - 9, centro_campana_y - 15, 18, 5)
        pygame.draw.rect(surface, (26, 22, 32), yugo_rect, border_radius=2)
        pygame.draw.rect(surface, (88, 82, 98), yugo_rect, 1, border_radius=2)
        pygame.draw.circle(surface, ORO_LITÚRGICO, (centro_campana_x - 7, centro_campana_y - 13), 2)
        pygame.draw.circle(surface, ORO_LITÚRGICO, (centro_campana_x + 7, centro_campana_y - 13), 2)
        pygame.draw.rect(surface, (175, 130, 55), (centro_campana_x - 4, centro_campana_y - 11, 8, 3), border_radius=1)

        # Campana de bronce bruñido facetada
        puntos_campana = [
            (centro_campana_x - 4, centro_campana_y - 8),
            (centro_campana_x + 4, centro_campana_y - 8),
            (centro_campana_x + 10, centro_campana_y + 4),
            (centro_campana_x + 12, centro_campana_y + 8),
            (centro_campana_x - 12, centro_campana_y + 8),
            (centro_campana_x - 10, centro_campana_y + 4),
        ]
        color_cuerpo = (212, 168, 72) if repicando else (158, 118, 52)
        pygame.draw.polygon(surface, color_cuerpo, puntos_campana)
        pygame.draw.polygon(surface, (72, 48, 22), puntos_campana, 1)

        # Bisel especular lateral izquierdo (reflejo litúrgico de luz)
        color_bisel = HUESO_MARFIL if repicando else ORO_LITÚRGICO
        pygame.draw.line(surface, color_bisel, (centro_campana_x - 3, centro_campana_y - 7), (centro_campana_x - 9, centro_campana_y + 4), 1)

        # Bandas de relieve litúrgico grabadas
        c_relieve = ORO_LITÚRGICO if repicando else (98, 72, 34)
        pygame.draw.line(surface, c_relieve, (centro_campana_x - 5, centro_campana_y - 2), (centro_campana_x + 5, centro_campana_y - 2), 1)
        pygame.draw.line(surface, c_relieve, (centro_campana_x - 8, centro_campana_y + 3), (centro_campana_x + 8, centro_campana_y + 3), 1)

        # Sombra interior bajo el labio de la campana
        pygame.draw.line(surface, (40, 26, 16), (centro_campana_x - 11, centro_campana_y + 8), (centro_campana_x + 11, centro_campana_y + 8), 2)

        # Badajo oscilante con cristal de resonancia en TURQUESA_ÁNIMA
        badajo_x = centro_campana_x + int(offset_osc * 1.6)
        badajo_y = centro_campana_y + 9
        pygame.draw.line(surface, (60, 52, 68), (centro_campana_x, centro_campana_y + 4), (badajo_x, badajo_y), 2)
        color_cristal = (195, 255, 245) if repicando else TURQUESA_ÁNIMA
        pygame.draw.circle(surface, color_cristal, (badajo_x, badajo_y), 3)
        pygame.draw.circle(surface, BLANCO if repicando else (180, 240, 230), (badajo_x, badajo_y), 1)

        # Onda expansiva doble (anillo exterior turquesa + anillo interior áureo)
        if repicando:
            prog = int((1.0 - (self.tiempo_repique / 0.45)) * 10)
            onda_surf = obtener_onda_campana(prog)
            ow = onda_surf.get_width()
            surface.blit(onda_surf, (centro_campana_x - ow // 2, centro_campana_y - ow // 2))


#---- Clase BloqueCripta ----#
class BloqueCripta:
    """Bloque de cripta destructible ('=') bajo los pies del Custodio en Fase 3."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.roto = False

    def reiniciar(self):
        self.roto = False

    def romper(self):
        """Rompe el bloque de cripta al recibir el pisotón del Custodio."""
        if self.roto:
            return False
        self.roto = True
        return True

    def dibujar(self, surface, camara, tiempo=0.0):
        rect = camara.aplicar_rect(self.rect)
        if self.roto:
            return
        # Piedra funeraria grabada con sello carmesí/violeta tenue para distinguirla del muro sólido
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
    """Rastrillo de hierro forjado que sella la cámara del Custodio durante el combate."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.cerrada = False
        self.progreso = 0.0

    def cerrar(self):
        """Sella la compuerta de la cámara del jefe."""
        self.cerrada = True

    def abrir(self):
        """Abre la compuerta al caer el jefe."""
        self.cerrada = False

    def reiniciar(self):
        self.cerrada = False
        self.progreso = 0.0

    def actualizar(self, dt):
        objetivo = 1.0 if self.cerrada else 0.0
        if self.progreso < objetivo:
            self.progreso = min(1.0, self.progreso + dt * 6.5)
        elif self.progreso > objetivo:
            self.progreso = max(0.0, self.progreso - dt * 3.5)

    def dibujar(self, surface, camara, tiempo=0.0):
        vis = self.progreso if self.cerrada else max(0.18, self.progreso)
        rect = camara.aplicar_rect(self.rect)
        alto_vis = max(8, int(rect.height * vis))
        barra_rect = pygame.Rect(rect.x + 4, rect.y, rect.width - 8, alto_vis)

        # Marco de hierro superior
        pygame.draw.rect(surface, (36, 30, 42), (rect.x + 2, rect.y, rect.width - 4, 5))
        pygame.draw.rect(surface, (112, 92, 60), (rect.x + 2, rect.y, rect.width - 4, 5), 1)

        # Barrotes verticales de acero forjado con puntas de lanza abajo
        for bx in (barra_rect.x + 4, barra_rect.centerx, barra_rect.right - 5):
            pygame.draw.line(surface, (55, 52, 66), (bx, rect.y + 4), (bx, rect.y + alto_vis - 2), 3)
            pygame.draw.line(surface, (140, 146, 165), (bx - 1, rect.y + 4), (bx - 1, rect.y + alto_vis - 4), 1)
        for by in range(rect.y + 14, rect.y + alto_vis - 4, 18):
            pygame.draw.line(surface, (42, 38, 52), (barra_rect.x, by), (barra_rect.right, by), 3)

        if self.cerrada:
            # Sello rúnico carmesí pulsante cuando la arena está trabada
            pulso = int(160 + 80 * math.sin(tiempo * 7.0))
            pygame.draw.circle(surface, (pulso, 45, 70), (barra_rect.centerx, rect.y + alto_vis // 2), 4)
            pygame.draw.circle(surface, ORO_LITÚRGICO, (barra_rect.centerx, rect.y + alto_vis // 2), 4, 1)


#---- Clase MuroMovilCompuerta ----#
class MuroMovilCompuerta:
    """Muro móvil tipo compuerta que se arma bloque a bloque de abajo hacia arriba en la arena del Mini-Boss."""

    def __init__(self, x, base_y, ancho=TILE, alto_max=3 * TILE):
        self.x = int(x)
        self.base_y = int(base_y)
        self.ancho = int(ancho)
        self.alto_max = int(alto_max)
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

    def _actualizar_rect(self):
        # Cuantización suave por tercios para enfatizar el armado de abajo hacia arriba en 3 bloques
        if self.progreso <= 0.02:
            alto_vis = 0
        else:
            tercios = self.progreso * 3.0
            bloque_idx = int(min(2.0, math.floor(tercios)))
            frac = tercios - bloque_idx
            frac_suave = min(1.0, frac * 1.25)
            progreso_esc = (bloque_idx + frac_suave) / 3.0
            alto_vis = max(6, int(round(self.alto_max * min(1.0, progreso_esc))))
        self.rect = pygame.Rect(self.x, self.base_y - alto_vis, self.ancho, alto_vis)

    def es_solido(self):
        return self.estado in ("emergiendo", "armado") and self.rect.height >= 12

    def puede_activarse(self):
        return self.estado == "oculto" and self.enfriamiento <= 0.0 and not self.usado_ciclo

    def activar(self, duracion_aviso=0.16, duracion_armado=1.5):
        """Inicia la secuencia de emergencia de abajo hacia arriba si no está en enfriamiento."""
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
        if self.estado not in ("oculto", "retrayendo"):
            self.estado = "retrayendo"

    def recibir_impacto(self):
        """Absorbe el choque de la embestida del Carcelero, entra en enfriamiento y se retrae."""
        self.tiempo_temblor = 0.30
        self.enfriamiento = 9.0
        self.usado_ciclo = True
        if self.estado in ("emergiendo", "armado"):
            self.progreso = min(1.0, max(0.75, self.progreso))
            self.estado = "retrayendo"
            self._actualizar_rect()

    def reiniciar(self):
        self.estado = "oculto"
        self.progreso = 0.0
        self.temporizador = 0.0
        self.tiempo_temblor = 0.0
        self.enfriamiento = 0.0
        self.usado_ciclo = False
        self.recien_aviso = False
        self.recien_armado = False
        self.rect = pygame.Rect(self.x, self.base_y, self.ancho, 0)

    def actualizar(self, dt, jugador=None):
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
            if jugador is not None and self.rect.height > 0 and jugador.rect.colliderect(self.rect):
                # Si el jugador está sobre la ranura mientras sube el muro, elevarlo con la compuerta
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

    def dibujar(self, surface, camara, tiempo=0.0):
        base_screen = camara.aplicar_rect(pygame.Rect(self.x, self.base_y - 4, self.ancho, 6))
        sx = base_screen.x
        by = base_screen.y + 4

        # Zócalo / ranura mecánica en el suelo de la arena
        pygame.draw.rect(surface, (28, 24, 34), (sx - 2, by - 3, self.ancho + 4, 5), border_radius=1)
        pygame.draw.rect(surface, (112, 92, 60), (sx - 2, by - 3, self.ancho + 4, 5), 1, border_radius=1)

        if self.estado == "aviso":
            pulso = 0.5 + 0.5 * math.sin(tiempo * 24.0)
            col_av = (255, int(150 + 80 * pulso), 70)
            pygame.draw.line(surface, col_av, (sx + 2, by - 2), (sx + self.ancho - 3, by - 2), 2)
            for i_b in range(3):
                h_guia = 12 + i_b * 10 + int(pulso * 6)
                gx = sx + 6 + i_b * 10
                pygame.draw.line(surface, (92, 220, 200), (gx, by - 3), (gx, by - h_guia), 1)
            return

        if self.rect.height <= 2:
            return

        rect_cam = camara.aplicar_rect(self.rect)
        ox = int(math.sin(tiempo * 55.0) * 2) if self.tiempo_temblor > 0 else 0
        rx = rect_cam.x + ox
        ry = rect_cam.y
        rw = rect_cam.width
        rh = rect_cam.height

        # Dibujar los módulos apilados de abajo hacia arriba (hasta 3 bloques de alto TILE)
        n_bloques = max(1, math.ceil(rh / float(TILE)))
        for b_idx in range(n_bloques):
            b_bottom = by - b_idx * TILE
            b_top = max(ry, b_bottom - TILE)
            b_h = max(4, b_bottom - b_top)
            b_rect = pygame.Rect(rx + 2, b_top, rw - 4, b_h)

            # Cuerpo de piedra acorazada y marco de hierro forjado
            col_cuerpo = (68, 62, 82) if self.tiempo_temblor <= 0 else (150, 142, 165)
            pygame.draw.rect(surface, col_cuerpo, b_rect, border_radius=3)
            pygame.draw.rect(surface, (32, 28, 42), b_rect, 2, border_radius=3)

            # Costillas verticales de compuerta y remaches de bronce
            pygame.draw.line(surface, (118, 124, 145), (b_rect.x + 5, b_top + 2), (b_rect.x + 5, b_bottom - 2), 2)
            pygame.draw.line(surface, (118, 124, 145), (b_rect.right - 6, b_top + 2), (b_rect.right - 6, b_bottom - 2), 2)
            pygame.draw.line(surface, ORO_LITÚRGICO, (b_rect.x + 2, b_top + 1), (b_rect.right - 3, b_top + 1), 1)

            if b_h >= 16:
                cy_b = b_top + b_h // 2
                col_runa = (255, 220, 110) if self.tiempo_temblor > 0 else (92, 220, 200)
                pygame.draw.circle(surface, col_runa, (b_rect.centerx, cy_b), 3)
                pygame.draw.circle(surface, (24, 20, 32), (b_rect.centerx, cy_b), 3, 1)
