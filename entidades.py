# ============================================================
# entidades.py — El sepulturero, los moradores y las almas
# ============================================================
# Cada clase guarda su estado y sabe actualizarse/dibujarse.
# La física está separada en métodos pequeños para poder probarla.
# ============================================================

import math

import pygame

from config import (
    AMARILLO,
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
    COYOTE_TIME,
    CORTE_SALTO,
    CREMA,
    DASH_COOLDOWN,
    DASH_DURACION,
    DASH_JUMP_IMPULSO_X,
    DASH_USOS_AIRE,
    DASH_VELOCIDAD,
    ENEMIGO_ALTO,
    ENEMIGO_ANCHO,
    FAROL_CÁLIDO,
    GRAVEDAD,
    GRIS,
    GRIS_OSCURO,
    HUESO,
    HUESO_MARFIL,
    INVULNERABILIDAD,
    JEFE_ALTO,
    JEFE_ANCHO,
    JEFE_CARGA_VELOCIDAD,
    JEFE_VELOCIDAD,
    JEFE_VIDA,
    JEFE_VULN_FASE2,
    JUMP_BUFFER,
    JUGADOR_ALTO,
    JUGADOR_ANCHO,
    MARRON,
    MARRON_OSCURO,
    MAX_CAIDA,
    MINIJEFE_ALTO,
    MINIJEFE_ANCHO,
    MINIJEFE_TELEGRAFO,
    MINIJEFE_VELOCIDAD,
    MINIJEFE_VIDA,
    MINIJEFE_VULNERABLE,
    MUSGO,
    NARANJA,
    NEGRO,
    NEGRO_NOCHE,
    ORO,
    ORO_LITÚRGICO,
    POST_DASH_DURACION,
    POST_DASH_GRAVEDAD_FACTOR,
    ROJO,
    SALTO,
    SANGRE,
    TURQUESA,
    TURQUESA_ÁNIMA,
    VELOCIDAD,
    VELOCIDAD_ENEMIGO,
    VERDE_OSCURO,
    VIDAS_INICIALES,
    VIOLETA,
    VIOLETA_POE,
)
from particulas import ParticulaPluma


# --- Función auxiliar: recortar un valor entre mínimo y máximo --- #
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


# --- Caché de iluminación radial y siluetas para 60 FPS estables --- #
_CACHE_LUCES = {}
_CACHE_GHOSTS = {}
_CACHE_ARCOS = {}
_CACHE_AURAS = {}


def obtener_aura_custodio(w, h, color, alfa):
    """Caché de aura translúcida del Custodio para cero asignaciones por frame."""
    clave = (int(w), int(h), tuple(color[:3]), int(alfa))
    surf = _CACHE_AURAS.get(clave)
    if surf is None:
        surf = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (*color[:3], int(alfa)), surf.get_rect())
        surf = surf.convert_alpha()
        _CACHE_AURAS[clave] = surf
    return surf


