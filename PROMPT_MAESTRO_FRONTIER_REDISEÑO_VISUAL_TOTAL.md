# PROMPT MAESTRO PARA MODELO FRONTIER: REDISEÑO VISUAL INTEGRAL, FEEDBACK AUDIOVISUAL Y SANITIZACIÓN POEANA DE IN CRYPTA

> **Destinatario:** Modelo Frontier de Alta Capacidad (Claude 3.7 Sonnet / Gemini 1.5 Pro / GPT-4o)  
> **Rol:** Arquitecto Principal de Arte Técnico, Shaders y Game Design para el videojuego gótico 2D **IN CRYPTA** (Pygame-CE / Python 3.14).  
> **Archivos de Contexto Suministrados:**
> - `repomix/repomix_visual_y_feedback.xml` (88.8K tokens: subsistema de shaders, renderizado procedural, entidades, HUD, partículas y audio)
> - `repomix/repomix_level_game_design.xml` (103.4K tokens: mapas ASCII, parsers, validadores de diseño, bucle principal y suites de pruebas MDA)

---

## 1. MISIÓN Y ENTREGABLE ESPERADO

Tu misión es realizar el **Rediseño Visual Integral desde Cero** de todos los componentes visuales, feedback sensorial y narrativa textual de *In Crypta*, manteniendo intacta la calibración de físicas del motor (`GRAVEDAD = 1500.0`, `VELOCIDAD = 250.0`, `SALTO = -620.0`, `REBOTE_ENEMIGO = 360.0`) y la geometría espacial aprobada del **Nivel 0 (Preludio / El Ritual del Sepulturero)**.

Debes devolver una respuesta estructurada en dos partes:
1. **Especificación Técnica Completa en XML (`<especificacion_visual_in_crypta>...</especificacion_visual_in_crypta>`)**: Conteniendo todas las paletas, algoritmos de renderizado celda a celda, correcciones de shaders, nuevas clases de efectos, decoraciones y sanitización de textos.
2. **Plan Maestro de Orquestación e Instrucciones de Código**: Un plan exhaustivo y modular con diffs de código precisos para que el agente ejecutor (`Antigravity CLI`) aplique los cambios secuencialmente en el repositorio sin romper las pruebas (`pytest`, `validar_niveles.py`, `test_logica.py`).

---

## 2. DIRECTIVAS DE REDISEÑO VISUAL INTEGRAL (DESDE CERO)

### A. Mampostería, Baldosas, Paredes y Plataformas
1. **Autotiling Celda por Celda (4 Vecinos Ortogonales):**
   - Todo bloque sólido `#` debe evaluar individualmente sus 4 vecinos (`arriba`, `abajo`, `izq`, `der`) en la cuadrícula de $32 \times 32\text{ px}$.
   - **Borde Superior Transitable (Walkable Edge Cue):** Solo si `not arriba`. Se dibuja la moldura de piedra con bisel en Marfil Xilográfico (`MARFIL_XILOGRAFICO = (228, 224, 210)`), muescas de cincel cada 16px en Tinta Abisal (`(6, 5, 10)`), franja de sombra de tinta y achurado vertical de 1px cada 8px. Si el bioma es exterior (`camposanto`), se coronará con briznas de hierba fúnebre.
   - **Borde Inferior de Techo:** Solo si `not abajo`. Sombra de corte inferior de 2px y salitre/estalactitas colgantes procedurales (`SALITRE_CRIPTA = (140, 160, 190)`).
   - **Muros y Pilares Continuos:** Cuando un bloque tiene bloques adyacentes arriba y abajo, **nunca** debe dibujarse una ranura divisoria horizontal ni esquinas redondeadas. Debe renderizarse como un sillar de piedra monumental continuo y homogéneo.
2. **Estalagmitas y Estalactitas Orgánicas:**
   - Definir perfiles dentados de roca para formaciones superiores e inferiores con sombreado de corte que enmarquen las bóvedas sin invadir la caja de colisión del jugador.
3. **Plataformas Fijas y Móviles (`M`, `V`):**
   - Rediseño con herrajes de hierro forjado gótico, pernos visibles en los extremos, suspensión por cadenas tensadas y engranajes mecánicos en las plataformas móviles.
