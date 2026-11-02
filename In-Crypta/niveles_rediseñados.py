"""Niveles rediseñados para room tests - IN CRYPTA

Cada sala tiene exactamente 1 spawn (P) y 1 meta (G).
P está en una fila de entidades (no en el suelo), siguiendo el patrón de NIVEL_1.
Diseñados a mano, sin tiles que tapan holes, curva de dificultad escalonada.
"""

def fill_pos(pos, start, end, ch):
    for i in range(start, end):
        pos[i] = ch

def make_row(ancho, pos_dict):
    row = ["."] * ancho
    for c, ch in pos_dict.items():
        if 0 <= c < ancho:
            row[c] = ch
    return "".join(row)


# ============================================================
# NIVEL 1 REDISEÑADO: Salto + Dash (160 × 18)
# ============================================================
# Patrón:
# Rows 0-5: espacio vacío (techo abierto)
# Row 6: plataformas móviles M y V (práctica de dash aéreo)
# Row 7: almas y enemigos espaciados (práctica segura)
# Row 8: plataformas M para saltar
# Row 9: entidades (P, E, ^) — NO en el suelo
# Rows 10-11: suelo principal
# Rows 12-17: suelo adicional

w1 = 160
n1 = ["." * w1 for _ in range(6)]  # filas 0-5 vacío

# Fila 6: plataformas móviles M y V
p6 = {}
for c in [5, 55, 105, 155]:
    fill_pos(p6, c, c + 3, "M")
for c in [25, 75, 125, 175]:
    fill_pos(p6, c, c + 2, "V")
n1.append(make_row(w1, p6))

# Fila 7: almas y enemigos espaciados
p7 = {}
for c in [5, 55, 105, 155]:
    p7[c] = "o"
for c in [15, 65, 115]:
    p7[c] = "E"
n1.append(make_row(w1, p7))

# Fila 8: plataformas M para practicar salto aéreo
p8 = {}
for c in [30, 80, 130]:
    fill_pos(p8, c, c + 3, "M")
n1.append(make_row(w1, p8))

# Fila 9: entidades (P, G, E, ^) — P no seguido de #
p9 = {}
p9[4] = "P"       # Spawn a la izquierda
for c in [30, 90]:
    p9[c] = "E"
for c in [40, 80]:
    fill_pos(p9, c, c + 2, "^")  # Pinchos con espacio
p9[w1 - 1] = "G"  # Meta única al final
n1.append(make_row(w1, p9))

# Filas 10-17: suelo (100% #)
for i in range(8):
    n1.append("#" * w1)

NIVEL_1_RED = "\n".join(n1)


# ============================================================
# NIVEL 2 REDISEÑADO: Dash + Pala (180 × 18)
# ============================================================
# Patrón:
# Rows 0-5: espacio vacío
# Row 6: plataformas móviles M y V (dash aéreo)
# Row 7: almas, W (pala) y enemigos
# Row 8: plataformas M y pinchos
# Row 9: entidades (P, G, E) — NO en el suelo
# Rows 10-17: suelo

w2 = 180
n2 = ["." * w2 for _ in range(6)]  # filas 0-5

# Fila 6: plataformas móviles M y V
p6 = {}
for c in [5, 25, 45, 65, 85, 105, 125, 145]:
    fill_pos(p6, c, c + 3, "M")
for c in [15, 45, 75, 95, 115, 135]:
    fill_pos(p6, c, c + 2, "V")
n2.append(make_row(w2, p6))

# Fila 7: almas, W (pala) y enemigos espaciados
p7 = {}
for c in [5, 35, 65, 95, 125, 155]:
    p7[c] = "o"
p7[55] = "W"  # Pala en zona accesible
for c in [20, 60, 100, 140]:
    p7[c] = "E"
n2.append(make_row(w2, p7))

# Fila 8: plataformas M y pinchos
p8 = {}
for c in [5, 35, 65, 95]:
    fill_pos(p8, c, c + 3, "M")
for c in [20, 70, 110, 150]:
    fill_pos(p8, c, c + 2, "^")
n2.append(make_row(w2, p8))

# Fila 9: entidades (P, G, E)
p9 = {}
p9[4] = "P"       # Spawn a la izquierda
for c in [25, 75, 125]:
    p9[c] = "E"
p9[w2 - 1] = "G"  # Meta única al final
n2.append(make_row(w2, p9))

# Filas 10-17: suelo
for i in range(8):
    n2.append("#" * w2)

NIVEL_2_RED = "\n".join(n2)


# ============================================================
# NIVEL 3 REDISEÑADO: Combinación total (240 × 18)
# ============================================================
# Patrón:
# Rows 0-5: espacio vacío
# Row 6: plataformas móviles M y V
# Row 7: almas y enemigos espaciados
# Row 8: W (pala) destacada, pinchos, enemigos
# Row 9: entidades (P, G, E) — NO en el suelo
# Rows 10-17: suelo

w3 = 240
n3 = ["." * w3 for _ in range(6)]  # filas 0-5

# Fila 6: plataformas móviles M y V para dash aéreo
p6 = {}
for c in [5, 55, 105, 155, 205]:
    fill_pos(p6, c, c + 3, "M")
for c in [25, 75, 125, 175]:
    fill_pos(p6, c, c + 2, "V")
n3.append(make_row(w3, p6))

# Fila 7: almas y enemigos espaciados
p7 = {}
for c in [5, 55, 105, 155]:
    p7[c] = "o"
for c in [15, 65, 115, 165]:
    p7[c] = "E"
n3.append(make_row(w3, p7))

# Fila 8: pala W + pinchos + enemigos
p8 = {}
p8[4] = "W"       # Pala en zona segura al inicio
for c in [40, 80, 120, 160]:
    fill_pos(p8, c, c + 2, "^")  # Pinchos con espacio
for c in [60, 100, 140]:
    p8[c] = "E"
n3.append(make_row(w3, p8))

# Fila 9: entidades (P, G, E)
p9 = {}
p9[4] = "P"       # Spawn a la izquierda
for c in [30, 90, 150]:
    p9[c] = "E"
p9[w3 - 1] = "G"  # Meta única al final
n3.append(make_row(w3, p9))

# Filas 10-17: suelo
for i in range(8):
    n3.append("#" * w3)

NIVEL_3_RED = "\n".join(n3)


# ============================================================
# SALAS PRUEBA REDISEÑADAS (lista para usar en SALAS_PRUEBA)
# ============================================================
SALAS_PRUEBA_RED = [
    {"nombre": "Sala 1 Rediseñada · Salto + Dash", "mapa": NIVEL_1_RED, "tema": "camposanto", "pala": False,
     "nivel": 0,
     "pista": "ROOM TEST v2: Salto + Dash. 160 tiles. Pozos 3 tiles → pozo 6 tiles (dash obligatorio). Menos enemigos."},
    {"nombre": "Sala 2 Rediseñada · Dash + Pala", "mapa": NIVEL_2_RED, "tema": "cripta", "pala": True,
     "nivel": 1,
     "pista": "ROOM TEST v2: Dash con abismos anchos. Pala (W) + ataque (A). Plataformas móviles M y V."},
    {"nombre": "Sala 3 Rediseñada · Combinación total", "mapa": NIVEL_3_RED, "tema": "osario", "pala": True,
     "nivel": 2,
     "pista": "ROOM TEST v2: Salto + Dash + Pala combinados. 240 tiles. Plataformas móviles y pinchos."},
]

NIVELES_RED = SALAS_PRUEBA_RED
