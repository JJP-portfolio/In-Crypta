# ============================================================================
# Makefile — Automatización DevEx para IN CRYPTA 1.0.0 (Linux / Multiplataforma)
# ============================================================================

SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

ROOT_DIR := $(shell pwd)
PYTHON := $(shell if [ -x "$(ROOT_DIR)/.venv/bin/python" ]; then echo "$(ROOT_DIR)/.venv/bin/python"; else command -v python3 || command -v python; fi)
PORT ?= 8000

.PHONY: help run web docs export test validate

help: ## Muestra esta ayuda con los comandos disponibles
	@echo "========================================================"
	@echo "  IN CRYPTA 1.0.0 — Comandos de Desarrollo y Ejecución"
	@echo "========================================================"
	@echo "  make run       Inicia la versión Desktop (Pygame-CE)"
	@echo "  make web       Inicia el servidor Web (GDevelop JS / PixiJS) en PORT=$(PORT)"
	@echo "  make docs      Abre la página explicativa del proyecto y el laboratorio visual"
	@echo "  make export    Ejecuta el pipeline completo de exportación, paridad y tests"
	@echo "  make test      Ejecuta todas las suites de pruebas en modo headless (SDL dummy)"
	@echo "  make validate  Verifica los 4 scripts (.sh --check), eventos GD y paridad"
	@echo "========================================================"

run: ## Inicia el juego en versión Desktop (Pygame)
	@./jugar_pygame.sh

web: ## Levanta el runtime Web en http://localhost:$(PORT)/export/gdevelop/index.html
	@PORT=$(PORT) ./jugar_web.sh

docs: ## Abre la documentación interactiva y el laboratorio de propuestas visuales
	@./ver_propuestas.sh

export: ## Sincroniza exportadores GDevelop, valida paridad y ejecuta pruebas
	@./exportar_todo.sh

test: ## Ejecuta las suites de tests (Pygame + Exportador + GDJS) en modo headless
	@PYTHONPATH="$(ROOT_DIR)" SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$(PYTHON)" -m pytest "$(ROOT_DIR)/tests" -q
	@PYTHONPATH="$(ROOT_DIR)" SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$(PYTHON)" "$(ROOT_DIR)/tests/test_logica.py"
	@PYTHONPATH="$(ROOT_DIR)" SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$(PYTHON)" "$(ROOT_DIR)/tests/test_hud.py"
	@if command -v node >/dev/null 2>&1 && [ -f "$(ROOT_DIR)/tests/test_fisica_gdjs.js" ]; then \
		node "$(ROOT_DIR)/tests/test_fisica_gdjs.js"; \
	fi

validate: ## Ejecuta la validación no interactiva de ejecutables, exportadores y documentos
	@./jugar_pygame.sh --check
	@./exportar_todo.sh --check
	@./jugar_web.sh --check
	@./ver_propuestas.sh --check
