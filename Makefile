#---- Comandos de ejecucion y pruebas ----#

SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

ROOT_DIR := $(shell pwd)
PYTHON := $(shell if [ -x "$(ROOT_DIR)/.venv/bin/python" ]; then echo "$(ROOT_DIR)/.venv/bin/python"; else command -v python3 || command -v python; fi)

.PHONY: help run test validate

help:
	@echo "Comandos disponibles:"
	@echo "  make run       - Inicia el juego (Pygame)"
	@echo "  make test      - Ejecuta los tests en modo headless"
	@echo "  make validate  - Valida el mapa y el entorno"

run:
	@./jugar_pygame.sh

test:
	@PYTHONPATH="$(ROOT_DIR)" SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$(PYTHON)" -m pytest "$(ROOT_DIR)/tests" -q

validate:
	@PYTHONPATH="$(ROOT_DIR)" "$(PYTHON)" tools/validar_niveles.py
	@./jugar_pygame.sh --check
