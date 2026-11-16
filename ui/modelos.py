#---- Importamos librerias y configuracion ----#
from dataclasses import dataclass, field
from pathlib import Path

import pygame

import config
from config import ALTO, ANCHO, HUD_BORDE, HUD_TEXTO, HUD_VERDE, JEFE_VIDA, VIDAS_MAXIMAS
from ui.animacion import Tween


#---- Constantes de diseno del HUD ----#
HUD_MARGEN_X = 24
HUD_MARGEN_Y = 16
HUD_ALTO = 72
HUD_GAP = 12
HUD_PADDING = 12
HUD_ZONA_IZQ = 336
HUD_ZONA_CENTRO = 512
HUD_ZONA_DER = 360
HUD_MENSAJE_ANCHO = 560
HUD_MENSAJE_ALTO = 48
HUD_MENSAJE_Y = 96

# Tamaños de fuente
FUENTE_LABEL = 12
FUENTE_CONTADOR = 14
FUENTE_NOMBRE = 18

# Ruta absoluta de la fuente gotica legible (trazos firmes sin astas ultrafinas)
_RAIZ_HUD = Path(__file__).resolve().parent.parent
_RUTA_FUENTE = _RAIZ_HUD / getattr(config, "RUTA_FUENTE_GOTICA", "assets/NotoSerif-Bold.ttf")


@dataclass
class HudTheme:
    panel_bg: tuple = (9, 8, 13, 190)
    panel_border: tuple = HUD_BORDE
    panel_border_alpha: int = 200
    linea_oro: tuple = (198, 156, 62, 140)
    texto: tuple = HUD_TEXTO
    texto_secundario: tuple = (170, 158, 146)
    oro: tuple = (198, 156, 62)
    alma: tuple = (92, 190, 174)
    dash_turquesa: tuple = (92, 190, 174)
    rojo: tuple = (112, 22, 34)
    verde: tuple = HUD_VERDE
    negro: tuple = (9, 8, 13)
    corazon_lleno: tuple = (195, 24, 46)
    corazon_vacio_fill: tuple = (38, 30, 42)
    corazon_vacio_borde: tuple = (110, 95, 120)
    jefe_borde_fase1: tuple = (*HUD_BORDE, 200)
    jefe_borde_fase2: tuple = (215, 45, 55)
    jefe_segmento_lleno: tuple = (225, 38, 52)
    jefe_segmento_vacio: tuple = (36, 26, 30)
    guadaña: tuple = (215, 85, 255)
    pala: tuple = (198, 156, 62)

    # Tamaños
    fuente_label: int = FUENTE_LABEL
    fuente_contador: int = FUENTE_CONTADOR
    fuente_nombre: int = FUENTE_NOMBRE
    icono_tamano: int = 16
    corazon_radio: int = 7
    corazon_pitch: int = 28


#---- Distribucion espacial ----#
@dataclass(frozen=True)
class HudLayout:
    riel: pygame.Rect
    zona_izq: pygame.Rect
    zona_centro: pygame.Rect
    zona_der: pygame.Rect
    contenido_izq: pygame.Rect
    contenido_centro: pygame.Rect
    contenido_der: pygame.Rect
    canal_mensajes: pygame.Rect

    @classmethod
    def construir(cls, ancho=ANCHO, alto=ALTO):
        riel = pygame.Rect(HUD_MARGEN_X, HUD_MARGEN_Y,
                           ancho - 2 * HUD_MARGEN_X, HUD_ALTO)
        zona_izq = pygame.Rect(HUD_MARGEN_X, HUD_MARGEN_Y,
                               HUD_ZONA_IZQ, HUD_ALTO)
        zona_centro = pygame.Rect(
            HUD_MARGEN_X + HUD_ZONA_IZQ + HUD_GAP, HUD_MARGEN_Y,
            HUD_ZONA_CENTRO, HUD_ALTO)
        zona_der = pygame.Rect(
            HUD_MARGEN_X + HUD_ZONA_IZQ + HUD_GAP +
            HUD_ZONA_CENTRO + HUD_GAP, HUD_MARGEN_Y,
            HUD_ZONA_DER, HUD_ALTO)
        contenido_izq = pygame.Rect(
            zona_izq.x + HUD_PADDING, HUD_MARGEN_Y + 12,
            HUD_ZONA_IZQ - 2 * HUD_PADDING, HUD_ALTO - 24)
        contenido_centro = pygame.Rect(
            zona_centro.x + HUD_PADDING, HUD_MARGEN_Y + 12,
            HUD_ZONA_CENTRO - 2 * HUD_PADDING, HUD_ALTO - 24)
        contenido_der = pygame.Rect(
            zona_der.x + HUD_PADDING, HUD_MARGEN_Y + 12,
            HUD_ZONA_DER - 2 * HUD_PADDING, HUD_ALTO - 24)
        canal_mensajes = pygame.Rect(
            360, HUD_MENSAJE_Y, HUD_MENSAJE_ANCHO, HUD_MENSAJE_ALTO)
        return cls(
            riel=riel,
            zona_izq=zona_izq,
            zona_centro=zona_centro,
            zona_der=zona_der,
            contenido_izq=contenido_izq,
            contenido_centro=contenido_centro,
            contenido_der=contenido_der,
            canal_mensajes=canal_mensajes,
        )