4. **Campanas / Incensarios de Resonancia (`I`):**
   - Soporte de forja arqueada visible anclado a la roca superior.
   - Campana de bronce oxidado con badajo visible.
   - Halo de resonancia concéntrico sutil en reposo que estalla en una onda de choque luminosa dorada/marfil al ser golpeada por el jugador.

### B. HUD y Renderizado de UI (Corrección de Opacidades y Bugs de Dibujo)
1. **Diagnóstico y Corrección de Alpha Blending:**
   - Corregir el bug de renderizado donde las superficies con `SRCALPHA` generan cajas negras o bandas de color oscurecidas sobre los fondos.
   - Asegurar que todos los paneles utilicen superficies translúcidas dedicadas con canal alfa uniforme (`(14, 11, 20, 210)`) y marcos heráldicos en oro viejo (`(190, 160, 90)`).
2. **Iconografía Heráldica:**
   - **Corazones de Vida:** Relicarios góticos labrados en plata con gema carmesí central para vida llena, cristal opaco para vida vacía y animación de latido/pulso al recibir daño.
   - **Contador de Almas:** Orbe etéreo giratorio con estela de partículas cian/violeta.
   - **Medidor de Dash / Guadaña:** Iconos nítidos con brillo de recarga tras rebotar en campanas.
3. **Tipografía y Cartelería:**
   - Renderizado de textos con sombra tipográfica en negro puro desplazada $(+1, +1)$ para legibilidad absoluta sobre cualquier fondo.

### C. Iluminación, Sombras y Blending
1. **Fuentes de Luz Cálida (Velas `c`, Antorchas `t`, Pebeteros):**
   - Radios concéntricos de iluminación con gradiente suave usando `pygame.BLEND_ADD` o superficies `SRCALPHA` pre-renderizadas.
   - Parpadeo procedural orgánico (flicker) basado en funciones senoidales desfasadas.
2. **Fuentes de Luz Fría y Espectral (Faroles `F`, Almas `o`, Incensarios `I`):**
   - Auras cian y violeta translúcidas con halos difuminados que bañan la mampostería circundante.
3. **Viñeteado y Niebla:**
   - Viñeta perimetral elíptica que oscurece suavemente los bordes del visor virtual ($1024 \times 576$) concentrando la mirada en la acción.
   - Capa de niebla baja con movimiento horizontal continuo a velocidad de paralaje diferenciada.

### D. Game Feel y Feedback Audiovisual Asertivo
1. **Estela del Dash:**
   - Generación de 3 fantasmas translúcidos del sprite/silueta del jugador con decaimiento rápido de alfa ($0.15\text{s}$).
2. **Hitsparks de Impacto:**
   - Sustituir destellos genéricos por chispas de mampostería quebrada, esirlas de piedra y salpicaduras de ectoplasma oscuro.
3. **Disolución de Enemigos al Morir:**
   - Desvanecimiento etéreo con partículas de ceniza que ascienden lentamente hacia la bóveda.
4. **Sacudida de Pantalla y Flash:**
   - Curvas de decaimiento cuadráticas para eliminar sacudidas toscas; duración áurea de $0.12\text{s}$ para impactos normales y $0.25\text{s}$ para jefes.

---

## 3. REESCALADO Y PRESENTACIÓN DE MONSTRUOS

1. **Reescalado Proporcional (-10% a -15%):**
   - Ajustar las dimensiones de dibujo de las criaturas para evitar que se sientan gigantescas o bloqueen la visual en corredores de 3-4 tiles:
     - **Morador del Camposanto (`E`):** Rediseñar a $24 \times 24\text{ px}$. Silueta encorvada, andrajos fúnebres, ojos amarillentos titilantes.
     - **Guardia Melee (`L`):** Rediseñar a $24 \times 26\text{ px}$. Armadura oxidada medieval, yelmo con hendidura roja, espada ancha apoyada.
     - **Polilla Espectral (`m`):** Rediseñar a $22 \times 22\text{ px}$. Alas membranosas translúcidas con aleteo senoidal suave.
     - **Cuervo del Osario (`C`):** Rediseñar a $20 \times 20\text{ px}$. Vuelo poeano articulado con desprendimiento de plumas negras.
     - **Araña de la Cripta (`A`):** Rediseñar a $24 \times 18\text{ px}$. Patas articuladas, abdomen globoso y marcha rápida.
