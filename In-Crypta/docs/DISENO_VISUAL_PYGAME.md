# DISEÑO VISUAL PARA PLATAFORMERO 2D EN PYGAME — DOCUMENTACIÓN EXHAUSTIVA

Proyecto: **IN CRYPTA** — Plataformero gótico 2D de tres niveles
Motor: **Python + pygame-ce**
Referencias: Blasphemous · Castlevania · Ender Lilies

---

## 1. MARCO TEÓRICO Y ACADÉMICO

### 1.1 Matriz MDA (Hunicke, LeBlanc, Zubek — 2004)
La matriz MDA separa el juego en tres capas:

| Capa | Definición | En IN CRYPTA |
|---|---|---|
| **Mecánicas** | Reglas y acciones del sistema | Salto, dash de sombra, golpe de pala |
| **Dinámicas** | Comportamiento que emerge al jugar | Encadenar salto+dash+pala, usar morador como rebote |
| **Estéticas** | Respuesta emocional del jugador | **Desafío** (precisión) y **Sensación** (oscuridad, velocidad, feedback) |

**Diseño visual parte de mecánicas hacia estéticas.** Cada acción mecánica debe tener una contraparte visual y sonora inmediata para que el jugador perciba la dinámica y alcance la estética deseada.

### 1.2 Game Feel / Juice (Jonasson & Purho, GDC 2013)
El "juice" es el feedback excesivo y satisfactorio que confirma cada acción. Principios clave aplicados al proyecto:

- **Cada acción deja una marca:** salto genera polvo, dash deja estela, golpe genera explosión de partículas.
- **Sacudida de cámara:** impacto, daño y golpe de pala sacuden la cámara con fuerza y duración escaladas según la intensidad del evento.
- **Flash de pantalla:** daño genera flash rojo; golpe de pala genera flash amarillo breve.
- **Feedback redundante:** partícula + sonido + cámara + HUD simultáneos. Nunca un solo canal.

### 1.3 Principios de UI/UX para juegos
- **Claridad sobre estética:** nunca ocultar información por "atmósfera oscura". Pinchos brillan, portón resalta, dash tiene barra y estela.
- **Hitbox menor que el sprite visual:** el jugador mide 24×30 px aunque parezca más grande, evitando muertes injustas.
- **Ayudas invisibles:** coyote time (0.18 s), jump buffer (0.15 s), corte de salto. Mejoran la sensación sin cambiar el desafío visible.
- **Invulnerabilidad breve tras daño:** parpadeo del sprite y ventana de 1.2 s sin recibir daño adicional.

---

## 2. HERRAMIENTAS DE DIBUJO DE PYGAME — REFERENCIA TÉCNICA

Toda la documentación técnica consultada proviene de `pygame.org/docs` (v2.6.0): `draw`, `Surface`, `font`, `transform`, `image`.

### 2.1 `pygame.draw` — Primitivas geométricas

| Función | Uso en el proyecto | Parámetros clave |
|---|---|---|
| `rect` | Paneles HUD, bloques sólidos, plataformas, cuerpo del jugador | `border_radius`, `width` (0 = relleno) |
| `polygon` | Pinchos, lápida, guadaña, cráneos, estadísticas | `points`, `width` |
| `circle` | Almas, ojos, farol, cabeza, portón, burbujas | `draw_top_right`, `draw_bottom_left`, etc. (cuadrantes) |
| `ellipse` | Sombras bajo pies, cuerpo de enemigos, aura del jefe | `rect`, `width` |
| `arc` | Olas de huesos del jefe, detalles decorativos | `start_angle`, `stop_angle` (radianes) |
| `line` | Costillas, raíces, espada de pala, detalles de tumba | `width` |
| `lines` | Secuencias de costillas, bordes decorativos | `closed`, `points`, `width` |
| `aaline` / `aalines` | Líneas finas antialiasadas en UI y detalles | `blend` |

**Buena práctica:** `width == 0` rellena; `width > 0` dibuja contorno. `border_radius` disponible en `rect` desde pygame 2.1.1 para paneles redondeados.

