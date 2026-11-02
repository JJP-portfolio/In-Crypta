# Diseño de Niveles: Castlevania (PlayStation 1) - Primer Nivel

## Área general: Castillo de Dracula's World

### Estructura del área
- **Tipo de scroll**: Vertical (corte 4-5 habitaciones)
- **Número de niveles**: 3-4 pisos principales
- **Columnas**: 15-20 columnas por pantalla
- **Salida del área**: Puerta del castillo o ascensor

### Patrón de progresión de dificultad

#### Sala 1: Introducción segura (0-3 min)
- **Techo**: Abierto, sin peligros
- **Piso**: Estático, sólido
- **Enemigos**: 1-2 hombres columna
- **Plataformas**: 1 tabla estática (salto de 3 tiles)
- **Salida**: Puerta de madera
- **Checkpoint**: Después del primer salto

#### Sala 2: Primeras amenazas (3-6 min)
- **Techo**: Parrilla, tiros de ácido
- **Piso**: Móvil (suave, horizontal)
- **Enemigos**: 2-3 hombres columna
- **Plataformas**: 1 tabla, 1 plataforma oscilante
- **Salida**: Escalera
- **Plataforma clave**: Abismo de 8 tiles (salto + dash)

#### Sala 3: Plataformas complejas (6-9 min)
- **Techo**: Puertas rotas, pinchos
- **Piso**: Roto, espaciado
- **Enemigos**: 2 columnas + 1 guardia
- **Plataformas**: 2 móviles, 1 móvil vertical
- **Salida**: Valla, ascensor
- **Plataforma clave**: Valla en zigzag, salto + dash

#### Sala 4: Jefe final (9-12 min)
- **Cámara**: Encerrada, protectora
- **Plataformas**: Estáticas, temáticas del jefe
- **Enemigos**: 1 jefe
- **Salida**: Puerta del castillo
- **Salto requerido**: 4 tiles + dash

### Métricas específicas del primer nivel

#### Distancia máxima
- **Salto**: 97px = 3 tiles
- **Dash**: No existe en PS1, solo salto
- **Columna máxima**: 180px = 5.6 tiles
- **Recomendación**: Usar plataforma móvil para distancias largas

#### Patrones de salto recomendados
| Tipo de sala | Ancho del hueco | Salto requerido |
|-------------|----------------|---------------|
| Sala 1 | 4 tiles | Únicamente salto |
| Sala 2 | 6 tiles | Saltar + dash (opcional) |
| Sala 3 | 8 tiles | Saltar + dash (obligatorio) |

#### Densidad de enemigos por habitación
- **Sala 1**: 1-2 enemigos (patrulla horizontal)
- **Sala 2**: 3 enemigos (patrulla + archivo)
- **Sala 3**: 4 enemigos (2 filas, 2 columnas)
- **Sala 4**: 0 enemigos (solo jefe)

### Patrones clave a extraer

#### 1. Progresión gradual de dificultad
- **Primeras 2 habitaciones**: Movimiento + salto
- **3ra habitación**: Introducir la mecanica del abismo
- **4ta habitación**: Combina todo con el jefe

#### 2. Diseño de plataforma específico
- **Tabla**: Colocada 2-3 columnas adelante del spawn
- **Plataforma móvil**: Oscila 1 tile verticalmente
- **Abismo**: Exactamente 8 tiles, obliga al dash
- **Plataforma vertical**: Subida para obtener altura

#### 3. Uso del espacio
- **Izquierda**: Spawn y salida
- **Centro**: Enemigos y plataformas
- **Derecha**: Objetos de decoración + riesgo

#### 4. Disposición de enemigos
- **Físicamente accesibles**: Contienen plataforma utilizable
- **No accesibles**: Como decoración o solo al principio
- **Especial**: Sirve como encuentro narrativo

### Patrón típico del primer nivel - "El Castillo de Dracula's World"

