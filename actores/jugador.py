#---- Importamos librerias y configuracion ----#
import pygame

from actores.render_jugador import RenderJugadorMixin
from actores.utilidades import _tecla_activa
from config import (
    APEX_GRAVEDAD_FACTOR,
    APEX_VY_UMBRAL,
    ATAQUE_ALCANCE,
    ATAQUE_ALCANCE_MEJORADO,
    ATAQUE_ALTO,
    ATAQUE_COOLDOWN,
    ATAQUE_DURACION,
    CORNER_NUDGE_TECHO,
    CORTE_SALTO,
    COYOTE_TIME,
    DASH_COOLDOWN,
    DASH_DURACION,
    DASH_JUMP_IMPULSO_X,
    DASH_USOS_AIRE,
    DASH_VELOCIDAD,
    FILO_ANIMA_ALCANCE,
    FILO_ANIMA_DASH_FACTOR,
    GRAVEDAD,
    INVULNERABILIDAD,
    JUGADOR_ALTO,
    JUGADOR_ANCHO,
    JUMP_BUFFER,
    MAX_CAIDA,
    POST_DASH_DURACION,
    POST_DASH_GRAVEDAD_FACTOR,
    SALTO,
    VELOCIDAD,
    VIDAS_INICIALES,
)


#---- Clase Jugador ----#
class Jugador(RenderJugadorMixin):
    """El sepulturero: salta, hace dash y clava la pala desde el aire."""

    def __init__(self, x, y, vidas=VIDAS_INICIALES, tiene_dash=False):
        self.rect = pygame.Rect(int(x), int(y), JUGADOR_ANCHO, JUGADOR_ALTO)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.teclas_izq = (pygame.K_a, pygame.K_LEFT)
        self.teclas_der = (pygame.K_d, pygame.K_RIGHT)
        self.direccion = 1
        self.dash_direccion = 1
        self.tiempo_animacion = 0.0
        self.vidas = vidas
        self.almas = 0
        self.tiene_pala = False
        self.tiene_dash = tiene_dash
        self._iniciar_estado_movimiento()
        self.invulnerable = 0.0

    def _iniciar_estado_movimiento(self):
        # Inicializamos velocidades y banderas temporales de movimiento y combate
        self.vx = 0.0
        self.vy = 0.0
        self.en_suelo = False
        self.coyote = 0.0
        self.buffer_salto = 0.0
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

    def pedir_salto(self):
        """Se llama en KEYDOWN: deja preparado el salto."""
        self.buffer_salto = JUMP_BUFFER
        self.manteniendo_salto = True

    def soltar_salto(self):
        """Se llama en KEYUP: corta el salto si todavia sube."""
        self.manteniendo_salto = False
        if self.vy < 0:
            self.vy *= CORTE_SALTO

    def pedir_dash(self):
        """Inicia un dash si esta desbloqueado, sin cooldown y con carga disponible."""
        if not self.tiene_dash or self.dash_tiempo > 0 or self.dash_cooldown > 0:
            return False
        if not self.en_suelo and self.dash_usos_aire <= 0:
            return False

        self.dash_tiempo = DASH_DURACION
        factor_cd = FILO_ANIMA_DASH_FACTOR if getattr(self, "filo_anima", False) else 1.0
        self.dash_cooldown = DASH_COOLDOWN * factor_cd
        self.dash_direccion = self.direccion

        if not self.en_suelo:
            self.dash_usos_aire -= 1

        self.vx = self.direccion * DASH_VELOCIDAD
        self.vy = 0.0
        self.dash_recien = True
        self._dash_pendiente_feedback = True
        return True

    def dash_listo(self):
        """Indica si el jugador puede ejecutar un dash en este instante."""
        return (
            self.tiene_dash
            and self.dash_tiempo <= 0
            and self.dash_cooldown <= 0
            and (self.en_suelo or self.dash_usos_aire > 0)
        )

    def pedir_ataque(self):
        """Inicia un golpe de pala si el arma esta desbloqueada."""
        if not self.tiene_pala or self.ataque_cooldown > 0 or self.ataque_tiempo > 0:
            return False
        self.ataque_tiempo = ATAQUE_DURACION
        self.ataque_cooldown = ATAQUE_COOLDOWN
        self.ataque_golpeado = False
        return True

    def rect_ataque(self):
        """Calcula el rectangulo de colision frontal del ataque activo."""
        es_guadaña = self.rango_ataque_mejorado
        alcance = ATAQUE_ALCANCE_MEJORADO if es_guadaña else ATAQUE_ALCANCE
        if getattr(self, "filo_anima", False):
            alcance += FILO_ANIMA_ALCANCE
        alto = (ATAQUE_ALTO + 16) if es_guadaña else ATAQUE_ALTO
        x = (self.rect.right - 4) if self.direccion > 0 else (self.rect.left - alcance + 4)
        return pygame.Rect(x, self.rect.centery - alto // 2, alcance, alto)

    def pose_actual(self):
        """Devuelve la clave de pose visual segun ataque y contacto con el suelo."""
        if self.ataque_tiempo > 0:
            if self.ataque_tiempo > ATAQUE_DURACION * 0.62:
                return "ataque1"
            if self.ataque_tiempo > ATAQUE_DURACION * 0.30:
                return "ataque2"
            return "ataque3"
        if not self.en_suelo:
            return "caida"
        return None

    def _actualizar_timers_frame(self, dt):
        # Actualiza banderas de un cuadro y descuenta todos los temporizadores
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

        for campo in (
            "invulnerable",
            "dash_cooldown",
            "ataque_cooldown",
            "ataque_tiempo",
            "post_dash_tiempo",
            "retroceso_tiempo",
        ):
            val = getattr(self, campo)
            if val > 0:
                setattr(self, campo, max(0.0, val - dt))

        self.actualizar_temporizadores(dt)

    def _iniciar_salto_normal(self):
        # Ejecuta salto con coyote o buffer activo
        self.vy = SALTO
        self.en_suelo = False
        self.coyote = 0.0
        self.buffer_salto = 0.0
        self.salto_recien = True
        self.squash_timer = 0.10
        self.squash_tipo = "salto"

    def _calcular_factor_gravedad(self, teclas):
        # Reduce la gravedad cerca de la cima del salto o justo tras terminar un dash
        factor = 1.0
        if self.post_dash_tiempo > 0:
            factor = min(factor, POST_DASH_GRAVEDAD_FACTOR)

        salto_mantenido = (
            self.manteniendo_salto
            or _tecla_activa(teclas, pygame.K_SPACE)
            or _tecla_activa(teclas, pygame.K_UP)
            or _tecla_activa(teclas, pygame.K_w)
        )
        if not self.en_suelo and abs(self.vy) < APEX_VY_UMBRAL and salto_mantenido:
            factor = min(factor, APEX_GRAVEDAD_FACTOR)
        return factor

    def actualizar(self, dt, teclas, solidos):
        """Actualiza fisica, dash, salto variable y colisiones en un frame."""
        self._actualizar_timers_frame(dt)

        if self.dash_tiempo > 0:
            if self.buffer_salto > 0 and (self.en_suelo or self.coyote > 0):
                self.dash_tiempo = 0.0
                self.post_dash_tiempo = POST_DASH_DURACION
                self._iniciar_salto_normal()
                self.vx = self.dash_direccion * VELOCIDAD * DASH_JUMP_IMPULSO_X
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
            self._iniciar_salto_normal()

        factor_gravedad = self._calcular_factor_gravedad(teclas)
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
        """Ejecuta un paso de desplazamiento rapido y conserva momento al salir."""
        self.dash_tiempo = max(0.0, self.dash_tiempo - dt)
        self.vx = self.dash_direccion * DASH_VELOCIDAD
        self.vy = 0.0

        self.mover_x(self.vx * dt, solidos)
        if self.vx == 0:
            self.dash_tiempo = 0.0

        if self.en_suelo:
            self.dash_usos_aire = DASH_USOS_AIRE
        if self.dash_tiempo == 0:
            self.vx = self.dash_direccion * VELOCIDAD
            self.post_dash_tiempo = POST_DASH_DURACION

    def actualizar_temporizadores(self, dt):
        """Descuenta jump buffer y coyote time segun contacto con el piso."""
        if self.buffer_salto > 0:
            self.buffer_salto = max(0.0, self.buffer_salto - dt)
        if self.en_suelo:
            self.coyote = COYOTE_TIME
        else:
            self.coyote = max(0.0, self.coyote - dt)

    def actualizar_horizontal(self, teclas):
        """Calcula velocidad horizontal segun teclas activas y retroceso."""
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
        elif self.post_dash_tiempo <= 0 and getattr(self, "retroceso_tiempo", 0.0) <= 0:
            self.vx = 0.0

    def _corregir_esquina_dash(self, solidos):
        # Desliza suavemente hasta 6 px si el dash roza el borde de una plataforma
        tolerancia = 6
        for signo in (1, -1):
            for dy in range(1, tolerancia + 1):
                shift = signo * dy
                test_rect = self.rect.move(0, shift)
                if not any(test_rect.colliderect(s) for s in solidos):
                    self.y += shift
                    self.rect.y = round(self.y)
                    return True
        return False

    def mover_x(self, dx, solidos):
        """Desplaza horizontalmente con tolerancia de esquina en dash y freno contra muro."""
        self.x += dx
        self.rect.x = round(self.x)

        colision = any(self.rect.colliderect(s) for s in solidos)
        if colision and self.dash_tiempo > 0 and self._corregir_esquina_dash(solidos):
            colision = False

        if not colision:
            return
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

    def _corregir_esquina_techo(self, solidos):
        # Desliza horizontalmente hasta 5 px cuando la cabeza roza un bloque superior
        direcciones_dx = [1, -1] if self.direccion >= 0 else [-1, 1]
        for sign in direcciones_dx:
            for d in range(1, CORNER_NUDGE_TECHO + 1):
                shift = sign * d
                test_rect = self.rect.move(shift, 0)
                if not any(test_rect.colliderect(s) for s in solidos):
                    self.x += shift
                    self.rect.x = round(self.x)
                    return True
        return False

    def _acoplar_suelo_bajo(self, solidos):
        # Detecta contacto a 1 px de distancia para mantener firmeza en suelo
        sonda = self.rect.move(0, 1)
        for solido in solidos:
            if sonda.colliderect(solido):
                self.rect.bottom = solido.top
                self.y = float(self.rect.y)
                self.en_suelo = True
                self.vy = 0.0
                return

    def mover_y(self, dy, solidos):
        """Desplaza verticalmente resolviendo techo, aterrizaje y esquinas."""
        self.y += dy
        self.rect.y = round(self.y)

        colision = any(self.rect.colliderect(s) for s in solidos)
        if colision and dy < 0 and self._corregir_esquina_techo(solidos):
            colision = False

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
            self._acoplar_suelo_bajo(solidos)

    def respawn(self, x, y):
        """Reubica al sepulturero en un punto de control limpiando efectos temporales."""
        self.rect.topleft = (int(x), int(y))
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self._iniciar_estado_movimiento()
        self.invulnerable = INVULNERABILIDAD