### 2.2 `pygame.Surface` — Superficies y transparencia

| Método | Uso en el proyecto |
|---|---|
| `SRCALPHA` | Paneles HUD semitransparentes, vineta, overlays de pausa, auras de jefe |
| `convert_alpha()` | Imágenes PNG con transparencia (si se usaran assets externos) |
| `set_alpha()` | Opacidad global de vineta y velos |
| `set_colorkey()` | Transparencia por color clave (alternativa a alpha) |
| `blit()` / `blits()` | Dibujar una o muchas superficies sobre otra; `BLEND_RGBA_ADD` para brillos aditivos |
| `fill()` | Fondos degradados (línea por línea), limpieza de paneles |
| `lock()` / `unlock()` | Acceso directo a píxeles (no usado en el proyecto, pero disponible para efectos de píxel) |
| `subsurface()` | Recortes de superficies mayores (no usado directamente) |

**Buena práctica:** Para brillos de alma y pala, el proyecto usa `BLEND_RGBA_ADD` con superficies `SRCALPHA` y círculos concéntricos de alpha decreciente.

### 2.3 `pygame.transform` — Transformaciones de superficie

| Función | Uso recomendado |
|---|---|
| `scale` / `scale_by` | Escalar assets de tiles y sprites al tamaño del tile (32 px) |
| `scale2x` | Doble escala de arte pixel sin suavizar (estilo 8-bit) |
| `smoothscale` | Escalado suave para UI o fondos |
| `flip` | Voltear sprites horizontalmente para cambiar dirección (jugador, enemigos) |
| `rotate` / `rotozoom` | Rotar proyectiles, partículas o elementos decorativos |

**Buena práctica:** Nunca transformar una superficie ya transformada (pierde calidad). Siempre partir del original y aplicar `scale`/`rotozoom` directo.

### 2.4 `pygame.font` — Tipografía

| Método | Uso en el proyecto |
|---|---|
| `Font` / `SysFont` | Cargar fuentes para HUD, título, overlays |
| `render` | Generar superficie de texto (una línea) |
| `size` | Calcular ancho/alto antes de posicionar (word wrap manual) |
| `get_linesize` | Espaciado entre líneas de párrafos |
| Sombra | Renderizar texto dos veces (negro desplazado + color real) para legibilidad sobre fondos oscuros |

**Buena práctica:** El proyecto renderiza sombra manualmente (`dibujar_texto` con `sombra=True`) para garantizar legibilidad sobre cualquier fondo. El HUD usa fuente pequeña (12–19 px) y título grande (92 px).

### 2.5 `pygame.image` — Carga de assets

| Función | Uso |
|---|---|
| `load` | Cargar PNG, BMP, JPG, etc. |
| `convert_alpha()` | Preparar imágenes con transparencia per-pixel para blit rápido |
| `save` / `save_extended` | Exportar capturas de pantalla (`tools/capturar.py`) |

**Nota del proyecto:** IN CRYPTA no usa imágenes externas; todo se dibuja con primitivas `pygame.draw`. Esto reduce dependencias y permite cambiar colores dinámicamente por tema de nivel.

---

## 3. APLICACIÓN AL HUD (Juego.py: `dibujar_hud`)

### 3.1 Estructura de paneles
- Barra angosta de **36 px** de alto en la parte superior.
- `HUD_PANEL = (18, 14, 24, 196)` — negro gótico con alpha 196 (semitransparente).
- `HUD_BORDE = (104, 82, 52)` — borde dorado oscuro.
- Esquinas decorativas con líneas doradas en las esquinas del panel (`dibujar_panel_hud`).

### 3.2 Elementos de información
| Elemento | Posición | Visual |
|---|---|---|
| Nivel y tiempo | Arriba-izq | Texto oro + blanco |
| Almas y progreso a vida extra | Arriba-der | Icono de alma (diamante violeta) + contador + barra segmentada (10 segmentos) |
| Vidas | Arriba-der | Hasta 5 corazones (rellenos rojo, vacíos oscuros) |
| Dash | Abajo-izq | Barra verde si listo, muted si en cooldown |
| Golpe de pala | Abajo-der | Barra oro si tiene pala y listo |
| Barra de jefe | Centro-arriba (Nivel 3) | Nombre, fase, 3 segmentos de voluntad (rojos) |
| Aviso de jefe | Centro | Texto centrado con sombra ("LA SALIDA ESTÁ SELLADA") |
| Pista de ayuda | Centro-abajo | Caja semitransparente con borde dorado, texto envuelto |

