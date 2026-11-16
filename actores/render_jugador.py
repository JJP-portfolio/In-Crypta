#---- Importamos librerias y configuracion ----#
import math

import pygame

from actores.estampas import (
    obtener_arco_guadaña,
    obtener_estampa_fantasma,
    obtener_estampa_luz,
)
from config import (
    AZUL_OSCURO,
    BLANCO,
    CARMESÍ_SANGRE,
    FAROL_CÁLIDO,
    GRIS,
    MARRON,
    MARRON_OSCURO,
    NEGRO_NOCHE,
    ORO_LITÚRGICO,
    TURQUESA_ÁNIMA,
)


#---- Mixin de renderizado del sepulturero ----#
class RenderJugadorMixin:
    """Metodos de dibujo del sepulturero, su arma, su farol y sus bendiciones."""

    def _dibujar_estela_y_luz(self, surface, rect, tiempo):
        # Dibuja las estelas del dash, sombra de contacto y halo del farol
        if self.dash_tiempo > 0:
            es_guadana = getattr(self, "rango_ataque_mejorado", False)
            col_ghost = (195, 85, 250) if es_guadana else (92, 220, 200)
            for i, alfa in enumerate((180, 120, 70, 30)):
                fx = rect.x - self.dash_direccion * (9 + i * 8)
                ghost_surf = obtener_estampa_fantasma(rect.width, rect.height, alfa, col_ghost)
                surface.blit(ghost_surf, (fx, rect.y))

        pygame.draw.ellipse(surface, NEGRO_NOCHE, (rect.x + 1, rect.bottom - 5, rect.width - 2, 8))

        farol_x = rect.centerx + self.direccion * 11
        farol_y = rect.y + 19
        tiene_consagrado = getattr(self, "rango_ataque_mejorado", False)
        color_halo = (195, 80, 255) if tiene_consagrado else FAROL_CÁLIDO
        halo_farol = obtener_estampa_luz(85, color_halo, 28 if tiene_consagrado else 22)
        surface.blit(halo_farol, (farol_x - 85, farol_y - 85), special_flags=pygame.BLEND_RGB_ADD)

    def _calcular_pose_y_escala(self, atacando):
        # Calcula deformacion elastica y paso de caminata
        moviendo = self.en_suelo and abs(self.vx) > 1 and not atacando
        despliegue_pierna = 0
        escala_x = 1.0
        escala_y = 1.0
        if getattr(self, "squash_timer", 0.0) > 0 and getattr(self, "squash_tipo", None):
            if self.squash_tipo == "salto":
                frac = min(1.0, self.squash_timer / 0.10)
                escala_y = 1.0 + 0.15 * frac
                escala_x = 1.0 - 0.13 * frac
            elif self.squash_tipo == "aterrizaje":
                frac = min(1.0, self.squash_timer / 0.09)
                escala_y = 1.0 - 0.15 * frac
                escala_x = 1.0 + 0.18 * frac
        elif moviendo:
            pasos = ((0.95, 6), (0.98, 2), (1.05, -5), (1.02, -1))
            escala_y, despliegue_pierna = pasos[int((self.tiempo_animacion * 9.5) % 4)]
        return despliegue_pierna, escala_x, escala_y

    def _dibujar_filo_guadana(self, surface, arco_caja, punta_x, alto_pala):
        # Hoja amatista y arco energetico de la Guadana Consagrada
        signo = self.direccion
        puntos_hoja = [
            (punta_x - signo * 4, alto_pala - 8),
            (punta_x + signo * 12, alto_pala - 11),
            (punta_x + signo * 25, alto_pala - 5),
            (punta_x + signo * 33, alto_pala + 9),
            (punta_x + signo * 31, alto_pala + 20),
            (punta_x + signo * 23, alto_pala + 13),
            (punta_x + signo * 15, alto_pala + 6),
            (punta_x + signo * 4, alto_pala + 3),
            (punta_x - signo * 2, alto_pala),
        ]
        pygame.draw.polygon(surface, (150, 48, 200), puntos_hoja)
        relleno = [puntos_hoja[1], puntos_hoja[2], puntos_hoja[3], puntos_hoja[6], puntos_hoja[7]]
        pygame.draw.polygon(surface, (215, 105, 255), relleno)
        pygame.draw.lines(surface, (255, 240, 255), False, puntos_hoja[:5], 2)
        pygame.draw.circle(surface, ORO_LITÚRGICO, (punta_x, alto_pala), 3)

        onda_x, onda_y = arco_caja.x - 2, arco_caja.y - 4
        surface.blit(obtener_arco_guadaña(signo), (onda_x, onda_y))
        if getattr(self, "filo_anima", False):
            start_ang = 0.0 if signo > 0 else 1.57
            end_ang = 3.14 if signo > 0 else 4.71
            box_ext = (onda_x - 3, onda_y - 3, arco_caja.width + 6, arco_caja.height + 12)
            box_int = (onda_x - 1, onda_y - 1, arco_caja.width + 2, arco_caja.height + 8)
            pygame.draw.arc(surface, TURQUESA_ÁNIMA, box_ext, start_ang, end_ang, 2)
            pygame.draw.arc(surface, ORO_LITÚRGICO, box_int, start_ang, end_ang, 1)

    def _dibujar_filo_pala(self, surface, arco_caja, punta_x, alto_pala):
        # Hoja acerada y arco luminoso del ataque comun con pala
        signo = self.direccion
        hoja = [
            (punta_x, alto_pala - 5), (punta_x + signo * 8, alto_pala),
            (punta_x, alto_pala + 6), (punta_x - signo * 2, alto_pala),
        ]
        filo_oro = [
            (punta_x + signo * 4, alto_pala - 3),
            (punta_x + signo * 8, alto_pala),
            (punta_x + signo * 4, alto_pala + 3),
        ]
        pygame.draw.polygon(surface, (195, 198, 208), hoja)
        pygame.draw.polygon(surface, ORO_LITÚRGICO, filo_oro)
        ang_ini = -0.4 if signo > 0 else 2.6
        ang_fin = 2.4 if signo > 0 else 5.4
        pygame.draw.arc(surface, (230, 235, 245), arco_caja, ang_ini, ang_fin, 2)
        pygame.draw.arc(surface, ORO_LITÚRGICO, arco_caja.inflate(2, 2), ang_ini, ang_fin, 1)
        if getattr(self, "filo_anima", False):
            pygame.draw.arc(surface, TURQUESA_ÁNIMA, arco_caja.inflate(6, 6), ang_ini, ang_fin, 2)
            pygame.draw.arc(surface, (255, 235, 140), arco_caja.inflate(4, 4), ang_ini, ang_fin, 1)
            for off_i in range(3):
                sp_x = punta_x - signo * (off_i * 6 + 4)
                sp_y = alto_pala + (off_i * 3 - 3)
                col_sp = (255, 225, 90) if off_i % 2 == 0 else TURQUESA_ÁNIMA
                pygame.draw.circle(surface, col_sp, (sp_x, sp_y), 2)
        pygame.draw.circle(surface, (255, 245, 190), (punta_x + signo * 2, alto_pala), 2)

    def _dibujar_arma_en_ataque(self, surface, camara, rect, pose, con_pala, es_guadana, color_mango):
        # Dibuja mango y hoja durante cualquiera de las tres fases del tajo
        centro_x, base_y = rect.centerx, rect.bottom
        hombro_x = centro_x - self.direccion * 7
        alcance = (36 if es_guadana else 16) if pose == "ataque2" else (28 if es_guadana else 13)
        alto_pala = {
            "ataque1": rect.y - (6 if es_guadana else -2),
            "ataque2": rect.y + 12,
            "ataque3": base_y + (4 if es_guadana else -1),
        }[pose]
        punta_x = centro_x + self.direccion * alcance
        origen_mango = (hombro_x, rect.y + 8)
        grosor = 4 if es_guadana else 3
        pygame.draw.line(surface, color_mango, origen_mango, (punta_x, alto_pala), grosor)
        if es_guadana:
            p0 = (punta_x - self.direccion * 5, alto_pala - 2)
            p1 = (punta_x + self.direccion * 2, alto_pala + 2)
            pygame.draw.line(surface, ORO_LITÚRGICO, p0, p1, 2)
            pygame.draw.circle(surface, (215, 110, 255), origen_mango, 2)
        if not con_pala:
            return
        arco_caja = camara.aplicar_rect(self.rect_ataque())
        if es_guadana:
            self._dibujar_filo_guadana(surface, arco_caja, punta_x, alto_pala)
        else:
            self._dibujar_filo_pala(surface, arco_caja, punta_x, alto_pala)

    def _dibujar_arma_pisoton(self, surface, rect, color_mango, es_guadana):
        # Dibuja el arma apuntando hacia abajo en picada
        centro_x, base_y = rect.centerx, rect.bottom
        p_sup, p_inf = (centro_x, rect.centery + 2), (centro_x, base_y + 11)
        pygame.draw.line(surface, color_mango, p_sup, p_inf, 4 if es_guadana else 3)
        punta_y = base_y + (16 if es_guadana else 13)
        if es_guadana:
            puntos = [
                (centro_x - 6, base_y + 6), (centro_x + 11, base_y + 7),
                (centro_x + 9, base_y + 14), (centro_x, punta_y + 2), (centro_x - 3, base_y + 10),
            ]
            pygame.draw.polygon(surface, (185, 65, 235), puntos)
            pygame.draw.lines(surface, (255, 240, 255), False, puntos[:4], 2)
            pygame.draw.circle(surface, ORO_LITÚRGICO, (centro_x, base_y + 7), 2)
        else:
            pala = [(centro_x - 5, base_y + 4), (centro_x + 5, base_y + 4), (centro_x, punta_y)]
            brillo = [(centro_x - 3, base_y + 5), (centro_x + 3, base_y + 5), (centro_x, punta_y - 1)]
            pygame.draw.polygon(surface, (195, 198, 208), pala)
            pygame.draw.polygon(surface, ORO_LITÚRGICO, brillo)
        pygame.draw.line(surface, BLANCO, (centro_x - 4, punta_y), (centro_x + 4, punta_y), 1)
        pygame.draw.line(surface, BLANCO, (centro_x, punta_y - 4), (centro_x, punta_y + 4), 1)
        pygame.draw.circle(surface, (255, 245, 190), (centro_x, punta_y), 2)

    def _dibujar_arma_en_espalda(self, surface, rect, hombro_x, color_mango, es_guadana):
        # Dibuja la pala o guadana enfundada sobre la espalda
        base_y = rect.bottom
        signo = self.direccion
        if es_guadana:
            top_x, top_y = hombro_x + signo * 2, rect.y - 4
            bot_x, bot_y = hombro_x - signo * 10, base_y + 4
            pygame.draw.line(surface, color_mango, (top_x, top_y), (bot_x, bot_y), 3)
            pygame.draw.circle(surface, ORO_LITÚRGICO, (top_x, top_y), 2)
            hoja = [
                (top_x - signo * 2, top_y - 2), (top_x + signo * 9, top_y - 8),
                (top_x + signo * 17, top_y - 2), (top_x + signo * 11, top_y + 4),
                (top_x + signo * 4, top_y + 1),
            ]
            pygame.draw.polygon(surface, (190, 72, 238), hoja)
            pygame.draw.lines(surface, (255, 232, 255), False, hoja[:3], 1)
            return

        pygame.draw.line(surface, MARRON, (hombro_x, rect.y + 7), (hombro_x - signo * 4, base_y - 2), 3)
        pala = [
            (hombro_x - signo * 7, base_y - 4),
            (hombro_x - signo * 1, base_y - 1),
            (hombro_x - signo * 4, base_y + 4),
        ]
        pygame.draw.polygon(surface, GRIS, pala)

    def _dibujar_arma_sepulturero(self, surface, camara, rect, pose, con_pala, atacando, postura_pisoton):
        # Selecciona la postura de renderizado del arma segun accion
        hombro_x = rect.centerx - self.direccion * 7
        es_guadana = getattr(self, "rango_ataque_mejorado", False)
        color_mango = (45, 30, 48) if es_guadana else MARRON

        if atacando:
            self._dibujar_arma_en_ataque(surface, camara, rect, pose, con_pala, es_guadana, color_mango)
        elif postura_pisoton:
            self._dibujar_arma_pisoton(surface, rect, color_mango, es_guadana)
        elif con_pala:
            self._dibujar_arma_en_espalda(surface, rect, hombro_x, color_mango, es_guadana)

    def _dibujar_piernas_sepulturero(
        self, surface, rect, pose, en_aire, atacando, postura_pisoton, despliegue_pierna, escala_y
    ):
        # Dibuja las piernas y botas animadas segun la postura
        centro_x, base_y = rect.centerx, rect.bottom
        if postura_pisoton:
            cadera_y, pie_y = base_y - 9, base_y - 2
            pares = ((centro_x - 4, centro_x - 2), (centro_x + 4, centro_x + 2))
        elif en_aire:
            sep = 7 if pose == "caida" else 9
            cadera_y, pie_y = base_y - 9, base_y - 2
            pares = ((centro_x - 5, centro_x - sep), (centro_x + 5, centro_x + sep))
        elif atacando:
            cadera_y, pie_y = base_y - 9, base_y - 1
            pares = ((centro_x - 5, centro_x - 7), (centro_x + 5, centro_x + 7))
        else:
            cadera_y, pie_y = base_y - int(9 * escala_y), base_y - 1
            pares = (
                (centro_x - 5, centro_x - 5 + despliegue_pierna),
                (centro_x + 5, centro_x + 5 - despliegue_pierna),
            )

        for origen_x, pie_x in pares:
            pygame.draw.line(surface, MARRON_OSCURO, (origen_x, cadera_y), (pie_x, pie_y), 4)
            pygame.draw.line(surface, NEGRO_NOCHE, (pie_x - 2, pie_y), (pie_x + 3, pie_y), 4)

    def _dibujar_cabeza_y_sombrero(self, surface, rect, cabeza_y, dw):
        # Cabeza embozada, sombrero gotico de ala ancha, ojos y bufanda carmesi
        centro_x = rect.centerx
        pygame.draw.circle(surface, (185, 175, 160), (centro_x, cabeza_y), 8)
        pygame.draw.circle(surface, NEGRO_NOCHE, (centro_x, cabeza_y), 8, 1)
        embozo = [
            (centro_x - 7, cabeza_y - 3), (centro_x + 7, cabeza_y - 3),
            (centro_x + 5, cabeza_y + 2), (centro_x - 5, cabeza_y + 2),
        ]
        pygame.draw.polygon(surface, NEGRO_NOCHE, embozo)

        ala_y = cabeza_y - 6
        pygame.draw.ellipse(surface, NEGRO_NOCHE, (rect.x - 2 - dw // 2, ala_y, rect.width + 4 + dw, 6))
        copa = [
            (rect.x + 4, ala_y), (rect.right - 4, ala_y), (centro_x - self.direccion * 4, cabeza_y - 15)
        ]
        pygame.draw.polygon(surface, (26, 20, 30), copa)
        pygame.draw.polygon(surface, NEGRO_NOCHE, copa, 1)
        pygame.draw.rect(surface, CARMESÍ_SANGRE, (rect.x + 5, cabeza_y - 8, rect.width - 10, 2))
        pygame.draw.rect(surface, (218, 178, 86), (centro_x - 2, cabeza_y - 9, 4, 3), 1)

        ojo_x = centro_x + self.direccion * 2
        pygame.draw.circle(surface, (160, 215, 255), (ojo_x, cabeza_y), 1)
        pygame.draw.circle(surface, (160, 215, 255), (ojo_x + self.direccion * 3, cabeza_y), 1)

        cuello = [
            (centro_x - 8, cabeza_y + 3), (centro_x - 4, cabeza_y + 8),
            (centro_x + 4, cabeza_y + 8), (centro_x + 8, cabeza_y + 3),
        ]
        pygame.draw.polygon(surface, (30, 24, 36), cuello)
        pygame.draw.rect(surface, CARMESÍ_SANGRE, (centro_x - 7, cabeza_y + 5, 14, 3), border_radius=1)

    def _dibujar_cuerpo_y_sombrero(self, surface, rect, escala_x, escala_y):
        # Dibuja el abrigo, la falda con inercia y delega cabeza y sombrero
        centro_x, base_y = rect.centerx, rect.bottom
        inercia_falda = -self.direccion * min(7, int(abs(self.vx) * 0.024))
        dw = int(rect.width * (escala_x - 1.0))
        cuerpo = pygame.Rect(
            rect.x + 3 - dw // 2,
            rect.y + int(10 * escala_y),
            rect.width - 6 + dw,
            rect.height - int(16 * escala_y),
        )

        pygame.draw.rect(surface, AZUL_OSCURO, cuerpo, border_radius=4)
        pechera = (cuerpo.x + 4, cuerpo.y + 5, cuerpo.width - 8, cuerpo.height - 5)
        pygame.draw.rect(surface, MARRON, pechera, border_radius=3)
        pygame.draw.rect(surface, NEGRO_NOCHE, cuerpo, 2, border_radius=4)
        pygame.draw.rect(surface, MARRON_OSCURO, (cuerpo.x, cuerpo.y + 7, cuerpo.width, 3))

        falda_y = base_y - 8
        puntos_falda = [
            (cuerpo.x, falda_y - 4), (cuerpo.right, falda_y - 4),
            (cuerpo.right + inercia_falda, falda_y + 4),
            (centro_x + inercia_falda * 0.7, falda_y + 2),
            (cuerpo.x + inercia_falda - 1, falda_y + 4),
        ]
        pygame.draw.polygon(surface, AZUL_OSCURO, puntos_falda)
        pygame.draw.polygon(surface, NEGRO_NOCHE, puntos_falda, 1)
        if self.dash_tiempo > 0:
            pygame.draw.rect(surface, TURQUESA_ÁNIMA, cuerpo, 1, border_radius=5)

        self._dibujar_cabeza_y_sombrero(surface, rect, rect.y + int(10 * escala_y), dw)

    def _dibujar_auras_bendiciones(self, surface, rect, tiempo):
        # Escudo del manto y chispas orbitantes del Filo de Anima
        centro_x = rect.centerx
        if getattr(self, "escudo_farol", False):
            pulso = 0.5 + 0.5 * math.sin(tiempo * 6.0)
            w_a, h_a = rect.width + 24, rect.height + 24
            aura = pygame.Surface((w_a, h_a), pygame.SRCALPHA)
            pygame.draw.ellipse(aura, (92, 190, 220, int(35 + pulso * 25)), (0, 0, w_a, h_a), 1)
            box_int = (4, 4, rect.width + 16, rect.height + 16)
            pygame.draw.ellipse(aura, (140, 225, 255, int(65 + pulso * 45)), box_int, 2)
            surface.blit(aura, (rect.x - 12, rect.y - 12))
            for k in range(4):
                ang = tiempo * 2.4 + k * (math.tau / 4.0)
                rx = centro_x + int(math.cos(ang) * (rect.width // 2 + 10))
                ry = rect.centery + int(math.sin(ang) * (rect.height // 2 + 8))
                rombo = [(rx, ry - 3), (rx + 2, ry), (rx, ry + 3), (rx - 2, ry)]
                pygame.draw.polygon(surface, (140, 230, 255), rombo)
                pygame.draw.circle(surface, BLANCO, (rx, ry), 1)

        if getattr(self, "filo_anima", False):
            for i, offset_fase in enumerate((0.0, 2.09, 4.18)):
                t_f = tiempo * 4.0 + offset_fase
                ch_x = centro_x + int(math.cos(t_f) * 14)
                ch_y = rect.centery + int(math.sin(t_f) * 14)
                col_ch = (255, 215, 80) if i % 2 == 0 else TURQUESA_ÁNIMA
                pygame.draw.circle(surface, col_ch, (ch_x, ch_y), 2)

    def _dibujar_farol_y_auras(self, surface, rect, tiempo):
        # Dibuja el farol colgante de mano y delega auras activas
        centro_x = rect.centerx
        farol_x = centro_x + self.direccion * 11
        farol_y = rect.y + 19
        pygame.draw.circle(surface, (115, 82, 34), (farol_x, farol_y), 6)
        pygame.draw.circle(surface, (165, 120, 50), (farol_x, farol_y), 6, 1)

        if self.tiene_dash and self.dash_listo():
            pygame.draw.circle(surface, (92, 220, 200), (farol_x, farol_y), 4)
            pygame.draw.line(surface, BLANCO, (farol_x - 5, farol_y), (farol_x + 5, farol_y), 1)
            pygame.draw.line(surface, BLANCO, (farol_x, farol_y - 5), (farol_x, farol_y + 5), 1)
            for des_ang in (0.0, math.pi):
                sx = farol_x + int(math.cos(tiempo * 6.0 + des_ang) * 6)
                sy = farol_y + int(math.sin(tiempo * 6.0 + des_ang) * 6)
                pygame.draw.circle(surface, (140, 245, 255), (sx, sy), 1)
        else:
            pygame.draw.circle(surface, (175, 115, 45), (farol_x, farol_y), 3)
            pygame.draw.circle(surface, (225, 165, 75), (farol_x, farol_y), 1)
            for h_idx in range(2):
                fase_h = (tiempo * 14.0 + h_idx * 3.0) % 7.0
                hx = farol_x - self.direccion * int(fase_h * 0.6)
                hy = farol_y - 4 - int(fase_h)
                pygame.draw.circle(surface, (125, 122, 132), (hx, hy), 1)

        p_cadena = (centro_x + self.direccion * 7, rect.y + 15)
        pygame.draw.line(surface, GRIS, p_cadena, (farol_x, rect.y + 15), 1)
        self._dibujar_auras_bendiciones(surface, rect, tiempo)

    def dibujar(self, surface, camara, tiempo, pose=None, con_pala=True):
        """Renderiza al sepulturero con arma, cuerpo, sombra y farol."""
        if self.invulnerable > 0 and int(tiempo * 16) % 2 == 0:
            return
        rect = camara.aplicar_rect(self.rect)
        en_aire = pose in ("caida", "caida2") or not self.en_suelo
        atacando = pose in ("ataque1", "ataque2", "ataque3")
        postura_pisoton = con_pala and en_aire and self.vy > 60 and not atacando

        self._dibujar_estela_y_luz(surface, rect, tiempo)
        despliegue_pierna, escala_x, escala_y = self._calcular_pose_y_escala(atacando)
        self._dibujar_arma_sepulturero(surface, camara, rect, pose, con_pala, atacando, postura_pisoton)
        self._dibujar_piernas_sepulturero(
            surface, rect, pose, en_aire, atacando, postura_pisoton, despliegue_pierna, escala_y
        )
        self._dibujar_cuerpo_y_sombrero(surface, rect, escala_x, escala_y)
        self._dibujar_farol_y_auras(surface, rect, tiempo)
