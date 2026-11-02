> **Track B — modificar la referencia.** Estos ejercicios se hacen sobre el juego
> ya implementado. Si querés construir el plataformero vos desde cero, usá
> `../EJERCICIOS_PLATAFORMERO_DESDE_CERO.md`; este proyecto queda como consulta.

# Ejercicios — Salto Pixel

> Estos ejercicios se hacen **sobre el proyecto que ya funciona**. La idea no es
> escribir un juego desde cero, sino modificar uno real, entender qué toca cada cambio
> y verificar el resultado.
>
> Guía de referencia: `GUIA_PYGAME.md`.
> Proyecto: `~/unahur/TallerDeProgramacion1/plataformero_pygame/`.
> Tests: `tests/test_logica.py`.

## Cómo trabajar cada ejercicio

Usá esta plantilla de **E/P/S** (Entrada → Proceso → Salida), tomada de Taller de
Programación I:

1. **Entrada**: ¿qué datos o teclas recibe el juego?
2. **Proceso**: ¿qué cálculo o regla cambia?
3. **Salida**: ¿qué se ve en pantalla o qué valor queda?
4. **Verificación**: ¿cómo sabés que funciona? (test, print, jugar, captura).

Reglas:

- Cambiá una cosa por vez.
- Corré `python main.py` y `tests/test_logica.py` después de cada cambio.
- Si el cambio es de física, probá con valores chicos y grandes.
- Comentá el **por qué** de las decisiones, no repitas el código.
- Nombres en `snake_case`; constantes en `MAYUSCULAS`.

---

## Ejercicio 0 — Leer y ejecutar (obligatorio)

**Objetivo:** entender el loop y la estructura antes de tocar nada.

1. Ejecutá `python main.py`.
2. Jugá el nivel 1 y el nivel 2.
3. Abrí `juego.py` y ubicá `run`, `procesar_eventos`, `actualizar`, `dibujar`.
4. Abrí `entidades.py` y ubicá `Jugador.actualizar`, `mover_x`, `mover_y`.
5. Corré los tests.

**Preguntas guía:**

- ¿Qué pasa si cambiás `FPS` a 30? ¿El personaje se mueve más lento? ¿Por qué?
- ¿Qué diferencia hay entre `KEYDOWN` y `key.get_pressed()`?
- ¿Dónde se guarda la posición del jugador: en píxeles o en tiles?
- ¿Quién dibuja el HUD: la cámara o `Juego`?

**Criterio:** podés explicar el recorrido `main.py → Juego.run → actualizar → dibujar`
sin mirar la guía.

---

## Ejercicio 1 — Cambiar la identidad visual (Fácil, C1)

**Objetivo:** modificar constantes y ver el efecto.

**Archivo:** `config.py`.

1. Cambiá `TITULO`.
2. Cambiá los colores de `AZUL`, `AMARILLO`, `MARRON` y `PASTO`.
3. Cambiá `ANCHO` y `ALTO` a `800×450`.
4. Ejecutá y ajustá lo que se rompa visualmente (por ejemplo, el HUD).

**Pistas:**

- Los colores son tuplas `(R, G, B)`.
- Si achicás la ventana, la cámara y el HUD siguen usando `ANCHO`/`ALTO`.
- No cambies todavía la física.

**Criterio:** la ventana tiene otro tamaño y paleta; el HUD sigue legible; los tests
pasan (si cambiaste `ANCHO`, revisá el test de cámara).

**Conceptos:** variables, constantes, tuplas, `config.py`, Clean Code.

---

## Ejercicio 2 — Personalizar el HUD (Fácil, C1/C2)

**Objetivo:** usar strings, `f-strings` y `font.render`.

**Archivo:** `juego.py`, método `dibujar_hud`.

1. El texto del nivel ya existe; agregá `Meta: derecha` o una flecha.
2. Mostrá la cantidad de monedas como `Monedas: 3/19` (recogidas / total).
3. Cambiá el color del tiempo a rojo cuando supere 30 segundos.
4. Si el jugador no tiene vidas, mostrá `SIN VIDAS`.

**Pistas:**

- `self.nivel.monedas` es una lista; podés contar las recogidas con un `for` o con
  `sum(1 for m in ... if m.recogida)`.
- `if self.tiempo_nivel > 30:` cambia el color antes de llamar a `dibujar_texto`.
- `f"{recogidas}/{total}"` arma el texto.

**Criterio:** el HUD muestra los datos nuevos y no tapa la barra superior.

**Conceptos:** `for`, `sum`, condicional, f-string, `font.render`.

---

## Ejercicio 3 — Diseñar una plataforma y monedas (Fácil, C2)

**Objetivo:** editar datos y entender el parser.

