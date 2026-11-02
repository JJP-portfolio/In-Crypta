# ============================================================
# juego.py — Bucle principal, estados y presentación
# ============================================================
# Estados: titulo / jugando / pausa / nivel_completado / derrota / victoria.
# La lógica de IN CRYPTA vive acá; las entidades y los niveles están
# separados para poder probarlos sin abrir una ventana.
# ============================================================

import asyncio
import math
from pathlib import Path
import random
import sys
import textwrap

import pygame

from audio import Audio
from camara import Camara
from config import (
    ALMAS_FILO_ANIMA,
    ALMAS_MANTO_FAROL,
    ALMAS_POR_VIDA,
    ALTO,
    ATAQUE_ALCANCE_MEJORADO,
    ATAQUE_COOLDOWN,
    AMARILLO,
    ANCHO,
    AZUL_OSCURO,
    BLANCO,
    CARMESÍ_SANGRE,
    CAMARA_ZOOM,
    CELESTE,
    CITAS_POE,
    CREMA,
    DASH_COOLDOWN,
    DASH_USOS_AIRE,
    DASH_DASHTURQUESA,
    DASH_VELOCIDAD,
    EQUIPO,
    ES_WEB,
    PERFIL_WEB_CALIDAD,
    PERFIL_WEB_SHADER,
    FAROL_CÁLIDO,
    FILO_ANIMA_ALCANCE,
    FILO_ANIMA_DASH_FACTOR,
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
    HUESO_MARFIL,
    HUD_GRIS_CLARO,
    INCENSARIO_COOLDOWN,
    INTEGRANTES,
    INVULNERABILIDAD,
    JEFE_ONDA_VELOCIDAD,
    LOSA_TIEMPO_QUIEBRE,
    ORO,
    ORO_LITÚRGICO,
    PIEDRA_FRIA,
    REBOTE_ENEMIGO,
    SALITRE_CRIPTA,
    TITULO,
    SUBTITULO,
    TILE,
    TURQUESA_ÁNIMA,
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

_CACHE_LUCES_JUEGO = {}

# --- Presets de Configuración de Teclado y Controles ---
PRESET_MODERNO = {
    "id": "moderno",
    "nombre": "Preset 1: WASD Moderno (WASD + Espacio + Shift + J/Click)",
    "etiqueta": "WASD Moderno",
    "desc": "Estilo PC plataformero: WASD/Flechas para mover, Espacio salto, Shift dash, J/Z/Click ataque",
    "teclas_izq": (pygame.K_a, pygame.K_LEFT),
    "teclas_der": (pygame.K_d, pygame.K_RIGHT),
    "teclas_salto": (pygame.K_SPACE, pygame.K_w, pygame.K_UP),
    "teclas_dash": (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_x),
    "teclas_ataque": (pygame.K_j, pygame.K_z, pygame.K_k),
    "mouse_ataque": True,
    "resumen": "Mov: WASD/←→ | Salto: ESPACIO/W | Dash: SHIFT/X | Ataque: J/Z/Click",
}

PRESET_RETRO = {
    "id": "retro",
    "nombre": "Preset 2: Retro Arcada (Flechas + Z/X/C)",
    "etiqueta": "Retro Arcada (Z-X-C)",
    "desc": "Estilo clásico de consola: Flechas para mover, Z = Salto, X = Dash, C = Ataque",
    "teclas_izq": (pygame.K_LEFT, pygame.K_a),
    "teclas_der": (pygame.K_RIGHT, pygame.K_d),
    "teclas_salto": (pygame.K_z, pygame.K_SPACE, pygame.K_UP),
    "teclas_dash": (pygame.K_x, pygame.K_LSHIFT, pygame.K_RSHIFT),
    "teclas_ataque": (pygame.K_c, pygame.K_j, pygame.K_z),
    "mouse_ataque": True,
    "resumen": "Mov: Flechas/AD | Salto: Z/ESPACIO | Dash: X/SHIFT | Ataque: C/J/Click",
}

PRESETS_TECLADO = (PRESET_MODERNO, PRESET_RETRO)

# Opciones configurables:
OPCIONES_CALIDAD = ("Alta", "Media", "Baja")
OPCIONES_HUD = ("Completo", "Compacto", "Inmersivo")
OPCIONES_SHADER = ("Gótico (Bloom + CRT)", "Suave (Solo Bloom)", "Puro (Pixel Art Clásico)")

# Constantes base de compatibilidad
TECLAS_SALTO = PRESET_MODERNO["teclas_salto"]
TECLAS_ATAQUE = PRESET_MODERNO["teclas_ataque"]

# Tolerancia vertical del pisotón: rect.bottom <= enemigo.rect.top + 18.
TOLERANCIA_PISOTON = 18
ALMAS_MINIJEFE = 5


def _obtener_luz_perforacion(radio):
    clave = ("sub", radio)
    surf = _CACHE_LUCES_JUEGO.get(clave)
    if surf is None:
        surf = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        for r in range(radio, 0, -1):
            norm = r / radio
            factor = max(0.0, (1.0 - norm * norm) ** 2.0)
            alfa = int(45 * factor)
            pygame.draw.circle(surf, (0, 0, 0, alfa), (radio, radio), r)
        _CACHE_LUCES_JUEGO[clave] = surf
    return surf


def _obtener_luz_calida(radio, color=(240, 196, 90), factor_mult=0.14):
    clave = ("add", radio, tuple(color), factor_mult)
    surf = _CACHE_LUCES_JUEGO.get(clave)
    if surf is None:
        surf = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        cr, cg, cb = color
        for r in range(radio, 0, -1):
            norm = r / radio
            factor = max(0.0, (1.0 - norm * norm) ** 2.0)
            pygame.draw.circle(
                surf,
                (
                    int(cr * factor * factor_mult),
                    int(cg * factor * factor_mult),
                    int(cb * factor * factor_mult),
                ),
                (radio, radio),
                r,
            )
        _CACHE_LUCES_JUEGO[clave] = surf
    return surf


_CACHE_HAZ_LUNAR = None


def _obtener_haz_lunar(h):
    """Caché de haz diagonal de luz lunar volumétrica y translúcida proyectada desde ventanales góticos."""
    global _CACHE_HAZ_LUNAR
    if _CACHE_HAZ_LUNAR is None or _CACHE_HAZ_LUNAR.get_height() != h:
        w_surf = 190
        surf = pygame.Surface((w_surf, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        base_color = (135, 185, 235)
        # Capas concéntricas con gradiente lateral suave para eliminar bordes poligonales rígidos
        num_capas = 16
        for i in range(num_capas, 0, -1):
            t = i / float(num_capas)
            top_w = 44 * t
            bot_w = 120 * t
            top_cx = 36
            bot_cx = 125

            # Alfa con caída cuadrática suave hacia los laterales
            alfa_capa = int(22 * (1.0 - t * t))
            if alfa_capa <= 0:
                continue
            pts = [
                (int(top_cx - top_w // 2), 0),
                (int(top_cx + top_w // 2), 0),
                (int(bot_cx + bot_w // 2), h),
                (int(bot_cx - bot_w // 2), h),
            ]
            pygame.draw.polygon(surf, (*base_color, alfa_capa), pts)

        # Atenuación vertical suave (brillante junto al ventanal, disipándose hacia el suelo)
        fade = pygame.Surface((w_surf, h), pygame.SRCALPHA)
        for y in range(0, h, 6):
            norm_y = y / float(h)
            fade_a = int(255 * (1.0 - norm_y * 0.78))
            pygame.draw.rect(fade, (255, 255, 255, fade_a), (0, y, w_surf, 6))
        surf.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        _CACHE_HAZ_LUNAR = surf.convert_alpha()
    return _CACHE_HAZ_LUNAR


class ParticulaBioma:
    """Partícula ambiental ligera reciclada en pantalla (máx 25, 60 FPS cero lag)."""

    def __init__(self, pantalla_w=VIRTUAL_ANCHO, pantalla_h=VIRTUAL_ALTO, tema="camposanto"):
        self.w = pantalla_w
        self.h = pantalla_h
        self.tema = tema
        self.reset(random_y=True)

    def reset(self, random_y=False):
        self.x = random.uniform(0, self.w)
        self.fase = random.uniform(0, math.tau)
        self.fase_vel = random.uniform(1.2, 2.5)

        if self.tema == "camposanto":
            # 60% fuegos fatuos ascendentes, 40% niebla rastrera a ras de suelo
            self.tipo = "fatuo" if random.random() < 0.6 else "niebla"
            if self.tipo == "fatuo":
                self.y = random.uniform(0, self.h) if random_y else self.h + random.uniform(2, 10)
                self.vx = random.uniform(-10, 10)
                self.vy = random.uniform(-18, -32)
                self.tamano = random.uniform(1.5, 3.0)
                self.color = random.choice(((70, 235, 220), (140, 240, 255), (90, 190, 220)))
                self.alfa = random.randint(80, 160)
            else:
                self.y = random.uniform(self.h - 50, self.h - 4) if random_y else self.h - random.uniform(4, 45)
                self.vx = random.uniform(15, 35)
                self.vy = random.uniform(-2, 2)
                self.tamano = random.uniform(8.0, 16.0)
                self.color = (35, 55, 75)
                self.alfa = random.randint(30, 65)

        elif self.tema == "cripta":
            # Motas de polvo gris/plata suspendidas en el aire con suave flotación
            self.tipo = "polvo"
            self.y = random.uniform(0, self.h) if random_y else (0 if random.random() < 0.5 else self.h)
            self.vx = random.uniform(-8, 8)
            self.vy = random.uniform(-6, 6)
            self.tamano = random.uniform(1.2, 2.4)
            self.color = random.choice(((210, 215, 225), (180, 185, 200), (235, 240, 250)))
            self.alfa = random.randint(70, 150)

        else:  # "osario"
            # Brasas carmesí y cenizas de hueso ascendiendo desde el abismo
            self.tipo = "brasa" if random.random() < 0.55 else "ceniza"
            self.y = random.uniform(0, self.h) if random_y else self.h + random.uniform(2, 15)
            self.vx = random.uniform(-15, 15)
            if self.tipo == "brasa":
                self.vy = random.uniform(-35, -65)
                self.tamano = random.uniform(1.8, 3.2)
                self.color = random.choice(((255, 80, 40), (255, 140, 50), (220, 50, 50), (255, 210, 80)))
                self.alfa = random.randint(110, 210)
            else:
                self.vy = random.uniform(-20, -45)
                self.tamano = random.uniform(1.4, 2.5)
                self.color = random.choice(((190, 175, 160), (140, 130, 125), (210, 200, 190)))
                self.alfa = random.randint(70, 140)

    def actualizar(self, dt, intensificar=False):
        self.fase += self.fase_vel * dt
        mult_vel = 1.6 if intensificar else 1.0

        if self.tipo == "niebla":
            self.x += self.vx * dt
            self.y += math.sin(self.fase) * 4.0 * dt
        elif self.tipo == "fatuo":
            self.x += (self.vx + math.sin(self.fase) * 12.0) * dt
            self.y += self.vy * dt
        elif self.tipo == "polvo":
            self.x += (self.vx + math.sin(self.fase) * 8.0) * dt
            self.y += (self.vy + math.cos(self.fase * 0.8) * 6.0) * dt
        else:  # brasa / ceniza
            self.x += (self.vx + math.sin(self.fase) * 14.0) * dt
            self.y += self.vy * mult_vel * dt

        # Wrap-around o reset al salir de pantalla
        if self.y < -15 or self.y > self.h + 15 or self.x < -25 or self.x > self.w + 25:
            self.reset(random_y=False)

    def dibujar(self, surface):
        px = int(self.x)
        py = int(self.y)
        if px < -20 or px > self.w + 20 or py < -20 or py > self.h + 20:
            return

        if self.tipo == "niebla":
            w_n = int(self.tamano * 2)
            h_n = int(self.tamano)
            s_niebla = pygame.Surface((w_n, h_n), pygame.SRCALPHA)
            pygame.draw.ellipse(s_niebla, (*self.color, self.alfa), (0, 0, w_n, h_n))
            surface.blit(s_niebla, (px - w_n // 2, py - h_n // 2))
        elif self.tipo == "fatuo":
            pygame.draw.circle(surface, self.color, (px, py), int(self.tamano))
            pygame.draw.circle(surface, (255, 255, 255), (px, py), max(1, int(self.tamano * 0.5)))
        elif self.tipo == "brasa":
            pygame.draw.circle(surface, self.color, (px, py), int(self.tamano))
            if self.tamano > 2.0:
                pygame.draw.circle(surface, (255, 240, 180), (px, py), 1)
        else:
            pygame.draw.circle(surface, self.color, (px, py), max(1, int(self.tamano)))


# --- Clase Juego --- #
class Juego:
    def __init__(self, sala_inicial=None):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO)
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        self.fuentes = {}
        p_font = Path("assets/NotoSerifDisplay-Bold.ttf")
        if not p_font.exists():
            p_font = Path("export/gdevelop_nativo/assets/NotoSerifDisplay-Bold.ttf")
        self._ruta_fuente_gotica = str(p_font) if p_font.exists() else None
        self.fondos = {}
        self.vineta = self.crear_vineta(90)
        self.vineta_carmesi = self.crear_vineta_carmesi()
        self.mascara_penumbra = pygame.Surface((VIRTUAL_ANCHO, VIRTUAL_ALTO), pygame.SRCALPHA)
        self.superficie_flash = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        self.hitstop = 0.0
        self.timer_corazon = 0.0

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
        self.test_opcion = 0
        self.menu_opcion = 0
        self.pausa_opcion = 0
        self.en_campaña = False
        self.nivel_seleccionado = 0
        self.tiempo_menu = 0.0
        self.superficie_mundo = pygame.Surface((VIRTUAL_ANCHO, VIRTUAL_ALTO))

        # Configuración del santuario: Presets de teclado, shaders, calidad y modo de HUD
        self.preset_teclado_idx = 0
        self.config_opcion = 0
        # En navegador (Pygbag/WASM) arranca con el perfil ligero; en PC, con el completo.
        self.config_shader_idx = PERFIL_WEB_SHADER if ES_WEB else 0   # 0: Gótico (Bloom + CRT), 1: Suave, 2: Puro
        self.config_calidad_idx = PERFIL_WEB_CALIDAD if ES_WEB else 0  # 0: Alta, 1: Media, 2: Baja
        self.particulas.factor_calidad = {0: 1.0, 1: 0.5, 2: 0.25}[self.config_calidad_idx]
        self.config_hud_idx = 0      # 0: Completo, 1: Compacto, 2: Inmersivo
        self.origen_configuracion = "menu"
        self._superficie_scanlines = self._crear_scanlines_goticas(ANCHO, ALTO)
        self.destello_manto = 0.0
        self._superficie_destello_manto = None
        self.teclas_salto = PRESETS_TECLADO[0]["teclas_salto"]
        self.teclas_dash = PRESETS_TECLADO[0]["teclas_dash"]
        self.teclas_ataque = PRESETS_TECLADO[0]["teclas_ataque"]
        self.particulas_bioma = []
        self.reiniciar_particulas_bioma("camposanto")

        if sala_inicial is not None:
            self.cargar_sala_prueba(sala_inicial)
        else:
            self.cargar_nivel(0, vidas=VIDAS_INICIALES)
            self.estado = "titulo"
            self.mostrar_ayuda = 0.0

    def reiniciar_particulas_bioma(self, tema="camposanto"):
        """Inicializa o recicla las partículas ambientales según la calidad gráfica (60 FPS sin lag)."""
        if getattr(self, "config_calidad_idx", 0) == 2:
            self.particulas_bioma = []
        elif getattr(self, "config_calidad_idx", 0) == 1:
            self.particulas_bioma = [ParticulaBioma(VIRTUAL_ANCHO, VIRTUAL_ALTO, tema) for _ in range(12)]
        else:
            self.particulas_bioma = [ParticulaBioma(VIRTUAL_ANCHO, VIRTUAL_ALTO, tema) for _ in range(25)]

    # --- Función cargar_nivel --- #
    def cargar_nivel(self, indice, vidas=None, sala=None):
        self.sala_prueba = sala is not None
        self.sala_prueba_indice = sala
        self.es_tutorial = False
        if sala is None:
            self.nivel_indice = indice
            datos = NIVELES[indice]
            # Progresión de habilidades fija por nivel (Matriz MDA):
            #   Nivel 1 (0): sin dash ni pala → recoge 'D' a mitad del nivel.
            #   Nivel 2 (1): inicia con dash → recoge el arma 'W'.
            #   Nivel 3 (2): inicia con dash y pala → 'X' tras el Mini-Boss.
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
        self.reiniciar_particulas_bioma(self.nivel.tema)
        vidas_iniciales = VIDAS_INICIALES if vidas is None else vidas
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
        # Iniciar dron fúnebre ambiental de la cripta
        self.audio.iniciar_dron()
        # Cita literaria de Edgar Allan Poe al comenzar cada nivel
        cita = CITAS_POE.get(self.nivel_indice, "")
        if cita:
            self.hud.mostrar_mensaje(cita, 2, 5.5)

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
                "FLECHAS / WASD: MOVERSE · ESPACIO / ARRIBA: SALTO VARIABLE (TAP CORTO / MANTENER) · "
                "RECOGÉ ALMAS (o) · FAROL DE REPOSO (F) CON 5 ALMAS: MANTO PROTECTOR · PORTÓN (G)"
            ),
            "camposanto",
        )
        self.reiniciar_particulas_bioma("camposanto")
        vidas_iniciales = VIDAS_INICIALES
        self.jugador = Jugador(*self.nivel.spawn, vidas=vidas_iniciales)
        self.jugador.tiene_pala = False
        self.jugador.tiene_dash = False
        self.aplicar_preset_teclado(getattr(self, "preset_teclado_idx", 0))
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
        self.almas_consagradas = 0
        self.almas_vida_consagradas = 0
        self.aviso_jefe = 0.0
        self.hud_aviso_altar = 0.0
        # Iniciar dron fúnebre ambiental
        self.audio.iniciar_dron()
        cita = CITAS_POE.get("tutorial", "")
        if cita:
            self.hud.mostrar_mensaje(cita, 1, 5.0)
        else:
            self.hud.mostrar_mensaje(
                "EL RITUAL DEL SEPULTURERO · Aprende las mecánicas básicas", 1, 5.0
            )

    # --- Función abrir_menu --- #
    def abrir_menu(self):
        self.estado = "menu"
        self.menu_opcion = 0
        self.audio.detener_dron()
        self.audio.reproducir("ui")

    # --- Función abrir_seleccion_nivel --- #
    def abrir_seleccion_nivel(self):
        self.estado = "seleccion_nivel"
        self.nivel_seleccionado = self.nivel_indice
        self.audio.detener_dron()
        self.audio.reproducir("ui")

    # --- Función abrir_creditos --- #
    def abrir_creditos(self):
        self.estado = "creditos"
        self.audio.detener_dron()
        self.audio.reproducir("ui")

    # --- Métodos del Módulo de Configuración del Santuario --- #
    def abrir_configuracion(self, origen="menu"):
        self.estado = "configuracion"
        self.origen_configuracion = origen
        self.config_opcion = 0
        self.audio.detener_dron()
        self.audio.reproducir("ui")

    def aplicar_preset_teclado(self, idx):
        """Aplica el preset de controles especificado actualizando las tuplas de teclas del juego y jugador."""
        self.preset_teclado_idx = idx % len(PRESETS_TECLADO)
        preset = PRESETS_TECLADO[self.preset_teclado_idx]
        self.teclas_salto = preset["teclas_salto"]
        self.teclas_dash = preset["teclas_dash"]
        self.teclas_ataque = preset["teclas_ataque"]
        if getattr(self, "jugador", None):
            self.jugador.teclas_izq = preset["teclas_izq"]
            self.jugador.teclas_der = preset["teclas_der"]

    def alternar_preset_teclado(self, delta=1):
        """Alterna entre Preset 1 (WASD Moderno) y Preset 2 (Retro Arcada Z-X-C)."""
        self.aplicar_preset_teclado(self.preset_teclado_idx + delta)
        self.audio.reproducir("ui")
        nombre_preset = PRESETS_TECLADO[self.preset_teclado_idx]["etiqueta"]
        self.hud.mostrar_mensaje(f"CONTROL: {nombre_preset.upper()}", 1, 3.0)

    def _crear_scanlines_goticas(self, ancho, alto):
        surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        # Micro-scanlines cinematográficas cada 3px con alpha sutil (16/255)
        for y in range(0, alto, 3):
            pygame.draw.line(surf, (4, 3, 8, 16), (0, y), (ancho, y), 1)
        return surf

    def _aplicar_bloom(self, origen, destino, intensidad=0.12):
        pw, ph = destino.get_size()
        sw, sh = max(1, pw // 4), max(1, ph // 4)
        mini = pygame.transform.smoothscale(origen, (sw, sh))
        bloom = pygame.transform.smoothscale(mini, (pw, ph))
        bloom.set_alpha(int(255 * intensidad))
        destino.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def alternar_shader(self, delta=1):
        self.config_shader_idx = (self.config_shader_idx + delta) % len(OPCIONES_SHADER)
        self.audio.reproducir("ui")
        shader = OPCIONES_SHADER[self.config_shader_idx]
        self.hud.mostrar_mensaje(f"EFECTOS / SHADER: {shader.upper()}", 1, 3.0)

    # --- Calidad Gráfica con Impacto Real --- #
    # Opciones: Alta (0: 100% partículas + halos + penumbra), Media (1: 50% partículas + penumbra), Baja (2: 60 FPS sin penumbra)
    def alternar_calidad_grafica(self, delta=1):
        self.config_calidad_idx = (self.config_calidad_idx + delta) % len(OPCIONES_CALIDAD)
        self.audio.reproducir("ui")
        factores = {0: 1.0, 1: 0.5, 2: 0.25}
        self.particulas.factor_calidad = factores.get(self.config_calidad_idx, 1.0)
        tema = self.nivel.tema if self.nivel and hasattr(self.nivel, "tema") else "camposanto"
        self.reiniciar_particulas_bioma(tema)
        calidad = OPCIONES_CALIDAD[self.config_calidad_idx]
        self.hud.mostrar_mensaje(f"CALIDAD GRÁFICA: {calidad.upper()}", 1, 3.0)

    # --- Modo de HUD / Interfaz con Impacto Real --- #
    # Opciones: Completo (0: riel superior 100%), Compacto (1: riel con opacidad alpha 140), Inmersivo (2: UI diegética pura, riel ante jefes o eventos)
    def alternar_modo_hud(self, delta=1):
        self.config_hud_idx = (self.config_hud_idx + delta) % len(OPCIONES_HUD)
        self.audio.reproducir("ui")
        self.hud.modo_hud = self.config_hud_idx
        modo = OPCIONES_HUD[self.config_hud_idx]
        self.hud.mostrar_mensaje(f"MODO DE HUD: {modo.upper()}", 1, 3.0)

    def alternar_accesibilidad(self):
        """Alterna el modo de reducción de movimiento (Principio 3 UX - Comodidad)."""
        self.reducir_movimiento = not self.reducir_movimiento
        self.camara.permitir_sacudida = not self.reducir_movimiento
        self.hud.reducir_movimiento = self.reducir_movimiento
        estado_str = "ACTIVADA" if self.reducir_movimiento else "DESACTIVADA"
        self.hud.mostrar_mensaje(f"ACCESIBILIDAD: REDUCIR MOVIMIENTO {estado_str}", 3, 2.5)
        self.audio.reproducir("ui")

    # --- Función ejecutar_seleccion_nivel --- #
    def ejecutar_seleccion_nivel(self, indice):
        if indice == 0:
            self.iniciar_tutorial()
        elif indice == 1:
            self.seleccionar_nivel(0)
        elif indice == 2:
            self.seleccionar_nivel(1)
        elif indice == 3:
            self.seleccionar_nivel(2)
        elif indice == 4:
            self.abrir_selector_pruebas()

    # --- Función seleccionar_nivel --- #
    def seleccionar_nivel(self, indice):
        if indice in (-1, "preludio", "tutorial"):
            self.iniciar_tutorial()
            return
        if indice in (4, "salas", "pruebas"):
            self.abrir_selector_pruebas()
            return
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
        self.audio.detener_dron()
        self.audio.reproducir("ui")

    # --- Función iniciar_campaña --- #
    def iniciar_campaña(self):
        """Inicia la campaña narrativa completa comenzando en el Preludio."""
        self.almas_totales = 0
        self.tiempo_total = 0.0
        self.jugador = None
        self.en_campaña = True
        self.iniciar_tutorial()

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
                    total_menu = 4
                    if evento.key in (pygame.K_UP, pygame.K_w):
                        self.menu_opcion = (self.menu_opcion - 1) % total_menu
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_opcion = (self.menu_opcion + 1) % total_menu
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.reproducir("ui")
                        if self.menu_opcion == 0:
                            self.iniciar_campaña()
                        elif self.menu_opcion == 1:
                            self.abrir_seleccion_nivel()
                        elif self.menu_opcion == 2:
                            self.abrir_configuracion("menu")
                        else:
                            self.abrir_creditos()
                    elif evento.key == pygame.K_ESCAPE:
                        self.estado = "titulo"
                        self.audio.reproducir("ui")
                    continue

                elif self.estado == "configuracion":
                    total_config = 7
                    if evento.key in (pygame.K_UP, pygame.K_w):
                        self.config_opcion = (self.config_opcion - 1) % total_config
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_DOWN, pygame.K_s):
                        self.config_opcion = (self.config_opcion + 1) % total_config
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_LEFT, pygame.K_a):
                        if self.config_opcion == 0:
                            self.alternar_preset_teclado(-1)
                        elif self.config_opcion == 1:
                            self.alternar_shader(-1)
                        elif self.config_opcion == 2:
                            self.alternar_calidad_grafica(-1)
                        elif self.config_opcion == 3:
                            self.alternar_modo_hud(-1)
                        elif self.config_opcion == 4:
                            self.alternar_accesibilidad()
                        elif self.config_opcion == 5:
                            self.audio.alternar()
                    elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                        if self.config_opcion == 0:
                            self.alternar_preset_teclado(1)
                        elif self.config_opcion == 1:
                            self.alternar_shader(1)
                        elif self.config_opcion == 2:
                            self.alternar_calidad_grafica(1)
                        elif self.config_opcion == 3:
                            self.alternar_modo_hud(1)
                        elif self.config_opcion == 4:
                            self.alternar_accesibilidad()
                        elif self.config_opcion == 5:
                            self.audio.alternar()
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.config_opcion == 0:
                            self.alternar_preset_teclado(1)
                        elif self.config_opcion == 1:
                            self.alternar_shader(1)
                        elif self.config_opcion == 2:
                            self.alternar_calidad_grafica(1)
                        elif self.config_opcion == 3:
                            self.alternar_modo_hud(1)
                        elif self.config_opcion == 4:
                            self.alternar_accesibilidad()
                        elif self.config_opcion == 5:
                            self.audio.alternar()
                        elif self.config_opcion == 6:
                            if self.origen_configuracion == "pausa":
                                self.estado = "pausa"
                            else:
                                self.abrir_menu()
                            self.audio.reproducir("ui")
                    elif evento.key == pygame.K_ESCAPE:
                        if self.origen_configuracion == "pausa":
                            self.estado = "pausa"
                        else:
                            self.abrir_menu()
                        self.audio.reproducir("ui")
                    continue

                elif self.estado == "pausa":
                    if evento.key in (pygame.K_UP, pygame.K_w):
                        self.pausa_opcion = (self.pausa_opcion - 1) % 4
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_DOWN, pygame.K_s):
                        self.pausa_opcion = (self.pausa_opcion + 1) % 4
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_c, pygame.K_o):
                        self.abrir_configuracion("pausa")
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.reproducir("ui")
                        if self.pausa_opcion == 0:
                            self.estado = "jugando"
                        elif self.pausa_opcion == 1:
                            if self.punto_reintento:
                                self.reintentar_nivel()
                            else:
                                if self.sala_prueba:
                                    self.cargar_sala_prueba(self.sala_prueba_indice)
                                elif self.es_tutorial:
                                    self.iniciar_tutorial()
                                else:
                                    self.cargar_nivel(self.nivel_indice, vidas=VIDAS_INICIALES)
                            self.estado = "jugando"
                        elif self.pausa_opcion == 2:
                            if self.sala_prueba:
                                self.cargar_sala_prueba(self.sala_prueba_indice)
                            elif self.es_tutorial:
                                self.iniciar_tutorial()
                            else:
                                self.cargar_nivel(self.nivel_indice, vidas=VIDAS_INICIALES)
                            self.estado = "jugando"
                        elif self.pausa_opcion == 3:
                            self.abrir_menu()
                    elif evento.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.audio.reproducir("ui")
                        self.estado = "jugando"
                    continue

                elif self.estado == "seleccion_nivel":
                    total_sn = 5
                    if evento.key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
                        self.nivel_seleccionado = (self.nivel_seleccionado - 1) % total_sn
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d):
                        self.nivel_seleccionado = (self.nivel_seleccionado + 1) % total_sn
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.reproducir("ui")
                        self.ejecutar_seleccion_nivel(self.nivel_seleccionado)
                    elif evento.key == pygame.K_ESCAPE:
                        self.abrir_menu()
                    continue

                elif self.estado == "creditos":
                    if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        self.abrir_menu()
                    continue

                elif self.estado == "test_selector":
                    if evento.key == pygame.K_ESCAPE:
                        self.abrir_seleccion_nivel()
                    elif evento.key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
                        self.test_opcion = (self.test_opcion - 1) % len(SALAS_PRUEBA)
                        self.audio.reproducir("ui")
                    elif evento.key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d):
                        self.test_opcion = (self.test_opcion + 1) % len(SALAS_PRUEBA)
                        self.audio.reproducir("ui")
                    elif pygame.K_1 <= evento.key <= pygame.K_6:
                        idx = evento.key - pygame.K_1
                        if idx < len(SALAS_PRUEBA):
                            self.cargar_sala_prueba(idx)
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.cargar_sala_prueba(self.test_opcion)
                    continue

                if evento.key == pygame.K_ESCAPE:
                    if self.estado == "jugando":
                        self.audio.reproducir("ui")
                        self.pausa_opcion = 0
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
                        self.pausa_opcion = 0
                        self.estado = "pausa"
                    elif self.estado == "pausa":
                        self.audio.reproducir("ui")
                        self.estado = "jugando"

                elif evento.key in getattr(self, "teclas_salto", TECLAS_SALTO) and self.estado == "jugando":
                    self.jugador.pedir_salto()

                elif evento.key in getattr(self, "teclas_dash", (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_x)) and self.estado == "jugando":
                    self.jugador.pedir_dash()

                elif evento.key in getattr(self, "teclas_ataque", TECLAS_ATAQUE) and self.estado == "jugando":
                    self.intentar_ataque()

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
                        self.reintentar_nivel()
                        self.estado = "jugando"
                    elif self.estado == "victoria":
                        self.abrir_menu()

            elif evento.type == pygame.KEYUP:
                if evento.key in getattr(self, "teclas_salto", TECLAS_SALTO) and self.jugador is not None:
                    self.jugador.soltar_salto()

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1 and self.estado == "jugando":
                    self.intentar_ataque()

    # --- Función intentar_ataque --- #
    def intentar_ataque(self):
        """Ataque frontal con pala (J / Z / C / click). Requiere tiene_pala."""
        if not self.jugador.pedir_ataque():
            return False
        self.audio.reproducir("ataque")
        self.particulas.ataque(
            self.jugador.rect.centerx,
            self.jugador.rect.centery,
            self.jugador.direccion,
            mejorado=self.jugador.rango_ataque_mejorado,
        )
        return True

    # --- Función actualizar --- #
    def actualizar(self, dt):
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt)
        if getattr(self, "destello_manto", 0.0) > 0:
            self.destello_manto = max(0.0, self.destello_manto - dt)
        if self.aviso_jefe > 0:
            self.aviso_jefe = max(0.0, self.aviso_jefe - dt)
        if self.hud_aviso_altar > 0:
            self.hud_aviso_altar = max(0.0, self.hud_aviso_altar - dt)

        if self.estado in ("titulo", "menu", "seleccion_nivel", "creditos"):
            self.tiempo_titulo += dt
            self.tiempo_menu += dt
            return

        if self.mostrar_ayuda > 0:
            self.mostrar_ayuda = max(0.0, self.mostrar_ayuda - dt)

        if self.estado != "jugando":
            self.particulas.actualizar(dt)
            for p in getattr(self, "particulas_bioma", []):
                p.actualizar(dt)
            self.camara.actualizar_sacudida(dt)
            return

        # Sfx del corazón delator a 1 HP
        if self.jugador and self.jugador.vidas == 1:
            self.timer_corazon += dt
            if self.timer_corazon >= (1.0 / 1.2):
                self.timer_corazon = 0.0
                self.audio.reproducir("corazon")
        else:
            self.timer_corazon = 0.0

        self.tiempo_nivel += dt
        self.tiempo_total += dt

        if self.almas_combo_timer > 0:
            self.almas_combo_timer = max(0.0, self.almas_combo_timer - dt)
            if self.almas_combo_timer <= 0:
                self.almas_combo_count = 0

        self.actualizar_plataformas(dt)
        self.actualizar_losas(dt)
        teclas = pygame.key.get_pressed()
        self.jugador.actualizar(dt, teclas, self.nivel.solidos_actuales())
        self.limitar_jugador()
        self.procesar_feedback_jugador()
        self.actualizar_ataque()
        self.actualizar_incensarios(dt)

        # Partículas ambientales de bioma (fuegos fatuos, polvo de cripta, cenizas/brasas de osario)
        intensificar_bioma = False
        if getattr(self.nivel, "tema", "") == "osario" and self.jugador:
            if self.jefe is not None and (getattr(self.jefe, "salud", 0) < getattr(self.jefe, "salud_maxima", 5) or self.jugador.rect.x >= 268 * TILE):
                intensificar_bioma = True
        for p in getattr(self, "particulas_bioma", []):
            p.actualizar(dt, intensificar=intensificar_bioma)

        if self.actualizar_jefe(dt):
            return

        if self.jugador.rect.top > self.nivel.alto + 120:
            self.perder_vida(ignorar_invulnerabilidad=True, causa="Caída al abismo de la cripta")
            return

        if self.actualizar_peligros():
            return

        self.actualizar_enemigos(dt)
        self.actualizar_minijefes(dt)
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
                if getattr(self, "en_campaña", False):
                    self.almas_totales += self.jugador.almas
                    self.cargar_nivel(0, vidas=self.jugador.vidas)
                    self.hud.mostrar_mensaje("¡UMBRAL SUPERADO! · Adentrándose en El Camposanto", 2, 4.0)
                else:
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

    # --- Función actualizar_losas --- #
    def actualizar_losas(self, dt):
        for losa in getattr(self.nivel, "losas_quebradizas", []):
            if (
                self.jugador.en_suelo
                and abs(self.jugador.rect.bottom - losa.rect.top) <= 2
                and self.jugador.rect.right > losa.rect.left
                and self.jugador.rect.left < losa.rect.right
            ):
                losa.pisar()

            # Mientras tiembla (0.40s): caen piedritas y polvo hacia abajo
            if getattr(losa, "activa", False) and getattr(losa, "pisada", False) and getattr(losa, "tiempo_quiebre", 0.0) > 0:
                if random.random() < 0.45:
                    self.particulas.emitir(
                        losa.rect.left + random.uniform(2, losa.rect.width - 2),
                        losa.rect.bottom - 2,
                        1,
                        (SALITRE_CRIPTA, PIEDRA_FRIA, HUESO),
                        50,
                        0.35,
                        2.0,
                        480,
                    )

            if losa.recien_quebrada:
                self.audio.reproducir("losa_romper")
                self.particulas.losa_romper(losa.rect.centerx, losa.rect.centery, w=losa.rect.width)
                self.camara.sacudir(3.5, 0.12)
            elif losa.recien_reconstruida:
                self.particulas.emitir(
                    losa.rect.centerx,
                    losa.rect.centery,
                    12,
                    (TURQUESA_ÁNIMA, BLANCO),
                    100,
                    0.35,
                    2,
                )

    # --- Función actualizar_incensarios --- #
    def actualizar_incensarios(self, dt):
        for incensario in getattr(self.nivel, "incensarios", []):
            if not incensario.puede_rebotar():
                continue

            # Pisotón / contacto cayendo desde arriba (funciona sin pala incluso en Nivel 1)
            if (
                self.jugador.vy > 0
                and self.jugador.rect.colliderect(incensario.rect)
                and self.jugador.rect.bottom <= incensario.rect.top + TOLERANCIA_PISOTON
            ):
                incensario.activar_rebote()
                self.jugador.rect.bottom = min(self.jugador.rect.bottom, incensario.rect.top)
                self.jugador.y = float(self.jugador.rect.y)
                self.jugador.vy = -REBOTE_ENEMIGO
                self.jugador.en_suelo = False
                self.jugador.dash_usos_aire = DASH_USOS_AIRE
                self.jugador.dash_cooldown = 0.0
                self.audio.reproducir("campana_repique")
                self.particulas.campana_repique(incensario.rect.centerx, incensario.rect.centery)
                self.camara.sacudir(5.0, 0.12, dir_x=0.0, dir_y=1.0)
                self.hitstop = 0.08

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

        if getattr(self.jugador, "aterrizaje_recien", False):
            # 4 partículas de polvo suave al aterrizar en pies
            pies_x = self.jugador.rect.centerx
            pies_y = self.jugador.rect.bottom
            self.particulas.emitir(
                pies_x,
                pies_y,
                4,
                (SALITRE_CRIPTA, PIEDRA_FRIA, HUESO, BLANCO),
                48,
                0.24,
                2.5,
                320,
            )

        if self.jugador.dash_recien:
            self.audio.reproducir("dash")
            self.camara.sacudir(3.5, 0.10, dir_x=self.jugador.direccion, dir_y=0.0)

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

        # Filo de Ánima: estela de chispas litúrgicas doradas y turquesas
        if getattr(self.jugador, "filo_anima", False):
            self.particulas.emitir(
                golpe.centerx,
                golpe.centery,
                2,
                (ORO, TURQUESA_ÁNIMA, BLANCO),
                120,
                0.25,
                3,
            )

        # Campanas de Resonancia / Incensarios (rebotan y recargan dash al golpearlas)
        for incensario in getattr(self.nivel, "incensarios", []):
            if incensario.puede_rebotar() and golpe.colliderect(incensario.rect):
                incensario.activar_rebote()
                self.jugador.ataque_golpeado = True
                self.jugador.vy = -REBOTE_ENEMIGO
                self.jugador.en_suelo = False
                self.jugador.dash_usos_aire = DASH_USOS_AIRE
                self.jugador.dash_cooldown = 0.0
                self.audio.reproducir("campana_repique")
                self.particulas.campana_repique(incensario.rect.centerx, incensario.rect.centery)
                self.camara.sacudir(6.0, 0.14, dir_x=self.jugador.direccion, dir_y=-0.5)
                self.hitstop = 0.08
                self.flash = 0.08
                self.flash_color = TURQUESA_ÁNIMA
                return

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
            self.camara.sacudir(5.0, 0.12, dir_x=self.jugador.direccion, dir_y=0.0)
            self.hitstop = 0.08
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
                self.camara.sacudir(5.0, 0.12, dir_x=self.jugador.direccion, dir_y=0.0)
                self.hitstop = 0.08
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
                self.camara.sacudir(5.0, 0.12, dir_x=self.jugador.direccion, dir_y=0.0)
                self.hitstop = 0.08
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
                self.camara.sacudir(5.0, 0.12, dir_x=self.jugador.direccion, dir_y=0.0)
                self.hitstop = 0.08
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
                self.camara.sacudir(5.0, 0.12, dir_x=self.jugador.direccion, dir_y=0.0)
                self.hitstop = 0.08
                self.flash = 0.06
                self.flash_color = AMARILLO
                break

        # Mini-Jefes (El Carcelero del Osario)
        if not self.jugador.ataque_golpeado:
            for mj in getattr(self.nivel, "minijefes", []):
                if not mj.vivo or not golpe.colliderect(mj.rect):
                    continue
                self.jugador.ataque_golpeado = True
                if mj.recibir_golpe_pala():
                    self.jugador.dash_usos_aire = DASH_USOS_AIRE
                    self.jugador.dash_cooldown = 0.0
                    self.audio.reproducir("pala")
                    self.particulas.pala(mj.rect.centerx, mj.rect.centery)
                    self.camara.sacudir(6.0, 0.14, dir_x=self.jugador.direccion, dir_y=0.0)
                    self.hitstop = 0.08
                    self.flash = 0.06
                    self.flash_color = AMARILLO
                    self._comprobar_muerte_minijefe(mj)
                else:
                    self._rebote_minijefe_guardia(mj)
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

    def _rebotar_jefe_coraza(self):
        self.jugador.vx = -self.jugador.direccion * 240
        self.jugador.vy = -180
        self.jugador.retroceso_tiempo = 0.20
        self.jugador.invulnerable = 0.25
        self.camara.sacudir(5.0, 0.12, dir_x=-self.jugador.direccion, dir_y=0.0)
        self.flash = 0.08
        self.flash_color = (200, 50, 50)
        self.audio.reproducir("rebote_pala")
        self.particulas.chispas_rebote(
            self.jefe.rect.centerx - self.jugador.direccion * 16,
            self.jefe.rect.centery,
            -self.jugador.direccion,
        )

    # --- Función dañar_jefe_pala --- #
    def dañar_jefe_pala(self):
        """Golpe de pala: daña en Fase 1; rebota en Fase 2 sin Guadaña Consagrada (X)."""
        if self.jefe is None or not self.jefe.vivo:
            return False
        rango_mejorado = getattr(self.jugador, "rango_ataque_mejorado", False)
        if self.jefe.fase >= 2 and not rango_mejorado:
            self._rebotar_jefe_coraza()
            self.hud.mostrar_mensaje("¡CORAZA ESPECTRAL! Necesitás la Guadaña Consagrada (X)", 2, 2.5)
            return False
        if not self.jefe.recibir_golpe_pala(rango_mejorado=rango_mejorado):
            self._rebotar_jefe_coraza()
            return False
        res = self._aplicar_golpe_jefe()
        # Ráfaga de rechazo al dañar con pala frontal
        dir_empuje = 1 if self.jugador.rect.centerx >= self.jefe.rect.centerx else -1
        self.jugador.vx = dir_empuje * 220.0
        self.jugador.retroceso_tiempo = 0.16
        return res

    # --- Función dañar_jefe_pisaton --- #
    def dañar_jefe_pisaton(self):
        """Pisotón: daña en Fase 1; en Fase 2 exige la Guadaña Consagrada (X)."""
        if self.jefe is None or not self.jefe.vivo:
            return False

        # Dirección de expulsión: hacia el lateral relativo al centro del jefe
        dir_empuje = 1 if self.jugador.rect.centerx >= self.jefe.rect.centerx else -1
        rango_mejorado = getattr(self.jugador, "rango_ataque_mejorado", False)

        if self.jefe.fase >= 2 and not rango_mejorado:
            # Coraza en Fase 2 sin guadaña: rebote oblicuo defensivo que expulsa al jugador
            self.jugador.vx = dir_empuje * 280.0
            self.jugador.vy = -220.0
            self.jugador.retroceso_tiempo = 0.22
            self.jugador.dash_usos_aire = DASH_USOS_AIRE
            self.jugador.dash_cooldown = 0.0
            self.audio.reproducir("rebote_pala")
            self.particulas.chispas_rebote(self.jefe.rect.centerx, self.jefe.rect.top, dir_empuje)
            self.camara.sacudir(5.0, 0.12, dir_x=dir_empuje, dir_y=0.0)
            self.hud.mostrar_mensaje("¡CORAZA ESPECTRAL! Necesitás la Guadaña Consagrada (X)", 2, 2.5)
            return False

        if not self.jefe.recibir_pisaton(rango_mejorado=rango_mejorado):
            # Fuera de la ventana de vulnerabilidad: yelmo blindado desvía oblicuamente al jugador
            self.jugador.vx = dir_empuje * 280.0
            self.jugador.vy = -220.0
            self.jugador.retroceso_tiempo = 0.22
            self.audio.reproducir("rebote_pala")
            self.particulas.chispas_rebote(self.jefe.rect.centerx, self.jefe.rect.top, dir_empuje)
            self.camara.sacudir(4.0, 0.10, dir_x=dir_empuje, dir_y=0.0)
            return False

        # Impacto exitoso en ventana vulnerable: daño y ráfaga de expulsión cinética
        res = self._aplicar_golpe_jefe()
        self.audio.reproducir("stomp")
        self.particulas.stomp(self.jefe.rect.centerx, self.jefe.rect.top)
        # Ráfaga defensiva de energía del Custodio que repele fuertemente al sepulturero
        self.particulas.emitir(
            self.jefe.rect.centerx,
            self.jefe.rect.top,
            16,
            (CARMESÍ_SANGRE, ORO_LITÚRGICO, BLANCO),
            200,
            0.4,
            3.5,
            350,
        )
        self.jugador.vx = dir_empuje * 340.0
        self.jugador.vy = -260.0
        self.jugador.retroceso_tiempo = 0.25
        self.camara.sacudir(9.0, 0.20, dir_x=dir_empuje, dir_y=0.5)
        return res

    # --- Función _aplicar_golpe_jefe (efectos comunes) --- #
    def _aplicar_golpe_jefe(self):
        self.jugador.dash_usos_aire = DASH_USOS_AIRE
        self.jugador.dash_cooldown = 0.0
        self.audio.reproducir("pala")
        self.particulas.pala(self.jefe.rect.centerx, self.jefe.rect.centery)
        self.camara.sacudir(8.0, 0.18, dir_x=self.jugador.direccion, dir_y=0.0)
        self.hitstop = 0.08
        self.flash = 0.10
        self.flash_color = AMARILLO

        if not self.jefe.vivo:
            self.audio.detener_dron()
            self.audio.reproducir("meta")
            self.particulas.meta(self.jefe.rect.centerx, self.jefe.rect.centery)
            self.ondas_jefe = []
            self.aviso_jefe = 3.2
            self.flash = 0.22
            self.hud.mostrar_mensaje("¡EL CUSTODIO CAYÓ! · La cripta se abre…", 5, 4.0)
        elif self.jefe.estado == "cambio":
            self.audio.reproducir("jefe_fase")
            self.camara.sacudir(11.0, 0.26, dir_x=0.0, dir_y=1.0)
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
            if getattr(self.jugador, "rango_ataque_mejorado", False):
                self.hud.mostrar_mensaje("¡FASE II! · Coraza espectral · La Guadaña Consagrada (X) la quiebra", 4, 4.5)
            else:
                self.hud.mostrar_mensaje("¡FASE II! · Coraza espectral · Necesitás la Guadaña Consagrada (X)", 4, 4.5)

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
        # Regla de diseño: el pisotón (stomp) solo mata si el jugador tiene la pala.
        # Cada pisotón rebota y recarga el dash aéreo → "trampolines dinámicos"
        # para encadenar Salto -> Dash -> Pisotón -> Rebote -> Nuevo Dash.
        for enemigo in self.nivel.enemigos:
            enemigo.actualizar(dt)
            if self._resolver_contacto(enemigo, "Contacto con un Morador de la cripta"):
                return

        for enemigo_melee in self.nivel.enemigos_melee:
            enemigo_melee.actualizar(dt, self.jugador)
            if self._resolver_contacto(enemigo_melee, "Embestida del Guardia de la cripta"):
                return

        for totem in self.nivel.totems:
            totem.actualizar(dt, self.jugador)

        # Cuervos: vuelo circular. Pisables con pala (trampolín aéreo).
        for cuervo in self.nivel.cuervos:
            cuervo.actualizar(dt)
            if self._resolver_contacto(cuervo, "Ataque aéreo de Cuervo espectral"):
                return

        # Polillas: vuelo zigzag. Pisables con pala (trampolín aéreo).
        for polilla in self.nivel.polillas:
            polilla.actualizar(dt)
            if self._resolver_contacto(polilla, "Polvo letal de Polilla sombría"):
                return

        # Arañas: patrullaje horizontal. Pisables con pala.
        for araña in self.nivel.aranias:
            araña.actualizar(dt)
            if self._resolver_contacto(araña, "Picadura de Araña espectral"):
                return

    # --- Función _viene_desde_arriba --- #
    def _viene_desde_arriba(self, rect):
        """Pisotón válido: cayendo y con los pies a ≤ 18 px de la cabeza del enemigo."""
        return (
            self.jugador.vy > 0
            and self.jugador.rect.bottom <= rect.top + TOLERANCIA_PISOTON
        )

    # --- Función _rebote_pisoton --- #
    def _rebote_pisoton(self, rect, fuerza_sacudida=6.0):
        """Rebote + recarga instantánea del dash aéreo tras un pisotón exitoso."""
        self.jugador.rect.bottom = min(self.jugador.rect.bottom, rect.top)
        self.jugador.y = float(self.jugador.rect.y)
        self.jugador.vy = -REBOTE_ENEMIGO
        self.jugador.en_suelo = False
        self.jugador.dash_usos_aire = DASH_USOS_AIRE
        self.jugador.dash_cooldown = 0.0
        self.audio.reproducir("stomp")
        self.particulas.stomp(rect.centerx, rect.top)
        self.camara.sacudir(fuerza_sacudida, 0.14, dir_x=0.0, dir_y=1.0)
        self.hitstop = 0.08

    # --- Función _resolver_contacto --- #
    def _resolver_contacto(self, enemigo, causa):
        """Resuelve el contacto jugador-enemigo. Devuelve True si el jugador perdió una vida."""
        if not enemigo.vivo or not self.jugador.rect.colliderect(enemigo.rect):
            return False
        if self.jugador.tiene_pala and self._viene_desde_arriba(enemigo.rect):
            enemigo.vivo = False
            self._rebote_pisoton(enemigo.rect)
            return False
        if self.jugador.invulnerable > 0:
            return False
        self.perder_vida(causa=causa)
        return True

    # --- Función actualizar_minijefes --- #
    def actualizar_minijefes(self, dt):
        for mj in getattr(self.nivel, "minijefes", []):
            mj.actualizar(dt, self.jugador)
            if not mj.vivo:
                continue

            if mj.aviso_recien:
                # Telegrafía: brillo carmesí (dibujar) + sonido de aviso.
                self.audio.reproducir("jefe_aviso")

            if not self.jugador.rect.colliderect(mj.rect):
                continue

            # Pisotón sobre el Mini-Jefe (Carcelero del Osario)
            if self.jugador.tiene_pala and self._viene_desde_arriba(mj.rect):
                if mj.recibir_pisaton():
                    self._rebote_pisoton(mj.rect, fuerza_sacudida=7.0)
                    self._comprobar_muerte_minijefe(mj)
                else:
                    # Fuera de su ventana de cansancio: rebota sin dañarlo.
                    self.jugador.rect.bottom = mj.rect.top
                    self.jugador.y = float(self.jugador.rect.y)
                    self.jugador.vy = -REBOTE_ENEMIGO * 0.75
                    self.jugador.en_suelo = False
                    self._rebote_minijefe_guardia(mj)
            elif self.jugador.invulnerable <= 0:
                self.perder_vida(causa="Ataque del Carcelero del Osario")
                return

    # --- Función _rebote_minijefe_guardia --- #
    def _rebote_minijefe_guardia(self, mj):
        """Feedback discernible: golpe fuera de la ventana vulnerable del Carcelero."""
        self.audio.reproducir("rebote_pala")
        self.particulas.chispas_rebote(mj.rect.centerx, mj.rect.centery, -self.jugador.direccion)
        self.camara.sacudir(3.0, 0.08)

    # --- Función _comprobar_muerte_minijefe --- #
    def _comprobar_muerte_minijefe(self, mj):
        if mj.vivo or mj.almas_otorgadas:
            return
        mj.almas_otorgadas = True
        self.jugador.almas += ALMAS_MINIJEFE
        self._sumar_almas_para_vida(ALMAS_MINIJEFE)
        self.audio.reproducir("meta")
        self.particulas.meta(mj.rect.centerx, mj.rect.centery)
        self.camara.sacudir(9.0, 0.22)
        self.hud.mostrar_mensaje(
            f"¡EL CARCELERO HA CAÍDO! · El altar de la Guadaña se abre (+{ALMAS_MINIJEFE} Almas)", 2, 4.0
        )

    # --- Función _sumar_almas_para_vida --- #
    def _sumar_almas_para_vida(self, cantidad):
        """Loop positivo 'Rosario de Vida': cada ALMAS_POR_VIDA almas → +1 vida (tope VIDAS_MAXIMAS)."""
        self.jugador.almas_para_vida += cantidad
        while self.jugador.almas_para_vida >= ALMAS_POR_VIDA:
            self.jugador.almas_para_vida -= ALMAS_POR_VIDA
            if self.jugador.vidas < VIDAS_MAXIMAS:
                self.jugador.vidas += 1
                self.audio.reproducir("vida_extra")
                self.flash = 0.12
                self.flash_color = AMARILLO
                self.efecto_hud.iniciar("escala", 1.25, 0.2)
                self.hud.mostrar_mensaje("¡VIDA EXTRA · 10 ALMAS CONSAGRADAS!", 2, 3.0)

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
                self._sumar_almas_para_vida(1)

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

                # Curación y Consagración de Almas: El Pacto del Farol (3 Grados)
                almas_tramo = self.jugador.almas - getattr(self, "almas_consagradas", 0)
                msg_partes = ["FAROL CONSAGRADO"]
                if almas_tramo >= ALMAS_FILO_ANIMA:
                    checkpoint.tier = 3
                    self.jugador.escudo_farol = True
                    self.jugador.filo_anima = True
                    self.destello_manto = 0.45
                    msg_partes.append("Fuego Fatuo (Filo de Ánima y Manto)")
                elif almas_tramo >= ALMAS_MANTO_FAROL:
                    checkpoint.tier = 2
                    self.jugador.escudo_farol = True
                    self.destello_manto = 0.40
                    msg_partes.append("Bendición del Manto")
                elif almas_tramo >= 1:
                    checkpoint.tier = 1
                    msg_partes.append("Consagración Básica")
                else:
                    checkpoint.tier = 0
                    msg_partes.append("Punto de control registrado")

                if checkpoint.tier > 0:
                    self.particulas.consagracion_farol(checkpoint.rect.centerx, checkpoint.rect.bottom, checkpoint.tier)
                    if checkpoint.tier == 1:
                        self.audio.reproducir("farol_tier_1")
                    elif checkpoint.tier == 2:
                        self.audio.reproducir("farol_tier_2")
                    elif checkpoint.tier >= 3:
                        self.audio.reproducir("farol_tier_3")

                if self.jugador.vidas < VIDAS_INICIALES:
                    self.jugador.vidas += 1
                    msg_partes.append("(+1 Vida)")

                self.almas_consagradas = self.jugador.almas
                self.almas_vida_consagradas = self.jugador.almas_para_vida
                self.hud.mostrar_mensaje(" · ".join(msg_partes), 2, 4.5)

    # --- Función actualizar_tutorial_contextual --- #
    def actualizar_tutorial_contextual(self):
        col = self.jugador.rect.x // TILE
        if col < 26:
            zona = 1
            msg = "MOVIMIENTO Y SALTO · WASD / FLECHAS: Mover · ESPACIO: Salto variable (tap corto / mantener)"
        elif col < 32:
            zona = 2
            msg = "FOSO DE SALTO · Medí tu impulso. Si caés, usá los escalones de la trinchera para subir"
        elif col < 58:
            zona = 3
            msg = "FAROL DE REPOSO (F) · Con 5 o más almas consagradas recibís el Manto Protector"
        else:
            zona = 4
            msg = "PORTÓN DEL UMBRAL (G) · Cruzá hacia El Camposanto"

        if getattr(self, "tutorial_zona_actual", None) != zona:
            self.tutorial_zona_actual = zona
            self.hud.mostrar_mensaje(msg, 2, 5.5, forzar=True)

    # --- Función actualizar_power_ups_rango --- #
    def actualizar_power_ups_rango(self):
        carcelero_vivo = any(mj.vivo for mj in getattr(self.nivel, "minijefes", []))
        for power_up in self.nivel.power_ups_rango:
            power_up.sellado = carcelero_vivo
            if (
                power_up.sellado
                and not power_up.recogida
                and power_up.rect.colliderect(self.jugador.rect)
                and self.hud_aviso_altar <= 0
            ):
                self.hud_aviso_altar = 3.0
                self.hud.mostrar_mensaje("ALTAR SELLADO · Derrotá al Carcelero del Osario para liberar la Guadaña", 2, 3.0)
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
                self.texto_ayuda = "¡GUADAÑA CONSAGRADA OBTENIDA! · ALCANCE ESPECTRAL Y CORAZA DEL CUSTODIO VULNERABLE"
                self.mostrar_ayuda = 4.0
                self.hud.mostrar_mensaje(
                    f"¡GUADAÑA CONSAGRADA! · Alcance {ATAQUE_ALCANCE_MEJORADO}px · Quiebra la coraza del Custodio",
                    3,
                    4.0,
                )

    # --- Función perder_vida --- #
    def perder_vida(self, ignorar_invulnerabilidad=False, causa="Peligros de la cripta"):
        if self.jugador.invulnerable > 0 and not ignorar_invulnerabilidad:
            return

        # Si el jugador posee el Manto del Farol, absorbe el golpe letal
        if getattr(self.jugador, "escudo_farol", False):
            self.jugador.escudo_farol = False
            self.jugador.invulnerable = INVULNERABILIDAD
            self.audio.reproducir("rebote_pala")
            self.particulas.emitir(
                self.jugador.rect.centerx,
                self.jugador.rect.centery,
                24,
                ((120, 220, 255), (200, 245, 255), BLANCO),
                220,
                0.7,
                4,
            )
            self.flash = 0.15
            self.flash_color = (120, 220, 255)
            self.destello_manto = 0.38
            self.hud.mostrar_mensaje("¡MANTO DEL FAROL CONSUMIDO! · Daño absorbido", 2, 2.5)
            return

        self.jugador.vidas -= 1
        self.jugador.filo_anima = False
        self.audio.reproducir("daño")
        self.particulas.daño(self.jugador.rect.centerx, self.jugador.rect.centery)
        self.camara.sacudir(9.0, 0.22, dir_x=-self.jugador.direccion, dir_y=-0.5)
        self.flash = 0.16
        self.flash_color = ROJO
        self.almas_combo_count = 0
        self.almas_combo_timer = 0.0

        if self.jugador.vidas <= 0:
            self.muertes_totales += 1
            self.causa_muerte = causa
            self.estado = "derrota"
            self.audio.detener_dron()
            self.audio.reproducir("muerte")
            return

        self.hitstop = 0.08

        if self.punto_reintento is not None:
            self.jugador.almas = getattr(self, "almas_consagradas", 0)
            self.jugador.almas_para_vida = getattr(self, "almas_vida_consagradas", 0)
            checkpoint_x = self.punto_reintento[0]
            for alma in self.nivel.almas:
                if alma.rect.x >= checkpoint_x:
                    alma.reiniciar()
            tenia_guadaña = self.jugador.rango_ataque_mejorado
            tenia_pala = self.jugador.tiene_pala
            tenia_dash = self.jugador.tiene_dash
            self.jugador.respawn(*self.punto_reintento)
            # respawn() limpia el contador del Rosario: restaurar lo consagrado en el farol.
            self.jugador.almas_para_vida = getattr(self, "almas_vida_consagradas", 0)
            self.jugador.rango_ataque_mejorado = tenia_guadaña
            self.jugador.tiene_pala = tenia_pala
            self.jugador.tiene_dash = tenia_dash
        else:
            self.jugador.almas = 0
            self.jugador.almas_para_vida = 0
            for alma in self.nivel.almas:
                alma.reiniciar()
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
        for mj in getattr(self.nivel, "minijefes", []):
            if mj.vivo:
                mj.reiniciar()
        self.camara.actualizar(self.jugador, self.nivel, 1.0)

    # --- Función reintentar_nivel --- #
    def reintentar_nivel(self):
        """Reinicia desde el último Farol activado o desde el inicio del nivel con vidas iniciales."""
        if self.punto_reintento is not None:
            self.jugador.vidas = VIDAS_INICIALES
            self.jugador.almas = getattr(self, "almas_consagradas", 0)
            self.jugador.almas_para_vida = getattr(self, "almas_vida_consagradas", 0)
            checkpoint_x = self.punto_reintento[0]
            for alma in self.nivel.almas:
                if alma.rect.x >= checkpoint_x:
                    alma.reiniciar()
            for enemigo in self.nivel.enemigos:
                if enemigo.rect.x >= checkpoint_x - TILE * 2:
                    enemigo.reiniciar()
            for em in self.nivel.enemigos_melee:
                if em.rect.x >= checkpoint_x - TILE * 2:
                    em.reiniciar()
            for mj in getattr(self.nivel, "minijefes", []):
                # Un Carcelero ya derrotado no resucita: el altar sigue libre.
                if mj.vivo:
                    mj.reiniciar()
            if self.jefe is not None and self.jefe.vivo:
                self.jefe.reiniciar()
                self.ondas_jefe = []
            tenia_guadaña = self.jugador.rango_ataque_mejorado
            tenia_pala = self.jugador.tiene_pala
            tenia_dash = self.jugador.tiene_dash
            self.jugador.respawn(*self.punto_reintento)
            # respawn() limpia el contador del Rosario: restaurar lo consagrado en el farol.
            self.jugador.almas_para_vida = getattr(self, "almas_vida_consagradas", 0)
            self.jugador.rango_ataque_mejorado = tenia_guadaña
            self.jugador.tiene_pala = tenia_pala
            self.jugador.tiene_dash = tenia_dash
            self.camara.actualizar(self.jugador, self.nivel, 1.0)
            self.audio.iniciar_dron()
        else:
            self.cargar_nivel(self.nivel_indice, vidas=VIDAS_INICIALES)

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

    # --- Función crear_vineta_carmesi --- #
    def crear_vineta_carmesi(self):
        vineta = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        small_w, small_h = 160, 90
        small = pygame.Surface((small_w, small_h), pygame.SRCALPHA)
        cx, cy = small_w / 2, small_h / 2
        for y in range(small_h):
            for x in range(small_w):
                dx = (x - cx) / (cx * 0.90)
                dy = (y - cy) / (cy * 0.85)
                dist = math.hypot(dx, dy)
                if dist > 0.70:
                    factor = min(1.0, (dist - 0.70) / 0.50)
                    alfa = int(70 * (factor ** 2))
                    small.set_at((x, y), (112, 22, 34, min(255, alfa)))
        pygame.transform.smoothscale(small, (ANCHO, ALTO), vineta)
        return vineta

    # --- Función dibujar_marco_heraldico --- #
    def dibujar_marco_heraldico(self, destino, x, y, ancho, alto, color_fondo=(14, 11, 20, 235), color_borde=None):
        """Marco heráldico gótico consistente con esquinas doradas (Principio 4 de UX)."""
        borde_oro = HUD_ORO
        borde_linea = color_borde if color_borde is not None else (*HUD_BORDE, 200)
        panel = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(panel, color_fondo, (0, 0, ancho, alto), border_radius=12)
        pygame.draw.rect(panel, borde_linea, (0, 0, ancho, alto), 1, border_radius=12)
        pygame.draw.rect(panel, borde_oro, (0, 0, ancho, alto), 2, border_radius=12)
        pygame.draw.line(panel, (*borde_oro, 140), (16, 1), (ancho - 16, 1), 1)
        pygame.draw.line(panel, (*borde_oro, 140), (16, alto - 1), (ancho - 16, alto - 1), 1)
        for vx, vy, vdx, vdy in ((0, 0, 1, 1), (ancho, 0, -1, 1), (0, alto, 1, -1), (ancho, alto, -1, -1)):
            pygame.draw.line(panel, borde_oro, (vx + 6 * vdx, vy), (vx + 22 * vdx, vy), 2)
            pygame.draw.line(panel, borde_oro, (vx, vy + 6 * vdy), (vx, vy + 22 * vdy), 2)
        destino.blit(panel, (x, y))

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
        halo_luna = pygame.Surface((160, 160), pygame.SRCALPHA)
        for r in range(76, 20, -4):
            norm = (r - 20) / 56.0
            a = int(24 * (1.0 - norm * norm))
            pygame.draw.circle(halo_luna, (210, 215, 175, a), (80, 80), r)
        destino.blit(halo_luna, (luna_x - 80, luna_y - 80))
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

        # Ventanales góticos ojivales con haz de luz lunar diagonal (paralaje 0.18)
        win_w = 320
        offset_w = int(self.camara.x * 0.18) % win_w
        haz_lunar = _obtener_haz_lunar(h)
        for i in range(-1, int(w / win_w) + 2):
            wx = i * win_w - offset_w + 80
            wy = 24
            ww, wh = 38, 86
            # Marco exterior de piedra oscura
            pygame.draw.rect(destino, (20, 18, 28), (wx - 2, wy + 16, ww + 4, wh - 16))
            pygame.draw.arc(destino, (20, 18, 28), (wx - 2, wy, ww + 4, 36), 0.0, 3.14, 3)
            # Cristal lunar translúcido
            pygame.draw.rect(destino, (32, 45, 64), (wx, wy + 18, ww, wh - 18))
            pygame.draw.arc(destino, (32, 45, 64), (wx, wy + 2, ww, 34), 0.0, 3.14, 2)
            # Tracería gótica (cruz de plomo)
            pygame.draw.line(destino, (22, 26, 36), (wx + ww // 2, wy + 6), (wx + ww // 2, wy + wh), 1)
            pygame.draw.line(destino, (22, 26, 36), (wx, wy + 42), (wx + ww, wy + 42), 1)
            # Haz de luz lunar diagonal proyectado hacia el suelo (translúcido y suave)
            destino.blit(haz_lunar, (wx - 10, wy + 10))

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

        # Resplandor de velas lejanas (paralaje 0.48, iluminación translúcida)
        torch_w = 360
        offset_t = int(self.camara.x * 0.48) % torch_w
        for i in range(-1, int(w / torch_w) + 2):
            x = i * torch_w - offset_t + 110
            base_y = h - 160
            halo_vela = pygame.Surface((44, 44), pygame.SRCALPHA)
            for r in range(20, 2, -2):
                norm = r / 20.0
                a = int(28 * (1.0 - norm * norm))
                pygame.draw.circle(halo_vela, (255, 180, 60, a), (22, 22), r)
            destino.blit(halo_vela, (x - 22, base_y - 22))

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

        # Marco heráldico litúrgico consistente (Principio 4 UX)
        pw, ph = 840, 520
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2 - 10
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph)

        # Título y ambientación
        self.dibujar_texto(TITULO, 0, py + 34, 76, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto(SUBTITULO, 0, py + 120, 22, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 140), (ANCHO // 2 - 160, py + 154), (ANCHO // 2 + 160, py + 154), 1)

        historia = (
            "El sepulturero bajó a la cripta a cumplir su jornada. "
            "La puerta de hierro se cerró a sus espaldas y la oscuridad despertó. "
            "Con su pala y su farol de sombra, debe hallar la salida antes de que la muerte lo alcance."
        )
        self.dibujar_parrafo(historia, 0, py + 184, 19, CREMA, ancho=68, centrado=True, interlineado=26)

        # Prompt de avance
        pulso = 0.5 + 0.5 * math.sin(self.tiempo_titulo * 4)
        alfa_prompt = int(170 + pulso * 85)
        color_prompt = (int(TURQUESA[0] * (alfa_prompt / 255)), int(TURQUESA[1] * (alfa_prompt / 255)), int(TURQUESA[2] * (alfa_prompt / 255)))
        self.dibujar_texto("PRESIONÁ ENTER PARA COMENZAR LA VIGILIA", 0, py + ph - 70, 20, color_prompt, centrado=True, sombra=True)
        self.dibujar_texto("[ENTER] Continuar · [ESC] Salir", 0, py + ph - 34, 13, HUD_MUTED, centrado=True)

    # --- Función dibujar_menu_principal --- #
    def dibujar_menu_principal(self):
        self.dibujar_fondo(self.pantalla)
        self.pantalla.blit(self.vineta, (0, 0))

        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((5, 4, 10, 165))
        self.pantalla.blit(velo, (0, 0))

        pw, ph = 740, 580
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2 - 10
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph)

        # Encabezado
        self.dibujar_texto(TITULO, 0, py + 30, 68, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto("PLATAFORMERO GÓTICO 2D · UNAHUR", 0, py + 104, 16, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 140), (ANCHO // 2 - 160, py + 132), (ANCHO // 2 + 160, py + 132), 1)

        # Opciones del menú (4 opciones claras ordenadas según principio 5)
        opciones = [
            ("JUGAR CAMPAÑA", "Preludio + 3 Niveles continuos sin volver al menú"),
            ("SELECCIÓN DE NIVEL", "Preludio, Camposanto, Cripta, Osario o Salas de Prueba"),
            ("CONFIGURACIÓN", "Presets de teclado (WASD / Retro), calidad, HUD y accesibilidad"),
            ("CRÉDITOS & MARCO TEÓRICO", "Equipo UNAHUR, Principios UX y Matriz MDA"),
        ]

        ancho_caja = 640
        alto_caja = 68
        x_caja = (ANCHO - ancho_caja) // 2
        y_base = py + 144

        for i, (titulo_op, subtitulo_op) in enumerate(opciones):
            y_caja = y_base + i * 84
            seleccionada = (i == self.menu_opcion)

            surf_op = pygame.Surface((ancho_caja, alto_caja), pygame.SRCALPHA)
            color_fondo = (32, 24, 42, 235) if seleccionada else (16, 13, 22, 180)
            pygame.draw.rect(surf_op, color_fondo, (0, 0, ancho_caja, alto_caja), border_radius=8)

            color_borde = HUD_ORO if seleccionada else (*HUD_BORDE, 150)
            grosor_borde = 2 if seleccionada else 1
            pygame.draw.rect(surf_op, color_borde, (0, 0, ancho_caja, alto_caja), grosor_borde, border_radius=8)

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
            self.dibujar_texto(prefijo + titulo_op, x_caja + 24, y_caja + 12, 20, color_titulo, sombra=seleccionada)
            self.dibujar_texto(subtitulo_op, x_caja + 50, y_caja + 38, 12, CREMA if seleccionada else HUD_MUTED)

        # Pie de página instructivo constante (Principio 2 UX)
        self.dibujar_texto(
            "[↑/↓ / WASD] Elegir · [ENTER] Confirmar · [ESC] Volver",
            0, py + ph - 36, 13, HUD_MUTED, centrado=True,
        )

    # --- Función dibujar_seleccion_nivel --- #
    def dibujar_seleccion_nivel(self):
        self.dibujar_fondo(self.pantalla)
        self.pantalla.blit(self.vineta, (0, 0))

        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((5, 4, 10, 175))
        self.pantalla.blit(velo, (0, 0))

        pw, ph = 840, 620
        px = (ANCHO - pw) // 2
        py = 40
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph)

        # Título
        self.dibujar_texto("SELECCIÓN DE NIVEL & SALAS", 0, py + 20, 36, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto("Elegí el tramo de la cripta o sala técnica para descender", 0, py + 58, 14, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 130), (ANCHO // 2 - 180, py + 78), (ANCHO // 2 + 180, py + 78), 1)

        datos_niveles = [
            (
                "0",
                "PRELUDIO · EL RITUAL DEL SEPULTURERO",
                "80 cols · Sensibilidad de salto, altar del farol y travesía segura",
                "Aprende el oficio sin peligros de muerte antes de descender a las profundidades.",
            ),
            (
                "I",
                "NIVEL I · EL CAMPOSANTO",
                "150 cols · Salto de precisión y altar del Dash de sombra",
                "Arranque melancólico bajo la luna llena. Los arcos de almas marcan la trayectoria.",
            ),
            (
                "II",
                "NIVEL II · LA CRIPTA",
                "130 cols · Recogida de pala y el salto de la ventana alta",
                "Fosos oscuros, combate con pala y el desafío final de la pared vertical.",
            ),
            (
                "III",
                "NIVEL III · EL OSARIO",
                "160 cols · Guadaña imperial y el Custodio en 2 fases",
                "El clímax final: power-up de rango consagrado, centinelas y duelo con el jefe.",
            ),
            (
                "★",
                "SALAS DE PRUEBA · RETOS MECÁNICOS",
                "6 desafíos aislados · Pozo de dash, salto de ventana y combate",
                "Espacio de experimentación técnica y verificación de mecánicas góticas.",
            ),
        ]

        ancho_tarjeta = 760
        alto_tarjeta = 82
        x_tarjeta = (ANCHO - ancho_tarjeta) // 2
        y_base = py + 92

        for i, (insignia, titulo_n, subtitulo_n, desc_n) in enumerate(datos_niveles):
            y_tarjeta = y_base + i * 94
            seleccionada = (i == self.nivel_seleccionado)

            surf_tarjeta = pygame.Surface((ancho_tarjeta, alto_tarjeta), pygame.SRCALPHA)
            color_fondo = (32, 22, 40, 235) if seleccionada else (16, 12, 22, 185)
            pygame.draw.rect(surf_tarjeta, color_fondo, (0, 0, ancho_tarjeta, alto_tarjeta), border_radius=8)

            color_borde = HUD_ORO if seleccionada else (*HUD_BORDE, 160)
            grosor = 2 if seleccionada else 1
            pygame.draw.rect(surf_tarjeta, color_borde, (0, 0, ancho_tarjeta, alto_tarjeta), grosor, border_radius=8)

            if seleccionada:
                pygame.draw.rect(surf_tarjeta, HUD_ORO, (0, 8, 4, alto_tarjeta - 16), border_radius=2)
                for ex, ey, edx, edy in ((0, 0, 1, 1), (ancho_tarjeta, 0, -1, 1), (0, alto_tarjeta, 1, -1), (ancho_tarjeta, alto_tarjeta, -1, -1)):
                    pygame.draw.line(surf_tarjeta, HUD_ORO, (ex + 6 * edx, ey), (ex + 16 * edx, ey), 1)
                    pygame.draw.line(surf_tarjeta, HUD_ORO, (ex, ey + 6 * edy), (ex, ey + 14 * edy), 1)

            self.pantalla.blit(surf_tarjeta, (x_tarjeta, y_tarjeta))

            # Insignia romana / estrella
            color_num = HUD_ORO if seleccionada else (120, 105, 130)
            self.dibujar_texto(insignia, x_tarjeta + 24, y_tarjeta + 18, 32, color_num, sombra=seleccionada)

            # Textos descriptivos
            prefijo = "▸  " if seleccionada else ""
            color_tit = HUD_ORO if seleccionada else HUD_TEXTO
            self.dibujar_texto(prefijo + titulo_n, x_tarjeta + 76, y_tarjeta + 10, 17, color_tit, sombra=seleccionada)
            self.dibujar_texto(subtitulo_n, x_tarjeta + 76, y_tarjeta + 34, 12, HUD_VERDE if seleccionada else HUD_MUTED)
            self.dibujar_texto(desc_n, x_tarjeta + 76, y_tarjeta + 54, 12, CREMA if seleccionada else (170, 160, 175))

        # Pie de página instructivo constante (Principio 2 UX)
        self.dibujar_texto(
            "[↑/↓ / WASD] Elegir · [ENTER] Descender / Probar · [ESC] Volver al Menú",
            0, py + ph - 30, 13, HUD_MUTED, centrado=True,
        )

    # --- Función dibujar_selector_pruebas --- #
    def dibujar_selector_pruebas(self):
        self.dibujar_fondo(self.pantalla)
        self.pantalla.blit(self.vineta, (0, 0))

        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((5, 4, 10, 180))
        self.pantalla.blit(velo, (0, 0))

        pw, ph = 840, 620
        px = (ANCHO - pw) // 2
        py = 40
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph)

        self.dibujar_texto("SALAS DE PRUEBA TÉCNICA", 0, py + 20, 36, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto("Verificación experimental de mecánicas góticas en entornos aislados", 0, py + 58, 14, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 130), (ANCHO // 2 - 180, py + 78), (ANCHO // 2 + 180, py + 78), 1)

        ancho_tarjeta = 760
        alto_tarjeta = 70
        x_tarjeta = (ANCHO - ancho_tarjeta) // 2
        y_base = py + 90

        for i, sala in enumerate(SALAS_PRUEBA):
            y_tarjeta = y_base + i * 78
            seleccionada = (i == self.test_opcion)

            surf_tarjeta = pygame.Surface((ancho_tarjeta, alto_tarjeta), pygame.SRCALPHA)
            color_fondo = (32, 22, 40, 235) if seleccionada else (16, 12, 22, 185)
            pygame.draw.rect(surf_tarjeta, color_fondo, (0, 0, ancho_tarjeta, alto_tarjeta), border_radius=8)

            color_borde = HUD_ORO if seleccionada else (*HUD_BORDE, 160)
            grosor = 2 if seleccionada else 1
            pygame.draw.rect(surf_tarjeta, color_borde, (0, 0, ancho_tarjeta, alto_tarjeta), grosor, border_radius=8)

            if seleccionada:
                pygame.draw.rect(surf_tarjeta, HUD_ORO, (0, 8, 4, alto_tarjeta - 16), border_radius=2)
                for ex, ey, edx, edy in ((0, 0, 1, 1), (ancho_tarjeta, 0, -1, 1), (0, alto_tarjeta, 1, -1), (ancho_tarjeta, alto_tarjeta, -1, -1)):
                    pygame.draw.line(surf_tarjeta, HUD_ORO, (ex + 6 * edx, ey), (ex + 16 * edx, ey), 1)
                    pygame.draw.line(surf_tarjeta, HUD_ORO, (ex, ey + 6 * edy), (ex, ey + 14 * edy), 1)

            self.pantalla.blit(surf_tarjeta, (x_tarjeta, y_tarjeta))

            color_num = HUD_ORO if seleccionada else (120, 105, 130)
            self.dibujar_texto(str(i + 1), x_tarjeta + 24, y_tarjeta + 16, 28, color_num, sombra=seleccionada)

            prefijo = "▸  " if seleccionada else ""
            color_tit = HUD_ORO if seleccionada else HUD_TEXTO
            nombre_sala = sala.get("nombre", f"Sala de Prueba {i + 1}")
            desc_sala = sala.get("desc", "Verificación de mecánicas")
            self.dibujar_texto(prefijo + nombre_sala, x_tarjeta + 70, y_tarjeta + 12, 16, color_tit, sombra=seleccionada)
            self.dibujar_texto(desc_sala, x_tarjeta + 70, y_tarjeta + 38, 12, HUD_VERDE if seleccionada else HUD_MUTED)

        self.dibujar_texto(
            "[↑/↓ / WASD] Elegir · [1-6 / ENTER] Probar · [ESC] Volver",
            0, py + ph - 30, 13, HUD_MUTED, centrado=True,
        )

    # --- Función dibujar_creditos --- #
    def dibujar_creditos(self):
        self.dibujar_fondo(self.pantalla)
        self.pantalla.blit(self.vineta, (0, 0))

        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((5, 4, 10, 185))
        self.pantalla.blit(velo, (0, 0))

        # Marco heráldico central
        ancho_m = 840
        alto_m = 610
        x_m = (ANCHO - ancho_m) // 2
        y_m = (ALTO - alto_m) // 2
        self.dibujar_marco_heraldico(self.pantalla, x_m, y_m, ancho_m, alto_m)

        # Título
        self.dibujar_texto("IN CRYPTA", 0, y_m + 22, 42, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto("CRÉDITOS, UX Y MARCO TEÓRICO (UNAHUR)", 0, y_m + 68, 15, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 140), (ANCHO // 2 - 140, y_m + 92), (ANCHO // 2 + 140, y_m + 92), 1)

        # Bloque de integrantes
        self.dibujar_texto("EQUIPO 6 — UNAHUR", 0, y_m + 104, 17, HUD_ORO, centrado=True)
        for idx, nombre in enumerate(INTEGRANTES):
            self.dibujar_texto(nombre, 0, y_m + 130 + idx * 24, 16, HUD_TEXTO, centrado=True)

        self.dibujar_texto("Taller de Diseño Conceptual · Introducción a los Videojuegos", 0, y_m + 210, 14, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_BORDE, 120), (ANCHO // 2 - 180, y_m + 234), (ANCHO // 2 + 180, y_m + 234), 1)

        # Matriz MDA
        self.dibujar_texto("MATRIZ MDA (MECÁNICAS · DINÁMICAS · ESTÉTICAS)", 0, y_m + 244, 16, HUD_ORO, centrado=True)
        mda_1 = "• Mecánicas: Salto sensible al input, Dash aéreo de sombra, Ataque frontal y Pisotón."
        mda_2 = "• Dinámicas: Riesgo/Recompensa en fosos de almas, Stomp-Dash encadenado, Faroles de reposo."
        mda_3 = "• Estéticas: Melancolía litúrgica, Sensación de logro y Desafío gótico de precisión."
        self.dibujar_texto(mda_1, 0, y_m + 270, 13, CREMA, centrado=True)
        self.dibujar_texto(mda_2, 0, y_m + 292, 13, CREMA, centrado=True)
        self.dibujar_texto(mda_3, 0, y_m + 314, 13, CREMA, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_BORDE, 120), (ANCHO // 2 - 180, y_m + 338), (ANCHO // 2 + 180, y_m + 338), 1)

        # Los 4 Tipos de Interfaz
        self.dibujar_texto("LOS 4 TIPOS DE INTERFAZ (APUNTE UI/UX UNAHUR)", 0, y_m + 348, 16, HUD_ORO, centrado=True)
        ui_1 = "1. No Diegética: Riel fijo 1232×72 sin layout shifts ([HP], Corazones, Grilla 2×2, Reloj)."
        ui_2 = "2. Diegética: Farol del sepulturero (llama turquesa/ámbar) y faroles de reposo (F) encendidos."
        ui_3 = "3. Espacial: Carteles flotantes en el mundo sobre altares de Dash (D), Pala (W) y Guadaña (X)."
        ui_4 = "4. Meta: Viñeta carmesí a 1 HP sincrónica con latido cardíaco (55 Hz) y destello del Manto."
        self.dibujar_texto(ui_1, 0, y_m + 372, 12, (200, 195, 215), centrado=True)
        self.dibujar_texto(ui_2, 0, y_m + 392, 12, (200, 195, 215), centrado=True)
        self.dibujar_texto(ui_3, 0, y_m + 412, 12, (200, 195, 215), centrado=True)
        self.dibujar_texto(ui_4, 0, y_m + 432, 12, (200, 195, 215), centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_BORDE, 120), (ANCHO // 2 - 180, y_m + 456), (ANCHO // 2 + 180, y_m + 456), 1)

        # Los 5 Principios de UX
        self.dibujar_texto("LOS 5 PRINCIPIOS DE UX (UNAHUR)", 0, y_m + 466, 16, HUD_ORO, centrado=True)
        ux_resumen = "1. Facilidad visual · 2. Rapidez y leyendas · 3. Comodidad dual · 4. Consistencia heráldica · 5. Fluidez de menús"
        self.dibujar_texto(ux_resumen, 0, y_m + 490, 13, HUD_VERDE, centrado=True)

        # Pie instructivo
        self.dibujar_texto("[ENTER / ESC] Volver al Menú Principal", 0, y_m + alto_m - 34, 15, TURQUESA, centrado=True, sombra=True)

    # --- Función dibujar_configuracion --- #
    def dibujar_configuracion(self):
        """Pantalla de Configuración gótica con 2 presets de teclado y esqueleto para opciones."""
        self.dibujar_fondo(self.pantalla)
        self.pantalla.blit(self.vineta, (0, 0))

        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((5, 4, 10, 175))
        self.pantalla.blit(velo, (0, 0))

        pw, ph = 880, 650
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2 - 10
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph)

        # Encabezado
        self.dibujar_texto("CONFIGURACIÓN DEL SANTUARIO", 0, py + 18, 36, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto("AJUSTES DE CONTROLES, SHADERS, INTERFAZ Y ACCESIBILIDAD", 0, py + 58, 13, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 120), (ANCHO // 2 - 200, py + 78), (ANCHO // 2 + 200, py + 78), 1)

        # Estado de opciones
        preset_activo = PRESETS_TECLADO[self.preset_teclado_idx]
        shader_activo = OPCIONES_SHADER[self.config_shader_idx]
        calidad_activa = OPCIONES_CALIDAD[self.config_calidad_idx]
        hud_activo = OPCIONES_HUD[self.config_hud_idx]
        acc_activa = "Activada" if self.reducir_movimiento else "Desactivada"
        audio_activo = "Activado" if getattr(self.audio, "activo", False) else "Silenciado"

        desc_shader = (
            "Bloom místico + scanlines CRT tenues para cohesión de pixel art y texto" if self.config_shader_idx == 0 else
            "Resplandor suave difuso sin scanlines horizontales" if self.config_shader_idx == 1 else
            "Renderizado plano directo sin filtros de post-procesado"
        )
        desc_calidad = (
            "Halos de luz completos, penumbra y 100% de partículas" if self.config_calidad_idx == 0 else
            "Máscara de penumbra activa y 50% de partículas de bioma" if self.config_calidad_idx == 1 else
            "Sin penumbra pesada para 60 FPS garantizados en PCs modestos"
        )
        desc_hud = (
            "Riel superior completo + canal único de mensajes con 100% opacidad" if self.config_hud_idx == 0 else
            "Riel superior con opacidad translúcida (alpha 140) y canal sutil" if self.config_hud_idx == 1 else
            "HUD oculto en exploración; emerge ante jefes, daño o recolección"
        )

        opciones = [
            ("CONTROLES / TECLADO", preset_activo["etiqueta"], preset_activo["desc"]),
            ("EFECTOS / SHADERS", shader_activo, desc_shader),
            ("CALIDAD GRÁFICA", calidad_activa, desc_calidad),
            ("MODO DE HUD", hud_activo, desc_hud),
            ("ACCESIBILIDAD", acc_activa, "Reducir movimiento: elimina sacudidas de cámara bruscas"),
            ("AUDIO Y SONIDO", audio_activo, "Música litúrgica, dron ambiental y efectos fúnebres"),
            ("VOLVER AL MENÚ", "Guardar y regresar", "Aplicar cambios y regresar a la pantalla anterior"),
        ]

        ancho_caja = 800
        alto_caja = 50
        x_caja = (ANCHO - ancho_caja) // 2
        y_base = py + 88

        for i, (titulo_op, valor_op, desc_op) in enumerate(opciones):
            y_caja = y_base + i * 55
            seleccionada = (i == self.config_opcion)

            surf_op = pygame.Surface((ancho_caja, alto_caja), pygame.SRCALPHA)
            color_fondo = (32, 24, 42, 235) if seleccionada else (16, 13, 22, 180)
            pygame.draw.rect(surf_op, color_fondo, (0, 0, ancho_caja, alto_caja), border_radius=6)

            color_borde = HUD_ORO if seleccionada else (*HUD_BORDE, 140)
            grosor_borde = 2 if seleccionada else 1
            pygame.draw.rect(surf_op, color_borde, (0, 0, ancho_caja, alto_caja), grosor_borde, border_radius=6)

            if seleccionada:
                pygame.draw.rect(surf_op, HUD_ORO, (0, 5, 4, alto_caja - 10), border_radius=2)

            self.pantalla.blit(surf_op, (x_caja, y_caja))

            color_titulo = HUD_ORO if seleccionada else HUD_TEXTO
            prefijo = "▸  " if seleccionada else "   "
            self.dibujar_texto(prefijo + titulo_op, x_caja + 14, y_caja + 8, 15, color_titulo, sombra=seleccionada)
            self.dibujar_texto(desc_op, x_caja + 36, y_caja + 28, 11, CREMA if seleccionada else HUD_MUTED)

            # Valor a la derecha
            color_valor = TURQUESA if seleccionada else HUD_ORO
            flechas_val = f"◂ {valor_op} ▸" if seleccionada and i < 6 else valor_op
            self.dibujar_texto(flechas_val, x_caja + ancho_caja - 270, y_caja + 14, 13, color_valor, sombra=seleccionada)

        # Panel de detalle dinámico del preset activo
        y_desglose = y_base + len(opciones) * 55 + 4
        ancho_d = ancho_caja
        alto_d = 62
        surf_d = pygame.Surface((ancho_d, alto_d), pygame.SRCALPHA)
        surf_d.fill((14, 11, 20, 225))
        pygame.draw.rect(surf_d, (*HUD_BORDE, 140), (0, 0, ancho_d, alto_d), 1, border_radius=6)
        self.pantalla.blit(surf_d, (x_caja, y_desglose))

        self.dibujar_texto("DISTRIBUCIÓN DEL PRESET SELECCIONADO:", x_caja + 16, y_desglose + 6, 12, HUD_ORO)
        self.dibujar_texto(preset_activo["resumen"], x_caja + 16, y_desglose + 24, 13, BLANCO)
        self.dibujar_texto("Presiona [← / →] o [ENTER] para alternar opciones", x_caja + 16, y_desglose + 42, 11, HUD_MUTED)

        # Pie instructivo
        self.dibujar_texto(
            "[↑/↓ / WASD] Elegir · [←/→ / ENTER] Cambiar ajuste · [ESC] Volver",
            0, py + ph - 26, 12, HUD_MUTED, centrado=True,
        )

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
        if self.estado == "configuracion":
            self.dibujar_configuracion()
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
        for p in getattr(self, "particulas_bioma", []):
            p.dibujar(destino)

        # Penumbra gótica y claroscuro sutil (alpha 38 / 255)
        # Calidad Alta (0) y Media (1): activa máscara de penumbra suave.
        # Calidad Baja (2): omite el blit de mascara_penumbra pesada para PCs antiguos (60 FPS garantizados).
        if getattr(self, "config_calidad_idx", 0) != 2:
            self.mascara_penumbra.fill((8, 7, 12, 38))
            if self.jugador:
                # Perforación centrada exactamente en el farol colgante del sepulturero
                fx = int(self.jugador.rect.centerx + self.jugador.direccion * 11 - self.camara.x)
                fy = int(self.jugador.rect.y + 19 - self.camara.y)
                radio_farol = 95
                luz_sub = _obtener_luz_perforacion(radio_farol)
                self.mascara_penumbra.blit(
                    luz_sub,
                    (fx - radio_farol, fy - radio_farol),
                    special_flags=pygame.BLEND_RGBA_SUB,
                )
            for cp in self.nivel.checkpoints:
                if cp.activo and self.camara.is_on_screen(cp.rect):
                    cpx = int(cp.rect.centerx - self.camara.x)
                    cpy = int(cp.rect.centery - self.camara.y)
                    self.mascara_penumbra.blit(
                        _obtener_luz_perforacion(65),
                        (cpx - 65, cpy - 65),
                        special_flags=pygame.BLEND_RGBA_SUB,
                    )
            destino.blit(self.mascara_penumbra, (0, 0))

        # Halos de luz aditivos suaves según calidad:
        # Alta (0): Halos completos. Media (1): Halos suaves. Baja (2): Omitidos.
        calidad = getattr(self, "config_calidad_idx", 0)
        if calidad in (0, 1):
            if self.jugador:
                fx = int(self.jugador.rect.centerx + self.jugador.direccion * 11 - self.camara.x)
                fy = int(self.jugador.rect.y + 19 - self.camara.y)
                color_luz = (195, 80, 255) if getattr(self.jugador, "rango_ataque_mejorado", False) else (240, 196, 90)
                factor_base = 0.12 if getattr(self.jugador, "rango_ataque_mejorado", False) else 0.09
                factor_luz = factor_base if calidad == 0 else factor_base * 0.65
                radio_luz = 90 if calidad == 0 else 70
                luz_add = _obtener_luz_calida(radio_luz, color_luz, factor_luz)
                destino.blit(luz_add, (fx - radio_luz, fy - radio_luz), special_flags=pygame.BLEND_RGB_ADD)

            if calidad == 0:
                for cp in self.nivel.checkpoints:
                    if cp.activo and self.camara.is_on_screen(cp.rect):
                        cpx = int(cp.rect.centerx - self.camara.x)
                        cpy = int(cp.rect.centery - self.camara.y)
                        luz_cp = _obtener_luz_calida(70, (90, 200, 255), 0.12)
                        destino.blit(luz_cp, (cpx - 70, cpy - 70), special_flags=pygame.BLEND_RGB_ADD)

        # Escalar mundo virtual a pantalla (zoom 1.25x cinematográfico)
        pw, ph = self.pantalla.get_size()
        pygame.transform.scale(self.superficie_mundo, (pw, ph), self.pantalla)
        # Asegurar canal alfa completamente opaco (255) en la superficie de pantalla
        # para evitar que blits posteriores con SRCALPHA (viñetas/shaders) borren el mundo en Pygame 2.6 clásico
        self.pantalla.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MAX)

        # Filtros de post-procesado / Shaders (0: Gótico Bloom+CRT, 1: Suave Bloom, 2: Puro)
        shader_modo = getattr(self, "config_shader_idx", 0)
        calidad_modo = getattr(self, "config_calidad_idx", 0)

        # 1. Bloom místico sutil (downscale/upscale aditivo) para unificar luces y pixel art
        if shader_modo in (0, 1) and calidad_modo != 2:
            self._aplicar_bloom(self.pantalla, self.pantalla, intensidad=0.12)

        # 2. Scanlines CRT góticas tenues (integración óptica que evita el look "crudo")
        if shader_modo == 0 and calidad_modo != 2:
            if not hasattr(self, "_superficie_scanlines") or self._superficie_scanlines.get_size() != (pw, ph):
                self._superficie_scanlines = self._crear_scanlines_goticas(pw, ph)
            self.pantalla.blit(self._superficie_scanlines, (0, 0))

        # Viñeta gótica en resolución nativa
        if self.vineta.get_size() != (pw, ph):
            self.vineta = pygame.transform.smoothscale(self.vineta, (pw, ph))
        self.pantalla.blit(self.vineta, (0, 0))

        # Viñeta reactiva carmesí sutil en salud crítica (1 HP) en sincronía con el corazón (55 Hz)
        if self.jugador and self.jugador.vidas == 1 and not self.reducir_movimiento:
            if self.vineta_carmesi.get_size() != (pw, ph):
                self.vineta_carmesi = pygame.transform.smoothscale(self.vineta_carmesi, (pw, ph))
            ciclo = (self.timer_corazon / (1.0 / 1.2)) * math.pi
            pulso = math.sin(ciclo)
            alfa_vineta = int(30 + 45 * pulso)
            self.vineta_carmesi.set_alpha(alfa_vineta)
            self.pantalla.blit(self.vineta_carmesi, (0, 0))

        # Destello celeste periférico reactivo al activar o consumir el Manto del Farol
        if getattr(self, "destello_manto", 0.0) > 0:
            alfa_manto = int(min(180, (self.destello_manto / 0.35) * 180))
            if getattr(self, "reducir_movimiento", False):
                alfa_manto = min(40, int(alfa_manto * 0.3))
            if getattr(self, "_superficie_destello_manto", None) is None or self._superficie_destello_manto.get_size() != (pw, ph):
                self._superficie_destello_manto = pygame.Surface((pw, ph), pygame.SRCALPHA)
            self._superficie_destello_manto.fill((0, 0, 0, 0))
            for step in range(12):
                a_step = int(alfa_manto * (1.0 - step / 12.0))
                pygame.draw.rect(
                    self._superficie_destello_manto,
                    (110, 215, 255, a_step),
                    (step * 2, step * 2, pw - step * 4, ph - step * 4),
                    2,
                )
            self.pantalla.blit(self._superficie_destello_manto, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # 3. UI Espacial en resolución nativa — carteles nítidos con sombra litúrgica
        self.dibujar_ui_espacial(self.pantalla, self.camara)

        self.hud.dibujar(self.pantalla, self, self.dt)

        if self.flash > 0:
            alfa = int(110 * (self.flash / 0.16))
            if getattr(self, "reducir_movimiento", False):
                alfa = min(28, int(alfa * 0.25))
            if self.superficie_flash.get_size() != (pw, ph):
                self.superficie_flash = pygame.Surface((pw, ph), pygame.SRCALPHA)
            self.superficie_flash.fill((*self.flash_color, max(0, min(255, alfa))))
            self.pantalla.blit(self.superficie_flash, (0, 0))

        if self.estado == "pausa":
            self.dibujar_menu_pausa()
        elif self.estado == "nivel_completado":
            self.dibujar_relicario_fin_nivel()
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

    # --- Función dibujar_hud --- #
    def dibujar_hud(self):
        """Renderiza el HUD No Diegético desde hud.py (riel fijo 1232x72 px)."""
        self.hud.dibujar(self.pantalla, self, self.dt)

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

    # --- Función dibujar_relicario_fin_nivel --- #
    def dibujar_relicario_fin_nivel(self):
        """Relicario de fin de nivel: resumen litúrgico de almas consagradas, vidas, tiempo y cita poeana."""
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((5, 4, 10, 215))
        self.pantalla.blit(overlay, (0, 0))

        pw, ph = 740, 480
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph)

        nombre_nivel = self.nivel.nombre.upper() if self.nivel and hasattr(self.nivel, "nombre") else f"NIVEL {self.nivel_indice + 1}"
        self.dibujar_texto(f"¡{nombre_nivel} SUPERADO!", 0, py + 22, 34, HUD_ORO, centrado=True, sombra=True)

        cita = CITAS_POE.get(self.nivel_indice, "«Los límites entre la Vida y la Muerte son borrosos e indefinidos.» — E. A. Poe")
        self.dibujar_texto(cita, 0, py + 66, 13, CREMA, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 140), (px + 30, py + 92), (px + pw - 30, py + 92), 1)

        # Estadísticas del nivel
        min_n = int(self.tiempo_nivel) // 60
        seg_n = int(self.tiempo_nivel) % 60
        dec_n = int((self.tiempo_nivel - int(self.tiempo_nivel)) * 10)
        tiempo_str = f"{min_n:02d}:{seg_n:02d}.{dec_n}"

        total_almas_nivel = self.nivel.total_almas if self.nivel else 0
        almas_jugador = self.jugador.almas if self.jugador else 0
        vidas_jugador = self.jugador.vidas if self.jugador else 0

        stats = [
            ("ALMAS CONSAGRADAS EN EL NIVEL", f"{almas_jugador} / {total_almas_nivel}", TURQUESA_ÁNIMA),
            ("VIDAS CONSERVADAS", f"{vidas_jugador} / {VIDAS_MAXIMAS}", HUD_VERDE),
            ("TIEMPO DEL NIVEL", tiempo_str, CREMA),
        ]

        # Rango del nivel
        if self.tiempo_nivel < 90 and almas_jugador >= total_almas_nivel:
            rango_nivel, col_r = "S+ · REQUÍEM PERFECTO", (255, 230, 110)
        elif self.tiempo_nivel < 130:
            rango_nivel, col_r = "S · PURIFICACIÓN VELOZ", HUD_ORO
        elif self.tiempo_nivel < 200:
            rango_nivel, col_r = "A · TRAVESÍA SACRA", (195, 205, 220)
        elif self.tiempo_nivel < 300:
            rango_nivel, col_r = "B · PENITENCIA SUPERADA", CREMA
        else:
            rango_nivel, col_r = "C · SUPERVIVENCIA EN PENUMBRA", HUESO

        y_stat = py + 116
        for etiqueta, valor, color in stats:
            self.dibujar_texto(etiqueta, px + 50, y_stat, 14, HUD_MUTED)
            self.dibujar_texto(valor, px + pw - 50, y_stat, 20, color, sombra=True, derecha=True)
            pygame.draw.line(self.pantalla, (*HUD_BORDE, 90), (px + 30, y_stat + 28), (px + pw - 30, y_stat + 28), 1)
            y_stat += 54

        # Caja de Rango de Nivel
        y_rango = y_stat + 10
        pygame.draw.rect(self.pantalla, (20, 16, 26), (px + 40, y_rango, pw - 80, 42), border_radius=8)
        pygame.draw.rect(self.pantalla, (*col_r, 180), (px + 40, y_rango, pw - 80, 42), 1, border_radius=8)
        self.dibujar_texto(f"RANGO DEL NIVEL: {rango_nivel}", 0, y_rango + 10, 16, col_r, centrado=True, sombra=True)

        # Prompt claro
        pygame.draw.line(self.pantalla, (*HUD_ORO, 140), (px + 30, py + ph - 48), (px + pw - 30, py + ph - 48), 1)
        self.dibujar_texto("[ENTER] Descender al siguiente nivel · [ESC] Menú Principal",
                           0, py + ph - 30, 13, HUD_ORO, centrado=True, sombra=True)

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

    # --- Función dibujar_menu_pausa --- #
    def dibujar_menu_pausa(self):
        """Menú de Pausa litúrgico e interactivo navegable con opciones claras."""
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((8, 6, 12, 195))
        self.pantalla.blit(overlay, (0, 0))

        ancho_panel = 540
        alto_panel = 370
        px = (ANCHO - ancho_panel) // 2
        py = (ALTO - alto_panel) // 2
        self.dibujar_marco_heraldico(self.pantalla, px, py, ancho_panel, alto_panel)

        self.dibujar_texto("PAUSA LITÚRGICA", 0, py + 22, 28, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto("EL RESPIRO DEL SEPULTURERO", 0, py + 56, 14, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 120), (ANCHO // 2 - 100, py + 78), (ANCHO // 2 + 100, py + 78), 1)

        opciones_pausa = [
            ("CONTINUAR", "Reanudar la vigilia en la cripta"),
            ("REINICIAR DESDE FAROL", "Volver al último farol de reposo consagrado"),
            ("REINICIAR NIVEL", "Comenzar el nivel actual desde el inicio"),
            ("VOLVER AL MENÚ", "Regresar a la selección y menú principal"),
        ]

        y_op = py + 98
        for i, (nombre_op, desc_op) in enumerate(opciones_pausa):
            activa = (i == self.pausa_opcion)
            rect_op = pygame.Rect(px + 36, y_op, ancho_panel - 72, 48)
            surf_op = pygame.Surface((rect_op.w, rect_op.h), pygame.SRCALPHA)
            color_bg = (32, 24, 42, 235) if activa else (18, 14, 22, 160)
            pygame.draw.rect(surf_op, color_bg, (0, 0, rect_op.w, rect_op.h), border_radius=6)
            color_border = HUD_ORO if activa else (*HUD_BORDE, 120)
            pygame.draw.rect(surf_op, color_border, (0, 0, rect_op.w, rect_op.h), 1, border_radius=6)
            self.pantalla.blit(surf_op, rect_op.topleft)

            prefijo = "▸ " if activa else "   "
            color_txt = HUD_ORO if activa else HUD_TEXTO
            self.dibujar_texto(f"{prefijo}{nombre_op}", rect_op.x + 16, rect_op.y + 6, 16, color_txt, sombra=activa)
            self.dibujar_texto(desc_op, rect_op.x + 36, rect_op.y + 27, 12, HUD_MUTED)
            y_op += 56

        self.dibujar_texto("[↑/↓ / WASD] Elegir · [ENTER] Confirmar · [ESC / P] Continuar", 0, py + alto_panel - 26, 12, (150, 140, 155), centrado=True)

    # --- Función dibujar_ui_espacial --- #
    def dibujar_ui_espacial(self, destino=None, camara=None):
        """UI Espacial: carteles de enseñanza anclados a coordenadas de pantalla nativa (1280x720)."""
        if not self.jugador or not self.nivel:
            return
        if destino is None:
            destino = self.pantalla
        if camara is None:
            camara = self.camara

        jx = self.jugador.rect.centerx
        jy = self.jugador.rect.centery
        tiempo = pygame.time.get_ticks() / 1000.0
        bobbing = math.sin(tiempo * 4.0) * 3.5

        puntos_clave = []
        es_retro = getattr(self, "preset_teclado_idx", 0) == 1
        tecla_atk = "C / J" if es_retro else "J / Z"
        tecla_dsh = "X / SHIFT" if es_retro else "SHIFT / X"
        tecla_jmp = "Z / ESPACIO" if es_retro else "ESPACIO / W"

        # 1. Dash Power-ups en el nivel (Altar D)
        for dp in getattr(self.nivel, "power_ups_dash", []):
            if not getattr(dp, "recogida", False) and not getattr(dp, "recogido", False):
                puntos_clave.append((dp.rect.centerx, dp.rect.top, f"[{tecla_dsh}] Altar de Sombras · Desbloquea el Dash"))

        # 2. Palas en el nivel (Altar W)
        for p in getattr(self.nivel, "palas", []):
            if not getattr(p, "recogida", False) and not getattr(p, "recogido", False):
                puntos_clave.append((p.rect.centerx, p.rect.top, f"[{tecla_atk}] Pala de Hierro · Atacar y rebotar"))

        # 3. Power-Up X de Rango / Guadaña en el nivel (Altar X)
        for pr in getattr(self.nivel, "power_ups_rango", []):
            if not getattr(pr, "recogida", False) and not getattr(pr, "recogido", False):
                if getattr(pr, "sellado", False):
                    puntos_clave.append((pr.rect.centerx, pr.rect.top, "[X] Altar de Guadaña Sellado · Vence al Carcelero"))
                else:
                    puntos_clave.append((pr.rect.centerx, pr.rect.top, "[X] Guadaña Consagrada · Alcance y filo ampliado"))

        # 4. Faroles de Checkpoint (F)
        for cp in getattr(self.nivel, "checkpoints", []):
            if not getattr(cp, "activo", False):
                puntos_clave.append((cp.rect.centerx, cp.rect.top, "[F] Farol de Reposo · Consagrar almas y curar"))
            else:
                tier_txt = {1: "Tier 1: Purificación", 2: "Tier 2: Bendición del Manto", 3: "Tier 3: Filo de Ánima y Manto"}.get(cp.tier, "Consagrado")
                puntos_clave.append((cp.rect.centerx, cp.rect.top, f"[F] Farol Consagrado · {tier_txt}"))

        # 5. Campanas de Resonancia / Incensarios (I)
        for inc in getattr(self.nivel, "incensarios", []):
            puntos_clave.append((inc.rect.centerx, inc.rect.top, f"[{tecla_atk}] Campana · Repicar para rebotar y recargar Dash"))

        # 6. Puntos pedagógicos del Preludio / Tutorial:
        if getattr(self, "es_tutorial", False):
            puntos_clave.append((18 * TILE, 8 * TILE, f"[{tecla_jmp}] Salto variable (tap corto / mantener alto)"))
            puntos_clave.append((40 * TILE, 8 * TILE, "Foso de salto · Si caés, usá los escalones de la trinchera"))
            puntos_clave.append((74 * TILE, 8 * TILE, "[G] Portón del Umbral hacia El Camposanto"))

        tamano_f = 15
        if tamano_f not in self.fuentes:
            try:
                self.fuentes[tamano_f] = pygame.font.Font(self._ruta_fuente_gotica, tamano_f)
            except Exception:
                self.fuentes[tamano_f] = pygame.font.Font(None, tamano_f)
        fuente = self.fuentes[tamano_f]

        zoom = CAMARA_ZOOM
        for wx, wy, texto in puntos_clave:
            dist = math.hypot(jx - wx, jy - wy)
            if dist <= 160:
                alfa = int(min(240, max(0, (160 - dist) / 45.0 * 240)))
                # Proyección a resolución de pantalla nativa
                sx = int((wx - camara.x) * zoom)
                sy = int((wy - camara.y) * zoom + bobbing)

                img_txt = fuente.render(texto, True, (246, 238, 224))
                tw, th = img_txt.get_size()
                bw, bh = tw + 24, th + 12
                bx = sx - bw // 2
                by = sy - bh - 24

                if -180 <= bx <= ANCHO + 80 and -60 <= by <= ALTO + 60:
                    burbuja = pygame.Surface((bw, bh + 6), pygame.SRCALPHA)
                    pygame.draw.rect(burbuja, (12, 10, 16, min(alfa, 225)), (0, 0, bw, bh), border_radius=6)
                    pygame.draw.rect(burbuja, (200, 160, 64, min(alfa, 230)), (0, 0, bw, bh), 1, border_radius=6)
                    pygame.draw.polygon(burbuja, (200, 160, 64, min(alfa, 230)), [(bw // 2 - 5, bh), (bw // 2 + 5, bh), (bw // 2, bh + 5)])
                    pygame.draw.polygon(burbuja, (12, 10, 16, min(alfa, 225)), [(bw // 2 - 4, bh - 1), (bw // 2 + 4, bh - 1), (bw // 2, bh + 4)])

                    # Sombra envolvente suave
                    img_sombra = fuente.render(texto, True, (0, 0, 0))
                    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
                        burbuja.blit(img_sombra, (12 + ox, 6 + oy))
                    burbuja.blit(img_txt, (12, 6))

                    destino.blit(burbuja, (bx, by))

    def calcular_rango_liturgico(self):
        """Calcula el rango litúrgico de la campaña (S+, S, A, B, C) con base en tiempo, vidas y caídas."""
        t = getattr(self, "tiempo_total", 0.0)
        vidas = self.jugador.vidas if getattr(self, "jugador", None) else 0
        muertes = getattr(self, "muertes_totales", 0)

        if t < 240 or (t < 320 and muertes == 0 and vidas >= 4):
            return "S+ · REQUÍEM SUPREMO", (255, 230, 110)
        elif t < 420 and muertes <= 1:
            return "S · MAESTRO DEL OSARIO", ORO
        elif t < 600 and muertes <= 3:
            return "A · SEPULTURERO SACRO", (195, 205, 220)
        elif t < 900:
            return "B · EXPLORADOR DE CRIPTAS", CREMA
        else:
            return "C · EL OSARIO TE PUSO A PRUEBA", HUESO

    # --- Función dibujar_victoria --- #
    def dibujar_victoria(self):
        """Pantalla de victoria estilizada con panel gótico y estadísticas litúrgicas completas."""
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
        pw, ph = 740, 500
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph)

        # Título
        self.dibujar_texto("¡EL SEPULTURERO ESCAPÓ!", 0, py + 22, 36, ORO, centrado=True, sombra=True)
        self.dibujar_texto("IN CRYPTA · CAMPAÑA COMPLETADA", 0, py + 62, 14, CREMA, centrado=True)
        pygame.draw.line(self.pantalla, (*ORO, 140),
                         (px + 30, py + 86), (px + pw - 30, py + 86), 1)

        # Stats (4 estadísticas de campaña)
        tiempo_min = int(self.tiempo_total) // 60
        tiempo_seg = int(self.tiempo_total) % 60
        tiempo_dec = int((self.tiempo_total - int(self.tiempo_total)) * 10)
        vidas_j = self.jugador.vidas if self.jugador else 0
        stats = [
            ("ALMAS TOTALES COSECHADAS", f"{self.almas_totales}", HUD_ORO),
            ("TIEMPO TOTAL DE CAMPAÑA",  f"{tiempo_min:02d}:{tiempo_seg:02d}.{tiempo_dec}", CREMA),
            ("VIDAS CONSERVADAS",        f"{vidas_j} / {VIDAS_MAXIMAS}", HUD_VERDE),
            ("CAÍDAS TOTALES",           f"{self.muertes_totales}", HUD_ROJO if self.muertes_totales > 0 else HUD_VERDE),
        ]

        y_stat = py + 100
        for etiqueta, valor, color in stats:
            self.dibujar_texto(etiqueta, px + 50, y_stat, 14, HUD_MUTED)
            self.dibujar_texto(valor, px + pw - 50, y_stat, 20, color, sombra=True, derecha=True)
            pygame.draw.line(self.pantalla, (*HUD_BORDE, 90),
                             (px + 30, y_stat + 26), (px + pw - 30, y_stat + 26), 1)
            y_stat += 46

        # Calificación / rango litúrgico (S+, S, A, B, C)
        rango, color_rango = self.calcular_rango_liturgico()

        y_rango = y_stat + 8
        pygame.draw.rect(self.pantalla, (20, 16, 26),
                         (px + 40, y_rango, pw - 80, 44), border_radius=8)
        pygame.draw.rect(self.pantalla, (*color_rango, 180),
                         (px + 40, y_rango, pw - 80, 44), 1, border_radius=8)
        self.dibujar_texto(f"RANGO LITÚRGICO: {rango}", 0, y_rango + 11, 16, color_rango, centrado=True, sombra=True)

        # Cita litúrgica final
        self.dibujar_texto("«Y el alma, redimida del osario, halló su eterno reposo.»", 0, py + ph - 54, 13, CREMA, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 120), (px + 30, py + ph - 38), (px + pw - 30, py + ph - 38), 1)

        # Pie constante (Principio 2 UX)
        self.dibujar_texto("[ENTER] Confirmar · [ESC] Volver al Menú",
                           0, py + ph - 24, 13, HUD_MUTED, centrado=True)

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
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph, color_fondo=(18, 10, 14, 245), color_borde=(160, 40, 50))

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
        self.dibujar_texto("[ENTER] Reintentar · [ESC] Volver al Menú",
                           0, py + 396, 16, HUD_ORO, centrado=True, sombra=True)

    # --- Función dibujar_texto --- #
    def dibujar_texto(self, texto, x, y, tamano=24, color=BLANCO, centrado=False, sombra=False, derecha=False):
        if tamano not in self.fuentes:
            try:
                self.fuentes[tamano] = pygame.font.Font(self._ruta_fuente_gotica, tamano)
            except Exception:
                self.fuentes[tamano] = pygame.font.Font(None, tamano)

        if sombra:
            imagen_sombra = self.fuentes[tamano].render(texto, True, (8, 6, 12))
            rect_sombra = imagen_sombra.get_rect()
            for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (2, 2)):
                if centrado:
                    rect_sombra.center = (ANCHO // 2 + ox, y + oy)
                elif derecha:
                    rect_sombra.topright = (x + ox, y + oy)
                else:
                    rect_sombra.topleft = (x + ox, y + oy)
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
            if self.hitstop > 0:
                self.hitstop = max(0.0, self.hitstop - dt)
                self.camara.actualizar_sacudida(dt)
            else:
                self.actualizar(dt)
            self.dt = dt
            self.hud.actualizar(dt)
            self.dibujar()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    async def run_async(self):
        """Bucle asíncrono para WebAssembly (Pygbag / Pyodide en navegador)."""
        while self.corriendo:
            dt = min(self.reloj.tick(FPS) / 1000, MAX_DT)
            self.procesar_eventos()
            if self.hitstop > 0:
                self.hitstop = max(0.0, self.hitstop - dt)
                self.camara.actualizar_sacudida(dt)
            else:
                self.actualizar(dt)
            self.dt = dt
            self.hud.actualizar(dt)
            self.dibujar()
            pygame.display.flip()
            await asyncio.sleep(0)

        pygame.quit()
        sys.exit()


# --- Arranque directo --- #
if __name__ == "__main__":
    Juego().run()