#### Encabezado: Área de Introducción
```text
# ======================================
# Castillo de Dracula's World - Sala 1
# ======================================

## Objetos principales:
- P: Spawn del jugador (columna 2, fila 2)
- G: Portón de salida (columna 16, fila 2)
- 3-4 enemigos (hombres columna)
- 1 tabla sólida

## Descripción del nivel:
La partida comienza en una cámara sencilla con suelo sólido y techo abierto. El objetivo es escapar por una puerta lejana con un saltos de 4 tiles. 2 hombres columna patrullan el pasillo lateral derecho.

## Mecánicas principales a enseñar:
1. Movimiento horizontal básico
2. Salto variable (3 tiles de altura)
3. Volar sobre el enemigo (pisotear)
4. Correr a la salida

## Elementos visuales:
- Luces de antorchas en las paredes
- Piso de piedra oscura
- Puerta de madera simple
```

#### Encabezado: Sala de Abismos
```text
# ======================================
# Castillo de Dracula's World - Sala 2
# ======================================

## Objetos principales:
- P: Spawn (columna 2, fila 2)
- G: Salida (columna 20, fila 2)
- 2 tablas móviles
- 3 enemigos columna
- 1 abismo de 8 tiles (columnas 6-14)

## Descripción del nivel:
Una cámara con un abismo central que requiere salto + dash para cruzar. Plataformas oscilantes proveen apoyo vertical y lado a lado. Los enemigos patrullan en ambas columnas laterales.

## Mecánicas principales a enseñar:
1. Dash en el aire (nuevo)
2. Uso de plataformas móviles
3. Evitar pinchos en los lados
4. Atravesar abismos largos

## Elementos visuales:
- Luces de velas en nichos
- Estalactitas colgando
- Plataformas de piedra móvil
```

### Métricas de diseño para implementar

| Métrica | Objetivo | Razón |
|--------|----------|--------|
| Columna de salto | 3 tiles | Físicamente auténtica para PS1 |
| Distancia de salto máxima | 180px | Para salas de 5-6 tiles |
| Altura máxima de plataforma | 1 tile | Suave, no disruptiva |
| Ancho de abismo | 8 tiles | Clásico de Castlevania |
| Espacio de plataforma móvil | 3-4 tiles | Para plataforma vertical |
| Columna de hueco estrecho | 1 tile | Para plataforma pequeña |
| Espacio de enemigo | Mínimo 2 tiles | Movilidad limitada |

### Patrones de nivelación recomendados

#### Nivel 1: "El Vestíbulo"
- **Etapa 1**: Movimiento en corredores seguros (0-3 enemigos)
- **Etapa 2**: Primer abismo de 4 tiles (con plataforma)
- **Etapa 3**: Abismo de 6 tiles (dash opcional)

#### Nivel 2: "El Pasillo del Abismo"
- **Etapa 1**: Abismo de 8 tiles (dash obligatorio)
- **Etapa 2**: Plataforma oscilante
- **Etapa 3**: Abismo + plataforma móvil

#### Nivel 3: "La Cámara del Jefe"
- **Etapa 1**: Sala estática, patrón de jefe
- **Etapa 2**: Jefe con trayectoria de ataque
- **Etapa 3**: Salida final, victoria

### Principios específicos del primer nivel a seguir

1. **Habilidades básicas primero**: Nunca enseñar una nueva mecánica sin que las anteriores estén dominadas
2. **Concentración de elementos**: Mantener 2-3 elementos principales por habitación
3. **Progresión gradual**: Construir uno sobre el otro de manera lógica
4. **Elección estratégica**: No forzar mecánicas nuevas, permitir crecimiento orgánico
5. **Elementos memorables**: Una imagen icónica por habitación

### Análisis del primer nivel - "El Castillo de Dracula's World"

#### Patrón general de la habitación
- **Dimensiones**: 20 columnas × 4 filas (tiles)
- **Salto**: 3 tiles (97px) = altura de salto 3 tiles
- **Dash**: No disponible (PS1), solo salto
- **Max. distancia horizontal**: 220px = 7 tiles

#### Sala específica 1: "El Vestíbulo"
- **Entrada**: Puerta en columna 2, fila 2
- **Salida**: Puerta en columna 18, fila 2
- **Altura máxima de salto**: 3 tiles
- **Distancia de hueco**: 14 tiles = 4.3 columnas
- **Superación**: Saltar al portón (posible)

