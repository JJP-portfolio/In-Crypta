#---- Importamos librerias y configuracion ----#
import math
import textwrap

import pygame

import config
from config import (
    ALTO,
    ANCHO,
    BLANCO,
    CAMARA_ZOOM,
    CITAS_POE,
    CREMA,
    HUD_BORDE,
    HUD_MUTED,
    HUD_ORO,
    HUD_ROJO,
    HUD_TEXTO,
    HUD_VERDE,
    HUESO,
    ORO,
    SOMBRA,
    TILE,
    TURQUESA_ÁNIMA,
    VIDAS_MAXIMAS,
)


#---- Mixin de pantallas finales, pausa y texto ----#
class PantallasMixin:
    """Metodos de overlays, relicario, pausa, victoria, derrota y fuente."""

    def _dibujar_overlays_estado(self, pw, ph):
        """Renderiza destellos de impacto y pantallas superpuestas según estado."""
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
            self.dibujar_overlay("DESAFÍO COMPLETADO", "ENTER para continuar · ESC volver al menú")
        elif self.estado == "tutorial_completado":
            self.dibujar_overlay("¡RITUAL COMPLETADO!", "El sepulturero ha aprendido su oficio · ENTER para volver al menú")
        elif self.estado == "derrota":
            self.dibujar_derrota()
        elif self.estado == "victoria":
            self.dibujar_victoria()

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
        pygame.draw.line(self.pantalla, (140, 112, 48), (px + 30, py + 92), (px + pw - 30, py + 92), 1)

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
            pygame.draw.line(self.pantalla, HUD_BORDE, (px + 30, y_stat + 28), (px + pw - 30, y_stat + 28), 1)
            y_stat += 54

        # Caja de Rango de Nivel
        y_rango = y_stat + 10
        pygame.draw.rect(self.pantalla, (20, 16, 26), (px + 40, y_rango, pw - 80, 42), border_radius=8)
        pygame.draw.rect(self.pantalla, col_r, (px + 40, y_rango, pw - 80, 42), 1, border_radius=8)
        self.dibujar_texto(f"RANGO DEL NIVEL: {rango_nivel}", 0, y_rango + 10, 16, col_r, centrado=True, sombra=True)

        # Prompt claro
        pygame.draw.line(self.pantalla, (140, 112, 48), (px + 30, py + ph - 48), (px + pw - 30, py + ph - 48), 1)
        self.dibujar_texto("[ENTER] Descender al siguiente nivel · [ESC] Menú Principal",
                           0, py + ph - 30, 13, HUD_ORO, centrado=True, sombra=True)

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

    def dibujar_menu_pausa(self):
        """Menú de Pausa litúrgico e interactivo navegable con opciones claras y directas."""
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((8, 6, 12, 195))
        self.pantalla.blit(overlay, (0, 0))

        ancho_panel = 480
        alto_panel = 392
        px = (ANCHO - ancho_panel) // 2
        py = (ALTO - alto_panel) // 2
        self.dibujar_marco_heraldico(self.pantalla, px, py, ancho_panel, alto_panel, color_fondo=(12, 10, 18, 238))

        self.dibujar_texto("PAUSA", 0, py + 24, 28, HUD_ORO, centrado=True, sombra=True)
        pygame.draw.line(self.pantalla, (140, 112, 48), (ANCHO // 2 - 90, py + 58), (ANCHO // 2 + 90, py + 58), 1)

        opciones_pausa = (
            "CONTINUAR",
            "OPCIONES",
            "REINICIAR DESDE FAROL",
            "REINICIAR NIVEL",
            "VOLVER AL MENÚ",
        )

        ancho_caja = 360
        alto_caja = 44
        x_caja = (ANCHO - ancho_caja) // 2
        y_base = py + 78

        for i, nombre_op in enumerate(opciones_pausa):
            y_caja = y_base + i * 52
            activa = (i == self.pausa_opcion)
            rect_op = pygame.Rect(x_caja, y_caja, ancho_caja, alto_caja)
            color_bg = (32, 24, 42) if activa else (18, 14, 22)
            pygame.draw.rect(self.pantalla, color_bg, rect_op, border_radius=6)
            color_border = HUD_ORO if activa else HUD_BORDE
            pygame.draw.rect(self.pantalla, color_border, rect_op, 2 if activa else 1, border_radius=6)
            if activa:
                pygame.draw.rect(self.pantalla, HUD_ORO, (x_caja, y_caja + 6, 4, alto_caja - 12), border_radius=2)

            color_txt = HUD_ORO if activa else HUD_TEXTO
            self.dibujar_texto(nombre_op, 0, y_caja + 22, 16, color_txt, centrado=True, sombra=activa)

        self.dibujar_texto("[W/S o Flechas] Elegir | [ENTER] Confirmar | [ESC o P] Continuar", 0, py + alto_panel - 22, 12, HUD_MUTED, centrado=True)

    def _recopilar_puntos_espaciales(self):
        """Reúne los puntos de interés y avisos contextuales cercanos del nivel."""
        jx = self.jugador.rect.centerx
        jy = self.jugador.rect.centery
        puntos_clave = []
        es_retro = getattr(self, "preset_teclado_idx", 0) == 1
        tecla_atk = "C / J" if es_retro else "J / Z"
        tecla_dsh = "X / SHIFT" if es_retro else "SHIFT / X"
        tecla_jmp = "Z / ESPACIO" if es_retro else "ESPACIO"

        for dp in getattr(self.nivel, "power_ups_dash", []):
            if not getattr(dp, "recogida", False) and not getattr(dp, "recogido", False):
                puntos_clave.append((dp.rect.centerx, dp.rect.top, tecla_dsh, "Impulso Espectral (Dash)", True))

        for p in getattr(self.nivel, "palas", []):
            if not getattr(p, "recogida", False) and not getattr(p, "recogido", False):
                puntos_clave.append((p.rect.centerx, p.rect.top, tecla_atk, "Empuñar la Pala y Pisotón", True))

        for pr in getattr(self.nivel, "power_ups_rango", []):
            if not getattr(pr, "recogida", False) and not getattr(pr, "recogido", False):
                if getattr(pr, "sellado", False):
                    puntos_clave.append((pr.rect.centerx, pr.rect.top, "ALTAR SELLADO", "Derrota primero al Carcelero", False))
                else:
                    puntos_clave.append((pr.rect.centerx, pr.rect.top, tecla_atk, "Consagrar la Guadaña", True))

        es_tut = getattr(self, "es_tutorial", False)
        n_idx = getattr(self, "nivel_indice", 0)
        for cp in getattr(self.nivel, "checkpoints", []):
            es_farol_salto_fe = (
                n_idx == 2
                and not es_tut
                and cp.rect.centery < 18 * TILE
                and 290 <= (cp.rect.centerx // TILE) <= 312
            )
            if es_farol_salto_fe and self.pista_fe_mostrada:
                etq = getattr(config, "PISTA_SALTO_DE_FE_DUDA", "LO INVISIBLE SOSTIENE AL QUE CAMINA SIN VER.")
                puntos_clave.append((cp.rect.centerx, cp.rect.top, "EL ABISMO", etq, False))
            else:
                puntos_clave.append((cp.rect.centerx, cp.rect.top, "INSCRIPCIÓN", self._inscripcion_farol(cp), False))

        if es_tut or n_idx < 2:
            inc_cercanos = [
                inc for inc in getattr(self.nivel, "incensarios", [])
                if math.hypot(jx - inc.rect.centerx, jy - inc.rect.top) <= 125
            ]
            if inc_cercanos:
                inc_min = min(inc_cercanos, key=lambda inc: math.hypot(jx - inc.rect.centerx, jy - inc.rect.top))
                col_inc = inc_min.rect.centerx // TILE
                if es_tut and col_inc <= 28:
                    puntos_clave.append((inc_min.rect.centerx, inc_min.rect.top, "CAMPANA DE BRONCE", "Cae sobre ella para rebotar", False))
                elif not es_tut and n_idx == 0 and col_inc <= 100:
                    puntos_clave.append((inc_min.rect.centerx, inc_min.rect.top, "CAMPANA + DASH", "Rebota encima y recarga Dash", False))
                elif not es_tut and n_idx == 1 and (col_inc <= 145 or (180 <= col_inc <= 186)):
                    puntos_clave.append((inc_min.rect.centerx, inc_min.rect.top, tecla_atk, "Golpea o pisa: rebote + Dash", True))

        if getattr(self.nivel, "meta", None):
            puntos_clave.append((self.nivel.meta.centerx, self.nivel.meta.top, "PORTÓN SACRO", "Cruzar al siguiente nivel", False))

        if es_tut:
            puntos_clave.append((12 * TILE, 8 * TILE, tecla_jmp, "Toque corto o mantenido", True))
            if getattr(self.jugador, "escudo_farol", False):
                enemigos_cercanos = [
                    e for e in getattr(self.nivel, "enemigos", [])
                    if getattr(e, "vivo", True) and math.hypot(jx - e.rect.centerx, jy - e.rect.top) <= 125
                ]
                if enemigos_cercanos:
                    e_min = min(enemigos_cercanos, key=lambda e: math.hypot(jx - e.rect.centerx, jy - e.rect.top))
                    puntos_clave.append((e_min.rect.centerx, e_min.rect.top, "MANTO ACTIVO", "Absorbe un golpe enemigo", False))

        return puntos_clave

    def _dibujar_tablilla_espacial(self, destino, camara, fuentes, punto, bobbing):
        """Renderiza una tablilla flotante anclada en coordenadas del mundo si entra en alcance."""
        wx, wy, encabezado, label_corta, es_tecla = punto
        dist = math.hypot(self.jugador.rect.centerx - wx, self.jugador.rect.centery - wy)
        if dist > 125:
            return
        alfa = int(min(230, max(0, (125 - dist) / 40.0 * 230)))
        if alfa <= 4:
            return

        sx = int((wx - camara.x) * CAMARA_ZOOM)
        sy = int((wy - camara.y) * CAMARA_ZOOM + bobbing)
        label_corta = label_corta[:58]

        fuente_kc, fuente_lbl = fuentes
        kw, kh = fuente_kc.size(encabezado)
        lw, lh = fuente_lbl.size(label_corta)
        kc_h = max(14, kh + 2)
        hdr_h = max(kc_h, kh)
        bw = max(kw + 22, lw + 22)
        bh = hdr_h + max(13, lh) + 9
        h_conector = 16
        bh_total = bh + h_conector
        bx = sx - bw // 2
        by = sy - bh_total
        if not (-180 <= bx <= ANCHO + 80 and -60 <= by <= ALTO + 60):
            return

        lienzo = pygame.Surface((bw, bh_total), pygame.SRCALPHA)
        cx_local = bw // 2
        pygame.draw.line(lienzo, (218, 178, 86, min(alfa, 170)), (cx_local, bh), (cx_local, bh_total - 2), 1)
        pygame.draw.polygon(
            lienzo,
            (255, 235, 160, min(alfa, 220)),
            [(cx_local, bh_total - 4), (cx_local + 2, bh_total - 2), (cx_local, bh_total), (cx_local - 2, bh_total - 2)],
        )
        pygame.draw.rect(lienzo, (10, 8, 16, min(alfa, 232)), (0, 0, bw, bh), border_radius=5)
        pygame.draw.rect(lienzo, (4, 3, 8, min(alfa, 240)), (0, 0, bw, bh), 1, border_radius=5)
        pygame.draw.rect(lienzo, (198, 162, 82, min(alfa, 210)), (1, 1, bw - 2, bh - 2), 1, border_radius=4)

        if es_tecla:
            kc_w = kw + 10
            kc_x, kc_y = (bw - kc_w) // 2, 3
            pygame.draw.rect(lienzo, (150, 115, 45, alfa), (kc_x, kc_y + 1, kc_w, kc_h - 1), border_radius=3)
            pygame.draw.rect(lienzo, (228, 195, 110, alfa), (kc_x, kc_y, kc_w, kc_h - 1), border_radius=3)
            pygame.draw.rect(lienzo, (24, 20, 16, alfa), (kc_x, kc_y, kc_w, kc_h), 1, border_radius=3)
            img_kc = fuente_kc.render(encabezado, True, (24, 18, 20))
            img_kc.set_alpha(alfa)
            lienzo.blit(img_kc, (kc_x + (kc_w - kw) // 2, kc_y + (kc_h - kh) // 2))
        else:
            img_hdr = fuente_kc.render(encabezado, True, (224, 188, 98))
            img_hdr.set_alpha(alfa)
            lienzo.blit(img_hdr, ((bw - kw) // 2, 3))
            sep_y = hdr_h + 4
            pygame.draw.line(lienzo, (130, 102, 48, min(alfa, 145)), (8, sep_y), (bw - 8, sep_y), 1)

        img_lbl = fuente_lbl.render(label_corta, True, (244, 238, 226))
        img_sombra = fuente_lbl.render(label_corta, True, (0, 0, 0))
        img_lbl.set_alpha(alfa)
        img_sombra.set_alpha(alfa)
        lx = (bw - lw) // 2
        ly = hdr_h + 6
        lienzo.blit(img_sombra, (lx + 1, ly + 1))
        lienzo.blit(img_lbl, (lx, ly))
        destino.blit(lienzo, (bx, by))

    def dibujar_ui_espacial(self, destino=None, camara=None):
        """UI Espacial: tablillas de obsidiana y bronce ancladas a objetos interactivos."""
        if not self.jugador or not self.nivel:
            return
        if destino is None:
            destino = self.pantalla
        if camara is None:
            camara = self.camara

        tiempo = pygame.time.get_ticks() / 1000.0
        bobbing = math.sin(tiempo * 4.0) * 3.0
        fuentes = (
            self.fuentes.get(10) or self.obtener_fuente(10),
            self.fuentes.get(11) or self.obtener_fuente(11),
        )
        for punto in self._recopilar_puntos_espaciales():
            self._dibujar_tablilla_espacial(destino, camara, fuentes, punto, bobbing)

    def calcular_rango_liturgico(self):
        """Calcula el rango litúrgico de la campaña (S+, S, A, B, C) con base en tiempo, vidas y caídas."""
        t = getattr(self, "tiempo_total", 0.0)
        vidas = self.jugador.vidas if getattr(self, "jugador", None) else 0
        muertes = getattr(self, "muertes_totales", 0)

        if t < 240 or (t < 320 and muertes == 0 and vidas >= 4):
            return "S+ · RÉQUIEM SUPREMO", (255, 230, 110)
        elif t < 420 and muertes <= 1:
            return "S · MAESTRO DEL OSARIO", ORO
        elif t < 600 and muertes <= 3:
            return "A · SEPULTURERO SACRO", (195, 205, 220)
        elif t < 900:
            return "B · EXPLORADOR DE CRIPTAS", CREMA
        else:
            return "C · EL OSARIO TE PUSO A PRUEBA", HUESO

    def dibujar_victoria(self):
        """Pantalla de victoria estilizada con panel gótico y estadísticas litúrgicas completas."""
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((5, 4, 10, 215))
        self.pantalla.blit(overlay, (0, 0))

        t = self.tiempo_total
        for i in range(14):
            ang = (i / 14) * math.tau + t * 0.18
            rx = ANCHO // 2 + int(math.cos(ang) * 300)
            ry = ALTO // 2 + int(math.sin(ang) * 160)
            radio = 3 if i % 3 == 0 else 2
            alpha = int(120 + 80 * math.sin(ang * 1.7 + t))
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

        # Pie constante
        self.dibujar_texto("[ENTER] Confirmar · [ESC] Volver al Menú",
                           0, py + ph - 24, 13, HUD_MUTED, centrado=True)

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

        # Separador inferior y opciones de Continue / Reinicio desde Nivel 1
        pygame.draw.line(self.pantalla, (160, 40, 50, 160),
                         (px + 30, py + 336), (px + pw - 30, py + 336), 1)
        if self.sala_prueba or self.es_tutorial:
            self.dibujar_texto("[ENTER] Reintentar · [ESC] Volver al Menú",
                               0, py + 382, 16, HUD_ORO, centrado=True, sombra=True)
        else:
            cont_restantes = getattr(self, "continues", 0)
            if cont_restantes > 0:
                op_sel = getattr(self, "derrota_opcion", 0)
                txt_op0 = f"{'▶ ' if op_sel == 0 else '   '}USAR CONTINUE ({cont_restantes} disp.) · Reiniciar Nivel {self.nivel_indice + 1} desde 0"
                txt_op1 = f"{'▶ ' if op_sel == 1 else '   '}NUEVA PARTIDA · Empezar desde Nivel 1 (El Camposanto)"
                self.dibujar_texto(txt_op0, 0, py + 362, 15, HUD_ORO if op_sel == 0 else HUD_MUTED, centrado=True, sombra=True)
                self.dibujar_texto(txt_op1, 0, py + 390, 15, HUD_ORO if op_sel == 1 else HUD_MUTED, centrado=True, sombra=True)
                self.dibujar_texto("[↑/↓] Elegir · [ENTER] Confirmar · [ESC] Menú",
                                   0, py + 418, 12, CREMA, centrado=True)
            else:
                self.dibujar_texto("SIN CONTINUES DISPONIBLES (0 / 2)",
                                   0, py + 362, 15, HUD_ROJO, centrado=True, sombra=True)
                self.dibujar_texto("[ENTER] Empezar desde Nivel 1 (El Camposanto) · [ESC] Menú",
                                   0, py + 396, 15, HUD_ORO, centrado=True, sombra=True)

    def obtener_fuente(self, tamano):
        escala = float(getattr(config, "ESCALA_FUENTES_ACTIVA", 1.15))
        if escala != getattr(self, "_escala_fuente_cache", escala):
            self._escala_fuente_cache = escala
            self.fuentes.clear()
            self._cache_texto.clear()
        if tamano not in self.fuentes:
            tam_eff = max(8, round(tamano * escala))
            try:
                self.fuentes[tamano] = pygame.font.Font(self._ruta_fuente_gotica, tam_eff)
            except Exception:
                self.fuentes[tamano] = pygame.font.Font(None, tam_eff)
        return self.fuentes[tamano]

    def dibujar_texto(self, texto, x, y, tamano=24, color=BLANCO, centrado=False, sombra=False, derecha=False):
        fuente = self.obtener_fuente(tamano)

        if sombra:
            imagen_sombra = self._renderizar_texto_cache(
                self.fuentes[tamano], tamano, texto, (8, 6, 12))
            rect_sombra = imagen_sombra.get_rect()
            for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (2, 2)):
                if centrado:
                    rect_sombra.center = (ANCHO // 2 + ox, y + oy)
                elif derecha:
                    rect_sombra.topright = (x + ox, y + oy)
                else:
                    rect_sombra.topleft = (x + ox, y + oy)
                self.pantalla.blit(imagen_sombra, rect_sombra)

        imagen = self._renderizar_texto_cache(self.fuentes[tamano], tamano, texto, color)
        rect = imagen.get_rect()
        if centrado:
            rect.center = (ANCHO // 2, y)
        elif derecha:
            rect.topright = (x, y)
        else:
            rect.topleft = (x, y)
        self.pantalla.blit(imagen, rect)

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
