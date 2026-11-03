<?xml version="1.0" encoding="UTF-8"?>
<argon_sensory_overhaul project="IN CRYPTA" version="2.0" target_branch="feat/menu-clean-procedural-chimes">
  <metadata>
    <purpose>
      1. Restaurar los chimes pentatónicos escalonados al recoger gemas/almas (investigación git + fix en audio.py).
      2. Eliminar todo el "slop" visual y textual de los menús (Título, Menú Principal, Selección de Nivel, Configuración, Pausa y Créditos), dejando una UI gótica limpia, directa y minimalista.
      3. Potenciar el arte procedural en las distintas áreas (Camposanto, Cripta, Osario) mejorando fondos, tiles, enemigos y efectos visuales/sonoros.
      4. Consolidar la bifurcación: Calidad Alta (Desktop Nativo Full Procedural + Bloom + Penumbra) vs Calidad Baja (Web/Pygbag &amp; Sony Vaio 60 FPS sin SRCALPHA de pantalla completa).
    </purpose>
    <target_engine>Pygame / Pygame-ce + Pygbag (emscripten)</target_engine>
    <execution_environment>agy-cli con soporte de sub-agentes y modo /goal</execution_environment>
  </metadata>

  <hard_guardrails>
    <rule id="G1" severity="CRITICAL">PROHIBIDO modificar constantes físicas en config.py (GRAVEDAD, SALTO, VELOCIDAD, MAX_CAIDA, COYOTE_TIME, JUMP_BUFFER, CORTE_SALTO, DASH_VELOCIDAD, DASH_DURACION, DASH_COOLDOWN, ATAQUE_DURACION, ATAQUE_COOLDOWN, ATAQUE_ALCANCE, ATAQUE_ALCANCE_MEJORADO, TOLERANCIA_PISOTON).</rule>
    <rule id="G2" severity="CRITICAL">PROHIBIDO alterar el tamaño, posición o lógica de colisión de self.rect en Jugador, Enemigo, EnemigoMelee, Custodio, MiniJefe, Cuervo, Polilla, Araña o Nivel.</rule>
    <rule id="G3" severity="CRITICAL">PROHIBIDO alterar los mapas ASCII en niveles.py o la lógica de parseo de símbolos en nivel.py.</rule>
    <rule id="G4" severity="CRITICAL">En esta fase base, mantener compatibilidad 100% estándar con pytest tests/ (51/51 tests en verde) y HudLayout.construir().solapamientos() == [].</rule>
  </hard_guardrails>

  <!-- ===================================================================== -->
  <!-- HALLAZGO DE AUDITORÍA: POR QUÉ SE PERDIERON LOS CHIMES ESCALONADOS    -->
  <!-- ===================================================================== -->
  <git_investigation_chimes>
    <root_cause>
      En `audio.py` (líneas 235-248), cuando se agregaron los archivos `.wav` en disco (`alma_ref.wav`), el bucle inicial carga `self.sonidos["alma"] = snd_disco`.
      Inmediatamente después, el condicional `if "alma" in self.sonidos:` ejecuta:
        `for idx in range(1, 7): self.sonidos[f"alma_{idx}"] = self.sonidos["alma"]`
      Esto SOBRESCRIBE las 6 notas escalonadas con el mismo archivo plano `alma_ref.wav`, impidiendo que se ejecute el bloque `else:` que sintetizaba la escala pentatónica cristalina `[523, 587, 659, 784, 880, 1046]` Hz.
      Además, `self.variaciones["alma"]` interceptaba llamadas genéricas.
    </root_cause>
    <solution>
      1. El sub-agente debe ejecutar `git log -S "notas_almas" -p -- audio.py` o `git log -L 230,255:audio.py` para documentar el commit exacto donde se introdujo `alma_ref`.
      2. En `audio.py`, SIEMPRE sintetizar proceduralmente `alma_1` a `alma_6` usando síntesis de campana cristalina/chime armónico en la escala `[523.25, 587.33, 659.25, 783.99, 880.00, 1046.50]` Hz (Do5, Re5, Mi5, Sol5, La5, Do6) con armónicos de quinta y octava brillantes, ignorando `alma_ref.wav` para la secuencia escalonada `alma_1..alma_6`.
      3. En `juego.py` (`actualizar_almas`), ampliar `self.almas_combo_timer = 2.2` segundos para que el jugador escuche claramente la progresión ascendente de los 6 chimes al recoger filas o arcos de gemas/almas.
    </solution>
  </git_investigation_chimes>

  <file_specifications>
    <!-- ================================================================= -->
    <!-- 1. audio.py — Restauración de Chimes Pentatónicos Escalonados     -->
    <!-- ================================================================= -->
    <file path="audio.py" action="restore_escalated_chimes">
      <description>Restaurar los chimes armónicos escalonados procedurales (alma_1 a alma_6) para que nunca sean pisados por alma_ref.wav y suenen como gemas cristalinas en ascenso.</description>
      <code_snippet><![CDATA[
        # 6. Chimes escalonados de Almas / Gemas (Escala Pentatónica Mayor Cristalina: C5, D5, E5, G5, A5, C6)
        # SIEMPRE procedural para conservar el ascenso armónico al encadenar recolecciones.
        notas_almas = [523.25, 587.33, 659.25, 783.99, 880.00, 1046.50]
        for idx, nota in enumerate(notas_almas, 1):
            # Síntesis de chime cristalino: fundamental pura + octava brillante + campana FM + destello armónico
            capas_chime = [
                ("seno", nota, 0, 0.65, None),
                ("seno", nota * 2.0, 15, 0.35, None),
                ("fm", nota * 1.5, 0, 0.28, (nota * 3.0, 0.9)),
                ("seno", nota * 3.0, 40, 0.15, None),
            ]
            snd_alma = sintetizar_sfx(
                0.34,
                capas_chime,
                adsr=(0.004, 0.07, 0.45, 0.266),
                volumen=0.22,
            )
            self.sonidos[f"alma_{idx}"] = snd_alma
        self.sonidos["alma"] = self.sonidos["alma_1"]
        # Eliminar 'alma' de self.variaciones para que reproducir('alma_X') respete siempre el peldaño exacto de la escala
        self.variaciones.pop("alma", None)
]]></code_snippet>
    </file>

    <!-- ================================================================= -->
    <!-- 2. config.py — Bifurcación Desktop (PROC Alta) vs Web/Vaio (NES)  -->
    <!-- ================================================================= -->
    <file path="config.py" action="update_quality_profiles">
      <description>Asegurar que en Web (ES_WEB) el perfil por defecto sea Calidad Baja (2 = NES 8-Bit 60 FPS sin penumbra) y en Desktop sea Calidad Alta (0 = PROC Gótico Completo).</description>
      <code_snippet><![CDATA[
PERFIL_WEB_SHADER = 2   # 2: Puro (sin bloom ni scanlines CRT en Web)
PERFIL_WEB_CALIDAD = 2  # 2: Baja en Web por defecto (60 FPS garantizados en navegador y Vaio)
CALIDAD_GLOBAL_ACTIVA = PERFIL_WEB_CALIDAD if ES_WEB else 0
]]></code_snippet>
    </file>

    <!-- ================================================================= -->
    <!-- 3. juego.py — Limpieza Total de Slop en Menús y Fondos Procedural -->
    <!-- ================================================================= -->
    <file path="juego.py" action="clean_menu_slop_and_upgrade_procedural_backgrounds">
      <description>
        Eliminar todo el texto redundante, subtítulos kilométricos, explicaciones de cátedra ("UNAHUR", "Matriz MDA", "Apunte UI/UX", "80 cols", descripciones redundantes de dos líneas por botón) en:
        - dibujar_titulo()
        - dibujar_menu_principal()
        - dibujar_seleccion_nivel()
        - dibujar_configuracion()
        - dibujar_creditos()
        - dibujar_menu_pausa()
        Reemplazarlos por una interfaz gótica minimalista, centrada, respirada y profesional, con un diorama procedural vivo de fondo.
      </description>
      <code_snippet><![CDATA[
    # --- Función dibujar_titulo (Minimalista y Atmosférica, Cero Slop) --- #
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
        self.dibujar_texto("PRESIONÁ [ENTER] PARA ENTRAR", 0, py + 225, 20, col_prompt, centrado=True, sombra=True)
        self.dibujar_texto("[ESC] Salir", 0, py + ph - 28, 13, HUD_MUTED, centrado=True)

    # --- Función dibujar_menu_principal (Limpio, Directo y Gótico) --- #
    def dibujar_menu_principal(self):
        self.dibujar_fondo(self.pantalla)
        if getattr(self, "config_calidad_idx", 0) != 2:
            self.pantalla.blit(self.vineta, (0, 0))

        pw, ph = 520, 430
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph, color_fondo=(12, 10, 18, 232))

        self.dibujar_texto(TITULO, 0, py + 36, 54, HUD_ORO, centrado=True, sombra=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 130), (ANCHO // 2 - 110, py + 92), (ANCHO // 2 + 110, py + 92), 1)

        opciones = (
            "INICIAR CAMPAÑA",
            "SELECCIÓN DE CAPÍTULO",
            "CONFIGURACIÓN",
            "CRÉDITOS",
        )

        ancho_caja = 380
        alto_caja = 50
        x_caja = (ANCHO - ancho_caja) // 2
        y_base = py + 118

        for i, titulo_op in enumerate(opciones):
            y_caja = y_base + i * 64
            seleccionada = (i == self.menu_opcion)
            color_fondo = (34, 24, 46) if seleccionada else (16, 13, 22)
            color_borde = HUD_ORO if seleccionada else HUD_BORDE
            rect_op = pygame.Rect(x_caja, y_caja, ancho_caja, alto_caja)

            pygame.draw.rect(self.pantalla, color_fondo, rect_op, border_radius=6)
            pygame.draw.rect(self.pantalla, color_borde, rect_op, 2 if seleccionada else 1, border_radius=6)
            if seleccionada:
                pygame.draw.rect(self.pantalla, HUD_ORO, (x_caja, y_caja + 8, 4, alto_caja - 16), border_radius=2)

            prefijo = "▸  " if seleccionada else ""
            color_txt = HUD_ORO if seleccionada else HUD_TEXTO
            self.dibujar_texto(prefijo + titulo_op, 0, y_caja + 25, 19, color_txt, centrado=True, sombra=seleccionada)

        self.dibujar_texto("[↑/↓] Navegar · [ENTER] Seleccionar · [ESC] Atrás", 0, py + ph - 26, 13, HUD_MUTED, centrado=True)

    # --- Función dibujar_seleccion_nivel (Capítulos Limpios sin Slop Técnico) --- #
    def dibujar_seleccion_nivel(self):
        self.dibujar_fondo(self.pantalla)
        if getattr(self, "config_calidad_idx", 0) != 2:
            self.pantalla.blit(self.vineta, (0, 0))

        pw, ph = 640, 490
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph, color_fondo=(12, 10, 18, 235))

        self.dibujar_texto("SELECCIÓN DE CAPÍTULO", 0, py + 32, 30, HUD_ORO, centrado=True, sombra=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 130), (ANCHO // 2 - 140, py + 66), (ANCHO // 2 + 140, py + 66), 1)

        datos_niveles = (
            ("0", "PRELUDIO · EL UMBRAL", "El ritual de iniciación del sepulturero"),
            ("I", "ACTO I · EL CAMPOSANTO", "Tumbas abiertas bajo la niebla lunar"),
            ("II", "ACTO II · LA CRIPTA", "Sillería húmeda y moradores en penumbra"),
            ("III", "ACTO III · EL OSARIO", "La cámara del Custodio y la Muerte Roja"),
            ("★", "SALAS DE PRUEBA", "Desafíos de precisión y combate"),
        )

        ancho_t = 540
        alto_t = 62
        x_t = (ANCHO - ancho_t) // 2
        y_base = py + 86

        for i, (insignia, titulo_n, sub_n) in enumerate(datos_niveles):
            y_t = y_base + i * 72
            sel = (i == self.nivel_seleccionado)
            rect_t = pygame.Rect(x_t, y_t, ancho_t, alto_t)
            pygame.draw.rect(self.pantalla, (32, 22, 42) if sel else (16, 13, 22), rect_t, border_radius=6)
            pygame.draw.rect(self.pantalla, HUD_ORO if sel else HUD_BORDE, rect_t, 2 if sel else 1, border_radius=6)
            if sel:
                pygame.draw.rect(self.pantalla, HUD_ORO, (x_t, y_t + 8, 4, alto_t - 16), border_radius=2)

            self.dibujar_texto(insignia, x_t + 22, y_t + 14, 26, HUD_ORO if sel else HUD_MUTED, sombra=sel)
            self.dibujar_texto(titulo_n, x_t + 68, y_t + 11, 17, HUD_ORO if sel else HUD_TEXTO, sombra=sel)
            self.dibujar_texto(sub_n, x_t + 68, y_t + 35, 13, CREMA if sel else HUD_MUTED)

        self.dibujar_texto("[↑/↓] Elegir · [ENTER] Jugar · [ESC] Volver", 0, py + ph - 26, 13, HUD_MUTED, centrado=True)

    # --- Función dibujar_configuracion (Solo Opciones Esenciales y Claras) --- #
    def dibujar_configuracion(self):
        self.dibujar_fondo(self.pantalla)
        if getattr(self, "config_calidad_idx", 0) != 2:
            self.pantalla.blit(self.vineta, (0, 0))

        pw, ph = 680, 510
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph, color_fondo=(12, 10, 18, 238))

        self.dibujar_texto("CONFIGURACIÓN", 0, py + 30, 32, HUD_ORO, centrado=True, sombra=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 120), (ANCHO // 2 - 140, py + 64), (ANCHO // 2 + 140, py + 64), 1)

        preset_activo = PRESETS_TECLADO[self.preset_teclado_idx]
        opciones = (
            ("CONTROLES", preset_activo["etiqueta"]),
            ("CALIDAD GRÁFICA", OPCIONES_CALIDAD[self.config_calidad_idx]),
            ("POST-PROCESADO", OPCIONES_SHADER[self.config_shader_idx]),
            ("INTERFAZ (HUD)", OPCIONES_HUD[self.config_hud_idx]),
            ("REDUCIR MOVIMIENTO", "Sí" if self.reducir_movimiento else "No"),
            ("SONIDO Y MÚSICA", "Activo" if getattr(self.audio, "activo", False) else "Silenciado"),
            ("VOLVER", ""),
        )

        ancho_c = 580
        alto_c = 44
        x_c = (ANCHO - ancho_c) // 2
        y_base = py + 82

        for i, (etiqueta, valor) in enumerate(opciones):
            y_c = y_base + i * 50
            sel = (i == self.config_opcion)
            rect_c = pygame.Rect(x_c, y_c, ancho_c, alto_c)
            pygame.draw.rect(self.pantalla, (32, 24, 44) if sel else (16, 13, 22), rect_c, border_radius=6)
            pygame.draw.rect(self.pantalla, HUD_ORO if sel else HUD_BORDE, rect_c, 2 if sel else 1, border_radius=6)

            prefijo = "▸ " if sel else "  "
            self.dibujar_texto(prefijo + etiqueta, x_c + 16, y_c + 11, 16, HUD_ORO if sel else HUD_TEXTO, sombra=sel)
            if valor:
                val_fmt = f"◂ {valor} ▸" if sel else valor
                self.dibujar_texto(val_fmt, x_c + ancho_c - 18, y_c + 11, 15, TURQUESA if sel else CREMA, derecha=True, sombra=sel)

        # Leyenda compacta del mapeo activo
        self.dibujar_texto(preset_activo["resumen"], 0, py + ph - 54, 13, CREMA, centrado=True)
        self.dibujar_texto("[↑/↓] Elegir · [←/→ / ENTER] Cambiar · [F4] Estilo Visual · [ESC] Volver", 0, py + ph - 24, 12, HUD_MUTED, centrado=True)

    # --- Función dibujar_creditos (Sin Slop de Apuntes de Cátedra) --- #
    def dibujar_creditos(self):
        self.dibujar_fondo(self.pantalla)
        if getattr(self, "config_calidad_idx", 0) != 2:
            self.pantalla.blit(self.vineta, (0, 0))

        pw, ph = 560, 380
        px = (ANCHO - pw) // 2
        py = (ALTO - ph) // 2
        self.dibujar_marco_heraldico(self.pantalla, px, py, pw, ph, color_fondo=(12, 10, 18, 238))

        self.dibujar_texto(TITULO, 0, py + 36, 44, HUD_ORO, centrado=True, sombra=True)
        self.dibujar_texto("DESARROLLO Y ARTE PROCEDURAL", 0, py + 84, 14, HUD_MUTED, centrado=True)
        pygame.draw.line(self.pantalla, (*HUD_ORO, 130), (ANCHO // 2 - 120, py + 110), (ANCHO // 2 + 120, py + 110), 1)

        for idx, nombre in enumerate(INTEGRANTES):
            self.dibujar_texto(nombre, 0, py + 148 + idx * 34, 19, HUD_TEXTO, centrado=True, sombra=True)

        self.dibujar_texto("Inspirado en la obra de Edgar Allan Poe", 0, py + 280, 14, CREMA, centrado=True)
        self.dibujar_texto("[ENTER / ESC] Volver al Menú", 0, py + ph - 30, 14, TURQUESA, centrado=True)
]]></code_snippet>
    </file>

    <!-- ================================================================= -->
    <!-- 4. nivel.py y juego.py — Procedurales Ricos por Área + 3 Calidades-->
    <!-- ================================================================= -->
    <file path="nivel.py" action="enrich_procedural_biomes_and_respect_quality">
      <description>
        Asegurar que cuando el estilo resuelto sea "PROC" (Calidad Alta) o "SNES" (Calidad Media), cada área tenga elementos procedurales distintivos deterministas (usando coordenadas x, y como semilla sin random por frame):
        - Camposanto: Rejas de hierro forjado quebradas en el borde de tierra, raíces entrelazadas, musgo esmeralda oscuro y lápidas inclinadas.
        - Cripta: Arcos ojivales grabados en los bloques de mampostería, estalactitas de salitre, argollas de hierro y reflejo húmedo azulado en el Walkable Edge Cue.
        - Osario: Estratificación de fémures y cráneos incrustados en los muros, vetas carmesí y candelabros de hueso.
        - En Calidad Baja ("NES", índice 2): Renderizado ortogonal directo de 8-bits sin superficies alfa para garantizar 60 FPS en Web y en la Vaio.
      </description>
    </file>
  </file_specifications>
</argon_sensory_overhaul>