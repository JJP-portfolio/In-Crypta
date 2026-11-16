#---- Importamos librerias y configuracion ----#

import math
import random

import pygame

import config
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
    ENEMIGO_MORTAJA,
    ENEMIGO_OJO_FUEGO,
    ENEMIGO_PURPURA,
    ENEMIGO_RIM_LUZ,
    FAROL_CÁLIDO,
    FILO_ANIMA_ALCANCE,
    FILO_ANIMA_DASH_FACTOR,
    FX_IMPACTO_BLANCO,
    GRAVEDAD,
    GRIS,
    HUESO,
    HUESO_MARFIL,
    INCENSARIO_COOLDOWN,
    INVULNERABILIDAD,
    JEFE_CARGA_VELOCIDAD,
    JEFE_VELOCIDAD,
    JEFE_VIDA,
    JEFE_VULN_FASE2,
    JUGADOR_ALTO,
    JUGADOR_ANCHO,
    JUMP_BUFFER,
    LOSA_TIEMPO_QUIEBRE,
    LOSA_TIEMPO_RECONSTRUCCION,
    MARFIL_XILOGRAFICO,
    MARRON,
    MARRON_OSCURO,
    MAX_CAIDA,
    MELEE_ACERO_CLARO,
    MINIJEFE_TELEGRAFO,
    MINIJEFE_VELOCIDAD,
    MINIJEFE_VIDA,
    MINIJEFE_VULNERABLE,
    NEGRO,
    NEGRO_NOCHE,
    ORO_LITÚRGICO,
    PIEDRA_FRIA,
    PIEDRA_OSCURA,
    POST_DASH_DURACION,
    POST_DASH_GRAVEDAD_FACTOR,
    ROJO,
    SALITRE_CRIPTA,
    SALTO,
    TILE,
    TURQUESA,
    TURQUESA_ÁNIMA,
    VELOCIDAD,
    VELOCIDAD_ENEMIGO,
    VIDAS_INICIALES,
    resolver_estilo,
)
from particulas import ParticulaPluma


#---- Funciones auxiliares ----#
def _escalar_rect_visual_enemigo(rect_camara: pygame.Rect, ancho_vis: int, alto_vis: int) -> pygame.Rect:
    """Reduce la caja de renderizado un 10%-15% manteniendo los pies apoyados en rect_camara.bottom."""
    return pygame.Rect(
        rect_camara.centerx - ancho_vis // 2,
        rect_camara.bottom - alto_vis,
        ancho_vis,
        alto_vis,
    )


def limitar(valor, minimo, maximo):
    return max(minimo, min(valor, maximo))


def _tecla_activa(teclas, key):
    if teclas is None:
        return False
    if isinstance(teclas, dict):
        return bool(teclas.get(key, False))
    try:
        return bool(teclas[key])
    except (IndexError, TypeError, KeyError):
        return False


#---- Cache de superficies de iluminacion ----#
_CACHE_LUCES = {}
_CACHE_GHOSTS = {}
_CACHE_ARCOS = {}
_CACHE_AURAS = {}
_CACHE_HALOS = {}


def obtener_aura_custodio(w, h, color, alfa):
    """Caché de aura translúcida con bordes difuminados del Custodio."""
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
            pass
        _CACHE_AURAS[clave] = surf
    return surf


def obtener_estampa_luz(radio, color, max_alfa):
    """Genera y cachea un halo radial con caída cuadrática suave para blend aditivo."""
    clave = (int(radio), tuple(color[:3]), int(max_alfa))
    surf = _CACHE_LUCES.get(clave)
    if surf is None:
        diametro = int(radio * 2)
        surf = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        cx, cy = radio, radio
        r_int = int(radio)
        paso = max(1, r_int // 24)
        cr, cg, cb = color[:3]
        intensidad = max_alfa / 255.0
        for r in range(r_int, 0, -paso):
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
    """Caché de silueta translúcida para ghosting del dash."""
    clave = (int(ancho), int(alto), int(alfa), tuple(color[:3]))
    surf = _CACHE_GHOSTS.get(clave)
    if surf is None:
        surf = pygame.Surface((int(ancho), int(alto)), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*color[:3], int(alfa)), (0, 0, ancho, alto), border_radius=6)
        pygame.draw.rect(surf, (255, 255, 255, min(255, int(alfa * 0.8))), (0, 0, ancho, alto), 1, border_radius=6)
        surf = surf.convert_alpha()
        _CACHE_GHOSTS[clave] = surf
    return surf


def obtener_arco_guadaña(direccion):
    """Caché del arco espectral de energía de la Guadaña Consagrada (3 capas)."""
    signo = 1 if direccion > 0 else -1
    clave = ("guadaña_arco_v2", signo)
    surf = _CACHE_ARCOS.get(clave)
    if surf is None:
        surf = pygame.Surface((84, 56), pygame.SRCALPHA)
        start_ang = -0.15 if signo > 0 else 1.50
        end_ang = 3.15 if signo > 0 else 4.80
        # Estela exterior amatista profunda
        pygame.draw.arc(surf, (175, 58, 232, 165), (2, 2, 80, 52), start_ang, end_ang, 7)
        # Media luna principal neón violeta
        pygame.draw.arc(surf, (232, 120, 255, 225), (4, 4, 76, 48), start_ang, end_ang, 4)
        # Filo central marfil-cristal
        pygame.draw.arc(surf, (255, 245, 255, 255), (6, 6, 72, 44), start_ang, end_ang, 2)
        # Destellos rúnicos a lo largo del tajo
        for rx, ry in ((18, 12), (40, 7), (60, 14), (28, 22)):
            pygame.draw.line(surf, (240, 200, 255, 200), (rx, ry), (rx + 4, ry + 4), 1)
            pygame.draw.line(surf, (240, 200, 255, 200), (rx + 4, ry), (rx, ry + 4), 1)
        surf = surf.convert_alpha()
        _CACHE_ARCOS[clave] = surf
    return surf


def obtener_halo_alma(step):
    """Caché de resplandor espectral tenue de Alma (atenuado para prioridad visual)."""
    step = max(0, min(7, int(step)))
    clave = ("halo_alma_v2", step)
    surf = _CACHE_HALOS.get(clave)
    if surf is None:
        surf = pygame.Surface((44, 44), pygame.SRCALPHA)
        pulso = step / 7.0
        factor = 0.8 + 0.2 * pulso
        pygame.draw.circle(surf, (160, 90, 245, int(14 * factor)), (22, 22), 18)
        pygame.draw.circle(surf, (180, 120, 255, int(28 * factor)), (22, 22), 12)
        pygame.draw.circle(surf, (210, 180, 255, int(48 * factor)), (22, 22), 6)
        surf = surf.convert_alpha()
        _CACHE_HALOS[clave] = surf
    return surf


def obtener_aura_pickup(color_base, step):
    """Caché común unificada para aura de 64x64 de pickups (Pala, Rango, Dash)."""
    step = max(0, min(7, int(step)))
    cr, cg, cb = color_base[:3]
    clave = ("aura_pickup", cr, cg, cb, step)
    surf = _CACHE_HALOS.get(clave)
    if surf is None:
        surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        pulso = step / 7.0
        factor = 0.75 + pulso * 0.25
        for radio, alfa in ((27, 24), (20, 42), (13, 72)):
            pygame.draw.circle(
                surf,
                (cr, cg, cb, int(alfa * factor)),
                (32, 32),
                radio,
            )
        surf = surf.convert_alpha()
        _CACHE_HALOS[clave] = surf
    return surf


