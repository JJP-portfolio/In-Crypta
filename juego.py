#---- Importamos librerias y modulos ----#
from collections import OrderedDict
import os
from pathlib import Path
import sys
import warnings

import pygame

from audio import Audio
from camara import Camara
import config
from config import (
    ALTO,
    ANCHO,
    CAMARA_ZOOM,
    CITAS_POE,
    FPS,
    JEFE_VIDA,
    MAX_DT,
    OSARIO_VERTICAL,
    TILE,
    TITULO,
    VIDAS_INICIALES,
    VIRTUAL_ALTO,
    VIRTUAL_ANCHO,
)
from entidades import Jugador
from escena.constantes import (
    ALMAS_MINIJEFE,
    OPCIONES_CALIDAD,
    OPCIONES_HUD,
    OPCIONES_SHADER,
    PRESETS_TECLADO,
    PRESET_MODERNO,
    PRESET_RETRO,
    TECLAS_ATAQUE,
    TECLAS_SALTO,
    TOLERANCIA_PISOTON,
)
from escena.fondos import (
    FondosMixin,
    ParticulaBioma,
    _CACHE_HAZ_LUNAR,
    _CACHE_LUCES_JUEGO,
    _obtener_haz_lunar,
    _obtener_luz_calida,
    _obtener_luz_perforacion,
)
from escena.menus import MenusMixin
from escena.pantallas import PantallasMixin
from escena.render_mundo import RenderMundoMixin
from hud import HudOrquestador
from logica.combate import CombateMixin
from logica.jefes import JefesMixin
from logica.mundo import MundoMixin
from nivel import Nivel
from niveles import NIVELES, NIVELES_VERTICALES, NIVEL_TUTORIAL, SALAS_PRUEBA
from particulas import SistemaParticulas


#---- Constantes y cache de texto ----#
TEXTO_CACHE_MAX = 256


def renderizar_texto_cacheado(cache, fuente, tamano, texto, color, maximo=TEXTO_CACHE_MAX):
    """Renderiza texto con caché LRU acotado.

    La pantalla de título y los menús repiten los mismos textos cuadro a cuadro,
    y rasterizar TTF cada frame es caro en WASM. Las superficies cacheadas solo
    se leen (get_rect y blit), así que reutilizarlas no cambia el resultado.
    """
    clave = (tamano, texto, tuple(color))
    imagen = cache.get(clave)
    if imagen is not None:
        cache.move_to_end(clave)
        return imagen
    imagen = fuente.render(texto, True, color)
    cache[clave] = imagen
    if len(cache) > maximo:
        cache.popitem(last=False)
    return imagen


#---- Clase Juego ----#
# Franja de piso: bloques de 18 filas. Los niveles de 18 filas tienen una sola
# franja, así que este filtro no cambia su comportamiento.
def _mismo_piso(rect, y_referencia):
    banda = 18 * TILE
    return rect.y // banda == int(y_referencia) // banda


