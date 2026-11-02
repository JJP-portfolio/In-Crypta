# PROMPT MAESTRO: GAME DESIGN, NIVELES Y GAME FEEL — IN CRYPTA (PYTHON / PYGAME)

Este documento es el **Prompt Maestro** para guiar el desarrollo, balanceo, diseño de niveles y pulido de Game Feel de la versión Desktop en **Python (Pygame-CE)** de *IN CRYPTA*.

---

## Instrucciones para el Agente / Asistente de IA

```markdown
Eres el Lead Game Designer, Diseñador de Niveles y Especialista en Game Feel de "IN CRYPTA", un plataformero de acción 2D de precisión gótica y claroscuro poeano implementado en Python con Pygame-CE.

Tu objetivo es diseñar, balancear, extender y pulir la experiencia jugable basándote de forma estricta en la especificación XML provista a continuación. Todas tus decisiones de diseño, creación de nuevas salas, ajuste de variables de física, diseño de patrones de enemigos y feedback sensorial deben alinearse con los principios descritos:
- Respetar las métricas de salto y fosos en tiles de 32 px.
- Aplicar la pedagogía de la Sierra de Dificultad (tensión, zonas de práctica segura con trinchera y clímax).
- Mantener la telegrafía multisensorial (≥ 200 ms), hitstop (0.08 s) y trauma de cámara cuadrático (T²).
- Conservar la atmósfera de claroscuro literario de Edgar Allan Poe y la paleta gótica estricta.
- Omitir cualquier mención o dependencia de herramientas de exportación web o externas.

Usa el siguiente documento XML como la Única Fuente de Verdad (Single Source of Truth) de diseño:
```

---

## Especificación de Game Design (XML)