2. **Telegrafiado Visual Orgánico:**
   - Eliminar cajas o rectángulos planos de advertencia.
   - Implementar halos rítmicos de advertencia proyectados sobre el suelo y cambio de color en los ojos de la criatura $0.4\text{s}$ antes del golpe.

---

## 4. SANITIZACIÓN LITERARIA POEANA DE TEXTOS

**Directiva Estricta:** Erradicar cualquier vestigio de redacción técnica, mensajes de depuración o estilo "juego en desarrollo". Todos los textos del juego (carteles tutoriales, pistas, diálogos, descripciones) deben reformularse en una prosa poética, litúrgica y fúnebre inspirada en la obra de **Edgar Allan Poe** (*El Cuervo*, *La Caída de la Casa Usher*, *Berenice*, *El Pozo y el Péndulo*).

### Tabla de Equivalencias Obligatorias para el Nivel 0 (Preludio):

| Zona | Texto Actual (A Erradicar) | Nueva Redacción Poeana Sanitizada |
| :--- | :--- | :--- |
| **Piso 0 - Inicio** | `[ESPACIO] Salto Variable: toque corto para escalones, mantener para muros altos` | *«La cripta exige templanza: la levedad del paso libra el peldaño roto; la firmeza de la voluntad corona el muro sellado.»* |
| **Piso 0 - Losas** | `[LOSAS] Las piedras frágiles (~~) colapsan tras pisarlas: cruzá sin dudar` | *«Lajas carcomidas por el tiempo. Al hollar su faz, la piedra cede al abismo: no vaciles en tu travesía.»* |
| **Piso 0 - Campana** | `[CAMPANA] Caé sobre la Campana (I) para propulsarte a la cornisa alta` | *«El bronce litúrgico resuena en la penumbra. Su eco férreo impulsa tu salto hacia las alturas inaccesibles.»* |
| **Piso 0 - Plataforma** | `[MÓVIL] Plataforma horizontal (M): sincronizá el salto sobre el abismo` | *«Piedra errante suspendida sobre el vacío. Aguarda su cadencia antes de confiarte a su seno.»* |
| **Piso 0 - Ascensor** | `[ASCENSOR] Plataforma vertical (V): abordala para ascender a la terraza` | *«El contrapeso de la cripta despierta: asciende en sus andamios hacia el atrio de las ánimas.»* |
| **Piso 0 - Farol** | `[FAROL] Consagrá almas en el Farol (F) y sorteá al Morador con pisotón` | *«Faro sepulcral. Deposita las ánimas dispersas para encender su lumbre y apaciguar las sombras del erial.»* |
| **Piso 0 - Pozo** | `[POZO] El Gran Abismo: descendé por las losas hacia la catacumba profunda` | *«La garganta ancestral de la tierra. Desciende al vientre de las catacumbas, donde la luz jamás reinó.»* |
| **Piso 1 - Aterrizaje** | `[CATACUMBAS] Aterrizaje seguro. Avanzá hacia el oeste por las galerías` | *«Las profundidades de la cripta te reciben en silencio. Avanza por los pasajes olvidados de los muertos.»* |
| **Piso 1 - Guardia** | `[GUARDIA] El Guardia (L) confinado telegrafía su estocada: observalo desde la pasarela` | *«El carcelero de hierro vela el corredor. Observa su acero ciego antes de descender a su dominio.»* |
| **Piso 1 - Polilla** | `[POLILLA] La Polilla (m) en la arcada superior: cruzá por el pasaje inferior` | *«Aleteo de alas espectrales en la arcada alta. Cruza el umbral bajo su vuelo ceniciento.»* |
| **Piso 1 - Cuervo** | `[CUERVO] El Cuervo (C) sobrevuela en círculo en la cúpula: medí su cadencia` | *«El vigía de alas negras dibuja círculos fúnebres en la cúpula. Mide su compás antes del salto.»* |
| **Piso 1 - Araña** | `[ARAÑA] La Araña (A) confinada vigila su cornisa: avanzá con paso firme` | *«Tejedora del osario. Reina en su roca suspendida; mantén el paso firme en la piedra baja.»* |
| **Piso 1 - Campana 1** | `[CAMPANA I] Caé sobre la Campana para rebotar sobre el foso seco` | *«El primer repique de campana. Libra el foso seco con el vuelo de su resonancia sagrada.»* |
| **Piso 1 - Doble Rebote** | `[DOBLE REBOTE] Encadená rebotes entre dos campanas en el aire` | *«Resonancia encadenada. Encuentra el ritmo de dos bronces sin posar los pies en la tierra.»* |
| **Piso 1 - Móvil + Campana** | `[ASCENSOR & CAMPANA] Elevate en la plataforma (V) y saltá hacia la campana` | *«Elevación y repique. Deja que el andamio te alce hacia el incensario suspendido en la bóveda.»* |
| **Piso 1 - 4 Campanas** | `[ASCENSIÓN FINAL] Encadená 4 campanas en subida para sobrevolar la muralla` | *«La Gran Ascensión del Campanario. Cuatro golpes de bronce labran tu vuelo sobre la monumental muralla.»* |
| **Piso 1 - Portón** | `[PORTÓN] Cruzá el Portón (G) para ingresar a El Camposanto` | *«El Portón Litúrgico aguarda consagrado. Cruza el umbral final y adéntrate en los misterios de El Camposanto.»* |