class Juego(
    MenusMixin,
    FondosMixin,
    PantallasMixin,
    RenderMundoMixin,
    CombateMixin,
    JefesMixin,
    MundoMixin,
):
    """Orquestador principal de escenas, bucle y estado de IN CRYPTA."""

    def __init__(self, sala_inicial=None):
        """Inicializa Pygame, recursos graficos, estado inicial y escena."""
        self._iniciar_pygame()
        self._iniciar_estado_partida()
        self._iniciar_configuracion()
        self._cargar_escena_inicial(sala_inicial)

    def _iniciar_pygame(self):
        warnings.filterwarnings("ignore", category=UserWarning)
        os.environ.setdefault("SDL_VIDEO_WAYLAND_WMCLASS", "in-crypta")
        os.environ.setdefault("SDL_VIDEO_X11_WMCLASS", "in-crypta")
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.pre_init(44100, -16, 2, 2048)
        except (pygame.error, OSError):
            # En entornos sin dispositivo de audio seguimos sin preinicializar el mezclador.
            pass
        pygame.init()
        es_dummy = os.environ.get("SDL_VIDEODRIVER") == "dummy"
        self._display_flags = 0 if es_dummy else (pygame.SCALED | pygame.RESIZABLE)
        self._pantalla_completa = False
        try:
            self.pantalla = pygame.display.set_mode((ANCHO, ALTO), self._display_flags)
        except pygame.error:
            self._display_flags = 0
            self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO)
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        self.fuentes = {}
        self._cache_texto = OrderedDict()
        ruta_cfg = getattr(config, "RUTA_FUENTE_GOTICA", "assets/NotoSerif-Bold.ttf")
        p_font = Path(__file__).resolve().parent / ruta_cfg
        self._ruta_fuente_gotica = str(p_font) if p_font.exists() else None
        self.fondos = {}
        self.vineta = self.crear_vineta(90)
        self.vineta_carmesi = self.crear_vineta_carmesi()
        self.mascara_penumbra = pygame.Surface((VIRTUAL_ANCHO, VIRTUAL_ALTO), pygame.SRCALPHA)
        self.superficie_flash = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        self.superficie_mundo = pygame.Surface((VIRTUAL_ANCHO, VIRTUAL_ALTO))
        self._superficie_scanlines = self._crear_scanlines_goticas(ANCHO, ALTO)
        self._superficie_destello_manto = None

    def _iniciar_estado_partida(self):
        self.hitstop = 0.0
        self.timer_corazon = 0.0
        self.particulas = SistemaParticulas()
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
        self.destello_manto = 0.0
        self.jefe = None
        self.ondas_jefe = []
        self.punto_reintento = None
        self.almas_consagradas = 0
        self.almas_vida_consagradas = 0
        self.aviso_jefe = 0.0
        self.hud_aviso_altar = 0.0
        self.sala_prueba = False
        self.sala_prueba_indice = None
        self.es_tutorial = False
        self.reducir_movimiento = False
        self.muertes_totales = 0
        self.causa_muerte = ""
        self.almas_combo_count = 0
        self.almas_combo_timer = 0.0
        self.campanas_combo_count = 0
        self.campanas_combo_timer = 0.0
        self.continues = getattr(config, "CONTINUES_INICIALES", 2)

    def _iniciar_configuracion(self):
        self.test_opcion = 0
        self.menu_opcion = 0
        self.pausa_opcion = 0
        self.derrota_opcion = 0
        self.en_campaña = False
        self.nivel_seleccionado = 0
        self.tiempo_menu = 0.0
        self.preset_teclado_idx = 0
        self.config_opcion = 0
        self.config_shader_idx = 0
        self.config_calidad_idx = 0
        factores_calidad = {0: 1.0, 1: 0.5, 2: 0.25}
        self.particulas.factor_calidad = factores_calidad[self.config_calidad_idx]
        self.config_hud_idx = 0
        self.origen_configuracion = "menu"
        self.teclas_salto = PRESETS_TECLADO[0]["teclas_salto"]
        self.teclas_dash = PRESETS_TECLADO[0]["teclas_dash"]
        self.teclas_ataque = PRESETS_TECLADO[0]["teclas_ataque"]
        self.particulas_bioma = []
        self.reiniciar_particulas_bioma("camposanto")
        self.debug_colisiones = False
        self.estilos_visuales = ("AUTO", "NES", "SNES", "PROC")
        self.estilo_visual_idx = 0
        self.escala_fuente_idx = 0
        self._escala_fuente_cache = getattr(config, "ESCALA_FUENTES_ACTIVA", 1.15)

    def _cargar_escena_inicial(self, sala_inicial):
        if sala_inicial is not None:
            self.cargar_sala_prueba(sala_inicial)
        else:
            self.cargar_nivel(0, vidas=VIDAS_INICIALES)
            self.estado = "titulo"
            self.mostrar_ayuda = 0.0
            self.audio.detener_dron()
            self.audio.reproducir_musica("titulo", bucle=True, fade_ms=600)

        calidad = OPCIONES_CALIDAD[self.config_calidad_idx]
        shader = OPCIONES_SHADER[self.config_shader_idx]
        print("[IN CRYPTA] Motor de juego inicializado.")
        print(
            f"[IN CRYPTA] Pygame: {pygame.__version__} | "
            f"Canvas virtual: {VIRTUAL_ANCHO}x{VIRTUAL_ALTO} (Zoom {CAMARA_ZOOM}x)"
        )
        print(f"[IN CRYPTA] Calidad inicial: {calidad} | Shader: {shader}")
        print("[IN CRYPTA] Audio: Procedural + Banco SFX/Musica cargado.")

    def _renderizar_texto_cache(self, fuente, tamano, texto, color):
        """Delega la cache de texto al helper expuesto en juego.py."""
        return renderizar_texto_cacheado(
            self._cache_texto, fuente, tamano, texto, color
        )

    def _es_mismo_piso(self, rect, y_referencia):
        """Comprueba si un rectangulo pertenece a la misma franja vertical."""
        return _mismo_piso(rect, y_referencia)

    def _inicializar_estado_nivel(self, vidas_iniciales, tiene_pala, tiene_dash):
        """Inicializa jugador, cámara, audio y contadores al entrar a un nivel o preludio."""
        self.reiniciar_particulas_bioma(self.nivel.tema)
        self.jugador = Jugador(*self.nivel.spawn, vidas=vidas_iniciales)
        self.jugador.tiene_pala = tiene_pala
        self.jugador.tiene_dash = tiene_dash
        self.aplicar_preset_teclado(getattr(self, "preset_teclado_idx", 0))
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
        self.almas_consagradas = 0
        self.almas_vida_consagradas = 0
        self.aviso_jefe = 0.0
        self.hud_aviso_altar = 0.0
        self.campanas_combo_count = 0
        self.campanas_combo_timer = 0.0
        self.derrota_opcion = 0
        self.tiempo_en_borde_fe = 0.0
        self.pista_fe_mostrada = False
        self._jefe_victoria_procesada = False
        self.audio.iniciar_dron()
        self.audio.reproducir_musica(self.nivel.tema, bucle=True, fade_ms=800)

    def cargar_nivel(self, indice, vidas=None, sala=None):
        self.sala_prueba = sala is not None
        self.sala_prueba_indice = sala
        self.es_tutorial = False
        if sala is None:
            self.nivel_indice = indice
            datos = NIVELES[indice]
            if indice == 2 and OSARIO_VERTICAL and len(NIVELES_VERTICALES) > 0:
                datos = NIVELES_VERTICALES[0]
            tiene_pala = indice >= 2
            tiene_dash = indice >= 1
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
        self._inicializar_estado_nivel(vidas_iniciales, tiene_pala, tiene_dash)
        cita = CITAS_POE.get(self.nivel_indice, "")
        if cita:
            self.hud.mostrar_mensaje(cita, 2, 5.5)

    def iniciar_tutorial(self):
        """Carga el nivel tutorial. No cuenta para la partida principal."""
        self.es_tutorial = True
        self.sala_prueba = False
        self.sala_prueba_indice = None
        self.almas_totales = 0
        self.tiempo_total = 0.0
        self.nivel_indice = 0
        self.tutorial_zona_actual = None
        self.nivel = Nivel(
            NIVEL_TUTORIAL,
            "El Ritual del Sepulturero",
            "El Umbral del Sepulturero · Preludio del Descenso",
            "camposanto",
        )
        self._inicializar_estado_nivel(VIDAS_INICIALES, False, False)
        self.mostrar_ayuda = 3.5
        cita = CITAS_POE.get("tutorial", "")
        if cita:
            self.hud.mostrar_mensaje(cita, 1, 5.0)
        else:
            self.hud.mostrar_mensaje(
                "El Umbral del Sepulturero · Avanza hacia las catacumbas", 1, 5.0
            )

    def seleccionar_nivel(self, indice):
        if indice in (-1, "preludio", "tutorial"):
            self.iniciar_tutorial()
            return
        if indice in (4, "salas", "pruebas"):
            self.abrir_selector_pruebas()
            return
        self.almas_totales = 0
        self.tiempo_total = 0.0
        self.continues = getattr(config, "CONTINUES_INICIALES", 2)
        self.derrota_opcion = 0
        self.cargar_nivel(indice, vidas=VIDAS_INICIALES)
        self.estado = "jugando"

    def cargar_sala_prueba(self, indice):
        self.cargar_nivel(SALAS_PRUEBA[indice]["nivel"], vidas=VIDAS_INICIALES, sala=indice)
        self.estado = "jugando"

    def iniciar_campaña(self):
        """Inicia la campaña narrativa completa comenzando en el Preludio."""
        self.almas_totales = 0
        self.tiempo_total = 0.0
        self.continues = getattr(config, "CONTINUES_INICIALES", 2)
        self.derrota_opcion = 0
        self.jugador = None
        self.en_campaña = True
        self.iniciar_tutorial()

    def reiniciar_juego(self):
        self.almas_totales = 0
        self.tiempo_total = 0.0
        self.continues = getattr(config, "CONTINUES_INICIALES", 2)
        self.derrota_opcion = 0
        self.jugador = None
        self.cargar_nivel(0, vidas=VIDAS_INICIALES)

    def _reiniciar_nivel_actual(self):
        """Reinicia desde el principio la sala de prueba, el preludio o el nivel en curso."""
        if self.sala_prueba:
            self.cargar_sala_prueba(self.sala_prueba_indice)
        elif self.es_tutorial:
            self.iniciar_tutorial()
        else:
            self.cargar_nivel(self.nivel_indice, vidas=VIDAS_INICIALES)

    def siguiente_nivel(self):
        self.almas_totales += self.jugador.almas
        if self.nivel_indice + 1 >= len(NIVELES):
            self.estado = "victoria"
            self.audio.reproducir_musica("victoria", bucle=False, fade_ms=500)
            return
        self.cargar_nivel(self.nivel_indice + 1, vidas=self.jugador.vidas)

    def procesar_eventos(self):
        handlers_pantalla = {
            "menu": self._manejar_tecla_menu,
            "configuracion": self._manejar_tecla_configuracion,
            "pausa": self._manejar_tecla_pausa,
            "seleccion_nivel": self._manejar_tecla_seleccion_nivel,
            "test_selector": self._manejar_tecla_test_selector,
            "derrota": self._manejar_tecla_derrota,
        }
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F11:
                    self.alternar_pantalla_completa()
                    continue
                if self.estado == "creditos":
                    if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        self.abrir_menu()
                    continue
                handler = handlers_pantalla.get(self.estado)
                if handler is not None:
                    handler(evento.key)
                    continue
                self._manejar_tecla_global(evento.key)
            elif evento.type == pygame.KEYUP:
                if evento.key in getattr(self, "teclas_salto", TECLAS_SALTO) and self.jugador is not None:
                    self.jugador.soltar_salto()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1 and self.estado == "jugando":
                    self.intentar_ataque()

    def _descontar_temporizadores_globales(self, dt):
        if hasattr(self, "hud") and self.hud is not None:
            self.hud.actualizar(dt)
        for campo in ("flash", "destello_manto", "aviso_jefe", "hud_aviso_altar"):
            valor = getattr(self, campo, 0.0)
            if valor > 0:
                setattr(self, campo, max(0.0, valor - dt))

    def _actualizar_latido_y_combos(self, dt):
        if self.jugador and self.jugador.vidas == 1:
            self.timer_corazon += dt
            if self.timer_corazon >= (1.0 / 1.2):
                self.timer_corazon = 0.0
                self.audio.reproducir("corazon")
        else:
            self.timer_corazon = 0.0

        self._dt_actual = dt
        self.tiempo_nivel += dt
        self.tiempo_total += dt
        if self.nivel and getattr(self.nivel, "tema", None):
            self.audio.asegurar_musica_activa(self.nivel.tema)

        if self.almas_combo_timer > 0:
            self.almas_combo_timer = max(0.0, self.almas_combo_timer - dt)
            if self.almas_combo_timer <= 0:
                self.almas_combo_count = 0

        if self.campanas_combo_timer > 0:
            self.campanas_combo_timer = max(0.0, self.campanas_combo_timer - dt)
            if self.campanas_combo_timer <= 0:
                self.campanas_combo_count = 0

    def _actualizar_particulas_bioma_juego(self, dt):
        intensificar = False
        if getattr(self.nivel, "tema", "") == "osario" and self.jugador:
            en_arena = (
                abs(self.jugador.rect.centerx - self.jefe.rect.centerx) <= 22 * TILE
                if (
                    OSARIO_VERTICAL
                    and getattr(self, "nivel_indice", 0) == 2
                    and self.jefe is not None
                )
                else (self.jugador.rect.x >= 268 * TILE)
            )
            if self.jefe is not None and (self.jefe.vida < JEFE_VIDA or en_arena):
                intensificar = True
        for particula in getattr(self, "particulas_bioma", []):
            particula.actualizar(dt, intensificar=intensificar)

    def _resolver_meta_nivel(self):
        if self.jefe is not None and self.jefe.vivo:
            if self.aviso_jefe <= 0:
                self.aviso_jefe = 2.2
                self.audio.reproducir("ui")
            return

        self.audio.reproducir("meta")
        self.particulas.meta(self.nivel.meta.centerx, self.nivel.meta.centery)
        if self.es_tutorial:
            if getattr(self, "en_campaña", False):
                self.almas_totales += self.jugador.almas
                self.cargar_nivel(0, vidas=self.jugador.vidas)
                self.hud.mostrar_mensaje(
                    "¡UMBRAL SUPERADO! · Adentrándose en El Camposanto", 2, 4.0
                )
            else:
                self.estado = "tutorial_completado"
        elif self.sala_prueba:
            self.estado = "sala_completada"
        elif self.nivel_indice + 1 >= len(NIVELES):
            self.almas_totales += self.jugador.almas
            self.estado = "victoria"
            self.audio.reproducir_musica("victoria", bucle=False, fade_ms=500)
        else:
            self.estado = "nivel_completado"

    def _actualizar_objetos_y_progreso(self, dt):
        self.actualizar_enemigos(dt)
        self.actualizar_minijefes(dt)
        self.actualizar_almas()
        self.actualizar_palas()
        self.actualizar_power_ups_dash()
        self.actualizar_power_ups_rango()
        self.actualizar_checkpoints()
        self._actualizar_duda_salto_de_fe(dt)
        if self.es_tutorial:
            self.actualizar_tutorial_contextual()

    def _actualizar_simulacion_jugando(self, dt):
        self._actualizar_latido_y_combos(dt)
        self.actualizar_plataformas(dt)
        self.actualizar_losas(dt)
        teclas = pygame.key.get_pressed()
        self.jugador.actualizar(dt, teclas, self.nivel.solidos_actuales())
        self.limitar_jugador()
        self.procesar_feedback_jugador()
        self.actualizar_ataque()
        self.actualizar_incensarios(dt)
        self._actualizar_particulas_bioma_juego(dt)
        if self.actualizar_jefe(dt):
            return
        if self.jugador.rect.top > self.nivel.alto + 120:
            self.perder_vida(
                ignorar_invulnerabilidad=True, causa="Caída al abismo de la cripta"
            )
            return
        if self.actualizar_peligros():
            return
        self._actualizar_objetos_y_progreso(dt)
        self.particulas.actualizar(dt)
        self.camara.actualizar(self.jugador, self.nivel, dt)
        if self.jugador.rect.colliderect(self.nivel.meta):
            self._resolver_meta_nivel()

    def actualizar(self, dt):
        """Actualiza la escena actual o delega la simulacion del nivel."""
        self._descontar_temporizadores_globales(dt)
        if self.estado in ("titulo", "menu", "seleccion_nivel", "creditos"):
            self.tiempo_titulo += dt
            self.tiempo_menu += dt
            return
        if self.mostrar_ayuda > 0:
            self.mostrar_ayuda = max(0.0, self.mostrar_ayuda - dt)
        if self.estado != "jugando":
            self.particulas.actualizar(dt)
            for particula in getattr(self, "particulas_bioma", []):
                particula.actualizar(dt)
            self.camara.actualizar_sacudida(dt)
            return
        self._actualizar_simulacion_jugando(dt)

    def dibujar(self):
        pantallas_menu = {
            "titulo": self.dibujar_titulo,
            "menu": self.dibujar_menu_principal,
            "seleccion_nivel": self.dibujar_seleccion_nivel,
            "configuracion": self.dibujar_configuracion,
            "creditos": self.dibujar_creditos,
            "test_selector": self.dibujar_selector_pruebas,
        }
        render_menu = pantallas_menu.get(self.estado)
        if render_menu is not None:
            render_menu()
            return

        self._dibujar_mundo_y_luz(self.superficie_mundo)
        pw, ph = self.pantalla.get_size()
        pygame.transform.scale(self.superficie_mundo, (pw, ph), self.pantalla)
        # Mantener canal alfa opaco antes de combinar filtros con SRCALPHA.
        self.pantalla.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MAX)

        self._aplicar_postprocesado_pantalla(pw, ph)
        self.dibujar_ui_espacial(self.pantalla, self.camara)
        self.hud.dibujar(self.pantalla, self, self.dt)
        self._dibujar_overlays_estado(pw, ph)

    def run(self):
        while self.corriendo:
            dt = min(self.reloj.tick(FPS) / 1000, MAX_DT)
            self.procesar_eventos()
            if self.hitstop > 0:
                self.hitstop = max(0.0, self.hitstop - dt)
                self.camara.actualizar_sacudida(dt)
                self.hud.actualizar(dt)
            else:
                self.actualizar(dt)
            self.dt = dt
            self.dibujar()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


#---- Arranque directo ----#
if __name__ == "__main__":
    Juego().run()
