# QA y pruebas

## Entorno de esta revisión
- Análisis estático del JSON de GDevelop 5.6.285 (Python sobre el archivo).
- Sin GDevelop, sin navegador, sin red. No se ejecutó ninguna escena.

## Verificado (estático, sobre el JSON)
- 15 escenas, 7 hojas externas, 0 eventos JavaScript (`JsCode`).
- 199 recursos declarados; todos existen en `assets/`.
- Ningún evento usa un objeto que no exista en su escena.
- Equivalencia del refactor: al expandir los Link, las 15 escenas son idénticas al archivo previo al refactor.
- Enlaces Link: todos apuntan a hojas que existen.
- Destinos de escena (Scene): todos existen.
- Teclas de cada menú: revisadas en eventos (ver `CONTROLES_Y_FISICAS.md`).
- Constantes de dash, buffer y coyote: leídas de las asignaciones de eventos.
- Plataformas Solido: alineadas a la rejilla de 32 px, sin solapamientos ni costuras. Comparadas con el arte del fondo por superposición de contornos: coinciden en Tutorial y Nivel 1 (verificación visual, sin ejecución).
- Alcanzabilidad por modelo: ver `DISENO_Y_PROGRESION.md`. Es una estimación.

## No verificado (requiere GDevelop)
- Abrir el JSON en GDevelop 5.6.
- Compilar todas las escenas y revisar diagnósticos.
- Previsualizar (Preview) y jugar cada escena.
- Exportar HTML5 y servirlo.
- Capturas de Título, Tutorial, Nivel 1, Nivel 2, Nivel 3 y una Sala (no producidas).
- Publicación en gd.games.
- Confirmar que los objetos ocultos (Solido) siguen colisionando en el juego.
- Comportamiento real del salto, dash, checkpoints, HUD y menús.

## No producido
- Carpeta `build/` con HTML5 jugable: requiere exportar desde GDevelop.
- Capturas de referencia del proyecto redimensionado.

## Checklist de prueba para hacer en GDevelop

1. **Compilación:** abrir y compilar las 15 escenas. Anotar cada diagnóstico con escena y texto.
2. **Título:** 1 → Tutorial, 2 → Nivel 1, 3 → Nivel 2, 4 → Salas. U → Tutorial. T → Salas. Clic sobre cada opción. Cada destino debe ser único y correcto.
3. **Tutorial:** completar hasta la puerta con salto corto. Anotar si el primer salto se repite de forma consistente.
4. **Nivel 1:** llegar al farol de la plataforma alta (x 3526) con salto corto. Anotar si se alcanza.
5. **Nivel 2, primer hueco (x ≈ 512–736):**
   - con salto corto: se espera que no se cruce (modelo);
   - con dash en el aire: se espera que sí;
   - manteniendo Espacio: se espera que sí.
   Anotar qué ayuda ve el jugador en pantalla.
6. **Nivel 2, farol en x 3844:** debe estar sobre la plataforma y no caer.
7. **Nivel 3:** los 3 faroles requieren dash o salto mantenido (modelo). Anotar cuáles faltan.
8. **Pulsaciones únicas:** Espacio no debe saltar dos veces por pulsación. X no debe disparar dos dashes. J no debe atacar dos veces. Un clic no debe disparar dos transiciones.
9. **Pausa:** Escape abre la pausa y Escape la cierra. Revisar que no se encadenen dos cambios de escena.
10. **F1:** alterna la reducción de sacudida.
11. **HUD a 1280×720:** vidas, almas, dash y controles sin solaparse.
12. **Colisiones:** caminar sobre cada tramo de plataformas del Tutorial y del Nivel 1 y confirmar que no hay bordes invisibles ni plataformas que atraviesen el arte.
13. **Exportación HTML5:** exportar, servir la carpeta por HTTP y abrir `index.html`. Revisar la consola del navegador por errores del juego.

## Límites conocidos
- El modelo de alcance no incluye enemigos, pinchos ni las plataformas móviles. Un salto que el modelo marca como alcanzable puede fallar por esos factores.
- El "se traba" reportado por el equipo no se pudo reproducir. La causa más probable es el primer hueco del Nivel 2 (ver `DECISIONES_Y_CAMBIOS.md`). Confirmarlo en el juego.
