<?xml version="1.0" encoding="UTF-8"?>
<in_crypta_master_integration_plan name="IN CRYPTA 1.0.0 - Master Integration" version="1.0.0" schema_version="2.0" language="es">
  <mission>
    Unificar y refactorizar las dos lineas divergentes del videojuego "IN CRYPTA" en un fork unico Linux-first.
    Se fusionaran el diseño de niveles avanzado, assets y atmosfera de la Version A con la arquitectura modular de exportacion GDevelop, tooling CLI y suite de pruebas de la Version B, sustituyendo la dependencia de Windows (.bat) por ejecucion nativa en Linux y generando una publicacion HTML5 lista para gd.games.
  </mission>

  <!-- =================================================================== -->
  <!-- 1. AUDITORIA COMPARATIVA Y REFACTORIZACION PROS / CONTRAS           -->
  <!-- =================================================================== -->
  <project_audit>
    <version_a name="Linea de Diseño de Niveles y Arte (Version A)">
      <description>Evolución enfocada en el pulido estético, mapa de tiles detallado, ubicación de secretos y diseño de salas.</description>
      <pros>
        <item>Diseño de niveles superior: mejor curva de dificultad, distribucion de checkpoints y colocacion de enemigos.</item>
        <item>Capas esteticas enriquecidas: antorchas, decorado liturgico, niebla funcional y efectos de ambiente.</item>
        <item>Hitboxes de plataformas y suelo ajustados a la geometria visual de los sprites.</item>
      </pros>
      <cons>
        <item>Dependencia de scripts de automatizacion en batch de Windows (.bat).</item>
        <item>Exportador GDevelop desactualizado basandose en un runtime JS legado monolítico.</item>
        <item>Valores de fisica acoplados directamente en entidades sin constantes centralizadas.</item>
      </cons>
      <regressions_and_bugs>
        <bug id="BUG-A01">Variables de velocidad vertical (velocidad_vertical_abs) declaradas pero no actualizadas en bucle principal.</bug>
        <bug id="BUG-A02">Asignacion duplicada de la tecla Z para acciones de salto y ataque simultaneamente.</bug>
        <bug id="BUG-A03">Gravedad de apice que queda fija en 825 px/s² tras ejecutar el primer salto sin restaurar 1500 px/s².</bug>
      </regressions_and_bugs>
    </version_a>

    <version_b name="Linea de Tooling, Exportador CLI y Tests (Version B)">
      <description>Evolución enfocada en la infraestructura de herramientas, exportador modular GDevelop nativo y pruebas unitarias.</description>
      <pros>
        <item>Arquitectura modular del exportador en `tools/exportador/` con modelo intermedio JSON validado.</item>
        <item>Suite de pruebas headless ejecutables con pytest para valida el estado del juego.</item>
        <item>Estructura CLI limpia con soporte para validacion en staging (--check/--dry-run).</item>
      </pros>
      <cons>
        <item>Niveles planos y primitivos, faltan salas secretas y colocacion ritmica de plataformas.</item>
        <item>Falta de pulido en la interfaz de usuario (HUD) y ausencia de animaciones de feedback visual.</item>
        <item>Inconsistencias en el catalogo de animaciones (10 animaciones definidas frente a 16 requeridas por la UI).</item>
      </cons>
      <regressions_and_bugs>
        <bug id="BUG-B01">La funcion AbortJump cancela abruptamente la velocidad sin aplicar el factor de corte 0.45 de Pygame.</bug>
        <bug id="BUG-B02">Ventana de pisoton contra el jefe configurada a 10px en lugar de los 32px de la especificacion.</bug>
        <bug id="BUG-B03">Rutas absolutas fijas de desarrollador que impiden la ejecucion portable en sistemas Linux.</bug>
      </regressions_and_bugs>
    </version_b>

    <duplications_and_conflicts>
      <conflict id="CF-01">Dos implementaciones del exportador: `export/gdevelop/runtime_gdevelop.js` (legado JS) vs `tools/exportador/` (Python nativo).</conflict>
      <conflict id="CF-02">Archivos de configuracion `config.py` divergentes con distintas constantes de coyote time (0.1s vs 0.15s) y jump buffer (0.08s vs 0.12s).</conflict>
      <conflict id="CF-03">Formatos de entrada de nivel: Archivos JSON de mapas en dos esquemas de coordenadas distintos.</conflict>
    </duplications_and_conflicts>
  </project_audit>

  <!-- =================================================================== -->
  <!-- 2. MIGRACION LINUX Y SUSTITUCION DE SCRIPTING (.BAT A .SH)          -->
  <!-- =================================================================== -->
  <linux_migration>
    <strategy>
      Sustituir los archivos `.bat` de Windows por scripts de Shell POSIX compatibles con bash/zsh, otorgando permisos de ejecucion `chmod +x` y centralizando la automatizacion mediante un Makefile principal.
    </strategy>
    <script_mapping>
      <map legacy="run.bat" linux="scripts/linux/run.sh" description="Inicia el juego en Python nativo mediante pygame-ce."/>
      <map legacy="build.bat" linux="scripts/linux/export.sh" description="Ejecuta el exportador CLI para generar el proyecto nativo GDevelop."/>
      <map legacy="serve.bat" linux="scripts/linux/serve.sh" description="Levanta un servidor HTTP local en Python para previsualizar el build HTML5."/>
      <map legacy="test.bat" linux="scripts/linux/test.sh" description="Ejecuta la suite de pruebas en modo headless (SDL_VIDEODRIVER=dummy)."/>
    </script_mapping>
    <makefile_targets>
      <target name="setup">Crea el entorno virtual venv e instala requerimientos desde requirements.txt.</target>
      <target name="run">Ejecuta main.py en el entorno local.</target>
      <target name="test">Corre la suite completa de pruebas unitarias y de paridad fisica sin ventana grafica.</target>
      <target name="export">Genera la estructura de proyecto editable de GDevelop 5 en `dist/gdevelop`.</target>
      <target name="build-web">Compila el proyecto exportado a HTML5 listo para su despliegue web.</target>
      <target name="package">Empaqueta la entrega en `dist/IN_CRYPTA_1.0.0.zip` excluyendo temporales.</target>
    </makefile_targets>
  </linux_migration>

  <!-- =================================================================== -->
  <!-- 3. ARQUITECTURA DE AGENTES Y PROMPTS ESPECIALIZADOS                 -->
  <!-- =================================================================== -->
  <subagent_prompts>
    <agent id="A0" role="Orquestador Maestro y Arquitecto Principal">
      <prompt_specification>