def obtener_halo_vela_farol(step):
    """Caché de halo tenue estilo vela azul para faroles aún sin consagrar."""
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
    """Caché de resplandor para FarolCheckpoint según grado de consagración."""
    step = max(0, min(7, int(step)))
    clave = ("aura_farol", int(tier), step)
    surf = _CACHE_HALOS.get(clave)
    if surf is None:
        pulso = step / 7.0
        if tier >= 3:
            color_aura_ext = (90, 220, 255, int(45 + pulso * 25))
            color_aura_mid = (255, 215, 100, int(70 + pulso * 35))
            color_aura_int = (255, 250, 200, int(100 + pulso * 45))
        elif tier >= 2:
            color_aura_ext = (80, 200, 255, int(40 + pulso * 25))
            color_aura_mid = (160, 235, 255, int(65 + pulso * 35))
            color_aura_int = (220, 250, 255, int(90 + pulso * 40))
        else:
            color_aura_ext = (60, 180, 255, int(30 + pulso * 20))
            color_aura_mid = (140, 220, 255, int(55 + pulso * 30))
            color_aura_int = (200, 245, 255, int(80 + pulso * 40))

        radio_aura = 26 if tier >= 3 else 22
        diam = radio_aura * 2 + 4
        surf = pygame.Surface((diam, diam), pygame.SRCALPHA)
        bc = radio_aura + 2
        pygame.draw.circle(surf, color_aura_ext, (bc, bc), radio_aura)
        pygame.draw.circle(surf, color_aura_mid, (bc, bc), radio_aura // 2 + 2)
        pygame.draw.circle(surf, color_aura_int, (bc, bc), 6)
        surf = surf.convert_alpha()
        _CACHE_HALOS[clave] = surf
    return surf


def obtener_fantasma_losa(width, height, step):
    """Caché de silueta espectral translúcida para LosaQuebradiza inactiva."""
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
    """Caché de halo turquesa de campana / incensario (atenuado en reposo)."""
    step = max(0, min(7, int(step)))
    clave = ("halo_campana_v2", bool(repicando), step)
    surf = _CACHE_HALOS.get(clave)
    if surf is None:
        pulso = step / 7.0
        brillo_radio = 24 if repicando else 16
        surf = pygame.Surface((brillo_radio * 2, brillo_radio * 2), pygame.SRCALPHA)
        alfa_halo = int(60 + pulso * 40) if repicando else int(16 + pulso * 10)
        pygame.draw.circle(surf, (92, 190, 174, alfa_halo), (brillo_radio, brillo_radio), brillo_radio)
        pygame.draw.circle(surf, (180, 240, 230, int(alfa_halo * 0.7)), (brillo_radio, brillo_radio), brillo_radio // 2)
        surf = surf.convert_alpha()
        _CACHE_HALOS[clave] = surf
    return surf


def obtener_onda_campana(progreso_onda):
    """Caché de onda expansiva doble turquesa y áurea al repicar campana."""
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
        # Anillo exterior turquesa
        pygame.draw.circle(surf, (92, 190, 174, alfa_onda), (center, center), radio_onda, 2)
        # Anillo interior áureo litúrgico
        if radio_onda > 6:
            pygame.draw.circle(
                surf,
                (218, 178, 86, int(alfa_onda * 0.75)),
                (center, center),
                radio_onda - 4,
                1,
            )
        surf = surf.convert_alpha()
        _CACHE_HALOS[clave] = surf
    return surf


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


#---- Clase EntidadPatrullera ----#
class EntidadPatrullera:
    """Clase base para criaturas que patrullan horizontalmente con rebote contra límites."""

    def __init__(self, rect, minimo_x, maximo_x):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.vivo = True
        self.minimo_x = int(minimo_x)
        self.maximo_x = int(maximo_x)
        self.tiempo_flash = 0.0

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.vivo = True
        self.tiempo_flash = 0.0

    def actualizar_flash(self, dt):
        """Reduce el temporizador de damage flash si está activo."""
        if getattr(self, "tiempo_flash", 0.0) > 0:
            self.tiempo_flash = max(0.0, self.tiempo_flash - dt)

    def avanzar_patrulla(self, dt, velocidad):
        """Cinemática de patrulla horizontal con rebote contra límites y clamping."""
        self.x += self.direccion * velocidad * dt
        self.rect.x = round(self.x)

        if self.rect.left <= self.minimo_x:
            self.rect.left = self.minimo_x
            self.x = float(self.rect.x)
            self.direccion = 1
        elif self.rect.right >= self.maximo_x:
            self.rect.right = self.maximo_x
            self.x = float(self.rect.x)
            self.direccion = -1

    _PALETAS_ESPECTRO = {
        "patrulla": {
            "sombra_suelo": (7, 6, 10),
            "nes_cuerpo": (24, 32, 54),
            "snes_sombra": (20, 26, 40),
            "cuerpo": ENEMIGO_MORTAJA,
            "harapos": ((28, 36, 56), (48, 62, 90)),
            "craneo": HUESO,
            "craneo_borde": NEGRO,
            "garra_snes": HUESO,
            "fuego_base": (60, 210, 190),
            "fuego_amp": (50, 40, 50),
            "estela_ojo": (200, 20, 30),
            "ojo_nes_linea": True,
        },
        "melee": {
            "sombra_suelo": NEGRO_NOCHE,
            "nes_cuerpo": (32, 20, 44),
            "snes_sombra": (26, 16, 32),
            "cuerpo": ENEMIGO_PURPURA,
            "harapos": ((38, 22, 46), (68, 38, 80)),
            "craneo": HUESO_MARFIL,
            "craneo_borde": NEGRO_NOCHE,
            "garra_snes": HUESO_MARFIL,
            "fuego_base": (160, 40, 190),
            "fuego_amp": (50, 30, 50),
            "estela_ojo": CARMESÍ_SANGRE,
            "ojo_nes_linea": False,
        },
    }

    def _dibujar_flash_espectral(self, surface, rect, salto):
        """Dibuja silueta blanca de impacto si hay flash activo y retorna si debe cortar render."""
        if getattr(self, "tiempo_flash", 0.0) <= 0:
            return False
        pygame.draw.ellipse(surface, FX_IMPACTO_BLANCO, (rect.x - 2, rect.y + 4 + salto, rect.width + 4, rect.height - 2))
        pygame.draw.circle(surface, FX_IMPACTO_BLANCO, (rect.centerx, rect.y + 9 + salto), 9)
        return True

    def _dibujar_espectro(self, surface, rect, salto, tiempo, estilo, variante, alerta=False):
        """Renderiza el cuerpo esquelético compartido entre espectros patrulleros y melee."""
        paleta = self._PALETAS_ESPECTRO[variante]
        centro_x = rect.centerx
        base_y = rect.bottom + salto
        ojo_offset = self.direccion * 2
        ojo_y = rect.y + 8 + salto

        pygame.draw.ellipse(surface, paleta["sombra_suelo"], (rect.x + 1, rect.bottom - 4, rect.width - 2, 7))

        if estilo == "NES":
            pygame.draw.ellipse(surface, ENEMIGO_RIM_LUZ, (rect.x - 2, rect.y + 4 + salto, rect.width + 4, rect.height - 4))
            pygame.draw.circle(surface, ENEMIGO_RIM_LUZ, (centro_x, rect.y + 9 + salto), 10)
            pygame.draw.ellipse(surface, paleta["nes_cuerpo"], (rect.x, rect.y + 6 + salto, rect.width, rect.height - 6))
            pygame.draw.circle(surface, HUESO_MARFIL, (centro_x, rect.y + 9 + salto), 8)
            pygame.draw.circle(surface, (10, 8, 14), (centro_x, rect.y + 9 + salto), 8, 1)
            pygame.draw.rect(surface, ENEMIGO_OJO_FUEGO, (centro_x - 4 + ojo_offset, ojo_y - 1, 3, 2))
            pygame.draw.rect(surface, ENEMIGO_OJO_FUEGO, (centro_x + 2 + ojo_offset, ojo_y - 1, 3, 2))
            if paleta["ojo_nes_linea"]:
                pygame.draw.line(surface, (255, 220, 220), (centro_x - 5 + ojo_offset, ojo_y), (centro_x + 5 + ojo_offset, ojo_y), 1)
            for lado in (rect.x + 3, rect.right - 4):
                pygame.draw.line(surface, HUESO_MARFIL, (lado, base_y - 2), (lado, base_y + 4), 2)
            return

        es_proc = estilo != "SNES"
        pygame.draw.ellipse(surface, paleta["snes_sombra"], (rect.x - 2, rect.y + 8 + salto, rect.width + 4, rect.height - 6))
        pygame.draw.ellipse(surface, paleta["cuerpo"], (rect.x, rect.y + 6 + salto, rect.width, rect.height - 6))
        if es_proc:
            pygame.draw.arc(surface, TURQUESA_ÁNIMA, (rect.x - 2, rect.y + 3 + salto, rect.width + 4, 16), 0, math.pi, 2)
        else:
            pygame.draw.arc(surface, ENEMIGO_RIM_LUZ, (rect.x - 1, rect.y + 4 + salto, rect.width + 2, 14), 0, math.pi, 2)

        harapo_osc, harapo_cla = paleta["harapos"]
        pygame.draw.polygon(
            surface,
            harapo_osc,
            [(rect.x + 1, rect.y + 14 + salto), (rect.x + 9, rect.y + 22 + salto), (rect.x + 5, rect.y + 29 + salto), (rect.x - 1, rect.y + 20 + salto)],
        )
        pygame.draw.polygon(
            surface,
            harapo_cla,
            [(rect.x + 3, rect.y + 17 + salto), (rect.x + 10, rect.y + 23 + salto), (rect.x + 7, rect.y + 28 + salto), (rect.x + 1, rect.y + 21 + salto)],
        )
        pygame.draw.polygon(
            surface,
            harapo_osc,
            [(rect.right - 1, rect.y + 13 + salto), (rect.right - 10, rect.y + 22 + salto), (rect.right - 4, rect.y + 28 + salto), (rect.right + 1, rect.y + 19 + salto)],
        )

        pygame.draw.circle(surface, paleta["craneo"], (centro_x, rect.y + 9 + salto), 8)
        pygame.draw.circle(surface, paleta["craneo_borde"], (centro_x, rect.y + 9 + salto), 8, 1)
        pygame.draw.arc(
            surface,
            MARFIL_XILOGRAFICO if es_proc else ENEMIGO_RIM_LUZ,
            (centro_x - 8, rect.y + 1 + salto, 16, 16),
            0.2,
            math.pi - 0.2,
            2,
        )

        if es_proc:
            trail_dx = -self.direccion * 4
            pygame.draw.line(surface, paleta["estela_ojo"], (centro_x - 3 + ojo_offset, ojo_y), (centro_x - 3 + ojo_offset + trail_dx, ojo_y), 2)
            pygame.draw.line(surface, paleta["estela_ojo"], (centro_x + 3 + ojo_offset, ojo_y), (centro_x + 3 + ojo_offset + trail_dx, ojo_y), 2)

        for ox in (centro_x - 3 + ojo_offset, centro_x + 3 + ojo_offset):
            if alerta:
                pygame.draw.circle(surface, CARMESÍ_SANGRE, (ox, ojo_y), 3)
                pygame.draw.circle(surface, (255, 40, 50), (ox, ojo_y), 2)
                pygame.draw.circle(surface, BLANCO, (ox, ojo_y), 1)
            else:
                if es_proc:
                    pygame.draw.circle(surface, (180, 20, 30), (ox, ojo_y), 3)
                pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (ox, ojo_y), 2)
                pygame.draw.circle(surface, BLANCO if es_proc else (255, 200, 200), (ox + 1, ojo_y - 1), 1)

        if es_proc:
            pulso = (math.sin(tiempo * 6.0) + 1.0) * 0.5
            fr, fg, fb = paleta["fuego_base"]
            ar, ag, ab = paleta["fuego_amp"]
            col_fuego = (int(fr + ar * pulso), int(fg + ag * pulso), int(fb + ab * pulso))
            pygame.draw.circle(surface, col_fuego, (centro_x, rect.y + 21 + salto), int(2 + 2 * pulso))

        for i in range(3):
            ry = rect.y + 17 + i * 4 + salto
            if not es_proc:
                pygame.draw.line(surface, (10, 8, 14), (rect.x + 8, ry + 1), (rect.right - 8, ry + 1), 1)
            pygame.draw.line(surface, HUESO_MARFIL, (rect.x + 8, ry), (rect.right - 8, ry), 1)

        col_garra = HUESO_MARFIL if es_proc else paleta["garra_snes"]
        for lado, signo in ((4, -1), (rect.width - 5, 1)):
            bx = rect.x + lado
            for dedo_dx in (-2, 0, 2):
                pygame.draw.line(surface, col_garra, (bx + dedo_dx, base_y - 3), (bx + dedo_dx + signo, base_y + 6), 1)


#---- Clase Enemigo ----#
class Enemigo(EntidadPatrullera):
    """Morador de la cripta que patrulla de izquierda a derecha."""

    def actualizar(self, dt):
        if not self.vivo:
            return
        self.actualizar_flash(dt)
        self.avanzar_patrulla(dt, VELOCIDAD_ENEMIGO)

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return

        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 23, 23)
        salto = int(math.sin(tiempo * 7 + rect.x * 0.02) * 2)
        if self._dibujar_flash_espectral(surface, rect, salto):
            return

        estilo = resolver_estilo(getattr(config, "ESTILO_ENEMIGOS", "AUTO"))
        self._dibujar_espectro(surface, rect, salto, tiempo, estilo, "patrulla")