### 3.3 Técnicas visuales de HUD
- **Sombra en texto:** `dibujar_texto` dibuja el texto negro en `(x+3, y+3)` antes del color real para contraste sobre fondos oscuros.
- **Barras segmentadas:** `dibujar_barra_hud` divide la barra en celdas según `segmentos` (ej. 10 almas para vida extra).
- **Paneles con `SRCALPHA`:** superficies con alpha para que el juego se vea detrás del HUD sin taparlo completamente.
- **Overlay de estados:** pausa, derrota y victoria usan `SOMBRA = (7, 6, 10, 205)` como velo semitransparente sobre toda la pantalla.

---

## 4. APLICACIÓN A TILES Y NIVELES (`nivel.py`)

### 4.1 Mapa ASCII
Cada carácter del mapa ASCII se interpreta como un objeto de juego:
- `#` → bloque sólido (`dibujar_solidos`)
- `o` → alma
- `E` / `L` / `C` / `m` / `A` → enemigos
- `W` → pala recogible
- `X` → power-up de rango
- `P` → spawn
- `G` → meta/portón
- `^` → peligro (pinchos)
- `M` / `V` → plataformas móviles (horizontal / vertical)
- `t`, `c`, `r`, `b`, `s` → decoraciones (tumba, vela, raíz, huesos, estatua)

### 4.2 Temas visuales por nivel

| Tema | Color piso | Borde | Detalle arriba | Fondo |
|---|---|---|---|---|
| **Camposanto** | `MARRON` (86,63,48) | `MARRON_OSCURO` | `PASTO` (66,88,60) | Luna, estrellas, árboles muertos, tumbas lejanas |
| **Cripta** | `PIEDRA_FRIA` (58,61,72) | Oscuro | `MUSGO` (72,94,62) | Ventanal gótico, cadenas colgantes, velas lejanas |
| **Osario** | (62,45,43) | (32,22,24) | (96,60,54) | Costillas gigantes, niebla roja |

### 4.3 Dibujo de sólidos (`dibujar_solidos`)
- **Pisos:** color de fondo + borde + detalle de hierba/musgo arriba + juntas de piedra cada `TILE` (32 px).
- **Paredes:** `PIEDRA` + `PIEDRA_OSCURA` + detalle interno + línea inferior.
- **Cámara:** `is_on_screen` con margen de 64 px para no dibujar lo que no se ve (optimización).

### 4.4 Decoraciones (`dibujar_decoraciones`)
Dibujadas puramente con primitivas `pygame.draw`:
- **Tumba:** rectángulo redondeado + línea de grieta + cruz simple.
- **Vela:** círculo base marrón, rectángulo cera, llama amarilla con polígono.
- **Raíz:** líneas marrones en zigzag.
- **Huesos:** dos líneas cruzadas + dos círculos en extremos.
- **Estatua:** rectángulo redondeado + círculo cabeza + detalles de musgo.

### 4.5 Peligros (`dibujar_peligros`)
- Pinchos: triángulos en fila con una línea central hueso para resaltar la punta. **Siempre visibles**, nunca camuflados con el fondo (principio de desafío justo).

### 4.6 Meta / Portón (`dibujar_meta`)
- Círculo base oscuro, rectángulo central, líneas laterales, arco superior.
- Núcleo oro con brillo amarillo (`AMARILLO`, `(255, 235, 170)`).
- Línea `SANGRE` en la base para anclarlo al suelo.

### 4.7 Plataformas móviles (`dibujar_plataformas`)
- Rectángulo principal gris oscuro `(63,57,68)` con borde más oscuro.
- Línea oro superior y línea gris inferior para dar volumen.
- `border_radius=3` para suavizar esquinas.

