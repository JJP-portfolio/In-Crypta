# PLAN DE DISEÑO VISUAL — ESTÉTICA POEANA (REDiseño)

Este documento planifica la parte de dibujo visual del proyecto IN CRYPTA, inspirada en Edgar Allan Poe y en el tono gótico del proyecto original. Estilo: **sobrio, congruente, macabro, sin exceso de efectos**.

## 1. Inspiración Edgar Allan Poe
| Concepto de Poe | Traducción visual en el juego |
|---|---|
| Entierro prematuro ("The Premature Burial") | Sepulturero atrapado, ataúdes, criptas, portón sellado |
| El Cuervo ("The Raven") | Enemigo volador negro, plumas, presagio de muerte |
| El Gato Negro ("The Black Cat") | Enemigo terrestre, ojos amarillos, superstición |
| El Péndulo ("The Pit and the Pendulum") | Trampa oscilante, hoja de metal, muerte inminente |
| La Caída de la Casa Usher | Arquitectura en decadencia, paredes agrietadas, humedad |
| Luz de vela como única esperanza | Farol del sepulturero, velas en cripta, oscuridad absoluta |
| Muerte, huesos, descomposición | Osario, costillas, calaveras, musgo, podredumbre |

## 2. Principios de buen forma (aplicados al rediseño)
1. **Solo primitivas `pygame.draw`** (sin imágenes externas).
2. **Paleta limitada y unificada**: negro azabache, púrpura muerto, verde musgo, blanco hueso, rojo sangre, oro vela, gris ceniza.
3. **Chiaroscuro**: el farol y las velas iluminan zonas pequeñas; el resto queda en sombra.
4. **Siluetas legibles**: jugador y enemigos reconocibles por contorno, no por detalle.
5. **Hitbox menor que el sprite**: evita muertes injustas.
6. **Feedback sobrio**: partícula leve + sacudida de cámara corta; sin flashes excesivos.
7. **Cámara separada del HUD**; HUD no se mueve con la cámara.
8. **Optimización**: `is_on_screen` con margen; limpieza de partículas muertas cada frame.

## 3. Ámbito del rediseño (solo dibujo visual)
- Fondo por tema con arquitectura en decadencia y niebla
- Suelos y muros (tiles criptográficos, ataúdes, huesos)
- Plataformas móviles (lápidas flotantes, osamentas colgantes)
- Decoraciones: ataúdes, paredes agrietadas, cadenas colgantes, perchas de cuervo
- Peligros: pinchos óseos, péndulo oscilante
- Meta: portón de hierro sellado
- Personaje: sepulturero con abrigo, sombrero ancho, farol con cono de luz, pala
- Enemigos: Cuervo (volador), Gato Negro (terrestre), Péndulo (trampa)
- Objetos: Almas (flamas violetas), Pala (recolectable)
- Partículas: polvo, humo de vela, plumas de cuervo, gotas de sangre
- HUD mínimo estilo pergamino

## 4. Estructura
```
prototipo_visual/
├── PLAN_DIBUJO.md      # este documento
├── visual_demo.py      # ejemplo ejecutable independiente
└── README_EJECUCION.md # cómo correr
```

**Nota:** Este prototipo es independiente y no modifica el código del juego principal. Solo se aplicarán los cambios al proyecto una vez aprobado este rediseño.