#---- Clase EnemigoMelee ----#
class EnemigoMelee(EntidadPatrullera):
    """Enemigo que ataca en rango melee (70px) con ciclo aviso -> estocada -> enfriamiento."""

    def __init__(self, rect, minimo_x, maximo_x):
        super().__init__(rect, minimo_x, maximo_x)
        self.aviso_tiempo = 0.0
        self.estocada_tiempo = 0.0
        self.enfriamiento_tiempo = 0.0
        self.atacando = False

    def reiniciar(self):
        super().reiniciar()
        self.aviso_tiempo = 0.0
        self.estocada_tiempo = 0.0
        self.enfriamiento_tiempo = 0.0
        self.atacando = False

    def rect_espada(self):
        """Devuelve el hitbox activo del mandoble durante la estocada."""
        if not (self.vivo and self.atacando):
            return None
        alcance = 20
        x = self.rect.right - 2 if self.direccion > 0 else self.rect.left - alcance + 2
        return pygame.Rect(x, self.rect.y + 4, alcance, max(12, self.rect.height - 8))

    def actualizar(self, dt, jugador):
        if not self.vivo:
            return

        self.actualizar_flash(dt)

        if self.estocada_tiempo > 0:
            self.estocada_tiempo = max(0.0, self.estocada_tiempo - dt)
            self.x += self.direccion * (VELOCIDAD_ENEMIGO * 2.6) * dt
            self.x = limitar(self.x, self.minimo_x, self.maximo_x)
            self.rect.x = round(self.x)
            if self.estocada_tiempo <= 0:
                self.atacando = False
                self.enfriamiento_tiempo = 0.50
            return

        if self.enfriamiento_tiempo > 0:
            self.enfriamiento_tiempo = max(0.0, self.enfriamiento_tiempo - dt)
            return

        distancia_x = abs(self.rect.centerx - jugador.rect.centerx)
        distancia_y = abs(self.rect.centery - jugador.rect.centery)

        if self.aviso_tiempo > 0:
            self.aviso_tiempo = max(0.0, self.aviso_tiempo - dt)
            if distancia_x > 2:
                self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
            if self.aviso_tiempo <= 0:
                self.estocada_tiempo = 0.22
                self.atacando = True
            return

        # Detecta al jugador en rango melee e inicia la telegrafía de estocada.
        if distancia_x <= 70 and distancia_y <= 24:
            if distancia_x > 2:
                self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
            self.aviso_tiempo = 0.28
            return

        self.avanzar_patrulla(dt, VELOCIDAD_ENEMIGO)

    def _dibujar_mandoble(self, surface, rect, salto, estilo):
        """Dibuja el mandoble del espectro melee según aviso, estocada o guardia."""
        centro_x = rect.centerx
        base_y = rect.bottom + salto
        signo = self.direccion
        espada_base_x = centro_x + signo * 8
        espada_base_y = rect.y + 14 + salto
        en_aviso = self.aviso_tiempo > 0
        en_estocada = self.atacando

        if en_estocada:
            punta_x = centro_x + signo * 26
            punta_y = rect.y + 12 + salto
        elif en_aviso:
            punta_x = centro_x + signo * 16
            punta_y = rect.y - 6 + salto
        else:
            punta_x = centro_x + signo * 12
            punta_y = base_y - 2

        if estilo == "NES":
            color_hoja = (255, 220, 130) if en_estocada else (ENEMIGO_RIM_LUZ if en_aviso else (180, 190, 210))
            pygame.draw.line(surface, color_hoja, (espada_base_x, espada_base_y), (punta_x, punta_y), 3)
            if en_aviso or en_estocada:
                pygame.draw.line(surface, BLANCO, (espada_base_x, espada_base_y), (punta_x, punta_y), 1)
            return

        pygame.draw.line(surface, MELEE_ACERO_CLARO, (espada_base_x, espada_base_y), (punta_x, punta_y), 3)
        pygame.draw.line(surface, BLANCO, (espada_base_x, espada_base_y), (punta_x, punta_y), 1)
        if en_estocada:
            pygame.draw.line(surface, (255, 195, 110), (espada_base_x, espada_base_y), (punta_x + signo * 4, punta_y), 2)
        elif en_aviso:
            pygame.draw.arc(surface, CARMESÍ_SANGRE, (rect.centerx - 14 + signo * 8, rect.y + 2, 28, 28), 0, 3.14, 2)

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return

        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 23, 24)
        salto = int(math.sin(tiempo * 7 + rect.x * 0.02) * 2)

        if self.aviso_tiempo > 0:
            rect.x += int(math.sin(tiempo * 55) * 2)
            pygame.draw.arc(surface, (210, 28, 50), (rect.centerx - 20, rect.bottom - 4, 40, 8), 0, math.pi, 2)

        if self._dibujar_flash_espectral(surface, rect, salto):
            return

        estilo = resolver_estilo(getattr(config, "ESTILO_ENEMIGOS", "AUTO"))
        self._dibujar_espectro(surface, rect, salto, tiempo, estilo, "melee", alerta=(self.aviso_tiempo > 0))
        self._dibujar_mandoble(surface, rect, salto, estilo)


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
        self.vida -= dt
        if self.vida <= 0:
            self.viva = False
            return
        self.x += self.direccion * self.velocidad * dt
        self.rect.x = round(self.x)

    def dibujar(self, surface, camara, tiempo):
        if not self.viva:
            return
        rect = camara.aplicar_rect(self.rect)
        cx = rect.centerx
        cy = rect.centery + 1
        signo = self.direccion

        # Onda de choque con cráneo rodante del osario
        # Halo de polvo / miasma a ras del suelo
        pygame.draw.ellipse(surface, (28, 22, 26), (rect.x - 4, rect.bottom - 4, rect.width + 8, 5))

        # Cráneo rodante
        pygame.draw.circle(surface, HUESO_MARFIL, (cx, cy - 2), 7)
        pygame.draw.rect(surface, HUESO_MARFIL, (cx - 4, cy + 1, 8, 4), border_radius=1)
        pygame.draw.circle(surface, NEGRO_NOCHE, (cx, cy - 2), 7, 1)

        # Cuencas oculares y nariz
        ojo_dx = signo * 2
        pygame.draw.circle(surface, NEGRO_NOCHE, (cx - 2 + ojo_dx, cy - 3), 2)
        pygame.draw.circle(surface, NEGRO_NOCHE, (cx + 3 + ojo_dx, cy - 3), 2)
        # Ojos con fulgor carmesí interior
        pygame.draw.circle(surface, CARMESÍ_SANGRE, (cx - 2 + ojo_dx, cy - 3), 1)
        pygame.draw.circle(surface, CARMESÍ_SANGRE, (cx + 3 + ojo_dx, cy - 3), 1)
        pygame.draw.rect(surface, NEGRO_NOCHE, (cx - 1 + ojo_dx, cy, 2, 2))

        # Dientes
        for dx_diente in (-3, -1, 1, 3):
            pygame.draw.line(surface, NEGRO_NOCHE, (cx + dx_diente, cy + 2), (cx + dx_diente, cy + 4), 1)

        # Cresta de esquirlas y espinas óseas que acompañan la onda
        pulso = int(2 * math.sin(tiempo * 20 + rect.x * 0.08))
        pygame.draw.arc(
            surface,
            (195, 185, 165),
            (rect.x - 6, rect.y - 4 - pulso, rect.width + 12, rect.height + 8),
            0.15,
            math.pi - 0.15,
            2,
        )
        for i in range(2):
            px = cx - signo * (6 + i * 5)
            pygame.draw.line(
                surface,
                HUESO_MARFIL,
                (px, rect.bottom - 2),
                (px - signo * 4, rect.top + 6 + i * 2),
                2,
            )