**Archivo:** `niveles.py`.

1. En `NIVEL_1`, agregá una plataforma de 5 tiles en la zona que quieras.
2. Agregá 3 monedas arriba.
3. Agregá un enemigo sobre una plataforma o en el piso.
4. No toques el código de `nivel.py`.

**Pistas:**

- Cada fila debe tener el mismo largo.
- `#` es sólido, `o` moneda, `E` enemigo.
- Si el enemigo queda sobre un tramo de piso, su patrulla se calcula sola.
- Si la plataforma queda muy alta, el jugador no llega: recordá que el salto supera
  unos 3 tiles.

**Criterio:** el nivel carga, la plataforma se ve, las monedas se recogen y el enemigo
patrulla sin caerse.

**Conceptos:** listas de strings, mapa ASCII, `for`, coordenadas, diseño de niveles.

---

## Ejercicio 4 — Crear un tercer nivel (Intermedio, C2/C3)

**Objetivo:** extender la estructura de datos `NIVELES`.

**Archivo:** `niveles.py`.

1. Creá `NIVEL_3` con un mapa nuevo.
2. Agregá un diccionario a `NIVELES` con `nombre`, `mapa` y `pista`.
3. Asegurate de que tenga `P` y `G`, monedas y al menos 3 enemigos.
4. Ajustá el HUD: debería decir `3/3`.
5. Jugá los tres niveles seguidos.

**Pistas:**

- Copiá `NIVEL_2` y cambiá plataformas/gaps.
- `Juego.cargar_nivel` y `siguiente_nivel` ya usan `len(NIVELES)`.
- No hardcodees `2` en ningún lado nuevo.

**Criterio:** el juego avanza 1 → 2 → 3 → victoria; los tests de niveles pasan.

**Conceptos:** listas de diccionarios, `len`, progresión, datos vs lógica.

---

## Ejercicio 5 — Validar los mapas (Intermedio, C3/C4)

**Objetivo:** escribir una función que revise datos antes de jugar.

**Archivo:** `nivel.py` o `tests/test_logica.py`.

1. Función `validar_mapa(filas)` que devuelva una lista de errores:
   - filas de distinto largo;
   - más de una `P`;
   - ninguna `P`;
   - más de una `G`;
   - ninguna `G`;
   - símbolo desconocido.
2. Llamala desde `Nivel.__init__` o desde un test.
3. Si hay errores, mostralos con `raise ValueError("\n".join(errores))`.

**Pistas:**

- Un `set` de símbolos válidos: `{".", "#", "P", "G", "o", "E"}`.
- `filas.count("P")` no sirve directo porque cada fila es un string; usá
  `sum(fila.count("P") for fila in filas)`.
- Los tests pueden comprobar un mapa inválido con `try/except ValueError`.

**Criterio:** un mapa con dos `P` o sin `G` falla con un mensaje claro.

**Conceptos:** funciones, listas, `set`, `sum`, validación, excepciones.

---

## Ejercicio 6 — Pinches (Intermedio, C3/C4)

**Objetivo:** agregar un peligro nuevo y conectarlo con las vidas.

**Archivos:** `niveles.py`, `nivel.py`, `juego.py`.

1. Elegí un símbolo, por ejemplo `^`.
2. En `Nivel`, creá una lista `pinches` con un rect por cada `^`.
3. Dibujalos como triángulos rojos.
4. En `Juego.actualizar`, si el jugador toca un pinch, llamá `perder_vida`.
5. Agregá un test que coloque al jugador sobre un pinch y verifique que pierde vida.

**Pistas:**

- No pongas pinches en el spawn.
- `pygame.draw.polygon` sirve para el triángulo.
- Después de `perder_vida`, el jugador puede quedar invulnerable; el test debe esperar
  o revisar `vidas`.

**Criterio:** el pinch se ve, quita una vida y no rompe el respawn.

**Conceptos:** listas, colisión, `if`, dibujo de polígonos, integración.

---

## Ejercicio 7 — Plataforma móvil (Intermedio, C3/C4)

**Objetivo:** crear una entidad que se mueva sola y pueda transportar al jugador.

**Archivos:** `entidades.py`, `nivel.py`, `juego.py`.

1. Creá una clase `PlataformaMovil` con `rect`, `x`, `y`, `direccion`, `rango`.
2. Actualizala en `Juego.actualizar`.
3. Dibujala en `Nivel.dibujar` o en `Juego.dibujar`.
4. Hacé que el jugador pueda pararse arriba.

**Pistas:**

- Es parecido a `Enemigo`, pero el rect es sólido.
- Para que el jugador se mueva con la plataforma, guardá el `dx` de la plataforma y
  sumáselo al jugador si está apoyado.
