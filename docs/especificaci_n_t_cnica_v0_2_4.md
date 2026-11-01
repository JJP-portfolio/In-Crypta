<incrypta_patch_release version="0.2.4" base_version="CURRENT_WORKSPACE_HEAD" status="READY_FOR_INTEGRATION">

  <header>
    <project_name>In Crypta</project_name>
    <target_branch>v0.2.4</target_branch>
    <base_state>Estado Actual del Repositorio / Workspace HEAD (Última versión modificada)</base_state>
    <author>Lead Architect &amp; Game Designer Pipeline</author>
    <description>
      Especificación técnica completa y consolidada para la versión 0.2.4. Integra correcciones de bugs,
      refactorización de física "Game Feel" tipo Celeste, sincronización de audio a 44.1 kHz stereo, unificación de las 4 interfaces UI/UX,
      y paridad 1:1 con el exportador nativo GDevelop 5.6, partiendo estrictamente del código más reciente.
    </description>
  </header>

  <git_workflow>
    <step order="1">git status (Verificar que los archivos modificados estén presentes en el workspace actual)</step>
    <step order="2">git checkout -b v0.2.4 (Crear e integrar directamente desde el estado actual)</step>
    <step order="3">Actualizar VERSION = "0.2.4" en config.py</step>
    <step order="4">Ejecutar la suite completa de certificación de paridad y pruebas de lógica antes del merge</step>
  </git_workflow>

  <audited_fixes_and_features>

    <category name="Pygame Code Integrity &amp; Bug Fixes">
      <fix id="FIX-PY-01" target="entidades.py">
        <issue>Conflicto de mapa de teclado WASD/Flechas. Presionar 'A' ejecutaba ataque al compartir binding con TECLAS_ATAQUE.</issue>
        <resolution>
          Removida pygame.K_a de TECLAS_ATAQUE en juego.py. Se asignaron TECLAS_ATAQUE = (pygame.K_j, pygame.K_z, pygame.K_k) + Click Izquierdo.
          En entidades.py (Jugador.actualizar_horizontal), se unificó la lectura: izquierda = teclas[K_LEFT] or teclas[K_a].
        </resolution>
      </fix>
      <fix id="FIX-PY-02" target="entidades.py">
        <issue>Método duplicado actualizar_temporizadores(self, dt) en la clase Jugador (líneas 317 y 341).</issue>
        <resolution>Eliminada la segunda declaración redundante para evitar sobreescrituras en tiempo de ejecución.</resolution>
      </fix>
      <fix id="FIX-PY-03" target="juego.py">
        <issue>UI Espacial (carteles flotantes sobre altares) seguía dibujándose tras haber recogido los ítems.</issue>
        <resolution>Corregida la verificación del atributo a getattr(dp, "recogida", False) en dibujar_ui_espacial.</resolution>
      </fix>
      <fix id="FIX-PY-04" target="audio.py">
        <issue>Desfase de frecuencia: el sintetizador generaba buffers a 22050 Hz mono mientras el mixer Pygame corría a 44100 Hz stereo.</issue>
        <resolution>Sincronizada la generación procedural de SFX a 44100 Hz con 2 canales interleaved estéreo.</resolution>
      </fix>
      <fix id="FIX-PY-05" target="juego.py">
        <issue>Métodos heredados/muertos de la UI previa (dibujar_hud_relicario_vidas, dibujar_hud_relicario_derecho, dibujar_barra_jefe).</issue>
        <resolution>Depurado el código legacy delegando el renderizado al módulo hud.py.</resolution>
      </fix>
    </category>

    <category name="Physics &amp; Game Feel Overhaul">
      <fix id="FIX-PHYS-01" target="entidades.py &amp; config.py">
        <issue>Causas de caída abrupta en saltos y falta de respuesta dinámica en el aire.</issue>
        <resolution>
          - Apex Hang-Time: Si not self.en_suelo, mantiene tecla de salto y |vy| &lt; 95.0 px/s, aplicar 55% de gravedad (0.55 * GRAVEDAD).
          - Coyote Time: Ventana de 0.10s tras dejar una plataforma en la que el salto permanece activo.
          - Jump Buffer: Registro de pulsación anticipada de salto durante 0.12s.
        </resolution>
      </fix>
      <fix id="FIX-PHYS-02" target="entidades.py">
        <issue>Frenazo brusco en el Dash ("pared invisible" al terminar la aceleración horizontal).</issue>
        <resolution>
          Al finalizar el Dash (dash_tiempo == 0), se activa post_dash_tiempo = 0.06s conservando el 100% de la velocidad horizontal (vx = dash_dir * VELOCIDAD) y 50% de gravedad.
        </resolution>
      </fix>
      <fix id="FIX-PHYS-03" target="entidades.py">
        <issue>Imposibilidad de realizar Dash-Jump y pisotones dinámicos.</issue>
        <resolution>
          - Dash-Jump: Si el jugador presiona salto durante un Dash en el suelo o Coyote Time, cancela el dash e impulsa vy = SALTO y vx = dash_dir * VELOCIDAD * 1.18.
          - Pisotón (Stomp): Rebotar sobre un enemigo con la pala equipada elimina al enemigo, genera vy = -360 px/s y recarga el dash aéreo (dash_usos_aire = 1, dash_cooldown = 0.0).
        </resolution>
      </fix>
    </category>

    <category name="UI/UX Four-Layer System">
      <fix id="FIX-UI-01" target="hud.py &amp; juego.py">
        <issue>Fragmentación y desalineación de los elementos de la interfaz de usuario.</issue>
        <resolution>
          - Capa No-Diegética: Riel HUD superior de 1232x72 px fijado en pantalla con grilla 2x2 ([ALMA], [DASH], VIDA EXTRA, [ARMA]).
          - Capa Diegética: Farol del Sepulturero en el personaje con núcleo turquesa cuando el Dash está listo y halo violeta con Guadaña ('X'). Checkpoints encendidos ('F').
          - Capa Espacial: Indicadores flotantes de controles sobre altares ('D', 'W', 'X') que desaparecen al interactuar.
          - Capa Meta: Viñeta carmesí periférica que pulsa en los bordes cuando el jugador queda a 1 HP.
        </resolution>
      </fix>
    </category>

    <category name="GDevelop 5.6 Native Exporter Parity">
      <fix id="FIX-GD-01" target="tools/generar_proyecto_nativo.py">
        <issue>Desincronización de zoom de cámara respecto a Pygame (1.0 vs 1.25).</issue>
        <resolution>Configurado GAME_ZOOM = 1.25 en la capa Base y 1.0 en la capa UI para proyección exacta de 1024x576 unidades virtuales.</resolution>
      </fix>
      <fix id="FIX-GD-02" target="tools/exportador/*">
        <issue>Pérdida de posición de Checkpoint al morir en GDevelop debido a recarga completa de Scene.</issue>
        <resolution>
          Reestructurado el flujo de eventos en GDevelop: si vidas &gt; 0 y checkpoint_activo == 1, se posiciona el objeto Jugador en (checkpoint_x, checkpoint_y) e inyecta 1.2s de invulnerabilidad sin invocar recarga de escena.
        </resolution>
      </fix>
      <fix id="FIX-GD-03" target="tools/integrar_assets_gdevelop.py">
        <issue>Hitbox genérica (32x32 px) causaba colisiones injustas en plataformas ajustadas.</issue>
        <resolution>Inyectada customCollisionMask de 24x30 px centrada en el objeto Jugador.</resolution>
      </fix>
      <fix id="FIX-GD-04" target="tools/exportador/hoja_eventos.py">
        <issue>Falta de correspondencia en las 16 animaciones multipose de Pixel-Art.</issue>
        <resolution>Enlazados en la hoja de eventos los índices de animación de GDevelop para Run, Jump, Caida, Dash, Idle y Ataque.</resolution>
      </fix>
    </category>

  </audited_fixes_and_features>

  <pending_revisions_and_improvements>

    <item id="REV-01" priority="HIGH">
      <title>Máquina de Estados de Fase 2 del Jefe Final ('B' - El Custodio)</title>
      <description>
        Verificar la transición al 50% de HP del Jefe Final en Nivel 3. Confirmar que el jefe despliegue su escudero espectral
        y que los ataques sin el Power-Up de Guadaña ('X') generen rechazo (parry) con partículas de chispas y SFX metálico.
      </description>
      <file>entidades.py / juego.py</file>
    </item>

    <item id="REV-02" priority="MEDIUM">
      <title>Pool de Partículas (Object Pooling)</title>
      <description>
        Optimizar la reinstanciación continua de partículas en el loop principal de Pygame reemplazándola por un pool preasignado
        para mejorar el rendimiento en plataformas de hardware modesto.
      </description>
      <file>sistema_particulas.py / entidades.py</file>
    </item>

    <item id="REV-03" priority="MEDIUM">
      <title>Controles Táctiles Integrados en GDevelop</title>
      <description>
        Inyectar soporte opcional para D-Pad táctil y botones en la capa UI del proyecto exported a GDevelop para permitir
        despliegue nativo directo en dispositivos Android/Web Touch.
      </description>
      <file>tools/generar_proyecto_nativo.py</file>
    </item>

    <item id="REV-04" priority="LOW">
      <title>Ampliación de Pruebas Unitarias de Física</title>
      <description>
        Añadir afirmaciones en tests/test_logica.py para certificar de forma automatizada los valores de vy durante Apex Hang-Time
        y la conservación de velocidad tras finalizar el Post-Dash.
      </description>
      <file>tests/test_logica.py</file>
    </item>

  </pending_revisions_and_improvements>

  <renewed_master_prompt>
