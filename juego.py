# ============================================================
# juego.py — Bucle principal, estados y presentación
# ============================================================
# Estados: titulo / jugando / pausa / nivel_completado / derrota / victoria.
# La lógica de IN CRYPTA vive acá; las entidades y los niveles están
# separados para poder probarlos sin abrir una ventana.
# ============================================================

import math
import sys
import textwrap

import pygame

from audio import Audio
from camara import Camara
from config import (
    ALMAS_POR_VIDA,
    ALTO,
    ATAQUE_COOLDOWN,
    AMARILLO,
    ANCHO,
    AZUL_OSCURO,
    BLANCO,
    CELESTE,
    CREMA,
    DASH_COOLDOWN,
    DASH_USOS_AIRE,
    DASH_DASHTURQUESA,
    DASH_VELOCIDAD,
    EQUIPO,
    FPS,
    GRIS,
    GRIS_OSCURO,
    HUD_ALMA,
    HUD_BORDE,
    HUD_DASHTURQUESA,
    HUD_MUTED,
    HUD_NEGRO,
    HUD_NEGRO_X,
    HUD_ORO,
    HUD_PANEL,
    HUD_PANEL_ALTO,
    HUD_ROJO,
    HUD_TEXTO,
    HUD_VERDE,
    HUESO,
    HUD_GRIS_CLARO,
    INTEGRANTES,
    JEFE_ONDA_VELOCIDAD,
    ORO,
    REBOTE_ENEMIGO,
    TITULO,
    SUBTITULO,
    TILE,
    VIDAS_INICIALES,
    VIDAS_MAXIMAS,
    ROJO,
    NEGRO,
    SANGRE,
    REFERENCIAS,
    NIEBLA,
    TURQUESA,
    SOMBRA,
    HUD_ANGOSTO_ALTO,
    HUD_MAX_ANCHO,
    HUD_ESQUINAS_X,
    HUD_ESQUINAS_Y,
    HUD_ESQUINAS_ANCHO,
    HUD_ESQUINAS_ALTO,
    MAX_DT,
)
from efectos import EfectoAnimacion, ease_out_back, ease_out_cubic, ease_in_out_cubic
from entidades import (
    Araña,
    Cuervo,
    EnemigoMelee,
    Jugador,
    OndaCustodio,
    Polilla,
    TotemProyectil,
)
from nivel import Nivel
from niveles import NIVELES, SALAS_PRUEBA
from particulas import SistemaParticulas


