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
from hud import HudOrquestador
from nivel import Nivel
from niveles import NIVELES, SALAS_PRUEBA, NIVEL_TUTORIAL
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
        self.hud = HudOrquestador()
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
        self.texto_ayuda = ""
        self.dt = 0.0
        self.flash = 0.0
        self.flash_color = (255, 255, 255)
        self.jefe = None
        self.ondas_jefe = []
        self.punto_reintento = None
        self.aviso_jefe = 0.0
        self.sala_prueba = False
        self.sala_prueba_indice = None
        self.es_tutorial = False
        self.reducir_movimiento = False
        self.muertes_totales = 0
        self.causa_muerte = ""
        self.almas_combo_count = 0
        self.almas_combo_timer = 0.0
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
        self.es_tutorial = False
        jugador_previo = getattr(self, "jugador", None)
        if sala is None:
            self.nivel_indice = indice
            datos = NIVELES[indice]
            tiene_pala = (jugador_previo.tiene_pala if jugador_previo else False) or (indice >= 2)
            tiene_dash = (jugador_previo.tiene_dash if jugador_previo else False) or (indice >= 2)
        else:
            datos = SALAS_PRUEBA[sala]
            self.nivel_indice = datos["nivel"]
            tiene_pala = datos["pala"]
            tiene_dash = datos.get("dash", datos["nivel"] >= 1)

        self.nivel = Nivel(
            datos["mapa"],
            datos["nombre"],
            datos["pista"],
            datos.get("tema", "camposanto"),
        )
        vidas_iniciales = VIDAS_INICIALES if vidas is None else vidas
        self.jugador = Jugador(*self.nivel.spawn, vidas=vidas_iniciales)
        self.jugador.tiene_pala = tiene_pala
        self.jugador.tiene_dash = tiene_dash
        self.camara = Camara()
        self.camara.permitir_sacudida = not self.reducir_movimiento
        self.camara.actualizar(self.jugador, self.nivel, 1.0)
        self.estado = "jugando"
        self.tiempo_nivel = 0.0
        self.mostrar_ayuda = 4.0
        self.texto_ayuda = self.nivel.pista if self.nivel else ""
        self.flash = 0.0
        self.jefe = self.nivel.jefes[0] if self.nivel.jefes else None
        self.ondas_jefe = []
        self.punto_reintento = None
        self.aviso_jefe = 0.0

    # --- Función iniciar_tutorial --- #
    def iniciar_tutorial(self):
        """Carga el nivel tutorial. No cuenta para la partida principal."""
        self.es_tutorial = True
        self.sala_prueba = False
        self.sala_prueba_indice = None
        self.almas_totales = 0
        self.tiempo_total = 0.0
        self.nivel_indice = 0  # 0-based; HUD leerá es_tutorial para mostrar "TUTORIAL"
        self.nivel = Nivel(
            NIVEL_TUTORIAL,
            "El Ritual del Sepulturero",
            (
                "FLECHAS / WASD: MOVERSE · ARRIBA/W: SALTAR · "
                "SHIFT: DASH EN EL AIRE · "
                "RECOGÉ LA PALA (W) · J/Z/CLICK: ATACAR · "
                "SALTÁ SOBRE LOS MORADORES PARA PISARLOS (STOMP) · "
                "LA PLATAFORMA SOBRE PINCHOS LLEVA AL PORTÓN"
            ),
            "cripta",
        )
        vidas_iniciales = VIDAS_INICIALES
        self.jugador = Jugador(*self.nivel.spawn, vidas=vidas_iniciales)
        self.jugador.tiene_pala = False
        self.jugador.tiene_dash = False
        self.tutorial_zona_actual = None
        self.camara = Camara()
        self.camara.permitir_sacudida = not self.reducir_movimiento
        self.camara.actualizar(self.jugador, self.nivel, 1.0)
        self.estado = "jugando"
        self.tiempo_nivel = 0.0
        self.mostrar_ayuda = 6.0
        self.texto_ayuda = self.nivel.pista
        self.flash = 0.0
        self.jefe = None
        self.ondas_jefe = []
        self.punto_reintento = None
        self.aviso_jefe = 0.0
        # Mensaje de bienvenida en el canal HUD
        self.hud.mostrar_mensaje(
            "EL RITUAL DEL SEPULTURERO · Aprende las mecánicas básicas", 1, 5.0
        )

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
        self.jugador = None
        self.cargar_nivel(0, vidas=VIDAS_INICIALES)
        self.estado = "jugando"

    # --- Función reiniciar_juego --- #
    def reiniciar_juego(self):
        self.almas_totales = 0
        self.tiempo_total = 0.0
        self.jugador = None
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
                        self.menu_opcion = (self.menu_opcion - 1) % 4
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_opcion = (self.menu_opcion + 1) % 4
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.reproducir("ui")
                        if self.menu_opcion == 0:
                            self.iniciar_partida()
                        elif self.menu_opcion == 1:
                            self.abrir_seleccion_nivel()
                        elif self.menu_opcion == 2:
                            self.iniciar_tutorial()
                        elif self.menu_opcion == 3:
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

                elif evento.key == pygame.K_F1:
                    self.reducir_movimiento = not self.reducir_movimiento
                    self.camara.permitir_sacudida = not self.reducir_movimiento
                    self.hud.reducir_movimiento = self.reducir_movimiento
                    estado_str = "ACTIVADA" if self.reducir_movimiento else "DESACTIVADA"
                    self.hud.mostrar_mensaje(f"ACCESIBILIDAD: REDUCIR MOVIMIENTO {estado_str}", 3, 2.5)
                    self.audio.reproducir("ui")

                elif evento.key == pygame.K_r and self.estado not in ("titulo", "menu", "seleccion_nivel", "creditos"):
                    if self.sala_prueba:
                        self.cargar_sala_prueba(self.sala_prueba_indice)
                    elif self.es_tutorial:
                        self.iniciar_tutorial()
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
                            mejorado=self.jugador.rango_ataque_mejorado,
                        )

                elif evento.key == pygame.K_RETURN:
                    if self.estado == "titulo":
                        self.audio.reproducir("ui")
                        self.abrir_menu()
                    elif self.estado == "nivel_completado":
                        self.siguiente_nivel()
                    elif self.estado == "sala_completada":
                        self.abrir_menu()
                    elif self.estado == "tutorial_completado":
                        self.abrir_menu()
                    elif self.estado == "derrota" and self.sala_prueba:
                        self.cargar_sala_prueba(self.sala_prueba_indice)
                    elif self.estado == "derrota" and self.es_tutorial:
                        self.iniciar_tutorial()
                    elif self.estado == "derrota":
                        self.cargar_nivel(self.nivel_indice, vidas=VIDAS_INICIALES)
                        self.estado = "jugando"
                    elif self.estado == "victoria":
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

        if self.almas_combo_timer > 0:
            self.almas_combo_timer = max(0.0, self.almas_combo_timer - dt)
            if self.almas_combo_timer <= 0:
                self.almas_combo_count = 0

        self.actualizar_plataformas(dt)
        teclas = pygame.key.get_pressed()
        self.jugador.actualizar(dt, teclas, self.nivel.solidos_actuales())
        self.limitar_jugador()
        self.procesar_feedback_jugador()
        self.actualizar_ataque()

        if self.actualizar_jefe(dt):
            return

        if self.jugador.rect.top > self.nivel.alto + 120:
            self.perder_vida(ignorar_invulnerabilidad=True, causa="Caída al abismo de la cripta")
            return

        if self.actualizar_peligros():
            return

        self.actualizar_enemigos(dt)
        self.actualizar_almas()
        self.actualizar_palas()
        self.actualizar_power_ups_dash()
        self.actualizar_power_ups_rango()
        self.actualizar_checkpoints()
        if self.es_tutorial:
            self.actualizar_tutorial_contextual()
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
            if self.es_tutorial:
                self.estado = "tutorial_completado"
            elif self.sala_prueba:
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

        # Jefe — pala: daña en Fase 1, rebota con chispas en Fase 2.
        if (
            not self.jugador.ataque_golpeado
            and self.jefe is not None
            and self.jefe.vivo
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
            # Fase 1: 2 ondas expansivas (izq, der)
            # Fase 2: 2 ondas iniciales + 2 ondas rápidas (sin ondas estáticas)
            direcciones = (-1, 1)
            for direccion in direcciones:
                self.ondas_jefe.append(OndaCustodio(
                    jefe.rect.centerx + direccion * 24,
                    jefe.rect.bottom,
                    direccion,
                    velocidad,
                ))
            if jefe.fase >= 2:
                for direccion in direcciones:
                    self.ondas_jefe.append(OndaCustodio(
                        jefe.rect.centerx + direccion * 48,
                        jefe.rect.bottom,
                        direccion,
                        velocidad * 1.35,
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
                self.perder_vida(causa="Onda de choque del Custodio")
                return True
        self.ondas_jefe = [onda for onda in self.ondas_jefe if onda.viva]

        if not jefe.vivo:
            return False

        if self.jugador.rect.colliderect(jefe.rect):
            viene_desde_arriba = (
                self.jugador.vy > 0
                and self.jugador.rect.bottom <= jefe.rect.top + 32
            )
            if viene_desde_arriba:
                # Pisotón limpio: posicionar sobre la cabeza y dar invulnerabilidad temporal
                self.jugador.rect.bottom = jefe.rect.top
                self.jugador.y = float(self.jugador.rect.y)
                self.jugador.vy = -REBOTE_ENEMIGO
                self.jugador.en_suelo = False
                self.jugador.invulnerable = 0.40
                self.dañar_jefe_pisaton()
            elif self.jugador.invulnerable <= 0:
                self.perder_vida(causa="Poder abrumador del Custodio")
                return True

        if self.punto_reintento is None:
            limite = jefe.minimo_x - 3 * TILE
            if self.jugador.rect.right > limite:
                self.punto_reintento = (limite, self.nivel.spawn[1])
                self.texto_ayuda = "PUNTO DE CONTROL · LA ANTESALA DEL CUSTODIO"
                self.mostrar_ayuda = 4.5
                self.hud.mostrar_mensaje("PUNTO DE CONTROL · La antesala del Custodio del Osario", 1, 3.5)
                self.audio.reproducir("ui")

        return False

    # --- Función dañar_jefe --- #
    def dañar_jefe(self):
        """Golpe al jefe (usado por compatibilidad y tests)."""
        return self.dañar_jefe_pala()

    # --- Función dañar_jefe_pala --- #
    def dañar_jefe_pala(self):
        """Golpe de pala: daña en Fase 1; rebota físicamente en Fase 2."""
        if not self.jefe.recibir_golpe_pala():
            # Fase 2: pala rebota contra la armadura reforzada
            self.jugador.vx = -self.jugador.direccion * 220
            self.jugador.vy = -160
            self.jugador.invulnerable = 0.25
            self.camara.sacudir(5.0, 0.12)
            self.flash = 0.08
            self.flash_color = (200, 50, 50)
            self.audio.reproducir("pala")
            self.particulas.emitir(
                self.jefe.rect.centerx - self.jugador.direccion * 16,
                self.jefe.rect.centery,
                14,
                ((255, 80, 80), (255, 200, 100), BLANCO),
                220,
                0.35,
                3,
                180,
            )
            return False
        return self._aplicar_golpe_jefe()

    # --- Función dañar_jefe_pisaton --- #
    def dañar_jefe_pisaton(self):
        """Pisotón: siempre funciona en ambas fases."""
        if not self.jefe.recibir_pisaton():
            return False
        res = self._aplicar_golpe_jefe()
        self.audio.reproducir("stomp")
        return res

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
            self.hud.mostrar_mensaje("¡EL CUSTODIO CAYÓ! · La cripta se abre…", 5, 4.0)
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
            self.hud.mostrar_mensaje("¡FASE II! · Armadura impenetrable · Solo PISOTÓN desde las cornisas", 4, 4.5)

        return True

    # --- Función actualizar_peligros --- #
    def actualizar_peligros(self):
        if self.jugador.invulnerable > 0:
            return False
        for peligro in self.nivel.peligros:
            if self.jugador.rect.colliderect(peligro):
                self.perder_vida(causa="Pinchos ancestrales del camposanto")
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
                self.audio.reproducir("stomp")
                self.particulas.pala(enemigo.rect.centerx, enemigo.rect.centery)
                self.camara.sacudir(6.0, 0.14)
            else:
                self.perder_vida(causa="Contacto con un Morador de la cripta")
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
                    self.audio.reproducir("stomp")
                    self.particulas.pala(enemigo_melee.rect.centerx, enemigo_melee.rect.centery)
                    self.camara.sacudir(6.0, 0.14)
                else:
                    self.perder_vida(causa="Embestida del Guardia de la cripta")
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
                self.perder_vida(causa="Ataque aéreo de Cuervo espectral")
                return

        # Polillas: vuelo zigzag, daño por contacto.
        for polilla in self.nivel.polillas:
            polilla.actualizar(dt)
            if (
                polilla.vivo
                and self.jugador.invulnerable <= 0
                and self.jugador.rect.colliderect(polilla.rect)
            ):
                self.perder_vida(causa="Polvo letal de Polilla sombría")
                return

        # Arañas: patrullaje horizontal, daño por contacto.
        for araña in self.nivel.aranias:
            araña.actualizar(dt)
            if (
                araña.vivo
                and self.jugador.invulnerable <= 0
                and self.jugador.rect.colliderect(araña.rect)
            ):
                self.perder_vida(causa="Picadura de Araña espectral")
                return

    # --- Función actualizar_almas --- #
    def actualizar_almas(self):
        for alma in self.nivel.almas:
            if alma.actualizar(self.jugador):
                self.almas_combo_timer = 1.3
                self.almas_combo_count = min(6, self.almas_combo_count + 1)
                sonido_alma = (
                    f"alma_{self.almas_combo_count}"
                    if f"alma_{self.almas_combo_count}" in self.audio.sonidos
                    else "alma"
                )
                self.audio.reproducir(sonido_alma)
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
                        self.hud.mostrar_mensaje("¡VIDA EXTRA · 10 ALMAS CONSAGRADAS!", 2, 3.0)

    # --- Función actualizar_palas --- #
    def actualizar_palas(self):
        for pala in self.nivel.palas:
            if pala.actualizar(self.jugador):
                self.audio.reproducir("pala_recoger")
                self.particulas.alma(pala.rect.centerx, pala.rect.centery)
                self.texto_ayuda = "¡PALA DE SEPULTURERO OBTENIDA! · J / CLICK: EXORCIZAR MORADORES"
                self.mostrar_ayuda = 4.0
                self.hud.mostrar_mensaje("¡PALA OBTENIDA! · J / Z: Atacar · Pisotón: salta sobre los moradores", 2, 4.0)

    # --- Función actualizar_power_ups_dash --- #
    def actualizar_power_ups_dash(self):
        for power_up in self.nivel.power_ups_dash:
            if power_up.actualizar(self.jugador):
                self.audio.reproducir("dash_recoger")
                self.particulas.emitir(
                    power_up.rect.centerx,
                    power_up.rect.centery,
                    28,
                    ((80, 220, 255), (180, 250, 255), BLANCO, (40, 150, 240)),
                    240,
                    0.7,
                    5,
                    200,
                )
                self.camara.sacudir(6.0, 0.16)
                self.flash = 0.14
                self.flash_color = (60, 200, 255)
                self.texto_ayuda = "¡AMULETO DE SOMBRAS OBTENIDO! · SHIFT: DASH EN EL AIRE"
                self.mostrar_ayuda = 4.0
                self.hud.mostrar_mensaje("¡AMULETO DE SOMBRAS! · SHIFT / X: Dash en el aire", 2, 4.0)

    # --- Función actualizar_checkpoints --- #
    def actualizar_checkpoints(self):
        for checkpoint in self.nivel.checkpoints:
            if checkpoint.actualizar(self.jugador):
                self.punto_reintento = (checkpoint.rect.x, checkpoint.rect.y - 4)
                self.audio.reproducir("checkpoint")
                self.particulas.emitir(
                    checkpoint.rect.centerx,
                    checkpoint.rect.bottom - 20,
                    18,
                    ((120, 220, 255), (200, 245, 255), BLANCO),
                    180,
                    0.6,
                    3,
                    120,
                )
                self.hud.mostrar_mensaje("FAROL CONSAGRADO · Punto de control registrado", 1, 3.0)

    # --- Función actualizar_tutorial_contextual --- #
    def actualizar_tutorial_contextual(self):
        col = self.jugador.rect.x // TILE
        if col < 15:
            zona = 1
            msg = "MOVIMIENTO Y SALTO · FLECHAS / WASD: Mover · ESPACIO: Salto variable"
        elif col < 32:
            zona = 2
            msg = "FOSO DE SALTO · Medí tu impulso. Si caés, usá los escalones para subir"
        elif col < 47:
            zona = 3
            msg = "ALTAR DE LA PALA · Recogé la pala (W) · J / Z / CLICK: Atacar morador"
        elif col < 62:
            zona = 4
            msg = "EL PISOTÓN (STOMP) · Saltá sobre la cabeza del morador para rebotar"
        elif col < 78:
            zona = 5
            msg = "AMULETO DE SOMBRAS · Recogé el dash (D) · SHIFT / X: Dash en el aire"
        else:
            zona = 6
            msg = "PORTÓN FINAL · Cruzá el umbral hacia la cripta"

        if getattr(self, "tutorial_zona_actual", None) != zona:
            self.tutorial_zona_actual = zona
            self.hud.mostrar_mensaje(msg, 2, 4.0)

    # --- Función actualizar_power_ups_rango --- #
    def actualizar_power_ups_rango(self):
        for power_up in self.nivel.power_ups_rango:
            if power_up.actualizar(self.jugador):
                self.audio.reproducir("alma")
                self.particulas.emitir(
                    power_up.rect.centerx,
                    power_up.rect.centery,
                    28,
                    ((215, 80, 255), (255, 200, 255), BLANCO, (160, 50, 220)),
                    240,
                    0.7,
                    5,
                    200,
                )
                self.camara.sacudir(6.0, 0.16)
                self.flash = 0.14
                self.flash_color = (190, 60, 255)
                self.texto_ayuda = "¡GUADAÑA MÍSTICA OBTENIDA! · ALCANCE ESPECTRAL Y PODER MEJORADO"
                self.mostrar_ayuda = 4.0
                self.hud.mostrar_mensaje("¡GUADAÑA MÍSTICA! · Alcance espectral de 72px · Pisotón en el Custodio", 3, 4.0)

    # --- Función perder_vida --- #
    def perder_vida(self, ignorar_invulnerabilidad=False, causa="Peligros de la cripta"):
        if self.jugador.invulnerable > 0 and not ignorar_invulnerabilidad:
            return

        self.jugador.vidas -= 1
        self.audio.reproducir("daño")
        self.particulas.daño(self.jugador.rect.centerx, self.jugador.rect.centery)
        self.camara.sacudir(9.0, 0.22)
        self.flash = 0.16
        self.flash_color = ROJO
        self.almas_combo_count = 0
        self.almas_combo_timer = 0.0

        if self.jugador.vidas <= 0:
            self.muertes_totales += 1
            self.causa_muerte = causa
            self.estado = "derrota"
            self.audio.reproducir("muerte")
            return

        self.jugador.almas = 0
        for alma in self.nivel.almas:
            alma.reiniciar()

        if self.punto_reintento is not None:
            tenia_guadaña = self.jugador.rango_ataque_mejorado
            tenia_pala = self.jugador.tiene_pala
            tenia_dash = self.jugador.tiene_dash
            self.jugador.respawn(*self.punto_reintento)
            self.jugador.rango_ataque_mejorado = tenia_guadaña
            self.jugador.tiene_pala = tenia_pala
            self.jugador.tiene_dash = tenia_dash
        else:
            tenia_pala = self.jugador.tiene_pala
            tenia_dash = self.jugador.tiene_dash
            self.jugador.respawn(*self.nivel.spawn)
            self.jugador.tiene_pala = tenia_pala
            self.jugador.tiene_dash = tenia_dash
            for pup in self.nivel.power_ups_rango:
                pup.reiniciar()
            for pup in self.nivel.power_ups_dash:
                pup.reiniciar()

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
            arriba, abajo = (14, 20, 36), (28, 42, 62)

        for y in range(h):
            proporcion = y / h
            color = tuple(
                int(arriba[i] + (abajo[i] - arriba[i]) * proporcion)
                for i in range(3)
            )
            pygame.draw.line(fondo, color, (0, y), (w, y))

        if tema == "cripta":
            vx = int(w * 0.68)
            pygame.draw.rect(fondo, (16, 15, 22), (vx, 40, 150, 230))
            pygame.draw.arc(fondo, (52, 50, 60), (vx - 10, 10, 170, 110), 0, math.pi, 8)
            pygame.draw.rect(fondo, (40, 52, 58), (vx + 16, 74, 118, 178))
            for x in range(vx + 26, vx + 130, 26):
                pygame.draw.line(fondo, (20, 25, 30), (x, 80), (x, 248), 3)
            pygame.draw.line(fondo, (20, 25, 30), (vx + 16, 166), (vx + 134, 166), 3)
            pygame.draw.arc(fondo, (42, 58, 62), (vx + 10, 48, 130, 70), 0, math.pi, 4)
        elif tema == "osario":
            cx = int(w * 0.76)
            pygame.draw.circle(fondo, (52, 16, 22), (cx, 120), 80)
            pygame.draw.circle(fondo, (94, 26, 32), (cx, 120), 54)
            pygame.draw.circle(fondo, (150, 48, 38), (cx, 120), 28)
        return fondo

    # --- Función crear_vineta --- #
    def crear_vineta(self, fuerza):
        vineta = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        # Viñeta gótica periférica suave: oscurece los bordes y esquinas exteriores,
        # dejando el área central y los fosos limpios sin oscurecer la acción.
        small_w, small_h = 160, 90
        small = pygame.Surface((small_w, small_h), pygame.SRCALPHA)
        cx, cy = small_w / 2, small_h / 2
        for y in range(small_h):
            for x in range(small_w):
                dx = (x - cx) / (cx * 0.88)
                dy = (y - cy) / (cy * 0.82)
                dist = math.hypot(dx, dy)
                if dist > 0.65:
                    factor = min(1.0, (dist - 0.65) / 0.60)
                    alfa = int(fuerza * (factor ** 2))
                    small.set_at((x, y), (0, 0, 0, min(255, alfa)))
        pygame.transform.smoothscale(small, (ANCHO, ALTO), vineta)
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

        # Luna llena con halo — paralaje lejano suave (0.04)
        luna_x = int(w * 0.68) - int(self.camara.x * 0.04)
        luna_y = 72
        halo_luna = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_luna, (200, 200, 160, 20), (60, 60), 58)
        pygame.draw.circle(halo_luna, (220, 220, 180, 30), (60, 60), 42)
        destino.blit(halo_luna, (luna_x - 60, luna_y - 60), special_flags=pygame.BLEND_RGBA_ADD)
        pygame.draw.circle(destino, (236, 230, 196), (luna_x, luna_y), 26)
        pygame.draw.circle(destino, (218, 210, 174), (luna_x + 6, luna_y - 4), 8)

        # Bóveda celeste con estrellas en paralaje continuo (0.06)
        estrellas = [
            (60, 42), (140, 20), (220, 56), (310, 28), (410, 44),
            (500, 16), (590, 38), (680, 22), (770, 50), (860, 32),
            (940, 18), (1010, 44), (90, 70), (270, 62), (460, 55),
            (640, 75), (820, 65), (980, 80),
        ]
        ox = int(self.camara.x * 0.06) % w
        for sx, sy in estrellas:
            px = (sx - ox) % w
            pygame.draw.circle(destino, (220, 218, 200), (px, sy), 1)

        # Colinas góticas continuas en bucle modular infinito (paralaje 0.18)
        hill_w = 300
        offset_h = int(self.camara.x * 0.18) % hill_w
        for i in range(-1, int(w / hill_w) + 2):
            bx = i * hill_w - offset_h
            pygame.draw.polygon(
                destino,
                (22, 34, 52),
                [(bx, h), (bx + 150, int(h * 0.52) + 32), (bx + 300, h)],
            )
            pygame.draw.polygon(
                destino,
                (28, 42, 62),
                [(bx + 75, h), (bx + 195, int(h * 0.58) + 32), (bx + 320, h)],
            )

        # Árboles marchitos y lápidas continuas a lo largo de todo el nivel (paralaje 0.38)
        elem_w = 190
        offset_e = int(self.camara.x * 0.38) % elem_w
        for i in range(-1, int(w / elem_w) + 2):
            ex = i * elem_w - offset_e
            idx_mundo = int((self.camara.x * 0.38 + ex) // elem_w)
            if idx_mundo % 2 == 0:
                escala = 0.95 + ((idx_mundo * 7) % 3) * 0.15
                self.dibujar_arbol_muerto(destino, ex + 40, h - 60, escala)
            else:
                escala = 0.85 + ((idx_mundo * 5) % 3) * 0.12
                self.dibujar_tumba_lejana(destino, ex + 60, h - 44, escala)

    def dibujar_arbol_muerto(self, destino, x, base_y, escala):
        alto = int(150 * escala)
        color = (24, 30, 44)
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
            (28, 38, 54),
            (x, base_y - alto, ancho, alto),
            border_radius=3,
        )
        pygame.draw.circle(
            destino,
            (28, 38, 54),
            (x + ancho // 2, base_y - alto),
            ancho // 2,
        )

    def dibujar_fondo_cripta(self, destino=None):
        if destino is None:
            destino = self.pantalla
        w, h = destino.get_width(), destino.get_height()
        
        # Columnas de piedra gótica en bucle continuo (paralaje 0.28)
        col_w = 230
        offset_c = int(self.camara.x * 0.28) % col_w
        for i in range(-1, int(w / col_w) + 2):
            x = i * col_w - offset_c
            pygame.draw.rect(destino, (22, 20, 32), (x, 162, 54, h - 162))
            pygame.draw.rect(destino, (34, 33, 42), (x + 6, 168, 42, h - 168), 2)
            pygame.draw.rect(destino, (24, 23, 30), (x - 8, 152, 70, 14))
            pygame.draw.rect(destino, (24, 23, 30), (x - 4, 136, 62, 10))
            for y in range(192, h, 48):
                pygame.draw.line(destino, (28, 27, 34), (x + 8, y), (x + 46, y), 1)

        # Cadenas colgantes continuas (paralaje 0.40)
        chain_w = 280
        offset_ch = int(self.camara.x * 0.40) % chain_w
        for i in range(-1, int(w / chain_w) + 2):
            x = i * chain_w - offset_ch + 60
            largo = 100 + ((i * 37) % 60)
            for y in range(0, largo, 12):
                pygame.draw.ellipse(destino, (42, 42, 50), (x - 3, y, 6, 12), 1)

        # Resplandor de velas lejanas (paralaje 0.48)
        torch_w = 360
        offset_t = int(self.camara.x * 0.48) % torch_w
        for i in range(-1, int(w / torch_w) + 2):
            x = i * torch_w - offset_t + 110
            base_y = h - 160
            pygame.draw.circle(destino, (58, 42, 18), (x, base_y), 18)
            pygame.draw.circle(destino, (112, 74, 28), (x, base_y), 8)

    def dibujar_fondo_osario(self, destino=None):
        if destino is None:
            destino = self.pantalla
        w, h = destino.get_width(), destino.get_height()
        
        # Arcos de huesos continuos (paralaje 0.22)
        arc_w = 300
        offset_a = int(self.camara.x * 0.22) % arc_w
        for i in range(-1, int(w / arc_w) + 2):
            x = i * arc_w - offset_a
            pygame.draw.arc(destino, (54, 34, 34), (x, 182, 280, 320), 3.14, 6.28, 9)
            pygame.draw.arc(destino, (42, 28, 30), (x + 40, 222, 220, 280), 3.14, 6.28, 5)

        # Cadenas de osario continuas (paralaje 0.38)
        chain_w = 260
        offset_ch = int(self.camara.x * 0.38) % chain_w
        for i in range(-1, int(w / chain_w) + 2):
            x = i * chain_w - offset_ch + 50
            largo = 120 + ((i * 43) % 70)
            pygame.draw.line(destino, (40, 28, 30), (x, 0), (x + 8, largo), 5)
            pygame.draw.line(destino, (40, 28, 30), (x + 8, largo), (x - 12, largo + 24), 3)

        pygame.draw.ellipse(destino, (58, 16, 20), (w // 2 - 260, h - 68, 520, 120))

    def dibujar_niebla(self, destino=None, tema="camposanto"):
        if destino is None:
            destino = self.pantalla
        w, h = destino.get_width(), destino.get_height()
        color = (25, 38, 50) if tema != "osario" else (56, 32, 34)
        alto_niebla = 64
        niebla = pygame.Surface((w, alto_niebla), pygame.SRCALPHA)
        for i in range(alto_niebla):
            alfa = int(24 * (i / alto_niebla))
            pygame.draw.line(niebla, (*color, alfa), (0, i), (w, i))
        destino.blit(niebla, (0, h - alto_niebla), special_flags=pygame.BLEND_RGBA_ADD)

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
            ("TUTORIAL", "El Ritual del Sepulturero · Aprende las mecánicas"),
            ("CRÉDITOS", "Equipo de desarrollo y referencias"),
        ]

        ancho_caja = 560
        alto_caja = 64
        x_caja = (ANCHO - ancho_caja) // 2
        y_base = 200

        for i, (titulo_op, subtitulo_op) in enumerate(opciones):
            y_caja = y_base + i * 84
            rect = pygame.Rect(x_caja, y_caja, ancho_caja, alto_caja)
            seleccionada = (i == self.menu_opcion)

            # Fondo de la opción
            surf_op = pygame.Surface((ancho_caja, alto_caja), pygame.SRCALPHA)
            # Tutorial gets a slightly different hue when not selected
            if i == 2 and not seleccionada:
                color_fondo = (14, 12, 22, 180)
            else:
                color_fondo = (28, 22, 34, 230) if seleccionada else (16, 13, 20, 180)
            pygame.draw.rect(surf_op, color_fondo, (0, 0, ancho_caja, alto_caja), border_radius=8)

            # Tutorial option gets a teal accent border
            if i == 2:
                color_borde = HUD_DASHTURQUESA if seleccionada else (*HUD_DASHTURQUESA[:3], 100)
            else:
                color_borde = HUD_ORO if seleccionada else (*HUD_BORDE, 150)
            grosor_borde = 2 if seleccionada else 1
            pygame.draw.rect(surf_op, color_borde, (0, 0, ancho_caja, alto_caja), grosor_borde, border_radius=8)

            # Detalles ornamentales en opción activa
            if seleccionada:
                accent = HUD_DASHTURQUESA if i == 2 else HUD_ORO
                # Resaltador lateral dorado
                pygame.draw.rect(surf_op, accent, (0, 8, 4, alto_caja - 16), border_radius=2)
                # Remates en esquinas
                for ex, ey, edx, edy in ((0, 0, 1, 1), (ancho_caja, 0, -1, 1), (0, alto_caja, 1, -1), (ancho_caja, alto_caja, -1, -1)):
                    pygame.draw.line(surf_op, accent, (ex + 6 * edx, ey), (ex + 16 * edx, ey), 1)
                    pygame.draw.line(surf_op, accent, (ex, ey + 6 * edy), (ex, ey + 14 * edy), 1)

            self.pantalla.blit(surf_op, (x_caja, y_caja))

            # Textos de la opción
            color_titulo = (HUD_DASHTURQUESA if i == 2 and seleccionada else HUD_ORO) if seleccionada else HUD_TEXTO
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
        self.hud.dibujar(self.pantalla, self, self.dt)

        if self.flash > 0:
            velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            alfa = int(110 * (self.flash / 0.16))
            velo.fill((*self.flash_color, max(0, min(255, alfa))))
            self.pantalla.blit(velo, (0, 0))

        if self.estado == "pausa":
            self.dibujar_overlay(
                "PAUSA",
                "P continuar · R reiniciar nivel · F1 reducir movimiento · ESC volver al menú principal",
            )
        elif self.estado == "nivel_completado":
            self.dibujar_overlay("LA CRIPTA SE ABRE", "ENTER para descender")
        elif self.estado == "sala_completada":
            self.dibujar_overlay(
                "DESAFÍO COMPLETADO",
                "ENTER para continuar · ESC volver al menú",
            )
        elif self.estado == "tutorial_completado":
            self.dibujar_overlay(
                "¡RITUAL COMPLETADO!",
                "El sepulturero ha aprendido su oficio · ENTER para volver al menú",
            )
        elif self.estado == "derrota":
            self.dibujar_derrota()
        elif self.estado == "victoria":
            self.dibujar_victoria()

    # --- Función dibujar_hud (Rediseño Total Gótico Diegético) --- #
    def dibujar_hud(self):
        # 1. Relicario Izquierdo: Vidas del Sepulturero (+10% tamaño)
        self.dibujar_hud_relicario_vidas(24, 16)

        # 2. Relicario Derecho: Almas + Rosario + Sello Dash (+ Arma solo si se posee)
        self.dibujar_hud_relicario_derecho(16)

        # 3. Corona del Custodio (Solo Nivel 3 cuando el jefe está activo)
        if self.jefe is not None and self.jefe.vivo:
            self.dibujar_barra_jefe()

        # 4. Aviso Central del Combate
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
            y_aviso = 98 if self.jefe is not None and self.jefe.vivo else 82
            self.dibujar_texto(
                texto, 0, y_aviso,
                16, color_aviso, centrado=True, sombra=True,
            )

        # 5. Pistas y Avisos Contextuales en la Franja Superior
        if self.mostrar_ayuda > 0 and self.estado == "jugando":
            self.dibujar_pista()

    # --- Módulo HUD: Relicario de Vidas (+20% tamaño) --- #
    def dibujar_hud_relicario_vidas(self, x, y):
        ancho, alto = 344, 68
        panel = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(panel, (14, 11, 18, 220), (0, 0, ancho, alto), border_radius=11)
        pygame.draw.rect(panel, (*HUD_BORDE, 185), (0, 0, ancho, alto), 1, border_radius=11)
        pygame.draw.line(panel, (*HUD_ORO, 120), (12, 1), (ancho - 12, 1), 1)

        # Vértices góticos
        for vx, vy, vdx, vdy in ((0, 0, 1, 1), (ancho, 0, -1, 1), (0, alto, 1, -1), (ancho, alto, -1, -1)):
            pygame.draw.line(panel, HUD_ORO, (vx + 4 * vdx, vy), (vx + 16 * vdx, vy), 1)
            pygame.draw.line(panel, HUD_ORO, (vx, vy + 4 * vdy), (vx, vy + 14 * vdy), 1)
        self.pantalla.blit(panel, (x, y))

        # Rótulo de clase y nivel (+20%)
        self.dibujar_texto("SEPULTURERO", x + 18, y + 8, 14, HUD_ORO)
        nivel_nombre = self.nivel.nombre.upper() if self.nivel else "CAMPOSANTO"
        self.dibujar_texto(nivel_nombre, x + 140, y + 8, 13, HUD_MUTED)

        # Corazones de sangre gótica (+20% radio y espaciado)
        pulso_latido = int(math.sin(self.tiempo_nivel * 9) * 2) if self.jugador.vidas == 1 else 0
        for i in range(VIDAS_MAXIMAS):
            cx = x + 30 + i * 36
            cy = y + 42
            lleno = (i < self.jugador.vidas)
            desp_y = pulso_latido if (i == 0 and self.jugador.vidas == 1) else 0

            # Aura si está en última vida
            if lleno and self.jugador.vidas == 1:
                aura = pygame.Surface((38, 38), pygame.SRCALPHA)
                pygame.draw.circle(aura, (220, 30, 40, int(35 + pulso_latido * 15)), (19, 19), 17)
                self.pantalla.blit(aura, (cx - 19, cy - 19 + desp_y), special_flags=pygame.BLEND_RGBA_ADD)

            self.dibujar_corazon_gotico(cx, cy + desp_y, lleno)

    # --- Módulo HUD: Corazón Gótico (+20% escala, silueta anatómica limpia) --- #
    def dibujar_corazon_gotico(self, cx, cy, lleno):
        r = 7
        top_y = cy - 4
        tip_y = cy + 14

        if lleno:
            color_base = (220, 28, 48)
            color_sombra = (130, 14, 26)
            color_brillo = (255, 110, 130)
            color_destello = (255, 235, 240)
            color_borde = (180, 20, 36)
        else:
            color_base = (34, 26, 36)
            color_sombra = (18, 14, 20)
            color_brillo = (48, 36, 50)
            color_destello = None
            color_borde = (78, 62, 82)

        # Sombra profunda envolvente
        pygame.draw.circle(self.pantalla, color_sombra, (cx - 6, top_y + 1), r + 1)
        pygame.draw.circle(self.pantalla, color_sombra, (cx + 6, top_y + 1), r + 1)
        pygame.draw.polygon(self.pantalla, color_sombra, [(cx - 12, top_y + 1), (cx + 12, top_y + 1), (cx, tip_y + 1)])

        # Cuerpo del corazón
        pygame.draw.circle(self.pantalla, color_base, (cx - 6, top_y), r)
        pygame.draw.circle(self.pantalla, color_base, (cx + 6, top_y), r)
        pygame.draw.polygon(self.pantalla, color_base, [(cx - 11, top_y), (cx + 11, top_y), (cx, tip_y)])

        # Borde exterior integral (sigue todo el contorno del corazón, sin triángulos sueltos)
        pygame.draw.line(self.pantalla, color_borde, (cx - 11, top_y), (cx, tip_y), 1)
        pygame.draw.line(self.pantalla, color_borde, (cx + 11, top_y), (cx, tip_y), 1)
        pygame.draw.arc(self.pantalla, color_borde, (cx - 6 - r, top_y - r, r * 2, r * 2), 0, 3.14, 1)
        pygame.draw.arc(self.pantalla, color_borde, (cx + 6 - r, top_y - r, r * 2, r * 2), 0, 3.14, 1)

        # Destellos o hueco interno
        if lleno and color_destello:
            pygame.draw.circle(self.pantalla, color_destello, (cx - 3, top_y - 3), 2)
            pygame.draw.circle(self.pantalla, color_brillo, (cx + 4, top_y - 2), 2)
        else:
            pygame.draw.circle(self.pantalla, (20, 16, 22), (cx - 5, top_y), 3)
            pygame.draw.circle(self.pantalla, (20, 16, 22), (cx + 5, top_y), 3)

    # --- Módulo HUD: Relicario Derecho (Almas + Rosario + Dash + Arma opcional) (+20%) --- #
    def dibujar_hud_relicario_derecho(self, y):
        tiene_arma = self.jugador.tiene_pala
        ancho = 542 if tiene_arma else 404
        alto = 68
        x = ANCHO - ancho - 24

        panel = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(panel, (14, 11, 18, 220), (0, 0, ancho, alto), border_radius=11)
        pygame.draw.rect(panel, (*HUD_BORDE, 185), (0, 0, ancho, alto), 1, border_radius=11)
        pygame.draw.line(panel, (*HUD_ORO, 120), (12, 1), (ancho - 12, 1), 1)

        for vx, vy, vdx, vdy in ((0, 0, 1, 1), (ancho, 0, -1, 1), (0, alto, 1, -1), (ancho, alto, -1, -1)):
            pygame.draw.line(panel, HUD_ORO, (vx + 4 * vdx, vy), (vx + 16 * vdx, vy), 1)
            pygame.draw.line(panel, HUD_ORO, (vx, vy + 4 * vdy), (vx, vy + 14 * vdy), 1)
        self.pantalla.blit(panel, (x, y))

        # Icono de alma espectral en rombo (+20%)
        ix, iy = x + 22, y + 34
        panel_alma = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.circle(panel_alma, (70, 230, 215, 55), (22, 22), 20)
        self.pantalla.blit(panel_alma, (ix - 22, iy - 22))
        pygame.draw.polygon(self.pantalla, HUD_ALMA, [(ix, iy - 13), (ix + 10, iy), (ix, iy + 13), (ix - 10, iy)])
        pygame.draw.polygon(self.pantalla, (230, 255, 250), [(ix, iy - 6), (ix + 4, iy), (ix, iy + 6), (ix - 4, iy)])

        # Contador de Almas (+20%)
        total = self.nivel.total_almas if self.nivel else 24
        self.dibujar_texto(f"ALMAS  {self.jugador.almas} / {total}", x + 44, y + 8, 15, HUD_ORO)

        # Rosario de 10 Cuentas de Ánima (+20% espaciado y tamaño)
        rx = x + 48
        ry = y + 42
        pulso_resurreccion = 0.5 + 0.5 * math.sin(self.tiempo_nivel * 8)
        for i in range(ALMAS_POR_VIDA):
            bx = rx + i * 20
            by = ry
            llena = (i < self.jugador.almas_para_vida)

            if llena:
                color_perla = (80, 235, 215)
                radio = 5
                if self.jugador.almas_para_vida >= 8:
                    radio = 5 + int(pulso_resurreccion * 2)
                pygame.draw.circle(self.pantalla, color_perla, (bx, by), radio)
                pygame.draw.circle(self.pantalla, (230, 255, 250), (bx - 1, by - 1), max(1, radio - 2))
            else:
                pygame.draw.circle(self.pantalla, (42, 34, 46), (bx, by), 4)
                pygame.draw.circle(self.pantalla, (22, 18, 26), (bx, by), 4, 1)

        # Divisoria vertical de hierro hacia Sello DASH
        pygame.draw.line(self.pantalla, (*HUD_BORDE, 160), (x + 280, y + 8), (x + 280, y + alto - 8), 1)

        # SELLO DE DASH (+20%)
        dx_box = x + 292
        dash_listo = self.jugador.dash_listo()
        color_dash = HUD_DASHTURQUESA if dash_listo else HUD_MUTED

        # Ala rúnica de dash (+20%)
        pygame.draw.polygon(self.pantalla, color_dash, [(dx_box + 2, y + 44), (dx_box + 16, y + 20), (dx_box + 22, y + 27), (dx_box + 9, y + 48)])
        pygame.draw.polygon(self.pantalla, color_dash, [(dx_box + 18, y + 31), (dx_box + 29, y + 17), (dx_box + 33, y + 24), (dx_box + 23, y + 39)])

        self.dibujar_texto("DASH", dx_box + 34, y + 8, 13, HUD_MUTED)
        estado_dash = "LISTO" if dash_listo else f"{1.0 - (self.jugador.dash_cooldown / DASH_COOLDOWN):.1f}"
        self.dibujar_texto(estado_dash, dx_box + 34, y + 34, 15, color_dash)

        # SELLO DE ARMA (Solo si tiene pala) (+20%)
        if tiene_arma:
            pygame.draw.line(self.pantalla, (*HUD_BORDE, 160), (x + 412, y + 8), (x + 412, y + alto - 8), 1)
            ax_box = x + 424
            es_guadaña = getattr(self.jugador, "rango_ataque_mejorado", False)
            color_arma = (215, 85, 255) if es_guadaña else HUD_ORO
            etiqueta = "GUADAÑA +" if es_guadaña else "PALA"

            if es_guadaña:
                # Guadaña mística púrpura (+20%)
                pygame.draw.arc(self.pantalla, color_arma, (ax_box + 2, y + 15, 34, 34), 0, 3.14, 4)
                pygame.draw.line(self.pantalla, (130, 50, 160), (ax_box + 20, y + 30), (ax_box + 8, y + 52), 3)
            else:
                # Pala plateada (+20%)
                pygame.draw.line(self.pantalla, (160, 120, 60), (ax_box + 8, y + 50), (ax_box + 22, y + 22), 3)
                pygame.draw.polygon(self.pantalla, (190, 190, 205), [(ax_box + 18, y + 20), (ax_box + 31, y + 15), (ax_box + 26, y + 32)])

            self.dibujar_texto(etiqueta, ax_box + 34, y + 8, 13, color_arma)
            estado_ataque = "LISTO" if self.jugador.ataque_cooldown <= 0 else "..."
            self.dibujar_texto(estado_ataque, ax_box + 34, y + 34, 15, HUD_VERDE if self.jugador.ataque_cooldown <= 0 else HUD_MUTED)

    # --- Módulo HUD: Barra Imperial del Custodio (+20% escala) --- #
    def dibujar_barra_jefe(self):
        ancho, alto = 660, 76
        x = (ANCHO - ancho) // 2
        y = 16

        panel = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(panel, (16, 12, 20, 230), (0, 0, ancho, alto), border_radius=12)
        color_borde = (215, 45, 55) if self.jefe.fase >= 2 else (*HUD_BORDE, 200)
        pygame.draw.rect(panel, color_borde, (0, 0, ancho, alto), 2 if self.jefe.fase >= 2 else 1, border_radius=12)

        # Corona de oro en el borde superior
        pygame.draw.line(panel, HUD_ORO, (16, 1), (ancho - 16, 1), 1)
        self.pantalla.blit(panel, (x, y))

        # Nombre y fase (+20%)
        nombre_color = HUD_ROJO if self.jefe.fase >= 2 else HUD_ORO
        self.dibujar_texto("EL CUSTODIO DEL OSARIO", x + 22, y + 9, 17, nombre_color, sombra=True)

        if self.jefe.fase >= 2:
            fase_txt = "FASE II · ¡LA PALA REBOTA! SOLO PISOTÓN"
            fase_color = (250, 65, 65)
        else:
            fase_txt = "FASE I · VULNERABLE A PALA Y PISOTÓN"
            fase_color = HUD_MUTED
        self.dibujar_texto(fase_txt, x + ancho - 340, y + 11, 13, fase_color)

        # 6 Celdas de Salud (Losas de Osario con Rubí) (+20%)
        ancho_celda = 98
        alto_celda = 15
        y_celdas = y + 44
        for i in range(6):
            cx = x + 22 + i * (ancho_celda + 6)
            rect_celda = pygame.Rect(cx, y_celdas, ancho_celda, alto_celda)
            llena = (i < self.jefe.vida)

            if llena:
                color_rubi = (225, 38, 52)
                pygame.draw.rect(self.pantalla, color_rubi, rect_celda, border_radius=4)
                pygame.draw.rect(self.pantalla, (255, 105, 120), (rect_celda.x + 2, rect_celda.y + 2, rect_celda.width - 4, 3), border_radius=2)
                pygame.draw.rect(self.pantalla, (120, 18, 28), rect_celda, 1, border_radius=4)
            else:
                pygame.draw.rect(self.pantalla, (36, 26, 30), rect_celda, border_radius=4)
                pygame.draw.rect(self.pantalla, (22, 16, 20), rect_celda, 1, border_radius=4)

    # --- Función dibujar_pista (Ubicación Superior Contextual) (+20%) --- #
    def dibujar_pista(self):
        texto = getattr(self, "texto_ayuda", None) or (self.nivel.pista if self.nivel else "")
        if not texto:
            return

        # Máximo 2 líneas visibles para no bloquear el área de juego
        lineas_todas = textwrap.wrap(texto, width=64)
        lineas = lineas_todas[:2]
        alto = 26 + 20 * len(lineas)
        ancho = 640
        x = (ANCHO - ancho) // 2
        y = 98 if (self.jefe is not None and self.jefe.vivo) else 16

        # Fade suave al desaparecer
        alpha = int(225 * min(1.0, self.mostrar_ayuda / 0.8)) if self.mostrar_ayuda < 0.8 else 225

        caja = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(caja, (14, 11, 18, alpha), (0, 0, ancho, alto), border_radius=10)
        pygame.draw.rect(caja, (*HUD_BORDE, min(200, alpha)), (0, 0, ancho, alto), 1, border_radius=10)
        pygame.draw.rect(caja, (*HUD_ORO, alpha), (0, 0, 4, alto), border_radius=2)
        self.pantalla.blit(caja, (x, y))

        self.dibujar_texto("GUÍA DEL SEPULTURERO", x + 16, y + 5, 11, HUD_ORO)
        for i, linea in enumerate(lineas):
            self.dibujar_texto(linea, x + 16, y + 21 + i * 20, 13, HUD_TEXTO)

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

    # --- Función dibujar_victoria --- #
    def dibujar_victoria(self):
        """Pantalla de victoria estilizada con panel gótico y estadísticas completas."""
        import math as _math

        # Oscurecer el fondo
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((5, 4, 10, 215))
        self.pantalla.blit(overlay, (0, 0))

        # Partículas de estrellas doradas (estáticas pero rotadas con tiempo)
        t = self.tiempo_total
        for i in range(14):
            ang = (i / 14) * _math.tau + t * 0.18
            rx = ANCHO // 2 + int(_math.cos(ang) * 300)
            ry = ALTO // 2 + int(_math.sin(ang) * 160)
            radio = 3 if i % 3 == 0 else 2
            alpha = int(120 + 80 * _math.sin(ang * 1.7 + t))
            s = pygame.Surface((radio * 2 + 2, radio * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*ORO, alpha), (radio + 1, radio + 1), radio)
            self.pantalla.blit(s, (rx - radio - 1, ry - radio - 1))

        # Panel central
        pw, ph = 680, 430
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (12, 10, 16, 240), (0, 0, pw, ph), border_radius=14)
        pygame.draw.rect(panel, (*ORO, 200), (0, 0, pw, ph), 2, border_radius=14)
        pygame.draw.line(panel, (*ORO, 120), (20, 1), (pw - 20, 1), 1)
        pygame.draw.line(panel, (*ORO, 120), (20, ph - 1), (pw - 20, ph - 1), 1)
        # Remates de esquina
        for cx_, cy_, dx_, dy_ in ((0, 0, 1, 1), (pw, 0, -1, 1), (0, ph, 1, -1), (pw, ph, -1, -1)):
            pygame.draw.line(panel, ORO, (cx_ + 8 * dx_, cy_), (cx_ + 28 * dx_, cy_), 1)
            pygame.draw.line(panel, ORO, (cx_, cy_ + 8 * dy_), (cx_, cy_ + 26 * dy_), 1)
        self.pantalla.blit(panel, (px, py))

        # Título
        self.dibujar_texto("¡EL SEPULTURERO ESCAPÓ!", 0, py + 24, 38, ORO, centrado=True, sombra=True)
        self.dibujar_texto("IN CRYPTA · COMPLETADO", 0, py + 68, 15, CREMA, centrado=True)
        pygame.draw.line(self.pantalla, (*ORO, 140),
                         (px + 30, py + 94), (px + pw - 30, py + 94), 1)

        # Stats
        tiempo_min = int(self.tiempo_total) // 60
        tiempo_seg = int(self.tiempo_total) % 60
        tiempo_dec = int((self.tiempo_total - int(self.tiempo_total)) * 10)
        stats = [
            ("ALMAS TOTALES",   f"{self.almas_totales}",                         HUD_ORO),
            ("TIEMPO TOTAL",    f"{tiempo_min:02d}:{tiempo_seg:02d}.{tiempo_dec}", CREMA),
            ("VIDAS RESTANTES", f"{self.jugador.vidas if self.jugador else 0}",    HUD_VERDE),
        ]

        y_stat = py + 114
        for etiqueta, valor, color in stats:
            self.dibujar_texto(etiqueta, px + 50, y_stat, 14, HUD_MUTED)
            self.dibujar_texto(valor, px + pw - 50, y_stat, 20, color, sombra=True, derecha=True)
            pygame.draw.line(self.pantalla, (*HUD_BORDE, 90),
                             (px + 30, y_stat + 26), (px + pw - 30, y_stat + 26), 1)
            y_stat += 52

        # Calificación / rango (dorado, plata, hueso según tiempo)
        if self.tiempo_total < 300:
            rango, color_rango = "S · MAESTRO DEL OSARIO", ORO
        elif self.tiempo_total < 540:
            rango, color_rango = "A · SEPULTURERO EXPERTO", (192, 192, 192)
        elif self.tiempo_total < 840:
            rango, color_rango = "B · EXPLORADOR DE CRIPTAS", CREMA
        else:
            rango, color_rango = "C · EL OSARIO TE PUSO A PRUEBA", HUESO

        y_rango = y_stat + 10
        pygame.draw.rect(self.pantalla, (20, 16, 26),
                         (px + 30, y_rango, pw - 60, 44), border_radius=8)
        pygame.draw.rect(self.pantalla, (*color_rango, 180),
                         (px + 30, y_rango, pw - 60, 44), 1, border_radius=8)
        self.dibujar_texto(f"RANGO {rango}", 0, y_rango + 11, 17, color_rango, centrado=True, sombra=True)

        # Pie
        self.dibujar_texto("ENTER · Volver al menú principal · ESC · Salir",
                           0, py + ph - 30, 13, HUD_MUTED, centrado=True)

    # --- Función dibujar_derrota --- #
    def dibujar_derrota(self):
        """Pantalla de derrota estilizada con panel gótico, causas y estadísticas."""
        # Oscurecer fondo con velo fúnebre carmesí
        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((10, 4, 6, 225))
        self.pantalla.blit(velo, (0, 0))

        # Panel central heráldico
        pw, ph = 680, 440
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (18, 10, 14, 245), (0, 0, pw, ph), border_radius=14)
        pygame.draw.rect(panel, (160, 40, 50, 220), (0, 0, pw, ph), 2, border_radius=14)
        pygame.draw.line(panel, (*HUD_ORO, 120), (20, 1), (pw - 20, 1), 1)
        pygame.draw.line(panel, (*HUD_ORO, 120), (20, ph - 1), (pw - 20, ph - 1), 1)

        # Ornamentos en esquinas
        for cx_, cy_, dx_, dy_ in ((0, 0, 1, 1), (pw, 0, -1, 1), (0, ph, 1, -1), (pw, ph, -1, -1)):
            pygame.draw.line(panel, HUD_ORO, (cx_ + 8 * dx_, cy_), (cx_ + 26 * dx_, cy_), 1)
            pygame.draw.line(panel, HUD_ORO, (cx_, cy_ + 8 * dy_), (cx_, cy_ + 26 * dy_), 1)
        self.pantalla.blit(panel, (px, py))

        # Título fúnebre
        self.dibujar_texto("LA OSCURIDAD TE RECLAMA", 0, py + 24, 34, HUD_ROJO, centrado=True, sombra=True)
        causa = getattr(self, "causa_muerte", "") or "Peligros de la cripta"
        self.dibujar_texto(f"CAUSA: {causa.upper()}", 0, py + 68, 14, CREMA, centrado=True)
        pygame.draw.line(self.pantalla, (160, 40, 50, 180),
                         (px + 30, py + 94), (px + pw - 30, py + 94), 1)

        # Estadísticas del intento
        tiempo_min = int(self.tiempo_total) // 60
        tiempo_seg = int(self.tiempo_total) % 60
        tiempo_dec = int((self.tiempo_total - int(self.tiempo_total)) * 10)

        nombre_nivel = "RITUAL DEL SEPULTURERO" if self.es_tutorial else (
            f"NIVEL {self.nivel_indice + 1} — {self.nivel.nombre.upper()}" if self.nivel and hasattr(self.nivel, "nombre") else "DESAFÍO"
        )
        stats = [
            ("LUGAR DE CAÍDA", nombre_nivel, HUD_ORO),
            ("TIEMPO SOBREVIVIDO", f"{tiempo_min:02d}:{tiempo_seg:02d}.{tiempo_dec}", CREMA),
            ("ALMAS TOTALES COSECHADAS", f"{self.almas_totales}", HUD_ORO),
            ("CAÍDAS TOTALES", f"{self.muertes_totales}", HUD_ROJO),
        ]

        y_stat = py + 114
        for etiqueta, valor, color in stats:
            self.dibujar_texto(etiqueta, px + 50, y_stat, 14, HUD_MUTED)
            self.dibujar_texto(valor, px + pw - 50, y_stat, 18, color, sombra=True, derecha=True)
            pygame.draw.line(self.pantalla, (80, 25, 35, 120),
                             (px + 30, y_stat + 28), (px + pw - 30, y_stat + 28), 1)
            y_stat += 52

        # Separador inferior y llamada a la acción
        pygame.draw.line(self.pantalla, (160, 40, 50, 160),
                         (px + 30, py + 372), (px + pw - 30, py + 372), 1)
        self.dibujar_texto("ENTER: REINTENTAR · ESC: VOLVER AL MENÚ",
                           0, py + 396, 16, HUD_ORO, centrado=True, sombra=True)

    # --- Función dibujar_texto --- #
    def dibujar_texto(self, texto, x, y, tamano=24, color=BLANCO, centrado=False, sombra=False, derecha=False):
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
            elif derecha:
                rect_sombra.topright = (x + 3, y + 3)
            else:
                rect_sombra.topleft = (x + 3, y + 3)
            self.pantalla.blit(imagen_sombra, rect_sombra)

        imagen = self.fuentes[tamano].render(texto, True, color)
        rect = imagen.get_rect()
        if centrado:
            rect.center = (ANCHO // 2, y)
        elif derecha:
            rect.topright = (x, y)
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
            self.dt = dt
            self.hud.actualizar(dt)
            self.dibujar()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


# --- Arranque directo --- #
if __name__ == "__main__":
    Juego().run()
