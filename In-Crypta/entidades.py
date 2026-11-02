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
    ATAQUE_ALCANCE,
    ATAQUE_ALCANCE_MEJORADO,
    ATAQUE_ALTO,
    ATAQUE_COOLDOWN,
    ATAQUE_DURACION,
    AZUL_OSCURO,
    BLANCO,
    COYOTE_TIME,
    CORTE_SALTO,
    CREMA,
    DASH_COOLDOWN,
    DASH_DURACION,
    DASH_USOS_AIRE,
    DASH_VELOCIDAD,
    ENEMIGO_ALTO,
    ENEMIGO_ANCHO,
    GRAVEDAD,
    GRIS,
    GRIS_OSCURO,
    HUESO,
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
    MUSGO,
    NARANJA,
    NEGRO,
    ORO,
    ROJO,
    SALTO,
    SANGRE,
    TURQUESA,
    VELOCIDAD,
    VELOCIDAD_ENEMIGO,
    VERDE_OSCURO,
    VIDAS_INICIALES,
    VIOLETA,
)


# --- Función auxiliar: recortar un valor entre mínimo y máximo --- #
def limitar(valor, minimo, maximo):
    return max(minimo, min(valor, maximo))


# --- Clase Jugador --- #
class Jugador:
    """El sepulturero: salta, hace dash y clava la pala desde el aire."""

    def __init__(self, x, y, vidas=VIDAS_INICIALES):
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

        self.salto_recien = False
        self.dash_recien = False

        self.ataque_tiempo = 0.0
        self.ataque_cooldown = 0.0
        self.ataque_golpeado = False

        self.vidas = vidas
        self.almas = 0
        self.almas_para_vida = 0
        self.tiene_pala = False
        self.rango_ataque_mejorado = False

        # Rigging cinemático y Squash & Stretch elástico
        self.aterrizaje_timer = 0.0
        self.vy_impacto = 0.0
        self.escala_x = 1.0
        self.escala_y = 1.0

    # --- Función pedir_salto --- #
    def pedir_salto(self):
        """Se llama en KEYDOWN: deja preparado el salto."""
        self.buffer_salto = JUMP_BUFFER

    # --- Función soltar_salto --- #
    def soltar_salto(self):
        """Se llama en KEYUP: corta el salto si todavía sube."""
        if self.vy < 0:
            self.vy *= CORTE_SALTO

    # --- Función pedir_dash --- #
    def pedir_dash(self):
        """Inicia un dash si hay carga y, en el aire, queda un uso."""
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
            self.dash_tiempo <= 0
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

        if self.dash_tiempo > 0:
            self.actualizar_dash(dt, solidos)
            return

        self.actualizar_horizontal(teclas)
        self.actualizar_temporizadores(dt)

        if self.buffer_salto > 0 and (self.en_suelo or self.coyote > 0):
            self.vy = SALTO
            self.en_suelo = False
            self.coyote = 0.0
            self.buffer_salto = 0.0
            self.salto_recien = True

        era_en_suelo = self.en_suelo
        vy_anterior = self.vy
        self.vy = min(MAX_CAIDA, self.vy + GRAVEDAD * dt)

        self.mover_x(self.vx * dt, solidos)
        self.en_suelo = False
        self.mover_y(self.vy * dt, solidos)

        if self.en_suelo:
            if not era_en_suelo and vy_anterior > 60:
                self.aterrizaje_timer = 0.20
                self.vy_impacto = vy_anterior
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
            self.vx = self.dash_direccion * VELOCIDAD * 0.55

    # --- Función actualizar_horizontal --- #
    def actualizar_horizontal(self, teclas):
        izquierda = teclas[pygame.K_LEFT]
        derecha = teclas[pygame.K_d] or teclas[pygame.K_RIGHT]

        if izquierda and not derecha:
            self.vx = -VELOCIDAD
            self.direccion = -1
        elif derecha and not izquierda:
            self.vx = VELOCIDAD
            self.direccion = 1
        else:
            self.vx = 0.0

    # --- Función actualizar_temporizadores --- #
    def actualizar_temporizadores(self, dt):
        if self.buffer_salto > 0:
            self.buffer_salto = max(0.0, self.buffer_salto - dt)
        if self.en_suelo:
            self.coyote = COYOTE_TIME
        else:
            self.coyote = max(0.0, self.coyote - dt)
        if self.aterrizaje_timer > 0:
            self.aterrizaje_timer = max(0.0, self.aterrizaje_timer - dt)

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
        self.salto_recien = False
        self.dash_recien = False
        self.ataque_tiempo = 0.0
        self.ataque_cooldown = 0.0
        self.ataque_golpeado = False
        self.almas_para_vida = 0
        self.rango_ataque_mejorado = False
        self.aterrizaje_timer = 0.0
        self.vy_impacto = 0.0
        self.escala_x = 1.0
        self.escala_y = 1.0

    # --- Función dibujar --- #
    def dibujar(self, surface, camara, tiempo, pose=None, con_pala=True):
        if self.invulnerable > 0 and int(tiempo * 16) % 2 == 0:
            return

        rect = camara.aplicar_rect(self.rect)
        centro_x = rect.centerx
        base_y = rect.bottom

        # Estela fantasma espectral durante dash
        if self.dash_tiempo > 0:
            for i, color in enumerate(((38, 30, 55), (64, 50, 92), (92, 74, 128))):
                fantasma = rect.move(-self.dash_direccion * (10 + i * 9), 0)
                pygame.draw.rect(surface, color, fantasma, border_radius=7)

        # --- Squash & Stretch con preservación estricta de volumen (escala_X * escala_Y = 1.0) --- #
        escala_y = 1.0
        if self.aterrizaje_timer > 0:
            # Impacto elástico al aterrizar (squash) con oscilación armónica amortiguada
            progreso = 1.0 - (self.aterrizaje_timer / 0.20)
            fuerza = min(0.30, max(0.12, getattr(self, "vy_impacto", 300.0) / 1400.0))
            amortiguacion = 1.0 - progreso
            oscilacion = math.sin(progreso * math.pi * 2.2)
            squash = fuerza * oscilacion * amortiguacion
            escala_y = 1.0 - squash
        elif not self.en_suelo:
            # Estiramiento en aire según impulso vertical (stretch)
            if self.vy < 0:
                escala_y = 1.0 + min(0.24, -self.vy / 2200.0)
            else:
                escala_y = 1.0 + min(0.20, self.vy / 2600.0)
        elif self.salto_recien:
            escala_y = 1.22

        # Límites seguros de deformación
        escala_y = max(0.65, min(1.38, escala_y))
        # Preservación estricta del volumen: escala_x * escala_y == 1.0
        escala_x = 1.0 / escala_y
        self.escala_x = escala_x
        self.escala_y = escala_y

        # Transformación afín procedural anclada en la base del personaje (centro_x, base_y)
        def trans(px, py):
            return (
                round(centro_x + (px - centro_x) * escala_x),
                round(base_y + (py - base_y) * escala_y),
            )

        def trans_r(rx, ry):
            return (max(1, round(rx * escala_x)), max(1, round(ry * escala_y)))

        # Sombra en el suelo con volumen elástico preservado
        sombra_w = max(4, round((rect.width - 2) * escala_x))
        sombra_h = max(2, round(8.0 / escala_x))
        pygame.draw.ellipse(
            surface,
            (7, 6, 10),
            (centro_x - sombra_w // 2, base_y - sombra_h // 2 - 1, sombra_w, sombra_h),
        )

        en_aire = pose in ("caida", "caida2") or (not self.en_suelo)
        atacando = pose in ("ataque1", "ataque2", "ataque3")

        # --- Balanceo vertical de cadera y torso & inclinación cinética --- #
        cadera_bob = 0.0
        lean_x = 0.0
        fase_locomocion = 0.0
        if pose is None and self.en_suelo and abs(self.vx) > 1:
            fase_locomocion = self.tiempo_animacion * 14.0
            # Dos oscilaciones por ciclo de paso (transferencia de peso entre piernas)
            cadera_bob = -abs(math.sin(fase_locomocion)) * 2.4
            lean_x = self.direccion * 1.5
        elif self.en_suelo:
            # Respiración sutil en estado de reposo
            cadera_bob = math.sin(tiempo * 3.2) * 0.8
        elif en_aire:
            lean_x = self.direccion * 1.0

        # --- Arrastre inercial elástico de la capa del sepulturero --- #
        arrastre_vx = -self.direccion * min(8.5, abs(self.vx) / 16.0)
        if self.dash_tiempo > 0:
            arrastre_vx = -self.dash_direccion * 16.0

        updraft = 0.0
        if not self.en_suelo:
            updraft = -min(5.5, max(0.0, self.vy / 80.0))

        ondulacion_1 = math.sin(tiempo * 16.0 + 1.2) * (2.4 if abs(self.vx) > 1 else 0.8)
        ondulacion_2 = math.cos(tiempo * 14.0) * (1.8 if abs(self.vx) > 1 else 0.6)

        # Hombros anclados
        hombro_izq = trans(centro_x - 7 + lean_x, rect.y + 11 + cadera_bob)
        hombro_der = trans(centro_x + 7 + lean_x, rect.y + 11 + cadera_bob)

        # Vértices de la capa ondeante
        cola_1 = trans(centro_x - self.direccion * 9 + arrastre_vx, base_y - 3 + updraft + ondulacion_1)
        cola_2 = trans(centro_x - self.direccion * 4 + arrastre_vx * 0.7, base_y - 1 + updraft + ondulacion_2)
        cola_3 = trans(centro_x + arrastre_vx * 0.3, base_y - 3 + updraft)
        cola_4 = trans(centro_x + self.direccion * 5, base_y - 2)

        # Polígono base de la capa (carbón oscuro de sepulturero)
        puntos_capa = [
            hombro_izq if self.direccion > 0 else hombro_der,
            hombro_der if self.direccion > 0 else hombro_izq,
            cola_4,
            cola_3,
            cola_2,
            cola_1,
        ]
        pygame.draw.polygon(surface, (18, 16, 26), puntos_capa)
        # Pliegue interior de terciopelo vino oscuro
        pygame.draw.polygon(surface, (38, 22, 34), [cola_1, cola_2, cola_3, trans(centro_x + lean_x, rect.y + 18 + cadera_bob)])
        pygame.draw.lines(surface, (28, 24, 38), False, [cola_1, cola_2, cola_3], 1)

        # --- Ciclo de caminado/carrera trigonométrico articulado en piernas/botas --- #
        def dibujar_pierna(lado, fase, es_frontal):
            hip_x = centro_x + lado + lean_x * 0.4
            hip_y = base_y - 11 + cadera_bob

            if en_aire:
                separacion = 6 if pose == "caida" else 8
                destino_x = hip_x + (separacion if lado > 0 else -separacion)
                knee_x = (hip_x + destino_x) * 0.5 + self.direccion * 1.5
                knee_y = (hip_y + base_y - 2) * 0.5
                foot_x = destino_x
                foot_y = base_y - (2 if lado > 0 else 4)
            elif atacando:
                avance = self.direccion * (5 if es_frontal else -4)
                knee_x = hip_x + avance * 0.6
                knee_y = (hip_y + base_y - 1) * 0.5 + 1.0
                foot_x = hip_x + avance
                foot_y = base_y - 1
            elif self.en_suelo and abs(self.vx) > 1:
                # Cinemática trigonométrica de zancada
                alcance = math.sin(fase) * 5.5 * self.direccion
                levantamiento = max(0.0, -math.cos(fase)) * 4.2
                foot_x = hip_x + alcance
                foot_y = base_y - 1 - levantamiento
                flexion = self.direccion * (2.0 + levantamiento * 0.4)
                knee_x = (hip_x + foot_x) * 0.5 + flexion
                knee_y = (hip_y + foot_y) * 0.5 - 0.5
            else:
                # Reposo
                foot_x = hip_x + (1 if lado > 0 else -1)
                foot_y = base_y - 1
                knee_x = (hip_x + foot_x) * 0.5
                knee_y = (hip_y + foot_y) * 0.5

            thip = trans(hip_x, hip_y)
            tknee = trans(knee_x, knee_y)
            tfoot = trans(foot_x, foot_y)

            color_pantalon = (26, 22, 34) if not es_frontal else MARRON_OSCURO
            ancho_art = max(2, round(4 * escala_x))

            # Muslo y espinilla
            pygame.draw.line(surface, color_pantalon, thip, tknee, ancho_art)
            pygame.draw.line(surface, color_pantalon, tknee, tfoot, ancho_art)
            # Rótula / articulación
            pygame.draw.circle(surface, (18, 14, 24), tknee, max(1, round(2 * escala_x)))

            # Bota de cuero reforzada
            talon = (tfoot[0] - round(self.direccion * 2 * escala_x), tfoot[1])
            punta = (tfoot[0] + round(self.direccion * 4 * escala_x), tfoot[1])
            pygame.draw.line(surface, NEGRO, talon, punta, max(2, round(4 * escala_y)))
            # Hebilla metálica de la bota
            hebilla_x = tfoot[0] + round(self.direccion * 1 * escala_x)
            pygame.draw.circle(surface, (185, 150, 60), (hebilla_x, tfoot[1] - 1), 1)

        # Capa trasera: pierna posterior (fase opuesta phi + pi)
        lado_trasero = -self.direccion * 4
        dibujar_pierna(lado_trasero, fase_locomocion + math.pi, False)

        # --- Torso, Abrigo y Delantal --- #
        cuerpo_w = 18
        cuerpo_h = rect.height - 16
        cuerpo_x = centro_x - 9 + lean_x
        cuerpo_y = rect.y + 10 + cadera_bob

        t_tl = trans(cuerpo_x, cuerpo_y)
        t_tr = trans(cuerpo_x + cuerpo_w, cuerpo_y)
        t_br = trans(cuerpo_x + cuerpo_w, cuerpo_y + cuerpo_h)
        t_bl = trans(cuerpo_x, cuerpo_y + cuerpo_h)
        poly_cuerpo = [t_tl, t_tr, t_br, t_bl]

        pygame.draw.polygon(surface, AZUL_OSCURO, poly_cuerpo)

        # Delantal de sepulturero
        d_tl = trans(cuerpo_x + 3, cuerpo_y + 4)
        d_tr = trans(cuerpo_x + cuerpo_w - 3, cuerpo_y + 4)
        d_br = trans(cuerpo_x + cuerpo_w - 4, cuerpo_y + cuerpo_h)
        d_bl = trans(cuerpo_x + 4, cuerpo_y + cuerpo_h)
        pygame.draw.polygon(surface, MARRON, [d_tl, d_tr, d_br, d_bl])

        pygame.draw.polygon(surface, NEGRO, poly_cuerpo, 1)

        # Cinturón de cuero y hebilla
        cinto_izq = trans(cuerpo_x, cuerpo_y + 6)
        cinto_der = trans(cuerpo_x + cuerpo_w, cuerpo_y + 6)
        pygame.draw.line(surface, MARRON_OSCURO, cinto_izq, cinto_der, max(1, round(3 * escala_y)))
        cinto_centro = trans(centro_x + lean_x, cuerpo_y + 6)
        pygame.draw.circle(surface, (190, 160, 60), cinto_centro, 2)

        if self.dash_tiempo > 0:
            pygame.draw.polygon(surface, TURQUESA, poly_cuerpo, 1)

        # Capa delantera: pierna frontal
        lado_frontal = self.direccion * 4
        dibujar_pierna(lado_frontal, fase_locomocion, True)

        # --- Cabeza, Sombrero de ala ancha y Bufanda --- #
        cabeza_pos = trans(centro_x + lean_x, rect.y + 10 + cadera_bob)
        rx_cabeza, ry_cabeza = trans_r(8, 8)
        pygame.draw.ellipse(
            surface,
            CREMA,
            (cabeza_pos[0] - rx_cabeza, cabeza_pos[1] - ry_cabeza, rx_cabeza * 2, ry_cabeza * 2),
        )
        pygame.draw.ellipse(
            surface,
            NEGRO,
            (cabeza_pos[0] - rx_cabeza, cabeza_pos[1] - ry_cabeza, rx_cabeza * 2, ry_cabeza * 2),
            1,
        )

        # Sombrero de sepulturero (ala ancha)
        ala_izq = trans(centro_x - 12 + lean_x, rect.y + 4 + cadera_bob)
        ala_der = trans(centro_x + 12 + lean_x, rect.y + 4 + cadera_bob)
        pygame.draw.line(surface, NEGRO, ala_izq, ala_der, max(2, round(4 * escala_y)))

        # Copa del sombrero
        copa_tl = trans(centro_x - 6 + lean_x, rect.y - 1 + cadera_bob)
        copa_tr = trans(centro_x + 6 + lean_x, rect.y - 1 + cadera_bob)
        copa_br = trans(centro_x + 6 + lean_x, rect.y + 3 + cadera_bob)
        copa_bl = trans(centro_x - 6 + lean_x, rect.y + 3 + cadera_bob)
        pygame.draw.polygon(surface, MARRON_OSCURO, [copa_tl, copa_tr, copa_br, copa_bl])

        # Cinta roja de la copa
        cinta_izq = trans(centro_x - 6 + lean_x, rect.y + 2 + cadera_bob)
        cinta_der = trans(centro_x + 6 + lean_x, rect.y + 2 + cadera_bob)
        pygame.draw.line(surface, SANGRE, cinta_izq, cinta_der, max(1, round(2 * escala_y)))

        # Ojo del sepulturero
        ojo_x = centro_x + self.direccion * 3 + lean_x
        ojo_pos = trans(ojo_x, rect.y + 10 + cadera_bob)
        pygame.draw.circle(surface, NEGRO, ojo_pos, 1)

        # Bufanda escarlata
        bufanda_izq = trans(centro_x - 7 + lean_x, rect.y + 15 + cadera_bob)
        bufanda_der = trans(centro_x + 7 + lean_x, rect.y + 15 + cadera_bob)
        pygame.draw.line(surface, SANGRE, bufanda_izq, bufanda_der, max(2, round(3 * escala_y)))
        # Cola de la bufanda que ondea con inercia
        cola_bufanda = trans(
            centro_x - self.direccion * 8 + arrastre_vx * 0.5 + lean_x,
            rect.y + 17 + cadera_bob + math.sin(tiempo * 18.0) * 1.5,
        )
        pygame.draw.line(surface, SANGRE, trans(centro_x - self.direccion * 4 + lean_x, rect.y + 15 + cadera_bob), cola_bufanda, 2)

        # --- Arma: Pala / Guadaña Mística --- #
        hombro_x = centro_x - self.direccion * 7 + lean_x
        es_guadaña = getattr(self, "rango_ataque_mejorado", False)

        if atacando:
            alcance = (34 if es_guadaña else 15) if pose == "ataque2" else (26 if es_guadaña else 12)
            alto_pala = {
                "ataque1": rect.y - (6 if es_guadaña else -2),
                "ataque2": rect.y + 12,
                "ataque3": base_y + (4 if es_guadaña else -1),
            }[pose]
            punta_x = centro_x + self.direccion * alcance

            thombro = trans(hombro_x, rect.y + 8 + cadera_bob)
            tpunta = trans(punta_x, alto_pala)

            color_mango = (45, 30, 48) if es_guadaña else MARRON
            pygame.draw.line(
                surface,
                color_mango,
                thombro,
                tpunta,
                max(2, round((4 if es_guadaña else 3) * escala_x)),
            )

            if con_pala:
                if es_guadaña:
                    signo = self.direccion
                    color_hoja = (215, 80, 255)
                    color_filo = (255, 205, 255)
                    puntos_hoja_rel = [
                        (punta_x, alto_pala - 8),
                        (punta_x + signo * 20, alto_pala - 2),
                        (punta_x + signo * 28, alto_pala + 14),
                        (punta_x + signo * 18, alto_pala + 10),
                        (punta_x + signo * 8, alto_pala + 4),
                        (punta_x - signo * 2, alto_pala),
                    ]
                    puntos_hoja = [trans(px, py) for px, py in puntos_hoja_rel]
                    pygame.draw.polygon(surface, color_hoja, puntos_hoja)
                    pygame.draw.lines(surface, color_filo, False, puntos_hoja[:4], 2)

                    # Arco espectral de energía
                    onda_x = centro_x if signo > 0 else centro_x - 76
                    onda_y = rect.y - 12
                    onda_surf = pygame.Surface((78, 50), pygame.SRCALPHA)
                    pygame.draw.arc(
                        onda_surf,
                        (215, 80, 255, 200),
                        (2, 2, 74, 46),
                        0.0 if signo > 0 else 1.57,
                        3.14 if signo > 0 else 4.71,
                        5,
                    )
                    pygame.draw.arc(
                        onda_surf,
                        (255, 230, 255, 255),
                        (4, 4, 70, 42),
                        0.0 if signo > 0 else 1.57,
                        3.14 if signo > 0 else 4.71,
                        2,
                    )
                    surface.blit(onda_surf, (onda_x, onda_y))
                else:
                    puntos_pala_rel = [
                        (punta_x, alto_pala - 5),
                        (punta_x + self.direccion * 8, alto_pala),
                        (punta_x, alto_pala + 6),
                        (punta_x - self.direccion * 2, alto_pala),
                    ]
                    puntos_pala = [trans(px, py) for px, py in puntos_pala_rel]
                    pygame.draw.polygon(surface, GRIS, puntos_pala)
        elif con_pala:
            if es_guadaña:
                thombro = trans(hombro_x, rect.y + 4 + cadera_bob)
                tbase = trans(hombro_x - self.direccion * 8, base_y + 4)
                pygame.draw.line(surface, (45, 30, 48), thombro, tbase, 3)
                rx_a, ry_a = trans_r(10, 11)
                arc_x = thombro[0] - (6 if self.direccion > 0 else 14)
                pygame.draw.arc(surface, (215, 80, 255), (arc_x, thombro[1] - ry_a, rx_a * 2, ry_a * 2), 0.0, 3.14, 3)
            else:
                thombro = trans(hombro_x, rect.y + 7 + cadera_bob)
                tbase = trans(hombro_x - self.direccion * 4, base_y - 2)
                pygame.draw.line(surface, MARRON, thombro, tbase, 3)
                puntos_rel = [
                    (hombro_x - self.direccion * 7, base_y - 4),
                    (hombro_x - self.direccion * 1, base_y - 1),
                    (hombro_x - self.direccion * 4, base_y + 4),
                ]
                pygame.draw.polygon(surface, GRIS, [trans(px, py) for px, py in puntos_rel])

        # --- Péndulo mortuorio del farol con oscilación armónica y halo de luz translúcido --- #
        pivote_x = centro_x + self.direccion * 7 + lean_x
        pivote_y = rect.y + 15 + cadera_bob
        tpivote = trans(pivote_x, pivote_y)

        # Oscilación armónica + arrastre inercial elástico
        oscilacion_farol = math.sin(tiempo * 4.2) * 0.28
        inercia_vx = -limitar(self.vx / 160.0, -0.65, 0.65)
        inercia_dash = (-self.dash_direccion * 0.85) if self.dash_tiempo > 0 else 0.0
        angulo_farol = oscilacion_farol + inercia_vx + inercia_dash

        longitud_cadena = 10.5
        farol_x = pivote_x + math.sin(angulo_farol) * longitud_cadena
        farol_y = pivote_y + math.cos(angulo_farol) * longitud_cadena
        tfarol = trans(farol_x, farol_y)

        # Cadena de eslabones oscilante
        pygame.draw.line(surface, (75, 70, 80), tpivote, tfarol, 1)

        # Armazón gótico del farol mortuorio
        cupula_top = (tfarol[0], tfarol[1] - 5)
        cupula_izq = (tfarol[0] - 4, tfarol[1] - 3)
        cupula_der = (tfarol[0] + 4, tfarol[1] - 3)
        pygame.draw.polygon(surface, (75, 58, 38), [cupula_top, cupula_der, cupula_izq])

        # Cámara de vidrio con fulgor ámbar
        pygame.draw.circle(surface, (120, 86, 34), tfarol, 5)
        pygame.draw.circle(surface, AMARILLO, tfarol, 3)
        pygame.draw.circle(surface, (255, 255, 220), tfarol, 1)

        # Remate inferior de hierro
        pygame.draw.line(surface, (45, 38, 28), (tfarol[0] - 3, tfarol[1] + 4), (tfarol[0] + 3, tfarol[1] + 4), 1)
        pygame.draw.line(surface, (45, 38, 28), (tfarol[0], tfarol[1] + 4), (tfarol[0], tfarol[1] + 6), 1)

        # Superficie con halo de luz circular translúcida
        halo_diametro = 80
        halo_radio = halo_diametro // 2
        halo_surf = pygame.Surface((halo_diametro, halo_diametro), pygame.SRCALPHA)
        flicker = math.sin(tiempo * 16.0) * 1.5 + math.cos(tiempo * 24.0) * 0.8

        pygame.draw.circle(halo_surf, (255, 175, 45, 16), (halo_radio, halo_radio), int(36 + flicker))
        pygame.draw.circle(halo_surf, (255, 195, 65, 34), (halo_radio, halo_radio), int(25 + flicker * 0.7))
        pygame.draw.circle(halo_surf, (255, 220, 95, 65), (halo_radio, halo_radio), int(15 + flicker * 0.4))
        pygame.draw.circle(halo_surf, (255, 248, 180, 110), (halo_radio, halo_radio), int(7 + flicker * 0.2))

        surface.blit(
            halo_surf,
            (tfarol[0] - halo_radio, tfarol[1] - halo_radio),
            special_flags=pygame.BLEND_RGBA_ADD,
        )


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
                self.aviso_tiempo = 0.30  # Telegrafía visual anticipada (>= 200 ms)
            else:
                self.aviso_tiempo = max(self.aviso_tiempo, 0.25)

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

        # Ojos: patrulla vs Fulgor en ojos telegrafiado (>= 200 ms antes de golpear)
        ojo_offset = self.direccion * 2
        ojo_izq = (centro_x - 3 + ojo_offset, rect.y + 8 + salto)
        ojo_der = (centro_x + 3 + ojo_offset, rect.y + 8 + salto)

        if self.aviso_tiempo > 0:
            # Fulgor ardiente en ojos durante telegrafía anticipada (>= 200 ms)
            pulso_ojos = math.sin(tiempo * 24.0)
            radio_fulgor = 4 if pulso_ojos > 0 else 3

            # Halo escarlata ardiente
            pygame.draw.circle(surface, (255, 30, 30), ojo_izq, radio_fulgor)
            pygame.draw.circle(surface, (255, 30, 30), ojo_der, radio_fulgor)
            # Núcleo de calor ígneo
            pygame.draw.circle(surface, (255, 230, 110), ojo_izq, 2)
            pygame.draw.circle(surface, (255, 230, 110), ojo_der, 2)
            pygame.draw.circle(surface, (255, 255, 220), ojo_izq, 1)
            pygame.draw.circle(surface, (255, 255, 220), ojo_der, 1)

            # Destello y haz proyectado hacia adelante en la dirección de embestida
            rayo_len = int(12 + pulso_ojos * 3)
            ojo_frontal = ojo_der if self.direccion > 0 else ojo_izq
            pygame.draw.line(
                surface,
                (255, 50, 50),
                ojo_frontal,
                (ojo_frontal[0] + self.direccion * rayo_len, ojo_frontal[1]),
                2,
            )
            pygame.draw.line(
                surface,
                (255, 240, 200),
                ojo_frontal,
                (ojo_frontal[0] + self.direccion * (rayo_len // 2), ojo_frontal[1]),
                1,
            )
        else:
            # Ojos normales
            pygame.draw.circle(surface, ROJO, ojo_izq, 2)
            pygame.draw.circle(surface, ROJO, ojo_der, 2)
            pygame.draw.circle(surface, (255, 160, 160), (ojo_izq[0] + 1, ojo_izq[1] - 1), 1)
            pygame.draw.circle(surface, (255, 160, 160), (ojo_der[0] + 1, ojo_der[1] - 1), 1)

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

        # Garras del lado libre
        lado_libre = 4 if self.direccion > 0 else rect.width - 5
        signo_libre = -1 if self.direccion > 0 else 1
        bx = rect.x + lado_libre
        for dedo_dx in (-2, 0, 2):
            pygame.draw.line(
                surface, HUESO,
                (bx + dedo_dx, base_y - 3),
                (bx + dedo_dx + signo_libre, base_y + 5),
                1,
            )

        # --- Elevación cinemática de arma / Lectura clara del peligro --- #
        hombro_x = centro_x + self.direccion * 5
        hombro_y = rect.y + 13 + salto

        if self.aviso_tiempo > 0:
            # Postura telegrafiada: arma elevada por encima de la cabeza lista para golpear
            codo_x = hombro_x - self.direccion * 4
            codo_y = hombro_y - 8
            mano_x = hombro_x - self.direccion * 2
            mano_y = hombro_y - 14

            # Brazo esquelético alzado
            pygame.draw.line(surface, HUESO, (hombro_x, hombro_y), (codo_x, codo_y), 3)
            pygame.draw.line(surface, HUESO, (codo_x, codo_y), (mano_x, mano_y), 3)

            # Mango del arma
            mango_punta_x = mano_x - self.direccion * 4
            mango_punta_y = mano_y + 6
            pygame.draw.line(surface, MARRON_OSCURO, (mano_x, mano_y), (mango_punta_x, mango_punta_y), 3)

            # Hoja de alfanje/hacha pesada elevada por encima de la cabeza
            hoja_punta_x = mano_x + self.direccion * 14
            hoja_punta_y = mano_y - 12
            pygame.draw.line(surface, (90, 85, 95), (mano_x, mano_y), (hoja_punta_x, hoja_punta_y), 4)

            puntos_hoja = [
                (mano_x, mano_y),
                (hoja_punta_x, hoja_punta_y),
                (hoja_punta_x + self.direccion * 6, hoja_punta_y + 5),
                (mano_x + self.direccion * 5, mano_y + 3),
            ]
            pygame.draw.polygon(surface, (115, 110, 120), puntos_hoja)
            pygame.draw.line(surface, (255, 235, 235), puntos_hoja[1], puntos_hoja[2], 2)
            pygame.draw.line(surface, SANGRE, puntos_hoja[0], puntos_hoja[3], 2)

            # Arco cinemático de peligro y destello de amenaza
            teleg_surf = pygame.Surface((36, 36), pygame.SRCALPHA)
            pygame.draw.arc(
                teleg_surf,
                (255, 45, 45, 210),
                (2, 2, 32, 32),
                0.2 if self.direccion > 0 else 1.8,
                2.8 if self.direccion > 0 else 4.4,
                3,
            )
            surface.blit(teleg_surf, (mano_x - 18, mano_y - 18), special_flags=pygame.BLEND_RGBA_ADD)

            # Heraldo de peligro visual sobre la cabeza
            alerta_y = rect.y - 7 + salto
            pygame.draw.polygon(
                surface,
                (255, 40, 40),
                [
                    (centro_x, alerta_y),
                    (centro_x - 4, alerta_y - 6),
                    (centro_x + 4, alerta_y - 6),
                ],
            )
            pygame.draw.circle(surface, (255, 255, 180), (centro_x, alerta_y - 9), 2)
        else:
            # Postura en patrulla: arma descansando baja al costado
            mano_x = hombro_x + self.direccion * 5
            mano_y = hombro_y + 8
            pygame.draw.line(surface, HUESO, (hombro_x, hombro_y), (mano_x, mano_y), 3)

            # Hoja apuntando hacia el suelo
            punta_x = mano_x + self.direccion * 4
            punta_y = base_y + 2
            pygame.draw.line(surface, (90, 85, 95), (mano_x, mano_y), (punta_x, punta_y), 3)
            puntos_hoja = [
                (mano_x, mano_y),
                (punta_x, punta_y),
                (punta_x - self.direccion * 4, punta_y - 2),
                (mano_x - self.direccion * 3, mano_y + 1),
            ]
            pygame.draw.polygon(surface, (115, 110, 120), puntos_hoja)
            pygame.draw.line(surface, (200, 195, 205), puntos_hoja[1], puntos_hoja[2], 1)


# --- Clase TotemProyectil --- #
class TotemProyectil:
    """Totem que lanza proyectiles a intervalos regulares."""

    def __init__(self, x, y):
        self.inicial_x = float(x)
        self.inicial_y = float(y)
        self.rect = pygame.Rect(int(x) - 16, int(y) - 32, 32, 32)
        self.inicial_rect = pygame.Rect(self.rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vivo = True
        self.temporizador_proyectil = 0.0
        self.ultimo_proyectil = 0.0
        self.conproyectil = False

    # --- Función reiniciar --- #
    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
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
        centro_x = rect.centerx
        base_y = rect.bottom

        # Sombra en la base
        pygame.draw.ellipse(
            surface,
            (7, 6, 10),
            (rect.x + 2, base_y - 4, rect.width - 4, 7),
        )

        # Obelisco / Tótem monolítico de piedra arcana de la cripta
        puntos_obelisco = [
            (centro_x, rect.top - 2),
            (rect.right - 2, base_y),
            (rect.left + 2, base_y),
        ]
        pygame.draw.polygon(surface, (58, 48, 54), puntos_obelisco)
        pygame.draw.polygon(surface, (36, 28, 34), puntos_obelisco, 2)

        # Relieve y faceta sombreada lateral
        puntos_sombra = [
            (centro_x, rect.top - 2),
            (centro_x, base_y),
            (rect.right - 2, base_y),
        ]
        pygame.draw.polygon(surface, (44, 34, 40), puntos_sombra)

        # Base escalonada de piedra antigua
        pygame.draw.rect(surface, (68, 56, 62), (rect.left + 4, base_y - 6, rect.width - 8, 6), border_radius=2)
        pygame.draw.rect(surface, (26, 20, 24), (rect.left + 4, base_y - 6, rect.width - 8, 6), 1, border_radius=2)

        # Runas místicas grabadas que pulsan con energía espectral
        pulso_runa = 0.5 + 0.5 * math.sin(tiempo * 4.0)
        color_runa = (
            int(150 + pulso_runa * 80),
            int(60 + pulso_runa * 50),
            int(215 + pulso_runa * 40),
        )
        # Glifo vertical
        pygame.draw.line(surface, color_runa, (centro_x, rect.top + 8), (centro_x, base_y - 10), 2)
        pygame.draw.line(surface, color_runa, (centro_x - 4, rect.top + 14), (centro_x + 4, rect.top + 14), 2)
        pygame.draw.line(surface, color_runa, (centro_x - 3, rect.top + 20), (centro_x + 3, rect.top + 20), 2)
        # Ojo arcano en el monolito
        pygame.draw.circle(surface, color_runa, (centro_x, rect.top + 10), 3)
        pygame.draw.circle(surface, (255, 230, 255), (centro_x, rect.top + 10), 1)

        # Proyectil de plasma suspendido levitando sobre el obelisco
        if self.conproyectil:
            levitacion = math.sin(tiempo * 6.0) * 3.0
            orb_y = rect.top - 8 + levitacion
            orb_centro = (centro_x, round(orb_y))

            # Halo translúcido del proyectil
            orb_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(orb_surf, (190, 80, 255, 45), (16, 16), 14)
            pygame.draw.circle(orb_surf, (255, 140, 50, 70), (16, 16), 9)
            pygame.draw.circle(orb_surf, (255, 220, 120, 160), (16, 16), 5)
            surface.blit(orb_surf, (orb_centro[0] - 16, orb_centro[1] - 16), special_flags=pygame.BLEND_RGBA_ADD)

            # Núcleo del proyectil
            pygame.draw.circle(surface, (230, 120, 40), orb_centro, 4)
            pygame.draw.circle(surface, (255, 245, 200), orb_centro, 2)

            # Partículas orbitales del proyectil
            for ang_offset in (0.0, math.pi * 0.66, math.pi * 1.33):
                ang = tiempo * 5.0 + ang_offset
                part_x = orb_centro[0] + round(math.cos(ang) * 9)
                part_y = orb_centro[1] + round(math.sin(ang) * 5)
                pygame.draw.circle(surface, (255, 180, 60), (part_x, part_y), 1)

            # Advertencia / Telegrafía de disparo inminente
            if self.ultimo_proyectil > 0 and int(tiempo * 12) % 2 == 0:
                pygame.draw.circle(surface, (255, 40, 40), orb_centro, 11, 1)

        # Soportes de osamenta en la base
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
        pulso = int(2 * math.sin(tiempo * 18 + rect.x * 0.05))
        pygame.draw.arc(
            surface,
            (235, 218, 184),
            (rect.x - 8, rect.y - 6 - pulso, rect.width + 16, rect.height + 12),
            0.1,
            math.pi - 0.1,
            3,
        )
        pygame.draw.arc(
            surface,
            (124, 96, 62),
            (rect.x - 12, rect.y - 2, rect.width + 24, rect.height + 4),
            0.15,
            math.pi - 0.15,
            2,
        )
        for i in range(3):
            px = rect.centerx - 8 + i * 8
            pygame.draw.line(
                surface,
                (225, 210, 180),
                (px, rect.bottom - 4),
                (px - 3, rect.top + 4 + i),
                2,
            )


# --- Clase Custodio --- #
class Custodio:
    """Jefe final: 2 fases.
    Fase 1 (vida 6->3): pala+pistón lo dañan, 2 ondas por golpe.
    Fase 2 (vida 3->0): SOLO pisotón lo daña (pala rebota), 3 ondas,
    ventana vulnerable más corta, carga horizontal telegrafíada.
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

    # --- Aplicar daño interno --- #
    def _aplicar_dano(self):
        """Descuenta 1 vida, maneja transición a Fase 2 y muerte."""
        self.vida -= 1
        self.golpes_fase += 1
        self.vulnerable = False
        self.recien_golpeado = True
        self.carga_activa = False

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
    def recibir_golpe_pala(self):
        """Pala: funciona en Fase 1. En Fase 2 rebota (solo pisotón hace daño)."""
        if not self.vivo:
            return False
        if self.fase >= 2:
            return False  # Pala rebota en Fase 2
        return self._aplicar_dano()

    # --- Función recibir_pisaton --- #
    def recibir_pisaton(self):
        """Pisotón: funciona siempre en ambas fases."""
        if not self.vivo:
            return False
        return self._aplicar_dano()

    # --- Función recibir_golpe (compatibilidad tests y golpe cuerpo a cuerpo) --- #
    def recibir_golpe(self):
        """Alias de recibir_golpe_pala."""
        return self.recibir_golpe_pala()

    # --- Función actualizar --- #
    def actualizar(self, dt, jugador):
        self.recien_golpeado = False
        self.ondas_recien = False
        self.aviso_recien = False
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

        pygame.draw.ellipse(surface, (7, 6, 10), (rect.x, base_y - 6, rect.width, 10))

        # Aura: dorada si vulnerable en Fase 1, roja permanente en Fase 2
        if self.fase >= 2:
            aura_color = (200, 40, 40, int(18 + pulso * 22))
            aura = pygame.Surface((rect.width + 22, rect.height + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(aura, aura_color, aura.get_rect())
            surface.blit(aura, (rect.x - 11, rect.y - 10), special_flags=pygame.BLEND_RGBA_ADD)
        elif self.vulnerable:
            aura = pygame.Surface((rect.width + 18, rect.height + 16), pygame.SRCALPHA)
            pygame.draw.ellipse(aura, (255, 205, 95, 30), aura.get_rect())
            pygame.draw.ellipse(
                aura, (255, 225, 150, 22), aura.get_rect().inflate(-14, -26)
            )
            surface.blit(
                aura,
                (rect.x - 9, rect.y - 8),
                special_flags=pygame.BLEND_RGBA_ADD,
            )

        if self.estado in ("telegrafia", "telegrafia_carga"):
            color_brillo = (220, 60, 60) if self.estado == "telegrafia_carga" else (170, 30, 38)
            brillo = pygame.Surface((rect.width + 50, rect.height + 40), pygame.SRCALPHA)
            pygame.draw.ellipse(
                brillo,
                (*color_brillo, int(70 + pulso * 50)),
                (10, 20, brillo.get_width() - 20, brillo.get_height() - 20),
            )
            surface.blit(
                brillo,
                (rect.x - 25, rect.y - 15),
                special_flags=pygame.BLEND_RGBA_ADD,
            )

        # Capa y joroba — roja en Fase 2
        capa_color = (55, 18, 18) if self.fase >= 2 else (38, 31, 44)
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
        cuerpo_color = (38, 12, 12) if self.fase >= 2 else (23, 20, 28)
        pygame.draw.rect(surface, cuerpo_color, (centro_x - 21, rect.y + 12, 42, 44), border_radius=12)
        pygame.draw.line(
            surface,
            (78, 55, 52),
            (centro_x - 15, rect.y + 26),
            (centro_x + 15, rect.y + 26),
            2,
        )
        for i in range(4):
            pygame.draw.line(
                surface,
                MUSGO,
                (centro_x - 14 + i * 2, rect.y + 31 + i * 4),
                (centro_x + 14 - i * 2, rect.y + 31 + i * 4),
                1,
            )

        # Cráneo y farol incrustado
        pygame.draw.circle(surface, HUESO, (centro_x, rect.y + 16), 12)
        pygame.draw.circle(surface, NEGRO, (centro_x, rect.y + 16), 12, 1)
        # Ojos: rojo fuego en Fase 2; dorado si vulnerable en Fase 1
        if self.fase >= 2:
            color_ojo = (200, 60, 40)
        else:
            color_ojo = (235, 198, 92) if self.vulnerable else (178, 38, 42)
        pygame.draw.circle(surface, color_ojo, (centro_x - 4, rect.y + 15), 2)
        pygame.draw.circle(surface, color_ojo, (centro_x + 4, rect.y + 15), 2)
        pygame.draw.rect(surface, NEGRO, (centro_x - 5, rect.y + 21, 10, 2))
        pygame.draw.circle(surface, (122, 82, 30), (centro_x, rect.y + 34), 7)
        pygame.draw.circle(surface, AMARILLO, (centro_x, rect.y + 34), 3)

        # Pala rota
        pygame.draw.line(
            surface,
            MARRON,
            (centro_x + 21, rect.y + 26),
            (centro_x + 29, base_y - 6),
            5,
        )
        pygame.draw.polygon(
            surface,
            GRIS,
            [
                (centro_x + 24, base_y - 12),
                (centro_x + 38, base_y - 5),
                (centro_x + 28, base_y + 3),
                (centro_x + 18, base_y - 3),
            ],
        )

class Cuervo:
    """Cuervo que vuela en patrón circular. Daño por contacto."""

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

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.angulo = 0.0
        self.vivo = True

    def actualizar(self, dt):
        if not self.vivo:
            return
        self.angulo += self.velocidad * dt
        self.x = self.centro_x + math.cos(self.angulo) * self.radio - self.rect.width // 2
        self.y = self.centro_y + math.sin(self.angulo) * self.radio * 0.5 - self.rect.height // 2
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return
        rect = camara.aplicar_rect(self.rect)
        centro_x = rect.centerx
        base_y = rect.bottom

        pygame.draw.ellipse(surface, (7, 6, 10), (rect.x + 2, base_y - 4, rect.width - 4, 5))

        # Cuerpo del cuervo (negro azabache).
        pygame.draw.ellipse(surface, (18, 16, 22), (rect.x + 4, rect.y + 6, rect.width - 8, rect.height - 10))
        # Alas extendidas.
        pygame.draw.polygon(surface, (10, 8, 14), [(rect.x, rect.y + 10), (rect.centerx - 4, rect.y + 2), (rect.centerx, rect.y + 10)])
        pygame.draw.polygon(surface, (10, 8, 14), [(rect.right, rect.y + 10), (rect.centerx + 4, rect.y + 2), (rect.centerx, rect.y + 10)])
        # Pico.
        pygame.draw.polygon(surface, NARANJA, [(rect.centerx, rect.y + 14), (rect.centerx + 5, rect.y + 16), (rect.centerx, rect.y + 18)])
        # Ojos rojos.
        pygame.draw.circle(surface, ROJO, (centro_x - 3, rect.y + 12), 1)
        pygame.draw.circle(surface, ROJO, (centro_x + 3, rect.y + 12), 1)


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
    """Power-up que mejora el alcance del ataque de pala."""

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
            jugador.rango_ataque_mejorado = True
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