- Empezá con una plataforma horizontal y sin transporte; después agregá el arrastre.

**Criterio:** la plataforma se mueve, el jugador no la atraviesa y puede subirse.

**Conceptos:** clases, `self`, listas, colisión, movimiento relativo.

---

## Ejercicio 8 — Doble salto (Difícil, C3/C4)

**Objetivo:** agregar estado al jugador y una regla nueva.

**Archivo:** `entidades.py` (`Jugador`).

1. Agregá `saltos_restantes` o `salto_doble_disponible`.
2. Al tocar el suelo, restaurá el contador.
3. En `pedir_salto`, si no hay suelo pero quedan saltos, permití el impulso.
4. Mostrá en el HUD cuántos saltos quedan.
5. Cuidado: no debe poder saltar infinito en el aire.

**Pistas:**

- No metas la lógica en `Juego`: el jugador es quien conoce su estado.
- `coyote` y doble salto compiten; definí el orden.
- Un `print` temporal o un test con `assert` ayuda.

**Criterio:** el jugador puede hacer exactamente dos saltos antes de tocar suelo.

**Conceptos:** atributos, `if`, estado, timers, ajuste de física.

---

## Ejercicio 9 — Dash (Difícil, C3/C4)

**Objetivo:** agregar una habilidad con cooldown.

**Archivos:** `entidades.py`, `juego.py`, `config.py`.

1. Tecla `SHIFT` o `K_LSHIFT` para dash.
2. Durante `0.15 s`, el jugador se mueve rápido en la dirección actual.
3. Después hay `0.5 s` de cooldown.
4. Mostrá el cooldown en el HUD.
5. El dash no debe atravesar paredes.

**Pistas:**

- Usá un timer `dash_tiempo` y otro `dash_cooldown`.
- Para no atravesar paredes, seguí usando `mover_x`/`mover_y`; no teletransportes.
- El dash puede anular la gravedad durante su duración.

**Criterio:** el dash se siente distinto al movimiento normal, tiene cooldown y no
atraviesa sólidos.

**Conceptos:** timers, condicionales, constantes, input, física.

---

## Ejercicio 10 — Wall jump (Difícil, C3/C4)

**Objetivo:** detectar una pared y saltar desde ella.

**Archivo:** `entidades.py`.

1. Detectá si hay un sólido a la izquierda o derecha del jugador.
2. Si está en el aire, tocando pared y presiona salto, impulsalo hacia arriba y afuera.
3. No permitas wall jump en el suelo.
4. Agregá un nivel con dos paredes para probarlo.

**Pistas:**

- Podés reutilizar `mover_x` para saber si hubo colisión horizontal.
- Guardá `en_pared` y `lado_pared`.
- El impulso horizontal debe ser menor que el vertical.

**Criterio:** el jugador puede subir entre dos paredes y no se queda pegado.

**Conceptos:** colisión por ejes, estado, signos, física.

---

## Ejercicio 11 — Checkpoint (Intermedio, C4)

**Objetivo:** guardar un punto de respawn.

**Archivos:** `nivel.py`, `juego.py`, `niveles.py`.

1. Agregá un símbolo `C` para checkpoint.
2. Cuando el jugador lo toca, guardá su posición.
3. Al perder una vida, reaparecer en el checkpoint en vez del inicio.
4. Mostrá un mensaje `Checkpoint` durante 1 segundo.
5. Reiniciar el nivel debe borrar el checkpoint.

**Pistas:**

- `Nivel` puede devolver `checkpoint` como `None` o una tupla.
- `Juego.perder_vida` usa `self.nivel.spawn`; cambialo por `self.punto_respawn`.
- Si el checkpoint está en el aire, el jugador va a caer; validá la posición.

**Criterio:** después de activar el checkpoint, morir no devuelve al inicio.

**Conceptos:** estado, tuplas, `None`, respawn, datos del nivel.

---

## Ejercicio 12 — Récord de tiempo (Integrador, C4/C5)

**Objetivo:** guardar datos en un archivo y leerlos al iniciar.

**Archivos:** `juego.py`, `config.py`.

1. Al ganar, guardá el tiempo total en `record.txt`.
2. Al iniciar, leé el récord si existe.
3. Mostralo en el HUD o en la pantalla de victoria.
4. Si el archivo no existe, no debe romper.
5. Si el tiempo nuevo es menor, actualizalo.

**Pistas:**

- `open("record.txt", "r")` / `open("record.txt", "w")`.
- `try/except FileNotFoundError`.
- Convertí con `float(texto)`.
- No guardes el archivo dentro de `.venv`.

**Criterio:** el récord sobrevive a cerrar y abrir el juego.

**Conceptos:** archivos, `try/except`, `float`, persistencia, f-strings.

