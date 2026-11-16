#---- Importamos librerias y configuracion ----#
import math
import random

import pygame

from actores.estampas import obtener_aura_custodio
from actores.utilidades import limitar
from config import (
    BLANCO,
    CARMESÍ_SANGRE,
    FAROL_CÁLIDO,
    HUESO_MARFIL,
    JEFE_CARGA_VELOCIDAD,
    JEFE_VELOCIDAD,
    JEFE_VIDA,
    JEFE_VULN_FASE2,
    MARRON_OSCURO,
    NEGRO_NOCHE,
    ORO_LITÚRGICO,
    TILE,
)

#---- Constantes locales ----#
ESTADOS_FASE3 = (
    "cambio_f3",
    "espera_smb3",
    "telegrafia_smb3",
    "salto_smb3",
    "aterrizaje_smb3",
    "cayendo_abismo",
)
COLORES_TELEGRAFIA = {
    "telegrafia_embate": (245, 200, 80),
    "telegrafia_smb3": (185, 85, 255),
    "telegrafia_carga": CARMESÍ_SANGRE,
}


#---- Clase OndaCustodio ----#
class OndaCustodio:
    """Onda de huesos que corre por el piso y obliga a saltar o dashar."""

    def __init__(self, x, y, direccion, velocidad):
        self.rect = pygame.Rect(int(x) - 10, int(y) - 22, 20, 22)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = direccion
        self.velocidad = velocidad
        self.vida = 3.4
        self.viva = True

    def actualizar(self, dt):
        """Avanza la onda por el piso hasta agotar su tiempo de vida."""
        self.vida -= dt
        if self.vida <= 0:
            self.viva = False
            return
        self.x += self.direccion * self.velocidad * dt
        self.rect.x = round(self.x)

    def _dibujar_craneo(self, surface, cx, cy, signo):
        # Dibuja el craneo rodante, ojos carmesi y dientes
        pygame.draw.circle(surface, HUESO_MARFIL, (cx, cy - 2), 7)
        pygame.draw.rect(surface, HUESO_MARFIL, (cx - 4, cy + 1, 8, 4), border_radius=1)
        pygame.draw.circle(surface, NEGRO_NOCHE, (cx, cy - 2), 7, 1)

        ojo_dx = signo * 2
        for ox in (cx - 2 + ojo_dx, cx + 3 + ojo_dx):
            pygame.draw.circle(surface, NEGRO_NOCHE, (ox, cy - 3), 2)
            pygame.draw.circle(surface, CARMESÍ_SANGRE, (ox, cy - 3), 1)
        pygame.draw.rect(surface, NEGRO_NOCHE, (cx - 1 + ojo_dx, cy, 2, 2))
        for dx_diente in (-3, -1, 1, 3):
            p0, p1 = (cx + dx_diente, cy + 2), (cx + dx_diente, cy + 4)
            pygame.draw.line(surface, NEGRO_NOCHE, p0, p1, 1)

    def dibujar(self, surface, camara, tiempo):
        """Renderiza el craneo rodante y la estela osea de la onda."""
        if not self.viva:
            return
        rect = camara.aplicar_rect(self.rect)
        cx = rect.centerx
        cy = rect.centery + 1
        signo = self.direccion

        sombra_box = (rect.x - 4, rect.bottom - 4, rect.width + 8, 5)
        pygame.draw.ellipse(surface, (28, 22, 26), sombra_box)
        self._dibujar_craneo(surface, cx, cy, signo)

        pulso = int(2 * math.sin(tiempo * 20 + rect.x * 0.08))
        arco_box = (rect.x - 6, rect.y - 4 - pulso, rect.width + 12, rect.height + 8)
        pygame.draw.arc(surface, (195, 185, 165), arco_box, 0.15, math.pi - 0.15, 2)
        for i in range(2):
            px = cx - signo * (6 + i * 5)
            p_fin = (px - signo * 4, rect.top + 6 + i * 2)
            pygame.draw.line(surface, HUESO_MARFIL, (px, rect.bottom - 2), p_fin, 2)


