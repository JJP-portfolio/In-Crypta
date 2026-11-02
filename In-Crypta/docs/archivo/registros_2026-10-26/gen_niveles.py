from pathlib import Path

def mapa(ancho, alto, suelos, plataformas, monedas, enemigos, spawn, meta):
    filas = [['.' for _ in range(ancho)] for _ in range(alto)]
    for y, x0, x1 in suelos:
        for x in range(x0, x1):
            filas[y][x] = '#'
    for y, x0, x1 in plataformas:
        for x in range(x0, x1):
            filas[y][x] = '#'
    for y, x in monedas:
        if filas[y][x] == '.':
            filas[y][x] = 'o'
    for y, x in enemigos:
        if filas[y][x] != '#':
            filas[y][x] = 'E'
    py, px = spawn
    filas[py][px] = 'P'
    gy, gx = meta
    filas[gy][gx] = 'G'
    return '\n'.join(''.join(f) for f in filas)

def rango(y, x0, x1):
    return (y, x0, x1)

def sobre(plataformas, y_plataforma, x):
    return (y_plataforma - 1, x)

# Nivel 1: 80 x 18
suelo1 = [rango(16,0,24), rango(16,27,50), rango(16,53,66), rango(16,69,80),
          rango(17,0,24), rango(17,27,50), rango(17,53,66), rango(17,69,80)]
plat1 = [
    rango(13,8,12), rango(13,18,22), rango(13,32,36), rango(13,43,47), rango(13,56,60), rango(13,70,74),
    rango(11,12,16), rango(11,28,32), rango(11,38,42), rango(11,52,56), rango(11,62,66),
    rango(9,20,24), rango(9,34,38), rango(9,46,50), rango(9,58,62),
]
mon1 = []
for (y,x0,x1) in plat1:
    mon1.append(sobre(plat1, y, x0+1))
# monedas sobre los tres pozos
mon1 += [(15,25),(15,26),(15,51),(15,52),(15,67),(15,68)]
ene1 = [(15,18),(15,40),(15,62)]
n1 = mapa(80,18,suelo1,plat1,mon1,ene1,(15,3),(15,76))

# Nivel 2: 100 x 18
suelo2 = [rango(16,0,20), rango(16,27,45), rango(16,52,70), rango(16,77,100),
          rango(17,0,20), rango(17,27,45), rango(17,52,70), rango(17,77,100)]
plat2 = [
    rango(13,5,9), rango(13,17,21), rango(13,30,34), rango(13,41,45), rango(13,55,59), rango(13,66,70), rango(13,82,86), rango(13,92,96),
    rango(11,10,14), rango(11,22,26), rango(11,35,39), rango(11,48,52), rango(11,60,64), rango(11,73,77), rango(11,87,91),
    rango(9,14,18), rango(9,27,31), rango(9,40,44), rango(9,53,57), rango(9,70,74), rango(9,80,84),
]
mon2 = []
for (y,x0,x1) in plat2:
    mon2.append(sobre(plat2, y, x0+1))
# líneas de dash sobre los pozos anchos
for x in [22,23,24,47,48,49,72,73,74]:
    mon2.append((13,x))
ene2 = [(15,12),(15,36),(15,64),(15,86),(10,61)]
n2 = mapa(100,18,suelo2,plat2,mon2,ene2,(15,3),(15,96))

# Nivel 3: 120 x 18
suelo3 = [rango(16,0,15), rango(16,22,36), rango(16,43,59), rango(16,66,83), rango(16,90,120),
          rango(17,0,15), rango(17,22,36), rango(17,43,59), rango(17,66,83), rango(17,90,120)]
plat3 = [
    rango(13,4,8), rango(13,12,16), rango(13,23,27), rango(13,34,38), rango(13,45,49), rango(13,56,60), rango(13,68,72), rango(13,79,83), rango(13,92,96),
    rango(11,8,12), rango(11,18,22), rango(11,29,33), rango(11,40,44), rango(11,51,55), rango(11,62,66), rango(11,74,78), rango(11,86,90), rango(11,98,102),
    rango(9,12,16), rango(9,25,29), rango(9,36,40), rango(9,47,51), rango(9,58,62), rango(9,70,74), rango(9,82,86), rango(9,94,98), rango(9,104,108),
    rango(7,110,117),
]
mon3 = []
for (y,x0,x1) in plat3:
    mon3.append(sobre(plat3, y, x0+1))
for x in [16,17,18,37,38,39,60,61,62,84,85,86]:
    mon3.append((13,x))
# ascenso final
mon3 += [(12,93),(10,99),(8,105),(6,111),(6,112)]
ene3 = [(15,10),(15,30),(15,50),(15,75),(15,100),(12,24),(12,69),(8,37),(8,83),(6,110)]
n3 = mapa(120,18,suelo3,plat3,mon3,ene3,(15,3),(6,114))

for name, data in [('NIVEL_1', n1), ('NIVEL_2', n2), ('NIVEL_3', n3)]:
    fs = data.splitlines()
    print(name, 'cols', len(fs[0]), 'rows', len(fs), 'coins', sum(r.count('o') for r in fs), 'enemies', sum(r.count('E') for r in fs))
    for r in fs:
        assert len(r) == len(fs[0])
    Path(f'/tmp/opencode/{name}.txt').write_text(data)
