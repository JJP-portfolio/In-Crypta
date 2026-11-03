# ============================================================================
# Makefile — Automatización DevEx para IN CRYPTA 1.0.0 (Pygame / Pygame-CE)
# ============================================================================

SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

ROOT_DIR := $(shell pwd)
PYTHON := $(shell if [ -x "$(ROOT_DIR)/.venv/bin/python" ]; then echo "$(ROOT_DIR)/.venv/bin/python"; else command -v python3 || command -v python; fi)
PORT ?= 8000

.PHONY: help run web build-web docs test validate

help: ## Muestra esta ayuda con los comandos disponibles
	@echo "========================================================"
	@echo "  IN CRYPTA 1.0.0 — Comandos de Desarrollo y Ejecución"
	@echo "========================================================"
	@echo "  make run        Inicia la versión Desktop nativa (Pygame-CE)"
	@echo "  make web        Inicia el servidor WebAssembly (Pygbag) en PORT=$(PORT)"
	@echo "  make build-web  Compila la versión WebAssembly lista para publicar"
	@echo "  make docs       Muestra la documentación del proyecto (README.md)"
	@echo "  make test       Ejecuta las suites de pruebas en modo headless (SDL dummy)"
	@echo "  make validate   Verifica ejecutables y estado de la build Web"
	@echo "========================================================"

run: ## Inicia el juego en versión Desktop (Pygame)
	@./jugar_pygame.sh

web: ## Levanta el servidor WebAssembly en http://localhost:$(PORT)/index.html
	@PORT=$(PORT) ./jugar_web_pygame.sh

build-web: ## Compila la versión WebAssembly autónoma
	@"$(PYTHON)" tools/exportar_web_pygame.py --build

docs: ## Muestra la documentación del proyecto
	@cat README.md

test: ## Ejecuta las suites de tests de Pygame en modo headless
	@PYTHONPATH="$(ROOT_DIR)" SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$(PYTHON)" -m pytest "$(ROOT_DIR)/tests" -q

validate: ## Ejecuta la validación no interactiva de ejecutables y build Web
	@./jugar_pygame.sh --check
	@./jugar_web_pygame.sh --check
