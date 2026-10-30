# Guion de presentación — IN CRYPTA

**Duración objetivo:** 6 a 8 minutos.  
**Formato:** 6 diapositivas + demo jugable.  
**Regla:** no leer el GDD; contar las decisiones y mostrar el juego.

---

## Antes de empezar

1. Abrir `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` en GDevelop o servir `export/gdevelop_nativo/build/` por HTTP.
2. Dejar la ventana en pantalla completa; el render es 1920 × 1080.
3. Tener a mano `docs/GDD_MDA.md` y las capturas de `capturas/` por si falla la demo.
4. Probar 10 segundos: mover, saltar y dash en el Nivel 1; recoger la pala y atacar en el Nivel 2; pausa.
5. El build nativo ya incluye SFX WAV de salto, alma, dash, pala, golpe, daño, portón, recogida de pala, vida extra y UI; el prototipo Pygame suma sonidos procedurales y mute con `M`.

**Controles para decir en voz alta:**
- `← / →`: mover.
- `↑`: saltar.
- `SHIFT`: dash.
- `A`: golpe de pala (se desbloquea al recogerla en el Nivel 2).
- `ESC`: pausa.
- `ENTER`: confirmar en los menús.

---

## Diapositiva 1 — Título (20 s)

**Decir:**
> “IN CRYPTA. Es un plataformero gótico 2D de tres niveles, hecho primero en Pygame y presentado en GDevelop. La pregunta que guió el diseño fue: ¿cómo hacer un juego chico que enseñe y demuestre MDA, UI/UX, curva de dificultad y sistemas?”

**Mostrar:** la pantalla de título o el juego en el portón final.

---

## Diapositiva 2 — High concept y pitch (40 s)

**Decir:**
> “Un sepulturero baja a la cripta a cumplir su jornada. La puerta se cierra detrás de él y la oscuridad despierta. Tiene que cruzar el camposanto, la cripta y el osario para escapar.”

> “En una frase: un plataformero de precisión donde un sepulturero escapa de su propia cripta usando salto, dash y pala.”

> “El género es plataformas 2D, subgénero de acción, con estética gótica. El público es estudiantes y jugadores ocasionales. La partida dura entre 8 y 12 minutos. Las referencias son Blasphemous, Castlevania y Ender Lilies.”

**Mostrar:** el high concept escrito y una captura del camposanto.

---

## Diapositiva 3 — MDA (1 min 30 s)

**Decir:**
> “Usamos MDA: mecánicas, dinámicas y estéticas. El diseñador va de las reglas a las emociones; el jugador vive el camino inverso.”

> “Elegimos tres mecánicas: salto de precisión, dash de sombra y golpe de pala. No agregamos más porque queríamos que se combinaran y se aprendieran.”

> “La primera estética es **Desafío**: el jugador tiene que leer distancias, timing y altura. La segunda es **Sensación**: el dash deja estela, la pala explota en partículas, la cámara se sacude y ambos builds suman sonido.”

**Mostrar:** tabla MDA del GDD o esta tabla:

| Mecánica | Dinámica | Estética |
|---|---|---|
| Salto de precisión | Medir y corregir en el aire | Desafío |
| Dash de sombra | Gastar el impulso en el momento justo | Desafío + Sensación |
| Golpe de pala | Convertir al morador en trampolín | Sensación + Desafío |

**Frase de cierre:**
> “Las otras seis estéticas quedaron afuera o en segundo plano a propósito: preferimos dos emociones fuertes a ocho tibias.”

---

## Diapositiva 4 — Curva de dificultad y niveles (1 min 30 s)

**Decir:**
> “La curva tiene forma de sierra. Cada nivel presenta una mecánica, la practica con bajo castigo y después la exige.”

