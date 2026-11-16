#---- Importamos librerias y configuracion ----#
import math

import pygame

from actores.estampas import (
    obtener_arco_guadaña,
    obtener_estampa_fantasma,
    obtener_estampa_luz,
)
from actores.utilidades import _tecla_activa
from config import (
    APEX_GRAVEDAD_FACTOR,
    APEX_VY_UMBRAL,
    ATAQUE_ALCANCE,
    ATAQUE_ALCANCE_MEJORADO,
    ATAQUE_ALTO,
    ATAQUE_COOLDOWN,
    ATAQUE_DURACION,
    AZUL_OSCURO,
    BLANCO,
    CARMESÍ_SANGRE,
    CORNER_NUDGE_TECHO,
    CORTE_SALTO,
    COYOTE_TIME,
    DASH_COOLDOWN,
    DASH_DURACION,
    DASH_JUMP_IMPULSO_X,
    DASH_USOS_AIRE,
    DASH_VELOCIDAD,
    FAROL_CÁLIDO,
    FILO_ANIMA_ALCANCE,
    FILO_ANIMA_DASH_FACTOR,
    GRAVEDAD,
    GRIS,
    INVULNERABILIDAD,
    JUGADOR_ALTO,
    JUGADOR_ANCHO,
    JUMP_BUFFER,
    MARRON,
    MARRON_OSCURO,
    MAX_CAIDA,
    NEGRO_NOCHE,
    ORO_LITÚRGICO,
    POST_DASH_DURACION,
    POST_DASH_GRAVEDAD_FACTOR,
    SALTO,
    TURQUESA_ÁNIMA,
    VELOCIDAD,
    VIDAS_INICIALES,
)