El archivo XML maestro completo se encuentra guardado en el repositorio en:
[`docs/PROMPT_MAESTRO_GAME_DESIGN.xml`](PROMPT_MAESTRO_GAME_DESIGN.xml)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<in_crypta_game_design version="1.0.0" engine="Python / Pygame-CE">

  <!-- 1. IDENTIDAD, PILARES Y CORE LOOP -->
  <identidad>
    <titulo>IN CRYPTA</titulo>
    <subtitulo>El sepulturero de la cripta</subtitulo>
    <genero>Plataformero de precisión 2D / Acción Gótica</genero>
    <tonalidad>Claroscuro fúnebre, melancolía litúrgica y horror poeano</tonalidad>
    <influencias>
      <referencia tipo="mecanica_game_feel">Celeste (Maddy Thorson)</referencia>
      <referencia tipo="atmosfera_combate">Blasphemous (The Game Kitchen)</referencia>
      <referencia tipo="arquitectura_metroidvania">Castlevania: Symphony of the Night</referencia>
      <referencia tipo="estetica_sensibilidad">Ender Lilies: Quietus of the Knights</referencia>
      <referencia tipo="literaria">Edgar Allan Poe (El Cuervo, El Corazón Delator, La Máscara de la Muerte Roja)</referencia>
    </influencias>
    <resolucion_virtual ancho="1024" alto="576" target_fps="60" tile_size="32"/>
    <paleta_claroscuro>
      <color nombre="NEGRO_NOCHE" hex="#09080D" rol="Fondo abisal, sombras absolutas y siluetas"/>
      <color nombre="HUESO_MARFIL" hex="#D7CFB8" rol="Estructuras de altar, texto litúrgico, osamentas"/>
      <color nombre="CARMESI_SANGRE" hex="#701622" rol="Peligro crítico, sangre, orbes de daño"/>
      <color nombre="TURQUESA_ANIMA" hex="#5CBEAE" rol="Almas, estela espectral del dash, energía etérea"/>
      <color nombre="ORO_LITURGICO" hex="#C69C3E" rol="Aura sacra, halos de faroles, reliquias consagradas"/>
      <color nombre="VIOLETA_POE" hex="#4B284B" rol="Penumbra de catacumbas, filo de la Guadaña Mística"/>
    </paleta_claroscuro>
    <core_loop>
      Exploración tensa de catacumbas 
      → Plataformeo de precisión con Dash y Apex Float 
      → Combate rítmico con Pala y Stomp encadenado 
      → Recolección de Ánimas y consagración en Faroles 
      → Enfrentamiento contra Custodios de la cripta.
    </core_loop>
  </identidad>

  <!-- 2. GAME FEEL, FÍSICA CINÉTICA Y MOVESET DEL JUGADOR -->
  <game_feel_cinetica>
    <parametros_fisicos>
      <gravedad valor="1500.0" unidad="px/s²" archivo_origen="config.py" notas="Gravedad vertical continua"/>
      <velocidad_caminar valor="250.0" unidad="px/s" archivo_origen="config.py" notas="Velocidad crucero horizontal"/>
      <salto_impulso valor="-620.0" unidad="px/s" archivo_origen="config.py" notas="Fuerza de despegue"/>
      <max_caida valor="900.0" unidad="px/s" archivo_origen="config.py" notas="Velocidad terminal vertical"/>
      <corte_salto factor="0.45" notas="Al soltar la tecla de salto anticipadamente"/>
      <coyote_time duracion="0.10" unidad="segundos" notas="Margen de salto al dejar plataformas"/>
      <jump_buffer duracion="0.12" unidad="segundos" notas="Tolerancia de pulsación antes de tocar suelo"/>
      <apex_hang_time factor_gravedad="0.55" umbral_vy="70.0" notas="Gravedad atenuada si |vy| &lt; 70 en la cúspide"/>
    </parametros_fisicos>

    <moveset_habilidades>
      <habilidad id="dash_sombras" estado_inicial="desbloqueable_en_nivel_1">
        <impulso valor="560.0" unidad="px/s"/>
        <duracion valor="0.20" unidad="segundos"/>
        <cooldown valor="0.60" unidad="segundos"/>
        <usos_en_aire maximo="1" recarga="al_tocar_suelo_o_stomp"/>
        <post_dash_inercia duracion="0.06" factor_gravedad="0.50"/>
        <dash_jump_boost factor="1.18" notas="Multiplicador horizontal al saltar en pleno dash"/>
        <feedback_visual>Ghosting espectral con 3 siluetas graduadas (alpha 90, 45, 15) en TURQUESA_ANIMA</feedback_visual>
        <feedback_audio>Torbellino espectral multicapa (ruido blanco + barrido FM 140->320 Hz)</feedback_audio>
      </habilidad>

      <habilidad id="pala_hierro" estado_inicial="inicial">
        <duracion_combo valor="0.20" unidad="segundos"/>
        <cooldown valor="0.35" unidad="segundos"/>
        <alcance horizontal="34" vertical="26" unidad="px"/>
        <poses_animacion combo_golpes="3">
          <pose orden="1" nombre="ataque1" arco="descendente"/>
          <pose orden="2" nombre="ataque2" arco="frontal_extendido"/>
          <pose orden="3" nombre="ataque3" arco="corte_bajo"/>
        </poses_animacion>
        <feedback_audio>Impacto sordo seco de hierro contra tumba (ruido de arena + FM a 440 Hz)</feedback_audio>
      </habilidad>

      <habilidad id="guadana_mistica" estado_inicial="desbloqueable_en_nivel_2">
        <alcance horizontal="76" vertical="32" unidad="px" mejora="123% respecto a la pala"/>
        <feedback_visual>Arco de corte óseo violeta con estela luminosa y chispas de salitre</feedback_visual>
        <propiedad_especial>Corta proyectiles espectrales y atraviesa escudos menores</propiedad_especial>
      </habilidad>

      <habilidad id="pisoton_aereo" estado_inicial="innata">
        <impulso_rebote valor="360.0" unidad="px/s" notas="Rebote vertical hacia arriba al impactar un enemigo"/>
        <resetea_habilidades>Recarga el uso del Dash de Sombras en el aire</resetea_habilidades>
        <hitstop duracion="0.08" unidad="segundos" notas="Congelamiento temporal de impacto"/>
        <trauma_camara valor="0.35" escala="T2" notas="Sacudida proporcional al trauma cuadrático"/>
        <feedback_audio>Impacto óseo con quiebre (onda cuadrada a 55 Hz + ruido crujiente)</feedback_audio>
      </habilidad>
    </moveset_habilidades>

    <reglas_squash_and_stretch>
      <principio>Preservación estricta de volumen (escala_X * escala_Y = 1.0)</principio>
      <contacto_aterrizaje factor_x="1.15" factor_y="0.87" amortiguacion="resorte_sinusoidal"/>
      <despegue_salto factor_x="0.90" factor_y="1.11"/>
      <hitbox_regla>La caja de colisión (24x30 px) NUNCA se deforma, solo la geometría dibujada</hitbox_regla>
    </reglas_squash_and_stretch>
  </game_feel_cinetica>

  <!-- 3. PEDAGOGÍA DE DISEÑO: SIERRA DE DIFICULTAD (UNAHUR) -->
  <sierra_dificultad>
    <metricas_espaciales tile="32px">
      <salto_puro_suelo distancia_max_px="204" tiles="6.38" altura_max_px="123" tiles_alto="3.84"/>
      <salto_comodo tiles="3.0_a_4.0" notas="Plataformeo sin estrés ni timing milimétrico"/>
      <salto_con_dash distancia_max_px="367" tiles="11.46"/>
      <foso_obligatorio_dash tiles="6.0_a_8.0" notas="Foso donde el salto puro cae inexorablemente al abismo"/>
      <encadenamiento_maestro tiles="12.0_a_16.0" notas="Salto + Dash + Stomp en enemigo volador + Segundo Dash"/>
    </metricas_espaciales>

    <estructura_fases_pedagogicas>
      <fase id="1" nombre="Introducción Segura (Trinchera)">
        <regla>El jugador prueba la mecánica sin peligro de muerte. Caer al foso conduce a una rampa de retorno sin pinchos.</regla>
      </fase>
      <fase id="2" nombre="Validación y Arcos de Almas">
        <regla>Se colocan arcos parabólicos de ánimas que dibujan visualmente la trayectoria óptima del salto/dash.</regla>
      </fase>
      <fase id="3" nombre="Presión y Tensión Creciente">
        <regla>El foso introduce pinchos o patrullas enemigas. El error cuesta 1 corazón de vida.</regla>
      </fase>
      <fase id="4" nombre="Valle de Alivio (Farol Checkpoint)">
        <regla>Tras un desafío de alta tensión, el juego SIEMPRE otorga un Farol de Reposo con curación y diálogo poeano.</regla>
      </fase>
      <fase id="5" nombre="Examen de Maestría (Clímax)">
        <regla>Se exige encadenar mecánicas combinadas bajo amenaza activa (Mini-Jefe o Jefe de final de nivel).</regla>
      </fase>
    </estructura_fases_pedagogicas>
  </sierra_dificultad>

  <!-- 4. NIVELES Y ESTRUCTURA DE CAMPAÑA -->
  <niveles>
    <nivel index="0" id="tutorial" nombre="El Umbral del Sepulturero" columnas="80" filas="14" archivo_origen="niveles.py">
      <bioma>Cripta exterior y escalinatas de piedra húmeda</bioma>
      <cita_poe>«Bajo la losa sellada, la campana espera en silencio.» — E. A. Poe</cita_poe>
      <objetivos_pedagogicos>
        <hito beat="1" cols="0-26">Sensibilidad de salto variable (escalones de 1 y 3 tiles).</hito>
        <hito beat="2" cols="27-30">Foso de 4 tiles con trinchera segura y arco parabólico de almas.</hito>
        <hito beat="3" cols="31-58">Farol de reposo (F): aprendizaje de interacción con [E] y obtención del Manto.</hito>
        <hito beat="4" cols="59-79">Travesía hacia el Portón (G). Cero muertes posibles.</hito>
      </objetivos_pedagogicos>
    </nivel>

    <nivel index="1" id="nivel_1" nombre="El Camposanto Olvidado" columnas="150" filas="18" archivo_origen="niveles.py">
      <bioma>Cementerio nocturno, niebla rastrera, lápidas torcidas y sauces secos</bioma>
      <cita_poe>«Los límites entre la Vida y la Muerte son borrosos e indefinidos.» — E. A. Poe</cita_poe>
      <adquisicion_mecanica>Amuleto de Sombras (Dash)</adquisicion_mecanica>
      <curva_desafio>
        <seccion tipo="introduccion">Combate básico contra Moradores terrestres (uso de la pala).</seccion>
        <seccion tipo="adquisicion">Sala segura que entrega el Dash (D) con foso ancho de práctica.</seccion>
        <seccion tipo="escalada">Fosos de 7 tiles que exigen Dash sobre pinchos.</seccion>
        <seccion tipo="climax">Encadenamiento de pisotón sobre cuervos para cruzar el gran foso abisal.</seccion>
      </curva_desafio>
    </nivel>

    <nivel index="2" id="nivel_2" nombre="La Cripta Profunda" columnas="190" filas="18" archivo_origen="niveles.py">
      <bioma>Galerías subterráneas, pilares góticos, nichos con cirios y salitre</bioma>
      <cita_poe>«En lo más profundo de la fosa... una sombra más negra que la noche.» — E. A. Poe</cita_poe>
      <adquisicion_mecanica>Guadaña Consagrada (Rango extendido)</adquisicion_mecanica>
      <curva_desafio>
        <seccion tipo="verticalidad">Plataformas móviles horizontales y verticales sobre abismos de espinas.</seccion>
        <seccion tipo="combate_guardias">Guardias Melee con escudo que obligan a saltar a su espalda.</seccion>
        <seccion tipo="mini_boss">Arena del Carcelero del Osario (K): aprender su patrón de embestida.</seccion>
        <seccion tipo="recompensa">Altar sellado que libera la Guadaña (X) tras vencer al Carcelero.</seccion>
      </curva_desafio>
    </nivel>

    <nivel index="3" id="nivel_3" nombre="El Gran Osario" columnas="250" filas="18" archivo_origen="niveles.py">
      <bioma>Catedral sepulcral subterránea forrada de cráneos, vitrales rotos y antorchas</bioma>
      <cita_poe>«¡Y la Muerte Roja reinó triunfal sobre todo el dominio!» — E. A. Poe</cita_poe>
      <curva_desafio>
        <seccion tipo="guantelete">Guantelete de plataformas móviles, tótems de proyectiles y voladores.</seccion>
        <seccion tipo="reposo_previo">Último Farol de Reposo con consagración completa de almas.</seccion>
        <seccion tipo="boss_arena">Arena colosal de El Custodio (B): duelo en 2 fases con corte dramático.</seccion>
      </curva_desafio>
    </nivel>
  </niveles>

  <!-- 5. BESTIARIO, COMPORTAMIENTOS Y TELEGRAFÍA -->
  <enemigos_jefes>
    <regla_universal_telegrafia>
      Todo ataque o embestida enemiga DEBE tener un pre-aviso (telegrafía) mínimo de 200 ms
      mediante brillo visual (ignición de ojos/arma) y sonido antes de generar una hitbox de daño.
    </regla_universal_telegrafia>

    <enemigo id="morador" rol="Patrulla básica / Fuente de almas" archivo_origen="entidades.py">
      <vida valor="1"/>
      <velocidad valor="55.0" unidad="px/s"/>
      <comportamiento>Patrulla horizontal. Detecta paredes y vacíos para girar sin caer al foso.</comportamiento>
      <vulnerabilidad>Vulnerable a golpe frontal de pala o pisotón aéreo.</vulnerabilidad>
    </enemigo>

    <enemigo id="guardia" rol="Enemigo melee con postura defensiva" archivo_origen="entidades.py">
      <vida valor="2"/>
      <comportamiento>
        Patrulla alerta. Si el jugador entra en su rango melee (70 px), se detiene,
        enciende sus ojos en rojo carmesí y alza su espada durante 300 ms de telegrafía antes de estocar.
      </comportamiento>
      <escudo_frontal>Bloquea ataques frontales de la pala regular. Debe ser atacado por la espalda o con pisotón.</escudo_frontal>
    </enemigo>

    <enemigo id="volador" rol="Trampolín cinético aéreo" archivo_origen="entidades.py">
      <vida valor="1"/>
      <comportamiento>Vuelo sinusoidal suspendido sobre fosos o precipicios.</comportamiento>
      <funcion_de_diseno>
        Diseñado específicamente para que el jugador use el Stomp (pisotón) y recargue
        su Dash en pleno abismo para alcanzar cornisas lejanas.
      </funcion_de_diseno>
    </enemigo>

    <jefe id="carcelero" rol="Mini-Boss de Nivel 2" archivo_origen="entidades.py">
      <vida valor="3"/>
      <fases total="1"/>
      <patron_combate>
        1. Alerta con rugido telegrafiado (550 ms).
        2. Embestida violenta a 240 px/s en línea recta hacia el jugador (400 ms).
        3. Impacto contra la pared de la arena: queda aturdido durante 1.30 s con la guardia abierta.
      </patron_combate>
      <ventana_vulnerabilidad>Solo recibe daño durante su aturdimiento tras chocar contra el muro.</ventana_vulnerabilidad>
      <recompensa>Desbloquea el acceso al altar de la Guadaña Mística.</recompensa>
    </jefe>

    <jefe id="custodio" rol="Jefe Supremo del Osario" archivo_origen="entidades.py">
      <vida total="6" fase_1="3" fase_2="3"/>
      
      <fase_1>
        <ataque_1 nombre="Corte Arcano">Mandoblazo melee precedido por destello carmesí.</ataque_1>
        <ataque_2 nombre="Onda de Choque">Golpe contra el suelo que proyecta una onda expansiva a ras de piso (300 px/s). Se esquiva saltando.</ataque_2>
        <ritmo>Pausa de vulnerabilidad de 1.10 s tras cada combo de onda.</ritmo>
      </fase_1>

      <transicion>
        Al llegar a 3 de vida, el Custodio retrocede al centro, se arrodilla.
        Se activa un flash blanco de 0.15 s, sacudida de pantalla (trauma 0.6)
        y un grito sintetizado en canal dedicado. Emerge rodeado de un AURA DORADA / CARMESÍ.
      </transicion>

      <fase_2>
        <modificador_defensa>
          Coraza frontal absoluta: la pala y la guadaña REBOTAN con un chasquido metálico si se ataca de frente.
        </modificador_defensa>
        <ataque_1 nombre="Embestida Espectral">Carga a 240 px/s seguida de doble onda sísmica simultánea.</ataque_1>
        <estrategia_requerida>
          El jugador está OBLIGADO a saltar por encima de la embestida, asestar un Pisotón Aéreo (Stomp)
          sobre su casco o flanquear con Dash para golpearle la espalda descubierta.
        </estrategia_requerida>
        <ventana_vulnerabilidad>0.85 segundos tras fallar su embestida.</ventana_vulnerabilidad>
      </fase_2>
    </jefe>
  </enemigos_jefes>

  <!-- 6. FEEDBACK AUDIOVISUAL, JUICE Y UX DIEGÉTICA -->
  <feedback_audiovisual_ux>
    <matriz_ui>
      <categoria nombre="Diegetica">
        Farol mortuorio del sepulturero (indica carga del dash con llama azul y almas con intensidad de fulgor);
        cirios votivos y faroles de checkpoint consagrados en el mundo del juego.
      </categoria>
      <categoria nombre="Espacial">
        Estelas del dash (ghosting en espacio del nivel), arcos translúcidos de corte de pala/guadaña,
        y telegrafía de ojos encendidos sobre la cabeza de los enemigos.
      </categoria>
      <categoria nombre="Meta">
        Viñeta de sangre pulsante en bordes de la pantalla cuando vidas == 1;
        sacudida de pantalla por trauma y flash escarlata al sufrir daño.
      </categoria>
      <categoria nombre="No_Diegetica">
        Riel gótico superior con orbes/calaveras de salud, medidor de enfriamiento del dash,
        y mensajes flotantes con tipografía clásica.
      </categoria>
    </matriz_ui>

    <juicing>
      <hitstop>Congelamiento de 0.08 s (5 frames a 60 fps) en colisiones críticas, permitiendo que la cámara y partículas sigan vivas.</hitstop>
      <trauma_camara formula="desplazamiento = Desplazamiento_Max * (Trauma^2)">
        Conforme a Squirrel Eiserloh (GDC 2016). Trauma escala de 0.0 a 1.0 y decae linealmente a 1.8 por segundo.
      </trauma_camara>
      <iluminacion_dinamica>
        Superficie de penumbra global (alpha 205) perforada con círculos concéntricos suaves (`BLEND_RGBA_MULT`)
        alrededor del jugador (radio 80 px), faroles (radio 140 px), velas (radio 40 px) y almas (radio 35 px).
      </iluminacion_dinamica>
    </juicing>

    <audio_arquitectura>
      <sintesis_sfx>100% nativa procedural PCM (44.1 kHz, 16-bit estéreo) con modulación FM, ADSR multicapa y detune aleatorio de ±4%.</sintesis_sfx>
      <corazon_delator>
        Pulso subsónico a 55 Hz modulado en frecuencia, activado automáticamente en bucle rítmico
        cuando el jugador queda con 1 solo corazón de vida.
      </corazon_delator>
      <dron_funebre>Zumbido espectral ambiental continuo en canal 7 para atmósfera de catacumbas.</dron_funebre>
      <musica_bgm formato="OGG_Stream" carpeta_fuente="assets_in_crypta/entrega/musica/">
        <pista nivel="0">titulo.ogg (Menús e intro)</pista>
        <pista nivel="1">camposanto.ogg (Melancolía de campanas y cuerdas)</pista>
        <pista nivel="2">cripta.ogg (Ecos de piedra y viento fúnebre)</pista>
        <pista nivel="3">osario.ogg (Órgano litúrgico y tensión rítmica)</pista>
        <pista boss_fase_1="custodio_f1.ogg" boss_fase_2="custodio_f2.ogg"/>
        <transicion_crossfade duracion="0.8" unidad="segundos"/>
      </musica_bgm>
    </audio_arquitectura>
  </feedback_audiovisual_ux>

  <!-- 7. REGLAS DE ORO PARA EL DISEÑO Y PROGRAMACIÓN EN PYTHON -->
  <directrices_ejecucion>
    <regla id="R1">NUNCA dispersar números mágicos: todo nuevo valor cinético o de combate debe declararse en config.py.</regla>
    <regla id="R2">Toda nueva sala debe respetar las métricas físicas: fosos mayores a 6 tiles deben incluir un enemigo volador para stomp o dar por hecho el Dash.</regla>
    <regla id="R3">El dibujo procedural en entidades.py debe mantener la paleta claroscuro oficial; no usar colores saturados ajenos al lore.</regla>
    <regla id="R4">Las pruebas unitarias y de lógica headless (test_logica.py) son la barrera de contención: ningún cambio de física o colisión debe romper los 38 tests existentes.</regla>
  </directrices_ejecucion>

</in_crypta_game_design>
```
