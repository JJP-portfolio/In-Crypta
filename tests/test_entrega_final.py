#---- Tests integrados de la entrega final ----#

import os
import pathlib
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import pygame  # noqa: E402
import config  # noqa: E402
import entidades  # noqa: E402
import juego as juego_mod  # noqa: E402
from camara import Camara  # noqa: E402
from entidades import BloqueCripta, CompuertaArena, EnemigoMelee, FarolCheckpoint, Jugador  # noqa: E402
from juego import Juego  # noqa: E402


class GrabadorAudio:
    """Envoltorio liviano que registra los efectos y músicas solicitados durante una prueba."""

    def __init__(self, audio_real):
        self._real = audio_real
        self.efectos = []
        self.musicas = []

    def reproducir(self, nombre):
        self.efectos.append(nombre)
        return self._real.reproducir(nombre)

    def reproducir_musica(self, nombre, bucle=True, fade_ms=350):
        self.musicas.append((nombre, bucle, fade_ms))
        return self._real.reproducir_musica(nombre, bucle=bucle, fade_ms=fade_ms)

    def __getattr__(self, item):
        return getattr(self._real, item)


class EntregaFinalTests(unittest.TestCase):
    """Verificación integral de audio, combate, legibilidad, faroles y rediseño de nivel."""

    def test_f2_alterna_escala_fuente_y_invalida_caches(self):
        juego = Juego()
        try:
            escala_ini = config.ESCALA_FUENTES_ACTIVA
            self.assertIn(escala_ini, (1.15, 1.20, 1.25))
            tam_20_ini = juego.obtener_fuente(20).get_height()

            juego.alternar_escala_fuente(1)
            self.assertAlmostEqual(config.ESCALA_FUENTES_ACTIVA, 1.20, places=2)
            tam_20_mid = juego.obtener_fuente(20).get_height()
            self.assertGreaterEqual(tam_20_mid, tam_20_ini)

            juego.alternar_escala_fuente(1)
            self.assertAlmostEqual(config.ESCALA_FUENTES_ACTIVA, 1.25, places=2)
            tam_20_max = juego.obtener_fuente(20).get_height()
            self.assertGreater(tam_20_max, tam_20_ini)

            juego.alternar_escala_fuente(1)
            self.assertAlmostEqual(config.ESCALA_FUENTES_ACTIVA, 1.15, places=2)
        finally:
            config.ESCALA_FUENTES_ACTIVA = 1.15
            juego.fuentes.clear()
            juego.hud.limpiar_caches_texto()

    def test_campanas_carillon_ascendente_y_sin_traba(self):
        juego = Juego()
        juego.cargar_nivel(2)
        grabador = GrabadorAudio(juego.audio)
        juego.audio = grabador

        for idx in range(7):
            campana = juego.nivel.incensarios[idx % len(juego.nivel.incensarios)]
            campana.cooldown = 0.0
            juego._aplicar_rebote_campana(campana, por_ataque=False)

        campanas_sonadas = [n for n in grabador.efectos if n.startswith("campana_")]
        self.assertEqual(
            campanas_sonadas,
            ["campana_1", "campana_2", "campana_3", "campana_4", "campana_5", "campana_6", "campana_6"],
        )

        # Al expirar el temporizador del carillón reinicia en campana_1.
        juego.campanas_combo_timer = 0.0
        campana0 = juego.nivel.incensarios[0]
        campana0.cooldown = 0.0
        juego._aplicar_rebote_campana(campana0, por_ataque=False)
        self.assertEqual(grabador.efectos[-1], "campana_1")

    def test_hitbox_arana_18px_y_tolerancia_pisoton_dinamica(self):
        juego = Juego()
        juego.cargar_nivel(2)
        self.assertEqual(config.ARANA_ALTO, 18)
        self.assertTrue(juego.nivel.aranias)
        for arana in juego.nivel.aranias:
            self.assertEqual(arana.rect.height, 18)

        juego.jugador.vy = 200.0
        tol_60hz = juego._tolerancia_pisoton_frame(1.0 / 60.0)
        juego.jugador.vy = 680.0
        tol_caida_rapida = juego._tolerancia_pisoton_frame(1.0 / 20.0)
        self.assertGreaterEqual(tol_60hz, 14)
        self.assertGreater(tol_caida_rapida, tol_60hz)

    def test_enemigo_melee_ciclo_completo_y_dano_por_espada(self):
        juego = Juego()
        juego.cargar_nivel(2)
        self.assertGreaterEqual(len(juego.nivel.enemigos_melee), 2)

        caballero = EnemigoMelee(pygame.Rect(200, 200, 26, 36), 100, 320)
        jugador = Jugador(250, 204)
        jugador.vidas = 3

        # Entra en rango melee -> inicia aviso.
        caballero.actualizar(1 / 60, jugador)
        self.assertGreater(caballero.aviso_tiempo, 0.0)
        self.assertIsNone(caballero.rect_espada())

        # Agota el aviso -> ejecuta estocada con hitbox activa.
        caballero.actualizar(0.30, jugador)
        self.assertGreater(caballero.estocada_tiempo, 0.0)
        self.assertTrue(caballero.atacando)
        self.assertIsNotNone(caballero.rect_espada())

        # Agota la estocada -> entra en enfriamiento antes de volver a patrullar.
        caballero.actualizar(0.25, jugador)
        self.assertFalse(caballero.atacando)
        self.assertGreater(caballero.enfriamiento_tiempo, 0.0)
        self.assertIsNone(caballero.rect_espada())

    def test_farol_piloto_encendido_inscripciones_y_duda_salto_fe(self):
        farol = FarolCheckpoint(pygame.Rect(100, 100, config.TILE, config.TILE))
        self.assertFalse(farol.activo)
        farol.actualizar_dt(0.25)

        superficie = pygame.Surface((200, 200), pygame.SRCALPHA)
        farol.dibujar(superficie, Camara(), tiempo=0.5)

        jugador = Jugador(104, 104)
        self.assertTrue(farol.actualizar(jugador))
        self.assertTrue(farol.activo)
        self.assertGreater(farol.tiempo_encendido, 0.0)
        farol.actualizar_dt(0.70)
        self.assertEqual(farol.tiempo_encendido, 0.0)

        # Inscripciones MK1 en el Osario vertical + pista de duda en el abismo ciego.
        juego = Juego()
        juego.cargar_nivel(2)
        mensajes_faroles = [juego._inscripcion_farol(cp) for cp in juego.nivel.checkpoints]
        self.assertTrue(all(mensajes_faroles))
        self.assertIn("NO BUSQUES PUENTE: EN ALGÚN MOMENTO HAY QUE CREER.", mensajes_faroles)

        # Posicionar al jugador quieto al borde del Salto de Fe (cols 296..311, fila <= 16).
        juego.jugador.rect.center = (304 * config.TILE + 12, 14 * config.TILE)
        juego.jugador.x = float(juego.jugador.rect.x)
        juego.jugador.y = float(juego.jugador.rect.y)
        juego.jugador.en_suelo = True
        juego.jugador.vx = 0.0
        juego._actualizar_duda_salto_de_fe(2.1)
        self.assertTrue(juego.pista_fe_mostrada)
        self.assertIn(config.PISTA_SALTO_DE_FE_DUDA, juego.hud.mensajes.texto)

    def test_arena_custodio_compuertas_criptas_y_musica_f3(self):
        juego = Juego()
        grabador = GrabadorAudio(juego.audio)
        juego.audio = grabador
        juego.cargar_nivel(2)

        self.assertGreaterEqual(len(juego.nivel.compuertas_arena), 2)
        self.assertGreaterEqual(len(juego.nivel.bloques_cripta), 20)
        jefe = juego.nivel.jefes[0]

        # Al entrar en la arena se cierran ambas compuertas.
        juego.jugador.rect.center = (jefe.rect.centerx + 48, jefe.rect.bottom - 10)
        juego.jugador.x = float(juego.jugador.rect.x)
        juego.jugador.y = float(juego.jugador.rect.y)
        juego.actualizar_jefe(1 / 60)
        self.assertTrue(all(c.cerrada for c in juego.nivel.compuertas_arena))

        # Al pasar a Fase 3 suena custodio_f3 y un salto aplastante rompe criptas bajo sus pies.
        jefe.vida = 1
        jefe.fase = 2
        jefe.estado = "recuperacion"
        jefe.vulnerable = True
        juego.jugador.rango_ataque_mejorado = True
        self.assertTrue(juego.dañar_jefe_pisaton())
        self.assertEqual(jefe.fase, 3)

        juego.actualizar_jefe(1 / 60)
        self.assertTrue(any(m[0] == "custodio_f3" for m in grabador.musicas))

        # Posicionar al jugador saltando fuera de las ondas mientras el Custodio cae sobre las criptas.
        juego.jugador.rect.center = (jefe.rect.centerx - 140, jefe.rect.top - 96)
        juego.jugador.x = float(juego.jugador.rect.x)
        juego.jugador.y = float(juego.jugador.rect.y)

        jefe.temporizador = 0.0
        solidos_antes = len(juego.nivel.solidos_actuales())
        juego.actualizar_jefe(1 / 60)
        jefe.estado = "salto_smb3"
        jefe.vy = 220.0
        jefe.y = jefe.y_suelo - 1.0
        juego.actualizar_jefe(1 / 60)
        rotos = [b for b in juego.nivel.bloques_cripta if b.roto]
        self.assertGreater(len(rotos), 0)
        self.assertEqual(len(juego.nivel.solidos_actuales()), solidos_antes - len(rotos))

        # El reinicio completo de arena vuelve a dejar las compuertas abiertas y criptas intactas.
        juego._reiniciar_arena_y_mecanismos()
        self.assertTrue(all(not c.cerrada for c in juego.nivel.compuertas_arena))
        self.assertTrue(all(not b.roto for b in juego.nivel.bloques_cripta))

    def test_musica_synthlab_ogg_disponible(self):
        carpeta = RAIZ / "assets" / "audio" / "musica"
        pistas = (
            "titulo",
            "camposanto",
            "cripta",
            "osario",
            "carcelero",
            "custodio_f1",
            "custodio_f2",
            "custodio_f3",
            "creditos",
            "victoria",
            "derrota",
        )
        for pista in pistas:
            ruta = carpeta / f"{pista}.ogg"
            self.assertTrue(ruta.exists(), f"Falta pista {ruta}")
            self.assertGreater(ruta.stat().st_size, 4096)

    def test_pausa_incluye_opciones_y_regresa_a_pausa(self):
        juego = Juego()
        juego.cargar_nivel(0)
        juego.estado = "pausa"
        juego.pausa_opcion = 1  # OPCIONES
        juego._manejar_tecla_pausa(pygame.K_RETURN)
        self.assertEqual(juego.estado, "configuracion")
        self.assertEqual(juego.origen_configuracion, "pausa")

        juego._cerrar_configuracion()
        self.assertEqual(juego.estado, "pausa")

    def test_campanas_reinicio_rapido_y_cinco_campanas_en_arena_minijefe(self):
        import niveles

        self.assertLessEqual(config.INCENSARIO_COOLDOWN, 0.35)
        juego = Juego()
        juego.cargar_nivel(2)
        campana = juego.nivel.incensarios[0]
        juego._aplicar_rebote_campana(campana)
        self.assertAlmostEqual(juego.campanas_combo_timer, 1.05, places=2)

        # Verificar que la arena del Carcelero (piso superior, cols 114..150) cuenta con 5 campanas
        filas = niveles.NIVEL_3_VERTICAL.strip().splitlines()
        campanas_arena = [
            (col, fila)
            for fila, linea in enumerate(filas)
            for col, ch in enumerate(linea)
            if ch == "I" and fila < 18 and 114 <= col <= 150
        ]
        self.assertEqual(len(campanas_arena), 5)

    def test_muro_movil_compuerta_emergiendo_y_choque_real_minijefe(self):
        from entidades import MiniJefe, MuroMovilCompuerta

        muro = MuroMovilCompuerta(132 * config.TILE, 14 * config.TILE, alto_max=3 * config.TILE)
        self.assertEqual(muro.estado, "oculto")
        self.assertFalse(muro.es_solido())

        muro.activar()
        self.assertEqual(muro.estado, "aviso")
        for _ in range(40):
            muro.actualizar(1 / 60)
        self.assertIn(muro.estado, ("emergiendo", "armado"))
        self.assertTrue(muro.es_solido())
        self.assertGreater(muro.rect.height, config.TILE)
        self.assertEqual(muro.rect.bottom, 14 * config.TILE)

        # MiniJefe que embiste en vacío con muros provistos no queda vulnerable sino en recuperación
        jugador_obj = Jugador(116 * config.TILE, 13 * config.TILE)
        mj_vacio = MiniJefe(
            pygame.Rect(120 * config.TILE, 14 * config.TILE - 58, 36, 58),
            114 * config.TILE,
            150 * config.TILE,
        )
        mj_vacio.estado = "ataque"
        mj_vacio.temporizador = 0.01
        mj_vacio.vx = 280.0
        mj_vacio.actualizar(0.02, jugador_obj, muros=[])
        self.assertEqual(mj_vacio.estado, "recuperacion")
        self.assertFalse(mj_vacio.vulnerable)

        # MiniJefe que choca contra el MuroMovilCompuerta queda aturdido y vulnerable
        jugador_der = Jugador(140 * config.TILE, 13 * config.TILE)
        mj_choque = MiniJefe(
            pygame.Rect(131 * config.TILE, 14 * config.TILE - 58, 36, 58),
            114 * config.TILE,
            150 * config.TILE,
        )
        mj_choque.estado = "ataque"
        mj_choque.temporizador = 0.8
        mj_choque.vx = 290.0
        mj_choque.direccion = 1
        mj_choque.actualizar(0.15, jugador_der, muros=[muro])
        self.assertTrue(mj_choque.choque_recien)
        self.assertEqual(mj_choque.estado, "cansado")
        self.assertTrue(mj_choque.vulnerable)
        self.assertGreater(muro.tiempo_temblor, 0.0)
        self.assertTrue(muro.usado_ciclo)
        self.assertGreater(muro.enfriamiento, 5.0)
        self.assertFalse(muro.puede_activarse())

        # Mientras el jugador está fuera de la arena (ej. col 110), el Carcelero se mantiene en vigilia al fondo
        mj_vigilia = MiniJefe(
            pygame.Rect(142 * config.TILE, 14 * config.TILE - 58, 36, 58),
            114 * config.TILE,
            150 * config.TILE,
        )
        jugador_fuera = Jugador(110 * config.TILE, 9 * config.TILE)
        for _ in range(120):
            mj_vigilia.actualizar(1 / 60, jugador_fuera, muros=[muro])
        self.assertFalse(mj_vigilia.activado)
        self.assertGreaterEqual(mj_vigilia.rect.x, 134 * config.TILE)

    def test_dash_sonido_y_reinicio_musica_tras_derrota_con_checkpoint(self):
        juego = Juego()
        grabador = GrabadorAudio(juego.audio)
        juego.audio = grabador
        juego.cargar_nivel(1)
        self.assertTrue(juego.jugador.tiene_dash)

        # Al pedir dash antes de actualizar(dt), el sonido "dash" debe reproducirse en ese mismo frame
        grabador.efectos.clear()
        self.assertTrue(juego.jugador.pedir_dash())
        juego.actualizar(1 / 60)
        self.assertIn("dash", grabador.efectos)

        # Al perder todas las vidas con un Farol activado y reintentar rápido, la música del nivel vuelve en bucle
        juego.punto_reintento = (87 * config.TILE, 13 * config.TILE - 4)
        juego.jugador.vidas = 1
        juego.perder_vida(ignorar_invulnerabilidad=True, causa="Prueba derrota")
        self.assertEqual(juego.estado, "derrota")
        self.assertEqual(grabador.musicas[-1][0], "derrota")
        self.assertFalse(grabador.musicas[-1][1])

        juego._manejar_tecla_enter_estado()
        self.assertEqual(juego.estado, "jugando")
        self.assertEqual(grabador.musicas[-1][0], juego.nivel.tema)
        self.assertTrue(grabador.musicas[-1][1])

    def test_saltos_post_minijefe_alcanzables_sin_enemigos(self):
        import niveles
        from tools.validar_niveles import _alcanzable

        filas = niveles.NIVEL_3_VERTICAL.strip().splitlines()
        paradas_piso_superior = [
            (150, 13),  # Salida de la arena del Carcelero
            (182, 11),  # Salida de la Torre de la Guadaña
            (210, 11),  # Terraza previa al ascensor VV
            (237, 12),  # Farol intermedio del bastión
            (257, 12),  # Plataforma central post-sarcófago
            (303, 13),  # Mirador del Salto de Fe
        ]
        for origen, destino in zip(paradas_piso_superior, paradas_piso_superior[1:]):
            self.assertTrue(
                _alcanzable(
                    filas, {"dash"}, inicio=origen, meta=destino, usar_k=False, usar_b=False
                )[0],
                f"Tramo {origen} -> {destino} inalcanzable sin enemigos (con dash)",
            )
            self.assertTrue(
                _alcanzable(
                    filas, set(), inicio=origen, meta=destino, usar_k=False, usar_b=False
                )[0],
                f"Tramo {origen} -> {destino} inalcanzable sin enemigos (sin dash)",
            )

    def test_verticalidad_nivel3_sin_solapamiento_y_custodio_f2_f3(self):
        import niveles

        self.assertEqual(niveles.NIVELES_VERTICALES[0]["nombre"], "El Osario")

        filas = niveles.NIVEL_3_VERTICAL.strip().splitlines()
        pos_v = [(c, r) for r, l in enumerate(filas) for c, ch in enumerate(l) if ch == "V"]
        pos_i = [(c, r) for r, l in enumerate(filas) for c, ch in enumerate(l) if ch == "I"]

        # 1) Ninguna campana 'I' se solapa con el recorrido vertical (±3 filas) de una plataforma 'V'
        for ci, ri in pos_i:
            for cv, rv in pos_v:
                self.assertFalse(
                    abs(ci - cv) <= 1 and abs(ri - rv) <= 3,
                    f"Campana I({ci},{ri}) solapada con plataforma vertical V({cv},{rv})",
                )

        # 2) El Nivel 3 posee plataformas y desafíos en las bóvedas altas de ambos pisos (filas 5..7 y 22..25)
        solidos_altos_p0 = sum(1 for r in (5, 6, 7) for ch in filas[r] if ch in ("#", "~"))
        solidos_altos_p1 = sum(1 for r in (22, 23, 24, 25) for ch in filas[r] if ch in ("#", "~"))
        self.assertGreaterEqual(solidos_altos_p0, 35)
        self.assertGreaterEqual(solidos_altos_p1, 35)

        # 3) Claridad de textos en Fase 2 (sin '(X)' ambiguo y con aviso de guardia cerrada)
        juego = Juego()
        juego.cargar_nivel(2)
        jefe = juego.jefe
        jefe.vida = 4
        jefe.fase = 1
        jefe.golpes_fase = 2
        jefe.estado = "recuperacion"
        jefe.vulnerable = True
        juego.jugador.rango_ataque_mejorado = True
        self.assertTrue(juego.dañar_jefe_pala())
        self.assertEqual(jefe.fase, 2)
        self.assertNotIn("(X)", juego.hud.mensajes.texto)
        self.assertIn("[J/Z]", juego.hud.mensajes.texto)

        # Golpear en Fase 2 con Guadaña mientras la guardia está cerrada explica que debe esperar a que termine su ataque
        jefe.estado = "espera"
        jefe.vulnerable = False
        self.assertFalse(juego.dañar_jefe_pala())
        self.assertIn("GUARDIA CERRADA", juego.hud.mensajes.texto)

        # 4) Fase 3: 4 capas de '=' (filas 30..33), cada salto rompe con precisión 1 sola capa (1-2 bloques)
        filas_cripta = {b.rect.y // config.TILE for b in juego.nivel.bloques_cripta}
        self.assertEqual(filas_cripta, {30, 31, 32, 33})

        jefe.fase = 3
        for capa_esperada in (30, 31, 32):
            jefe.estado = "salto_smb3"
            jefe.quiebre_usado_en_salto = False
            jefe.vy = 260.0
            jefe.y = jefe.y_suelo - 2.0
            for _ in range(25):
                juego.actualizar_jefe(1 / 60)
                if jefe.estado == "aterrizaje_smb3":
                    break
            self.assertEqual(jefe.estado, "aterrizaje_smb3")
            rotos_en_capa = [b for b in juego.nivel.bloques_cripta if b.roto and (b.rect.y // config.TILE) == capa_esperada]
            self.assertGreaterEqual(len(rotos_en_capa), 1)
            self.assertLessEqual(len(rotos_en_capa), 2)
            # La capa siguiente aún sigue intacta tras ese salto
            rotos_capa_sig = [b for b in juego.nivel.bloques_cripta if b.roto and (b.rect.y // config.TILE) == capa_esperada + 1]
            self.assertEqual(len(rotos_capa_sig), 0)

        # En el 3er aterrizaje (apoyado sobre la 4ta capa, fila 33), un Quiebre Sísmico rompe la 4ta capa y cae al abismo
        self.assertTrue(juego.dañar_jefe_pala())
        self.assertEqual(jefe.estado, "cayendo_abismo")

        # 5) 2 Continues al perder todas las vidas (reinicia el nivel actual desde 0) y luego empieza desde Nivel 1 (No tutorial)
        juego.seleccionar_nivel(2)
        self.assertEqual(juego.continues, 2)
        for cont_esperado in (1, 0):
            juego.punto_reintento = (109 * config.TILE, 9 * config.TILE)
            juego.jugador.vidas = 1
            juego.perder_vida(ignorar_invulnerabilidad=True)
            self.assertEqual(juego.estado, "derrota")
            juego._manejar_tecla_enter_estado()
            self.assertEqual(juego.estado, "jugando")
            self.assertEqual(juego.nivel_indice, 2)
            self.assertEqual(juego.continues, cont_esperado)
            self.assertIsNone(juego.punto_reintento)

        # Al perder todas las vidas sin continues (0), empieza desde el Nivel 1 (índice 0, El Camposanto, no el tutorial)
        juego.jugador.vidas = 1
        juego.perder_vida(ignorar_invulnerabilidad=True)
        self.assertEqual(juego.estado, "derrota")
        juego._manejar_tecla_enter_estado()
        self.assertEqual(juego.estado, "jugando")
        self.assertFalse(juego.es_tutorial)
        self.assertEqual(juego.nivel_indice, 0)
        self.assertEqual(juego.continues, 2)

    def test_faroles_no_duplicados_y_alcance_real_con_embate_custodio(self):
        import niveles
        import tools.validar_niveles as V

        # 1) Ningún par de faroles 'F' a <= 20 columnas en el mismo piso en todos los niveles jugables,
        # y regla espacial I6 limpia (0 flotantes, 0 choques M/V/C, 0 pegotes ni aglomeraciones).
        specs_niveles = (
            ("NIVEL_TUTORIAL", (), False),
            ("NIVEL_1", (), True),
            ("NIVEL_2", ("dash",), True),
            ("NIVEL_3_VERTICAL", ("dash", "pala"), True),
        )
        for nombre, habs, es_prin in specs_niveles:
            mapa_str = getattr(niveles, nombre)
            filas = mapa_str.strip("\n").splitlines()
            faroles = sorted((c, r) for r, l in enumerate(filas) for c, ch in enumerate(l) if ch == "F")
            for (c1, r1), (c2, r2) in zip(faroles, faroles[1:]):
                mismo_piso = (r1 // 18) == (r2 // 18)
                if mismo_piso:
                    self.assertGreater(c2 - c1, 20, f"Faroles cercanos en {nombre}: {(c1, r1)} y {(c2, r2)}")
            res_n = V.validar(mapa_str, nombre, habilidades=habs, principal=es_prin)
            self.assertTrue(res_n.ok(), f"Errores en {nombre}: {res_n.errores}")
            self.assertIn("I6: coherencia espacial y decoraciones limpias", res_n.info)

        # 2) El Osario pasa validar_niveles sin plataformas huérfanas (V5 = 0) y el rebote real es 1 fila
        self.assertEqual(V.JH_REBOTE, 1)
        res = V.validar(niveles.NIVEL_3_VERTICAL, "osario", habilidades=("dash", "pala"), principal=True)
        self.assertTrue(res.ok(), f"Errores en Osario: {res.errores}")
        self.assertIn("V5: 0 plataformas huérfanas con física real", res.info)

        # Si se planta una repisa huérfana 2 filas sobre una campana en zona alta, V5 falla;
        # y si queda una gárgola flotando en el aire, I6 falla con ERROR.
        filas_tmp = [list(f) for f in niveles.NIVEL_3_VERTICAL.strip("\n").splitlines()]
        filas_tmp[12][10] = "I"
        for dc in range(3):
            filas_tmp[10][9 + dc] = "#"
        filas_tmp[4][180] = "g"
        res_huerfana = V.validar("\n".join("".join(f) for f in filas_tmp), "osario_huerfana", habilidades=("dash", "pala"), principal=True)
        self.assertFalse(res_huerfana.ok())
        self.assertTrue(any("fila 9" in e and "V5:" in e for e in res_huerfana.errores))
        self.assertTrue(any("I6:" in e and "flotando" in e for e in res_huerfana.errores))

        # 3) Simulación real con Pygame: subida al tramo final superior y Cadena de Fe del Calvario
        T = config.TILE
        juego = Juego()

        def simular(x0_col, y0_row, dir_x, modo, check, df_set, hold=60):
            for df in df_set:
                juego.cargar_nivel(2)
                jug = juego.jugador
                jug.rect.topleft = (x0_col * T + 4, y0_row * T - config.JUGADOR_ALTO)
                jug.x, jug.y = float(jug.rect.x), float(jug.rect.y)
                jug.en_suelo = modo == "salto"
                teclas = {k: False for k in (pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE)}
                teclas[pygame.K_d if dir_x > 0 else pygame.K_a] = True
                if modo == "salto":
                    teclas[pygame.K_SPACE] = True
                    jug.manteniendo_salto = True
                    jug.pedir_salto()
                else:
                    camp = min(juego.nivel.incensarios, key=lambda c: abs(c.rect.centerx - (x0_col * T + T // 2)) + abs(c.rect.centery - y0_row * T))
                    jug.rect.midbottom = (camp.rect.centerx, camp.rect.top + 4)
                    jug.x, jug.y = float(jug.rect.x), float(jug.rect.y)
                    jug.vy = 200.0
                    juego.actualizar_incensarios(1 / 60)
                for frame in range(90):
                    if modo == "salto" and frame == hold:
                        jug.soltar_salto()
                        teclas[pygame.K_SPACE] = False
                    if frame == df and df > 0:
                        jug.pedir_dash()
                    juego.actualizar_plataformas(1 / 60)
                    juego.actualizar_losas(1 / 60)
                    jug.actualizar(1 / 60, teclas, juego.nivel.solidos_actuales())
                    juego.actualizar_incensarios(1 / 60)
                    if check(jug, juego):
                        return True
            return False

        # Subida real al nivel alto del tramo final superior y puente de cierre (P0)
        self.assertTrue(
            simular(222, 9, 1, "salto", lambda j, g: j.en_suelo and 225 * T <= j.rect.centerx <= 231 * T and j.rect.bottom <= 6 * T + 2, range(0, 18))
        )
        self.assertTrue(
            simular(282, 7, 1, "campana", lambda j, g: j.en_suelo and 285 * T <= j.rect.centerx <= 287 * T and j.rect.bottom <= 6 * T + 2, range(0, 18))
        )
        # El Calvario de las Campanas endurecido completo con Pygame real:
        # T1: I(219,28)->214..215(27)->I(209,27)->I(203,28)->T2: ~~(197..198,29)->I(191,28)
        self.assertTrue(simular(219, 28, -1, "campana", lambda j, g: j.en_suelo and 214 * T <= j.rect.centerx <= 216 * T and j.rect.bottom <= 27 * T + 2, range(4, 14)))
        self.assertTrue(simular(209, 27, -1, "campana", lambda j, g: any(c.cooldown > 0 and c.rect.x // T == 203 for c in g.nivel.incensarios), range(1, 8)))
        self.assertTrue(simular(197, 29, -1, "salto", lambda j, g: any(c.cooldown > 0 and c.rect.x // T == 191 for c in g.nivel.incensarios), range(0, 10)))
        # T4 Cadena de Fe Mixta (4 campanas con Dash): I(169,26)->I(163,27)->I(157,28)->I(152,28)->Antesala 142..151(30)
        self.assertTrue(simular(169, 26, -1, "campana", lambda j, g: any(c.cooldown > 0 and c.rect.x // T == 163 for c in g.nivel.incensarios), range(1, 8)))
        self.assertTrue(simular(163, 27, -1, "campana", lambda j, g: any(c.cooldown > 0 and c.rect.x // T == 157 for c in g.nivel.incensarios), range(1, 8)))
        self.assertTrue(simular(157, 28, -1, "campana", lambda j, g: any(c.cooldown > 0 and c.rect.x // T == 152 for c in g.nivel.incensarios), range(1, 8)))
        self.assertTrue(simular(152, 28, -1, "campana", lambda j, g: j.en_suelo and 142 * T <= j.rect.centerx <= 152 * T and j.rect.bottom <= 30 * T + 2, range(0, 8)))

        # 4) Embate Ascendente del Custodio en Fase 1 anti-campeo sobre campanas
        juego.cargar_nivel(2)
        jefe = juego.jefe
        jefe.fase = 1
        jefe.estado = "espera"
        campana_arena = next(c for c in juego.nivel.incensarios if 104 * T <= c.rect.centerx <= 129 * T and c.rect.centery >= 18 * T)
        jefe.x = float(campana_arena.rect.centerx - jefe.rect.width // 2)
        jefe.rect.x = round(jefe.x)
        juego.jugador.vidas = 3
        juego.jugador.invulnerable = 0.0

        # Mantener al jugador encima (sobre la campana de la arena) durante >0.60 s -> telegrafía embate
        juego.jugador.vidas = 1
        juego.jugador.rect.midbottom = (campana_arena.rect.centerx, campana_arena.rect.top)
        juego.jugador.x, juego.jugador.y = float(juego.jugador.rect.x), float(juego.jugador.rect.y)
        for _ in range(42):  # 0.70 s > 0.60 s
            juego.jugador.rect.midbottom = (campana_arena.rect.centerx, campana_arena.rect.top)
            juego.jugador.vy = 0.0
            juego.actualizar_jefe(1 / 60)
            if jefe.estado == "telegrafia_embate":
                break
        self.assertEqual(jefe.estado, "telegrafia_embate")

        # Si logra esquivar hacia el costado antes del golpe, embate silencia la campana y luego queda vulnerable
        juego.jugador.rect.centerx = campana_arena.rect.centerx + 120
        juego.jugador.x = float(juego.jugador.rect.x)
        for _ in range(35):
            juego.actualizar_jefe(1 / 60)
            if jefe.estado == "embate":
                break
        self.assertEqual(jefe.estado, "embate")
        self.assertIsNotNone(jefe.rect_embate())
        self.assertGreaterEqual(campana_arena.cooldown, 1.0)
        for _ in range(20):
            juego.actualizar_jefe(1 / 60)
            if jefe.estado == "recuperacion":
                break
        self.assertEqual(jefe.estado, "recuperacion")
        self.assertTrue(jefe.vulnerable)

        # Y si permanece arriba sobre la campana durante el embate, recibe el daño vertical
        jefe.estado = "telegrafia_embate"
        jefe.temporizador = 0.02
        jefe.vulnerable = False
        juego.jugador.rect.midbottom = (campana_arena.rect.centerx, campana_arena.rect.top)
        juego.jugador.x, juego.jugador.y = float(juego.jugador.rect.x), float(juego.jugador.rect.y)
        for _ in range(5):
            if juego.actualizar_jefe(1 / 60):
                break
        self.assertEqual(juego.jugador.vidas, 0)
        self.assertIn("Embate ascendente", juego.causa_muerte)


if __name__ == "__main__":
    unittest.main()
