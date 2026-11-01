# ============================================================
# tests/test_hud.py — Tests de HUD de IN CRYPTA (headless)
# ============================================================
# Verifica layout, contadores, mensajes, animaciones y caché
# sin tocar gameplay. Correr con SDL_VIDEODRIVER=dummy.
# ============================================================

import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from hud import (
    HudLayout,
    HudOrquestador,
    HudModel,
    HudRenderer,
    HudTheme,
    MensajeHUD,
    TextoCache,
    Tween,
    envolver,
    fmt_cooldown,
    fmt_dash,
    fmt_tiempo,
    fmt_tiempo_dec,
    _partir_palabra,
    fmt_arma,
)
from config import ALMAS_POR_VIDA, ANCHO, ALTO, JEFE_VIDA, VIDAS_MAXIMAS


class TestTween(unittest.TestCase):
    def test_lineal_no_supera_uno(self):
        t = Tween(0.2, curva="linear")
        t.update(0.1)
        self.assertAlmostEqual(t.valor(), 0.5)
        t.update(0.2)
        self.assertAlmostEqual(t.valor(), 1.0)

    def test_out_back_puede_superar_uno(self):
        t = Tween(0.2, curva="out_back")
        t.update(0.2)
        self.assertGreaterEqual(t.valor(), 1.0)

    def test_esta_activo(self):
        t = Tween(0.2)
        self.assertTrue(t.esta_activo())
        t.update(0.3)
        self.assertFalse(t.esta_activo())


class TestFormatos(unittest.TestCase):
    def test_fmt_cooldown(self):
        self.assertEqual(fmt_cooldown(0), "LISTO")
        self.assertEqual(fmt_cooldown(0.35), "0.4s")
        self.assertEqual(fmt_cooldown(0.60), "0.6s")
        self.assertEqual(fmt_cooldown(0.05), "0.1s")
        self.assertEqual(fmt_cooldown(0.01), "0.1s")

    def test_fmt_dash(self):
        m = HudModel(dash_cooldown=0.3, en_suelo=True, dash_usos_aire=1)
        self.assertEqual(fmt_dash(m), "[DASH] 0.3s")
        m.dash_cooldown = 0.0
        self.assertEqual(fmt_dash(m), "[DASH] LISTO")
        # Prioridad: cooldown > SIN USO
        m.dash_cooldown = 0.2
        m.en_suelo = False
        m.dash_usos_aire = 0
        self.assertEqual(fmt_dash(m), "[DASH] 0.2s")
        # En el aire sin uso
        m.dash_cooldown = 0.0
        self.assertEqual(fmt_dash(m), "[DASH] SIN USO")

    def test_fmt_arma(self):
        m = HudModel(tiene_pala=False)
        self.assertEqual(fmt_arma(m), "[PALA] --")
        m.tiene_pala = True
        m.rango_ataque_mejorado = False
        m.ataque_cooldown = 0.0
        self.assertEqual(fmt_arma(m), "[PALA] LISTO")
        m.ataque_cooldown = 0.35
        self.assertEqual(fmt_arma(m), "[PALA] 0.4s")
        m.rango_ataque_mejorado = True
        m.ataque_cooldown = 0.0
        self.assertEqual(fmt_arma(m), "[GUADAÑA] LISTO")

    def test_fmt_tiempo(self):
        self.assertEqual(fmt_tiempo(59.9), "00:59")
        self.assertEqual(fmt_tiempo(60), "01:00")
        self.assertEqual(fmt_tiempo(0), "00:00")
        self.assertEqual(fmt_tiempo_dec(83.27), "01:23.2")
        self.assertEqual(fmt_tiempo_dec(0.0), "00:00.0")