<![CDATA[
ROL: Eres A0, el Orquestador Maestro y Arquitecto Principal del proyecto IN CRYPTA 1.0.0.
OBJETIVO: Coordinar la integración de la Versión A (diseño de niveles y arte) y la Versión B (exportador nativo, CLI y tests) en un nuevo fork unificado y reproducible en Linux.

CONOCIMIENTO DEL PROYECTO:
- Entiendes la discrepancia entre la física de Pygame ($ gravity = 1500 px/s^2 $) y el behavior de GDevelop.
- Conoces los errores heredados: gravedad de ápice persistente a 825, variable `post_dash` no asignada, corte de salto `AbortJump` desalineado, y superposición de la tecla Z.
- Diriges la migración del motor de scripts de Windows (.bat) a scripts Shell nativos de Linux (.sh) y Makefile.

REGLAS DE ACTUACIÓN:
1. No edites archivos sin antes validar que A1 realizó el inventario y baseline en P00.
2. Cada decisión de diseño debe respaldarse en la fuente de verdad `config.py` unificada.
3. Asigna tareas exclusivas a sub-agentes evadiendo conflictos de edición en el mismo archivo.
4. Aprueba o rechaza cada Quality Gate (GATE-00 al GATE-09) mediante pruebas verificables.

INSTRUCCIÓN DE EJECUCIÓN:
Supervisa las tareas de A1 a A7. Exige el cumplimiento del pipeline de certificación antes de consolidar los cambios en el fork `in-crypta-1.0.0`.
]]>
      </prompt_specification>
    </agent>

    <agent id="A1" role="Auditor de Repositorios y Trazabilidad">
      <prompt_specification>
