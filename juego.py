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
    VIRTUAL_ALTO,
    VIRTUAL_ANCHO,
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
        self.menu_opcion = 0
        self.nivel_seleccionado = 0
        self.tiempo_menu = 0.0
        self.superficie_mundo = pygame.Surface((VIRTUAL_ANCHO, VIRTUAL_ALTO))

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

    # --- Función abrir_menu --- #
    def abrir_menu(self):
        self.estado = "menu"
        self.menu_opcion = 0
        self.audio.reproducir("ui")

    # --- Función abrir_seleccion_nivel --- #
    def abrir_seleccion_nivel(self):
        self.estado = "seleccion_nivel"
        self.nivel_seleccionado = self.nivel_indice
        self.audio.reproducir("ui")

    # --- Función abrir_creditos --- #
    def abrir_creditos(self):
        self.estado = "creditos"
        self.audio.reproducir("ui")

    # --- Función seleccionar_nivel --- #
    def seleccionar_nivel(self, indice):
        self.almas_totales = 0
        self.tiempo_total = 0.0
        self.cargar_nivel(indice, vidas=VIDAS_INICIALES)
        self.estado = "jugando"

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
                if self.estado == "menu":
                    if evento.key in (pygame.K_UP, pygame.K_w):
                        self.menu_opcion = (self.menu_opcion - 1) % 3
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_opcion = (self.menu_opcion + 1) % 3
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.reproducir("ui")
                        if self.menu_opcion == 0:
                            self.iniciar_partida()
                        elif self.menu_opcion == 1:
                            self.abrir_seleccion_nivel()
                        elif self.menu_opcion == 2:
                            self.abrir_creditos()
                    elif evento.key == pygame.K_ESCAPE:
                        self.estado = "titulo"
                        self.audio.reproducir("ui")
                    continue

                elif self.estado == "seleccion_nivel":
                    if evento.key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
                        self.nivel_seleccionado = (self.nivel_seleccionado - 1) % len(NIVELES)
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d):
                        self.nivel_seleccionado = (self.nivel_seleccionado + 1) % len(NIVELES)
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.reproducir("ui")
                        self.seleccionar_nivel(self.nivel_seleccionado)
                    elif evento.key == pygame.K_ESCAPE:
                        self.abrir_menu()
                    continue

                elif self.estado == "creditos":
                    if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        self.abrir_menu()
                    continue

                elif self.estado == "test_selector":
                    if evento.key == pygame.K_ESCAPE:
                        self.abrir_menu()
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
                    if self.estado == "jugando":
                        self.audio.reproducir("ui")
                        self.estado = "pausa"
                    elif self.estado == "pausa":
                        self.abrir_menu()
                    elif self.estado in ("derrota", "victoria"):
                        self.abrir_menu()
                    elif self.estado == "titulo":
                        self.corriendo = False
                    else:
                        self.abrir_menu()

                elif evento.key == pygame.K_m:
                    self.audio.alternar()

                elif evento.key == pygame.K_r and self.estado not in ("titulo", "menu", "seleccion_nivel", "creditos"):
                    if self.sala_prueba:
                        self.cargar_sala_prueba(self.sala_prueba_indice)
                    else:
                        self.reiniciar_juego()

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
                        self.abrir_menu()
                    elif self.estado == "nivel_completado":
                        self.siguiente_nivel()
                    elif self.estado == "sala_completada":
                        self.abrir_menu()
                    elif self.estado == "derrota" and self.sala_prueba:
                        self.cargar_sala_prueba(self.sala_prueba_indice)
                    elif self.estado in ("derrota", "victoria"):
                        self.abrir_menu()

            elif evento.type == pygame.KEYUP:
                if evento.key == pygame.K_SPACE and self.jugador is not None:
                    self.jugador.soltar_salto()

    # --- Función actualizar --- #
    def actualizar(self, dt):
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt)
        if self.aviso_jefe > 0:
            self.aviso_jefe = max(0.0, self.aviso_jefe - dt)

        if self.estado in ("titulo", "menu", "seleccion_nivel", "creditos"):
            self.tiempo_titulo += dt
            self.tiempo_menu += dt
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

        # Enemigos Melee.
        if not self.jugador.ataque_golpeado:
            for enemigo_melee in self.nivel.enemigos_melee:
                if not enemigo_melee.vivo or not golpe.colliderect(enemigo_melee.rect):
                    continue
                enemigo_melee.vivo = False
                self.jugador.ataque_golpeado = True
                self.jugador.dash_usos_aire = DASH_USOS_AIRE
                self.jugador.dash_cooldown = 0.0
                self.audio.reproducir("pala")
                self.particulas.pala(enemigo_melee.rect.centerx, enemigo_melee.rect.centery)
                self.camara.sacudir(5.0, 0.12)
                self.flash = 0.06
                self.flash_color = AMARILLO
                break

        # Jefe — pala: solo daña en Fase 1 (y con vulnerable=True)
        if (
            not self.jugador.ataque_golpeado
            and self.jefe is not None
            and self.jefe.vulnerable
            and self.jefe.rect.colliderect(golpe)
        ):
            self.jugador.ataque_golpeado = True
            self.dañar_jefe_pala()

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
            # Fase 2: triple onda (izq, der + central lenta)
            direcciones = (-1, 1)
            for direccion in direcciones:
                self.ondas_jefe.append(OndaCustodio(
                    jefe.rect.centerx + direccion * 24,
                    jefe.rect.bottom,
                    direccion,
                    velocidad,
                ))
            if jefe.fase >= 2:
                # Tercera onda central (se expande despacio)
                self.ondas_jefe.append(OndaCustodio(
                    jefe.rect.centerx,
                    jefe.rect.bottom,
                    0,
                    velocidad * 0.55,
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
            self.dañar_jefe_pala()
            if not jefe.vivo:
                return False

        if self.jugador.rect.colliderect(jefe.rect):
            viene_desde_arriba = (
                self.jugador.vy > 0
                and self.jugador.rect.bottom - jefe.rect.top <= 20
            )
            if viene_desde_arriba:
                # Pisotón: funciona siempre (Fase 1 y 2), sin chequear vulnerable
                self.jugador.vy = -REBOTE_ENEMIGO
                self.jugador.en_suelo = False
                self.dañar_jefe_pisaton()
            elif self.jugador.invulnerable <= 0:
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
        """Golpe de pala: requiere vulnerable y solo funciona en Fase 1."""
        if not self.jefe.recibir_golpe():
            return False
        return self._aplicar_golpe_jefe()

    # --- Función dañar_jefe_pala --- #
    def dañar_jefe_pala(self):
        """Golpe de pala: requiere vulnerable y solo funciona en Fase 1."""
        if not self.jefe.recibir_golpe_pala():
            # Fase 2: pala rebota — efecto visual de rechazo
            self.camara.sacudir(3.0, 0.08)
            self.flash = 0.05
            self.flash_color = (180, 60, 60)
            return False
        return self._aplicar_golpe_jefe()

    # --- Función dañar_jefe_pisaton --- #
    def dañar_jefe_pisaton(self):
        """Pisotón: siempre funciona en ambas fases."""
        if not self.jefe.recibir_pisaton():
            return False
        return self._aplicar_golpe_jefe()

    # --- Función _aplicar_golpe_jefe (efectos comunes) --- #
    def _aplicar_golpe_jefe(self):
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
            if (
                enemigo_melee.vivo
                and self.jugador.invulnerable <= 0
                and self.jugador.rect.colliderect(enemigo_melee.rect)
            ):
                viene_desde_arriba = (
                    self.jugador.vy > 0
                    and self.jugador.rect.bottom - enemigo_melee.rect.top <= 18
                )
                if viene_desde_arriba and self.jugador.tiene_pala:
                    enemigo_melee.vivo = False
                    self.jugador.vy = -REBOTE_ENEMIGO
                    self.jugador.en_suelo = False
                    self.jugador.dash_usos_aire = DASH_USOS_AIRE
                    self.jugador.dash_cooldown = 0.0
                    self.audio.reproducir("pala")
                    self.particulas.pala(enemigo_melee.rect.centerx, enemigo_melee.rect.centery)
                    self.camara.sacudir(6.0, 0.14)
                else:
                    self.perder_vida()
                    return

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
    def crear_fondo(self, tema, w=ANCHO, h=ALTO):
        fondo = pygame.Surface((w, h))
        if tema == "cripta":
            arriba, abajo = (8, 7, 14), (25, 20, 26)
        elif tema == "osario":
            arriba, abajo = (12, 5, 9), (34, 13, 17)
        else:
            arriba, abajo = (6, 8, 18), (22, 30, 42)

        for y in range(h):
            proporcion = y / h
            color = tuple(
                int(arriba[i] + (abajo[i] - arriba[i]) * proporcion)
                for i in range(3)
            )
            pygame.draw.line(fondo, color, (0, y), (w, y))

        if tema == "camposanto":
            luna_x = int(w * 0.78)
            pygame.draw.circle(fondo, (120, 116, 96), (luna_x, 96), 55)
            pygame.draw.circle(fondo, (188, 180, 148), (luna_x, 96), 44)
            pygame.draw.circle(fondo, (222, 214, 182), (luna_x, 96), 33)
            pygame.draw.circle(fondo, (198, 190, 160), (luna_x - 14, 88), 6)
            pygame.draw.circle(fondo, (198, 190, 160), (luna_x + 14, 108), 4)
            estrellas = [
                (70, 55, 2), (140, 120, 1), (230, 45, 2), (310, 150, 1),
                (390, 70, 1), (470, 30, 2), (560, 130, 1), (640, 58, 2),
                (720, 170, 1), (880, 40, 2), (930, 140, 1), (180, 210, 1),
                (520, 200, 1), (840, 220, 1),
            ]
            for sx, sy, tamano in estrellas:
                if sx < w and sy < h:
                    pygame.draw.circle(fondo, (190, 200, 190), (sx, sy), tamano)
        elif tema == "cripta":
            vx = int(w * 0.68)
            pygame.draw.rect(fondo, (16, 15, 22), (vx, 40, 150, 230))
            pygame.draw.arc(fondo, (52, 50, 60), (vx - 10, 10, 170, 110), 0, math.pi, 8)
            pygame.draw.rect(fondo, (40, 52, 58), (vx + 16, 74, 118, 178))
            for x in range(vx + 26, vx + 130, 26):
                pygame.draw.line(fondo, (20, 25, 30), (x, 80), (x, 248), 3)
            pygame.draw.line(fondo, (20, 25, 30), (vx + 16, 166), (vx + 134, 166), 3)
            pygame.draw.arc(fondo, (42, 58, 62), (vx + 10, 48, 130, 70), 0, math.pi, 4)
        else:
            cx = int(w * 0.76)
            pygame.draw.circle(fondo, (52, 16, 22), (cx, 120), 80)
            pygame.draw.circle(fondo, (94, 26, 32), (cx, 120), 54)
            pygame.draw.circle(fondo, (150, 48, 38), (cx, 120), 28)
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
    def dibujar_fondo(self, destino=None):
        if destino is None:
            destino = self.pantalla
        w = destino.get_width()
        h = destino.get_height()
        tema = self.nivel.tema if self.nivel else "camposanto"
        clave = (tema, w, h)
        if clave not in self.fondos:
            self.fondos[clave] = self.crear_fondo(tema, w, h)
        destino.blit(self.fondos[clave], (0, 0))

        if tema == "camposanto":
            self.dibujar_fondo_camposanto(destino)
        elif tema == "cripta":
            self.dibujar_fondo_cripta(destino)
        else:
            self.dibujar_fondo_osario(destino)

        self.dibujar_niebla(destino, tema)

    # --- Función dibujar_fondo_camposanto --- #
    def dibujar_fondo_camposanto(self, destino=None):
        if destino is None:
            destino = self.pantalla
        w, h = destino.get_width(), destino.get_height()
        desplazamiento = int(self.camara.x * 0.16)

        # Luna llena con halo
        luna_x = int(w * 0.78) - int(self.camara.x * 0.04)
        luna_y = 72
        halo_luna = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_luna, (200, 200, 160, 18), (60, 60), 58)
        pygame.draw.circle(halo_luna, (220, 220, 180, 28), (60, 60), 42)
        destino.blit(halo_luna, (luna_x - 60, luna_y - 60))
        pygame.draw.circle(destino, (236, 230, 196), (luna_x, luna_y), 26)
        pygame.draw.circle(destino, (218, 210, 174), (luna_x + 6, luna_y - 4), 8)

        # Estrellas fijas
        estrellas = [
            (88, 42), (142, 18), (240, 56), (310, 28), (418, 44),
            (520, 15), (620, 38), (730, 22), (840, 50), (1100, 32),
            (1160, 18), (1220, 44), (60, 70), (380, 62), (700, 55),
        ]
        ox = int(self.camara.x * 0.04) % w
        for sx, sy in estrellas:
            px = (sx - ox) % w
            if sy < h:
                pygame.draw.circle(destino, (220, 218, 200), (px, sy), 1)

        # Colinas traseras
        for i in range(-2, 10):
            x = i * 260 - desplazamiento
            pygame.draw.polygon(
                destino,
                (18, 26, 34),
                [(x, h), (x + 180, int(h * 0.52) + 32), (x + 360, h)],
            )
            pygame.draw.polygon(
                destino,
                (23, 34, 40),
                [(x + 90, h), (x + 230, int(h * 0.58) + 32), (x + 380, h)],
            )

        for base_x, escala in ((140, 1.15), (560, 0.9), (980, 1.25), (1320, 0.8)):
            x = (base_x - self.camara.x * 0.28) % (w + 420) - 180
            self.dibujar_arbol_muerto(destino, x, h - 60, escala)

        for i in range(-2, 18):
            x = i * 92 - int(self.camara.x * 0.48)
            self.dibujar_tumba_lejana(destino, x, h - 44, 0.8 + (i % 3) * 0.12)

    def dibujar_arbol_muerto(self, destino, x, base_y, escala):
        alto = int(150 * escala)
        color = (12, 14, 18)
        pygame.draw.polygon(
            destino,
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
                destino,
                color,
                inicio,
                (inicio[0] - largo * escala, inicio[1] - 26 * escala),
                max(2, int(4 * escala)),
            )

    def dibujar_tumba_lejana(self, destino, x, base_y, escala):
        ancho = int(22 * escala)
        alto = int(32 * escala)
        pygame.draw.rect(
            destino,
            (15, 19, 22),
            (x, base_y - alto, ancho, alto),
            border_radius=3,
        )
        pygame.draw.circle(
            destino,
            (15, 19, 22),
            (x + ancho // 2, base_y - alto),
            ancho // 2,
        )

    def dibujar_fondo_cripta(self, destino=None):
        if destino is None:
            destino = self.pantalla
        w, h = destino.get_width(), destino.get_height()
        desplazamiento = int(self.camara.x * 0.25)
        for i in range(-2, 8):
            x = i * 230 - desplazamiento
            pygame.draw.rect(destino, (15, 14, 20), (x, 162, 54, h - 162))
            pygame.draw.rect(destino, (34, 33, 42), (x + 6, 168, 42, h - 168), 2)
            pygame.draw.rect(destino, (24, 23, 30), (x - 8, 152, 70, 14))
            pygame.draw.rect(destino, (24, 23, 30), (x - 4, 136, 62, 10))
            for y in range(192, h, 48):
                pygame.draw.line(destino, (28, 27, 34), (x + 8, y), (x + 46, y), 1)

        # Cadenas colgantes
        for base_x, largo in ((210, 110), (470, 150), (760, 90), (1050, 170)):
            x = int(base_x - self.camara.x * 0.38) % (w + 240) - 120
            for y in range(0, largo, 12):
                pygame.draw.ellipse(destino, (42, 42, 50), (x - 3, y, 6, 12), 1)

        # Resplandor de velas lejanas
        for base_x, base_y in ((150, h - 158), (520, h - 188), (850, h - 138)):
            x = base_x - int(self.camara.x * 0.5)
            pygame.draw.circle(destino, (58, 42, 18), (x, base_y), 18)
            pygame.draw.circle(destino, (112, 74, 28), (x, base_y), 8)

    def dibujar_fondo_osario(self, destino=None):
        if destino is None:
            destino = self.pantalla
        w, h = destino.get_width(), destino.get_height()
        desplazamiento = int(self.camara.x * 0.2)
        for i in range(-2, 8):
            x = i * 300 - desplazamiento
            pygame.draw.arc(destino, (54, 34, 34), (x, 182, 280, 320), 3.14, 6.28, 9)
            pygame.draw.arc(destino, (42, 28, 30), (x + 40, 222, 220, 280), 3.14, 6.28, 5)
        for base_x, largo in ((160, 130), (430, 190), (760, 120), (1010, 170)):
            x = int(base_x - self.camara.x * 0.35) % (w + 240) - 120
            pygame.draw.line(destino, (40, 28, 30), (x, 0), (x + 8, largo), 5)
            pygame.draw.line(destino, (40, 28, 30), (x + 8, largo), (x - 12, largo + 24), 3)
        pygame.draw.ellipse(destino, (58, 16, 20), (w // 2 - 260, h - 68, 520, 120))

    def dibujar_niebla(self, destino=None, tema="camposanto"):
        if destino is None:
            destino = self.pantalla
        w, h = destino.get_width(), destino.get_height()
        color = (92, 108, 116) if tema != "osario" else (72, 40, 42)
        for i in range(4):
            y = h - 68 + i * 22
            alfa = 18 + i * 5
            banda = pygame.Surface((w, 30), pygame.SRCALPHA)
            banda.fill((*color, alfa))
            destino.blit(banda, (0, y))

    # --- Función dibujar_titulo (Intro) --- #
    def dibujar_titulo(self):
        self.dibujar_fondo(self.pantalla)
        self.dibujar_arbol_muerto(self.pantalla, 90, ALTO - 54, 1.5)
        self.dibujar_arbol_muerto(self.pantalla, 1100, ALTO - 40, 1.1)
        self.dibujar_tumba_lejana(self.pantalla, 950, ALTO - 54, 1.3)
        self.dibujar_tumba_lejana(self.pantalla, 1020, ALTO - 44, 0.9)
        self.pantalla.blit(self.vineta, (0, 0))

        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((4, 4, 8, 140))
        self.pantalla.blit(velo, (0, 0))

        # Título y ambientación
        self.dibujar_texto(TITULO, 0, 110, 88, ORO, centrado=True, sombra=True)
        self.dibujar_texto(SUBTITULO, 0, 206, 26, HUESO, centrado=True)
        pygame.draw.line(self.pantalla, SANGRE, (ANCHO // 2 - 180, 248), (ANCHO // 2 + 180, 248), 2)

        historia = (
            "El sepulturero bajó a la cripta a cumplir su jornada. "
            "La puerta de hierro se cerró a sus espaldas y la oscuridad despertó. "
            "Con su pala y su farol de sombra, debe hallar la salida antes de que la muerte lo alcance."
        )
        self.dibujar_parrafo(historia, 0, 280, 20, CREMA, ancho=76, centrado=True, interlineado=28)

        # Prompt de avance
        pulso = 0.5 + 0.5 * math.sin(self.tiempo_titulo * 4)
        alfa_prompt = int(170 + pulso * 85)
        color_prompt = (int(TURQUESA[0] * (alfa_prompt / 255)), int(TURQUESA[1] * (alfa_prompt / 255)), int(TURQUESA[2] * (alfa_prompt / 255)))
        self.dibujar_texto("PRESIONÁ ENTER PARA CONTINUAR", 0, 560, 22, color_prompt, centrado=True, sombra=True)

    # --- Función dibujar_menu_principal --- #
    def dibujar_menu_principal(self):
        self.dibujar_fondo(self.pantalla)
        self.pantalla.blit(self.vineta, (0, 0))

        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((5, 4, 10, 165))
        self.pantalla.blit(velo, (0, 0))

        # Encabezado
        self.dibujar_texto(TITULO, 0, 72, 72, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto("PLATAFORMERO GÓTICO 2D", 0, 154, 18, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 140), (ANCHO // 2 - 140, 185), (ANCHO // 2 + 140, 185), 1)

        # Opciones del menú
        opciones = [
            ("JUGAR", "Comenzar la travesía desde el Camposanto"),
            ("SELECCIÓN DE PANTALLA", "Elegir nivel para descender a la cripta"),
            ("CRÉDITOS", "Equipo de desarrollo y referencias"),
        ]

        ancho_caja = 560
        alto_caja = 64
        x_caja = (ANCHO - ancho_caja) // 2
        y_base = 240

        for i, (titulo_op, subtitulo_op) in enumerate(opciones):
            y_caja = y_base + i * 94
            rect = pygame.Rect(x_caja, y_caja, ancho_caja, alto_caja)
            seleccionada = (i == self.menu_opcion)

            # Fondo de la opción
            surf_op = pygame.Surface((ancho_caja, alto_caja), pygame.SRCALPHA)
            color_fondo = (28, 22, 34, 230) if seleccionada else (16, 13, 20, 180)
            pygame.draw.rect(surf_op, color_fondo, (0, 0, ancho_caja, alto_caja), border_radius=8)

            color_borde = HUD_ORO if seleccionada else (*HUD_BORDE, 150)
            grosor_borde = 2 if seleccionada else 1
            pygame.draw.rect(surf_op, color_borde, (0, 0, ancho_caja, alto_caja), grosor_borde, border_radius=8)

            # Detalles ornamentales en opción activa
            if seleccionada:
                # Resaltador lateral dorado
                pygame.draw.rect(surf_op, HUD_ORO, (0, 8, 4, alto_caja - 16), border_radius=2)
                # Remates en esquinas
                for ex, ey, edx, edy in ((0, 0, 1, 1), (ancho_caja, 0, -1, 1), (0, alto_caja, 1, -1), (ancho_caja, alto_caja, -1, -1)):
                    pygame.draw.line(surf_op, HUD_ORO, (ex + 6 * edx, ey), (ex + 16 * edx, ey), 1)
                    pygame.draw.line(surf_op, HUD_ORO, (ex, ey + 6 * edy), (ex, ey + 14 * edy), 1)

            self.pantalla.blit(surf_op, (x_caja, y_caja))

            # Textos de la opción
            color_titulo = HUD_ORO if seleccionada else HUD_TEXTO
            prefijo = "▸  " if seleccionada else "   "
            self.dibujar_texto(prefijo + titulo_op, x_caja + 24, y_caja + 12, 22, color_titulo, sombra=seleccionada)
            self.dibujar_texto(subtitulo_op, x_caja + 48, y_caja + 38, 13, HUD_MUTED if not seleccionada else CREMA)

        # Pie de página instructivo
        self.dibujar_texto(
            "FLECHAS / WASD: ELEGIR · ENTER: SELECCIONAR · ESC: SALIR",
            0, 620, 14, HUD_MUTED, centrado=True,
        )

    # --- Función dibujar_seleccion_nivel --- #
    def dibujar_seleccion_nivel(self):
        self.dibujar_fondo(self.pantalla)
        self.pantalla.blit(self.vineta, (0, 0))

        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((5, 4, 10, 175))
        self.pantalla.blit(velo, (0, 0))

        # Título
        self.dibujar_texto("SELECCIÓN DE PANTALLA", 0, 52, 54, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto("Elegí el nivel para descender a la oscuridad", 0, 114, 16, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 120), (ANCHO // 2 - 160, 142), (ANCHO // 2 + 160, 142), 1)

        datos_niveles = [
            (
                "NIVEL I · EL CAMPOSANTO",
                "160 columnas · Salto de precisión y dash de sombra",
                "Arranque melancólico bajo la luna llena. Los arcos de almas marcan la trayectoria.",
                "CAMPOSANTO",
            ),
            (
                "NIVEL II · LA CRIPTA",
                "130 columnas · Recogida de pala y el salto de la ventana",
                "Fosos oscuros, la pala del sepulturero y el desafío final: saltar por la pared alta.",
                "CRIPTA",
            ),
            (
                "NIVEL III · EL OSARIO",
                "160 columnas · Guadaña imperial y el Custodio en 2 fases",
                "El clímax final en 5 actos: power-up de rango ampliado, centinelas y batalla de jefe.",
                "OSARIO",
            ),
        ]

        ancho_tarjeta = 760
        alto_tarjeta = 110
        x_tarjeta = (ANCHO - ancho_tarjeta) // 2
        y_base = 180

        for i, (titulo_n, subtitulo_n, desc_n, tema_n) in enumerate(datos_niveles):
            y_tarjeta = y_base + i * 134
            seleccionada = (i == self.nivel_seleccionado)

            surf_tarjeta = pygame.Surface((ancho_tarjeta, alto_tarjeta), pygame.SRCALPHA)
            color_fondo = (28, 20, 36, 235) if seleccionada else (16, 12, 22, 185)
            pygame.draw.rect(surf_tarjeta, color_fondo, (0, 0, ancho_tarjeta, alto_tarjeta), border_radius=10)

            color_borde = HUD_ORO if seleccionada else (*HUD_BORDE, 160)
            grosor = 2 if seleccionada else 1
            pygame.draw.rect(surf_tarjeta, color_borde, (0, 0, ancho_tarjeta, alto_tarjeta), grosor, border_radius=10)

            if seleccionada:
                pygame.draw.rect(surf_tarjeta, HUD_ORO, (0, 10, 5, alto_tarjeta - 20), border_radius=2)
                # Remates en las 4 esquinas
                for ex, ey, edx, edy in ((0, 0, 1, 1), (ancho_tarjeta, 0, -1, 1), (0, alto_tarjeta, 1, -1), (ancho_tarjeta, alto_tarjeta, -1, -1)):
                    pygame.draw.line(surf_tarjeta, HUD_ORO, (ex + 8 * edx, ey), (ex + 20 * edx, ey), 1)
                    pygame.draw.line(surf_tarjeta, HUD_ORO, (ex, ey + 8 * edy), (ex, ey + 18 * edy), 1)

            self.pantalla.blit(surf_tarjeta, (x_tarjeta, y_tarjeta))

            # Número romano estilizado
            romanos = ["I", "II", "III"]
            color_num = HUD_ORO if seleccionada else (110, 95, 120)
            self.dibujar_texto(romanos[i], x_tarjeta + 24, y_tarjeta + 26, 42, color_num, sombra=seleccionada)

            # Textos descriptivos
            color_tit = HUD_ORO if seleccionada else HUD_TEXTO
            self.dibujar_texto(titulo_n, x_tarjeta + 82, y_tarjeta + 16, 20, color_tit, sombra=seleccionada)
            self.dibujar_texto(subtitulo_n, x_tarjeta + 82, y_tarjeta + 44, 13, HUD_VERDE if seleccionada else HUD_MUTED)
            self.dibujar_texto(desc_n, x_tarjeta + 82, y_tarjeta + 70, 14, CREMA if seleccionada else (170, 160, 175))

        self.dibujar_texto(
            "FLECHAS / WASD: ELEGIR · ENTER: DESCENDER · ESC: VOLVER AL MENÚ",
            0, 646, 14, HUD_MUTED, centrado=True,
        )

    # --- Función dibujar_creditos --- #
    def dibujar_creditos(self):
        self.dibujar_fondo(self.pantalla)
        self.pantalla.blit(self.vineta, (0, 0))

        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((5, 4, 10, 185))
        self.pantalla.blit(velo, (0, 0))

        # Marco heráldico central
        ancho_m = 780
        alto_m = 560
        x_m = (ANCHO - ancho_m) // 2
        y_m = (ALTO - alto_m) // 2

        panel_c = pygame.Surface((ancho_m, alto_m), pygame.SRCALPHA)
        pygame.draw.rect(panel_c, (16, 13, 22, 235), (0, 0, ancho_m, alto_m), border_radius=12)
        pygame.draw.rect(panel_c, (*HUD_BORDE, 200), (0, 0, ancho_m, alto_m), 1, border_radius=12)
        pygame.draw.rect(panel_c, HUD_ORO, (0, 0, ancho_m, alto_m), 2, border_radius=12)

        # Ornamentos en esquinas
        for ex, ey, edx, edy in ((0, 0, 1, 1), (ancho_m, 0, -1, 1), (0, alto_m, 1, -1), (ancho_m, alto_m, -1, -1)):
            pygame.draw.line(panel_c, HUD_ORO, (ex + 10 * edx, ey), (ex + 28 * edx, ey), 1)
            pygame.draw.line(panel_c, HUD_ORO, (ex, ey + 10 * edy), (ex, ey + 24 * edy), 1)
        self.pantalla.blit(panel_c, (x_m, y_m))

        # Título
        self.dibujar_texto("IN CRYPTA", 0, y_m + 26, 44, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto("CRÉDITOS & DESARROLLO", 0, y_m + 76, 16, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 140), (ANCHO // 2 - 120, y_m + 102), (ANCHO // 2 + 120, y_m + 102), 1)

        # Bloque de integrantes
        self.dibujar_texto("EQUIPO 6 — UNAHUR", 0, y_m + 122, 18, HUD_ORO, centrado=True)
        for idx, nombre in enumerate(INTEGRANTES):
            self.dibujar_texto(nombre, 0, y_m + 152 + idx * 26, 17, HUD_TEXTO, centrado=True)

        # Materias
        self.dibujar_texto("Taller de Diseño Conceptual · Introducción a los Videojuegos", 0, y_m + 244, 15, HUD_MUTED, centrado=True)
        self.dibujar_texto("Universidad Nacional de Hurlingham (UNAHUR)", 0, y_m + 268, 14, (140, 130, 150), centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_BORDE, 120), (ANCHO // 2 - 160, y_m + 300), (ANCHO // 2 + 160, y_m + 300), 1)

        # Referencias
        self.dibujar_texto("INSPIRACIONES & HOMENAJES", 0, y_m + 322, 17, HUD_ORO, centrado=True)
        ref_texto = "Blasphemous (penitencia y pala) · Castlevania (criptas y portones) · Ender Lilies (atmósfera y melancolía)"
        self.dibujar_texto(ref_texto, 0, y_m + 352, 14, CREMA, centrado=True)

        # Tecnología
        self.dibujar_texto("TECNOLOGÍA & ARTE", 0, y_m + 396, 17, HUD_ORO, centrado=True)
        tec_texto = "Motor Python 3 + pygame-ce · Arte procedimental vectorial pygame.draw · Tipografía Noto Serif Display"
        self.dibujar_texto(tec_texto, 0, y_m + 424, 14, HUD_MUTED, centrado=True)

        # Pie
        self.dibujar_texto("ESC o ENTER: VOLVER AL MENÚ", 0, y_m + 500, 16, TURQUESA, centrado=True, sombra=True)

    def dibujar_selector_pruebas(self):
        self.dibujar_seleccion_nivel()

    # --- Función dibujar --- #
    def dibujar(self):
        if self.estado == "titulo":
            self.dibujar_titulo()
            return
        if self.estado == "menu":
            self.dibujar_menu_principal()
            return
        if self.estado == "seleccion_nivel":
            self.dibujar_seleccion_nivel()
            return
        if self.estado == "creditos":
            self.dibujar_creditos()
            return
        if self.estado == "test_selector":
            self.dibujar_selector_pruebas()
            return

        # Renderizar mundo al canvas virtual (Zoom 1.25x)
        destino = self.superficie_mundo
        self.dibujar_fondo(destino)
        self.nivel.dibujar(destino, self.camara)

        for enemigo in self.nivel.enemigos:
            enemigo.dibujar(destino, self.camara, pygame.time.get_ticks() / 1000)

        for onda in self.ondas_jefe:
            onda.dibujar(destino, self.camara, pygame.time.get_ticks() / 1000)
        if self.jefe is not None:
            self.jefe.dibujar(destino, self.camara, pygame.time.get_ticks() / 1000)

        self.jugador.dibujar(
            destino,
            self.camara,
            pygame.time.get_ticks() / 1000,
            pose=self.jugador.pose_actual(),
            con_pala=self.jugador.tiene_pala,
        )
        self.particulas.dibujar(destino, self.camara)

        # Escalar mundo virtual a pantalla (zoom 1.25x cinematográfico)
        pygame.transform.scale(self.superficie_mundo, (ANCHO, ALTO), self.pantalla)

        # Viñeta gótica y HUD en resolución nativa
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
                "P continuar · R reiniciar nivel · ESC volver al menú principal",
            )
        elif self.estado == "nivel_completado":
            self.dibujar_overlay("LA CRIPTA SE ABRE", "ENTER para descender")
        elif self.estado == "sala_completada":
            self.dibujar_overlay(
                "DESAFÍO COMPLETADO",
                "ENTER para continuar · ESC volver al menú",
            )
        elif self.estado == "derrota":
            self.dibujar_overlay(
                "LA OSCURIDAD TE RECLAMA",
                "ENTER para reintentar · ESC volver al menú",
            )
        elif self.estado == "victoria":
            self.dibujar_overlay(
                "¡ESCAPASTE DE LA CRIPTA!",
                f"Almas: {self.almas_totales} · Tiempo: {self.tiempo_total:04.1f}s · ENTER menú",
            )

    # --- Función dibujar_hud (Rediseño Total Gótico) --- #
    def dibujar_hud(self):
        # 1. Medallón Izquierdo: Vidas del Sepulturero
        self.dibujar_hud_relicario_vidas(24, 18)

        # 2. Relicario Derecho: Almas y Rosario de Ascenso
        self.dibujar_hud_relicario_almas(ANCHO - 308, 18)

        # 3. Sellos Tácticos de Habilidad: Dash y Pala/Guadaña
        self.dibujar_hud_habilidades(ANCHO - 264, ALTO - 62)

        # 4. Corona del Custodio (Solo Nivel 3 cuando el jefe está activo)
        if self.jefe is not None and self.jefe.vivo:
            self.dibujar_barra_jefe()

        # 5. Aviso Central del Combate
        if self.aviso_jefe > 0:
            if not self.jefe.vivo:
                texto = "EL CUSTODIO CAYÓ · LA SALIDA SE ABRIÓ"
                color_aviso = HUD_ORO
            elif self.jefe.estado == "cambio" or self.jefe.fase >= 2:
                texto = "¡FASE II! LA PALA REBOTA — SOLO EL PISOTÓN LO DAÑA"
                color_aviso = HUD_ROJO
            else:
                texto = "LA SALIDA ESTÁ SELLADA"
                color_aviso = HUD_ORO
            self.dibujar_texto(
                texto, 0, 142 if self.jefe is not None and self.jefe.vivo else 124,
                16, color_aviso, centrado=True, sombra=True,
            )

        # 6. Pistas de Orientación
        if self.mostrar_ayuda > 0 and self.estado == "jugando":
            self.dibujar_pista()

    # --- Módulo HUD: Relicario de Vidas --- #
    def dibujar_hud_relicario_vidas(self, x, y):
        ancho, alto = 260, 50
        panel = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(panel, (14, 11, 18, 215), (0, 0, ancho, alto), border_radius=8)
        pygame.draw.rect(panel, (*HUD_BORDE, 180), (0, 0, ancho, alto), 1, border_radius=8)
        pygame.draw.line(panel, (*HUD_ORO, 110), (10, 1), (ancho - 10, 1), 1)

        # Vértices góticos
        for vx, vy, vdx, vdy in ((0, 0, 1, 1), (ancho, 0, -1, 1), (0, alto, 1, -1), (ancho, alto, -1, -1)):
            pygame.draw.line(panel, HUD_ORO, (vx + 4 * vdx, vy), (vx + 14 * vdx, vy), 1)
            pygame.draw.line(panel, HUD_ORO, (vx, vy + 4 * vdy), (vx, vy + 12 * vdy), 1)
        self.pantalla.blit(panel, (x, y))

        # Rótulo de clase y nivel
        self.dibujar_texto("SEPULTURERO", x + 14, y + 6, 11, HUD_ORO)
        nivel_nombre = self.nivel.nombre.upper() if self.nivel else "CAMPOSANTO"
        self.dibujar_texto(nivel_nombre, x + 104, y + 6, 11, HUD_MUTED)

        # Corazones de sangre gótica
        pulso_latido = int(math.sin(self.tiempo_nivel * 9) * 2) if self.jugador.vidas == 1 else 0
        for i in range(VIDAS_MAXIMAS):
            cx = x + 18 + i * 26
            cy = y + 28
            lleno = (i < self.jugador.vidas)
            desp_y = pulso_latido if (i == 0 and self.jugador.vidas == 1) else 0

            # Aura si está en última vida
            if lleno and self.jugador.vidas == 1:
                aura = pygame.Surface((28, 28), pygame.SRCALPHA)
                pygame.draw.circle(aura, (220, 30, 40, int(35 + pulso_latido * 15)), (14, 14), 12)
                self.pantalla.blit(aura, (cx - 14, cy - 14 + desp_y), special_flags=pygame.BLEND_RGBA_ADD)

            self.dibujar_corazon_gotico(cx, cy + desp_y, lleno)

    # --- Módulo HUD: Corazón Gótico --- #
    def dibujar_corazon_gotico(self, cx, cy, lleno):
        if lleno:
            color_base = (215, 30, 45)
            color_sombra = (120, 16, 26)
            color_brillo = (255, 95, 115)
            color_destello = (255, 235, 240)
        else:
            color_base = (38, 28, 38)
            color_sombra = (22, 16, 24)
            color_brillo = (50, 38, 50)
            color_destello = None

        # Sombra profunda
        pygame.draw.circle(self.pantalla, color_sombra, (cx - 5, cy - 2), 6)
        pygame.draw.circle(self.pantalla, color_sombra, (cx + 5, cy - 2), 6)
        pygame.draw.polygon(self.pantalla, color_sombra, [(cx - 10, cy - 1), (cx + 10, cy - 1), (cx, cy + 11)])

        # Cuerpo carmesí
        pygame.draw.circle(self.pantalla, color_base, (cx - 5, cy - 3), 5)
        pygame.draw.circle(self.pantalla, color_base, (cx + 5, cy - 3), 5)
        pygame.draw.polygon(self.pantalla, color_base, [(cx - 9, cy - 2), (cx + 9, cy - 2), (cx, cy + 10)])

        # Borde exterior de hierro
        pygame.draw.polygon(self.pantalla, (*HUD_BORDE, 220), [(cx - 9, cy - 2), (cx + 9, cy - 2), (cx, cy + 10)], 1)

        # Destello especular
        if lleno and color_destello:
            pygame.draw.circle(self.pantalla, color_destello, (cx - 3, cy - 4), 2)
            pygame.draw.circle(self.pantalla, color_brillo, (cx + 4, cy - 4), 1)

    # --- Módulo HUD: Relicario de Almas & Rosario de Ascensión --- #
    def dibujar_hud_relicario_almas(self, x, y):
        ancho, alto = 280, 50
        panel = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(panel, (14, 11, 18, 215), (0, 0, ancho, alto), border_radius=8)
        pygame.draw.rect(panel, (*HUD_BORDE, 180), (0, 0, ancho, alto), 1, border_radius=8)
        pygame.draw.line(panel, (*HUD_ORO, 110), (10, 1), (ancho - 10, 1), 1)

        for vx, vy, vdx, vdy in ((0, 0, 1, 1), (ancho, 0, -1, 1), (0, alto, 1, -1), (ancho, alto, -1, -1)):
            pygame.draw.line(panel, HUD_ORO, (vx + 4 * vdx, vy), (vx + 14 * vdx, vy), 1)
            pygame.draw.line(panel, HUD_ORO, (vx, vy + 4 * vdy), (vx, vy + 12 * vdy), 1)
        self.pantalla.blit(panel, (x, y))

        # Icono de alma espectral en rombo
        ix, iy = x + 18, y + 25
        halo = pygame.Surface((34, 34), pygame.SRCALPHA)
        pygame.draw.circle(halo, (70, 230, 215, 38), (17, 17), 15)
        self.pantalla.blit(halo, (ix - 17, iy - 17), special_flags=pygame.BLEND_RGBA_ADD)
        pygame.draw.polygon(self.pantalla, HUD_ALMA, [(ix, iy - 9), (ix + 6, iy), (ix, iy + 9), (ix - 6, iy)])
        pygame.draw.polygon(self.pantalla, (230, 255, 250), [(ix, iy - 4), (ix + 2, iy), (ix, iy + 4), (ix - 2, iy)])

        # Contador de Almas
        total = self.nivel.total_almas if self.nivel else 24
        self.dibujar_texto(f"ALMAS  {self.jugador.almas} / {total}", x + 34, y + 6, 13, HUD_ORO)

        # Rosario de 10 Cuentas de Ánima (Progreso a Vida Extra)
        rx = x + 38
        ry = y + 31
        pulso_resurreccion = 0.5 + 0.5 * math.sin(self.tiempo_nivel * 8)
        for i in range(ALMAS_POR_VIDA):
            bx = rx + i * 23
            by = ry
            llena = (i < self.jugador.almas_para_vida)

            if llena:
                # Perla espectral encendida
                color_perla = (80, 235, 215)
                radio = 4
                if self.jugador.almas_para_vida >= 8:
                    radio = 4 + int(pulso_resurreccion * 1.5)
                pygame.draw.circle(self.pantalla, color_perla, (bx, by), radio)
                pygame.draw.circle(self.pantalla, (230, 255, 250), (bx - 1, by - 1), max(1, radio - 2))
            else:
                # Cuenta vacía de hierro
                pygame.draw.circle(self.pantalla, (42, 34, 46), (bx, by), 3)
                pygame.draw.circle(self.pantalla, (22, 18, 26), (bx, by), 3, 1)

    # --- Módulo HUD: Sellos de Habilidad (Dash & Pala/Guadaña) --- #
    def dibujar_hud_habilidades(self, x, y):
        ancho, alto = 244, 46
        panel = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(panel, (14, 11, 18, 210), (0, 0, ancho, alto), border_radius=8)
        pygame.draw.rect(panel, (*HUD_BORDE, 170), (0, 0, ancho, alto), 1, border_radius=8)
        self.pantalla.blit(panel, (x, y))

        # SELLO 1: DASH (Sombra)
        dx_box = x + 12
        dash_listo = self.jugador.dash_listo()
        color_dash = HUD_DASHTURQUESA if dash_listo else HUD_MUTED

        # Ala rúnica de dash
        pygame.draw.polygon(self.pantalla, color_dash, [(dx_box + 2, y + 28), (dx_box + 12, y + 16), (dx_box + 16, y + 22), (dx_box + 7, y + 31)])
        pygame.draw.polygon(self.pantalla, color_dash, [(dx_box + 14, y + 23), (dx_box + 22, y + 14), (dx_box + 24, y + 20), (dx_box + 17, y + 27)])

        self.dibujar_texto("DASH", dx_box + 28, y + 8, 11, HUD_MUTED)
        estado_dash = "LISTO" if dash_listo else f"{1.0 - (self.jugador.dash_cooldown / DASH_COOLDOWN):.1f}"
        self.dibujar_texto(estado_dash, dx_box + 28, y + 24, 13, color_dash)

        # Línea divisoria central
        pygame.draw.line(self.pantalla, (*HUD_BORDE, 150), (x + 115, y + 8), (x + 115, y + alto - 8), 1)

        # SELLO 2: ARMA (Pala / Guadaña Imperial)
        ax_box = x + 128
        if not self.jugador.tiene_pala:
            self.dibujar_texto("SIN ARMA", ax_box + 8, y + 16, 12, (55, 50, 62))
        else:
            es_guadaña = getattr(self.jugador, "rango_ataque_mejorado", False)
            color_arma = (215, 85, 255) if es_guadaña else HUD_ORO
            etiqueta = "GUADAÑA +" if es_guadaña else "PALA"

            # Icono de arma
            if es_guadaña:
                # Guadaña mística púrpura
                pygame.draw.arc(self.pantalla, color_arma, (ax_box + 4, y + 12, 18, 20), 0, 3.14, 3)
                pygame.draw.line(self.pantalla, (130, 50, 160), (ax_box + 13, y + 22), (ax_box + 6, y + 36), 2)
            else:
                # Pala plateada
                pygame.draw.line(self.pantalla, (160, 120, 60), (ax_box + 8, y + 34), (ax_box + 16, y + 18), 2)
                pygame.draw.polygon(self.pantalla, (190, 190, 205), [(ax_box + 14, y + 16), (ax_box + 22, y + 14), (ax_box + 18, y + 24)])

            self.dibujar_texto(etiqueta, ax_box + 28, y + 8, 11, color_arma)
            estado_ataque = "LISTO" if self.jugador.ataque_cooldown <= 0 else "..."
            self.dibujar_texto(estado_ataque, ax_box + 28, y + 24, 13, HUD_VERDE if self.jugador.ataque_cooldown <= 0 else HUD_MUTED)

    # --- Módulo HUD: Barra Imperial del Custodio (Jefe Final) --- #
    def dibujar_barra_jefe(self):
        ancho, alto = 500, 58
        x = (ANCHO - ancho) // 2
        y = 18

        panel = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(panel, (16, 12, 20, 230), (0, 0, ancho, alto), border_radius=10)
        color_borde = (215, 45, 55) if self.jefe.fase >= 2 else (*HUD_BORDE, 200)
        pygame.draw.rect(panel, color_borde, (0, 0, ancho, alto), 2 if self.jefe.fase >= 2 else 1, border_radius=10)

        # Corona de oro en el borde superior
        pygame.draw.line(panel, HUD_ORO, (14, 1), (ancho - 14, 1), 1)
        self.pantalla.blit(panel, (x, y))

        # Nombre y fase
        nombre_color = HUD_ROJO if self.jefe.fase >= 2 else HUD_ORO
        self.dibujar_texto("EL CUSTODIO DEL OSARIO", x + 16, y + 7, 14, nombre_color, sombra=True)

        # Subtítulo dinámico según fase
        if self.jefe.fase >= 2:
            fase_txt = "FASE II · ¡LA PALA REBOTA! SOLO PISOTÓN"
            fase_color = (250, 65, 65)
        else:
            fase_txt = "FASE I · VULNERABLE A PALA Y PISOTÓN"
            fase_color = HUD_MUTED
        self.dibujar_texto(fase_txt, x + ancho - 270, y + 8, 11, fase_color)

        # 6 Celdas de Salud (Losas de Osario con Rubí)
        ancho_celda = 74
        alto_celda = 10
        y_celdas = y + 32
        for i in range(6):
            cx = x + 16 + i * (ancho_celda + 5)
            rect_celda = pygame.Rect(cx, y_celdas, ancho_celda, alto_celda)
            llena = (i < self.jefe.vida)

            if llena:
                # Rubí carmesí de salud
                color_rubi = (225, 38, 52)
                pygame.draw.rect(self.pantalla, color_rubi, rect_celda, border_radius=3)
                pygame.draw.rect(self.pantalla, (255, 105, 120), (rect_celda.x + 2, rect_celda.y + 2, rect_celda.width - 4, 3), border_radius=2)
                pygame.draw.rect(self.pantalla, (120, 18, 28), rect_celda, 1, border_radius=3)
            else:
                # Cavidad agrietada gris piedra
                pygame.draw.rect(self.pantalla, (36, 26, 30), rect_celda, border_radius=3)
                pygame.draw.rect(self.pantalla, (22, 16, 20), rect_celda, 1, border_radius=3)

    # --- Función dibujar_pista --- #
    def dibujar_pista(self):
        if not self.nivel or not self.nivel.pista:
            return
        lineas = textwrap.wrap(self.nivel.pista, width=82)
        alto = 26 + 19 * len(lineas)
        x = (ANCHO - 780) // 2
        y = ALTO - alto - 16
        caja = pygame.Surface((780, alto), pygame.SRCALPHA)
        pygame.draw.rect(caja, (14, 11, 18, 220), (0, 0, 780, alto), border_radius=9)
        pygame.draw.rect(caja, (*HUD_BORDE, 170), (0, 0, 780, alto), 1, border_radius=9)
        pygame.draw.rect(caja, HUD_ORO, (0, 0, 4, alto), border_radius=2)
        self.pantalla.blit(caja, (x, y))
        self.dibujar_texto("PISTA", x + 18, y + 7, 14, HUD_ORO)
        for i, linea in enumerate(lineas):
            self.dibujar_texto(linea, x + 18, y + 26 + i * 19, 16, HUD_TEXTO)

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
