# ============================================================
# main.py — Arranque del plataformero IN CRYPTA
# ============================================================
# Uso:
#   python main.py                    → menú interactivo de consola
#   python main.py --sala 0           → sala de prueba original 0
#   python main.py --sala 3           → room test Nivel 1 rediseñado
# ============================================================
import sys

from juego import Juego
from niveles import SALAS_PRUEBA


def mostrar_menu():
    print("=== IN CRYPTA — Menú de inicio ===")
    print("")
    print("Opciones:")
    print("  0  → Jugar juego normal (campaña completa)")
    print("  1  → Test Room: Sala 1 · Movimiento (original)")
    print("  2  → Test Room: Sala 2 · Pala y ataque (original)")
    print("  3  → Test Room: Sala 3 · Custodio (original)")
    print("  4  → Test Room: Nivel 1 Rediseñado · Salto + Dash")
    print("  5  → Test Room: Nivel 2 Rediseñado · Dash + Pala")
    print("  6  → Test Room: Nivel 3 Rediseñado · Combinación total")
    print("  q  → Salir")
    print("")


def indice_desde_opcion(opcion):
    if opcion in ("1", "2", "3"):
        return int(opcion) - 1  # salas originales: índices 0-2
    if opcion in ("4", "5", "6"):
        return int(opcion) + 2  # salas rediseñadas: índices 3-5
    return None


if __name__ == "__main__":
    # Carga directa por argumento
    if len(sys.argv) >= 3 and sys.argv[1] == "--sala":
        try:
            indice = int(sys.argv[2])
            if 0 <= indice < len(SALAS_PRUEBA):
                Juego(sala_inicial=indice).run()
            else:
                print(f"Índice inválido. Rango: 0-{len(SALAS_PRUEBA)-1}")
                sys.exit(1)
        except ValueError:
            print(f"Índice inválido: {sys.argv[2]}")
            sys.exit(1)
        sys.exit(0)

    # Menú interactivo
    mostrar_menu()
    while True:
        try:
            opcion = input("Seleccioná (0-6, q para salir): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            sys.exit(0)

        if opcion == "q":
            print("Saliendo...")
            sys.exit(0)
        elif opcion == "0":
            Juego().run()
            break
        elif opcion in ("1", "2", "3", "4", "5", "6"):
            indice = indice_desde_opcion(opcion)
            if indice is not None:
                Juego(sala_inicial=indice).run()
            break
        else:
            print("Opción inválida.")