---

## Ejercicio 13 — Menú y pausa (Integrador, C3/C5)

**Objetivo:** practicar estados sin una StateMachine completa.

**Archivo:** `juego.py`.

1. Al iniciar, mostrá un menú con `Jugar` y `Salir`.
2. `ENTER` empieza; `ESC` sale.
3. En pausa, mostrá `Continuar`, `Reiniciar` y `Salir`.
4. No actualices la física mientras está en pausa.
5. Volvé al estado anterior correctamente.

**Pistas:**

- Podés agregar `self.estado = "menu"` y dibujar opciones.
- Reutilizá `dibujar_overlay`.
- No dupliques el loop: un solo `run` con estados.

**Criterio:** se puede jugar, pausar, reiniciar y salir sin bugs.

**Conceptos:** estados, condicionales, eventos, organización.

---

## Ejercicio 14 — Variantes de enemigo (Integrador, C3/C4)

**Objetivo:** convertir un enemigo en una familia de comportamientos.

**Archivos:** `entidades.py`, `nivel.py`, `niveles.py`.

1. Agregá un enemigo que se quede quieto y dispare un proyectil simple.
2. Agregá un enemigo más rápido pero que no pueda saltar.
3. Definí los tipos con un diccionario de configuración.
4. Elegí el tipo con un símbolo distinto en el mapa (por ejemplo `S` y `V`).
5. Mantené el stomp funcionando.

**Pistas:**

- Un `dict` de configuración evita `if` gigantes.
- Si el proyectil es un rect que se mueve, necesitás actualizarlo y dibujarlo.
- El daño debe pasar por `perder_vida`.

**Criterio:** hay al menos dos enemigos con comportamientos distintos y se pueden
derrotar.

**Conceptos:** diccionarios, clases, polimorfismo simple, colisiones.

---

## Ejercicio 15 — Nivel final y playtest (Integrador, LADPAE)

**Objetivo:** cerrar el proyecto con una experiencia completa.

1. Diseñá un nivel 3 más difícil.
2. Agregá un jefe simple o una secuencia de tres enemigos.
3. Agregá una pantalla de victoria con tiempo y monedas.
4. Hacé que un compañero juegue sin explicarle nada.
5. Anotá:
   - dónde se trabó;
   - qué salto le pareció injusto;
   - qué parte no se entendía;
   - qué cambiaría.
6. Aplicá **un solo** cambio a partir del feedback y volvé a probar.

**Criterio:** el nivel se puede terminar, el jefe o secuencia tiene una regla clara y
el feedback está escrito.

**Conceptos:** diseño, dificultad, evaluación, iteración, documentación.

---

## Tabla de progreso

| # | Ejercicio | Nivel | Unidad | Estado |
|---|---|---|---|---|
| 0 | Leer y ejecutar | — | — | [ ] |
| 1 | Identidad visual | Fácil | C1 | [ ] |
| 2 | HUD | Fácil | C1/C2 | [ ] |
| 3 | Plataforma y monedas | Fácil | C2 | [ ] |
| 4 | Tercer nivel | Intermedio | C2/C3 | [ ] |
| 5 | Validar mapas | Intermedio | C3/C4 | [ ] |
| 6 | Pinches | Intermedio | C3/C4 | [ ] |
| 7 | Plataforma móvil | Intermedio | C3/C4 | [ ] |
| 8 | Doble salto | Difícil | C3/C4 | [ ] |
| 9 | Dash | Difícil | C3/C4 | [ ] |
| 10 | Wall jump | Difícil | C3/C4 | [ ] |
| 11 | Checkpoint | Intermedio | C4 | [ ] |
| 12 | Récord | Integrador | C4/C5 | [ ] |
| 13 | Menú/pausa | Integrador | C3/C5 | [ ] |
| 14 | Variantes de enemigo | Integrador | C3/C4 | [ ] |
| 15 | Nivel final | Integrador | LADPAE | [ ] |

## Preguntas de reflexión

Al terminar cada ejercicio, contestá:

1. ¿Qué dato entra y qué dato sale?
2. ¿Qué parte fue código nuevo y qué parte fue reutilización?
3. ¿Qué caso borde probaste? (borde de plataforma, techo, enemigo, muerte)
4. ¿Qué cambiarías si el ejercicio tuviera que funcionar a 30 FPS?
5. ¿Qué nombre de variable o función mejorarías?

## Cómo pedir ayuda

Si te trabás, traé:

- el ejercicio;
- el error completo;
- el archivo y la línea;
- qué probaste;
- qué esperabas que pasara.

Con eso se puede diagnosticar sin adivinar. Si no hay error, mostrá el estado con
`print` o una captura.
