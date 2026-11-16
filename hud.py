#---- Importamos librerias y configuracion ----#
from config import DASH_USOS_AIRE, JEFE_VIDA, MINIJEFE_VIDA, VIDAS_MAXIMAS
from ui.animacion import (
    TextoCache,
    Tween,
    _ease_in_out_cubic,
    _ease_out_back,
    _ease_out_cubic,
    _partir_palabra,
    envolver,
    fmt_tiempo,
)
from ui.modelos import (
    FUENTE_CONTADOR,
    FUENTE_LABEL,
    FUENTE_NOMBRE,
    HUD_ALTO,
    HUD_GAP,
    HUD_MARGEN_X,
    HUD_MARGEN_Y,
    HUD_MENSAJE_ALTO,
    HUD_MENSAJE_ANCHO,
    HUD_MENSAJE_Y,
    HUD_PADDING,
    HUD_ZONA_CENTRO,
    HUD_ZONA_DER,
    HUD_ZONA_IZQ,
    HudLayout,
    HudModel,
    HudTheme,
    MensajeHUD,
    _RAIZ_HUD,
    _RUTA_FUENTE,
)
from ui.renderer import HudRenderer

try:
    from niveles import NIVELES
except ImportError:
    NIVELES = []


#---- Orquestador del HUD ----#
class HudOrquestador:
    def __init__(self):
        self.layout = HudLayout.construir()
        self.tema = HudTheme()
        self.texto_cache = TextoCache(lambda t: self.renderer._fuente(t))
        self.renderer = HudRenderer(self.layout, self.tema, self.texto_cache)
        self.mensajes = MensajeHUD(self.layout, self.tema, self.texto_cache)
        self.modelo = HudModel()
        self.reducir_movimiento = False
        self.modo_hud = 0
        self.timer_inmersivo = 0.0

    def limpiar_caches_texto(self):
        """Limpia las cachés tipográficas del HUD al alternar escala."""
        self.renderer.limpiar_caches_texto()

    def actualizar(self, dt):
        self.mensajes.actualizar(dt)
        if self.timer_inmersivo > 0:
            self.timer_inmersivo = max(0.0, self.timer_inmersivo - dt)

    def armar_modelo(self, juego):
        """Sincroniza el estado del HUD a partir de la instancia activa de Juego."""
        jugador = juego.jugador
        nivel = juego.nivel

        self.modo_hud = getattr(juego, "config_hud_idx", 0)
        self._sincronizar_jugador(jugador, nivel, juego)
        self._sincronizar_jefe(juego, jugador, nivel)
        self._sincronizar_nivel(juego, nivel)
        self.modelo.snapshot_prev()

    def _sincronizar_jugador(self, jugador, nivel, juego):
        """Actualiza recursos y capacidades del jugador y despierta el modo inmersivo."""
        nueva_vida = jugador.vidas if jugador else VIDAS_MAXIMAS
        nuevas_almas = jugador.almas if jugador else 0
        nuevo_dash = getattr(jugador, "tiene_dash", False) if jugador else False
        nueva_pala = jugador.tiene_pala if jugador else False
        nuevo_manto = getattr(jugador, "escudo_farol", False) if jugador else False

        if self.modelo.vidas_prev > 0 and (
            nueva_vida < self.modelo.vidas
            or nuevas_almas > self.modelo.almas
            or (nuevo_dash and not self.modelo.tiene_dash)
            or (nueva_pala and not self.modelo.tiene_pala)
            or (nuevo_manto and not self.modelo.escudo_farol)
        ):
            self.timer_inmersivo = 3.0

        self.modelo.vidas = nueva_vida
        self.modelo.vidas_max = VIDAS_MAXIMAS
        self.modelo.almas = nuevas_almas
        self.modelo.almas_total = nivel.total_almas if nivel else 0
        self.modelo.almas_volatiles = max(0, nuevas_almas - getattr(juego, "almas_consagradas", 0))
        self.modelo.almas_para_vida = jugador.almas_para_vida if jugador else 0
        self.modelo.dash_cooldown = jugador.dash_cooldown if jugador else 0.0
        self.modelo.dash_usos_aire = jugador.dash_usos_aire if jugador else DASH_USOS_AIRE
        self.modelo.tiene_dash = nuevo_dash
        self.modelo.en_suelo = jugador.en_suelo if jugador else True
        self.modelo.ataque_cooldown = jugador.ataque_cooldown if jugador else 0.0
        self.modelo.tiene_pala = nueva_pala
        self.modelo.rango_ataque_mejorado = getattr(jugador, "rango_ataque_mejorado", False) if jugador else False
        self.modelo.escudo_farol = nuevo_manto
        self.modelo.filo_anima = getattr(jugador, "filo_anima", False) if jugador else False

    def _entidad_jefe_visible(self, entidad, jugador, juego, margen_x, margen_y, vida_max, dist_herido):
        if not (hasattr(entidad, "rect") and jugador is not None and hasattr(jugador, "rect")):
            return True
        dist_x = abs(jugador.rect.centerx - entidad.rect.centerx)
        dist_y = abs(jugador.rect.centery - entidad.rect.centery)
        camara = getattr(juego, "camara", None)
        en_camara = camara is not None and camara.is_on_screen(entidad.rect)
        return (dist_y <= margen_y) and (
            en_camara
            or dist_x <= margen_x
            or (getattr(entidad, "vida", vida_max) < vida_max and dist_x <= dist_herido)
        )

    def _buscar_minijefe_activo(self, jugador, nivel):
        if not (nivel and hasattr(nivel, "minijefes")):
            return None
        for mj in nivel.minijefes:
            if mj.vivo and mj.estado != "muerto" and self._entidad_jefe_visible(
                mj, jugador, getattr(self, "_juego_ref", None), 380, 150, MINIJEFE_VIDA, 540
            ):
                return mj
        return None

    def _sincronizar_jefe(self, juego, jugador, nivel):
        """Selecciona la barra activa entre el jefe principal y los carceleros cercanos."""
        jefe = juego.jefe
        jefe_cerca = bool(
            jefe is not None
            and getattr(jefe, "vivo", False)
            and self._entidad_jefe_visible(jefe, jugador, juego, 420, 220, JEFE_VIDA, 680)
        )
        if jefe_cerca:
            self.modelo.jefe_vivo = True
            if jefe.fase >= 3 and nivel and getattr(nivel, "bloques_cripta", None):
                total_cr = len(nivel.bloques_cripta)
                sanos_cr = sum(1 for b in nivel.bloques_cripta if not getattr(b, "roto", False))
                self.modelo.jefe_vida = sanos_cr
                self.modelo.jefe_vida_max = max(1, total_cr)
            else:
                self.modelo.jefe_vida = jefe.vida
                self.modelo.jefe_vida_max = JEFE_VIDA
            self.modelo.jefe_fase = jefe.fase
            self.modelo.jefe_nombre = "EL CUSTODIO DEL OSARIO"
            return

        self._juego_ref = juego
        mj = self._buscar_minijefe_activo(jugador, nivel)
        if mj is not None:
            self.modelo.jefe_vivo = True
            self.modelo.jefe_vida = mj.vida
            self.modelo.jefe_vida_max = MINIJEFE_VIDA
            self.modelo.jefe_fase = 1
            self.modelo.jefe_nombre = "EL CARCELERO DEL OSARIO"
            return
        self.modelo.jefe_vivo = False
        self.modelo.jefe_vida = 0
        self.modelo.jefe_vida_max = JEFE_VIDA
        self.modelo.jefe_fase = 1
        self.modelo.jefe_nombre = "EL CUSTODIO DEL OSARIO"

    def _sincronizar_nivel(self, juego, nivel):
        if getattr(juego, "es_tutorial", False):
            self.modelo.nivel_indice = -1
            self.modelo.nivel_total = 3
            self.modelo.nivel_nombre = "RITUAL DEL SEPULTURERO"
        else:
            self.modelo.nivel_indice = juego.nivel_indice
            total = len(getattr(juego, "niveles", [])) or (len(NIVELES) if "NIVELES" in globals() and NIVELES else 3)
            self.modelo.nivel_total = total
            self.modelo.nivel_nombre = nivel.nombre.upper() if nivel and hasattr(nivel, "nombre") else "CAMPOSANTO"
        self.modelo.tiempo = juego.tiempo_total
        self.modelo.estado = juego.estado
        self.modelo.pista = getattr(juego, "texto_ayuda", "") or (nivel.pista if nivel and hasattr(nivel, "pista") else "")
        self.modelo.aviso_jefe = juego.aviso_jefe

    def dibujar(self, pantalla, juego, dt):
        self.armar_modelo(juego)
        self.renderer.dibujar(pantalla, self.modelo, self.mensajes,
                              self.reducir_movimiento, dt,
                              modo_hud=self.modo_hud,
                              timer_inmersivo=self.timer_inmersivo)

    def mostrar_mensaje(self, texto, prioridad, hold, forzar=False):
        self.mensajes.mostrar(texto, prioridad, hold, forzar=forzar)