def obtener_estampa_luz(radio, color, max_alfa):
    """Genera y cachea un halo radial con desvanecimiento cuadrático suave."""
    clave = (int(radio), tuple(color[:3]), int(max_alfa))
    surf = _CACHE_LUCES.get(clave)
    if surf is None:
        diametro = int(radio * 2)
        surf = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
        cx, cy = radio, radio
        r_int = int(radio)
        paso = max(1, r_int // 18)
        for r in range(r_int, 0, -paso):
            norm = r / radio
            factor = max(0.0, (1.0 - norm * norm) ** 1.5)
            alfa = int(max_alfa * factor)
            if alfa > 0:
                pygame.draw.circle(surf, (*color[:3], alfa), (int(cx), int(cy)), r)
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
    """Caché del arco espectral de energía de 76px de la Guadaña Mística."""
    signo = 1 if direccion > 0 else -1
    clave = ("guadaña_arco", signo)
    surf = _CACHE_ARCOS.get(clave)
    if surf is None:
        surf = pygame.Surface((80, 52), pygame.SRCALPHA)
        start_ang = 0.0 if signo > 0 else 1.57
        end_ang = 3.14 if signo > 0 else 4.71
        # Arco violeta místico
        pygame.draw.arc(surf, (215, 80, 255, 190), (2, 2, 76, 48), start_ang, end_ang, 5)
        # Filo central blanco luminoso
        pygame.draw.arc(surf, (255, 235, 255, 255), (4, 4, 72, 44), start_ang, end_ang, 2)
        # Runas flotantes translúcidas
        for rx, ry in ((22, 10), (42, 8), (62, 16)):
            pygame.draw.line(surf, (230, 180, 255, 180), (rx, ry), (rx + 4, ry + 4), 1)
            pygame.draw.line(surf, (230, 180, 255, 180), (rx + 4, ry), (rx, ry + 4), 1)
        surf = surf.convert_alpha()
        _CACHE_ARCOS[clave] = surf
    return surf


# --- Clase Jugador --- #
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

    # --- Función pedir_salto --- #
    def pedir_salto(self):
        """Se llama en KEYDOWN: deja preparado el salto."""
        self.buffer_salto = JUMP_BUFFER
        self.manteniendo_salto = True

    # --- Función soltar_salto --- #
    def soltar_salto(self):
        """Se llama en KEYUP: corta el salto si todavía sube."""
        self.manteniendo_salto = False
        if self.vy < 0:
            self.vy *= CORTE_SALTO

    # --- Función pedir_dash --- #
    def pedir_dash(self):
        """Inicia un dash si hay carga, la habilidad está desbloqueada y, en el aire, queda un uso."""
        if not self.tiene_dash:
            return False
        if self.dash_tiempo > 0 or self.dash_cooldown > 0:
            return False
        if not self.en_suelo and self.dash_usos_aire <= 0:
            return False

        self.dash_tiempo = DASH_DURACION
        self.dash_cooldown = DASH_COOLDOWN
        self.dash_direccion = self.direccion

        if not self.en_suelo:
            self.dash_usos_aire -= 1

        self.vx = self.direccion * DASH_VELOCIDAD
        self.vy = 0.0
        self.dash_recien = True
        return True

    # --- Función dash_listo --- #
    def dash_listo(self):
        return (
            self.tiene_dash
            and self.dash_tiempo <= 0
            and self.dash_cooldown <= 0
            and (self.en_suelo or self.dash_usos_aire > 0)
        )

    # --- Función pedir_ataque --- #
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

    # --- Función rect_ataque --- #
    def rect_ataque(self):
        es_guadaña = self.rango_ataque_mejorado
        alcance = ATAQUE_ALCANCE_MEJORADO if es_guadaña else ATAQUE_ALCANCE
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

    # --- Función pose_actual --- #
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

    # --- Función actualizar --- #
    def actualizar(self, dt, teclas, solidos):
        self.salto_recien = False
        self.dash_recien = False

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
            else:
                self.actualizar_dash(dt, solidos)
                return

        self.actualizar_horizontal(teclas)

        if self.buffer_salto > 0 and (self.en_suelo or self.coyote > 0):
            self.vy = SALTO
            self.en_suelo = False
            self.coyote = 0.0
            self.buffer_salto = 0.0
            self.salto_recien = True

        # Gravedad con Apex Hang-Time (flotación en cima de salto) y Post-Dash Float
        factor_gravedad = 1.0
        if self.post_dash_tiempo > 0:
            factor_gravedad = min(factor_gravedad, POST_DASH_GRAVEDAD_FACTOR)

        salto_mantenido = (
            self.manteniendo_salto
            or _tecla_activa(teclas, pygame.K_SPACE)
            or _tecla_activa(teclas, pygame.K_UP)
            or _tecla_activa(teclas, pygame.K_w)
            or _tecla_activa(teclas, pygame.K_z)
        )
        if not self.en_suelo and abs(self.vy) < APEX_VY_UMBRAL and salto_mantenido:
            factor_gravedad = min(factor_gravedad, APEX_GRAVEDAD_FACTOR)

        self.vy = min(MAX_CAIDA, self.vy + GRAVEDAD * factor_gravedad * dt)

        self.mover_x(self.vx * dt, solidos)
        self.en_suelo = False
        self.mover_y(self.vy * dt, solidos)

        if self.en_suelo:
            self.coyote = COYOTE_TIME
            self.dash_usos_aire = DASH_USOS_AIRE
            if abs(self.vx) > 1:
                self.tiempo_animacion += dt
        else:
            self.tiempo_animacion = 0.0

    # --- Función actualizar_dash --- #
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
            # Conservación de momentum y float post-dash estilo Celeste
            self.vx = self.dash_direccion * VELOCIDAD
            self.post_dash_tiempo = POST_DASH_DURACION

    # --- Función actualizar_temporizadores --- #
    def actualizar_temporizadores(self, dt):
        if self.buffer_salto > 0:
            self.buffer_salto = max(0.0, self.buffer_salto - dt)
        if self.en_suelo:
            self.coyote = COYOTE_TIME
        else:
            self.coyote = max(0.0, self.coyote - dt)

    # --- Función actualizar_horizontal --- #
    def actualizar_horizontal(self, teclas):
        teclas_i = getattr(self, "teclas_izq", (pygame.K_a, pygame.K_LEFT))
        teclas_d = getattr(self, "teclas_der", (pygame.K_d, pygame.K_RIGHT))
        izquierda = any(_tecla_activa(teclas, k) for k in teclas_i)
        derecha = any(_tecla_activa(teclas, k) for k in teclas_d)

        if izquierda and not derecha:
            self.vx = -VELOCIDAD
            self.direccion = -1
        elif derecha and not izquierda:
            self.vx = VELOCIDAD
            self.direccion = 1
        else:
            if self.post_dash_tiempo > 0:
                # Conserva impulso horizontal durante la ventana post-dash float
                pass
            else:
                self.vx = 0.0

    # --- Función mover_x --- #
    def mover_x(self, dx, solidos):
        self.x += dx
        self.rect.x = round(self.x)

        colision = False
        for solido in solidos:
            if self.rect.colliderect(solido):
                colision = True
                break

        # Tolerancia de esquinas en dash (corner nudge estilo Celeste):
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

    # --- Función mover_y --- #
    def mover_y(self, dy, solidos):
        self.y += dy
        self.rect.y = round(self.y)

        colision = any(self.rect.colliderect(s) for s in solidos)
        # Jump Corner Correction (Tolerancia de esquinas en techo estilo Celeste):
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
                    self.en_suelo = True
                    self.vy = 0.0
                    break

    # --- Función respawn --- #
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
        self.ataque_tiempo = 0.0
        self.ataque_cooldown = 0.0
        self.ataque_golpeado = False
        self.almas_para_vida = 0
        self.rango_ataque_mejorado = False
        self.escudo_farol = False

    # --- Función dibujar --- #
    def dibujar(self, surface, camara, tiempo, pose=None, con_pala=True):
        if self.invulnerable > 0 and int(tiempo * 16) % 2 == 0:
            return

        rect = camara.aplicar_rect(self.rect)
        centro_x = rect.centerx
        base_y = rect.bottom

        # 1. Dash de Sombras: ghosting espectral con 3 siluetas graduadas (90, 45, 15)
        if self.dash_tiempo > 0:
            for i, alfa in enumerate((90, 45, 15)):
                fx = rect.x - self.dash_direccion * (12 + i * 10)
                ghost_surf = obtener_estampa_fantasma(rect.width, rect.height, alfa, TURQUESA_ÁNIMA)
                surface.blit(ghost_surf, (fx, rect.y))

        # Sombra de contacto en el suelo
        pygame.draw.ellipse(
            surface,
            NEGRO_NOCHE,
            (rect.x + 1, base_y - 5, rect.width - 2, 8),
        )

        en_aire = pose in ("caida", "caida2") or not self.en_suelo
        atacando = pose in ("ataque1", "ataque2", "ataque3")
        moviendo = self.en_suelo and abs(self.vx) > 1 and not atacando

        # 2. Ciclo de caminata (4 Poses): Contacto (squash 0.95x), paso bajo, extensión (stretch 1.05x), paso alto
        despliegue_pierna = 0
        factor_squash = 1.0
        if moviendo:
            fase_paso = int((self.tiempo_animacion * 9.5) % 4)
            if fase_paso == 0:  # Contacto: squash leve
                factor_squash = 0.95
                despliegue_pierna = 6
            elif fase_paso == 1:  # Paso bajo
                factor_squash = 0.98
                despliegue_pierna = 2
            elif fase_paso == 2:  # Extensión: stretch
                factor_squash = 1.05
                despliegue_pierna = -5
            elif fase_paso == 3:  # Paso alto
                factor_squash = 1.02
                despliegue_pierna = -1

        # 3. Pala / Guadaña Mística: al hombro o extendida durante el golpe
        hombro_x = centro_x - self.direccion * 7
        es_guadaña = getattr(self, "rango_ataque_mejorado", False)

        if atacando:
            alcance = (36 if es_guadaña else 16) if pose == "ataque2" else (28 if es_guadaña else 13)
            alto_pala = {
                "ataque1": rect.y - (6 if es_guadaña else -2),
                "ataque2": rect.y + 12,
                "ataque3": base_y + (4 if es_guadaña else -1),
            }[pose]
            punta_x = centro_x + self.direccion * alcance

            color_mango = (45, 30, 48) if es_guadaña else MARRON
            pygame.draw.line(
                surface,
                color_mango,
                (hombro_x, rect.y + 8),
                (punta_x, alto_pala),
                4 if es_guadaña else 3,
            )

            if con_pala:
                if es_guadaña:
                    # Hoja curvada esquelética de Guadaña Mística
                    signo = self.direccion
                    color_hoja = (215, 80, 255)
                    color_filo = (255, 220, 255)
                    puntos_hoja = [
                        (punta_x, alto_pala - 10),
                        (punta_x + signo * 22, alto_pala - 3),
                        (punta_x + signo * 30, alto_pala + 16),
                        (punta_x + signo * 20, alto_pala + 12),
                        (punta_x + signo * 9, alto_pala + 5),
                        (punta_x - signo * 2, alto_pala),
                    ]
                    pygame.draw.polygon(surface, color_hoja, puntos_hoja)
                    pygame.draw.lines(surface, color_filo, False, puntos_hoja[:4], 2)
                    # Arco espectral bioluminiscente de 76px cacheado
                    onda_x = centro_x if signo > 0 else centro_x - 76
                    onda_y = rect.y - 12
                    surface.blit(obtener_arco_guadaña(signo), (onda_x, onda_y))
                else:
                    # Hoja de pala de hierro plateada con filo
                    pygame.draw.polygon(
                        surface,
                        (195, 198, 208),
                        [
                            (punta_x, alto_pala - 5),
                            (punta_x + self.direccion * 8, alto_pala),
                            (punta_x, alto_pala + 6),
                            (punta_x - self.direccion * 2, alto_pala),
                        ],
                    )
                    pygame.draw.polygon(
                        surface,
                        ORO_LITÚRGICO,
                        [
                            (punta_x + self.direccion * 4, alto_pala - 3),
                            (punta_x + self.direccion * 8, alto_pala),
                            (punta_x + self.direccion * 4, alto_pala + 3),
                        ],
                    )
                    # Arco relampagueante en forma de medialuna plateada con filo dorado
                    signo = self.direccion
                    arco_caja = pygame.Rect(
                        centro_x if signo > 0 else centro_x - 36,
                        rect.y + 4,
                        36,
                        24,
                    )
                    ang_ini = -0.4 if signo > 0 else 2.6
                    ang_fin = 2.4 if signo > 0 else 5.4
                    pygame.draw.arc(surface, (230, 235, 245), arco_caja, ang_ini, ang_fin, 2)
                    pygame.draw.arc(surface, ORO_LITÚRGICO, arco_caja.inflate(2, 2), ang_ini, ang_fin, 1)
                    # Chispas en el vértice del golpe
                    pygame.draw.circle(surface, (255, 245, 190), (punta_x + signo * 2, alto_pala), 2)
        elif con_pala:
            if es_guadaña:
                # Guadaña mística reposando en la espalda
                pygame.draw.line(
                    surface,
                    (45, 30, 48),
                    (hombro_x, rect.y + 4),
                    (hombro_x - self.direccion * 8, base_y + 4),
                    3,
                )
                pygame.draw.arc(
                    surface,
                    (215, 80, 255),
                    (hombro_x - 6 if self.direccion > 0 else hombro_x - 14, rect.y - 10, 20, 22),
                    0.0,
                    3.14,
                    3,
                )
            else:
                pygame.draw.line(
                    surface,
                    MARRON,
                    (hombro_x, rect.y + 7),
                    (hombro_x - self.direccion * 4, base_y - 2),
                    3,
                )
                pygame.draw.polygon(
                    surface,
                    GRIS,
                    [
                        (hombro_x - self.direccion * 7, base_y - 4),
                        (hombro_x - self.direccion * 1, base_y - 1),
                        (hombro_x - self.direccion * 4, base_y + 4),
                    ],
                )

        # 4. Piernas y botas animadas
        if en_aire:
            separacion = 7 if pose == "caida" else 9
            for lado, destino in ((-5, -separacion), (5, separacion)):
                pygame.draw.line(
                    surface,
                    MARRON_OSCURO,
                    (centro_x + lado, base_y - 9),
                    (centro_x + destino, base_y - 2),
                    4,
                )
                pygame.draw.line(
                    surface,
                    NEGRO_NOCHE,
                    (centro_x + destino - 2, base_y - 2),
                    (centro_x + destino + 3, base_y - 2),
                    4,
                )
        elif atacando:
            for lado in (-5, 5):
                pygame.draw.line(
                    surface,
                    MARRON_OSCURO,
                    (centro_x + lado, base_y - 9),
                    (centro_x + lado + (2 if lado > 0 else -2), base_y - 1),
                    4,
                )
                pygame.draw.line(
                    surface,
                    NEGRO_NOCHE,
                    (centro_x + lado - 2, base_y - 1),
                    (centro_x + lado + 3, base_y - 1),
                    4,
                )
        else:
            # Poses de caminata coordinadas
            offset_p1 = despliegue_pierna
            offset_p2 = -despliegue_pierna
            for lado, offset in ((-5, offset_p1), (5, offset_p2)):
                pygame.draw.line(
                    surface,
                    MARRON_OSCURO,
                    (centro_x + lado, base_y - int(9 * factor_squash)),
                    (centro_x + lado + offset, base_y - 1),
                    4,
                )
                pygame.draw.line(
                    surface,
                    NEGRO_NOCHE,
                    (centro_x + lado + offset - 2, base_y - 1),
                    (centro_x + lado + offset + 3, base_y - 1),
                    4,
                )

        # 5. Abrigo largo andrajoso con inercia secundaria según vx
        inercia_falda = -self.direccion * min(7, int(abs(self.vx) * 0.024))
        cuerpo_y = rect.y + int(10 * factor_squash)
        cuerpo_h = rect.height - int(16 * factor_squash)
        cuerpo = pygame.Rect(rect.x + 3, cuerpo_y, rect.width - 6, cuerpo_h)

        pygame.draw.rect(surface, AZUL_OSCURO, cuerpo, border_radius=4)
        pygame.draw.rect(surface, MARRON, (cuerpo.x + 4, cuerpo.y + 5, cuerpo.width - 8, cuerpo.height - 5), border_radius=3)
        pygame.draw.rect(surface, NEGRO_NOCHE, cuerpo, 2, border_radius=4)
        pygame.draw.rect(surface, MARRON_OSCURO, (cuerpo.x, cuerpo.y + 7, cuerpo.width, 3))

        # Faldones inferiores andrajosos con arrastre de inercia
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

        # 6. Cabeza, rostro sombreado y sombrero de ala ancha caído
        pygame.draw.circle(surface, (185, 175, 160), (centro_x, rect.y + 10), 8)
        pygame.draw.circle(surface, NEGRO_NOCHE, (centro_x, rect.y + 10), 8, 1)

        # Sombra profunda sobre el rostro bajo el ala del sombrero
        pygame.draw.polygon(
            surface,
            NEGRO_NOCHE,
            [
                (centro_x - 7, rect.y + 7),
                (centro_x + 7, rect.y + 7),
                (centro_x + 5, rect.y + 12),
                (centro_x - 5, rect.y + 12),
            ],
        )

        # Sombrero de ala ancha caído hacia el frente
        ala_caida_y = rect.y + 4
        pygame.draw.ellipse(surface, NEGRO_NOCHE, (rect.x - 2, ala_caida_y, rect.width + 4, 6))
        pygame.draw.rect(surface, (32, 26, 36), (rect.x + 5, rect.y - 1, rect.width - 10, 6), border_radius=2)
        pygame.draw.rect(surface, CARMESÍ_SANGRE, (rect.x + 5, rect.y + 2, rect.width - 10, 2))

        # Dos ojos luminosos azul pálido fulgurando en la penumbra
        ojo_base_x = centro_x + self.direccion * 2
        pygame.draw.circle(surface, (160, 215, 255), (ojo_base_x, rect.y + 10), 1)
        pygame.draw.circle(surface, (160, 215, 255), (ojo_base_x + self.direccion * 3, rect.y + 10), 1)

        # Bufanda fúnebre
        pygame.draw.rect(surface, CARMESÍ_SANGRE, (centro_x - 7, rect.y + 15, 14, 3), border_radius=1)

        # 7. Farol litúrgico diegético aditivo
        farol_x = centro_x + self.direccion * 11
        farol_y = rect.y + 19
        tiene_consagrado = getattr(self, "rango_ataque_mejorado", False)
        color_halo = (205, 80, 255) if tiene_consagrado else FAROL_CÁLIDO
        halo_farol = obtener_estampa_luz(95, color_halo, 42 if tiene_consagrado else 35)
        surface.blit(halo_farol, (farol_x - 95, farol_y - 95), special_flags=pygame.BLEND_RGB_ADD)

        # Montura de bronce del farol colgante
        pygame.draw.circle(surface, (115, 82, 34), (farol_x, farol_y), 6)
        pygame.draw.circle(surface, (165, 120, 50), (farol_x, farol_y), 6, 1)

        # Llama diegética: chispa turquesa brillante si dash_listo(), ámbar tenue si en cooldown o gastado
        dash_disponible = self.tiene_dash and self.dash_listo()
        if dash_disponible:
            color_llama = (70, 235, 220)  # Turquesa brillante
            pygame.draw.circle(surface, color_llama, (farol_x, farol_y), 4)
            pygame.draw.circle(surface, (235, 255, 255), (farol_x, farol_y), 2)  # Chispa brillante
        else:
            color_llama = (175, 115, 45)  # Ámbar tenue
            pygame.draw.circle(surface, color_llama, (farol_x, farol_y), 3)
            pygame.draw.circle(surface, (205, 145, 55), (farol_x, farol_y), 1)  # Centro ámbar tenue
        # Cadena de sujeción
        pygame.draw.line(
            surface,
            GRIS,
            (centro_x + self.direccion * 7, rect.y + 15),
            (farol_x, rect.y + 15),
            1,
        )

        # Manto del Farol (UI Diegética/Espacial: aura celeste sutil de protección)
        if getattr(self, "escudo_farol", False):
            pulso = 0.5 + 0.5 * math.sin(tiempo * 6.0)
            aura = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
            pygame.draw.ellipse(
                aura,
                (92, 190, 220, int(50 + pulso * 35)),
                (0, 0, rect.width + 16, rect.height + 16),
                2,
            )
            surface.blit(aura, (rect.x - 8, rect.y - 8))


# --- Clase Enemigo --- #
class Enemigo:
    """Morador de la cripta que patrulla de izquierda a derecha."""

    def __init__(self, rect, minimo_x, maximo_x):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.vivo = True
        self.minimo_x = int(minimo_x)
        self.maximo_x = int(maximo_x)

    # --- Función reiniciar --- #
    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.vivo = True

    # --- Función actualizar --- #
    def actualizar(self, dt):
        if not self.vivo:
            return

        self.x += self.direccion * VELOCIDAD_ENEMIGO * dt
        self.rect.x = round(self.x)

        if self.rect.left <= self.minimo_x:
            self.rect.left = self.minimo_x
            self.x = float(self.rect.x)
            self.direccion = 1
        elif self.rect.right >= self.maximo_x:
            self.rect.right = self.maximo_x
            self.x = float(self.rect.x)
            self.direccion = -1

    # --- Función dibujar --- #
    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return

        rect = camara.aplicar_rect(self.rect)
        salto = int(math.sin(tiempo * 7 + rect.x * 0.02) * 2)
        centro_x = rect.centerx
        base_y = rect.bottom + salto

        # Sombra en el suelo
        pygame.draw.ellipse(
            surface,
            (7, 6, 10),
            (rect.x + 1, rect.bottom - 4, rect.width - 2, 7),
        )

        # Harapos exteriores (capa de profundidad oscura)
        pygame.draw.ellipse(
            surface,
            (22, 32, 18),
            (rect.x - 2, rect.y + 8 + salto, rect.width + 4, rect.height - 6),
        )
        # Cuerpo encorvado principal
        pygame.draw.ellipse(
            surface,
            VERDE_OSCURO,
            (rect.x, rect.y + 6 + salto, rect.width, rect.height - 6),
        )

        # Harapos laterales (polígonos superpuestos en distintos tonos)
        pygame.draw.polygon(
            surface,
            (38, 30, 20),
            [
                (rect.x + 1, rect.y + 14 + salto),
                (rect.x + 9, rect.y + 22 + salto),
                (rect.x + 5, rect.y + 29 + salto),
                (rect.x - 1, rect.y + 20 + salto),
            ],
        )
        pygame.draw.polygon(
            surface,
            MARRON_OSCURO,
            [
                (rect.x + 3, rect.y + 17 + salto),
                (rect.x + 10, rect.y + 23 + salto),
                (rect.x + 7, rect.y + 28 + salto),
                (rect.x + 1, rect.y + 21 + salto),
            ],
        )
        pygame.draw.polygon(
            surface,
            (38, 30, 20),
            [
                (rect.right - 1, rect.y + 13 + salto),
                (rect.right - 10, rect.y + 22 + salto),
                (rect.right - 4, rect.y + 28 + salto),
                (rect.right + 1, rect.y + 19 + salto),
            ],
        )
        pygame.draw.polygon(
            surface,
            MARRON_OSCURO,
            [
                (rect.right - 3, rect.y + 16 + salto),
                (rect.right - 10, rect.y + 24 + salto),
                (rect.right - 5, rect.y + 27 + salto),
                (rect.right - 1, rect.y + 21 + salto),
            ],
        )

        # Cráneo
        pygame.draw.circle(surface, HUESO, (centro_x, rect.y + 9 + salto), 8)
        pygame.draw.circle(surface, NEGRO, (centro_x, rect.y + 9 + salto), 8, 1)

        # Ojos que "miran" según la dirección del morador
        ojo_offset = self.direccion * 2
        pygame.draw.circle(surface, ROJO, (centro_x - 3 + ojo_offset, rect.y + 8 + salto), 2)
        pygame.draw.circle(surface, ROJO, (centro_x + 3 + ojo_offset, rect.y + 8 + salto), 2)
        # Brillo en los ojos
        pygame.draw.circle(surface, (255, 160, 160), (centro_x - 2 + ojo_offset, rect.y + 7 + salto), 1)
        pygame.draw.circle(surface, (255, 160, 160), (centro_x + 4 + ojo_offset, rect.y + 7 + salto), 1)

        # Mandíbula
        pygame.draw.rect(surface, NEGRO, (centro_x - 3, rect.y + 13 + salto, 6, 2))

        # Costillas visibles entre los harapos
        for i in range(3):
            pygame.draw.line(
                surface,
                MUSGO,
                (rect.x + 8, rect.y + 17 + i * 4 + salto),
                (rect.right - 8, rect.y + 17 + i * 4 + salto),
                1,
            )

        # Garras largas y afiladas (3 dedos por lado)
        for lado, signo in ((4, -1), (rect.width - 5, 1)):
            bx = rect.x + lado
            for dedo_dx in (-2, 0, 2):
                pygame.draw.line(
                    surface, HUESO,
                    (bx + dedo_dx, base_y - 3),
                    (bx + dedo_dx + signo, base_y + 6),
                    1,
                )


# --- Clase EnemigoMelee --- #
class EnemigoMelee:
    """Enemigo que ataca en rango melee (70px). Al jugador le toma y domina."""

    def __init__(self, rect, minimo_x, maximo_x):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.vivo = True
        self.minimo_x = int(minimo_x)
        self.maximo_x = int(maximo_x)
        self.aviso_tiempo = 0.0
        self.atacando = False

    # --- Función reiniciar --- #
    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.vivo = True
        self.aviso_tiempo = 0.0
        self.atacando = False

    # --- Función actualizar --- #
    def actualizar(self, dt, jugador):
        if not self.vivo:
            return

        if self.aviso_tiempo > 0:
            self.aviso_tiempo = max(0.0, self.aviso_tiempo - dt)

        # Mantener en el rango
        self.x += self.direccion * VELOCIDAD_ENEMIGO * dt
        self.rect.x = round(self.x)

        if self.rect.left <= self.minimo_x:
            self.rect.left = self.minimo_x
            self.x = float(self.rect.x)
            self.direccion = 1
        elif self.rect.right >= self.maximo_x:
            self.rect.right = self.maximo_x
            self.x = float(self.rect.x)
            self.direccion = -1

        # Verificar si el jugador está en rango melee y prevenir el paso
        distancia_x = abs(self.rect.centerx - jugador.rect.centerx)
        distancia_y = abs(self.rect.centery - jugador.rect.centery)

        # Rango melee: 70px horizontal, 20px vertical (por debajo del torso del enemigo)
        if distancia_x <= 70 and distancia_y <= 20:
            if self.aviso_tiempo <= 0:
                self.aviso_tiempo = 0.20

    # --- Función dibujar --- #
    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return

        rect = camara.aplicar_rect(self.rect)
        salto = int(math.sin(tiempo * 7 + rect.x * 0.02) * 2)

        # Telegrafía de 200 ms: temblor horizontal sutil (±2 px)
        temblor = 0
        if self.aviso_tiempo > 0:
            temblor = int(math.sin(tiempo * 55) * 2)
            rect.x += temblor

        centro_x = rect.centerx
        base_y = rect.bottom + salto

        # Sombra en el suelo
        pygame.draw.ellipse(
            surface,
            NEGRO_NOCHE,
            (rect.x + 1, rect.bottom - 4, rect.width - 2, 7),
        )

        # Harapos exteriores (capa de profundidad oscura)
        pygame.draw.ellipse(
            surface,
            (22, 32, 18),
            (rect.x - 2, rect.y + 8 + salto, rect.width + 4, rect.height - 6),
        )
        # Cuerpo encorvado principal
        pygame.draw.ellipse(
            surface,
            VERDE_OSCURO,
            (rect.x, rect.y + 6 + salto, rect.width, rect.height - 6),
        )

        # Harapos laterales (polígonos superpuestos en distintos tonos)
        pygame.draw.polygon(
            surface,
            (38, 30, 20),
            [
                (rect.x + 1, rect.y + 14 + salto),
                (rect.x + 9, rect.y + 22 + salto),
                (rect.x + 5, rect.y + 29 + salto),
                (rect.x - 1, rect.y + 20 + salto),
            ],
        )
        pygame.draw.polygon(
            surface,
            MARRON_OSCURO,
            [
                (rect.x + 3, rect.y + 17 + salto),
                (rect.x + 10, rect.y + 23 + salto),
                (rect.x + 7, rect.y + 28 + salto),
                (rect.x + 1, rect.y + 21 + salto),
            ],
        )
        pygame.draw.polygon(
            surface,
            (38, 30, 20),
            [
                (rect.right - 1, rect.y + 13 + salto),
                (rect.right - 10, rect.y + 22 + salto),
                (rect.right - 4, rect.y + 28 + salto),
                (rect.right + 1, rect.y + 19 + salto),
            ],
        )
        pygame.draw.polygon(
            surface,
            MARRON_OSCURO,
            [
                (rect.right - 3, rect.y + 16 + salto),
                (rect.right - 10, rect.y + 24 + salto),
                (rect.right - 5, rect.y + 27 + salto),
                (rect.right - 1, rect.y + 21 + salto),
            ],
        )

        # Cráneo
        pygame.draw.circle(surface, HUESO_MARFIL, (centro_x, rect.y + 9 + salto), 8)
        pygame.draw.circle(surface, NEGRO_NOCHE, (centro_x, rect.y + 9 + salto), 8, 1)

        # Ojos: en telegrafía fulguran en rojo vivo ardiente
        ojo_offset = self.direccion * 2
        ojo_y = rect.y + 8 + salto
        if self.aviso_tiempo > 0:
            # Fulgor ardiente telegrafiado
            pygame.draw.circle(surface, CARMESÍ_SANGRE, (centro_x - 3 + ojo_offset, ojo_y), 3)
            pygame.draw.circle(surface, CARMESÍ_SANGRE, (centro_x + 3 + ojo_offset, ojo_y), 3)
            pygame.draw.circle(surface, (255, 40, 50), (centro_x - 3 + ojo_offset, ojo_y), 2)
            pygame.draw.circle(surface, (255, 40, 50), (centro_x + 3 + ojo_offset, ojo_y), 2)
            pygame.draw.circle(surface, BLANCO, (centro_x - 3 + ojo_offset, ojo_y), 1)
            pygame.draw.circle(surface, BLANCO, (centro_x + 3 + ojo_offset, ojo_y), 1)
        else:
            pygame.draw.circle(surface, ROJO, (centro_x - 3 + ojo_offset, ojo_y), 2)
            pygame.draw.circle(surface, ROJO, (centro_x + 3 + ojo_offset, ojo_y), 2)
            pygame.draw.circle(surface, (255, 160, 160), (centro_x - 2 + ojo_offset, ojo_y - 1), 1)
            pygame.draw.circle(surface, (255, 160, 160), (centro_x + 4 + ojo_offset, ojo_y - 1), 1)

        # Mandíbula
        pygame.draw.rect(surface, NEGRO_NOCHE, (centro_x - 3, rect.y + 13 + salto, 6, 2))

        # Mandoble de hierro gótico del guardia
        signo = self.direccion
        espada_base_x = centro_x + signo * 8
        espada_base_y = rect.y + 14 + salto
        if self.aviso_tiempo > 0:
            # Mandoble alzado en guardia alta telegrafiada
            punta_espada_x = centro_x + signo * 16
            punta_espada_y = rect.y - 6 + salto
            pygame.draw.line(surface, (160, 165, 178), (espada_base_x, espada_base_y), (punta_espada_x, punta_espada_y), 3)
            pygame.draw.line(surface, BLANCO, (espada_base_x, espada_base_y), (punta_espada_x, punta_espada_y), 1)
            # Arco amenazante de telegrafía
            pygame.draw.arc(
                surface,
                CARMESÍ_SANGRE,
                (rect.centerx - 14 + signo * 8, rect.y + 2, 28, 28),
                0,
                3.14,
                2,
            )
        else:
            # Mandoble en reposo hacia abajo
            punta_espada_x = centro_x + signo * 12
            punta_espada_y = base_y - 2
            pygame.draw.line(surface, (140, 145, 155), (espada_base_x, espada_base_y), (punta_espada_x, punta_espada_y), 3)

        # Costillas visibles entre los harapos
        for i in range(3):
            pygame.draw.line(
                surface,
                MUSGO,
                (rect.x + 8, rect.y + 17 + i * 4 + salto),
                (rect.right - 8, rect.y + 17 + i * 4 + salto),
                1,
            )

        # Garras largas y afiladas (3 dedos por lado)
        for lado, sgn in ((4, -1), (rect.width - 5, 1)):
            bx = rect.x + lado
            for dedo_dx in (-2, 0, 2):
                pygame.draw.line(
                    surface, HUESO_MARFIL,
                    (bx + dedo_dx, base_y - 3),
                    (bx + dedo_dx + sgn, base_y + 6),
                    1,
                )


# --- Clase TotemProyectil --- #
class TotemProyectil:
    """Totem que lanza proyectiles a intervalos regulares."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 16, y - 32, 32, 32)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vivo = True
        self.temporizador_proyectil = 0.0
        self.ultimo_proyectil = 0.0
        self.conproyectil = False

    # --- Función reiniciar --- #
    def reiniciar(self):
        self.rect = pygame.Rect(self.x - 16, self.y - 32, 32, 32)
        self.vivo = True
        self.temporizador_proyectil = 0.0
        self.ultimo_proyectil = 0.0
        self.conproyectil = False

    # --- Función actualizar --- #
    def actualizar(self, dt, jugador):
        if not self.vivo:
            return

        self.temporizador_proyectil = max(0.0, self.temporizador_proyectil - dt)
        self.ultimo_proyectil = max(0.0, self.ultimo_proyectil - dt)

        # Lanzar proyectil a intervalos regulares (2 segundos)
        if self.temporizador_proyectil <= 0:
            self.ultimo_proyectil = 0.5
            self.conproyectil = True

        # Si está siendo atacado, crear daño
        if self.conproyectil and jugador.ataque_tiempo > 0:
            if jugador.rect.colliderect(self.rect):
                self.conproyectil = False
                jugador.ataque_golpeado = True
                jugador.dash_usos_aire = DASH_USOS_AIRE
                jugador.dash_cooldown = 0.0

    # --- Función dibujar --- #
    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return

        rect = camara.aplicar_rect(self.rect)

        # Dibujar el totem (basado en los monumentos del juego)
        pygame.draw.polygon(
            surface,
            (72, 54, 38),  # Color Marrón
            [
                (rect.centerx, rect.top),
                (rect.left, rect.bottom),
                (rect.right, rect.bottom),
            ],
        )

        pygame.draw.rect(
            surface,
            (52, 38, 31),  # Color Marrón Oscuro
            (rect.left + 6, rect.top + 12, rect.width - 12, rect.height - 24),
            border_radius=4,
        )

        # Proyectil
        if self.conproyectil:
            pygame.draw.circle(
                surface,
                (190, 104, 48),  # Color Naranja
                (rect.centerx + 8 * (1 if tiempo % 1 < 0.5 else -1), rect.centery - 20),
                4,
            )

        # Advertencia cuando es atacado
        if self.conproyectil and int(tiempo * 2) % 2 == 0:
            pygame.draw.circle(
                surface,
                (255, 0, 0),  # Rojo
                (rect.centerx, rect.centery - 8),
                6,
                2,  # Borde
            )
        for lado in (4, rect.width - 5):
            pygame.draw.line(
                surface,
                HUESO,
                (rect.x + lado, base_y - 3),
                (rect.x + lado - 2, base_y + 4),
                2,
            )


# --- Clase OndaCustodio --- #
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

    # --- Función actualizar --- #
    def actualizar(self, dt):
        self.vida -= dt
        if self.vida <= 0:
            self.viva = False
            return
        self.x += self.direccion * self.velocidad * dt
        self.rect.x = round(self.x)

    # --- Función dibujar --- #
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


# --- Clase Custodio --- #
class Custodio:
    """Jefe final: 2 fases.
    Fase 1 (vida 6->3): pala y pisotón lo dañan en su ventana vulnerable, 2 ondas por golpe.
    Fase 2 (vida 3->0): coraza espectral; pala y pisotón SOLO lo dañan si el jugador
    posee la Guadaña Consagrada ('X'). 4 ondas, ventana vulnerable más corta,
    carga horizontal telegrafiada.
    """

    def __init__(self, rect, minimo_x, maximo_x):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
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
        self.recien_golpeado = False
        self.ondas_recien = False
        self.aviso_recien = False
        self.carga_activa = False
        self.tiempo_muerte = 0.0
        self.tiempo_flash = 0.0

    # --- Función reiniciar --- #
    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vida = JEFE_VIDA
        self.fase = 1
        self.estado = "espera"
        self.temporizador = 1.25
        self.vulnerable = False
        self.vivo = True
        self.direccion = -1
        self.golpes_fase = 0
        self.recien_golpeado = False
        self.ondas_recien = False
        self.aviso_recien = False
        self.carga_activa = False
        self.tiempo_muerte = 0.0
        self.tiempo_flash = 0.0

    # --- Aplicar daño interno --- #
    def _aplicar_dano(self):
        """Descuenta 1 vida, maneja transición a Fase 2 y muerte."""
        self.vida -= 1
        self.golpes_fase += 1
        self.vulnerable = False
        self.recien_golpeado = True
        self.carga_activa = False
        self.tiempo_flash = 0.06

        if self.vida <= 0:
            self.vivo = False
            self.estado = "muerto"
            self.tiempo_muerte = 0.0
            return True

        # Transición: 3 golpes acumulados en la fase → avanza a Fase 2
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

    # --- Función recibir_golpe_pala --- #
    def recibir_golpe_pala(self, rango_mejorado=False):
        """Pala: funciona en Fase 1. En Fase 2 requiere la Guadaña Consagrada (rango_mejorado).
        En ambas fases solo daña dentro de la ventana de vulnerabilidad."""
        if not self.vivo or not self.vulnerable:
            return False
        if self.fase >= 2 and not rango_mejorado:
            return False  # Pala rebota en Fase 2 sin power-up X
        return self._aplicar_dano()

    # --- Función recibir_pisaton --- #
    def recibir_pisaton(self, rango_mejorado=False):
        """Pisotón: funciona en Fase 1. En Fase 2 requiere la Guadaña Consagrada (rango_mejorado).
        En ambas fases solo daña dentro de la ventana de vulnerabilidad."""
        if not self.vivo or not self.vulnerable:
            return False
        if self.fase >= 2 and not rango_mejorado:
            return False  # Pisotón rebota en Fase 2 sin power-up X
        return self._aplicar_dano()

    # --- Función recibir_golpe (compatibilidad tests y golpe cuerpo a cuerpo) --- #
    def recibir_golpe(self, rango_mejorado=False):
        """Alias de recibir_golpe_pala."""
        return self.recibir_golpe_pala(rango_mejorado=rango_mejorado)

    # --- Función actualizar --- #
    def actualizar(self, dt, jugador):
        self.recien_golpeado = False
        self.ondas_recien = False
        self.aviso_recien = False
        if self.tiempo_flash > 0:
            self.tiempo_flash = max(0.0, self.tiempo_flash - dt)

        if not self.vivo:
            self.tiempo_muerte += dt
            return

        if self.estado == "espera":
            if abs(jugador.rect.centerx - self.rect.centerx) > 60:
                self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
                self.x += self.direccion * JEFE_VELOCIDAD * dt
                self.x = max(self.minimo_x, min(self.maximo_x, self.x))
                self.rect.x = round(self.x)
            self.temporizador -= dt
            if self.temporizador <= 0:
                # Fase 2: 40% de chance de carga en vez de pisotón
                import random
                if self.fase >= 2 and random.random() < 0.40:
                    self.estado = "telegrafia_carga"
                    self.temporizador = 0.45
                else:
                    self.estado = "telegrafia"
                    self.temporizador = max(0.38, 0.78 - self.fase * 0.12)
                self.aviso_recien = True

        elif self.estado == "telegrafia":
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "golpe"
                self.temporizador = 0.14
                self.ondas_recien = True

        elif self.estado == "golpe":
            self.temporizador -= dt
            if self.temporizador <= 0:
                self.estado = "recuperacion"
                vuln_dur = JEFE_VULN_FASE2 if self.fase >= 2 else max(0.75, 1.7 - self.fase * 0.25)
                self.temporizador = vuln_dur
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
            # Corre rápido a través de la arena hasta el límite
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
                # Al chocar contra el muro o frenar: aturdido de rodillas (oportunidad de pisar)
                self.carga_activa = False
                self.estado = "recuperacion"
                self.temporizador = JEFE_VULN_FASE2
                self.vulnerable = True
                if choco_muro:
                    self.ondas_recien = True

    # --- Función dibujar --- #
    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return

        rect = camara.aplicar_rect(self.rect)
        centro_x = rect.centerx
        base_y = rect.bottom
        pulso = 0.5 + 0.5 * math.sin(tiempo * 5)

        # Sombra en el suelo
        pygame.draw.ellipse(surface, NEGRO_NOCHE, (rect.x, base_y - 6, rect.width, 10))

        # Fase 2: "La Máscara de la Muerte Roja" - Aura ardiente carmesí con anillos sinusoidales
        if self.fase >= 2:
            aura = obtener_aura_custodio(rect.width + 24, rect.height + 22, CARMESÍ_SANGRE, int(22 + pulso * 24))
            surface.blit(aura, (rect.x - 12, rect.y - 11), special_flags=pygame.BLEND_RGBA_ADD)
            # Anillos sinusoidales concéntricos de fuego rojo
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
            # Aura dorada de oportunidad en Fase 1 (cacheada)
            aura = obtener_aura_custodio(rect.width + 18, rect.height + 16, ORO_LITÚRGICO, 32)
            surface.blit(aura, (rect.x - 9, rect.y - 8), special_flags=pygame.BLEND_RGBA_ADD)

        # Telegrafía de pisotón o carga: resplandor ardiente telegrafiado
        if self.estado in ("telegrafia", "telegrafia_carga"):
            color_brillo = CARMESÍ_SANGRE if self.estado == "telegrafia_carga" else (180, 32, 42)
            brillo = obtener_aura_custodio(rect.width + 48, rect.height + 40, color_brillo, int(65 + pulso * 45))
            surface.blit(brillo, (rect.x - 24, rect.y - 20), special_flags=pygame.BLEND_RGBA_ADD)

        # Capa y joroba episcopal — carmesí fúnebre en Fase 2, litúrgico púrpura oscuro en Fase 1
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
        # Brocado pectoral litúrgico
        pygame.draw.line(surface, ORO_LITÚRGICO if self.fase < 2 else (180, 50, 45), (centro_x - 15, rect.y + 26), (centro_x + 15, rect.y + 26), 2)
        for i in range(4):
            pygame.draw.line(
                surface,
                HUESO_MARFIL if self.fase < 2 else (160, 40, 50),
                (centro_x - 14 + i * 2, rect.y + 31 + i * 4),
                (centro_x + 14 - i * 2, rect.y + 31 + i * 4),
                1,
            )

        # Mitra episcopal (tocado litúrgico en el cráneo colosal)
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
        # Cruz litúrgica en la mitra
        pygame.draw.line(surface, ORO_LITÚRGICO, (centro_x, mitra_y - 14), (centro_x, mitra_y - 2), 1)
        pygame.draw.line(surface, ORO_LITÚRGICO, (centro_x - 3, mitra_y - 9), (centro_x + 3, mitra_y - 9), 1)

        # Cráneo colosal
        pygame.draw.circle(surface, HUESO_MARFIL, (centro_x, rect.y + 16), 12)
        pygame.draw.circle(surface, NEGRO_NOCHE, (centro_x, rect.y + 16), 12, 1)

        # Ojos: fuego rojo carmesí en Fase 2; dorado si vulnerable en Fase 1; rubí ardiente en espera
        if self.fase >= 2:
            color_ojo = (255, 45, 55)
        else:
            color_ojo = (245, 205, 95) if self.vulnerable else CARMESÍ_SANGRE
        pygame.draw.circle(surface, color_ojo, (centro_x - 4, rect.y + 15), 2.5)
        pygame.draw.circle(surface, color_ojo, (centro_x + 4, rect.y + 15), 2.5)
        pygame.draw.circle(surface, BLANCO, (centro_x - 4, rect.y + 15), 1)
        pygame.draw.circle(surface, BLANCO, (centro_x + 4, rect.y + 15), 1)
        pygame.draw.rect(surface, NEGRO_NOCHE, (centro_x - 5, rect.y + 21, 10, 2))

        # Farol incrustado en el pecho del Custodio
        pygame.draw.circle(surface, (115, 78, 28), (centro_x, rect.y + 34), 7)
        pygame.draw.circle(surface, FAROL_CÁLIDO, (centro_x, rect.y + 34), 3)

        # Maza de Osario colosal (mango de fémur reforzado con bandas de hierro y corona espinosa)
        maza_mango_ini = (centro_x + 20, rect.y + 22)
        maza_mango_fin = (centro_x + 30, base_y - 4)
        pygame.draw.line(surface, MARRON_OSCURO, maza_mango_ini, maza_mango_fin, 5)
        pygame.draw.line(surface, HUESO_MARFIL, maza_mango_ini, maza_mango_fin, 2)
        # Cabeza de maza con calavera de osario
        maza_cx = centro_x + 30
        maza_cy = base_y - 8
        pygame.draw.circle(surface, (85, 78, 88), (maza_cx, maza_cy), 8)
        pygame.draw.circle(surface, HUESO_MARFIL, (maza_cx, maza_cy), 6)
        pygame.draw.rect(surface, (55, 48, 58), (maza_cx - 9, maza_cy - 2, 18, 4))
        for espina_ang in (0.0, 1.2, 2.4, 3.6, 4.8):
            ex = maza_cx + math.cos(espina_ang) * 10
            ey = maza_cy + math.sin(espina_ang) * 10
            pygame.draw.line(surface, (160, 155, 170), (maza_cx, maza_cy), (int(ex), int(ey)), 2)

        # Flash de silueta al recibir daño (1 frame BLEND_RGB_ADD 140)
        if self.tiempo_flash > 0:
            flash_overlay = obtener_aura_custodio(rect.width, rect.height, (140, 140, 140), 140)
            surface.blit(flash_overlay, rect.topleft, special_flags=pygame.BLEND_RGB_ADD)


# --- Clase MiniJefe (El Carcelero del Osario) --- #
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

    def _aplicar_dano(self):
        # Patrón justo: solo recibe daño en su ventana de cansancio (1.3 s).
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
        return self._aplicar_dano()

    def recibir_pisaton(self):
        return self._aplicar_dano()

    def recibir_golpe(self):
        return self._aplicar_dano()

    def actualizar(self, dt, jugador):
        self.aviso_recien = False
        if not self.vivo:
            return

        if self.invulnerable > 0:
            self.invulnerable = max(0.0, self.invulnerable - dt)
        if self.tiempo_flash > 0:
            self.tiempo_flash = max(0.0, self.tiempo_flash - dt)

        self.temporizador -= dt

        dist_x = jugador.rect.centerx - self.rect.centerx
        dir_jugador = 1 if dist_x > 0 else -1

        if self.estado == "patrulla":
            self.vulnerable = False
            self.direccion = dir_jugador
            self.vx = self.direccion * MINIJEFE_VELOCIDAD
            self.x += self.vx * dt
            if abs(dist_x) < 170 or self.temporizador <= 0:
                self.estado = "telegrafo"
                self.temporizador = MINIJEFE_TELEGRAFO
                self.vx = 0.0
                self.aviso_recien = True

        elif self.estado == "telegrafo":
            self.vulnerable = False
            self.vx = 0.0
            self.direccion = dir_jugador
            if self.temporizador <= 0:
                self.estado = "ataque"
                self.temporizador = 0.40
                self.vx = self.direccion * 220.0

        elif self.estado == "ataque":
            self.vulnerable = False
            self.x += self.vx * dt
            if self.temporizador <= 0:
                self.estado = "cansado"
                self.temporizador = MINIJEFE_VULNERABLE
                self.vulnerable = True
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

        # Aura de telegrafiado carmesí
        if self.estado == "telegrafo":
            pulso = 0.5 + 0.5 * math.sin(tiempo * 18)
            radio_alerta = int(24 + pulso * 6)
            alerta = pygame.Surface((radio_alerta * 2, radio_alerta * 2), pygame.SRCALPHA)
            pygame.draw.circle(alerta, (180, 20, 36, int(70 + pulso * 60)), (radio_alerta, radio_alerta), radio_alerta, 3)
            surface.blit(alerta, (cx - radio_alerta, rect.centery - radio_alerta), special_flags=pygame.BLEND_RGBA_ADD)

        # Aura de cansancio / vulnerabilidad dorada/ámbar
        if self.vulnerable:
            pulso_v = 0.5 + 0.5 * math.sin(tiempo * 10)
            alerta_v = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
            pygame.draw.ellipse(alerta_v, (240, 200, 70, int(60 + pulso_v * 50)), (0, 0, rect.width + 12, rect.height + 12), 2)
            surface.blit(alerta_v, (rect.x - 6, rect.y - 6))

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


# --- Clase Cuervo --- #
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

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.angulo = 0.0
        self.vivo = True
        self.plumas = []
        self.tiempo_pluma = 0.0

    def actualizar(self, dt):
        if not self.vivo:
            return
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

        # Dibujar plumas desprendidas primero
        for pluma in self.plumas:
            pluma.dibujar(surface, camara)

        rect = camara.aplicar_rect(self.rect)
        centro_x = rect.centerx
        base_y = rect.bottom

        # Sombra sutil en el suelo
        pygame.draw.ellipse(surface, NEGRO_NOCHE, (rect.x + 2, base_y - 4, rect.width - 4, 5))

        # Aleteo articulado de las alas
        aleteo = int(math.sin(tiempo * 16.0) * 5)

        # Cuerpo del cuervo (silueta afilada en negro carbón poeano)
        pygame.draw.ellipse(surface, (14, 12, 18), (rect.x + 4, rect.y + 6, rect.width - 8, rect.height - 10))
        pygame.draw.ellipse(surface, (25, 22, 32), (rect.x + 6, rect.y + 7, rect.width - 12, rect.height - 12))

        # Alas articuladas con 3 primarias escalonadas
        # Ala izquierda
        ala_izq_puntos = [
            (rect.centerx - 2, rect.y + 9),
            (rect.x - 2, rect.y + 2 - aleteo),
            (rect.x + 4, rect.y + 7 - aleteo // 2),
            (rect.centerx - 2, rect.y + 11),
        ]
        pygame.draw.polygon(surface, (10, 8, 14), ala_izq_puntos)
        pygame.draw.line(surface, (38, 32, 45), ala_izq_puntos[1], ala_izq_puntos[2], 1)

        # Ala derecha
        ala_der_puntos = [
            (rect.centerx + 2, rect.y + 9),
            (rect.right + 2, rect.y + 2 - aleteo),
            (rect.right - 4, rect.y + 7 - aleteo // 2),
            (rect.centerx + 2, rect.y + 11),
        ]
        pygame.draw.polygon(surface, (10, 8, 14), ala_der_puntos)
        pygame.draw.line(surface, (38, 32, 45), ala_der_puntos[1], ala_der_puntos[2], 1)

        # Cola afilada en cuña
        pygame.draw.polygon(surface, (10, 8, 14), [
            (centro_x - 3, rect.bottom - 6),
            (centro_x, rect.bottom),
            (centro_x + 3, rect.bottom - 6),
        ])

        # Pico curvado de cuervo en cuerno oscuro
        pygame.draw.polygon(surface, (58, 48, 38), [
            (rect.centerx, rect.y + 13),
            (rect.centerx + 6, rect.y + 16),
            (rect.centerx, rect.y + 18),
        ])

        # Ojos ámbar penetrantes con brillo
        ojo_x = centro_x - 2
        ojo_y = rect.y + 11
        pygame.draw.circle(surface, (235, 180, 40), (ojo_x, ojo_y), 1.5)
        pygame.draw.circle(surface, BLANCO, (ojo_x, ojo_y), 0.5)


# --- Clase Polilla (Moth) --- #
class Polilla:
    """Polilla que vuela en zigzag lento. Daño por contacto."""

    def __init__(self, rect, minimo_x, maximo_x):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.minimo_x = int(minimo_x)
        self.maximo_x = int(maximo_x)
        self.vivo = True
        self.tiempo = 0.0

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.tiempo = 0.0
        self.vivo = True

    def actualizar(self, dt):
        if not self.vivo:
            return
        self.tiempo += dt
        self.x += self.direccion * (VELOCIDAD_ENEMIGO * 0.6) * dt
        self.rect.x = round(self.x)
        if self.rect.left <= self.minimo_x:
            self.rect.left = self.minimo_x
            self.x = float(self.rect.x)
            self.direccion = 1
        elif self.rect.right >= self.maximo_x:
            self.rect.right = self.maximo_x
            self.x = float(self.rect.x)
            self.direccion = -1
        # Movimiento vertical suave (zigzag).
        self.rect.y = round(self.inicial_rect.y + math.sin(self.tiempo * 3) * 8)

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return
        rect = camara.aplicar_rect(self.rect)
        centro_x = rect.centerx
        base_y = rect.bottom

        pygame.draw.ellipse(surface, (7, 6, 10), (rect.x + 2, base_y - 4, rect.width - 4, 5))

        # Cuerpo de polilla (gris pálido).
        pygame.draw.ellipse(surface, VERDE_OSCURO, (rect.x + 4, rect.y + 4, rect.width - 8, rect.height - 8))
        # Alas.
        pygame.draw.ellipse(surface, GRIS_OSCURO, (rect.x, rect.y + 2, rect.width // 2, rect.height // 2))
        pygame.draw.ellipse(surface, GRIS_OSCURO, (rect.x + rect.width // 2, rect.y + 2, rect.width // 2, rect.height // 2))
        # Ojos.
        pygame.draw.circle(surface, NEGRO, (centro_x - 2, rect.y + 8), 1)
        pygame.draw.circle(surface, NEGRO, (centro_x + 2, rect.y + 8), 1)


# --- Clase Araña (Spider) --- #
class Araña:
    """Araña que se mueve por el techo o suelo. Daño por contacto."""

    def __init__(self, rect, minimo_x, maximo_x):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.minimo_x = int(minimo_x)
        self.maximo_x = int(maximo_x)
        self.vivo = True

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.vivo = True

    def actualizar(self, dt):
        if not self.vivo:
            return
        self.x += self.direccion * (VELOCIDAD_ENEMIGO * 0.5) * dt
        self.rect.x = round(self.x)
        if self.rect.left <= self.minimo_x:
            self.rect.left = self.minimo_x
            self.x = float(self.rect.x)
            self.direccion = 1
        elif self.rect.right >= self.maximo_x:
            self.rect.right = self.maximo_x
            self.x = float(self.rect.x)
            self.direccion = -1

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return
        rect = camara.aplicar_rect(self.rect)
        centro_x = rect.centerx
        base_y = rect.bottom

        pygame.draw.ellipse(surface, (7, 6, 10), (rect.x + 2, base_y - 4, rect.width - 4, 5))

        # Cuerpo de araña (negro).
        pygame.draw.ellipse(surface, NEGRO, (rect.x + 4, rect.y + 6, rect.width - 8, rect.height - 10))
        # Patas.
        for i in range(3):
            dx = (i - 1) * 5
            pygame.draw.line(surface, NEGRO, (centro_x + dx, rect.y + 10), (rect.x + dx - 6, rect.y + 16), 2)
            pygame.draw.line(surface, NEGRO, (centro_x + dx, rect.y + 10), (rect.right - dx + 6, rect.y + 16), 2)
        # Ojos rojos.
        pygame.draw.circle(surface, ROJO, (centro_x - 2, rect.y + 9), 1)
        pygame.draw.circle(surface, ROJO, (centro_x + 2, rect.y + 9), 1)


# --- Clase Alma --- #
class Alma:
    """Alma flotante que se puede recoger una sola vez."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.recogida = False

    # --- Función reiniciar --- #
    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.recogida = False

    # --- Función actualizar --- #
    def actualizar(self, jugador):
        if not self.recogida and self.rect.colliderect(jugador.rect):
            self.recogida = True
            jugador.almas += 1
            return True
        return False

    # --- Función dibujar --- #
    def dibujar(self, surface, camara, tiempo):
        if self.recogida:
            return

        rect = camara.aplicar_rect(self.rect)
        flotacion = int(math.sin(tiempo * 5 + rect.x * 0.03) * 3)
        centro = (rect.centerx, rect.centery + flotacion)

        pygame.draw.circle(surface, (54, 38, 76), (centro[0], centro[1] + 1), 11)
        pygame.draw.circle(surface, VIOLETA, centro, 8)
        pygame.draw.circle(surface, BLANCO, centro, 4)
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


# --- Clase PalaRecogible --- #
class PalaRecogible:
    """Pala que desbloquea el ataque y el pisotón."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.recogida = False

    # --- Función reiniciar --- #
    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.recogida = False

    # --- Función actualizar --- #
    def actualizar(self, jugador):
        if not self.recogida and self.rect.colliderect(jugador.rect):
            self.recogida = True
            jugador.tiene_pala = True
            return True
        return False

    # --- Función dibujar --- #
    def dibujar(self, surface, camara, tiempo):
        if self.recogida:
            return

        rect = camara.aplicar_rect(self.rect)
        flotacion = int(math.sin(tiempo * 4 + rect.x * 0.02) * 3)
        rect.y += flotacion

        pulso = 0.5 + 0.5 * math.sin(tiempo * 5 + rect.x * 0.03)
        brillo = pygame.Surface((64, 64), pygame.SRCALPHA)
        for radio, alfa in ((27, 24), (20, 42), (13, 72)):
            pygame.draw.circle(
                brillo,
                (255, 191, 82, int(alfa * (0.75 + pulso * 0.25))),
                (32, 32),
                radio,
            )
        surface.blit(
            brillo,
            (rect.centerx - 32, rect.centery - 32),
            special_flags=pygame.BLEND_RGBA_ADD,
        )
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


# --- Clase RangoPowerUp --- #
class RangoPowerUp:
    """Power-up que mejora el alcance del ataque de pala (Guadaña Consagrada, 'X').

    Mientras `sellado` sea True (el Carcelero del Osario sigue vivo) el altar
    no puede recogerse: el Mini-Boss despeja el camino al morir.
    """

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.recogida = False
        self.sellado = False

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.recogida = False

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
            # Altar sellado: guadaña apagada tras cadenas cruzadas.
            cx, cy = rect.centerx, rect.centery
            pygame.draw.circle(surface, (60, 40, 70), (cx, cy), 14, 1)
            pygame.draw.line(surface, (110, 70, 130), (cx - 6, cy - 6), (cx + 6, cy + 6), 2)
            pygame.draw.line(surface, (110, 70, 130), (cx + 6, cy + 6), (cx + 10, cy + 2), 2)
            pygame.draw.line(surface, (110, 70, 130), (cx - 6, cy - 6), (cx - 2, cy - 10), 2)
            pygame.draw.line(surface, (130, 125, 140), (cx - 12, cy - 12), (cx + 12, cy + 12), 2)
            pygame.draw.line(surface, (130, 125, 140), (cx + 12, cy - 12), (cx - 12, cy + 12), 2)
            return

        flotacion = int(math.sin(tiempo * 4 + rect.x * 0.02) * 3)
        rect.y += flotacion

        pulso = 0.5 + 0.5 * math.sin(tiempo * 5 + rect.x * 0.03)
        brillo = pygame.Surface((64, 64), pygame.SRCALPHA)
        for radio, alfa in ((27, 24), (20, 42), (13, 72)):
            pygame.draw.circle(
                brillo,
                (200, 100, 255, int(alfa * (0.75 + pulso * 0.25))),
                (32, 32),
                radio,
            )
        surface.blit(
            brillo,
            (rect.centerx - 32, rect.centery - 32),
            special_flags=pygame.BLEND_RGBA_ADD,
        )
        pygame.draw.circle(
            surface,
            (230, 150, 255),
            (rect.centerx, rect.centery),
            14 + int(pulso * 2),
            1,
        )
        # Dibujo de guadaña estilizada.
        cx, cy = rect.centerx, rect.centery
        pygame.draw.line(surface, (200, 100, 255), (cx - 6, cy - 6), (cx + 6, cy + 6), 2)
        pygame.draw.line(surface, (200, 100, 255), (cx + 6, cy + 6), (cx + 10, cy + 2), 2)
        pygame.draw.line(surface, (200, 100, 255), (cx - 6, cy - 6), (cx - 2, cy - 10), 2)


# --- Clase DashPowerUp --- #
class DashPowerUp:
    """Power-up que desbloquea el dash espectral (Amuleto de Sombras)."""

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
            jugador.tiene_dash = True
            return True
        return False

    def dibujar(self, surface, camara, tiempo):
        if self.recogida:
            return

        rect = camara.aplicar_rect(self.rect)
        flotacion = int(math.sin(tiempo * 4 + rect.x * 0.02) * 3)
        rect.y += flotacion

        pulso = 0.5 + 0.5 * math.sin(tiempo * 5 + rect.x * 0.03)
        brillo = pygame.Surface((64, 64), pygame.SRCALPHA)
        # Resplandor espectral cian/turquesa
        for radio, alfa in ((27, 24), (20, 42), (13, 72)):
            pygame.draw.circle(
                brillo,
                (70, 210, 255, int(alfa * (0.75 + pulso * 0.25))),
                (32, 32),
                radio,
            )
        surface.blit(
            brillo,
            (rect.centerx - 32, rect.centery - 32),
            special_flags=pygame.BLEND_RGBA_ADD,
        )
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


# --- Clase FarolCheckpoint --- #
class FarolCheckpoint:
    """Farol de reposo litúrgico que funciona como punto de control diegético."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.activo = False

    def reiniciar(self):
        self.activo = False

    def actualizar(self, jugador):
        if not self.activo and self.rect.colliderect(jugador.rect):
            self.activo = True
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
        # Jaula del farol
        pygame.draw.rect(surface, (65, 60, 75), (cx - 7, base_y - 32, 14, 10), 1)
        # Techo piramidal
        pygame.draw.polygon(surface, (80, 75, 92), [(cx - 8, base_y - 32), (cx + 8, base_y - 32), (cx, base_y - 38)])

        flame_y = base_y - 27
        if self.activo:
            pulso = 0.5 + 0.5 * math.sin(tiempo * 8 + cx * 0.05)
            radio_llama = int(3 + pulso * 2)
            pygame.draw.circle(surface, (120, 220, 255), (cx, flame_y), radio_llama)
            pygame.draw.circle(surface, (240, 255, 255), (cx, flame_y), max(1, radio_llama - 2))

            # Resplandor místico
            brillo = pygame.Surface((48, 48), pygame.SRCALPHA)
            pygame.draw.circle(brillo, (60, 180, 255, int(35 + pulso * 20)), (24, 24), 22)
            pygame.draw.circle(brillo, (140, 220, 255, int(60 + pulso * 30)), (24, 24), 12)
            surface.blit(brillo, (cx - 24, flame_y - 24), special_flags=pygame.BLEND_RGBA_ADD)
        else:
            # Vela apagada
            pygame.draw.rect(surface, (120, 110, 100), (cx - 1, flame_y, 2, 4))