- **Nivel 1, El Camposanto:** salto y dash; todavía no hay pala. Pozos de 3 tiles y enemigos para esquivar. Es la práctica segura.
- **Nivel 2, La Cripta:** dash, recogida de pala, ataque y plataformas móviles. Los abismos anchos no se cruzan con un salto normal; la pista anticipa salto + dash y la pala.
- **Nivel 3, El Osario:** las tres mecánicas con la pala equipada. Pozos, pinchos, plataformas móviles y moradores. El golpe de pala devuelve el dash aéreo para encadenar.

**Decir:**
> “La dificultad no sube solo poniendo enemigos con más vida. Sube combinando mecánicas: eso es dificultad diseñada, no artificial.”

> “También usamos ajustes invisibles: coyote time de 0,10 segundos, buffer de salto de 0,12, hitbox generosa y rebote de pala generoso. El jugador siente que el control responde, no que el juego es fácil.”

**Mostrar:** capturas de los tres niveles o la gráfica de sierra.

---

## Diapositiva 5 — Sistemas, meaningful play y UI/UX (1 min 30 s)

**Decir:**
> “IN CRYPTA también se puede leer como sistema: objetos, atributos, relaciones, entorno, reglas y resultados. El sepulturero, los moradores, las almas y el portón son objetos; la velocidad, las vidas y el cooldown son atributos; las colisiones y la pala son relaciones.”

> “Hay dos feedback loops. El positivo: golpe de pala, rebote, recupero el dash, cruzo un pozo y llego a un alma. El negativo: recibo daño, quedo invulnerable un momento, vuelvo al inicio y releo el tramo.”

> “Las almas no son solo puntaje: cada 10 dan una vida extra, hasta un máximo de 5. Al morir se reinician el contador y las almas del nivel, pero las vidas extra ya ganadas se conservan.”

> “Buscamos meaningful play: que la acción sea **discernible** y **integrada**. Si aprieto dash, veo la estela, cambia mi posición y se actualiza el HUD; en Pygame también lo escucho. Si golpeo a un morador con la pala, desaparece, reboto y recupero el dash.”

**Mostrar:** HUD y una acción de dash/pala en la demo.

**Decir:**
> “La UI es no diegética en el HUD, diegética en el portón y las velas, espacial en la estela y meta en el flash de daño. Los cinco principios de UX están aplicados: lo importante se encuentra rápido, se entiende qué hacer, los controles son cómodos, todo es consistente y la pausa es fluida.”

---

## Diapositiva 6 — Pygame → GDevelop (1 min)

**Decir:**
> “El prototipo está en Pygame porque me permite iterar rápido la física. La versión de presentación es un proyecto nativo de GDevelop.”

> “GDevelop no ejecuta Python. Reconstruimos el juego con objetos, eventos y comportamientos nativos: el jugador, los moradores, las almas, los pinchos, el portón y la cámara. Los niveles salen de los mismos mapas y constantes que el prototipo.”

> “La ventaja es que el mismo diseño se prueba en Pygame y se presenta en GDevelop. La versión nativa corre a 1920 × 1080, con pausa propia, menú de reinicio, SFX y build HTML5 listo para abrir desde un servidor local.”

**Mostrar:** las escenas y eventos del proyecto nativo, o el build corriendo.

**Frase:**
> “Para la cátedra, lo importante es que el diseño y las pruebas son los mismos; cambia el motor de presentación.”

---

## Demo en vivo (2 min)

### Guion de demo

1. **Título (10 s):** mostrar el nombre, el equipo y las referencias. Decir: “La estética gótica se presenta desde la pantalla de título”.
2. **Nivel 1 (30 s):** mover, saltar un pozo y esquivar un morador. Decir: “Esto es la práctica segura; la pala todavía no aparece”.
3. **Nivel 2 (40 s):** cruzar el primer abismo con dash, recoger la pala, atacar y subir a una plataforma móvil. Decir: “El dash abre el paso y la pala desbloquea el ataque”.
4. **Nivel 3 (40 s):** mostrar un tramo con pozo, pinchos, plataforma móvil y morador. Decir: “Acá se combinan las tres mecánicas”.
5. **Portón (10 s):** llegar a la meta o mostrar la captura de victoria.