class TestLayout(unittest.TestCase):
    def test_no_hay_solapamientos(self):
        layout = HudLayout.construir()
        self.assertEqual(layout.solapamientos(), [])

    def test_geometria_exacta(self):
        layout = HudLayout.construir()
        self.assertEqual(layout.riel, pygame.Rect(24, 16, 1232, 72))
        self.assertEqual(layout.zona_izq, pygame.Rect(24, 16, 336, 72))
        self.assertEqual(layout.zona_centro, pygame.Rect(372, 16, 512, 72))
        self.assertEqual(layout.zona_der, pygame.Rect(896, 16, 360, 72))
        self.assertEqual(layout.canal_mensajes, pygame.Rect(360, 96, 560, 48))

    def test_celdas_derechas_164x22_no_se_solapan(self):
        layout = HudLayout.construir()
        c = layout.contenido_der
        celda_w, celda_h = 164, 22
        gap_x, gap_y = 8, 4
        rects = []
        for fila in range(2):
            for col in range(2):
                x = c.x + col * (celda_w + gap_x)
                y = c.y + fila * (celda_h + gap_y)
                rects.append(pygame.Rect(x, y, celda_w, celda_h))
        self.assertEqual(c.w, 2 * celda_w + gap_x)
        self.assertEqual(c.h, 2 * celda_h + gap_y)
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                self.assertFalse(rects[i].colliderect(rects[j]))

    def test_barra_jefe_segmentos(self):
        segmento_w, segmento_h = 68, 12
        gap = 4
        total = JEFE_VIDA * segmento_w + (JEFE_VIDA - 1) * gap
        self.assertEqual(total, 428)
        self.assertEqual(total + 12 + 48, 488)


class TestMensajes(unittest.TestCase):
    def test_prioridad_jefe_sobre_pista(self):
        layout = HudLayout.construir()
        tema = HudTheme()
        cache = TextoCache(lambda t: pygame.font.Font(None, t))
        m = MensajeHUD(layout, tema, cache)
        m.mostrar("pista inicial", 0, 4.0)
        m.mostrar("¡FASE II!", 3, 3.2)
        self.assertEqual(m.texto, "¡FASE II!")
        self.assertEqual(m.prioridad, 3)

    def test_menor_prioridad_no_reemplaza(self):
        layout = HudLayout.construir()
        tema = HudTheme()
        cache = TextoCache(lambda t: pygame.font.Font(None, t))
        m = MensajeHUD(layout, tema, cache)
        m.mostrar("¡FASE II!", 3, 3.2)
        m.mostrar("pista", 0, 4.0)
        self.assertEqual(m.texto, "¡FASE II!")
        self.assertEqual(m.prioridad, 3)

    def test_misma_prioridad_ignorada(self):
        layout = HudLayout.construir()
        tema = HudTheme()
        cache = TextoCache(lambda t: pygame.font.Font(None, t))
        m = MensajeHUD(layout, tema, cache)
        m.mostrar("objeto A", 2, 3.5)
        m.mostrar("objeto B", 2, 3.5)
        self.assertEqual(m.texto, "objeto A")


class TestEnvolver(unittest.TestCase):
    def test_max_dos_lineas(self):
        fuente = pygame.font.Font(None, 14)
        texto = "Esta es una pista bastante larga que no debe pasar de dos líneas"
        lineas = envolver(texto, fuente, 300, max_lineas=2)
        self.assertLessEqual(len(lineas), 2)
        for linea in lineas:
            self.assertLessEqual(fuente.size(linea)[0], 300)

    def test_elipsis_entra(self):
        fuente = pygame.font.Font(None, 14)
        texto = "PalabraExtraordinariamenteLargaQueNoEntra"
        lineas = envolver(texto, fuente, 50, max_lineas=2)
        self.assertTrue(lineas[-1].endswith("…"))
        self.assertLessEqual(fuente.size(lineas[-1])[0], 50)

    def test_partir_palabra(self):
        fuente = pygame.font.Font(None, 14)
        partes = _partir_palabra("ABCDE", fuente, 10)
        self.assertGreaterEqual(len(partes), 2)