#---- Clase Custodio ----#
class Custodio:
    """Jefe final en 3 fases:
    Fase 1 (vida 6->4): pala y pisotón lo dañan en su ventana vulnerable.
    Fase 2 (vida 3->1): coraza espectral; requiere Guadaña Consagrada ('X') y suma carga.
    Fase 3 (Furia del Sepulcro - estilo Super Mario Bros. 3): invulnerable a golpes directos;
    salta sobre el sepulturero aplastando los bloques de cripta bajo sus pies hasta abrir
    el abismo y precipitarse en su propia tumba.
    """

    def __init__(self, rect, minimo_x, maximo_x):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.y_suelo = float(self.inicial_rect.y)
        self.vy = 0.0
        self.vx_smb3 = 0.0
        self.minimo_x = int(minimo_x)
        self.maximo_x = int(maximo_x)
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
        self.recien_golpeado = False
        self.ondas_recien = False
        self.aviso_recien = False
        self.embate_recien = False
        self.carga_activa = False
        self.aplasto_suelo_recien = False
        self.quiebre_sismico_recien = False
        self.en_abismo_recien = False
        self.cambio_fase3_recien = False
        self.tiempo_jugador_arriba = 0.0
        self.tiempo_muerte = 0.0
        self.tiempo_flash = 0.0

    def reiniciar(self):
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
        self.recien_golpeado = False
        self.ondas_recien = False
        self.aviso_recien = False
        self.embate_recien = False
        self.carga_activa = False
        self.aplasto_suelo_recien = False
        self.quiebre_sismico_recien = False
        self.en_abismo_recien = False
        self.cambio_fase3_recien = False
        self.tiempo_jugador_arriba = 0.0
        self.tiempo_muerte = 0.0
        self.tiempo_flash = 0.0

    def rect_embate(self):
        """Hitbox vertical del Embate Ascendente contra campanas en Fases 1 y 2."""
        if self.estado != "embate":
            return None
        alto = int(3.5 * TILE)
        ancho = 80
        return pygame.Rect(self.rect.centerx - ancho // 2, self.rect.top - alto, ancho, alto + 12)

    def rect_aplastamiento(self):
        """Franja precisa bajo los pies del Custodio (1-2 columnas de ancho y 1 sola fila de profundidad por impacto)."""
        ancho_preciso = 28
        return pygame.Rect(
            self.rect.centerx - ancho_preciso // 2,
            self.rect.bottom - 2,
            ancho_preciso,
            16,
        )

    def rect_soporte_central_f3(self):
        """Columna central bajo los pies del Custodio a través de las 4 capas de criptas ('=') en Fase 3."""
        ancho_nucleo = 28
        return pygame.Rect(
            self.rect.centerx - ancho_nucleo // 2,
            int(self.y_suelo) + self.rect.height - 2,
            ancho_nucleo,
            4 * TILE + 12,
        )

    def puede_quiebre_sismico_f3(self):
        """Indica si el Custodio está en la ventana post-salto donde un golpe quiebra 1 capa extra bajo él."""
        return (
            self.vivo
            and self.fase >= 3
            and self.estado == "aterrizaje_smb3"
            and not getattr(self, "quiebre_usado_en_salto", False)
        )

    def recibir_quiebre_sismico_f3(self, rango_mejorado=False):
        """En Fase 3, golpear al Custodio con Guadaña/Pisotón al aterrizar rompe 1 capa extra bajo sus pies."""
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
        """Culmina la Fase 3 cuando el Custodio cae en el abismo que él mismo abrió."""
        self.vivo = False
        self.estado = "muerto"
        self.tiempo_muerte = 0.0

    def _aplicar_dano(self):
        """Descuenta 1 vida, maneja transición a Fase 2 y salto a Fase 3 (Sepulcro)."""
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

        # Transición: 3 golpes acumulados en la fase 1 → avanza a Fase 2
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
        """Pala: daña en Fase 1 y (con Guadaña Consagrada) en Fase 2. Invulnerable en Fase 3."""
        if not self.vivo or not self.vulnerable or self.fase >= 3:
            return False
        if self.fase == 2 and not rango_mejorado:
            return False  # Pala rebota en Fase 2 sin power-up X
        return self._aplicar_dano()

    def recibir_pisaton(self, rango_mejorado=False):
        """Pisotón: daña en Fase 1 y (con Guadaña) en Fase 2. Invulnerable en Fase 3."""
        if not self.vivo or not self.vulnerable or self.fase >= 3:
            return False
        if self.fase == 2 and not rango_mejorado:
            return False  # Pisotón rebota en Fase 2 sin power-up X
        return self._aplicar_dano()

    def _actualizar_espera(self, dt, jugador):
        """Gestiona la patrulla fuera de rango, anti-campeo superior y elección de ataque."""
        dist_x_j = abs(jugador.rect.centerx - self.rect.centerx)
        dist_y_j = abs(jugador.rect.centery - self.rect.centery)
        en_rango_jefe = (dist_y_j <= 14 * TILE and dist_x_j <= 28 * TILE) or (self.vida < JEFE_VIDA and dist_y_j <= 14 * TILE)
        if not en_rango_jefe:
            self.tiempo_jugador_arriba = 0.0
            # Patrulla silenciosa en su catedral sin sacudir la cámara en pisos alejados.
            self.x += self.direccion * (JEFE_VELOCIDAD * 0.65) * dt
            if self.x <= self.minimo_x:
                self.x = float(self.minimo_x)
                self.direccion = 1
            elif self.x >= self.maximo_x:
                self.x = float(self.maximo_x)
                self.direccion = -1
            self.rect.x = round(self.x)
            return

        sobre_jefe = (
            self.fase in (1, 2)
            and jugador.rect.bottom <= self.rect.top + 10
            and dist_x_j <= 2.5 * TILE
        )
        if sobre_jefe:
            # Si el jugador permanece arriba sobre las campanas, el Custodio se alinea debajo y prepara Embate Ascendente
            if dist_x_j > 8:
                self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
                self.x = max(self.minimo_x, min(self.maximo_x, self.x + self.direccion * (JEFE_VELOCIDAD * 1.4) * dt))
                self.rect.x = round(self.x)
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
                self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
                self.x += self.direccion * JEFE_VELOCIDAD * dt
                self.x = max(self.minimo_x, min(self.maximo_x, self.x))
                self.rect.x = round(self.x)
        self.temporizador -= dt
        if self.temporizador <= 0:
            # Fase 2: 40 % de probabilidad de carga en lugar de pisotón.
            if self.fase >= 2 and random.random() < 0.40:
                self.estado = "telegrafia_carga"
                self.temporizador = 0.45
            else:
                self.estado = "telegrafia"
                self.temporizador = max(0.38, 0.78 - self.fase * 0.12)
            self.aviso_recien = True

    def _actualizar_carga(self, dt):
        """Ejecuta la embestida horizontal hasta agotar tiempo o impactar contra un muro."""
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

    def actualizar(self, dt, jugador, solidos_cripta=None):
        self.recien_golpeado = False
        self.ondas_recien = False
        self.aviso_recien = False
        self.embate_recien = False
        self.aplasto_suelo_recien = False
        self.quiebre_sismico_recien = False
        self.en_abismo_recien = False
        self.cambio_fase3_recien = False
        if self.tiempo_flash > 0:
            self.tiempo_flash = max(0.0, self.tiempo_flash - dt)
        if not self.vivo:
            self.tiempo_muerte += dt
            return

        if self.estado == "espera":
            self._actualizar_espera(dt, jugador)
        elif self.estado == "telegrafia":
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
                self.temporizador = JEFE_VULN_FASE2 if self.fase >= 2 else max(0.75, 1.7 - self.fase * 0.25)
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
        elif self.estado == "telegrafia_carga":
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
                self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
                self.x = max(self.minimo_x, min(self.maximo_x, self.x + self.direccion * (JEFE_VELOCIDAD * 1.5) * dt))
                self.rect.x = round(self.x)
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
        elif self.estado in ("cambio_f3", "espera_smb3", "telegrafia_smb3", "salto_smb3", "aterrizaje_smb3", "cayendo_abismo"):
            self._actualizar_fase3_smb3(dt, jugador, solidos_cripta)

    def _actualizar_fase3_smb3(self, dt, jugador, solidos_cripta):
        """Máquina de estados de Fase 3: saltos precisos que excavan las 4 capas de criptas del suelo."""
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
                self.estado = "salto_smb3"
                self.quiebre_usado_en_salto = False
                profundidad_actual = max(0.0, self.y - self.y_suelo)
                self.vy = -660.0 - min(80.0, profundidad_actual * 0.65)
                dx = float(jugador.rect.centerx - self.rect.centerx)
                self.vx_smb3 = limitar(dx / 0.72, -280.0, 280.0)
        elif self.estado == "salto_smb3":
            if self.vy < 40.0:
                objetivo_vx = limitar((jugador.rect.centerx - self.rect.centerx) * 2.5, -280.0, 280.0)
                self.vx_smb3 += (objetivo_vx - self.vx_smb3) * min(1.0, 5.0 * dt)
            else:
                # Al iniciar la caída vertical como Bowser en Mario 3, se alinea en columna para aplastar
                self.vx_smb3 *= max(0.0, 1.0 - 9.0 * dt)
            self.x = limitar(self.x + self.vx_smb3 * dt, self.minimo_x, self.maximo_x)
            self.vy += 1520.0 * dt
            self.y += self.vy * dt
            self.rect.x = round(self.x)
            self.rect.y = round(self.y)

            if self.vy > 0 and self.y >= self.y_suelo:
                franja_suelo = self.rect_soporte_central_f3()
                if solidos_cripta is not None:
                    soportes = [s for s in solidos_cripta if franja_suelo.colliderect(s)]
                    if soportes:
                        y_aterrizaje = float(min(s.top for s in soportes) - self.rect.height)
                        if self.y >= y_aterrizaje:
                            self.y = y_aterrizaje
                            self.vy = 0.0
                            self.vx_smb3 = 0.0
                            self.rect.y = round(self.y)
                            self.aplasto_suelo_recien = True
                            self.ondas_recien = True
                            self.saltos_smb3 += 1
                            self.estado = "aterrizaje_smb3"
                            self.temporizador = 0.50
                    else:
                        self.estado = "cayendo_abismo"
                        self.en_abismo_recien = True
                        self.vy = max(self.vy, 280.0)
                else:
                    self.y = self.y_suelo
                    self.vy = 0.0
                    self.vx_smb3 = 0.0
                    self.rect.y = round(self.y)
                    self.aplasto_suelo_recien = True
                    self.ondas_recien = True
                    self.saltos_smb3 += 1
                    self.estado = "aterrizaje_smb3"
                    self.temporizador = 0.50
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

    def _dibujar_auras_estado(self, surface, rect, tiempo, pulso):
        """Dibuja la sombra, las auras de fase/vulnerabilidad y el brillo de telegrafía."""
        pygame.draw.ellipse(surface, NEGRO_NOCHE, (rect.x, rect.bottom - 6, rect.width, 10))
        if self.fase >= 3:
            aura_f3 = obtener_aura_custodio(rect.width + 28, rect.height + 26, (165, 70, 235), int(30 + pulso * 30))
            surface.blit(aura_f3, (rect.x - 14, rect.y - 13))
            pygame.draw.ellipse(surface, (205, 130, 255), rect.inflate(14, 10), 2)
            if self.estado == "aterrizaje_smb3":
                # Anillo sísmico dorado/violeta en la base indicando ventana de Quiebre Sísmico
                anillo_sismico = pygame.Rect(rect.x - 14, rect.bottom - 10, rect.width + 28, 16)
                pygame.draw.ellipse(surface, ORO_LITÚRGICO, anillo_sismico, 2)
                pygame.draw.ellipse(surface, (235, 180, 255), anillo_sismico.inflate(8, 4), 1)
        elif self.fase == 2:
            if self.vulnerable:
                # Guardia abierta en Fase 2: aura dorada-carmesí y escudo fragmentado en arcos
                aura = obtener_aura_custodio(rect.width + 26, rect.height + 24, ORO_LITÚRGICO, int(34 + pulso * 26))
                surface.blit(aura, (rect.x - 13, rect.y - 12))
                ring_box = rect.inflate(20, 18)
                for ang_ini in (0.2, 1.8, 3.4, 5.0):
                    pygame.draw.arc(surface, ORO_LITÚRGICO, ring_box, ang_ini, ang_ini + 0.7, 2)
            else:
                # Guardia cerrada en Fase 2: escudo espectral carmesí continuo
                aura = obtener_aura_custodio(rect.width + 24, rect.height + 22, CARMESÍ_SANGRE, int(22 + pulso * 24))
                surface.blit(aura, (rect.x - 12, rect.y - 11))
                for r_offset in (16, 26):
                    ondulacion = int(2.5 * math.sin(tiempo * 7.5 + r_offset * 0.3))
                    ring_box = pygame.Rect(
                        rect.x - r_offset // 2,
                        rect.y - r_offset // 2 + ondulacion,
                        rect.width + r_offset,
                        rect.height + r_offset,
                    )
                    pygame.draw.ellipse(surface, CARMESÍ_SANGRE, ring_box, 1)
        elif self.vulnerable:
            aura = obtener_aura_custodio(rect.width + 18, rect.height + 16, ORO_LITÚRGICO, 32)
            surface.blit(aura, (rect.x - 9, rect.y - 8))

        if self.estado in ("telegrafia", "telegrafia_carga", "telegrafia_smb3", "telegrafia_embate"):
            color_brillo = (
                (245, 200, 80) if self.estado == "telegrafia_embate"
                else ((185, 85, 255) if self.estado == "telegrafia_smb3"
                      else (CARMESÍ_SANGRE if self.estado == "telegrafia_carga" else (180, 32, 42)))
            )
            brillo = obtener_aura_custodio(rect.width + 48, rect.height + 40, color_brillo, int(45 + pulso * 35))
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
        """Dibuja la capa episcopal, el brocado pectoral y la mitra litúrgica."""
        centro_x = rect.centerx
        base_y = rect.bottom
        capa_color = (68, 16, 22) if self.fase >= 2 else (38, 28, 44)
        pygame.draw.polygon(
            surface,
            capa_color,
            [
                (centro_x - 24, base_y - 2),
                (centro_x - 18, rect.y + 18),
                (centro_x - 8, rect.y + 4),
                (centro_x + 8, rect.y + 2),
                (centro_x + 20, rect.y + 20),
                (centro_x + 27, base_y - 2),
            ],
        )
        cuerpo_color = (44, 14, 18) if self.fase >= 2 else (23, 19, 28)
        pygame.draw.rect(surface, cuerpo_color, (centro_x - 21, rect.y + 12, 42, 44), border_radius=10)
        pygame.draw.line(surface, ORO_LITÚRGICO if self.fase < 2 else (180, 50, 45), (centro_x - 15, rect.y + 26), (centro_x + 15, rect.y + 26), 2)
        for i in range(4):
            pygame.draw.line(
                surface,
                HUESO_MARFIL if self.fase < 2 else (160, 40, 50),
                (centro_x - 14 + i * 2, rect.y + 31 + i * 4),
                (centro_x + 14 - i * 2, rect.y + 31 + i * 4),
                1,
            )

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
        pygame.draw.line(surface, ORO_LITÚRGICO, (centro_x - 3, mitra_y - 9), (centro_x + 3, mitra_y - 9), 1)

    def _dibujar_craneo_y_farol(self, surface, rect):
        """Dibuja el cráneo colosal, sus ojos expresivos y el farol pectoral."""
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
        """Dibuja la maza de osario orientada hacia la dirección del Custodio (alzada en Embate Ascendente)."""
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
        if not self.vivo:
            return
        rect = camara.aplicar_rect(self.rect)
        pulso = 0.5 + 0.5 * math.sin(tiempo * 5)

        self._dibujar_auras_estado(surface, rect, tiempo, pulso)
        self._dibujar_vestimenta_y_mitra(surface, rect)
        self._dibujar_craneo_y_farol(surface, rect)
        self._dibujar_maza_osario(surface, rect)

        if self.vulnerable or self.puede_quiebre_sismico_f3():
            # Emblema de guardia abierta sobre la mitra para indicar el momento exacto de atacar
            bob = int(2.5 * math.sin(tiempo * 9.0))
            cx, cy = rect.centerx, rect.y - 24 + bob
            color_emblema = (225, 165, 255) if self.puede_quiebre_sismico_f3() else ORO_LITÚRGICO
            rombo = [(cx, cy - 6), (cx + 6, cy), (cx, cy + 6), (cx - 6, cy)]
            pygame.draw.polygon(surface, color_emblema, rombo)
            pygame.draw.polygon(surface, BLANCO, rombo, 1)

        if self.tiempo_flash > 0:
            flash_overlay = obtener_aura_custodio(rect.width, rect.height, (140, 140, 140), 140)
            surface.blit(flash_overlay, rect.topleft, special_flags=pygame.BLEND_RGB_ADD)


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


#---- Clase Cuervo ----#
class Cuervo:
    """Cuervo poeano que vuela en patrón circular con aleteo articulado y plumas negras."""

    def __init__(self, rect, centro_x, centro_y, radio, velocidad):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.centro_x = centro_x
        self.centro_y = centro_y
        self.radio = radio
        self.velocidad = velocidad
        self.angulo = 0.0
        self.vivo = True
        self.plumas = []
        self.tiempo_pluma = 0.0
        self.tiempo_flash = 0.0

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.angulo = 0.0
        self.vivo = True
        self.plumas = []
        self.tiempo_pluma = 0.0
        self.tiempo_flash = 0.0

    def actualizar(self, dt):
        if not self.vivo:
            return

        if getattr(self, "tiempo_flash", 0.0) > 0:
            self.tiempo_flash = max(0.0, self.tiempo_flash - dt)

        self.angulo += self.velocidad * dt
        self.x = self.centro_x + math.cos(self.angulo) * self.radio - self.rect.width // 2
        self.y = self.centro_y + math.sin(self.angulo) * self.radio * 0.5 - self.rect.height // 2
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)

        # Emisión de plumas negras livianas que caen lentamente
        self.tiempo_pluma += dt
        if self.tiempo_pluma >= 0.38:
            self.tiempo_pluma = 0.0
            if len(self.plumas) < 12:
                self.plumas.append(ParticulaPluma(self.rect.centerx, self.rect.centery))

        for pluma in self.plumas:
            pluma.actualizar(dt)
        self.plumas = [p for p in self.plumas if p.vida > 0]

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return

        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 20, 20)
        if getattr(self, "tiempo_flash", 0.0) > 0:
            pygame.draw.ellipse(surface, FX_IMPACTO_BLANCO, rect)
            return

        # Dibujar plumas desprendidas primero
        for pluma in self.plumas:
            pluma.dibujar(surface, camara)

        centro_x = rect.centerx
        base_y = rect.bottom

        # Sombra sutil en el suelo
        pygame.draw.ellipse(surface, NEGRO_NOCHE, (rect.x + 2, base_y - 4, rect.width - 4, 5))

        # Aleteo articulado con apertura tensa en fase descendente
        fase_descenso = math.cos(self.angulo) < 0
        aleteo = int(math.sin(tiempo * 16.0) * (3 if fase_descenso else 5))

        # Cuerpo del cuervo (silueta afilada en negro carbón poeano) con recorte cenital marfil de 2px
        pygame.draw.ellipse(surface, (14, 12, 18), (rect.x + 2, rect.y + 4, rect.width - 4, rect.height - 8))
        pygame.draw.ellipse(surface, (25, 22, 32), (rect.x + 4, rect.y + 5, rect.width - 8, rect.height - 10))
        pygame.draw.arc(surface, MARFIL_XILOGRAFICO, (rect.x + 3, rect.y + 3, rect.width - 6, 7), 0.2, math.pi - 0.2, 2)

        # Alas articuladas con 3 primarias escalonadas y borde de luz de recorte
        ala_izq_puntos = [
            (rect.centerx - 2, rect.y + 7),
            (rect.x - (4 if fase_descenso else 2), rect.y + 1 - aleteo),
            (rect.x + 3, rect.y + 5 - aleteo // 2),
            (rect.centerx - 2, rect.y + 9),
        ]
        pygame.draw.polygon(surface, (10, 8, 14), ala_izq_puntos)
        pygame.draw.line(surface, ENEMIGO_RIM_LUZ, ala_izq_puntos[1], ala_izq_puntos[2], 1)

        ala_der_puntos = [
            (rect.centerx + 2, rect.y + 7),
            (rect.right + (4 if fase_descenso else 2), rect.y + 1 - aleteo),
            (rect.right - 3, rect.y + 5 - aleteo // 2),
            (rect.centerx + 2, rect.y + 9),
        ]
        pygame.draw.polygon(surface, (10, 8, 14), ala_der_puntos)
        pygame.draw.line(surface, ENEMIGO_RIM_LUZ, ala_der_puntos[1], ala_der_puntos[2], 1)

        # Cola afilada en cuña
        pygame.draw.polygon(surface, (10, 8, 14), [
            (centro_x - 3, rect.bottom - 5),
            (centro_x, rect.bottom),
            (centro_x + 3, rect.bottom - 5),
        ])

        # Pico curvado de cuervo en cuerno oscuro
        pygame.draw.polygon(surface, (58, 48, 38), [
            (rect.centerx, rect.y + 11),
            (rect.centerx + 5, rect.y + 14),
            (rect.centerx, rect.y + 16),
        ])

        # Ojos con estela ocular roja de 4px
        trail_dx = -4 if math.cos(self.angulo) >= 0 else 4
        ojo_x = centro_x - 2
        ojo_y = rect.y + 10
        pygame.draw.line(surface, (210, 28, 50), (ojo_x, ojo_y), (ojo_x + trail_dx, ojo_y), 1)
        pygame.draw.circle(surface, (235, 180, 40), (ojo_x, ojo_y), 1.5)
        pygame.draw.circle(surface, BLANCO, (ojo_x, ojo_y), 0.5)


#---- Clase Polilla ----#
class Polilla(EntidadPatrullera):
    """Polilla que vuela en zigzag lento. Daño por contacto."""

    def __init__(self, rect, minimo_x, maximo_x):
        super().__init__(rect, minimo_x, maximo_x)
        self.tiempo = 0.0

    def reiniciar(self):
        super().reiniciar()
        self.tiempo = 0.0

    def actualizar(self, dt):
        if not self.vivo:
            return
        self.actualizar_flash(dt)
        self.tiempo += dt
        self.avanzar_patrulla(dt, VELOCIDAD_ENEMIGO * 0.6)
        # Movimiento vertical suave (zigzag).
        self.rect.y = round(self.inicial_rect.y + math.sin(self.tiempo * 3) * 8)

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return
        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 22, 22)
        if getattr(self, "tiempo_flash", 0.0) > 0:
            pygame.draw.ellipse(surface, FX_IMPACTO_BLANCO, rect)
            return

        centro_x = rect.centerx
        base_y = rect.bottom

        # Esporas lumínicas orgánicas al aproximarse al cambio de vector
        if abs(self.rect.left - self.minimo_x) < 16 or abs(self.rect.right - self.maximo_x) < 16:
            pygame.draw.circle(surface, (92, 220, 200), (centro_x + int(math.sin(tiempo * 14.0) * 8), rect.y + 3), 1)

        pygame.draw.ellipse(surface, (7, 6, 10), (rect.x + 2, base_y - 4, rect.width - 4, 5))

        # Cuerpo de polilla con borde turquesa y recorte cenital marfil de 2px
        pygame.draw.ellipse(surface, (28, 38, 48), (rect.x + 3, rect.y + 4, rect.width - 6, rect.height - 8))
        pygame.draw.arc(surface, MARFIL_XILOGRAFICO, (rect.x + 3, rect.y + 3, rect.width - 6, 8), 0.2, math.pi - 0.2, 2)

        # Alas con borde de luz de recorte
        pygame.draw.ellipse(surface, (55, 60, 75), (rect.x, rect.y + 2, rect.width // 2, rect.height // 2))
        pygame.draw.ellipse(surface, (55, 60, 75), (rect.x + rect.width // 2, rect.y + 2, rect.width // 2, rect.height // 2))
        pygame.draw.arc(surface, ENEMIGO_RIM_LUZ, (rect.x, rect.y + 2, rect.width // 2, rect.height // 2), 0, math.pi, 1)
        pygame.draw.arc(surface, ENEMIGO_RIM_LUZ, (rect.x + rect.width // 2, rect.y + 2, rect.width // 2, rect.height // 2), 0, math.pi, 1)

        # Estela ocular roja de 4px y ojos brillantes
        trail_dx = -self.direccion * 4
        pygame.draw.line(surface, (210, 28, 50), (centro_x - 2, rect.y + 8), (centro_x - 2 + trail_dx, rect.y + 8), 1)
        pygame.draw.line(surface, (210, 28, 50), (centro_x + 2, rect.y + 8), (centro_x + 2 + trail_dx, rect.y + 8), 1)
        pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (centro_x - 2, rect.y + 8), 1.5)
        pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (centro_x + 2, rect.y + 8), 1.5)


#---- Clase Araña ----#
class Araña(EntidadPatrullera):
    """Araña que se mueve por el techo o suelo. Daño por contacto."""

    def actualizar(self, dt):
        if not self.vivo:
            return
        self.actualizar_flash(dt)
        self.avanzar_patrulla(dt, VELOCIDAD_ENEMIGO * 0.8)

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return
        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 22, 18)
        if getattr(self, "tiempo_flash", 0.0) > 0:
            pygame.draw.ellipse(surface, FX_IMPACTO_BLANCO, rect)
            return

        centro_x = rect.centerx
        base_y = rect.bottom

        pygame.draw.ellipse(surface, (7, 6, 10), (rect.x + 2, base_y - 4, rect.width - 4, 5))

        # Cuerpo de araña con recorte cenital marfil de 2px
        pygame.draw.ellipse(surface, (18, 14, 24), (rect.x + 3, rect.y + 4, rect.width - 6, rect.height - 7))
        pygame.draw.arc(surface, MARFIL_XILOGRAFICO, (rect.x + 3, rect.y + 3, rect.width - 6, 7), 0.2, math.pi - 0.2, 2)

        # Patas articuladas con vibración rápida
        vib = int(math.sin(tiempo * 24.0) * 2)
        for i in range(3):
            dx = (i - 1) * 4
            pata_y = rect.y + 13 + (vib if i % 2 == 0 else -vib)
            pygame.draw.line(surface, (24, 20, 32), (centro_x + dx, rect.y + 8), (rect.x + dx - 5, pata_y), 2)
            pygame.draw.line(surface, ENEMIGO_RIM_LUZ, (rect.x + dx - 5, pata_y), (rect.x + dx - 3, pata_y), 1)
            pygame.draw.line(surface, (24, 20, 32), (centro_x + dx, rect.y + 8), (rect.right - dx + 5, pata_y), 2)
            pygame.draw.line(surface, ENEMIGO_RIM_LUZ, (rect.right - dx + 3, pata_y), (rect.right - dx + 5, pata_y), 1)

        # Ojos con estela ocular roja de 4px
        trail_dx = -self.direccion * 4
        pygame.draw.line(surface, (210, 28, 50), (centro_x - 2, rect.y + 7), (centro_x - 2 + trail_dx, rect.y + 7), 1)
        pygame.draw.line(surface, (210, 28, 50), (centro_x + 2, rect.y + 7), (centro_x + 2 + trail_dx, rect.y + 7), 1)
        pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (centro_x - 2, rect.y + 7), 1.5)
        pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (centro_x + 2, rect.y + 7), 1.5)
        pygame.draw.circle(surface, ROJO, (centro_x - 2, rect.y + 7), 1)
        pygame.draw.circle(surface, ROJO, (centro_x + 2, rect.y + 7), 1)


#---- Clase Alma ----#
class Alma:
    """Alma flotante que se puede recoger una sola vez."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.recogida = False

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.recogida = False

    def actualizar(self, jugador):
        if not self.recogida and self.rect.colliderect(jugador.rect):
            self.recogida = True
            jugador.almas += 1
            return True
        return False

    def dibujar(self, surface, camara, tiempo):
        if self.recogida:
            return

        rect = camara.aplicar_rect(self.rect)
        flotacion = int(math.sin(tiempo * 5 + rect.x * 0.03) * 3)
        centro = (rect.centerx, rect.centery + flotacion)

        # Resplandor espectral translúcido suave cacheado
        pulso = 0.5 + 0.5 * math.sin(tiempo * 6 + rect.x * 0.04)
        halo_alma = obtener_halo_alma(int(pulso * 7))
        surface.blit(halo_alma, (centro[0] - 22, centro[1] - 22))

        # Núcleo sagrado de ánima
        pygame.draw.circle(surface, (220, 190, 255), centro, 3)
        pygame.draw.polygon(
            surface,
            TURQUESA,
            [
                (centro[0], centro[1] - 9),
                (centro[0] + 4, centro[1] - 2),
                (centro[0], centro[1] + 6),
                (centro[0] - 4, centro[1] - 2),
            ],
        )


#---- Clase PowerUpBase ----#
class PowerUpBase:
    """Clase base para reliquias y power-ups de altares con halo y flotación."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.recogida = False

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.recogida = False

    def obtener_transformacion_visual(self, camara, tiempo):
        """Calcula el rectángulo con flotación vertical y el pulso sinusoidal."""
        rect = camara.aplicar_rect(self.rect)
        flotacion = int(math.sin(tiempo * 4 + rect.x * 0.02) * 3)
        rect.y += flotacion
        pulso = 0.5 + 0.5 * math.sin(tiempo * 5 + rect.x * 0.03)
        return rect, pulso

    def dibujar_aura_base(self, surface, rect, pulso, color_rgb, radio_circulo=14):
        """Dibuja el resplandor aditivo exterior y el halo litúrgico."""
        brillo = obtener_aura_pickup(color_rgb, int(pulso * 7))
        surface.blit(brillo, (rect.centerx - 32, rect.centery - 32))


#---- Clase PalaRecogible ----#
class PalaRecogible(PowerUpBase):
    """Pala que desbloquea el ataque y el pisotón."""

    def actualizar(self, jugador):
        if not self.recogida and self.rect.colliderect(jugador.rect):
            self.recogida = True
            jugador.tiene_pala = True
            return True
        return False

    def dibujar(self, surface, camara, tiempo):
        if self.recogida:
            return

        rect, pulso = self.obtener_transformacion_visual(camara, tiempo)
        self.dibujar_aura_base(surface, rect, pulso, (255, 191, 82), 17)
        pygame.draw.circle(
            surface,
            (238, 188, 86),
            (rect.centerx, rect.centery),
            17 + int(pulso * 2),
            1,
        )
        for giro in (0.0, math.pi / 2, math.pi, math.pi * 1.5):
            angulo = tiempo * 1.8 + giro
            x = rect.centerx + int(math.cos(angulo) * (20 + pulso * 4))
            y = rect.centery + int(math.sin(angulo) * (20 + pulso * 4))
            pygame.draw.circle(surface, (255, 225, 150), (x, y), 2)
            pygame.draw.line(surface, (255, 205, 105), (x - 3, y), (x + 3, y), 1)
            pygame.draw.line(surface, (255, 205, 105), (x, y - 3), (x, y + 3), 1)
        pygame.draw.line(
            surface,
            MARRON,
            (rect.x + 5, rect.bottom - 3),
            (rect.x + 13, rect.y + 5),
            3,
        )
        pygame.draw.polygon(
            surface,
            GRIS,
            [
                (rect.x + 10, rect.y + 2),
                (rect.x + 18, rect.y + 8),
                (rect.x + 12, rect.y + 14),
                (rect.x + 5, rect.y + 8),
            ],
        )
        pygame.draw.line(
            surface,
            BLANCO,
            (rect.x + 9, rect.y + 6),
            (rect.x + 15, rect.y + 9),
            1,
        )


#---- Clase RangoPowerUp ----#
class RangoPowerUp(PowerUpBase):
    """Power-up que mejora el alcance del ataque de pala (Guadaña Consagrada, 'X').

    Mientras `sellado` sea True (el Carcelero del Osario sigue vivo) el altar
    no puede recogerse: el Mini-Boss despeja el camino al morir.
    """

    def __init__(self, rect):
        super().__init__(rect)
        self.sellado = False

    def actualizar(self, jugador):
        if self.sellado:
            return False
        if not self.recogida and self.rect.colliderect(jugador.rect):
            self.recogida = True
            jugador.rango_ataque_mejorado = True
            return True
        return False

    def dibujar(self, surface, camara, tiempo):
        if self.recogida:
            return

        rect = camara.aplicar_rect(self.rect)
        if self.sellado:
            # Altar sellado: guadaña apagada tras cadenas cruzadas y candado rúnico.
            cx, cy = rect.centerx, rect.centery
            pygame.draw.circle(surface, (55, 38, 68), (cx, cy), 15, 1)
            pygame.draw.line(surface, (70, 50, 82), (cx - 8, cy + 10), (cx + 5, cy - 8), 3)
            pygame.draw.arc(surface, (115, 82, 140), (cx - 4, cy - 14, 16, 14), 0.2, 3.0, 3)
            pygame.draw.line(surface, (130, 125, 140), (cx - 12, cy - 12), (cx + 12, cy + 12), 2)
            pygame.draw.line(surface, (130, 125, 140), (cx + 12, cy - 12), (cx - 12, cy + 12), 2)
            pygame.draw.rect(surface, (165, 130, 62), (cx - 4, cy - 2, 8, 7), border_radius=1)
            return

        rect, pulso = self.obtener_transformacion_visual(camara, tiempo)
        self.dibujar_aura_base(surface, rect, pulso, (200, 100, 255), 16)
        pygame.draw.circle(
            surface,
            (230, 150, 255),
            (rect.centerx, rect.centery),
            15 + int(pulso * 2),
            1,
        )
        # Guadaña Consagrada: asta de ébano/bronce + hoja creciente de amatista y filo marfil.
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
    """Power-up que desbloquea el dash espectral (Amuleto de Sombras)."""

    def actualizar(self, jugador):
        if not self.recogida and self.rect.colliderect(jugador.rect):
            self.recogida = True
            jugador.tiene_dash = True
            return True
        return False

    def dibujar(self, surface, camara, tiempo):
        if self.recogida:
            return

        rect, pulso = self.obtener_transformacion_visual(camara, tiempo)
        self.dibujar_aura_base(surface, rect, pulso, (70, 210, 255), 14)
        pygame.draw.circle(
            surface,
            (140, 230, 255),
            (rect.centerx, rect.centery),
            14 + int(pulso * 2),
            1,
        )
        # Alas espectrales estilizadas
        cx, cy = rect.centerx, rect.centery
        ala_izq = [(cx - 2, cy + 3), (cx - 9, cy - 2), (cx - 13, cy - 8), (cx - 6, cy - 6), (cx - 2, cy - 1)]
        ala_der = [(cx + 2, cy + 3), (cx + 9, cy - 2), (cx + 13, cy - 8), (cx + 6, cy - 6), (cx + 2, cy - 1)]
        pygame.draw.polygon(surface, (140, 230, 255), ala_izq)
        pygame.draw.polygon(surface, (140, 230, 255), ala_der)
        pygame.draw.polygon(surface, (230, 250, 255), [(p[0], p[1] + 1) for p in ala_izq[:3]])
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 3)
        pygame.draw.circle(surface, (50, 180, 240), (cx, cy), 2)


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