---

## 5. CINCO EJEMPLOS DE DISEÑO Y NUEVOS CARACTERES ASCII

Debes proporcionar **cinco especificaciones de diseño distintas**, abarcando la riqueza de los biomas del juego y la nueva mecánica de pisos verticales estancos:

1. **Diseño 1: El Atrio de las Candelas (Bioma Camposanto / Superficie)**
   - Atmósfera: Cielo crepuscular con luna lejana, cruces inclinadas, mausoleos de piedra tosca y maleza fúnebre.
2. **Diseño 2: Las Catacumbas del Salitre (Bioma Cripta Subterránea / Piso 1)**
   - Atmósfera: Bóvedas góticas con estalagmitas y estalactitas, tracería con haz de luz lunar filtrado, arcos apuntados continuos y pebeteros.
3. **Diseño 3: La Torre del Campanario Litúrgico (Vertical Ascendente)**
   - Atmósfera: Arquitectura de fortaleza estilo SMB3 con múltiples cadenas tensadas, contrapesos móviles y carillones suspendidos.
4. **Diseño 4: La Nave Inundada del Osario (Bioma Osario)**
   - Atmósfera: Mosaicos de calaveras talladas en sillería de piedra, huesos entrecruzados, losas quebradizas sobre fosas secas y antorchas espectrales de llama azul.
5. **Diseño 5: El Claustro Ceremonial Bi-Nivel (Descenso Estanco por Pozo)**
   - Atmósfera: Transición vertical perfecta entre un nivel superior de jardín fúnebre y una cripta subterránea profunda mediante un pozo de losas quebradizas, con conmutación dinámica de fondos y nieblas.

### Nuevos Caracteres ASCII para Decoración y Atmósfera:
Diseñar y documentar la integración en `nivel.py:_crear_decoraciones()` de:
- `j`: **Cadena de Hierro Colgante** (elemento puramente visual que cuelga de techos `#`).
- `g`: **Gárgola Ornamental** de piedra apoyada en repisas.
- `u`: **Urna Cineraria Tallada** apoyada en suelos o nichos.
- `b`: **Antorcha Espectral Azul** con halo frío.

---

## 6. INSTRUCCIONES DE RESPUESTA

Entrega tu respuesta estructurada exactamente como:
1. **`<especificacion_visual_in_crypta>`**: Especificación completa XML con todas las paletas RGB, fórmulas de autotiling, parámetros de shaders, tablas de textos poeanos y los 5 ejemplos de diseño.
2. **`### PLAN MAESTRO DE ORQUESTACIÓN PARA ANTIGRAVITY CLI`**: Lista secuencial de tareas con archivos afectados, funciones específicas a modificar y verificaciones de no-regresión.