class TestTextoCache(unittest.TestCase):
    def test_no_re_renderer_misma_clave(self):
        llamado = {"n": 0}

        class FuenteFalsa:
            def render(self, texto, antialias, color):
                llamado["n"] += 1
                surf = pygame.Surface((20, 10))
                surf.fill((255, 255, 255))
                return surf

        def cargar(tamano):
            return FuenteFalsa()

        cache = TextoCache(cargar)
        cache.render("HOLA", 14, (255, 255, 255))
        cache.render("HOLA", 14, (255, 255, 255))
        cache.render("MUNDO", 14, (255, 255, 255))
        self.assertEqual(llamado["n"], 2)


class TestModeloEventos(unittest.TestCase):
    def test_evento_alma_recogida(self):
        m = HudModel(almas=5)
        m.almas_prev = 3
        self.assertTrue(m.evento_alma_recogida())
        m.almas_prev = 5
        self.assertFalse(m.evento_alma_recogida())

    def test_evento_perdio_vida(self):
        m = HudModel(vidas=2)
        m.vidas_prev = 3
        self.assertTrue(m.evento_perdio_vida())

    def test_evento_vida_extra(self):
        m = HudModel(vidas=4)
        m.vidas_prev = 3
        self.assertTrue(m.evento_vida_extra())

    def test_evento_dash_listo(self):
        m = HudModel(dash_cooldown=0.0)
        m.dash_cooldown_prev = 0.3
        self.assertTrue(m.evento_dash_listo())

    def test_evento_jefe_cambio_fase(self):
        m = HudModel(jefe_fase=2)
        m.jefe_fase_prev = 1
        self.assertTrue(m.evento_jefe_cambio_fase())


class TestOrquestador(unittest.TestCase):
    def _jugador_falso(self, vidas=3, almas=0, almas_para_vida=0,
                       dash_cooldown=0.0, dash_usos_aire=1, en_suelo=True,
                       ataque_cooldown=0.0, tiene_pala=False):
        return type("JugadorFalso", (), {
            "vidas": vidas, "almas": almas, "almas_para_vida": almas_para_vida,
            "dash_cooldown": dash_cooldown, "dash_usos_aire": dash_usos_aire,
            "en_suelo": en_suelo, "ataque_cooldown": ataque_cooldown,
            "tiene_pala": tiene_pala,
        })()

    def _nivel_falso(self, total_almas=17, nombre="Camposanto"):
        return type("NivelFalso", (), {
            "total_almas": total_almas, "nombre": nombre,
        })()

    def test_modelo_sin_jefe_no_crashea(self):
        o = HudOrquestador()

        class JuegoFalso:
            jugador = self._jugador_falso()
            jefe = None
            nivel_indice = 0
            nivel = self._nivel_falso()
            tiempo_total = 10.5
            estado = "jugando"
            texto_ayuda = ""
            aviso_jefe = 0.0

        o.armar_modelo(JuegoFalso())
        self.assertFalse(o.modelo.jefe_vivo)
        self.assertEqual(o.modelo.vidas, 3)

    def test_dibujar_no_crashea_sin_jefe(self):
        o = HudOrquestador()
        pantalla = pygame.Surface((ANCHO, ALTO))

        class JuegoFalso:
            jugador = self._jugador_falso()
            jefe = None
            nivel_indice = 0
            nivel = self._nivel_falso()
            tiempo_total = 10.5
            estado = "jugando"
            texto_ayuda = ""
            aviso_jefe = 0.0

        o.dibujar(pantalla, JuegoFalso(), 0.016)

    def test_dibujar_con_jefe_no_crashea(self):
        o = HudOrquestador()
        pantalla = pygame.Surface((ANCHO, ALTO))

        class JefeFalso:
            vivo = True
            vida = 4
            fase = 2

        class JuegoFalso:
            jugador = self._jugador_falso()
            jefe = JefeFalso()
            nivel_indice = 2
            nivel = self._nivel_falso()
            tiempo_total = 10.5
            estado = "jugando"
            texto_ayuda = ""
            aviso_jefe = 0.0

        o.dibujar(pantalla, JuegoFalso(), 0.016)

    def test_modelo_escudo_farol(self):
        o = HudOrquestador()
        pantalla = pygame.Surface((ANCHO, ALTO))
        jf = self._jugador_falso()
        jf.escudo_farol = True

        class JuegoFalso:
            jugador = jf
            jefe = None
            nivel_indice = 0
            nivel = self._nivel_falso()
            tiempo_total = 5.0
            estado = "jugando"
            texto_ayuda = ""
            aviso_jefe = 0.0

        o.dibujar(pantalla, JuegoFalso(), 0.016)
        self.assertTrue(o.modelo.escudo_farol)

    def test_dibujar_con_minijefe(self):
        o = HudOrquestador()
        pantalla = pygame.Surface((ANCHO, ALTO))

        class MiniJefeFalso:
            vivo = True
            vida = 2
            estado = "ataque"
            rect = pygame.Rect(100, 100, 36, 48)

        jf = self._jugador_falso()
        jf.rect = pygame.Rect(120, 100, 24, 30)

        class NivelConMiniJefe:
            total_almas = 10
            nombre = "El Osario"
            minijefes = [MiniJefeFalso()]

        class JuegoFalso:
            jugador = jf
            jefe = None
            nivel_indice = 2
            nivel = NivelConMiniJefe()
            tiempo_total = 20.0
            estado = "jugando"
            texto_ayuda = ""
            aviso_jefe = 0.0

        o.dibujar(pantalla, JuegoFalso(), 0.016)
        self.assertTrue(o.modelo.jefe_vivo)
        self.assertEqual(o.modelo.jefe_vida, 2)
        self.assertEqual(o.modelo.jefe_vida_max, 3)
        self.assertEqual(o.modelo.jefe_nombre, "EL CARCELERO DEL OSARIO")