#---- Clase Jugador ----#
class Jugador:
    """El sepulturero: salta, hace dash y clava la pala desde el aire."""

    def __init__(self, x, y, vidas=VIDAS_INICIALES, tiene_dash=False):
        self.rect = pygame.Rect(
            int(x),
            int(y),
            JUGADOR_ANCHO,
            JUGADOR_ALTO,
        )
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.vx = 0.0
        self.vy = 0.0
        self.en_suelo = False
        self.coyote = 0.0
        self.buffer_salto = 0.0
        self.invulnerable = 0.0
        self.direccion = 1
        self.tiempo_animacion = 0.0

        self.dash_tiempo = 0.0
        self.dash_cooldown = 0.0
        self.dash_usos_aire = DASH_USOS_AIRE
        self.dash_direccion = 1
        self.post_dash_tiempo = 0.0
        self.manteniendo_salto = False
        self.teclas_izq = (pygame.K_a, pygame.K_LEFT)
        self.teclas_der = (pygame.K_d, pygame.K_RIGHT)

        self.salto_recien = False
        self.dash_recien = False
        self.squash_timer = 0.0
        self.squash_tipo = None
        self.aterrizaje_recien = False
        self.retroceso_tiempo = 0.0

        self.ataque_tiempo = 0.0
        self.ataque_cooldown = 0.0
        self.ataque_golpeado = False

        self.vidas = vidas
        self.almas = 0
        self.almas_para_vida = 0
        self.tiene_pala = False
        self.tiene_dash = tiene_dash
        self.rango_ataque_mejorado = False
        self.escudo_farol = False
        self.filo_anima = False

    def pedir_salto(self):
        """Se llama en KEYDOWN: deja preparado el salto."""
        self.buffer_salto = JUMP_BUFFER
        self.manteniendo_salto = True

    def soltar_salto(self):
        """Se llama en KEYUP: corta el salto si todavía sube."""
        self.manteniendo_salto = False
        if self.vy < 0:
            self.vy *= CORTE_SALTO

    def pedir_dash(self):
        """Inicia un dash si hay carga, la habilidad está desbloqueada y, en el aire, queda un uso."""
        if not self.tiene_dash:
            return False
        if self.dash_tiempo > 0 or self.dash_cooldown > 0:
            return False
        if not self.en_suelo and self.dash_usos_aire <= 0:
            return False

        self.dash_tiempo = DASH_DURACION
        cd = DASH_COOLDOWN * (FILO_ANIMA_DASH_FACTOR if getattr(self, "filo_anima", False) else 1.0)
        self.dash_cooldown = cd
        self.dash_direccion = self.direccion

        if not self.en_suelo:
            self.dash_usos_aire -= 1

        self.vx = self.direccion * DASH_VELOCIDAD
        self.vy = 0.0
        self.dash_recien = True
        self._dash_pendiente_feedback = True
        return True

    def dash_listo(self):
        return (
            self.tiene_dash
            and self.dash_tiempo <= 0
            and self.dash_cooldown <= 0
            and (self.en_suelo or self.dash_usos_aire > 0)
        )

    def pedir_ataque(self):
        """Inicia un golpe de pala si el arma está desbloqueada."""
        if (
            not self.tiene_pala
            or self.ataque_cooldown > 0
            or self.ataque_tiempo > 0
        ):
            return False

        self.ataque_tiempo = ATAQUE_DURACION
        self.ataque_cooldown = ATAQUE_COOLDOWN
        self.ataque_golpeado = False
        return True

    def rect_ataque(self):
        es_guadaña = self.rango_ataque_mejorado
        alcance = ATAQUE_ALCANCE_MEJORADO if es_guadaña else ATAQUE_ALCANCE
        if getattr(self, "filo_anima", False):
            alcance += FILO_ANIMA_ALCANCE
        alto = (ATAQUE_ALTO + 16) if es_guadaña else ATAQUE_ALTO
        if self.direccion > 0:
            x = self.rect.right - 4
        else:
            x = self.rect.left - alcance + 4
        return pygame.Rect(
            x,
            self.rect.centery - alto // 2,
            alcance,
            alto,
        )

    def pose_actual(self):
        if self.ataque_tiempo > 0:
            if self.ataque_tiempo > ATAQUE_DURACION * 0.62:
                return "ataque1"
            if self.ataque_tiempo > ATAQUE_DURACION * 0.30:
                return "ataque2"
            return "ataque3"
        if not self.en_suelo:
            return "caida"
        return None

    def actualizar(self, dt, teclas, solidos):
        self.salto_recien = False
        if getattr(self, "_dash_pendiente_feedback", False):
            self._dash_pendiente_feedback = False
            self.dash_recien = True
        else:
            self.dash_recien = False
        self.aterrizaje_recien = False

        if self.squash_timer > 0:
            self.squash_timer = max(0.0, self.squash_timer - dt)
            if self.squash_timer <= 0:
                self.squash_tipo = None

        if self.invulnerable > 0:
            self.invulnerable = max(0.0, self.invulnerable - dt)
        if self.dash_cooldown > 0:
            self.dash_cooldown = max(0.0, self.dash_cooldown - dt)
        if self.ataque_cooldown > 0:
            self.ataque_cooldown = max(0.0, self.ataque_cooldown - dt)
        if self.ataque_tiempo > 0:
            self.ataque_tiempo = max(0.0, self.ataque_tiempo - dt)
        if self.post_dash_tiempo > 0:
            self.post_dash_tiempo = max(0.0, self.post_dash_tiempo - dt)
        if self.retroceso_tiempo > 0:
            self.retroceso_tiempo = max(0.0, self.retroceso_tiempo - dt)

        # Actualizar siempre temporizadores (buffer_salto, coyote) antes del chequeo de dash
        self.actualizar_temporizadores(dt)

        if self.dash_tiempo > 0:
            # Dash-Jump: Salto impulsado si se presiona salto durante un dash en suelo
            if self.buffer_salto > 0 and (self.en_suelo or self.coyote > 0):
                self.dash_tiempo = 0.0
                self.post_dash_tiempo = POST_DASH_DURACION
                self.vy = SALTO
                self.vx = self.dash_direccion * VELOCIDAD * DASH_JUMP_IMPULSO_X
                self.en_suelo = False
                self.coyote = 0.0
                self.buffer_salto = 0.0
                self.salto_recien = True
                self.squash_timer = 0.10
                self.squash_tipo = "salto"
            else:
                era_en_suelo = self.en_suelo
                self.actualizar_dash(dt, solidos)
                if not era_en_suelo and self.en_suelo:
                    self.aterrizaje_recien = True
                    self.squash_timer = 0.09
                    self.squash_tipo = "aterrizaje"
                return

        self.actualizar_horizontal(teclas)

        if self.buffer_salto > 0 and (self.en_suelo or self.coyote > 0):
            self.vy = SALTO
            self.en_suelo = False
            self.coyote = 0.0
            self.buffer_salto = 0.0
            self.salto_recien = True
            self.squash_timer = 0.10
            self.squash_tipo = "salto"

        # Gravedad con Apex Hang-Time (flotación en cima de salto) y Post-Dash Float
        factor_gravedad = 1.0
        if self.post_dash_tiempo > 0:
            factor_gravedad = min(factor_gravedad, POST_DASH_GRAVEDAD_FACTOR)

        salto_mantenido = (
            self.manteniendo_salto
            or _tecla_activa(teclas, pygame.K_SPACE)
            or _tecla_activa(teclas, pygame.K_UP)
            or _tecla_activa(teclas, pygame.K_w)
        )
        if not self.en_suelo and abs(self.vy) < APEX_VY_UMBRAL and salto_mantenido:
            factor_gravedad = min(factor_gravedad, APEX_GRAVEDAD_FACTOR)

        self.vy = min(MAX_CAIDA, self.vy + GRAVEDAD * factor_gravedad * dt)

        self.mover_x(self.vx * dt, solidos)
        era_en_suelo = self.en_suelo
        self.en_suelo = False
        self.mover_y(self.vy * dt, solidos)

        if not era_en_suelo and self.en_suelo:
            self.aterrizaje_recien = True
            self.squash_timer = 0.09
            self.squash_tipo = "aterrizaje"

        if self.en_suelo:
            self.coyote = COYOTE_TIME
            self.dash_usos_aire = DASH_USOS_AIRE
            if abs(self.vx) > 1:
                self.tiempo_animacion += dt
        else:
            self.tiempo_animacion = 0.0

    def actualizar_dash(self, dt, solidos):
        self.dash_tiempo = max(0.0, self.dash_tiempo - dt)
        self.vx = self.dash_direccion * DASH_VELOCIDAD
        self.vy = 0.0

        self.mover_x(self.vx * dt, solidos)
        if self.vx == 0:
            self.dash_tiempo = 0.0

        if self.en_suelo:
            self.dash_usos_aire = DASH_USOS_AIRE
        if self.dash_tiempo == 0:
            # Conservación de momentum y float post-dash para mejor control
            self.vx = self.dash_direccion * VELOCIDAD
            self.post_dash_tiempo = POST_DASH_DURACION

    def actualizar_temporizadores(self, dt):
        if self.buffer_salto > 0:
            self.buffer_salto = max(0.0, self.buffer_salto - dt)
        if self.en_suelo:
            self.coyote = COYOTE_TIME
        else:
            self.coyote = max(0.0, self.coyote - dt)

    def actualizar_horizontal(self, teclas):
        teclas_i = getattr(self, "teclas_izq", (pygame.K_a, pygame.K_LEFT))
        teclas_d = getattr(self, "teclas_der", (pygame.K_d, pygame.K_RIGHT))
        izquierda = any(_tecla_activa(teclas, k) for k in teclas_i)
        derecha = any(_tecla_activa(teclas, k) for k in teclas_d)

        if izquierda and not derecha:
            if getattr(self, "retroceso_tiempo", 0.0) <= 0:
                self.vx = -VELOCIDAD
                self.direccion = -1
        elif derecha and not izquierda:
            if getattr(self, "retroceso_tiempo", 0.0) <= 0:
                self.vx = VELOCIDAD
                self.direccion = 1
        else:
            if self.post_dash_tiempo > 0 or getattr(self, "retroceso_tiempo", 0.0) > 0:
                # Conserva impulso horizontal durante la ventana post-dash float o retroceso cinético
                pass
            else:
                self.vx = 0.0

    def mover_x(self, dx, solidos):
        self.x += dx
        self.rect.x = round(self.x)

        colision = False
        for solido in solidos:
            if self.rect.colliderect(solido):
                colision = True
                break

        # Tolerancia de esquinas en dash (corner nudge para mejor control):
        # Si durante un dash rozamos una esquina por hasta 6 px, deslizar suavemente hacia el hueco
        if colision and self.dash_tiempo > 0:
            tolerancia = 6
            for dy in range(1, tolerancia + 1):
                test_rect = self.rect.move(0, dy)
                if not any(test_rect.colliderect(s) for s in solidos):
                    self.y += dy
                    self.rect.y = round(self.y)
                    colision = False
                    break
            if colision:
                for dy in range(1, tolerancia + 1):
                    test_rect = self.rect.move(0, -dy)
                    if not any(test_rect.colliderect(s) for s in solidos):
                        self.y -= dy
                        self.rect.y = round(self.y)
                        colision = False
                        break

        if colision:
            for solido in solidos:
                if not self.rect.colliderect(solido):
                    continue
                if dx > 0:
                    self.rect.right = solido.left
                elif dx < 0:
                    self.rect.left = solido.right
                self.x = float(self.rect.x)
                self.vx = 0.0
                break

    def mover_y(self, dy, solidos):
        self.y += dy
        self.rect.y = round(self.y)

        colision = any(self.rect.colliderect(s) for s in solidos)
        # Jump Corner Correction (Tolerancia de esquinas en techo para mejor control):
        # Si sube y roza la esquina de un bloque superior por <= 5 px, deslizarlo suavemente hacia el hueco
        if colision and dy < 0:
            tolerancia = CORNER_NUDGE_TECHO
            direcciones_dx = [1, -1] if self.direccion >= 0 else [-1, 1]
            corregido = False
            for sign in direcciones_dx:
                for d in range(1, tolerancia + 1):
                    shift = sign * d
                    test_rect = self.rect.move(shift, 0)
                    if not any(test_rect.colliderect(s) for s in solidos):
                        self.x += shift
                        self.rect.x = round(self.x)
                        colision = False
                        corregido = True
                        break
                if corregido:
                    break

        if colision:
            for solido in solidos:
                if not self.rect.colliderect(solido):
                    continue
                if dy > 0:
                    self.rect.bottom = solido.top
                    self.en_suelo = True
                elif dy < 0:
                    self.rect.top = solido.bottom
                self.y = float(self.rect.y)
                self.vy = 0.0
                break

        if dy >= 0 and not self.en_suelo:
            sonda = self.rect.move(0, 1)
            for solido in solidos:
                if sonda.colliderect(solido):
                    self.rect.bottom = solido.top
                    self.y = float(self.rect.y)
                    self.en_suelo = True
                    self.vy = 0.0
                    break

    def respawn(self, x, y):
        self.rect.topleft = (int(x), int(y))
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0
        self.en_suelo = False
        self.coyote = 0.0
        self.buffer_salto = 0.0
        self.invulnerable = INVULNERABILIDAD
        self.dash_tiempo = 0.0
        self.dash_cooldown = 0.0
        self.dash_usos_aire = DASH_USOS_AIRE
        self.post_dash_tiempo = 0.0
        self.manteniendo_salto = False
        self.salto_recien = False
        self.dash_recien = False
        self.squash_timer = 0.0
        self.squash_tipo = None
        self.aterrizaje_recien = False
        self.retroceso_tiempo = 0.0
        self.ataque_tiempo = 0.0
        self.ataque_cooldown = 0.0
        self.ataque_golpeado = False
        self.almas_para_vida = 0
        self.rango_ataque_mejorado = False
        self.escudo_farol = False
        self.filo_anima = False

    def _dibujar_estela_y_luz(self, surface, rect, tiempo):
        """Dibuja las estelas del dash, la sombra de contacto y el halo del farol."""
        if self.dash_tiempo > 0:
            es_guadana = getattr(self, "rango_ataque_mejorado", False)
            col_ghost = (195, 85, 250) if es_guadana else (92, 220, 200)
            for i, alfa in enumerate((180, 120, 70, 30)):
                fx = rect.x - self.dash_direccion * (9 + i * 8)
                ghost_surf = obtener_estampa_fantasma(rect.width, rect.height, alfa, col_ghost)
                surface.blit(ghost_surf, (fx, rect.y))

        pygame.draw.ellipse(surface, NEGRO_NOCHE, (rect.x + 1, rect.bottom - 5, rect.width - 2, 8))

        farol_x = rect.centerx + self.direccion * 11
        farol_y = rect.y + 19
        tiene_consagrado = getattr(self, "rango_ataque_mejorado", False)
        color_halo = (195, 80, 255) if tiene_consagrado else FAROL_CÁLIDO
        halo_farol = obtener_estampa_luz(85, color_halo, 28 if tiene_consagrado else 22)
        surface.blit(halo_farol, (farol_x - 85, farol_y - 85), special_flags=pygame.BLEND_RGB_ADD)

    def _calcular_pose_y_escala(self, atacando):
        """Calcula squash & stretch y el desplazamiento de paso al caminar."""
        moviendo = self.en_suelo and abs(self.vx) > 1 and not atacando
        despliegue_pierna = 0
        escala_x = 1.0
        escala_y = 1.0
        if getattr(self, "squash_timer", 0.0) > 0 and getattr(self, "squash_tipo", None):
            if self.squash_tipo == "salto":
                frac = min(1.0, self.squash_timer / 0.10)
                escala_y = 1.0 + 0.15 * frac
                escala_x = 1.0 - 0.13 * frac
            elif self.squash_tipo == "aterrizaje":
                frac = min(1.0, self.squash_timer / 0.09)
                escala_y = 1.0 - 0.15 * frac
                escala_x = 1.0 + 0.18 * frac
        elif moviendo:
            pasos = ((0.95, 6), (0.98, 2), (1.05, -5), (1.02, -1))
            escala_y, despliegue_pierna = pasos[int((self.tiempo_animacion * 9.5) % 4)]
        return despliegue_pierna, escala_x, escala_y

    def _dibujar_arma_sepulturero(self, surface, camara, rect, pose, con_pala, atacando, postura_pisoton):
        """Dibuja la pala o guadaña en ataque, en pisotón aéreo o reposando en la espalda."""
        centro_x = rect.centerx
        base_y = rect.bottom
        hombro_x = centro_x - self.direccion * 7
        es_guadana = getattr(self, "rango_ataque_mejorado", False)
        color_mango = (45, 30, 48) if es_guadana else MARRON

        if atacando:
            alcance = (36 if es_guadana else 16) if pose == "ataque2" else (28 if es_guadana else 13)
            alto_pala = {
                "ataque1": rect.y - (6 if es_guadana else -2),
                "ataque2": rect.y + 12,
                "ataque3": base_y + (4 if es_guadana else -1),
            }[pose]
            punta_x = centro_x + self.direccion * alcance
            origen_mango = (hombro_x, rect.y + 8)
            pygame.draw.line(surface, color_mango, origen_mango, (punta_x, alto_pala), 4 if es_guadana else 3)
            if es_guadana:
                # Virola de bronce y remache amatista en la empuñadura
                pygame.draw.line(surface, ORO_LITÚRGICO, (punta_x - self.direccion * 5, alto_pala - 2), (punta_x + self.direccion * 2, alto_pala + 2), 2)
                pygame.draw.circle(surface, (215, 110, 255), origen_mango, 2)
            if not con_pala:
                return
            signo = self.direccion
            arco_caja = camara.aplicar_rect(self.rect_ataque())
            if es_guadana:
                puntos_hoja = [
                    (punta_x - signo * 4, alto_pala - 8),
                    (punta_x + signo * 12, alto_pala - 11),
                    (punta_x + signo * 25, alto_pala - 5),
                    (punta_x + signo * 33, alto_pala + 9),
                    (punta_x + signo * 31, alto_pala + 20),
                    (punta_x + signo * 23, alto_pala + 13),
                    (punta_x + signo * 15, alto_pala + 6),
                    (punta_x + signo * 4, alto_pala + 3),
                    (punta_x - signo * 2, alto_pala),
                ]
                lomo_hoja = puntos_hoja[:5]
                pygame.draw.polygon(surface, (150, 48, 200), puntos_hoja)
                pygame.draw.polygon(surface, (215, 105, 255), [puntos_hoja[1], puntos_hoja[2], puntos_hoja[3], puntos_hoja[6], puntos_hoja[7]])
                pygame.draw.lines(surface, (255, 240, 255), False, lomo_hoja, 2)
                pygame.draw.circle(surface, ORO_LITÚRGICO, (punta_x, alto_pala), 3)
                onda_x, onda_y = arco_caja.x - 2, arco_caja.y - 4
                surface.blit(obtener_arco_guadaña(signo), (onda_x, onda_y))
                if getattr(self, "filo_anima", False):
                    start_ang = 0.0 if signo > 0 else 1.57
                    end_ang = 3.14 if signo > 0 else 4.71
                    pygame.draw.arc(surface, TURQUESA_ÁNIMA, (onda_x - 3, onda_y - 3, arco_caja.width + 6, arco_caja.height + 12), start_ang, end_ang, 2)
                    pygame.draw.arc(surface, ORO_LITÚRGICO, (onda_x - 1, onda_y - 1, arco_caja.width + 2, arco_caja.height + 8), start_ang, end_ang, 1)
            else:
                pygame.draw.polygon(
                    surface,
                    (195, 198, 208),
                    [(punta_x, alto_pala - 5), (punta_x + signo * 8, alto_pala), (punta_x, alto_pala + 6), (punta_x - signo * 2, alto_pala)],
                )
                pygame.draw.polygon(
                    surface,
                    ORO_LITÚRGICO,
                    [(punta_x + signo * 4, alto_pala - 3), (punta_x + signo * 8, alto_pala), (punta_x + signo * 4, alto_pala + 3)],
                )
                ang_ini = -0.4 if signo > 0 else 2.6
                ang_fin = 2.4 if signo > 0 else 5.4
                pygame.draw.arc(surface, (230, 235, 245), arco_caja, ang_ini, ang_fin, 2)
                pygame.draw.arc(surface, ORO_LITÚRGICO, arco_caja.inflate(2, 2), ang_ini, ang_fin, 1)
                if getattr(self, "filo_anima", False):
                    pygame.draw.arc(surface, TURQUESA_ÁNIMA, arco_caja.inflate(6, 6), ang_ini, ang_fin, 2)
                    pygame.draw.arc(surface, (255, 235, 140), arco_caja.inflate(4, 4), ang_ini, ang_fin, 1)
                    for off_i in range(3):
                        sp_x = punta_x - signo * (off_i * 6 + 4)
                        sp_y = alto_pala + (off_i * 3 - 3)
                        col_sp = (255, 225, 90) if off_i % 2 == 0 else TURQUESA_ÁNIMA
                        pygame.draw.circle(surface, col_sp, (sp_x, sp_y), 2)
                pygame.draw.circle(surface, (255, 245, 190), (punta_x + signo * 2, alto_pala), 2)
            return

        if postura_pisoton:
            pygame.draw.line(surface, color_mango, (centro_x, rect.centery + 2), (centro_x, base_y + 11), 4 if es_guadana else 3)
            punta_pogo_y = base_y + (16 if es_guadana else 13)
            if es_guadana:
                puntos_pogo = [
                    (centro_x - 6, base_y + 6),
                    (centro_x + 11, base_y + 7),
                    (centro_x + 9, base_y + 14),
                    (centro_x, punta_pogo_y + 2),
                    (centro_x - 3, base_y + 10),
                ]
                pygame.draw.polygon(surface, (185, 65, 235), puntos_pogo)
                pygame.draw.lines(surface, (255, 240, 255), False, puntos_pogo[:4], 2)
                pygame.draw.circle(surface, ORO_LITÚRGICO, (centro_x, base_y + 7), 2)
            else:
                pygame.draw.polygon(surface, (195, 198, 208), [(centro_x - 5, base_y + 4), (centro_x + 5, base_y + 4), (centro_x, punta_pogo_y)])
                pygame.draw.polygon(surface, ORO_LITÚRGICO, [(centro_x - 3, base_y + 5), (centro_x + 3, base_y + 5), (centro_x, punta_pogo_y - 1)])
            pygame.draw.line(surface, BLANCO, (centro_x - 4, punta_pogo_y), (centro_x + 4, punta_pogo_y), 1)
            pygame.draw.line(surface, BLANCO, (centro_x, punta_pogo_y - 4), (centro_x, punta_pogo_y + 4), 1)
            pygame.draw.circle(surface, (255, 245, 190), (centro_x, punta_pogo_y), 2)
            return

        if not con_pala:
            return
        if es_guadana:
            top_x = hombro_x + self.direccion * 2
            top_y = rect.y - 4
            bot_x = hombro_x - self.direccion * 10
            bot_y = base_y + 4
            pygame.draw.line(surface, color_mango, (top_x, top_y), (bot_x, bot_y), 3)
            pygame.draw.circle(surface, ORO_LITÚRGICO, (top_x, top_y), 2)
            signo = self.direccion
            hoja_espalda = [
                (top_x - signo * 2, top_y - 2),
                (top_x + signo * 9, top_y - 8),
                (top_x + signo * 17, top_y - 2),
                (top_x + signo * 11, top_y + 4),
                (top_x + signo * 4, top_y + 1),
            ]
            pygame.draw.polygon(surface, (190, 72, 238), hoja_espalda)
            pygame.draw.lines(surface, (255, 232, 255), False, hoja_espalda[:3], 1)
        else:
            pygame.draw.line(surface, MARRON, (hombro_x, rect.y + 7), (hombro_x - self.direccion * 4, base_y - 2), 3)
            pygame.draw.polygon(
                surface,
                GRIS,
                [(hombro_x - self.direccion * 7, base_y - 4), (hombro_x - self.direccion * 1, base_y - 1), (hombro_x - self.direccion * 4, base_y + 4)],
            )

    def _dibujar_piernas_sepulturero(self, surface, rect, pose, en_aire, atacando, postura_pisoton, despliegue_pierna, escala_y):
        """Dibuja las piernas y botas animadas según la postura."""
        centro_x = rect.centerx
        base_y = rect.bottom
        if postura_pisoton:
            cadera_y, pie_y = base_y - 9, base_y - 2
            pares = ((centro_x - 4, centro_x - 2), (centro_x + 4, centro_x + 2))
        elif en_aire:
            separacion = 7 if pose == "caida" else 9
            cadera_y, pie_y = base_y - 9, base_y - 2
            pares = ((centro_x - 5, centro_x - separacion), (centro_x + 5, centro_x + separacion))
        elif atacando:
            cadera_y, pie_y = base_y - 9, base_y - 1
            pares = ((centro_x - 5, centro_x - 7), (centro_x + 5, centro_x + 7))
        else:
            cadera_y, pie_y = base_y - int(9 * escala_y), base_y - 1
            pares = ((centro_x - 5, centro_x - 5 + despliegue_pierna), (centro_x + 5, centro_x + 5 - despliegue_pierna))

        for origen_x, pie_x in pares:
            pygame.draw.line(surface, MARRON_OSCURO, (origen_x, cadera_y), (pie_x, pie_y), 4)
            pygame.draw.line(surface, NEGRO_NOCHE, (pie_x - 2, pie_y), (pie_x + 3, pie_y), 4)

    def _dibujar_cuerpo_y_sombrero(self, surface, rect, escala_x, escala_y):
        """Dibuja el abrigo, cabeza, sombrero gótico, ojos y bufanda del sepulturero."""
        centro_x = rect.centerx
        base_y = rect.bottom
        inercia_falda = -self.direccion * min(7, int(abs(self.vx) * 0.024))
        dw = int(rect.width * (escala_x - 1.0))
        cuerpo = pygame.Rect(rect.x + 3 - dw // 2, rect.y + int(10 * escala_y), rect.width - 6 + dw, rect.height - int(16 * escala_y))

        pygame.draw.rect(surface, AZUL_OSCURO, cuerpo, border_radius=4)
        pygame.draw.rect(surface, MARRON, (cuerpo.x + 4, cuerpo.y + 5, cuerpo.width - 8, cuerpo.height - 5), border_radius=3)
        pygame.draw.rect(surface, NEGRO_NOCHE, cuerpo, 2, border_radius=4)
        pygame.draw.rect(surface, MARRON_OSCURO, (cuerpo.x, cuerpo.y + 7, cuerpo.width, 3))

        falda_y = base_y - 8
        puntos_falda = [
            (cuerpo.x, falda_y - 4),
            (cuerpo.right, falda_y - 4),
            (cuerpo.right + inercia_falda, falda_y + 4),
            (centro_x + inercia_falda * 0.7, falda_y + 2),
            (cuerpo.x + inercia_falda - 1, falda_y + 4),
        ]
        pygame.draw.polygon(surface, AZUL_OSCURO, puntos_falda)
        pygame.draw.polygon(surface, NEGRO_NOCHE, puntos_falda, 1)
        if self.dash_tiempo > 0:
            pygame.draw.rect(surface, TURQUESA_ÁNIMA, cuerpo, 1, border_radius=5)

        cabeza_y = rect.y + int(10 * escala_y)
        pygame.draw.circle(surface, (185, 175, 160), (centro_x, cabeza_y), 8)
        pygame.draw.circle(surface, NEGRO_NOCHE, (centro_x, cabeza_y), 8, 1)
        pygame.draw.polygon(
            surface,
            NEGRO_NOCHE,
            [(centro_x - 7, cabeza_y - 3), (centro_x + 7, cabeza_y - 3), (centro_x + 5, cabeza_y + 2), (centro_x - 5, cabeza_y + 2)],
        )

        ala_caida_y = cabeza_y - 6
        pygame.draw.ellipse(surface, NEGRO_NOCHE, (rect.x - 2 - dw // 2, ala_caida_y, rect.width + 4 + dw, 6))
        puntos_sombrero = [(rect.x + 4, ala_caida_y), (rect.right - 4, ala_caida_y), (centro_x - self.direccion * 4, cabeza_y - 15)]
        pygame.draw.polygon(surface, (26, 20, 30), puntos_sombrero)
        pygame.draw.polygon(surface, NEGRO_NOCHE, puntos_sombrero, 1)
        pygame.draw.rect(surface, CARMESÍ_SANGRE, (rect.x + 5, cabeza_y - 8, rect.width - 10, 2))
        pygame.draw.rect(surface, (218, 178, 86), (centro_x - 2, cabeza_y - 9, 4, 3), 1)

        ojo_base_x = centro_x + self.direccion * 2
        pygame.draw.circle(surface, (160, 215, 255), (ojo_base_x, cabeza_y), 1)
        pygame.draw.circle(surface, (160, 215, 255), (ojo_base_x + self.direccion * 3, cabeza_y), 1)

        pygame.draw.polygon(
            surface,
            (30, 24, 36),
            [(centro_x - 8, cabeza_y + 3), (centro_x - 4, cabeza_y + 8), (centro_x + 4, cabeza_y + 8), (centro_x + 8, cabeza_y + 3)],
        )
        pygame.draw.rect(surface, CARMESÍ_SANGRE, (centro_x - 7, cabeza_y + 5, 14, 3), border_radius=1)

    def _dibujar_farol_y_auras(self, surface, rect, tiempo):
        """Dibuja el farol colgante del sepulturero y las auras de bendiciones activas."""
        centro_x = rect.centerx
        farol_x = centro_x + self.direccion * 11
        farol_y = rect.y + 19

        pygame.draw.circle(surface, (115, 82, 34), (farol_x, farol_y), 6)
        pygame.draw.circle(surface, (165, 120, 50), (farol_x, farol_y), 6, 1)

        if self.tiene_dash and self.dash_listo():
            pygame.draw.circle(surface, (92, 220, 200), (farol_x, farol_y), 4)
            pygame.draw.line(surface, BLANCO, (farol_x - 5, farol_y), (farol_x + 5, farol_y), 1)
            pygame.draw.line(surface, BLANCO, (farol_x, farol_y - 5), (farol_x, farol_y + 5), 1)
            t_orb = tiempo * 6.0
            for des_ang in (0.0, math.pi):
                sx = farol_x + int(math.cos(t_orb + des_ang) * 6)
                sy = farol_y + int(math.sin(t_orb + des_ang) * 6)
                pygame.draw.circle(surface, (140, 245, 255), (sx, sy), 1)
        else:
            pygame.draw.circle(surface, (175, 115, 45), (farol_x, farol_y), 3)
            pygame.draw.circle(surface, (225, 165, 75), (farol_x, farol_y), 1)
            for h_idx in range(2):
                fase_h = (tiempo * 14.0 + h_idx * 3.0) % 7.0
                hx = farol_x - self.direccion * int(fase_h * 0.6)
                hy = farol_y - 4 - int(fase_h)
                pygame.draw.circle(surface, (125, 122, 132), (hx, hy), 1)

        pygame.draw.line(surface, GRIS, (centro_x + self.direccion * 7, rect.y + 15), (farol_x, rect.y + 15), 1)

        if getattr(self, "escudo_farol", False):
            pulso = 0.5 + 0.5 * math.sin(tiempo * 6.0)
            aura = pygame.Surface((rect.width + 24, rect.height + 24), pygame.SRCALPHA)
            pygame.draw.ellipse(aura, (92, 190, 220, int(35 + pulso * 25)), (0, 0, rect.width + 24, rect.height + 24), 1)
            pygame.draw.ellipse(aura, (140, 225, 255, int(65 + pulso * 45)), (4, 4, rect.width + 16, rect.height + 16), 2)
            surface.blit(aura, (rect.x - 12, rect.y - 12))
            for k in range(4):
                ang_runa = tiempo * 2.4 + k * (math.tau / 4.0)
                rx = centro_x + int(math.cos(ang_runa) * (rect.width // 2 + 10))
                ry = rect.centery + int(math.sin(ang_runa) * (rect.height // 2 + 8))
                pygame.draw.polygon(surface, (140, 230, 255), [(rx, ry - 3), (rx + 2, ry), (rx, ry + 3), (rx - 2, ry)])
                pygame.draw.circle(surface, BLANCO, (rx, ry), 1)

        if getattr(self, "filo_anima", False):
            for i, offset_fase in enumerate((0.0, 2.09, 4.18)):
                t_f = tiempo * 4.0 + offset_fase
                ch_x = centro_x + int(math.cos(t_f) * 14)
                ch_y = rect.centery + int(math.sin(t_f) * 14)
                col_ch = (255, 215, 80) if i % 2 == 0 else TURQUESA_ÁNIMA
                pygame.draw.circle(surface, col_ch, (ch_x, ch_y), 2)

    def dibujar(self, surface, camara, tiempo, pose=None, con_pala=True):
        if self.invulnerable > 0 and int(tiempo * 16) % 2 == 0:
            return

        rect = camara.aplicar_rect(self.rect)
        en_aire = pose in ("caida", "caida2") or not self.en_suelo
        atacando = pose in ("ataque1", "ataque2", "ataque3")
        postura_pisoton = con_pala and en_aire and self.vy > 60 and not atacando

        self._dibujar_estela_y_luz(surface, rect, tiempo)
        despliegue_pierna, escala_x, escala_y = self._calcular_pose_y_escala(atacando)
        self._dibujar_arma_sepulturero(surface, camara, rect, pose, con_pala, atacando, postura_pisoton)
        self._dibujar_piernas_sepulturero(surface, rect, pose, en_aire, atacando, postura_pisoton, despliegue_pierna, escala_y)
        self._dibujar_cuerpo_y_sombrero(surface, rect, escala_x, escala_y)
        self._dibujar_farol_y_auras(surface, rect, tiempo)