<![CDATA[
# PROMPT RENOVADO DE INTEGRACIÓN Y CERTIFICACIÓN - IN CRYPTA v0.2.4

> **Instrucción de Sistema:** Actuás como el **Lead Architect & Pipeline Engineer** en el repositorio "In Crypta".
> Tu objetivo principal en esta sesión es ejecutar la integración formal de la versión `0.2.4` partiendo del **estado actual de tu espacio de trabajo (HEAD)**, verificando los arreglos aplicados y completando las revisiones pendientes.

---

### PASOS DE EJECUCIÓN OBLIGATORIOS:

1. **Integración en Git desde el Estado Actual:**
   - Asegúrate de trabajar sobre los últimos cambios del workspace.
   - Ejecuta: `git checkout -b v0.2.4`
   - Actualiza la constante `VERSION = "0.2.4"` en `config.py`.

2. **Revisión y Ajuste del Jefe Final (REV-01):**
   - Revisa la lógica del Boss ('B') en `entidades.py` y `juego.py`.
   - Asegura que al alcanzar el 50% de HP entre en Fase 2, activando proyectiles espectrales.
   - Si el jugador golpea sin la Guadaña ('X'), debe disparar SFX `escudo_parry` y emitir partículas de chispas sin restar vida al Boss.

3. **Verificación de la Física Game Feel (Fase 1):**
   - Confirma la presencia de Apex Hang-Time (gravedad 0.55 cuando $|v_y| < 95.0$).
   - Confirma el Post-Dash Float ($0.06\text{ s}$ a 50% de gravedad conservando $v_x$).
   - Confirma que el pisotón resetea `dash_usos_aire = 1`.

4. **Certificación Obligatoria de la Suite:**
   Ejecuta la siguiente secuencia de comandos en terminal y confirma que TODOS finalicen con exit code 0:

   ```bash
   # 1. Exportar proyecto nativo a GDevelop y sincronizar assets
   PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/exportar_todo.py

   # 2. Validar sintaxis y esquema de eventos GDevelop 5.6
   PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/validar_eventos_gd.py

   # 3. Comprobar paridad geométrica y física entre motores
   PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tools/verificar_paridad.py

   # 4. Pruebas unitarias de lógica y física Pygame
   PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_logica.py

   # 5. Pruebas unitarias del HUD de 4 capas
   PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python tests/test_hud.py
   ```

5. **Commit Final v0.2.4:**
   - Commitea los cambios por rutas específicas de archivo indicando en el mensaje el cumplimiento de la versión 0.2.4.
]]>
  </renewed_master_prompt>

</incrypta_patch_release>