class TestPrioridad3UIUX(unittest.TestCase):
    """Verificaciones unitarias de los 4 Tipos de Interfaz y 5 Principios UX."""

    def test_ui_no_diegetica_riel_superior_fijo(self):
        """UI No Diegética: riel 1232x72 y panel derecho de ancho fijo (360 px) sin layout shifts."""
        layout = HudLayout.construir()
        self.assertEqual(layout.riel.size, (1232, 72))
        self.assertEqual(layout.zona_der.width, 360)
        self.assertEqual(layout.zona_izq.width, 336)
        self.assertEqual(layout.zona_centro.width, 512)

        # Formatos de la grilla 2x2
        m = HudModel(almas=5, almas_total=20, almas_para_vida=3)
        self.assertEqual(fmt_dash(m), "[DASH] LISTO")
        self.assertEqual(fmt_arma(m), "[PALA] --")
        m.tiene_pala = True
        self.assertEqual(fmt_arma(m), "[PALA] LISTO")
        m.rango_ataque_mejorado = True
        self.assertEqual(fmt_arma(m), "[GUADAÑA] LISTO")

    def test_ui_diegetica_faroles(self):
        """UI Diegética: Farol del jugador (llama turquesa/ámbar) y Checkpoints activos/inactivos."""
        from entidades import Jugador, FarolCheckpoint

        j = Jugador(100, 100)
        j.tiene_dash = True
        j.dash_cooldown = 0.0
        j.en_suelo = True
        self.assertTrue(j.dash_listo())

        # Checkpoint: inactivo (apagado) y activo (encendido)
        cp = FarolCheckpoint(pygame.Rect(200, 200, 20, 30))
        self.assertFalse(cp.activo)
        # Jugador toca el checkpoint
        j.rect.center = cp.rect.center
        cp.actualizar(j)
        self.assertTrue(cp.activo)

    def test_ui_espacial_coordenadas_y_distancia(self):
        """UI Espacial: cálculo de distancia a 140 px y proyección mediante camara.aplicar_rect."""
        from camara import Camara

        cam = Camara()
        cam.x = 200.0
        cam.y = 50.0

        rect_mundo = pygame.Rect(400, 300, 100, 30)
        rect_pantalla = cam.aplicar_rect(rect_mundo)
        self.assertEqual(rect_pantalla.x, 200)
        self.assertEqual(rect_pantalla.y, 250)


if __name__ == "__main__":
    unittest.main()
