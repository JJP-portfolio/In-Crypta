# Ejecución del prototipo visual (diseño poeano)

Desde la raíz del proyecto, con el entorno virtual activado:

```bash
cd ~/unahur/PlataformeroMDA
source .venv/bin/activate
python prototipo_visual/visual_demo.py
```

Controles:
- `A` / `D` o flechas: mover
- `ESPACIO`: saltar
- `SHIFT` o `X`: dash
- `A`: ataque con pala
- `P`: pausa / reanudar
- `T`: cambiar tema (Camposanto / Cripta / Osario)
- `ESC`: salir

El demo genera todo visualmente con primitivas `pygame.draw`. No requiere assets externos.