# --- Clase Juego --- #
class Juego:
    def __init__(self, sala_inicial=None):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO)
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        self.fuentes = {}
        try:
            self._ruta_fuente_gotica = "export/gdevelop_nativo/assets/NotoSerifDisplay-Bold.ttf"
        except Exception:
            self._ruta_fuente_gotica = None
        self.fondos = {}
        self.vineta = self.crear_vineta(90)

        self.particulas = SistemaParticulas()
        self.efecto_hud = EfectoAnimacion()
        self.audio = Audio()

        self.nivel_indice = 0
        self.nivel = None
        self.jugador = None
        self.camara = Camara()
        self.estado = "titulo"
        self.tiempo_nivel = 0.0
        self.tiempo_total = 0.0
        self.tiempo_titulo = 0.0
        self.almas_totales = 0
        self.mostrar_ayuda = 0.0
        self.flash = 0.0
        self.flash_color = (255, 255, 255)
        self.jefe = None
        self.ondas_jefe = []
        self.punto_reintento = None
        self.aviso_jefe = 0.0
        self.sala_prueba = False
        self.sala_prueba_indice = None
        self.test_opcion = 0

        if sala_inicial is not None:
            self.cargar_sala_prueba(sala_inicial)
        else:
            self.cargar_nivel(0, vidas=VIDAS_INICIALES)
            self.estado = "titulo"
            self.mostrar_ayuda = 0.0

    # --- Función cargar_nivel --- #
    def cargar_nivel(self, indice, vidas=None, sala=None):
        self.sala_prueba = sala is not None
        self.sala_prueba_indice = sala
        if sala is None:
            self.nivel_indice = indice
            datos = NIVELES[indice]
            tiene_pala = indice >= 2
        else:
            datos = SALAS_PRUEBA[sala]
            self.nivel_indice = datos["nivel"]
            tiene_pala = datos["pala"]

        self.nivel = Nivel(
            datos["mapa"],
            datos["nombre"],
            datos["pista"],
            datos.get("tema", "camposanto"),
        )
        vidas_iniciales = VIDAS_INICIALES if vidas is None else vidas
        self.jugador = Jugador(*self.nivel.spawn, vidas=vidas_iniciales)
        self.jugador.tiene_pala = tiene_pala
        self.camara = Camara()
        self.camara.actualizar(self.jugador, self.nivel, 1.0)
        self.estado = "jugando"
        self.tiempo_nivel = 0.0
        self.mostrar_ayuda = 5.0
        self.flash = 0.0
        self.jefe = self.nivel.jefes[0] if self.nivel.jefes else None
        self.ondas_jefe = []
        self.punto_reintento = None
        self.aviso_jefe = 0.0

    # --- Función cargar_sala_prueba --- #
    def cargar_sala_prueba(self, indice):
        self.cargar_nivel(SALAS_PRUEBA[indice]["nivel"], vidas=VIDAS_INICIALES, sala=indice)
        self.estado = "jugando"

    # --- Función abrir_selector_pruebas --- #
    def abrir_selector_pruebas(self):
        self.estado = "test_selector"
        self.test_opcion = 0
        self.audio.reproducir("ui")

    # --- Función iniciar_partida --- #
    def iniciar_partida(self):
        self.almas_totales = 0
        self.tiempo_total = 0.0
        self.cargar_nivel(0, vidas=VIDAS_INICIALES)
        self.estado = "jugando"

    # --- Función reiniciar_juego --- #
    def reiniciar_juego(self):
        self.almas_totales = 0
        self.tiempo_total = 0.0
        self.cargar_nivel(0, vidas=VIDAS_INICIALES)

    # --- Función siguiente_nivel --- #
    def siguiente_nivel(self):
        self.almas_totales += self.jugador.almas
        if self.nivel_indice + 1 >= len(NIVELES):
            self.estado = "victoria"
            return
        self.cargar_nivel(self.nivel_indice + 1, vidas=self.jugador.vidas)

    # --- Función procesar_eventos --- #
    def procesar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False

            elif evento.type == pygame.KEYDOWN:
                if self.estado == "test_selector":
                    if evento.key == pygame.K_ESCAPE:
                        self.estado = "titulo"
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_UP, pygame.K_w):
                        self.test_opcion = (self.test_opcion - 1) % len(SALAS_PRUEBA)
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_DOWN, pygame.K_s):
                        self.test_opcion = (self.test_opcion + 1) % len(SALAS_PRUEBA)
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        self.cargar_sala_prueba(evento.key - pygame.K_1)
                    elif evento.key == pygame.K_RETURN:
                        self.cargar_sala_prueba(self.test_opcion)
                    continue

                if evento.key == pygame.K_ESCAPE:
                    if self.estado == "sala_completada":
                        self.abrir_selector_pruebas()
                    else:
                        self.corriendo = False

                elif evento.key == pygame.K_m:
                    self.audio.alternar()

                elif evento.key == pygame.K_r and self.estado != "titulo":
                    if self.sala_prueba:
                        self.cargar_sala_prueba(self.sala_prueba_indice)
                    else:
                        self.reiniciar_juego()

                elif evento.key == pygame.K_t and self.estado == "titulo":
                    self.abrir_selector_pruebas()

                elif evento.key == pygame.K_p:
                    if self.estado == "jugando":
                        self.audio.reproducir("ui")
                        self.estado = "pausa"
                    elif self.estado == "pausa":
                        self.audio.reproducir("ui")
                        self.estado = "jugando"

                elif evento.key == pygame.K_SPACE and self.estado == "jugando":
                    self.jugador.pedir_salto()

                elif evento.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_x):
                    if self.estado == "jugando":
                        self.jugador.pedir_dash()

                elif evento.key == pygame.K_a and self.estado == "jugando":
                    if self.jugador.pedir_ataque():
                        self.audio.reproducir("ataque")
                        self.particulas.ataque(
                            self.jugador.rect.centerx,
                            self.jugador.rect.centery,
                            self.jugador.direccion,
                        )

                elif evento.key == pygame.K_RETURN:
                    if self.estado == "titulo":
                        self.audio.reproducir("ui")
                        self.iniciar_partida()
                    elif self.estado == "nivel_completado":
                        self.siguiente_nivel()
                    elif self.estado == "sala_completada":
                        self.abrir_selector_pruebas()
                    elif self.estado == "derrota" and self.sala_prueba:
                        self.cargar_sala_prueba(self.sala_prueba_indice)
                    elif self.estado in ("derrota", "victoria"):
                        self.reiniciar_juego()

            elif evento.type == pygame.KEYUP:
                if evento.key == pygame.K_SPACE and self.jugador is not None:
                    self.jugador.soltar_salto()

    # --- Función actualizar --- #
    def actualizar(self, dt):
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt)
        if self.aviso_jefe > 0:
            self.aviso_jefe = max(0.0, self.aviso_jefe - dt)

        if self.estado == "titulo":
            self.tiempo_titulo += dt
            return

        if self.mostrar_ayuda > 0:
            self.mostrar_ayuda = max(0.0, self.mostrar_ayuda - dt)

        if self.estado != "jugando":
            self.particulas.actualizar(dt)
            self.camara.actualizar_sacudida(dt)
            return

        self.tiempo_nivel += dt
        self.tiempo_total += dt

        self.actualizar_plataformas(dt)
        teclas = pygame.key.get_pressed()
        self.jugador.actualizar(dt, teclas, self.nivel.solidos_actuales())
        self.limitar_jugador()
        self.procesar_feedback_jugador()
        self.actualizar_ataque()

        if self.actualizar_jefe(dt):
            return

        if self.jugador.rect.top > self.nivel.alto + 120:
            self.perder_vida(ignorar_invulnerabilidad=True)
            return

        if self.actualizar_peligros():
            return

        self.actualizar_enemigos(dt)
        self.actualizar_almas()
        self.actualizar_palas()
        self.actualizar_power_ups_rango()
        self.particulas.actualizar(dt)
        self.camara.actualizar(self.jugador, self.nivel, dt)

        if self.jugador.rect.colliderect(self.nivel.meta):
            if self.jefe is not None and self.jefe.vivo:
                if self.aviso_jefe <= 0:
                    self.aviso_jefe = 2.2
                    self.audio.reproducir("ui")
                return

            self.audio.reproducir("meta")
            self.particulas.meta(self.nivel.meta.centerx, self.nivel.meta.centery)
            if self.sala_prueba:
                self.estado = "sala_completada"
            elif self.nivel_indice + 1 >= len(NIVELES):
                self.almas_totales += self.jugador.almas
                self.estado = "victoria"
            else:
                self.estado = "nivel_completado"

    # --- Función actualizar_plataformas --- #
    def actualizar_plataformas(self, dt):
        soporte = None
        if self.jugador.en_suelo:
            for plataforma in self.nivel.plataformas:
                rect = plataforma.rect
                if (
                    abs(self.jugador.rect.bottom - rect.top) <= 2
                    and self.jugador.rect.right > rect.left
                    and self.jugador.rect.left < rect.right
                ):
                    soporte = plataforma
                    break

        self.nivel.actualizar(dt)

        if soporte is not None:
            self.jugador.x += soporte.dx
            self.jugador.y += soporte.dy
            self.jugador.rect.x = round(self.jugador.x)
            self.jugador.rect.y = round(self.jugador.y)

    # --- Función limitar_jugador --- #
    def limitar_jugador(self):
        minimo = 0
        maximo = self.nivel.ancho - self.jugador.rect.width
        if self.jugador.rect.x < minimo:
            self.jugador.rect.x = minimo
            self.jugador.x = float(minimo)
            self.jugador.vx = 0.0
        elif self.jugador.rect.x > maximo:
            self.jugador.rect.x = maximo
            self.jugador.x = float(maximo)
            self.jugador.vx = 0.0

    # --- Función procesar_feedback_jugador --- #
    def procesar_feedback_jugador(self):
        if self.jugador.salto_recien:
            self.audio.reproducir("salto")
            self.particulas.salto(self.jugador.rect.centerx, self.jugador.rect.bottom)

        if self.jugador.dash_recien:
            self.audio.reproducir("dash")
            self.camara.sacudir(3.5, 0.10)

        if self.jugador.dash_tiempo > 0:
            self.particulas.dash(
                self.jugador.rect.centerx,
                self.jugador.rect.centery,
                self.jugador.dash_direccion,
            )

    # --- Función actualizar_ataque --- #
    def actualizar_ataque(self):
        if self.jugador.ataque_tiempo <= 0 or self.jugador.ataque_golpeado:
            return

        golpe = self.jugador.rect_ataque()

        # Enemigos normales.
        for enemigo in self.nivel.enemigos:
            if not enemigo.vivo or not golpe.colliderect(enemigo.rect):
                continue
            enemigo.vivo = False
            self.jugador.ataque_golpeado = True
            self.jugador.dash_usos_aire = DASH_USOS_AIRE
            self.jugador.dash_cooldown = 0.0
            self.audio.reproducir("pala")
            self.particulas.pala(enemigo.rect.centerx, enemigo.rect.centery)
            self.camara.sacudir(5.0, 0.12)
            self.flash = 0.06
            self.flash_color = AMARILLO
            break

        # Cuervos.
        if not self.jugador.ataque_golpeado:
            for cuervo in self.nivel.cuervos:
                if not cuervo.vivo or not golpe.colliderect(cuervo.rect):
                    continue
                cuervo.vivo = False
                self.jugador.ataque_golpeado = True
                self.jugador.dash_usos_aire = DASH_USOS_AIRE
                self.jugador.dash_cooldown = 0.0
                self.audio.reproducir("pala")
                self.particulas.pala(cuervo.rect.centerx, cuervo.rect.centery)
                self.camara.sacudir(5.0, 0.12)
                self.flash = 0.06
                self.flash_color = AMARILLO
                break

        # Polillas.
        if not self.jugador.ataque_golpeado:
            for polilla in self.nivel.polillas:
                if not polilla.vivo or not golpe.colliderect(polilla.rect):
                    continue
                polilla.vivo = False
                self.jugador.ataque_golpeado = True
                self.jugador.dash_usos_aire = DASH_USOS_AIRE
                self.jugador.dash_cooldown = 0.0
                self.audio.reproducir("pala")
                self.particulas.pala(polilla.rect.centerx, polilla.rect.centery)
                self.camara.sacudir(5.0, 0.12)
                self.flash = 0.06
                self.flash_color = AMARILLO
                break

        # Arañas.
        if not self.jugador.ataque_golpeado:
            for araña in self.nivel.aranias:
                if not araña.vivo or not golpe.colliderect(araña.rect):
                    continue
                araña.vivo = False
                self.jugador.ataque_golpeado = True
                self.jugador.dash_usos_aire = DASH_USOS_AIRE
                self.jugador.dash_cooldown = 0.0
                self.audio.reproducir("pala")
                self.particulas.pala(araña.rect.centerx, araña.rect.centery)
                self.camara.sacudir(5.0, 0.12)
                self.flash = 0.06
                self.flash_color = AMARILLO
                break

        # Jefe.
        if (
            not self.jugador.ataque_golpeado
            and self.jefe is not None
            and self.jefe.vulnerable
            and self.jefe.rect.colliderect(golpe)
        ):
            self.jugador.ataque_golpeado = True
            self.dañar_jefe()

    # --- Función actualizar_jefe --- #
    def actualizar_jefe(self, dt):
        if self.jefe is None:
            return False

        jefe = self.jefe
        jefe.actualizar(dt, self.jugador)

        if jefe.aviso_recien:
            self.audio.reproducir("jefe_aviso")
            self.camara.sacudir(3.0, 0.12)

        if jefe.ondas_recien:
            velocidad = JEFE_ONDA_VELOCIDAD + (jefe.fase - 1) * 45
            for direccion in (-1, 1):
                self.ondas_jefe.append(OndaCustodio(
                    jefe.rect.centerx + direccion * 24,
                    jefe.rect.bottom,
                    direccion,
                    velocidad,
                ))
            self.audio.reproducir("onda")
            self.camara.sacudir(8.0, 0.20)
            self.particulas.emitir(
                jefe.rect.centerx,
                jefe.rect.bottom - 4,
                16,
                (HUESO, CREMA, (126, 100, 68)),
                190,
                0.55,
                5,
                620,
            )

        for onda in self.ondas_jefe:
            onda.actualizar(dt)
            if (
                onda.viva
                and self.jugador.invulnerable <= 0
                and onda.rect.colliderect(self.jugador.rect)
            ):
                self.perder_vida()
                return True
        self.ondas_jefe = [onda for onda in self.ondas_jefe if onda.viva]

        if not jefe.vivo:
            return False

        if (
            jefe.vulnerable
            and self.jugador.ataque_tiempo > 0
            and not self.jugador.ataque_golpeado
            and jefe.rect.colliderect(self.jugador.rect_ataque())
        ):
            self.jugador.ataque_golpeado = True
            self.dañar_jefe()
            if not jefe.vivo:
                return False

        if self.jugador.rect.colliderect(jefe.rect):
            viene_desde_arriba = (
                self.jugador.vy > 0
                and self.jugador.rect.bottom - jefe.rect.top <= 20
            )
            if viene_desde_arriba and jefe.vulnerable:
                self.jugador.vy = -REBOTE_ENEMIGO
                self.jugador.en_suelo = False
                self.dañar_jefe()
            elif not jefe.vulnerable and self.jugador.invulnerable <= 0:
                self.perder_vida()
                return True

        if self.punto_reintento is None:
            limite = jefe.minimo_x - 3 * TILE
            if self.jugador.rect.right > limite:
                self.punto_reintento = (limite, self.nivel.spawn[1])
                self.mostrar_ayuda = 3.5
                self.audio.reproducir("ui")

        return False

    # --- Función dañar_jefe --- #
    def dañar_jefe(self):
        if not self.jefe.recibir_golpe():
            return False

        self.jugador.dash_usos_aire = DASH_USOS_AIRE
        self.jugador.dash_cooldown = 0.0
        self.audio.reproducir("pala")
        self.particulas.pala(self.jefe.rect.centerx, self.jefe.rect.centery)
        self.camara.sacudir(8.0, 0.18)
        self.flash = 0.10
        self.flash_color = AMARILLO

        if not self.jefe.vivo:
            self.audio.reproducir("meta")
            self.particulas.meta(self.jefe.rect.centerx, self.jefe.rect.centery)
            self.ondas_jefe = []
            self.aviso_jefe = 3.2
            self.flash = 0.22
        elif self.jefe.estado == "cambio":
            self.audio.reproducir("jefe_fase")
            self.camara.sacudir(11.0, 0.26)
            self.particulas.emitir(
                self.jefe.rect.centerx,
                self.jefe.rect.centery,
                24,
                (ORO, AMARILLO, HUESO),
                230,
                0.8,
                5,
                280,
            )
            self.aviso_jefe = 2.0

        return True

    # --- Función actualizar_peligros --- #
    def actualizar_peligros(self):
        if self.jugador.invulnerable > 0:
            return False
        for peligro in self.nivel.peligros:
            if self.jugador.rect.colliderect(peligro):
                self.perder_vida()
                return True
        return False

    # --- Función actualizar_enemigos --- #
    def actualizar_enemigos(self, dt):
        for enemigo in self.nivel.enemigos:
            enemigo.actualizar(dt)
            if not enemigo.vivo or not self.jugador.rect.colliderect(enemigo.rect):
                continue

            viene_desde_arriba = (
                self.jugador.vy > 0
                and self.jugador.rect.bottom - enemigo.rect.top <= 18
            )
            if viene_desde_arriba and self.jugador.tiene_pala:
                enemigo.vivo = False
                self.jugador.vy = -REBOTE_ENEMIGO
                self.jugador.en_suelo = False
                self.jugador.dash_usos_aire = DASH_USOS_AIRE
                self.jugador.dash_cooldown = 0.0
                self.audio.reproducir("pala")
                self.particulas.pala(enemigo.rect.centerx, enemigo.rect.centery)
                self.camara.sacudir(6.0, 0.14)
            else:
                self.perder_vida()
                return

        for enemigo_melee in self.nivel.enemigos_melee:
            enemigo_melee.actualizar(dt, self.jugador)

        for totem in self.nivel.totems:
            totem.actualizar(dt, self.jugador)

        # Cuervos: vuelo circular, daño por contacto.
        for cuervo in self.nivel.cuervos:
            cuervo.actualizar(dt)
            if (
                cuervo.vivo
                and self.jugador.invulnerable <= 0
                and self.jugador.rect.colliderect(cuervo.rect)
            ):
                self.perder_vida()
                return

        # Polillas: vuelo zigzag, daño por contacto.
        for polilla in self.nivel.polillas:
            polilla.actualizar(dt)
            if (
                polilla.vivo
                and self.jugador.invulnerable <= 0
                and self.jugador.rect.colliderect(polilla.rect)
            ):
                self.perder_vida()
                return

        # Arañas: patrullaje horizontal, daño por contacto.
        for araña in self.nivel.aranias:
            araña.actualizar(dt)
            if (
                araña.vivo
                and self.jugador.invulnerable <= 0
                and self.jugador.rect.colliderect(araña.rect)
            ):
                self.perder_vida()
                return

    # --- Función actualizar_almas --- #
    def actualizar_almas(self):
        for alma in self.nivel.almas:
            if alma.actualizar(self.jugador):
                self.audio.reproducir("alma")
                self.particulas.alma(alma.rect.centerx, alma.rect.centery)
                self.jugador.almas_para_vida += 1
                if self.jugador.almas_para_vida >= ALMAS_POR_VIDA:
                    self.jugador.almas_para_vida = 0
                    if self.jugador.vidas < VIDAS_MAXIMAS:
                        self.jugador.vidas += 1
                        self.audio.reproducir("vida_extra")
                        self.flash = 0.12
                        self.flash_color = AMARILLO
                        self.efecto_hud.iniciar("escala", 1.25, 0.2)

    # --- Función actualizar_palas --- #
    def actualizar_palas(self):
        for pala in self.nivel.palas:
            if pala.actualizar(self.jugador):
                self.audio.reproducir("pala_recoger")
                self.particulas.alma(pala.rect.centerx, pala.rect.centery)
                self.mostrar_ayuda = 2.5

    # --- Función actualizar_power_ups_rango --- #
    def actualizar_power_ups_rango(self):
        for power_up in self.nivel.power_ups_rango:
            if power_up.actualizar(self.jugador):
                self.audio.reproducir("alma")
                self.particulas.alma(
                    power_up.rect.centerx, power_up.rect.centery
                )
                self.mostrar_ayuda = 3.0

    # --- Función perder_vida --- #
    def perder_vida(self, ignorar_invulnerabilidad=False):
        if self.jugador.invulnerable > 0 and not ignorar_invulnerabilidad:
            return

        self.jugador.vidas -= 1
        self.audio.reproducir("daño")
        self.particulas.daño(self.jugador.rect.centerx, self.jugador.rect.centery)
        self.camara.sacudir(9.0, 0.22)
        self.flash = 0.16
        self.flash_color = ROJO

        if self.jugador.vidas <= 0:
            self.estado = "derrota"
            return

        self.jugador.almas = 0
        for alma in self.nivel.almas:
            alma.reiniciar()

        reaparicion = self.punto_reintento or self.nivel.spawn
        self.jugador.respawn(*reaparicion)
        if self.jefe is not None and self.jefe.vivo:
            self.jefe.reiniciar()
            self.ondas_jefe = []
        self.camara.actualizar(self.jugador, self.nivel, 1.0)

    # --- Función crear_fondo --- #
    def crear_fondo(self, tema):
        fondo = pygame.Surface((ANCHO, ALTO))
        if tema == "cripta":
            arriba, abajo = (8, 7, 14), (25, 20, 26)
        elif tema == "osario":
            arriba, abajo = (12, 5, 9), (34, 13, 17)
        else:
            arriba, abajo = (6, 8, 18), (22, 30, 42)

        for y in range(ALTO):
            proporcion = y / ALTO
            color = tuple(
                int(arriba[i] + (abajo[i] - arriba[i]) * proporcion)
                for i in range(3)
            )
            pygame.draw.line(fondo, color, (0, y), (ANCHO, y))

        if tema == "camposanto":
            pygame.draw.circle(fondo, (120, 116, 96), (790, 96), 55)
            pygame.draw.circle(fondo, (188, 180, 148), (790, 96), 44)
            pygame.draw.circle(fondo, (222, 214, 182), (790, 96), 33)
            pygame.draw.circle(fondo, (198, 190, 160), (776, 88), 6)
            pygame.draw.circle(fondo, (198, 190, 160), (804, 108), 4)
            estrellas = [
                (70, 55, 2), (140, 120, 1), (230, 45, 2), (310, 150, 1),
                (390, 70, 1), (470, 30, 2), (560, 130, 1), (640, 58, 2),
                (720, 170, 1), (880, 40, 2), (930, 140, 1), (180, 210, 1),
                (520, 200, 1), (840, 220, 1),
            ]
            for x, y, tamano in estrellas:
                pygame.draw.circle(fondo, (190, 200, 190), (x, y), tamano)
        elif tema == "cripta":
            # Ventanal gótico lejano.
            pygame.draw.rect(fondo, (16, 15, 22), (690, 40, 150, 230))
            pygame.draw.arc(fondo, (52, 50, 60), (680, 10, 170, 110), 0, math.pi, 8)
            pygame.draw.rect(fondo, (40, 52, 58), (706, 74, 118, 178))
            for x in range(716, 820, 26):
                pygame.draw.line(fondo, (20, 25, 30), (x, 80), (x, 248), 3)
            pygame.draw.line(fondo, (20, 25, 30), (706, 166), (824, 166), 3)
            pygame.draw.arc(fondo, (42, 58, 62), (700, 48, 130, 70), 0, math.pi, 4)
        else:
            pygame.draw.circle(fondo, (52, 16, 22), (780, 120), 80)
            pygame.draw.circle(fondo, (94, 26, 32), (780, 120), 54)
            pygame.draw.circle(fondo, (150, 48, 38), (780, 120), 28)
        return fondo

    # --- Función crear_vineta --- #
    def crear_vineta(self, fuerza):
        vineta = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        for i in range(24):
            margen_x = i * 22
            margen_y = i * 12
            alfa = int(fuerza * (1 - i / 24) ** 1.4)
            pygame.draw.ellipse(
                vineta,
                (0, 0, 0, max(0, min(255, alfa))),
                (
                    margen_x,
                    margen_y,
                    ANCHO - margen_x * 2,
                    ALTO - margen_y * 2,
                ),
            )
        return vineta

    # --- Función dibujar_fondo --- #
    def dibujar_fondo(self):
        tema = self.nivel.tema if self.nivel else "camposanto"
        if tema not in self.fondos:
            self.fondos[tema] = self.crear_fondo(tema)
        self.pantalla.blit(self.fondos[tema], (0, 0))

        if tema == "camposanto":
            self.dibujar_fondo_camposanto()
        elif tema == "cripta":
            self.dibujar_fondo_cripta()
        else:
            self.dibujar_fondo_osario()

        self.dibujar_niebla(tema)

    # --- Función dibujar_fondo_camposanto --- #
    def dibujar_fondo_camposanto(self):
        desplazamiento = int(self.camara.x * 0.16)

        # Luna llena con halo
        luna_x = 980 - int(self.camara.x * 0.04)
        luna_y = 72
        halo_luna = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_luna, (200, 200, 160, 18), (60, 60), 58)
        pygame.draw.circle(halo_luna, (220, 220, 180, 28), (60, 60), 42)
        self.pantalla.blit(halo_luna, (luna_x - 60, luna_y - 60))
        pygame.draw.circle(self.pantalla, (236, 230, 196), (luna_x, luna_y), 26)
        pygame.draw.circle(self.pantalla, (218, 210, 174), (luna_x + 6, luna_y - 4), 8)

        # Estrellas fijas (posiciones pseudo-aleatorias con seed fija)
        estrellas = [
            (88, 42), (142, 18), (240, 56), (310, 28), (418, 44),
            (520, 15), (620, 38), (730, 22), (840, 50), (1100, 32),
            (1160, 18), (1220, 44), (60, 70), (380, 62), (700, 55),
        ]
        ox = int(self.camara.x * 0.04) % 1280
        for sx, sy in estrellas:
            px = (sx - ox) % 1280
            pygame.draw.circle(self.pantalla, (220, 218, 200), (px, sy), 1)

        # Colinas traseras
        for i in range(-2, 8):
            x = i * 260 - desplazamiento
            pygame.draw.polygon(
                self.pantalla,
                (18, 26, 34),
                [(x, ALTO), (x + 180, 300), (x + 360, ALTO)],
            )
            pygame.draw.polygon(
                self.pantalla,
                (23, 34, 40),
                [(x + 90, ALTO), (x + 230, 340), (x + 380, ALTO)],
            )

        for base_x, escala in ((140, 1.15), (560, 0.9), (980, 1.25), (1320, 0.8)):
            x = (base_x - self.camara.x * 0.28) % (ANCHO + 420) - 180
            self.dibujar_arbol_muerto(x, ALTO - 92, escala)

        for i in range(-2, 15):
            x = i * 92 - int(self.camara.x * 0.48)
            self.dibujar_tumba_lejana(x, ALTO - 76, 0.8 + (i % 3) * 0.12)

    def dibujar_arbol_muerto(self, x, base_y, escala):
        alto = int(150 * escala)
        color = (12, 14, 18)
        pygame.draw.polygon(
            self.pantalla,
            color,
            [
                (x - 8 * escala, base_y),
                (x - 3 * escala, base_y - alto),
                (x + 5 * escala, base_y - alto),
                (x + 10 * escala, base_y),
            ],
        )
        for dx, dy, largo in ((-4, -0.55, 54), (3, -0.72, 66), (-1, -0.88, 44)):
            inicio = (x + dx * escala, base_y - alto * (-dy))
            pygame.draw.line(
                self.pantalla,
                color,
                inicio,
                (inicio[0] - largo * escala, inicio[1] - 26 * escala),
                max(2, int(4 * escala)),
            )
            pygame.draw.line(
                self.pantalla,
                color,
                (inicio[0] - largo * escala, inicio[1] - 26 * escala),
                (inicio[0] - largo * escala - 18 * escala, inicio[1] - 38 * escala),
                max(1, int(3 * escala)),
            )

    def dibujar_tumba_lejana(self, x, base_y, escala):
        ancho = int(22 * escala)
        alto = int(32 * escala)
        pygame.draw.rect(
            self.pantalla,
            (15, 19, 22),
            (x, base_y - alto, ancho, alto),
            border_radius=3,
        )
        pygame.draw.circle(
            self.pantalla,
            (15, 19, 22),
            (x + ancho // 2, base_y - alto),
            ancho // 2,
        )

    # --- Función dibujar_fondo_cripta --- #
    def dibujar_fondo_cripta(self):
        desplazamiento = int(self.camara.x * 0.25)
        for i in range(-2, 7):
            x = i * 230 - desplazamiento
            pygame.draw.rect(self.pantalla, (15, 14, 20), (x, 130, 54, ALTO - 130))
            pygame.draw.rect(self.pantalla, (34, 33, 42), (x + 6, 136, 42, ALTO - 136), 2)
            pygame.draw.rect(self.pantalla, (24, 23, 30), (x - 8, 120, 70, 14))
            pygame.draw.rect(self.pantalla, (24, 23, 30), (x - 4, 104, 62, 10))
            for y in range(160, ALTO, 48):
                pygame.draw.line(
                    self.pantalla,
                    (28, 27, 34),
                    (x + 8, y),
                    (x + 46, y),
                    1,
                )

        # Cadenas colgantes.
        for base_x, largo in ((210, 110), (470, 150), (760, 90), (1050, 170)):
            x = int(base_x - self.camara.x * 0.38) % (ANCHO + 240) - 120
            for y in range(0, largo, 12):
                pygame.draw.ellipse(
                    self.pantalla,
                    (42, 42, 50),
                    (x - 3, y, 6, 12),
                    1,
                )

        # Resplandor de velas lejanas.
        for base_x, base_y in ((150, 380), (520, 350), (850, 400)):
            x = base_x - int(self.camara.x * 0.5)
            pygame.draw.circle(self.pantalla, (58, 42, 18), (x, base_y), 18)
            pygame.draw.circle(self.pantalla, (112, 74, 28), (x, base_y), 8)

    # --- Función dibujar_fondo_osario --- #
    def dibujar_fondo_osario(self):
        desplazamiento = int(self.camara.x * 0.2)
        # Costillas gigantes.
        for i in range(-2, 7):
            x = i * 300 - desplazamiento
            pygame.draw.arc(
                self.pantalla,
                (54, 34, 34),
                (x, 150, 280, 320),
                3.14,
                6.28,
                9,
            )
            pygame.draw.arc(
                self.pantalla,
                (42, 28, 30),
                (x + 40, 190, 220, 280),
                3.14,
                6.28,
                5,
            )
        for base_x, largo in ((160, 130), (430, 190), (760, 120), (1010, 170)):
            x = int(base_x - self.camara.x * 0.35) % (ANCHO + 240) - 120
            pygame.draw.line(self.pantalla, (40, 28, 30), (x, 0), (x + 8, largo), 5)
            pygame.draw.line(self.pantalla, (40, 28, 30), (x + 8, largo), (x - 12, largo + 24), 3)
        pygame.draw.ellipse(self.pantalla, (58, 16, 20), (ANCHO // 2 - 260, ALTO - 100, 520, 120))

    # --- Función dibujar_niebla --- #
    def dibujar_niebla(self, tema):
        color = (92, 108, 116) if tema != "osario" else (72, 40, 42)
        for i in range(4):
            y = ALTO - 100 + i * 22
            alfa = 18 + i * 5
            banda = pygame.Surface((ANCHO, 30), pygame.SRCALPHA)
            banda.fill((*color, alfa))
            self.pantalla.blit(banda, (0, y))

    # --- Función dibujar_titulo --- #
    def dibujar_titulo(self):
        self.dibujar_fondo()
        self.dibujar_arbol_muerto(90, ALTO - 54, 1.5)
        self.dibujar_arbol_muerto(840, ALTO - 40, 1.1)
        self.dibujar_tumba_lejana(690, ALTO - 54, 1.3)
        self.dibujar_tumba_lejana(760, ALTO - 44, 0.9)
        self.pantalla.blit(self.vineta, (0, 0))

        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((4, 4, 8, 120))
        self.pantalla.blit(velo, (0, 0))

        self.dibujar_texto(TITULO, 0, 82, 92, ORO, centrado=True, sombra=True)
        self.dibujar_texto(SUBTITULO, 0, 172, 28, HUESO, centrado=True)
        pygame.draw.line(self.pantalla, SANGRE, (330, 212), (630, 212), 2)

        historia = (
            "El sepulturero bajó a la cripta a cumplir su jornada. "
            "La puerta se cerró detrás de él y la oscuridad despertó. "
            "Superá los obstáculos, enfrentá a los moradores y encontrá la salida."
        )
        self.dibujar_parrafo(historia, 0, 244, 22, CREMA, ancho=70, centrado=True, interlineado=30)

        self.dibujar_texto(EQUIPO, 0, 356, 22, AMARILLO, centrado=True)
        for i, nombre in enumerate(INTEGRANTES):
            self.dibujar_texto(nombre, 0, 386 + i * 24, 19, HUESO, centrado=True)

        self.dibujar_texto(
            "INSPIRADO EN " + " · ".join(REFERENCIAS).upper(),
            0,
            474,
            15,
            NIEBLA,
            centrado=True,
        )

        if int(self.tiempo_titulo * 2) % 2 == 0:
            self.dibujar_texto("ENTER PARA ENTRAR A LA CRIPTA", 0, 500, 22, TURQUESA, centrado=True)
        self.dibujar_texto("T: SALAS DE PRUEBA DEL PROFESOR", 0, 526, 15, HUD_ORO, centrado=True)

    # --- Función dibujar --- #
    def dibujar(self):
        if self.estado == "titulo":
            self.dibujar_titulo()
            return
        if self.estado == "test_selector":
            self.dibujar_selector_pruebas()
            return

        self.dibujar_fondo()
        self.nivel.dibujar(self.pantalla, self.camara)

        for enemigo in self.nivel.enemigos:
            enemigo.dibujar(self.pantalla, self.camara, pygame.time.get_ticks() / 1000)

        for onda in self.ondas_jefe:
            onda.dibujar(self.pantalla, self.camara, pygame.time.get_ticks() / 1000)
        if self.jefe is not None:
            self.jefe.dibujar(self.pantalla, self.camara, pygame.time.get_ticks() / 1000)

        self.jugador.dibujar(
            self.pantalla,
            self.camara,
            pygame.time.get_ticks() / 1000,
            pose=self.jugador.pose_actual(),
            con_pala=self.jugador.tiene_pala,
        )
        self.particulas.dibujar(self.pantalla, self.camara)
        self.pantalla.blit(self.vineta, (0, 0))
        self.dibujar_hud()

        if self.flash > 0:
            velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            alfa = int(110 * (self.flash / 0.16))
            velo.fill((*self.flash_color, max(0, min(255, alfa))))
            self.pantalla.blit(velo, (0, 0))

        if self.estado == "pausa":
            self.dibujar_overlay(
                "PAUSA",
                "P continuar · R reiniciar · M sonido · ESC salir",
            )
        elif self.estado == "nivel_completado":
            self.dibujar_overlay("LA CRIPTA SE ABRE", "ENTER para descender")
        elif self.estado == "sala_completada":
            self.dibujar_overlay(
                "TEST ROOM COMPLETADA",
                "ENTER para elegir otra sala · ESC para salir",
            )
        elif self.estado == "derrota":
            self.dibujar_overlay(
                "LA OSCURIDAD TE RECLAMA",
                "ENTER para volver a intentar · R para reiniciar",
            )
        elif self.estado == "victoria":
            self.dibujar_overlay(
                "¡ESCAPASTE DE LA CRIPTA!",
                f"Almas: {self.almas_totales} · Tiempo: {self.tiempo_total:04.1f}s",
            )

    # --- Función dibujar_hud --- #
    def dibujar_hud(self):
        # Paneles angostos (Fase 1 — 36px de alto)
        self.dibujar_panel_hud(pygame.Rect(HUD_ESQUINAS_X[0], HUD_ESQUINAS_Y[0], HUD_ESQUINAS_ANCHO[0], HUD_ANGOSTO_ALTO))
        self.dibujar_panel_hud(pygame.Rect(HUD_ESQUINAS_X[1], HUD_ESQUINAS_Y[1], HUD_ESQUINAS_ANCHO[1], HUD_ANGOSTO_ALTO))

        # Panel inferior para barras de cooldown
        panel_barras = pygame.Rect(680, 74, 300, 28)
        self.dibujar_panel_hud(panel_barras)

        # Arriba-izq: nivel y nombre (dentro del panel Y=12, alto=36)
        etiqueta = "TEST ROOM" if self.sala_prueba else f"NIVEL {self.nivel_indice + 1}/{len(NIVELES)}"
        self.dibujar_texto(etiqueta, 28, 16, 12, HUD_ORO)
        self.dibujar_texto(self.nivel.nombre.upper(), 28, 30, 16, HUD_TEXTO)

        # Arriba-der: almas (dentro del panel Y=12, alto=36)
        self.dibujar_icono_alma(492, 30)
        self.dibujar_texto(
            f"ALMAS {self.jugador.almas}/{self.nivel.total_almas}",
            510, 14, 16, HUD_ORO,
        )
        progreso_almas = self.jugador.almas_para_vida / ALMAS_POR_VIDA
        color_progreso = HUD_ORO if self.jugador.almas_para_vida >= 8 else HUD_MUTED
        self.dibujar_barra_hud(510, 34, 240, progreso_almas, color_progreso, segmentos=ALMAS_POR_VIDA)

        # Corazones: arriba-der del panel derecho (Y=16 centrado en el panel)
        for i in range(VIDAS_MAXIMAS):
            self.dibujar_corazon(724 + i * 23, 30, i < self.jugador.vidas)

        # Panel de cooldowns (abajo, centrado a la derecha)
        # Dash
        dash_listo = self.jugador.dash_listo()
        color_dash = HUD_VERDE if dash_listo else HUD_MUTED
        progreso_dash = 1.0 if dash_listo else 1.0 - min(
            1.0, self.jugador.dash_cooldown / DASH_COOLDOWN
        )
        self.dibujar_texto("DASH", 690, 80, 11, HUD_MUTED)
        self.dibujar_barra_hud(720, 82, 88, progreso_dash, color_dash)

        # Golpe de pala
        if self.jugador.tiene_pala:
            color_golpe = HUD_ORO if self.jugador.ataque_cooldown <= 0 else HUD_MUTED
            progreso_golpe = 1.0 - min(
                1.0, self.jugador.ataque_cooldown / ATAQUE_COOLDOWN
            )
            self.dibujar_texto("PALA", 820, 80, 11, HUD_MUTED)
            self.dibujar_barra_hud(852, 82, 80, progreso_golpe, color_golpe)
        else:
            self.dibujar_texto("PALA", 820, 80, 11, (45, 40, 50))
            self.dibujar_barra_hud(852, 82, 80, 0.0, (45, 40, 50))

        # Tiempo en la esquina superior izquierda del panel izquierdo
        self.dibujar_texto(f"{self.tiempo_nivel:04.1f}s", 268, 18, 11, HUD_MUTED)

        # Barra de jefe (solo en Nivel 3)
        if self.jefe is not None and self.jefe.vivo:
            self.dibujar_barra_jefe()

        if self.aviso_jefe > 0:
            texto = (
                "LA SALIDA ESTÁ SELLADA"
                if self.jefe is not None and self.jefe.vivo
                else "EL CUSTODIO CAYÓ · LA SALIDA SE ABRIÓ"
            )
            self.dibujar_texto(
                texto, 0, 142 if self.jefe is not None and self.jefe.vivo else 124,
                16, HUD_ORO, centrado=True, sombra=True,
            )

        if self.mostrar_ayuda > 0 and self.estado == "jugando":
            self.dibujar_pista()

    # --- Función dibujar_panel_hud --- #
    def dibujar_panel_hud(self, rect):
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, HUD_PANEL, (0, 0, rect.width, rect.height), border_radius=9)
        pygame.draw.rect(
            panel, (*HUD_BORDE, 160), (0, 0, rect.width, rect.height), 1, border_radius=9
        )
        pygame.draw.line(
            panel, (*HUD_ORO, 105), (12, 1), (rect.width - 12, 1), 1
        )
        for x, y, dx, dy in (
            (0, 0, 1, 1),
            (rect.width, 0, -1, 1),
            (0, rect.height, 1, -1),
            (rect.width, rect.height, -1, -1),
        ):
            pygame.draw.line(
                panel, (*HUD_ORO, 150), (x + 8 * dx, y), (x + 20 * dx, y), 1
            )
            pygame.draw.line(
                panel, (*HUD_ORO, 150), (x, y + 8 * dy), (x, y + 18 * dy), 1
            )
        self.pantalla.blit(panel, rect.topleft)

    # --- Función dibujar_barra_hud --- #
    def dibujar_barra_hud(self, x, y, ancho, progreso, color, segmentos=1):
        pygame.draw.rect(self.pantalla, (33, 27, 36), (x, y, ancho, 5), border_radius=3)
        if segmentos <= 1:
            pygame.draw.rect(
                self.pantalla,
                color,
                (x, y, int(ancho * max(0.0, min(1.0, progreso))), 5),
                border_radius=3,
            )
            return

        paso = ancho / segmentos
        for i in range(segmentos):
            celda = pygame.Rect(
                int(x + i * paso + 1),
                y,
                max(1, int(paso - 2)),
                5,
            )
            activo = (i + 1) / segmentos <= progreso + 0.001
            pygame.draw.rect(
                self.pantalla, color if activo else (45, 37, 44), celda, border_radius=2
            )

    # --- Función dibujar_icono_alma --- #
    def dibujar_icono_alma(self, x, y):
        # Halo exterior difuso
        halo = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(halo, (*HUD_ALMA, 40), (16, 16), 14)
        self.pantalla.blit(halo, (x - 16, y - 16))
        # Fondo oscuro
        pygame.draw.circle(self.pantalla, (38, 26, 54), (x, y), 10)
        # Rombo externo (alma)
        pygame.draw.polygon(
            self.pantalla,
            HUD_ALMA,
            [(x, y - 9), (x + 6, y), (x, y + 9), (x - 6, y)],
        )
        # Rombo interno (brillo)
        pygame.draw.polygon(
            self.pantalla,
            (220, 200, 255),
            [(x, y - 4), (x + 2, y), (x, y + 4), (x - 2, y)],
        )

    # --- Función dibujar_corazon --- #
    def dibujar_corazon(self, x, y, lleno):
        color_base = HUD_ROJO if lleno else (48, 34, 40)
        color_brillo = (240, 110, 120) if lleno else (60, 42, 50)
        color_sombra = (130, 28, 38) if lleno else (32, 22, 28)
        # Mitades superiores (dos círculos)
        pygame.draw.circle(self.pantalla, color_sombra, (x - 4, y + 1), 5)
        pygame.draw.circle(self.pantalla, color_sombra, (x + 4, y + 1), 5)
        pygame.draw.circle(self.pantalla, color_base, (x - 4, y), 5)
        pygame.draw.circle(self.pantalla, color_base, (x + 4, y), 5)
        # Triángulo inferior
        pygame.draw.polygon(
            self.pantalla,
            color_sombra,
            [(x - 9, y + 2), (x + 9, y + 2), (x, y + 13)],
        )
        pygame.draw.polygon(
            self.pantalla,
            color_base,
            [(x - 9, y + 1), (x + 9, y + 1), (x, y + 12)],
        )
        # Borde oscuro
        pygame.draw.polygon(
            self.pantalla,
            (*HUD_BORDE, 200),
            [(x - 9, y + 1), (x + 9, y + 1), (x, y + 12)],
            1,
        )
        # Destello (solo lleno)
        if lleno:
            pygame.draw.circle(self.pantalla, color_brillo, (x - 2, y - 2), 2)

    # --- Función dibujar_barra_jefe --- #
    def dibujar_barra_jefe(self):
        ancho = 430
        x = (ANCHO - ancho) // 2
        y = 90
        self.dibujar_panel_hud(pygame.Rect(x, y, ancho, 44))
        self.dibujar_texto("EL CUSTODIO DEL OSARIO", x + 14, y + 7, 14, HUD_ORO)
        self.dibujar_texto(
            f"FASE {self.jefe.fase}/3",
            x + ancho - 78, y + 7, 12, HUD_MUTED,
        )
        celda = 60
        for i in range(self.jefe.vida):
            rect = pygame.Rect(x + 14 + i * (celda + 5), y + 27, celda, 7)
            pygame.draw.rect(self.pantalla, HUD_ROJO, rect, border_radius=3)
        for i in range(self.jefe.vida, 6):
            rect = pygame.Rect(x + 14 + i * (celda + 5), y + 27, celda, 7)
            pygame.draw.rect(self.pantalla, (45, 31, 36), rect, border_radius=3)

    # --- Función dibujar_pista --- #
    def dibujar_pista(self):
        lineas = textwrap.wrap(self.nivel.pista, width=82)
        alto = 26 + 19 * len(lineas)
        x = (ANCHO - 780) // 2
        y = ALTO - alto - 16
        caja = pygame.Surface((780, alto), pygame.SRCALPHA)
        pygame.draw.rect(caja, HUD_PANEL_ALTO, (0, 0, 780, alto), border_radius=9)
        pygame.draw.rect(caja, (*HUD_BORDE, 170), (0, 0, 780, alto), 1, border_radius=9)
        pygame.draw.rect(caja, HUD_ORO, (0, 0, 4, alto), border_radius=2)
        self.pantalla.blit(caja, (x, y))
        self.dibujar_texto("PISTA", x + 18, y + 7, 14, HUD_ORO)
        for i, linea in enumerate(lineas):
            self.dibujar_texto(linea, x + 18, y + 26 + i * 19, 16, HUD_TEXTO)

    # --- Función dibujar_selector_pruebas --- #
    def dibujar_selector_pruebas(self):
        self.dibujar_fondo()
        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((4, 4, 8, 190))
        self.pantalla.blit(velo, (0, 0))

        self.dibujar_texto("SALAS DE PRUEBA", 0, 58, 46, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto(
            "Mecánicas aisladas para evaluación",
            0, 102, 18, HUD_MUTED, centrado=True,
        )

        for i, sala in enumerate(SALAS_PRUEBA):
            rect = pygame.Rect(150, 138 + i * 104, 660, 88)
            self.dibujar_panel_hud(rect)
            if i == self.test_opcion:
                pygame.draw.rect(
                    self.pantalla, HUD_ORO,
                    (rect.x, rect.y, rect.width, rect.height), 2, border_radius=9,
                )
                pygame.draw.rect(
                    self.pantalla, HUD_ORO,
                    (rect.x, rect.y + 10, 4, rect.height - 20), border_radius=2,
                )
            self.dibujar_texto(f"{i + 1}", rect.x + 18, rect.y + 19, 28, HUD_ORO)
            self.dibujar_texto(sala["nombre"], rect.x + 56, rect.y + 12, 22, HUD_TEXTO)
            lineas = textwrap.wrap(sala["pista"], width=88)
            for j, linea in enumerate(lineas[:2]):
                self.dibujar_texto(
                    linea, rect.x + 56, rect.y + 42 + j * 18, 14, HUD_MUTED,
                )

        self.dibujar_texto(
            "FLECHAS elegir · ENTER entrar · 1/2/3 directo · ESC volver",
            0, 478, 16, HUD_TEXTO, centrado=True,
        )
        self.dibujar_texto(
            "El profesor puede probar cada mecánica sin recorrer la campaña.",
            0, 505, 13, HUD_MUTED, centrado=True,
        )

    # --- Función dibujar_overlay --- #
    def dibujar_overlay(self, titulo, subtitulo):
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill(SOMBRA)
        self.pantalla.blit(overlay, (0, 0))
        self.dibujar_texto(titulo, 0, ALTO // 2 - 62, 46, ORO, centrado=True, sombra=True)
        self.dibujar_parrafo(
            subtitulo,
            0,
            ALTO // 2 + 14,
            23,
            HUESO,
            ancho=58,
            centrado=True,
            interlineado=30,
        )

    # --- Función dibujar_texto --- #
    def dibujar_texto(self, texto, x, y, tamano=24, color=BLANCO, centrado=False, sombra=False):
        if tamano not in self.fuentes:
            try:
                self.fuentes[tamano] = pygame.font.Font(self._ruta_fuente_gotica, tamano)
            except Exception:
                self.fuentes[tamano] = pygame.font.Font(None, tamano)

        if sombra:
            imagen_sombra = self.fuentes[tamano].render(texto, True, NEGRO)
            rect_sombra = imagen_sombra.get_rect()
            if centrado:
                rect_sombra.center = (ANCHO // 2 + 3, y + 3)
            else:
                rect_sombra.topleft = (x + 3, y + 3)
            self.pantalla.blit(imagen_sombra, rect_sombra)

        imagen = self.fuentes[tamano].render(texto, True, color)
        rect = imagen.get_rect()
        if centrado:
            rect.center = (ANCHO // 2, y)
        else:
            rect.topleft = (x, y)
        self.pantalla.blit(imagen, rect)

    # --- Función dibujar_parrafo --- #
    def dibujar_parrafo(self, texto, x, y, tamano, color, ancho=70, centrado=False, interlineado=24):
        lineas = textwrap.wrap(texto, width=ancho)
        for i, linea in enumerate(lineas):
            self.dibujar_texto(
                linea,
                x,
                y + i * interlineado,
                tamano,
                color,
                centrado=centrado,
            )

    # --- Función run --- #
    def run(self):
        while self.corriendo:
            dt = min(self.reloj.tick(FPS) / 1000, MAX_DT)
            self.procesar_eventos()
            self.actualizar(dt)
            self.dibujar()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


# --- Arranque directo --- #
if __name__ == "__main__":
    Juego().run()