---

## 5. APLICACIÓN A PERSONAJES Y ENEMIGOS (`entidades.py`)

### 5.1 Jugador — El Sepulturero
Dibujo compuesto por capas con `pygame.draw`:

| Parte | Técnica | Colores |
|---|---|---|
| Sombra bajo pies | `ellipse` `(7,6,10)` | Sombra proyectada |
| Abrigo | `rect` `AZUL_OSCURO` + `rect` `MARRON` + borde `NEGRO` | Azul gótico + marrón |
| Delantal | `rect` `MARRON_OSCURO` sobre el abrigo | Marrón oscuro |
| Cabeza | `circle` `CREMA` + borde `NEGRO` + `rect` ala ancha | Crema + negro |
| Sombrero | `rect` `NEGRO` + `rect` `MARRON_OSCURO` + línea `SANGRE` | Ala ancha gótica |
| Ojo | `circle` `NEGRO` desplazado según `direccion` | Mirada direccional |
| Bufanda | `rect` `SANGRE` | Rojo sangre |
| Farol | `circle` `(120,86,34)` + `circle` `AMARILLO` + línea `GRIS` | Única luz del personaje |
| Piernas/botas | `line` `MARRON_OSCURO` + `line` `NEGRO` | Pose varia según estado |
| Pala | `line` `MARRON` + `polygon` `GRIS` (hoja) | Al hombro o extendida en ataque |
| Fantasmas de dash | 3 `rect` desplazados en dirección opuesta al dash | `(38,30,55)`, `(64,50,92)`, `(92,74,128)` |
| Brillo de dash | `rect` `TURQUESA` alrededor del cuerpo durante el dash | Turquesa `(92,190,174)` |

**Poses:** `ataque1`, `ataque2`, `ataque3` (secuencia de golpe), `caida` (salto), `None` (idle/caminata con animación de seno en piernas).

### 5.2 Enemigos — Moradores de la Cripta
- **Cuerpo:** `ellipse` `VERDE_OSCURO` encorvado.
- **Cráneo:** `circle` `HUESO` + borde `NEGRO`.
- **Ojos:** 2 círculos `ROJO` pequeños.
- **Boca:** `rect` `NEGRO` delgada.
- **Costillas:** 3 líneas `MUSGO` horizontales.
- **Garras:** líneas `HUESO` en pies.
- **Sombra:** `ellipse` negra bajo los pies.
- **Animación:** seno en `base_y` para efecto de flotación suave (`salto = int(sin(tiempo * 7) * 2)`).

### 5.3 Jefe — El Custodio del Osario
- **Capa y joroba:** `polygon` `(38,31,44)` + `rect` `(23,20,28)` redondeado.
- **Cráneo:** `circle` `HUESO` + ojos que cambian de color cuando es vulnerable (`AMARILLO` dorado vs `ROJO`).
- **Farol incrustado:** `circle` `(122,82,30)` + `circle` `AMARILLO` en el cráneo.
- **Pala rota:** `line` `MARRON` + `polygon` `GRIS` rota.
- **Aura de vulnerabilidad:** `ellipse` con `SRCALPHA` y `BLEND_RGBA_ADD`, color `(255,205,95,30)`.
- **Telegrafía de ataque:** `ellipse` roja pulsante `(170,30,38, alpha)` antes del golpe.
- **Ondas de huesos (`OndaCustodio`):** `arc` hueso claro y oscuro, líneas verticales simulando huesos.

### 5.4 Alma (`Alma`)
- Círculo base oscuro `(54,38,76)` + círculo violeta `VIOLETA` + destello blanco `BLANCO`.
- Estela turquesa `TURQUESA` (polígono diamante).
- Movimiento: senoidal en Y (`sin(tiempo * 5) * 3`) para flotación.
- Recogida: desaparece al colisionar con el jugador.

### 5.5 Pala Recogible (`PalaRecogible`)
- Brillo aditivo: superficie `SRCALPHA` de 64×64 con 3 círculos concéntricos de alpha decreciente, bliteada con `BLEND_RGBA_ADD`.
- Círculo central dorado pulsante `(238,188,86)`.
- Partículas giratorias alrededor (4 posiciones con `cos`/`sen`).
- Línea marrón y polígono gris como hoja de la pala.
- Rotación continua basada en `tiempo`.