### Si algo falla

- Si GDevelop no abre: mostrar `capturas/titulo.png`, `nivel_1.png`, `nivel_2.png` y `nivel_3.png`, y el GDD.
- Si el build HTML5 no carga: servirlo con `python3 -m http.server` desde `export/gdevelop_nativo/build/` y abrir `http://127.0.0.1:8000/`.
- Si no hay audio: revisar el volumen del navegador y que los WAV de `export/gdevelop_nativo/assets/` se hayan copiado al build; el feedback visual sigue funcionando.

---

## Preguntas probables

### “¿Por qué solo tres mecánicas?”
> “Porque el objetivo era que se combinaran y se aprendieran. Con tres mecánicas y tres niveles se puede enseñar, practicar y exigir sin agregar complejidad innecesaria.”

### “¿Por qué dos estéticas y no más?”
> “MDA recomienda elegir las estéticas que se quieren provocar. Desafío y Sensación son las que el juego puede sostener con un equipo y un alcance chicos. Las otras seis están analizadas y justificadas como ausentes o secundarias.”

### “¿La versión de GDevelop es nativa?”
> “Sí. Es un proyecto de GDevelop con escenas, objetos, eventos y comportamientos propios. No carga el runtime JavaScript anterior ni ejecuta Python.”

### “¿Cómo sabés que el nivel 2 se puede pasar?”
> “Hay una prueba automatizada que simula el abismo ancho y verifica que exista una ventana de salto + dash para aterrizar. También validamos el build nativo de forma headless: pausa, reinicio, salto, dash, audio, recogida de pala, ataque, pisotón, daño, pozo, límites, plataformas móviles y transición de los tres niveles.”

### “¿Qué es meaningful play en tu juego?”
> “Que la relación entre acción y consecuencia sea visible e integrada. El dash no es una animación: cambia la posición, tiene cooldown y se ve en el HUD. El golpe de pala no es solo un efecto: elimina al morador, te hace rebotar y te devuelve el dash.”

### “¿Hay boss final?”
> “El build actual termina al cruzar el portón del Osario. En el GDD dejamos diseñado a **El Custodio del Osario**: un examen de salto, dash y pisotón, con tres fases y sin mecánicas nuevas. No lo implementamos para no ampliar el alcance a último momento.”

### “¿Por qué la estética gótica?”
> “Porque permite una atmósfera clara con recursos limitados: oscuridad, luz puntual, siluetas y piedra. Además conecta con las referencias que elegimos y con la historia del sepulturero. La oscuridad se usa con contraste para que el desafío siga siendo justo.”

### “¿Qué aprendiste de la cursada?”
> “Que un juego es un sistema y que la dificultad se diseña, no se improvisa. MDA me dio el vocabulario para conectar reglas con emociones; la curva de dificultad me dio la estructura de los tres niveles; UI/UX me hizo pensar en cómo se comunica cada acción.”

---

## Cierre (20 s)

**Decir:**
> “IN CRYPTA es un juego chico, pero cada decisión está justificada: tres mecánicas que se combinan, dos estéticas que se refuerzan, tres niveles que enseñan y una versión en GDevelop que permite presentarlo. Gracias.”

---

## Checklist final

- [ ] GDevelop abierto con `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json`.
- [ ] Ventana en 1920 × 1080 o el build servido por HTTP.
- [ ] Escenas `Titulo`, `Pausa`, `Victoria` y `Nivel 1..3` presentes.
- [ ] Teclado probado: mover, saltar, dash, recoger pala, atacar, pausa y reinicio desde el menú.
- [ ] Plataformas móviles probadas en Nivel 2 y Nivel 3.
- [ ] Capturas de respaldo.
- [ ] GDD abierto en otra pestaña.