#---- Modelo de estado del HUD ----#
@dataclass
class HudModel:
    # Jugador
    vidas: int = 0
    vidas_max: int = VIDAS_MAXIMAS
    almas: int = 0
    almas_total: int = 0
    almas_para_vida: int = 0
    dash_cooldown: float = 0.0
    dash_usos_aire: int = 0
    tiene_dash: bool = True
    en_suelo: bool = True
    ataque_cooldown: float = 0.0
    tiene_pala: bool = False
    rango_ataque_mejorado: bool = False
    escudo_farol: bool = False
    filo_anima: bool = False
    almas_volatiles: int = 0
    # Jefe
    jefe_vivo: bool = False
    jefe_vida: int = 0
    jefe_vida_max: int = JEFE_VIDA
    jefe_fase: int = 1
    jefe_nombre: str = "EL CUSTODIO DEL OSARIO"
    # Nivel y tiempo
    nivel_indice: int = 0
    nivel_total: int = 1
    nivel_nombre: str = "CAMPOSANTO"
    tiempo: float = 0.0
    # Estado y mensajes
    estado: str = "jugando"
    pista: str = ""
    aviso_jefe: float = 0.0
    # Instantanea previa para activar el modo inmersivo sin acoplar el gameplay
    vidas_prev: int = field(init=False, default=0)

    def snapshot_prev(self):
        self.vidas_prev = self.vidas

    @property
    def dash_listo(self) -> bool:
        return self.tiene_dash and self.dash_cooldown <= 0 and (self.en_suelo or self.dash_usos_aire > 0)

    @property
    def rango_mejorado(self) -> bool:
        return getattr(self, "rango_ataque_mejorado", False)

    @property
    def nombre_nivel(self) -> str:
        return getattr(self, "nivel_nombre", "CAMPOSANTO")


#---- MensajeHUD ----#
class MensajeHUD:
    OCULTO = "oculto"
    ENTRANDO = "entrando"
    VISIBLE = "visible"
    SALIENDO = "saliendo"

    def __init__(self, layout: HudLayout, tema: HudTheme, texto_cache: TextoCache):
        self.layout = layout
        self.tema = tema
        self.texto_cache = texto_cache
        self.estado = self.OCULTO
        self.tween = Tween(0.2, 0.0, "out_cubic")
        self.hold_timer = 0.0
        self.texto = ""
        self.prioridad = 0
        self.hold = 0.0
        self.t_entrada = 0.2
        self.t_salida = 0.30

    def mostrar(self, texto, prioridad, hold, forzar=False):
        # Solo reemplaza si hay prioridad mayor, si se fuerza, o si está oculto.
        # Un mensaje entrando/visible/saliendo con prioridad >= se respeta salvo que forzar=True.
        if self.esta_visible() and not forzar and prioridad <= self.prioridad:
            return
        self.texto = texto
        self.prioridad = prioridad
        self.hold = hold
        self.estado = self.ENTRANDO
        self.tween.reiniciar(self.t_entrada, "out_cubic")
        self.hold_timer = 0.0

    def actualizar(self, dt):
        if self.estado == self.OCULTO:
            return
        if self.estado == self.ENTRANDO:
            self.tween.update(dt)
            if not self.tween.esta_activo():
                self.estado = self.VISIBLE
                self.hold_timer = 0.0
        elif self.estado == self.VISIBLE:
            self.hold_timer += dt
            if self.hold_timer >= self.hold:
                self.estado = self.SALIENDO
                self.tween.reiniciar(self.t_salida, "in_out_cubic")
        elif self.estado == self.SALIENDO:
            self.tween.update(dt)
            if not self.tween.esta_activo():
                self.estado = self.OCULTO
                self.texto = ""
                self.prioridad = 0

    def esta_visible(self):
        return self.estado in (self.ENTRANDO, self.VISIBLE, self.SALIENDO)

    def alpha(self):
        if self.estado == self.OCULTO:
            return 0
        t = self.tween.valor()
        if self.estado == self.ENTRANDO:
            return int(255 * t)
        if self.estado == self.VISIBLE:
            return 255
        if self.estado == self.SALIENDO:
            return int(255 * (1.0 - t))
        return 0

    def offset_y(self):
        """Slide vertical de 8 px al entrar."""
        if self.estado == self.OCULTO:
            return 0
        t = self.tween.valor()
        if self.estado == self.ENTRANDO:
            # ease-out: empieza rápido, llega a 0
            return int(8 * (1.0 - t))
        if self.estado == self.VISIBLE:
            return 0
        if self.estado == self.SALIENDO:
            return int(8 * t)
        return 0