---

## 6. EFECTOS VISUALES Y PARTÍCULAS (`particulas.py`)

### 6.1 Sistema de partículas
Cada partícula tiene: posición, velocidad, vida, color, tamaño, gravedad. Se actualizan con integración de Euler simple y se dibujan como círculos (`pygame.draw.circle`).

### 6.2 Emisores por acción

| Acción | Cantidad | Colores | Vida | Tamaño | Gravedad | Uso |
|---|---|---|---|---|---|---|
| Salto | 5 | HUESO, crema | 0.3 s | 3 px | 300 | Polvo al saltar |
| Dash | 3 | Violeta, blanco | 0.18–0.35 s | 2–5 px | 0 | Estela direccional |
| Ataque | 7 | Amarillo, blanco | 0.12–0.24 s | 2–4 px | 80 | Chispas de golpe |
| Daño | 16 | Rojo, blanco | 0.6 s | 5 px | 700 | Explosión de impacto |
| Alma | 12 | Violeta, turquesa, blanco | 0.6 s | 4 px | 120 | Destello al recoger |
| Pala | 14 | Hueso, sangre, rojo, naranja | 0.55 s | 5 px | 600 | Al recoger pala |
| Meta | 30 | Amarillo, blanco, turquesa, violeta | 1.0 s | 5 px | 300 | Explosión de victoria |
| Jefe onda | 16 | Hueso, crema, marrón | 0.55 s | 5 px | 620 | Al lanzar onda |
| Jefe fase | 24 | Oro, amarillo, hueso | 0.8 s | 5 px | 280 | Cambio de fase |

**Buena práctica:** Las partículas se limpian cada frame (`self.particulas = [p for p in self.particulas if p.vida > 0]`) para no acumular objetos.

---

## 7. CÁMARA Y EFECTOS DE PANTALLA (`camara.py` + `juego.py`)

### 7.1 Cámara
- Seguimiento suave con interpolación lineal: `factor = min(1.0, CAMARA_SUAVIZADO * dt)`.
- Límites de nivel para no mostrar vacío más allá de los bordes.
- Centrado si el nivel es más pequeño que la pantalla.

### 7.2 Sacudida (`sacudir`)
- Fuerza y duración configurables por evento (dash: 3.5/0.10, golpe: 5.0/0.12, daño: 9.0/0.22, jefe: 11.0/0.26).
- Descaimiento lineal de la intensidad durante la duración.
- Offset aleatorio aplicado a todas las coordenadas de mundo al dibujar.

### 7.3 Flash de pantalla (`juego.py`)
- `flash_color` + `flash` (tiempo restante).
- Superficie `SRCALPHA` del tamaño de pantalla con color y alfa proporcional a `flash / 0.16`.
- Usado para daño (rojo), golpe (amarillo), vida extra (amarillo).

### 7.4 Vineta (`crear_vineta`)
- 24 elipses concéntricas negras con alpha decreciente hacia los bordes.
- Efecto de encuadre que enfoca la atención en el centro.

### 7.5 Fondos por tema (`crear_fondo` + `dibujar_fondo_*`)
- Degradado vertical línea por línea (`pygame.draw.line`).
- **Camposanto:** luna con círculos concéntricos, estrellas aleatorias.
- **Cripta:** ventanal gótico (rectángulo + arcos), cadenas colgantes (elipses en columna), resplandor de velas.
- **Osario:** costillas gigantes (arcos), niebla roja en el suelo.
- **Niebla:** bandas horizontales `SRCALPHA` con alpha baja en la parte inferior de la pantalla.

---

## 8. MEJORES PRÁCTICAS RESUMIDAS (APLICABLES A CUALQUIER PLATAFORMERO 2D)