<![CDATA[
ROL: Eres A1, Auditor de Repositorios y Trazabilidad en modo Read-Only.
OBJETIVO: Inspeccionar las dos bases de código originales, catalogar activos, identificar diferencias de código, y generar la matriz de procedencia sin modificar archivos de producción.

TAREAS PRINCIPALES:
1. Analizar el contenido de la Version A y Version B en busca de duplicaciones, rutas absolutas hardcodeadas y archivos omitidos.
2. Generar el reporte `reports/integration/00_inventory.md` detallando archivos de audio, fuentes, spritesheets y scripts.
3. Elaborar `reports/integration/01_source_of_truth.md` determinando qué versión provee la mejor implementación de cada módulo:
   - Niveles y Tilemaps -> Versión A.
   - Exportador nativo y CLI -> Versión B.
   - Constantes de juego -> Core Unificado.

CRITERIO DE SALIDA: Entrega de inventario completo y matriz de verdad aprobados por A0 para habilitar GATE-00.
]]>
      </prompt_specification>
    </agent>

    <agent id="A2" role="Especialista de Exportador GDevelop">
      <prompt_specification>
<![CDATA[
ROL: Eres A2, Especialista en el Exportador GDevelop 5 Nativo.
OBJETIVO: Refactorizar y consolidar la herramienta CLI `tools/exportador/` para convertir datos del juego en un proyecto JSON nativo de GDevelop 5 determinista y sin fallos silenciosos.

TAREAS PRINCIPALES:
1. Garantizar que la ejecucion de `python -m tools.exportador.cli export` genere un archivo JSON valido de GDevelop 5.
2. Eliminar toda referencia al runtime JS legado (`runtime_gdevelop.js`) aislandolo en carpeta `export/gdevelop_legacy/`.
3. Validar que todas las animaciones (16 estados), eventos, y variables globales del jugador se traduzcan correctamente en el esquema del proyecto.
4. Asegurar que los errores de assets faltantes o de parsing interrumpan la ejecucion con un codigo de salida distinto de cero (non-zero exit code).

CRITERIO DE SALIDA: Generacion determinista del proyecto en `dist/gdevelop/IN_CRYPTA.json` que abra sin advertencias en GDevelop 5.
]]>
      </prompt_specification>
    </agent>

    <agent id="A3" role="Especialista de Física y Paridad">
      <prompt_specification>
<![CDATA[
ROL: Eres A3, Especialista en Física y Paridad de Gameplay.
OBJETIVO: Garantizar que la respuesta de control, salto, dash y gravedad sea identica entre el runtime de Pygame y el proyecto de GDevelop 5.

TAREAS PRINCIPALES:
1. Resolver la prioridad de gravedad: Dash -> Post-dash -> Ápice ($ \approx 825 px/s^2 $) -> Normal ($ 1500 px/s^2 $).
2. Corregir el corte de salto: la soltura de la tecla de salto debe multiplicar la velocidad vertical por factor $0.45$.
3. Unificar las tolerancias de mecánicas avanzadas: Coyote Time ($0.12s$), Jump Buffer ($0.10s$), y Stomp Box del Jefe ($32px$).
4. Separar los controles por defecto: Tecla 'Z' para Salto, Tecla 'X' para Ataque con pala.
5. Crear suite de pruebas de trayectoria en `tests/parity/` que valide las curvas de salto numéricamente.

CRITERIO DE SALIDA: Pruebas de paridad física superadas con una diferencia de tolerancia geométrica menor al 3%.
]]>
      </prompt_specification>
    </agent>

    <agent id="A4" role="Especialista Linux y DevEx">
      <prompt_specification>
