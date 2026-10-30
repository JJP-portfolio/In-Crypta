# ============================================================
# ROOM TESTS: Salones de Prueba para IN CRYPTA
# ============================================================
# Cada salón aísla una mecánica de IN CRYPTA para que el profesor
# pueda evaluarlas sin recorrer la campaña completa.
# ============================================================

# Reglas duras para cualquier room test:
# - Una sola mecánica por salón
# - Sin tiles que tapan holes, un solo P y un solo G
# - Validación con simulador antes de exportar
# - Diseñados a mano, no generados por loops

# ============================================================
# SALA 1 · MOVIMIENTO Y SALTO (Original Nivel 1)
# ============================================================

# Mecánicas aisladas: Movimiento horizontal, salto variable,
# coyote time y corte de salto.

# Características:
# - 20 columnas, 12 filas de tiles (240 × 384 px)
# - Sin enemigos, sin pinchos, sin plataformas móviles
# - Primer salto en el gran abismo (7 tiles)
# - Arma: ninguna (A no desbloqueada)
# - Nivel: El Camposanto

# Mejora del rediseño (v2):
# - Huecos más medibles: 3 tiles, 4 tiles, 7 tiles, 10 tiles
# - Menos enemigos: 6 en total
# - Plataformas básicas en la zona central
# - Reposa: una pared vertical de 6 tiles en la sección media derecha

# Mejoras pendientes (además del rediseño v2):
# - Agregar plataformas móviles solo en las zonas de práctica para el dash aéreo.
# - Agregar pinchos como peligro de contacto.

# ============================================================
# SALA 2 · PALA Y ATAQUE (Original Nivel 2)
# ============================================================

# Mecánicas aisladas: Recogida de pala, ataque con J y
# derribo aéreo (dash aire requerido).

# Características:
# - 20 columnas, 12 filas de tiles (240 × 384 px)
# - Una pala recogible (W) ubicada al 25% de ancho
# - Dos enemigos patrullando, espaciados (1 y 1)
# - Pinchos como peligro de contacto (3)
# - Sin plataformas móviles (introducidas en Nivel 3)
# - Nivel: La Cripta

# Mejora del rediseño (v2):
# - Introducir plataforma móvil horizontal (M) para dash aéreo.
# - Espaciar enemigos más ampliamente (separamiento mayor).
# - Colocar pala (W) más al centro del escenario para esquivar.

# Mejoras pendientes:
# - Agregar plataforma móvil vertical (V) para movimiento vertical.
# - Agregar plataforma móvil horizontal (M) como en Nivel 3.

# ============================================================
# SALA 3 · CUSTODIO (Original Nivel 3)
# ============================================================

# Mecánicas aisladas: Enfrentar al jefe Custodio, combinar salto,
# dash y ataque, derrotar al jefe y salir del portón sellado.

# Características:
# - 20 columnas, 12 filas de tiles (240 × 384 px)
# - Un jefe Custodio (B) en la parte media derecha del escenario
# - Esbirros: uno a la izquierda del jefe, uno a la derecha (2)
# - Dos pinchos cerca de la plataforma del jefe (2)
# - Sin plataformas móviles (introducidas en Nivel 3)
# - Nivel: El Osario

# Mejora del rediseño (v2):
# - Agregar plataformas móviles M y V para practicar dash sobre móviles.
# - Espaciar enemigos más ampliamente para no bloquear visión.
# - Ubicar jefe B más al centro del nivel.

# Mejoras pendientes:
# - Agregar plataformas móviles M y V para practicar dash sobre móviles.
# - Agregar plataforma móvil vertical (V) para movimiento vertical.

# ============================================================
# RENDIMIENTO ESPERADO (simulado con simulador)

# Sala 1 · Movimiento y salto:
# - El jugador puede completar el nivel con salto, subiendo tres
#   cornisas en las columnas 1-3 del GRAN ABISMO (cols 56-68).
# - Desde el suelo, NO se cruza el GRAN ABISMO de 7 tiles de ancho sin dash.

# Sala 2 · Pala y ataque:
# - El jugador obtiene la pala W y puede derribar un enemigo con un
#   pisotón desde el aire (dash aire requerido).

# Sala 3 · Custodio:
# - El jugador toma la pala W y ataca al jefe. Cuando el jefe se
#   arrodilla, se expone vulnerable y el jugador puede derrotarlo.
# - Al derrotar al jefe, se abre la puerta de salida y se completa el nivel.

# ============================================================
# NOTAS DE VALIDACIÓN (protegidas)

# Los mapas están validados:
# - Salidas consecutivas de almas después de casilleros.
# - Portones que están al menos 8 tiles del spawn (sin salida fácil).
# - Enemigos dentro de los límites de patrulla (no flotan).
# - No hay paredes que tapan holes.
# - Saltos simulados exitosos.

# Los room tests están preservados en SALAS_PRUEBA (niveles.py).
# Los tests del profesor se ejecutan en estas salas originales.