#---- Clase Custodio ----#
class Custodio:
    """Jefe final de 3 fases con embestida, embate ascendente y destruccion del piso."""

    def __init__(self, rect, minimo_x, maximo_x):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.minimo_x = int(minimo_x)
        self.maximo_x = int(maximo_x)
        self.reiniciar()

    def reiniciar(self):
        """Restaura estado, fase y contadores del Custodio."""
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.y_suelo = float(self.inicial_rect.y)
        self.vy = 0.0
        self.vx_smb3 = 0.0
        self.vida = JEFE_VIDA
        self.fase = 1
        self.estado = "espera"
        self.temporizador = 1.25
        self.vulnerable = False
        self.vivo = True
        self.direccion = -1
        self.golpes_fase = 0
        self.saltos_smb3 = 0
        self.quiebres_sismicos = 0
        self.quiebre_usado_en_salto = False
        self._limpiar_senales_frame()
        self.carga_activa = False
        self.tiempo_jugador_arriba = 0.0
        self.tiempo_muerte = 0.0
        self.tiempo_flash = 0.0

    def _limpiar_senales_frame(self):
        # Reiniciamos banderas de un solo frame al iniciar cada actualizacion
        self.recien_golpeado = False
        self.ondas_recien = False
        self.aviso_recien = False
        self.embate_recien = False
        self.aplasto_suelo_recien = False
        self.quiebre_sismico_recien = False
        self.en_abismo_recien = False
        self.cambio_fase3_recien = False

    def rect_embate(self):
        """Hitbox vertical del embate ascendente contra campanas en fases 1 y 2."""
        if self.estado != "embate":
            return None
        alto = int(3.5 * TILE)
        ancho = 80
        return pygame.Rect(self.rect.centerx - ancho // 2, self.rect.top - alto, ancho, alto + 12)

    def rect_aplastamiento(self):
        """Franja bajo los pies para quebrar una capa de criptas por impacto."""
        ancho_preciso = 28
        return pygame.Rect(
            self.rect.centerx - ancho_preciso // 2,
            self.rect.bottom - 2,
            ancho_preciso,
            16,
        )

    def rect_soporte_central_f3(self):
        """Columna central de soporte a traves de las 4 capas de criptas en fase 3."""
        ancho_nucleo = 28
        return pygame.Rect(
            self.rect.centerx - ancho_nucleo // 2,
            int(self.y_suelo) + self.rect.height - 2,
            ancho_nucleo,
            4 * TILE + 12,
        )

    def puede_quiebre_sismico_f3(self):
        """Indica si el Custodio esta en la ventana post-salto de quiebre sismico."""
        return (
            self.vivo
            and self.fase >= 3
            and self.estado == "aterrizaje_smb3"
            and not getattr(self, "quiebre_usado_en_salto", False)
        )

    def recibir_quiebre_sismico_f3(self, rango_mejorado=False):
        """En fase 3, golpear con guadana al aterrizar quiebra una capa extra."""
        if not self.puede_quiebre_sismico_f3() or not rango_mejorado:
            return False
        self.quiebres_sismicos += 1
        self.quiebre_usado_en_salto = True
        self.quiebre_sismico_recien = True
        self.aplasto_suelo_recien = True
        self.tiempo_flash = 0.08
        self.temporizador = min(self.temporizador, 0.18)
        return True

    def matar_por_abismo(self):
        """Culmina la fase 3 cuando cae al abismo que abrio bajo sus pies."""
        self.vivo = False
        self.estado = "muerto"
        self.tiempo_muerte = 0.0

    def _aplicar_dano(self):
        # Descuenta vida y maneja transicion a fase 2 y fase 3
        self.vida -= 1
        self.golpes_fase += 1
        self.vulnerable = False
        self.recien_golpeado = True
        self.carga_activa = False
        self.tiempo_flash = 0.06

        if self.vida <= 0:
            self.vida = 0
            self.fase = 3
            self.golpes_fase = 0
            self.estado = "cambio_f3"
            self.temporizador = 1.15
            self.cambio_fase3_recien = True
            self.aviso_recien = True
            self.vy = 0.0
            self.vx_smb3 = 0.0
            return True

        if self.golpes_fase >= 3 and self.fase < 2:
            self.fase += 1
            self.golpes_fase = 0
            self.estado = "cambio"
            self.temporizador = 1.20
        else:
            vuln_time = JEFE_VULN_FASE2 if self.fase >= 2 else 0.55
            self.estado = "recuperacion"
            self.temporizador = vuln_time
        return True

    def recibir_golpe_pala(self, rango_mejorado=False):
        """Aplica danio con pala en fase 1 o con guadana en fase 2."""
        if not self.vivo or not self.vulnerable or self.fase >= 3:
            return False
        if self.fase == 2 and not rango_mejorado:
            return False
        return self._aplicar_dano()

    def recibir_pisaton(self, rango_mejorado=False):
        """Aplica danio por pisoton en fase 1 o con guadana en fase 2."""
        if not self.vivo or not self.vulnerable or self.fase >= 3:
            return False
        if self.fase == 2 and not rango_mejorado:
            return False
        return self._aplicar_dano()

    def _patrullar_fuera_de_rango(self, dt):
        # Patrulla tranquila en la catedral mientras el jugador esta lejos
        self.tiempo_jugador_arriba = 0.0
        self.x += self.direccion * (JEFE_VELOCIDAD * 0.65) * dt
        if self.x <= self.minimo_x:
            self.x = float(self.minimo_x)
            self.direccion = 1
        elif self.x >= self.maximo_x:
            self.x = float(self.maximo_x)
            self.direccion = -1
        self.rect.x = round(self.x)

    def _mover_hacia_x(self, dt, jugador, factor_vel):
        # Acerca horizontalmente al Custodio hacia el jugador dentro de la arena
        self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
        nuevo_x = self.x + self.direccion * (JEFE_VELOCIDAD * factor_vel) * dt
        self.x = max(self.minimo_x, min(self.maximo_x, nuevo_x))
        self.rect.x = round(self.x)

    def _actualizar_espera(self, dt, jugador):
        # Patrulla, responde si el jugador campea arriba y elige proximo ataque
        dist_x_j = abs(jugador.rect.centerx - self.rect.centerx)
        dist_y_j = abs(jugador.rect.centery - self.rect.centery)
        en_rango = (
            (dist_y_j <= 14 * TILE and dist_x_j <= 28 * TILE)
            or (self.vida < JEFE_VIDA and dist_y_j <= 14 * TILE)
        )
        if not en_rango:
            self._patrullar_fuera_de_rango(dt)
            return

        sobre_jefe = (
            self.fase in (1, 2)
            and jugador.rect.bottom <= self.rect.top + 10
            and dist_x_j <= 2.5 * TILE
        )
        if sobre_jefe:
            if dist_x_j > 8:
                self._mover_hacia_x(dt, jugador, 1.4)
            self.tiempo_jugador_arriba += dt
            if self.tiempo_jugador_arriba >= 0.60:
                self.tiempo_jugador_arriba = 0.0
                self.estado = "telegrafia_embate"
                self.temporizador = 0.45
                self.aviso_recien = True
                return
        else:
            self.tiempo_jugador_arriba = max(0.0, self.tiempo_jugador_arriba - dt * 1.5)
            if dist_x_j > 60:
                self._mover_hacia_x(dt, jugador, 1.0)

        self.temporizador -= dt
        if self.temporizador <= 0:
            if self.fase >= 2 and random.random() < 0.40:
                self.estado = "telegrafia_carga"
                self.temporizador = 0.45
            else:
                self.estado = "telegrafia"
                self.temporizador = max(0.38, 0.78 - self.fase * 0.12)
            self.aviso_recien = True

    def _actualizar_carga(self, dt):
        # Embestida horizontal rapida hasta chocar muro o agotar tiempo
        self.x += self.direccion * JEFE_CARGA_VELOCIDAD * dt
        choco_muro = False
        if self.x <= self.minimo_x:
            self.x = float(self.minimo_x)
            choco_muro = True
        elif self.x >= self.maximo_x:
            self.x = float(self.maximo_x)
            choco_muro = True
        self.rect.x = round(self.x)
        self.temporizador -= dt

        if self.temporizador <= 0 or choco_muro:
            self.carga_activa = False
            self.estado = "recuperacion"
            self.temporizador = JEFE_VULN_FASE2
            self.vulnerable = True
            if choco_muro:
                self.ondas_recien = True

    def _actualizar_transiciones_fases_12(self, dt, jugador):
        # Estados de ataque y recuperacion de las dos primeras fases
        if self.estado == "telegrafia":
            self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "golpe"
                self.temporizador = 0.14
                self.ondas_recien = True
        elif self.estado == "golpe":
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "recuperacion"
                vuln_f1 = max(0.75, 1.7 - self.fase * 0.25)
                self.temporizador = JEFE_VULN_FASE2 if self.fase >= 2 else vuln_f1
                self.vulnerable = True
        elif self.estado == "recuperacion":
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "espera"
                self.temporizador = max(0.65, 1.45 - self.fase * 0.22)
                self.vulnerable = False
        elif self.estado == "cambio":
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "espera"
                self.temporizador = max(0.55, 1.2 - self.fase * 0.18)

    def _actualizar_embates_fases_12(self, dt, jugador):
        # Carga horizontal y embate vertical ascendente de fases 1 y 2
        if self.estado == "telegrafia_carga":
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "carga"
                self.carga_activa = True
                self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
                self.temporizador = 0.75
        elif self.estado == "carga":
            self._actualizar_carga(dt)
        elif self.estado == "telegrafia_embate":
            if abs(jugador.rect.centerx - self.rect.centerx) > 6:
                self._mover_hacia_x(dt, jugador, 1.5)
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "embate"
                self.temporizador = 0.22
                self.embate_recien = True
        elif self.estado == "embate":
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "recuperacion"
                self.temporizador = JEFE_VULN_FASE2 if self.fase >= 2 else 0.70
                self.vulnerable = True

    def actualizar(self, dt, jugador, solidos_cripta=None):
        """Actualiza la maquina de estados del Custodio en sus 3 fases."""
        self._limpiar_senales_frame()
        if self.tiempo_flash > 0:
            self.tiempo_flash = max(0.0, self.tiempo_flash - dt)
        if not self.vivo:
            self.tiempo_muerte += dt
            return

        if self.estado == "espera":
            self._actualizar_espera(dt, jugador)
        elif self.estado in ("telegrafia", "golpe", "recuperacion", "cambio"):
            self._actualizar_transiciones_fases_12(dt, jugador)
        elif self.estado in ("telegrafia_carga", "carga", "telegrafia_embate", "embate"):
            self._actualizar_embates_fases_12(dt, jugador)
        elif self.estado in ESTADOS_FASE3:
            self._actualizar_fase3_smb3(dt, jugador, solidos_cripta)

    def _f3_iniciar_salto(self, jugador):
        # Despega apuntando al jugador antes de la caida vertical aplastante
        self.estado = "salto_smb3"
        self.quiebre_usado_en_salto = False
        profundidad_actual = max(0.0, self.y - self.y_suelo)
        self.vy = -660.0 - min(80.0, profundidad_actual * 0.65)
        dx = float(jugador.rect.centerx - self.rect.centerx)
        self.vx_smb3 = limitar(dx / 0.72, -280.0, 280.0)

    def _f3_registrar_aterrizaje(self, y_destino):
        # Posiciona sobre el soporte alcanzado y dispara el impacto sismico
        self.y = y_destino
        self.vy = 0.0
        self.vx_smb3 = 0.0
        self.rect.y = round(self.y)
        self.aplasto_suelo_recien = True
        self.ondas_recien = True
        self.saltos_smb3 += 1
        self.estado = "aterrizaje_smb3"
        self.temporizador = 0.50

    def _f3_actualizar_salto(self, dt, jugador, solidos_cripta):
        # Sigue brevemente en el aire, cae en columna y comprueba criptas bajo los pies
        if self.vy < 40.0:
            objetivo_vx = limitar((jugador.rect.centerx - self.rect.centerx) * 2.5, -280.0, 280.0)
            self.vx_smb3 += (objetivo_vx - self.vx_smb3) * min(1.0, 5.0 * dt)
        else:
            self.vx_smb3 *= max(0.0, 1.0 - 9.0 * dt)

        self.x = limitar(self.x + self.vx_smb3 * dt, self.minimo_x, self.maximo_x)
        self.vy += 1520.0 * dt
        self.y += self.vy * dt
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)

        if not (self.vy > 0 and self.y >= self.y_suelo):
            return
        if solidos_cripta is None:
            self._f3_registrar_aterrizaje(self.y_suelo)
            return
        franja_suelo = self.rect_soporte_central_f3()
        soportes = [s for s in solidos_cripta if franja_suelo.colliderect(s)]
        if not soportes:
            self.estado = "cayendo_abismo"
            self.en_abismo_recien = True
            self.vy = max(self.vy, 280.0)
            return
        y_aterrizaje = float(min(s.top for s in soportes) - self.rect.height)
        if self.y >= y_aterrizaje:
            self._f3_registrar_aterrizaje(y_aterrizaje)

    def _actualizar_fase3_smb3(self, dt, jugador, solidos_cripta):
        # Maquina de estados de fase 3 excavando las 4 capas de criptas
        self.vulnerable = False
        if self.estado == "cambio_f3":
            self.y = self.y_suelo
            self.vy = 0.0
            self.rect.y = round(self.y)
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "espera_smb3"
                self.temporizador = 0.28
        elif self.estado == "espera_smb3":
            self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "telegrafia_smb3"
                self.temporizador = 0.28
                self.aviso_recien = True
        elif self.estado == "telegrafia_smb3":
            self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
            self.temporizador -= dt
            if self.temporizador <= 0:
                self._f3_iniciar_salto(jugador)
        elif self.estado == "salto_smb3":
            self._f3_actualizar_salto(dt, jugador, solidos_cripta)
        elif self.estado == "aterrizaje_smb3":
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "espera_smb3"
                self.temporizador = 0.24
        elif self.estado == "cayendo_abismo":
            self.vy += 1200.0 * dt
            self.y += self.vy * dt
            self.rect.y = round(self.y)
            if self.y >= self.y_suelo + 4 * TILE + 80:
                self.matar_por_abismo()

    def _dibujar_aura_fase(self, surface, rect, tiempo, pulso):
        # Dibuja auras segun la fase y ventana de vulnerabilidad
        if self.fase >= 3:
            col_f3 = (165, 70, 235)
            aura_f3 = obtener_aura_custodio(
                rect.width + 28, rect.height + 26, col_f3, int(30 + pulso * 30)
            )
            surface.blit(aura_f3, (rect.x - 14, rect.y - 13))
            pygame.draw.ellipse(surface, (205, 130, 255), rect.inflate(14, 10), 2)
            if self.estado == "aterrizaje_smb3":
                anillo = pygame.Rect(rect.x - 14, rect.bottom - 10, rect.width + 28, 16)
                pygame.draw.ellipse(surface, ORO_LITÚRGICO, anillo, 2)
                pygame.draw.ellipse(surface, (235, 180, 255), anillo.inflate(8, 4), 1)
            return

        if self.fase == 2:
            if self.vulnerable:
                aura = obtener_aura_custodio(
                    rect.width + 26, rect.height + 24, ORO_LITÚRGICO, int(34 + pulso * 26)
                )
                surface.blit(aura, (rect.x - 13, rect.y - 12))
                ring_box = rect.inflate(20, 18)
                for ang_ini in (0.2, 1.8, 3.4, 5.0):
                    pygame.draw.arc(surface, ORO_LITÚRGICO, ring_box, ang_ini, ang_ini + 0.7, 2)
            else:
                aura = obtener_aura_custodio(
                    rect.width + 24, rect.height + 22, CARMESÍ_SANGRE, int(22 + pulso * 24)
                )
                surface.blit(aura, (rect.x - 12, rect.y - 11))
                for r_offset in (16, 26):
                    ond = int(2.5 * math.sin(tiempo * 7.5 + r_offset * 0.3))
                    ring_box = pygame.Rect(
                        rect.x - r_offset // 2,
                        rect.y - r_offset // 2 + ond,
                        rect.width + r_offset,
                        rect.height + r_offset,
                    )
                    pygame.draw.ellipse(surface, CARMESÍ_SANGRE, ring_box, 1)
            return

        if self.vulnerable:
            aura = obtener_aura_custodio(rect.width + 18, rect.height + 16, ORO_LITÚRGICO, 32)
            surface.blit(aura, (rect.x - 9, rect.y - 8))

    def _dibujar_auras_estado(self, surface, rect, tiempo, pulso):
        # Dibuja sombra, auras de fase y haces de telegrafia o embate
        pygame.draw.ellipse(surface, NEGRO_NOCHE, (rect.x, rect.bottom - 6, rect.width, 10))
        self._dibujar_aura_fase(surface, rect, tiempo, pulso)

        telegrafias = ("telegrafia", "telegrafia_carga", "telegrafia_smb3", "telegrafia_embate")
        if self.estado in telegrafias:
            color_brillo = COLORES_TELEGRAFIA.get(self.estado, (180, 32, 42))
            brillo = obtener_aura_custodio(
                rect.width + 48, rect.height + 40, color_brillo, int(45 + pulso * 35)
            )
            surface.blit(brillo, (rect.x - 24, rect.y - 20))
            if self.estado == "telegrafia_embate":
                col_aviso = pygame.Surface((80, int(3.5 * TILE)), pygame.SRCALPHA)
                col_aviso.fill((245, 200, 80, int(28 + pulso * 36)))
                surface.blit(col_aviso, (rect.centerx - 40, rect.top - int(3.5 * TILE)))
        elif self.estado == "embate":
            haz = pygame.Surface((80, int(3.5 * TILE) + 12), pygame.SRCALPHA)
            haz.fill((255, 225, 130, 115))
            pygame.draw.rect(haz, (255, 248, 210, 210), (14, 0, 52, haz.get_height()), 2)
            surface.blit(haz, (rect.centerx - 40, rect.top - int(3.5 * TILE)))

    def _dibujar_vestimenta_y_mitra(self, surface, rect):
        # Dibuja capa episcopal, pectoral y mitra litúrgica
        centro_x = rect.centerx
        base_y = rect.bottom
        capa_color = (68, 16, 22) if self.fase >= 2 else (38, 28, 44)
        pts_capa = [
            (centro_x - 24, base_y - 2),
            (centro_x - 18, rect.y + 18),
            (centro_x - 8, rect.y + 4),
            (centro_x + 8, rect.y + 2),
            (centro_x + 20, rect.y + 20),
            (centro_x + 27, base_y - 2),
        ]
        pygame.draw.polygon(surface, capa_color, pts_capa)
        cuerpo_color = (44, 14, 18) if self.fase >= 2 else (23, 19, 28)
        cuerpo_box = (centro_x - 21, rect.y + 12, 42, 44)
        pygame.draw.rect(surface, cuerpo_color, cuerpo_box, border_radius=10)
        col_pect = ORO_LITÚRGICO if self.fase < 2 else (180, 50, 45)
        pygame.draw.line(surface, col_pect, (centro_x - 15, rect.y + 26), (centro_x + 15, rect.y + 26), 2)
        col_cost = HUESO_MARFIL if self.fase < 2 else (160, 40, 50)
        for i in range(4):
            y_c = rect.y + 31 + i * 4
            pygame.draw.line(surface, col_cost, (centro_x - 14 + i * 2, y_c), (centro_x + 14 - i * 2, y_c), 1)

        mitra_y = rect.y + 4
        puntos_mitra = [
            (centro_x - 9, mitra_y + 4),
            (centro_x - 11, mitra_y - 12),
            (centro_x, mitra_y - 20),
            (centro_x + 11, mitra_y - 12),
            (centro_x + 9, mitra_y + 4),
        ]
        color_mitra = (85, 20, 28) if self.fase >= 2 else (52, 38, 62)
        pygame.draw.polygon(surface, color_mitra, puntos_mitra)
        pygame.draw.polygon(surface, ORO_LITÚRGICO, puntos_mitra, 1)
        pygame.draw.line(surface, ORO_LITÚRGICO, (centro_x, mitra_y - 14), (centro_x, mitra_y - 2), 1)
        p_cruz = ((centro_x - 3, mitra_y - 9), (centro_x + 3, mitra_y - 9))
        pygame.draw.line(surface, ORO_LITÚRGICO, p_cruz[0], p_cruz[1], 1)

    def _dibujar_craneo_y_farol(self, surface, rect):
        # Dibuja el craneo colosal, ojos y farol pectoral
        centro_x = rect.centerx
        pygame.draw.circle(surface, HUESO_MARFIL, (centro_x, rect.y + 16), 12)
        pygame.draw.circle(surface, NEGRO_NOCHE, (centro_x, rect.y + 16), 12, 1)

        if self.vulnerable or self.puede_quiebre_sismico_f3():
            color_ojo = (245, 205, 95)
        elif self.fase >= 2:
            color_ojo = (255, 45, 55)
        else:
            color_ojo = CARMESÍ_SANGRE
        for dx_ojo in (-4, 4):
            pygame.draw.circle(surface, color_ojo, (centro_x + dx_ojo, rect.y + 15), 2.5)
            pygame.draw.circle(surface, BLANCO, (centro_x + dx_ojo, rect.y + 15), 1)
        pygame.draw.rect(surface, NEGRO_NOCHE, (centro_x - 5, rect.y + 21, 10, 2))

        pygame.draw.circle(surface, (115, 78, 28), (centro_x, rect.y + 34), 7)
        pygame.draw.circle(surface, FAROL_CÁLIDO, (centro_x, rect.y + 34), 3)

    def _dibujar_maza_osario(self, surface, rect):
        # Dibuja la maza orientada al frente o alzada durante embate
        centro_x = rect.centerx
        base_y = rect.bottom
        signo = 1 if self.direccion >= 0 else -1
        if self.estado in ("telegrafia_embate", "embate"):
            elev = 48 if self.estado == "embate" else 22
            maza_mango_ini = (centro_x + signo * 12, rect.y + 18)
            maza_cx = centro_x + signo * 14
            maza_cy = rect.y - elev
            maza_mango_fin = (maza_cx, maza_cy)
        else:
            maza_mango_ini = (centro_x + signo * 20, rect.y + 22)
            maza_mango_fin = (centro_x + signo * 30, base_y - 4)
            maza_cx = centro_x + signo * 30
            maza_cy = base_y - 8
        pygame.draw.line(surface, MARRON_OSCURO, maza_mango_ini, maza_mango_fin, 5)
        pygame.draw.line(surface, HUESO_MARFIL, maza_mango_ini, maza_mango_fin, 2)
        pygame.draw.circle(surface, (85, 78, 88), (maza_cx, maza_cy), 8)
        pygame.draw.circle(surface, HUESO_MARFIL, (maza_cx, maza_cy), 6)
        pygame.draw.rect(surface, (55, 48, 58), (maza_cx - 9, maza_cy - 2, 18, 4))
        for espina_ang in (0.0, 1.2, 2.4, 3.6, 4.8):
            ex = maza_cx + math.cos(espina_ang) * 10
            ey = maza_cy + math.sin(espina_ang) * 10
            pygame.draw.line(surface, (160, 155, 170), (maza_cx, maza_cy), (int(ex), int(ey)), 2)

    def dibujar(self, surface, camara, tiempo):
        """Renderiza al Custodio con sus auras, maza e indicador de guardia abierta."""
        if not self.vivo:
            return
        rect = camara.aplicar_rect(self.rect)
        pulso = 0.5 + 0.5 * math.sin(tiempo * 5)

        self._dibujar_auras_estado(surface, rect, tiempo, pulso)
        self._dibujar_vestimenta_y_mitra(surface, rect)
        self._dibujar_craneo_y_farol(surface, rect)
        self._dibujar_maza_osario(surface, rect)

        if self.vulnerable or self.puede_quiebre_sismico_f3():
            bob = int(2.5 * math.sin(tiempo * 9.0))
            cx, cy = rect.centerx, rect.y - 24 + bob
            es_quiebre = self.puede_quiebre_sismico_f3()
            color_emblema = (225, 165, 255) if es_quiebre else ORO_LITÚRGICO
            rombo = [(cx, cy - 6), (cx + 6, cy), (cx, cy + 6), (cx - 6, cy)]
            pygame.draw.polygon(surface, color_emblema, rombo)
            pygame.draw.polygon(surface, BLANCO, rombo, 1)

        if self.tiempo_flash > 0:
            flash_overlay = obtener_aura_custodio(rect.width, rect.height, (140, 140, 140), 140)
            surface.blit(flash_overlay, rect.topleft, special_flags=pygame.BLEND_RGB_ADD)