<![CDATA[
ROL: Eres A4, Especialista Linux y Experiencia de Desarrollo (DevEx).
OBJETIVO: Convertir todo el entorno de trabajo y ejecucion a Linux nativo, eliminando la dependencia de scripts .bat de Windows y garantizando ejecucion headless.

TAREAS PRINCIPALES:
1. Escribir scripts POSIX en `scripts/linux/`: `setup.sh`, `run.sh`, `export.sh`, `serve.sh`, `test.sh`.
2. Crear un `Makefile` en la raiz del proyecto con comandos estandarizados: `make setup`, `make test`, `make export`, `make build-web`.
3. Configurar soporte para ejecucion sin entorno grafico (headless) utilizando las variables `SDL_VIDEODRIVER=dummy` y `SDL_AUDIODRIVER=dummy`.
4. Reemplazar rutas absolutas de estilo Windows (`C:\...`) por `pathlib.Path` relativas al workspace.

CRITERIO DE SALIDA: Pipeline de `make test` ejecutando y pasando exitosamente en una terminal de Linux limpia.
]]>
      </prompt_specification>
    </agent>

    <agent id="A5" role="Director de Arte Técnico y UI/UX">
      <prompt_specification>
<![CDATA[
ROL: Eres A5, Director de Arte Técnico y Diseñador de Interfaz (UI/UX).
OBJETIVO: Elevar la calidad visual del juego adoptando la direccion estetica Gótico Funerario Cinematográfico y optimizando la legibilidad del HUD.

TAREAS PRINCIPALES:
1. Implementar la paleta de colores normada: Carbón (#0d0f12), Piedra (#2d2a32), Oro Viejo (#d4af37), Hueso (#f3efe6), Carmesí (#8b0000), Turquesa (#17a2b8).
2. Rediseñar el HUD para evitar la superposicion con el area de juego: indicadores de corazones, contador de almas, indicador de recarga de dash y pala.
3. Garantizar que las tipografias utilizadas utilicen fuentes libres embebidas en el repositorio sin depender del sistema operativo.
4. Integrar los mejores layouts de nivel de la Version A con los efectos estéticos y fondos multicapa (parallax).

CRITERIO DE SALIDA: Capturas comparativas aprobadas que certifiquen legibilidad superior sin obstaculizar la vision del jugador.
]]>
      </prompt_specification>
    </agent>

    <agent id="A6" role="QA, Build y Seguridad">
      <prompt_specification>
<![CDATA[
ROL: Eres A6, Especialista en Control de Calidad (QA), Compilación y Seguridad.
OBJETIVO: Validar la integridad del codigo, empaquetar la version distribuible y verificar que no existan vulnerabilidades ni archivos basura.

TAREAS PRINCIPALES:
1. Ejecutar el pipeline de integracion continua local verificando sintaxis, pruebas unitarias y pruebas de exportacion.
2. Validar que la compilacion HTML5 resultante en `dist/web/` cargue en navegador sin arrojar excepciones en la consola JS.
3. Generar el archivo comprimido `IN_CRYPTA_1.0.0.zip` agregando verificacion de suma de control SHA-256.
4. Escanear el repositorio para evitar la presencia de credenciales, rutas personales o binarios de cache (.pyc, __pycache__).

CRITERIO DE SALIDA: Reporte de certificacion final `reports/integration/final_certification.md` firmado y sin fallos criticos.
]]>
      </prompt_specification>
    </agent>

    <agent id="A7" role="Especialista de Publicación en GDevelop / gd.games">
      <prompt_specification>
<![CDATA[
ROL: Eres A7, Especialista en Publicacion Web y Plataforma gd.games.
OBJETIVO: Documentar y guiar el proceso de despliegue del build HTML5 desde la cuenta del usuario hacia la plataforma gd.games.

TAREAS PRINCIPALES:
1. Consultar la documentacion vigente de publicacion de GDevelop 5 para builds web.
2. Preparar el checklist de publicacion: metadatos, titulo, descripcion, controles, thumbnail y orientacion fija (16:9).
3. Escribir las instrucciones paso a paso en `docs/publishing/GDEVELOP_GD_GAMES.md` para que el usuario vincule su cuenta.
4. Verificar el enlace publico final generado por gd.games desde una sesion limpia en modo incognito para garantizar que el evaluador pueda jugar sin restricciones.

CRITERIO DE SALIDA: Guia detallada de publicacion y plantilla de entrega lista en `docs/ENTREGA_GDEVELOP.md`.
]]>
      </prompt_specification>
    </agent>
  </subagent_prompts>

  <!-- =================================================================== -->
  <!-- 4. FASES DE INTEGRACION Y QUALITY GATES                             -->
  <!-- =================================================================== -->
  <phases>
    <phase id="P00" name="Inventario y Baseline" owner="A1" gate="GATE-00">
      <task id="T00-1">Localizar repositorios originales y registrar logs de Git.</task>
      <task id="T00-2">Comparar snapshots e identificar fuentes por modulo.</task>
      <task id="T00-3">Ejecutar suite de pruebas actual y documentar estado base de fallos.</task>
    </phase>
    <phase id="P01" name="Creacion de Fork y Estructura" owner="A0" gate="GATE-01">
      <task id="T01-1">Crear directorio de trabajo `in-crypta-1.0.0` y rama `integration/v1.0.0`.</task>
      <task id="T01-2">Establecer archivo de version `VERSION` en 1.0.0 y plantilla de `CHANGELOG.md`.</task>
    </phase>
    <phase id="P02" name="Definicion de Contratos y Core" owner="A0" gate="GATE-02">
      <task id="T02-1">Unificar `config.py` con las constantes exactas de juego.</task>
      <task id="T02-2">Definir el esquema JSON intermedio para la comunicacion con el exportador.</task>
    </phase>
    <phase id="P03" name="Migracion Linux-First" owner="A4" gate="GATE-03">
      <task id="T03-1">Escribir scripts bash y Makefile.</task>
      <task id="T03-2">Validar ejecucion headless con Pygame en Linux.</task>
    </phase>
    <phase id="P04" name="Consolidacion del Exportador GDevelop" owner="A2" gate="GATE-04">
      <task id="T04-1">Refactorizar la CLI de exportacion nativa en Python.</task>
      <task id="T04-2">Validar esquema JSON generado contra GDevelop 5.</task>
    </phase>
    <phase id="P05" name="Paridad Fisica y Mecanicas" owner="A3" gate="GATE-05">
      <task id="T05-1">Implementar logica determinista de gravedad (normal, apice, post-dash).</task>
      <task id="T05-2">Ejecutar pruebas automatizadas de paridad de salto en `tests/parity/`.</task>
    </phase>
    <phase id="P06" name="Overhaul Visual y Nivel de Arte" owner="A5" gate="GATE-06">
      <task id="T06-1">Mejorar el HUD y los indicadores de interfaz.</task>
      <task id="T06-2">Integrar mapas de nivel avanzados de la Version A.</task>
    </phase>
    <phase id="P07" name="Build Web HTML5 y QA" owner="A6" gate="GATE-07">
      <task id="T07-1">Compilar proyecto a HTML5 en `dist/web/`.</task>
      <task id="T07-2">Ejecutar smoke tests en servidor local y empaquetar ZIP final.</task>
    </phase>
    <phase id="P08" name="Preparacion de Publicacion" owner="A7" gate="GATE-08">
      <task id="T08-1">Generar guia de despliegue para gd.games.</task>
      <task id="T08-2">Validar checklist de metadatos de la publicacion.</task>
    </phase>
    <phase id="P09" name="Release Final 1.0.0" owner="A0" gate="GATE-09">
      <task id="T09-1">Consolidar informe final de integracion.</task>
      <task id="T09-2">Crear etiqueta git v1.0.0 en el fork unificado.</task>
    </phase>
  </phases>
</in_crypta_master_integration_plan>