#### Sala específica 2: "La Cámara del Abismo"
- **Entrada**: Puerta de madera en columna 2, fila 2
- **Salida**: Escalera en columna 20, fila 2
- **Plataforma clave**: Abismo de 8 tiles (columnas 6-14)
- **Patrón de enemigo**: Columna izquierda + derecha
- **Plataforma móvil**: Columna 10-12
- **Plataforma vertical**: Columna 12-14

#### Sala específica 3: "El Pasillo del Jefe"
- **Entrada**: Puerta de ascensor en columna 2, fila 2
- **Salida**: Puerta en columna 18, fila 2
- **Plataformas**: Estáticas, temáticas de la cámara del jefe
- **Jefe**: Dracula (vida alta, fases)
- **Salto requerido**: 4 tiles + dash (nuevo para 3ra sala)

### Principios específicos para extracción

#### 1. Patrón de habitación tipo
```
Entrada -> Seguridad -> Desafío -> Jefe -> Salida
```
- **Seguridad**: Sin peligros, solo movimiento
- **Desafío**: Introducir primer elemento amenazante
- **Jefe**: Elemento final, requiere todas las mecánicas aprendidas

#### 2. Dificultad escalonada
- **Sala 1**: 0-3 enemigos, sin plataformas peligrosas
- **Sala 2**: 3-4 enemigos, 1 plataforma móvil
- **Sala 3**: 4-5 enemigos, plataformas combinadas
- **Sala 4**: 0 enemigos, solo jefe

#### 3. Mecánicas principales por habitación
- **Sala 1**: Movimiento + salto
- **Sala 2**: Plataformas móviles + abismo
- **Sala 3**: Plataformas verticales + enemigos espaciados
- **Sala 4**: Combina todo + jefe

#### 4. Elementos visuales distintivos
- **Sala 1**: Luces de antorchas, piso de piedra
- **Sala 2**: Luces de velas, estalactitas
- **Sala 3**: Nichos, estructuras góticas
- **Sala 4**: Cortinas de tela, santuario del jefe

### Mejores prácticas para implementar estos patrones

1. **Corregir la física del primer nivel**: Salto de 3 tiles (107px en el nativo) o mantener salto de 4 tiles (125px)
2. **Manejar correctamente el coyote time**: 0.18s (original PS1)
3. **Diseñar correctamente las alturas de los huecos**: 3-4 tiles = salto cómodo
4. **Crear progresión gradual**: Introducir mecánica por habitación
5. **Validar correctamente el ritmo**: Prueba de pasos del jugador real

### Propuesta de diseño de primer nivel

```text
"El Castillo de Dracula's World" - Nivel 1

Componentes principales:
- 3 habitaciones principales (18 columnas × 12 filas tiles)
- Progresión: Movimiento -> Plataformas móviles -> Plataformas verticales -> Jefe
- Mecánicas: Salto -> Dash -> Placar vertical
- Físicamente: Salto de 3 tiles, coyote 0.18s, gravedad 1500px/s²
- Elementos icónicos: Abismo de 8 tiles, plataforma móvil oscilante
```

### Conclusión principal

El primer nivel de Castlevania PS1 muestra el mejor ejemplo de cómo diseñar una progresión gradual:

1. **Hablar un lenguaje, fluir uno a la vez**: No introducir nuevas mecánicas hasta que las anteriores estén dominadas
2. **Elementos esenciales**: 2-3 elementos principales por habitación
3. **Patrón lógico**: Cada habitación construye sobre la anterior
4. **Superación física**: Corregir la física para hacerla medible y no estimada
5. **Elementos icónicos**: Una imagen memorable por habitación

#### Por qué esto es importante para IN CRYPTA

IN CRYPTA actualmente tiene:
- **Salto desigual**: 3 tiles en el nativo, 4 tiles en pygame
- **No hay progresión**: El nivel 1 ya introduce dash y pickaxe
- **Elementos aleatorios**: Demasiados, no medibles

Propuesta:
- **Primer nivel**: Solo movimiento + salto (4 tiles)
- **Segundo nivel**: Plataformas móviles + dash
- **Tercer nivel**: Combinación completa + jefe
- **Validación**: Física medible, ritmo escalonado