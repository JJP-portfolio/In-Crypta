#---- Importamos librerias y configuracion ----#
import math

import pygame

import config
from config import (
    ALTO,
    ANCHO,
    CREMA,
    EQUIPO,
    HUD_BORDE,
    HUD_MUTED,
    HUD_ORO,
    HUD_TEXTO,
    INTEGRANTES,
    ROLES_EQUIPO,
    SUBTITULO,
    TITULO,
    TURQUESA,
    VIDAS_INICIALES,
)
from escena.constantes import (
    OPCIONES_CALIDAD,
    OPCIONES_HUD,
    OPCIONES_SHADER,
    PRESETS_TECLADO,
    TECLAS_ATAQUE,
    TECLAS_SALTO,
)
from niveles import SALAS_PRUEBA


#---- Mixin de menus y navegacion ----#
class MenusMixin:
    """Metodos de menus, transiciones de pantalla y configuracion."""

    def abrir_menu(self):
        self.estado = "menu"
        self.menu_opcion = 0
        self.audio.detener_dron()
        self.audio.reproducir("ui")
        self.audio.reproducir_musica("titulo", bucle=True, fade_ms=600)

    def abrir_seleccion_nivel(self):
        self.estado = "seleccion_nivel"
        self.nivel_seleccionado = self.nivel_indice
        self.audio.detener_dron()
        self.audio.reproducir("ui")

    def abrir_creditos(self):
        self.estado = "creditos"
        self.audio.detener_dron()
        self.audio.reproducir("ui")
        self.audio.reproducir_musica("creditos", bucle=True, fade_ms=600)

    #---- Metodos de configuracion ----#
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

    def alternar_shader(self, delta=1):
        self.config_shader_idx = (self.config_shader_idx + delta) % len(OPCIONES_SHADER)
        self.audio.reproducir("ui")
        shader = OPCIONES_SHADER[self.config_shader_idx]
        self.hud.mostrar_mensaje(f"EFECTOS / SHADER: {shader.upper()}", 1, 3.0)

    #---- Calidad grafica ----#
    # Opciones: Alta (0: 100% particulas), Media (1: 50% particulas), Baja (2: optimizada para bajos recursos)
    def alternar_calidad_grafica(self, delta=1):
        self.config_calidad_idx = (self.config_calidad_idx + delta) % len(OPCIONES_CALIDAD)
        config.CALIDAD_GLOBAL_ACTIVA = self.config_calidad_idx
        if hasattr(self, "hud") and hasattr(self.hud, "renderer"):
            self.hud.renderer._paneles_cache.clear()
        self.audio.reproducir("ui")
        factores = {0: 1.0, 1: 0.5, 2: 0.25}
        self.particulas.factor_calidad = factores.get(self.config_calidad_idx, 1.0)
        tema = self.nivel.tema if self.nivel and hasattr(self.nivel, "tema") else "camposanto"
        self.reiniciar_particulas_bioma(tema)
        calidad = OPCIONES_CALIDAD[self.config_calidad_idx]
        self.hud.mostrar_mensaje(f"CALIDAD GRÁFICA: {calidad.upper()}", 1, 3.0)

    #---- Modo de HUD e interfaz ----#
    # Opciones: Completo (0: riel 100%), Compacto (1: reducido), Inmersivo (2: minimo).
    def alternar_modo_hud(self, delta=1):
        self.config_hud_idx = (self.config_hud_idx + delta) % len(OPCIONES_HUD)
        self.audio.reproducir("ui")
        self.hud.modo_hud = self.config_hud_idx
        modo = OPCIONES_HUD[self.config_hud_idx]
        self.hud.mostrar_mensaje(f"MODO DE HUD: {modo.upper()}", 1, 3.0)

    def alternar_accesibilidad(self):
        """Alterna el modo de reducción de movimiento."""
        self.reducir_movimiento = not self.reducir_movimiento
        self.camara.permitir_sacudida = not self.reducir_movimiento
        self.hud.reducir_movimiento = self.reducir_movimiento
        estado_str = "ACTIVADA" if self.reducir_movimiento else "DESACTIVADA"
        self.hud.mostrar_mensaje(f"ACCESIBILIDAD: REDUCIR MOVIMIENTO {estado_str}", 3, 2.5)
        self.audio.reproducir("ui")

    def alternar_escala_fuente(self, delta=1):
        """Alterna la escala tipográfica in-game (+15%, +20%, +25%) mediante F2."""
        opciones = getattr(config, "OPCIONES_ESCALA_FUENTE", ((1.15, "+15%"), (1.20, "+20%"), (1.25, "+25%")))
        self.escala_fuente_idx = (self.escala_fuente_idx + delta) % len(opciones)
        escala, etiqueta = opciones[self.escala_fuente_idx]
        config.ESCALA_FUENTES_ACTIVA = escala
        self._escala_fuente_cache = escala
        self.fuentes.clear()
        self._cache_texto.clear()
        if hasattr(self, "hud") and hasattr(self.hud, "limpiar_caches_texto"):
            self.hud.limpiar_caches_texto()
        self.hud.mostrar_mensaje(f"TAMAÑO DE TEXTO (F2): {etiqueta}", 1, 2.5)
        self.audio.reproducir("ui")

    def alternar_pantalla_completa(self):
        """Alterna entre ventana escalada y pantalla completa (Alt+Enter / F11)."""
        self._pantalla_completa = not getattr(self, "_pantalla_completa", False)
        base_flags = getattr(self, "_display_flags", 0)
        if self._pantalla_completa:
            flags = (base_flags & ~pygame.RESIZABLE) | pygame.FULLSCREEN
        else:
            flags = base_flags
        try:
            self.pantalla = pygame.display.set_mode((ANCHO, ALTO), flags)
        except pygame.error:
            self._pantalla_completa = False
            self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO)
        self.audio.reproducir("ui")
        modo = "PANTALLA COMPLETA" if self._pantalla_completa else "VENTANA"
        self.hud.mostrar_mensaje(f"MODO DE VIDEO: {modo}", 1, 2.5)

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

    def abrir_selector_pruebas(self):
        self.estado = "test_selector"
        self.test_opcion = 0
        self.audio.detener_dron()
        self.audio.reproducir("ui")

    def _cerrar_configuracion(self):
        """Regresa al menú de origen tras cerrar la pantalla de configuración."""
        if self.origen_configuracion == "pausa":
            self.estado = "pausa"
        else:
            self.abrir_menu()
        self.audio.reproducir("ui")

    def _aplicar_ajuste_config(self, delta):
        """Aplica incremento o decremento sobre la opción activa en configuración."""
        acciones = {
            0: lambda: self.alternar_preset_teclado(delta),
            1: lambda: self.alternar_shader(delta),
            2: lambda: self.alternar_calidad_grafica(delta),
            3: lambda: self.alternar_modo_hud(delta),
            4: self.alternar_pantalla_completa,
            5: self.alternar_accesibilidad,
            6: self.audio.alternar,
        }
        accion = acciones.get(self.config_opcion)
        if accion is not None:
            accion()

    def _manejar_tecla_menu(self, key):
        total_menu = 4
        if key in (pygame.K_UP, pygame.K_w):
            self.menu_opcion = (self.menu_opcion - 1) % total_menu
            self.audio.reproducir("ui")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.menu_opcion = (self.menu_opcion + 1) % total_menu
            self.audio.reproducir("ui")
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.audio.reproducir("ui")
            if self.menu_opcion == 0:
                self.iniciar_campaña()
            elif self.menu_opcion == 1:
                self.abrir_seleccion_nivel()
            elif self.menu_opcion == 2:
                self.abrir_configuracion("menu")
            else:
                self.abrir_creditos()
        elif key == pygame.K_ESCAPE:
            self.estado = "titulo"
            self.audio.reproducir("ui")

    def _manejar_tecla_configuracion(self, key):
        opciones = self._opciones_configuracion_visibles(PRESETS_TECLADO[self.preset_teclado_idx])
        total_config = len(opciones)
        if key in (pygame.K_UP, pygame.K_w):
            self.config_opcion = (self.config_opcion - 1) % total_config
            self.audio.reproducir("ui")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.config_opcion = (self.config_opcion + 1) % total_config
            self.audio.reproducir("ui")
        elif key in (pygame.K_LEFT, pygame.K_a):
            self._aplicar_ajuste_config(-1)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self._aplicar_ajuste_config(1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.config_opcion == total_config - 1:
                self._cerrar_configuracion()
            else:
                self._aplicar_ajuste_config(1)
        elif key == pygame.K_ESCAPE:
            self._cerrar_configuracion()

    def _manejar_tecla_pausa(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            self.pausa_opcion = (self.pausa_opcion - 1) % 5
            self.audio.reproducir("ui")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.pausa_opcion = (self.pausa_opcion + 1) % 5
            self.audio.reproducir("ui")
        elif key in (pygame.K_c, pygame.K_o):
            self.abrir_configuracion("pausa")
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.audio.reproducir("ui")
            if self.pausa_opcion == 0:
                self.estado = "jugando"
            elif self.pausa_opcion == 1:
                self.abrir_configuracion("pausa")
            elif self.pausa_opcion == 2:
                if self.punto_reintento:
                    self.reintentar_nivel()
                else:
                    self._reiniciar_nivel_actual()
                self.estado = "jugando"
            elif self.pausa_opcion == 3:
                self._reiniciar_nivel_actual()
                self.estado = "jugando"
            elif self.pausa_opcion == 4:
                self.abrir_menu()
        elif key in (pygame.K_ESCAPE, pygame.K_p):
            self.audio.reproducir("ui")
            self.estado = "jugando"

    def _manejar_tecla_seleccion_nivel(self, key):
        total_sn = 5
        if key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
            self.nivel_seleccionado = (self.nivel_seleccionado - 1) % total_sn
            self.audio.reproducir("ui")
        elif key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d):
            self.nivel_seleccionado = (self.nivel_seleccionado + 1) % total_sn
            self.audio.reproducir("ui")
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.audio.reproducir("ui")
            self.ejecutar_seleccion_nivel(self.nivel_seleccionado)
        elif key == pygame.K_ESCAPE:
            self.abrir_menu()

    def _manejar_tecla_test_selector(self, key):
        if key == pygame.K_ESCAPE:
            self.abrir_seleccion_nivel()
        elif key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
            self.test_opcion = (self.test_opcion - 1) % len(SALAS_PRUEBA)
            self.audio.reproducir("ui")
        elif key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d):
            self.test_opcion = (self.test_opcion + 1) % len(SALAS_PRUEBA)
            self.audio.reproducir("ui")
        elif pygame.K_1 <= key <= pygame.K_6:
            idx = key - pygame.K_1
            if idx < len(SALAS_PRUEBA):
                self.cargar_sala_prueba(idx)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.cargar_sala_prueba(self.test_opcion)

    def _manejar_tecla_derrota(self, key):
        tiene_continues = (
            not self.sala_prueba
            and not self.es_tutorial
            and getattr(self, "continues", 0) > 0
        )
        teclas_nav = (
            pygame.K_UP,
            pygame.K_w,
            pygame.K_DOWN,
            pygame.K_s,
            pygame.K_LEFT,
            pygame.K_a,
            pygame.K_RIGHT,
            pygame.K_d,
        )
        if tiene_continues and key in teclas_nav:
            self.derrota_opcion = 1 - getattr(self, "derrota_opcion", 0)
            self.audio.reproducir("ui")
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._manejar_tecla_enter_estado()
        elif key == pygame.K_ESCAPE:
            self.abrir_menu()

    def _manejar_tecla_enter_estado(self):
        if self.estado == "titulo":
            self.audio.reproducir("ui")
            self.abrir_menu()
        elif self.estado == "nivel_completado":
            self.siguiente_nivel()
        elif self.estado in ("sala_completada", "tutorial_completado", "victoria"):
            self.abrir_menu()
        elif self.estado == "derrota":
            if self.sala_prueba or self.es_tutorial:
                self._reiniciar_nivel_actual()
            elif getattr(self, "continues", 0) > 0 and getattr(self, "derrota_opcion", 0) == 0:
                # Usa 1 Continue y reinicia desde 0 el nivel donde perdió todas las vidas
                self.continues -= 1
                self.cargar_nivel(self.nivel_indice, vidas=VIDAS_INICIALES)
                self.estado = "jugando"
            else:
                # Sin continues (o eligiendo empezar de nuevo): arranca desde el Nivel 1 (El Camposanto), NO el tutorial
                self.reiniciar_juego()
                self.estado = "jugando"

    def _alternar_pausa_tecla(self):
        if self.estado == "jugando":
            self.audio.reproducir("ui")
            self.pausa_opcion = 0
            self.estado = "pausa"
        elif self.estado == "pausa":
            self.audio.reproducir("ui")
            self.estado = "jugando"

    def _alternar_modo_visual_f4(self):
        self.estilo_visual_idx = (self.estilo_visual_idx + 1) % len(self.estilos_visuales)
        modo_estilo = self.estilos_visuales[self.estilo_visual_idx]
        config.ESTILO_HUD = modo_estilo
        config.ESTILO_MUNDO = modo_estilo
        config.ESTILO_ENEMIGOS = modo_estilo
        config.ESTILO_EFECTOS = modo_estilo
        if hasattr(self, "hud") and hasattr(self.hud, "renderer"):
            self.hud.renderer._paneles_cache.clear()
        self.hud.mostrar_mensaje(f"MODELO VISUAL (F4): {modo_estilo}", 1, 3.0)
        self.audio.reproducir("ui")

    def _reiniciar_partida_tecla(self):
        if self.sala_prueba:
            self.cargar_sala_prueba(self.sala_prueba_indice)
        elif self.es_tutorial:
            self.iniciar_tutorial()
        else:
            self.reiniciar_juego()

    def _manejar_tecla_escape(self):
        if self.estado == "jugando":
            self.audio.reproducir("ui")
            self.pausa_opcion = 0
            self.estado = "pausa"
        elif self.estado == "titulo":
            self.corriendo = False
        else:
            self.abrir_menu()

    def _manejar_tecla_global(self, key):
        if key == pygame.K_ESCAPE:
            self._manejar_tecla_escape()
        elif key == pygame.K_m:
            self.audio.alternar()
        elif key == pygame.K_F1:
            self.alternar_accesibilidad()
        elif key == pygame.K_F2:
            self.alternar_escala_fuente()
        elif key == pygame.K_F3:
            self.debug_colisiones = not self.debug_colisiones
            estado_f3 = "ACTIVADO" if self.debug_colisiones else "DESACTIVADO"
            self.hud.mostrar_mensaje(f"DEBUG HITBOX/HURTBOX (F3): {estado_f3}", 1, 3.0)
            self.audio.reproducir("ui")
        elif key == pygame.K_F4:
            self._alternar_modo_visual_f4()
        elif key == pygame.K_r and self.estado not in (
            "titulo", "menu", "seleccion_nivel", "creditos"
        ):
            self._reiniciar_partida_tecla()
        elif key == pygame.K_p:
            self._alternar_pausa_tecla()
        elif self.estado == "jugando":
            self._manejar_tecla_acciones_jugando(key)
        elif key == pygame.K_RETURN:
            self._manejar_tecla_enter_estado()

    def _manejar_tecla_acciones_jugando(self, key):
        teclas_dash = getattr(
            self, "teclas_dash", (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_x)
        )
        if key in getattr(self, "teclas_salto", TECLAS_SALTO):
            self.jugador.pedir_salto()
        elif key in teclas_dash:
            self.jugador.pedir_dash()
        elif key in getattr(self, "teclas_ataque", TECLAS_ATAQUE):
            self.intentar_ataque()

    def dibujar_titulo(self):
        self.dibujar_fondo(self.pantalla)
        self.dibujar_arbol_muerto(self.pantalla, 140, ALTO - 54, 1.45)
        self.dibujar_arbol_muerto(self.pantalla, 1120, ALTO - 44, 1.15)
        self.dibujar_tumba_lejana(self.pantalla, 960, ALTO - 50, 1.25)
        if getattr(self, "config_calidad_idx", 0) != 2:
            self.pantalla.blit(self.vineta, (0, 0))

        pw, ph = 620, 320
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph, color_fondo=(10, 8, 16, 220))

        self.dibujar_texto(TITULO, 0, py + 58, 74, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto(SUBTITULO.upper(), 0, py + 132, 16, CREMA, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 140), (ANCHO // 2 - 120, py + 166), (ANCHO // 2 + 120, py + 166), 1)

        pulso = 0.5 + 0.5 * math.sin(self.tiempo_titulo * 4.0)
        col_prompt = (
            int(TURQUESA[0] * (0.65 + 0.35 * pulso)),
            int(TURQUESA[1] * (0.65 + 0.35 * pulso)),
            int(TURQUESA[2] * (0.65 + 0.35 * pulso)),
        )
        self.dibujar_texto("PRESIONA [ENTER] PARA ENTRAR", 0, py + 225, 20, col_prompt, centrado=True, sombra=True)
        self.dibujar_texto("[ESC] Salir", 0, py + ph - 28, 13, HUD_MUTED, centrado=True)

    def _dibujar_fondo_panel_menu(self, pw, ph, alfa=235):
        """Dibuja fondo ambiental, viñeta y marco heráldico centrado; retorna (px, py)."""
        self.dibujar_fondo(self.pantalla)
        if getattr(self, "config_calidad_idx", 0) != 2:
            self.pantalla.blit(self.vineta, (0, 0))
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph, color_fondo=(12, 10, 18, alfa))
        return px, py

    def _dibujar_tarjeta_opcion(self, rect_op, seleccionada, color_activo=(32, 22, 42)):
        """Dibuja una tarjeta de opción de menú con borde dorado y barra lateral si está activa."""
        color_fondo = color_activo if seleccionada else (16, 13, 22)
        color_borde = HUD_ORO if seleccionada else HUD_BORDE
        pygame.draw.rect(self.pantalla, color_fondo, rect_op, border_radius=6)
        pygame.draw.rect(self.pantalla, color_borde, rect_op, 2 if seleccionada else 1, border_radius=6)
        if seleccionada:
            borde_lat = (rect_op.x, rect_op.y + 8, 4, rect_op.height - 16)
            pygame.draw.rect(self.pantalla, HUD_ORO, borde_lat, border_radius=2)

    def dibujar_menu_principal(self):
        pw, ph = 520, 430
        px, py = self._dibujar_fondo_panel_menu(pw, ph, alfa=232)

        self.dibujar_texto(TITULO, 0, py + 36, 54, HUD_ORO, centrado=True, sombra=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 130), (ANCHO // 2 - 110, py + 92), (ANCHO // 2 + 110, py + 92), 1)

        opciones = (
            "INICIAR CAMPAÑA",
            "SELECCIÓN DE CAPÍTULO",
            "CONFIGURACIÓN",
            "CRÉDITOS",
        )
        ancho_caja, alto_caja = 380, 50
        x_caja = (ANCHO - ancho_caja) // 2
        y_base = py + 118

        for i, titulo_op in enumerate(opciones):
            y_caja = y_base + i * 64
            seleccionada = (i == self.menu_opcion)
            self._dibujar_tarjeta_opcion(pygame.Rect(x_caja, y_caja, ancho_caja, alto_caja), seleccionada, (34, 24, 46))
            color_txt = HUD_ORO if seleccionada else HUD_TEXTO
            self.dibujar_texto(titulo_op, 0, y_caja + 25, 19, color_txt, centrado=True, sombra=seleccionada)

        self.dibujar_texto(
            "[W/S o Flechas] Navegar | [ENTER] Seleccionar | [ESC] Salir",
            0, py + ph - 26, 13, HUD_MUTED, centrado=True,
        )

    def dibujar_seleccion_nivel(self):
        pw, ph = 640, 490
        px, py = self._dibujar_fondo_panel_menu(pw, ph, alfa=235)

        self.dibujar_texto("SELECCIÓN DE CAPÍTULO", 0, py + 32, 30, HUD_ORO, centrado=True, sombra=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 130), (ANCHO // 2 - 140, py + 66), (ANCHO // 2 + 140, py + 66), 1)

        datos_niveles = (
            ("0", "PRELUDIO - EL UMBRAL", "El ritual de iniciación del sepulturero"),
            ("I", "ACTO I - EL CAMPOSANTO", "Tumbas abiertas bajo la niebla lunar"),
            ("II", "ACTO II - LA CRIPTA", "Sillería húmeda y moradores en penumbra"),
            ("III", "ACTO III - EL OSARIO", "La cámara del Custodio y la Muerte Roja"),
            ("V", "SALAS DE PRUEBA", "Desafíos de precisión y combate"),
        )
        ancho_t, alto_t = 540, 62
        x_t = (ANCHO - ancho_t) // 2
        y_base = py + 86

        for i, (insignia, titulo_n, sub_n) in enumerate(datos_niveles):
            y_t = y_base + i * 72
            sel = (i == self.nivel_seleccionado)
            self._dibujar_tarjeta_opcion(pygame.Rect(x_t, y_t, ancho_t, alto_t), sel, (32, 22, 42))
            self.dibujar_texto(insignia, x_t + 22, y_t + 14, 26, HUD_ORO if sel else HUD_MUTED, sombra=sel)
            self.dibujar_texto(titulo_n, x_t + 68, y_t + 11, 17, HUD_ORO if sel else HUD_TEXTO, sombra=sel)
            self.dibujar_texto(sub_n, x_t + 68, y_t + 35, 13, CREMA if sel else HUD_MUTED)

        self.dibujar_texto(
            "[W/S o Flechas] Elegir | [ENTER] Jugar | [ESC] Volver",
            0, py + ph - 26, 13, HUD_MUTED, centrado=True,
        )

    def dibujar_selector_pruebas(self):
        pw, ph = 700, 520
        px, py = self._dibujar_fondo_panel_menu(pw, ph, alfa=235)

        self.dibujar_texto("SALAS DE PRUEBA", 0, py + 26, 30, HUD_ORO, centrado=True, sombra=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 130), (ANCHO // 2 - 140, py + 60), (ANCHO // 2 + 140, py + 60), 1)

        ancho_tarjeta, alto_tarjeta = 600, 58
        x_tarjeta = (ANCHO - ancho_tarjeta) // 2
        y_base = py + 78

        for i, sala in enumerate(SALAS_PRUEBA):
            y_tarjeta = y_base + i * 64
            sel = (i == self.test_opcion)
            rect_t = pygame.Rect(x_tarjeta, y_tarjeta, ancho_tarjeta, alto_tarjeta)
            self._dibujar_tarjeta_opcion(rect_t, sel, (32, 22, 40))
            self.dibujar_texto(
                str(i + 1), x_tarjeta + 20, y_tarjeta + 14, 24, HUD_ORO if sel else HUD_MUTED, sombra=sel
            )
            nombre_sala = sala.get("nombre", f"Sala de Prueba {i + 1}")
            desc_sala = sala.get("desc", "Verificación de mecánicas")
            self.dibujar_texto(
                nombre_sala, x_tarjeta + 60, y_tarjeta + 10, 16, HUD_ORO if sel else HUD_TEXTO, sombra=sel
            )
            self.dibujar_texto(
                desc_sala, x_tarjeta + 60, y_tarjeta + 32, 12, CREMA if sel else HUD_MUTED
            )

        self.dibujar_texto(
            "[W/S o Flechas] Elegir | [1-6 o ENTER] Probar | [ESC] Volver",
            0, py + ph - 24, 12, HUD_MUTED, centrado=True,
        )

    def dibujar_creditos(self):
        pw, ph = 640, 440
        px, py = self._dibujar_fondo_panel_menu(pw, ph, alfa=238)

        self.dibujar_texto(TITULO, 0, py + 32, 44, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto(f"{EQUIPO.upper()} · DESARROLLO Y DISEÑO", 0, py + 80, 14, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 130), (ANCHO // 2 - 140, py + 104), (ANCHO // 2 + 140, py + 104), 1)

        for idx, nombre in enumerate(INTEGRANTES):
            y_fila = py + 132 + idx * 66
            rol = ROLES_EQUIPO.get(nombre, "")
            self.dibujar_texto(nombre, 0, y_fila, 18, HUD_TEXTO, centrado=True, sombra=True)
            if rol:
                self.dibujar_texto(rol, 0, y_fila + 23, 13, CREMA, centrado=True)

        self.dibujar_texto("Inspirado en la obra de Edgar Allan Poe", 0, py + ph - 66, 14, HUD_ORO, centrado=True)
        self.dibujar_texto("[ENTER o ESC] Volver al Menú", 0, py + ph - 30, 14, TURQUESA, centrado=True)

    def _opciones_configuracion_visibles(self, preset_activo):
        modo_video = "Completa" if getattr(self, "_pantalla_completa", False) else "Ventana"
        return (
            ("CONTROLES", preset_activo["etiqueta"]),
            ("POST-PROCESADO", OPCIONES_SHADER[self.config_shader_idx]),
            ("CALIDAD GRÁFICA", OPCIONES_CALIDAD[self.config_calidad_idx]),
            ("INTERFAZ (HUD)", OPCIONES_HUD[self.config_hud_idx]),
            ("PANTALLA COMPLETA", modo_video),
            ("REDUCIR MOVIMIENTO", "Sí" if self.reducir_movimiento else "No"),
            ("SONIDO Y MÚSICA", "Activo" if getattr(self.audio, "activo", False) else "Silenciado"),
            ("VOLVER", ""),
        )

    def _dibujar_fila_configuracion(self, indice, etiqueta, valor, y_base):
        ancho_c, alto_c = 580, 40
        x_c = (ANCHO - ancho_c) // 2
        y_c = y_base + indice * 46
        sel = indice == self.config_opcion
        rect_c = pygame.Rect(x_c, y_c, ancho_c, alto_c)
        fondo = (32, 24, 44) if sel else (16, 13, 22)
        borde = HUD_ORO if sel else HUD_BORDE
        pygame.draw.rect(self.pantalla, fondo, rect_c, border_radius=6)
        pygame.draw.rect(self.pantalla, borde, rect_c, 2 if sel else 1, border_radius=6)

        prefijo = "> " if sel else "  "
        self.dibujar_texto(
            prefijo + etiqueta,
            x_c + 16,
            y_c + 9,
            16,
            HUD_ORO if sel else HUD_TEXTO,
            sombra=sel,
        )
        if valor:
            val_fmt = f"< {valor} >" if sel else valor
            self.dibujar_texto(
                val_fmt,
                x_c + ancho_c - 18,
                y_c + 9,
                15,
                TURQUESA if sel else CREMA,
                derecha=True,
                sombra=sel,
            )

    def dibujar_configuracion(self):
        pw, ph = 680, 540
        _, py = self._dibujar_fondo_panel_menu(pw, ph, alfa=238)
        self.dibujar_texto("CONFIGURACIÓN", 0, py + 28, 32, HUD_ORO, centrado=True, sombra=True)
        pygame.draw.line(
            self.pantalla,
            (*HUD_ORO, 120),
            (ANCHO // 2 - 140, py + 62),
            (ANCHO // 2 + 140, py + 62),
            1,
        )

        preset_activo = PRESETS_TECLADO[self.preset_teclado_idx]
        opciones = self._opciones_configuracion_visibles(preset_activo)
        for i, (etiqueta, valor) in enumerate(opciones):
            self._dibujar_fila_configuracion(i, etiqueta, valor, py + 78)

        opciones_escala = getattr(config, "OPCIONES_ESCALA_FUENTE", ((1.15, "+15%"),))
        _, etiq_fuente = opciones_escala[self.escala_fuente_idx % len(opciones_escala)]
        self.dibujar_texto(preset_activo["resumen"], 0, py + ph - 54, 13, CREMA, centrado=True)
        self.dibujar_texto(
            f"[W/S] Elegir | [A/D] Cambiar | [Alt+Enter] Pant. Completa | "
            f"[F2] Texto ({etiq_fuente}) | [ESC] Volver",
            0,
            py + ph - 24,
            12,
            HUD_MUTED,
            centrado=True,
        )
