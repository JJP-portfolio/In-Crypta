# Diseño de niveles: Castlevania (PlayStation 1)

## Referencias principales
- **Symphony of the Night** (1997) - Jugador: Richter Belmont
- **Chronicles of the Moon** (1999) - Jugador: Wayne Bell

## 1.1 Estructura de salas y scroll

### Symphony of the Night
- **Scroll vertical**: Principal modo de juego
- **Salas tipo**: 5-10 habitaciones por área
- **Checkpoints**: Guardados en castillos/jardines separados
- **Transiciones**: Generadas a través de puertas y ascensores

**Área típica**: Castillo de Dracula's World (corte vertical)

### Chronicles of the Moon
- **Scroll horizontal**: Secuencias clave (torre, calabozo, altar)
- **Sección tipo**: 3-4 pantallas por etapa
- **Checkpoints**: Estatua de save en cada torre principal

## 1.2 Ritmo de dificultad

**Patrón típico del área:**
1. **Introducción segura** (0-3 enemigos, movimiento básico)
2. **Primeras amenazas** (enemigos + objetos)
3. **Cuello de botella** (plataformas complejas)
4. **Sección jefe** (Jefe con patrón de ataque)
5. **Espacio libre** (elementos decorativos, transición)

**Aumento gradual de la dificultad:**
- 1-2 salas: Movimiento solo
- 3-4 salas: Saltos de plataforma
- 5-6 salas: Enemigos agrupados
- 7-8 salas: Plataformas móviles + pinchos
- 9-10 salas: Jefe + combinación de mecánicas

## 1.3 Diseño de plataformas

### Características principales
- **Anchuras de hueco**: 3-4 tiles = salto cómodo
- **Alturas de salto**: 97px (3 tiles) en física original
- **Ancho máximo de salto**: 180px (5.6 tiles)
- **Elemento clave**: Plataformas con margen para refinar la precisión

### Patrones
- **Hueco simple**: 4-6 tiles, uno por área
- **Combinación**: Hueco estrecho + salida lateral
- **Plataformas móviles**: Máximo 3 en pantalla
- **Tablas rotas**: Se mueven vertical u horizontalmente

### Castlevania específico
- **Abismo 8 tiles**: Característica icónica (Saltar + Dash)
- **Vinculación de plataformas**: Algunos casos (sumergible)
- **Zonas de peligro**: Gotas de ácido, pinchos giratorios
- **Puertas/cámaras**: Se abren con artefactos clave

## 1.4 Ubicación de checkpoints y salidas

### Ubicación típica
- **Checkpoint 1**: Al final de la sala segura (antes de la primera amenaza)
- **Checkpoint 2**: Después de la primera plataforma difícil
- **Checkpoint 3**: Antes de la sección de jefe
- **Salida**: Después de derrotar al jefe o encontrar el cofre

### Jugabilidad
- **Distancia de regreso segura**: Hasta el checkpoint anterior (no al inicio)
- **Sin "reset"**: Una vez superada cierta sección, no se vuelve atrás
- **Repetición**: Disponible solo al morir

## 1.5 Integración de enemigos

### Patrones de patrulla
- **Lineal**: Izquierda-derecha, muerte a un golpe
- **Curvo**: En arcadas, seguimiento de jugador
- **Agrupados**: Esperan y atacan en conjunto

### Diseño de niveles con enemigos
- **Separados por habitaciones**: Para facilitar el aprendizaje
- **En lados opuestos**: Para forzar la elección
- **Trampa vs peligro**: Diferenciar coleccionable vs daño

## 1.6 Ejemplos concretos

### Área ejemplo: Castillo de Dracula's World
- **Sala 1**: Fondo seguro, tabla estática (0-3 tiles de salto)
- **Sala 2**: Primeras batallas (hombres columna, saltar + dash)
- **Sala 3**: Abismo + plataformas (zapata móvil + pinchos)
- **Sala 4**: Jefe (Dr. Vlad Dracula)

### Área ejemplo: Jardín del Foso
- **Corte horizontal**: Columna salpicada (salto lateral)
- **Plataforma móvil**: Swing + pinchos
- **Archivos**: Salida hacia la torre principal

## 1.7 URL de referencia

- Castlevania Wiki: https://castlevania.fandom.com/wiki/Category:Level_Design
- GameFAQs: https://www.gamefaqs.com/classic/51368/castlevania-symphony-of-the-night
- YouTube: "Castlevania Symphony of the Night level design analysis"

## 1.8 Resumen de patrones de diseño

| Elemento | Patrón típico | Notas de diseño |
|---------|----------------|----------------|
| Huecos | 4-6 tiles | Permitir la habilidad de aterrizar para dominar |
| Plataformas | 1-3 móviles | No demasiado anchas |
| Enemigos | Máximo 5 en pantalla | Dirigidos por patrulla, no aleatorios |
| Salidas | Al final de cada área | Permiten avance vs retroceso |
| Checkpoints | Al 50% del área | Evitan retroceso excesivo |
| Salto | 3 tiles | Físicamente limitado |
| Dash | No en PS1 | Se añade en versiones posteriores |

## 1.9 Métricas de diseño a experimentar

- **Columna de salto**: De 3 a 6 tiles
- **Distancia máxima**: De 180 a 220 px
- **Densidad de enemigos**: De 1 a 3 por habitación
- **Número de plataformas**: De 1 a 4 móviles
- **Regresiones por nivel**: Máximo 3 chequeos distintos