### 8.1 Dibujo con `pygame.draw`
1. **Nunca uses imágenes externas si puedes evitarlo:** las primitivas permiten cambiar colores por tema y reducen assets.
2. **Usa `SRCALPHA` para todo lo semitransparente:** paneles HUD, vineta, overlays, auras.
3. **Usa `BLEND_RGBA_ADD` para brillos:** almas, pala, portón, efectos mágicos.
4. **Dibuja sombra de texto manualmente:** garantiza legibilidad sobre cualquier fondo.
5. **Agrupa dibujo por capa:** fondo → nivel → entidades → partículas → vineta → HUD → overlays → flash.

### 8.2 Optimización de rendimiento
1. **`is_on_screen` con margen:** no dibujes entidades fuera de la cámara (margen 64 px para bordes).
2. **`blits` por lote:** si dibujas muchas superficies similares, usa `Surface.blits` en lugar de múltiples `blit`.
3. **Evita `transform` repetido:** parte siempre de la superficie original para escalar/rotar.
4. **Limpiar partículas muertas:** filtra la lista cada frame.

### 8.3 Diseño visual para claridad (Game Feel)
1. **Feedback redundante:** cada acción importante debe tener partícula + sonido + efecto de cámara.
2. **Hitbox menor que el sprite visual:** evita muertes por píxeles que el jugador no percibe como peligrosos.
3. **Nunca oculte peligros en la oscuridad:** pinchos brillan, portón resalta, el dash tiene estela y barra.
4. **Paleta limitada y consistente:** define colores en `config.py` y reutilízalos en todo el proyecto.
5. **Ayudas invisibles:** coyote time, jump buffer, invulnerabilidad breve mejoran la sensación sin reducir el desafío.

### 8.4 Estructura recomendada de archivos
```
proyecto/
├── config.py          # Constantes, paleta, físicas, HUD
├── main.py            # Arranque
├── juego.py           # Bucle, estados, HUD, fondos, dibujado principal
├── camara.py          # Seguimiento y sacudida
├── nivel.py           # Mapa ASCII, dibujo de tiles y decoraciones
├── entidades.py       # Jugador, enemigos, jefe, almas, objetos
├── particulas.py      # Sistema de partículas por acción
├── audio.py           # Sonidos y música
├── niveles.py         # Datos de mapas ASCII
├── tools/
│   └── capturar.py    # Capturas headless para documentación
├── docs/
│   ├── GDD_MDA.md     # Diseño y matriz MDA
│   └── DISENO_VISUAL_PYGAME.md  # Este documento
└── capturas/          # Imágenes generadas
```

---

## 9. EJEMPLO DE CÓDIGO: PANEL HUD SEMITRANSPARENTE

```python
def dibujar_panel_hud(self, rect):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, HUD_PANEL, (0, 0, rect.width, rect.height), border_radius=9)
    pygame.draw.rect(panel, (*HUD_BORDE, 160), (0, 0, rect.width, rect.height), 1, border_radius=9)
    pygame.draw.line(panel, (*HUD_ORO, 105), (12, 1), (rect.width - 12, 1), 1)
    self.pantalla.blit(panel, rect.topleft)
```

## 10. EJEMPLO DE CÓDIGO: BRILLO ADITIVO (ALMA / PALA)

```python
brillo = pygame.Surface((64, 64), pygame.SRCALPHA)
for radio, alfa in ((27, 24), (20, 42), (13, 72)):
    pygame.draw.circle(brillo, (200, 100, 255, alfa), (32, 32), radio)
surface.blit(brillo, (rect.centerx - 32, rect.centery - 32), special_flags=pygame.BLEND_RGBA_ADD)
```

---

**Fuentes consultadas:**
- Documentación oficial pygame v2.6.0: `draw`, `Surface`, `font`, `transform`, `image` (pygame.org/docs)
- Código fuente del proyecto IN CRYPTA (`config.py`, `nivel.py`, `entidades.py`, `particulas.py`, `camara.py`, `juego.py`)
- GDD_MDA.md del proyecto (matriz MDA, estéticas, UI/UX, game feel)
- Hunicke, LeBlanc & Zubek (2004) — MDA: A Formal Approach to Game Design and Game Research
- Jonasson & Purho (GDC 2013) — Juice It or Lose It
