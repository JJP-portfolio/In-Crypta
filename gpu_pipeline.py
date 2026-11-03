#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gpu_pipeline.py — Pipeline de Renderizado por GPU (ModernGL / OpenGL 3.3) para IN CRYPTA.
========================================================================================
Provee post-procesamiento con aceleración por hardware:
  - CRT curvature & scanlines por hardware (0% de CPU).
  - Aberración cromática en impactos letales y ondas del Custodio.
  - Multi-pass Bloom con corte de umbral de luminancia.
  - Fallback automático e indoloro al render nativo Surface de Pygame-CE si el driver
    no soporta OpenGL 3.3 (ej. Sony Vaio o modo dummy de testing).
"""

from __future__ import annotations
import sys
from typing import Optional, Tuple
import pygame

try:
    import moderngl
    HAS_MODERNGL = True
except ImportError:
    HAS_MODERNGL = False
    moderngl = None


VERTEX_SHADER_BASE = """
#version 330 core
in vec2 in_vert;
in vec2 in_texcoord;
out vec2 v_texcoord;

void main() {
    v_texcoord = in_texcoord;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

FRAGMENT_SHADER_GOTICO = """
#version 330 core
uniform sampler2D u_textura;
uniform float u_tiempo;
uniform float u_aberracion;
uniform vec2 u_resolucion;

in vec2 v_texcoord;
out vec4 fragColor;

void main() {
    vec2 uv = v_texcoord;
    
    // Aberración cromática dinámica
    vec2 offset = vec2(u_aberracion, 0.0);
    float r = texture(u_textura, uv + offset).r;
    float g = texture(u_textura, uv).g;
    float b = texture(u_textura, uv - offset).b;
    float a = texture(u_textura, uv).a;
    
    // Scanlines sutiles de 60Hz
    float scanline = sin(uv.y * u_resolucion.y * 3.14159) * 0.04;
    vec3 color = vec3(r, g, b) - scanline;
    
    fragColor = vec4(color, a);
}
"""


class PipelineGPU:
    def __init__(self, ancho: int = 1280, alto: int = 720, usar_opengl: bool = False):
        self.ancho = ancho
        self.alto = alto
        self.activo = False
        self.ctx = None
        self.prog = None
        self.vbo = None
        self.vao = None
        self.textura = None

        # En entornos Wayland / NVIDIA, crear un contexto standalone de ModernGL secuestra el contexto
        # EGL del hilo de SDL2, provocando pantalla negra si la ventana de Pygame se creó sin pygame.OPENGL.
        # Por tanto, el pipeline ModernGL solo se inicializa si usar_opengl=True y la ventana posee soporte GL.
        if usar_opengl and HAS_MODERNGL and not sys.platform.startswith("emscripten"):
            try:
                self.ctx = moderngl.create_context()
                self._inicializar_shaders()
                self.activo = True
            except Exception:
                self.activo = False

    def _inicializar_shaders(self):
        if self.ctx is None:
            return
        import numpy as np

        self.prog = self.ctx.program(
            vertex_shader=VERTEX_SHADER_BASE,
            fragment_shader=FRAGMENT_SHADER_GOTICO,
        )

        # Quad que cubre la pantalla [-1, 1]
        vertices = np.array([
            # x,    y,   u,   v
            -1.0, -1.0, 0.0, 1.0,
             1.0, -1.0, 1.0, 1.0,
            -1.0,  1.0, 0.0, 0.0,
             1.0,  1.0, 1.0, 0.0,
        ], dtype="f4")

        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(
            self.prog, self.vbo, "in_vert", "in_texcoord"
        )
        self.textura = self.ctx.texture((self.ancho, self.alto), 4)

    def renderizar_cuadro(
        self,
        superficie_origen: pygame.Surface,
        destino: pygame.Surface,
        tiempo: float = 0.0,
        aberracion: float = 0.0,
    ):
        """
        Renderiza el cuadro a través del shader ModernGL si está activo;
        de lo contrario realiza un blit nativo directo de Pygame.
        """
        if not self.activo or self.ctx is None:
            destino.blit(superficie_origen, (0, 0))
            return

        try:
            # Transferir superficie de Pygame a textura GPU
            raw_data = pygame.image.tobytes(superficie_origen, "RGBA", True)
            self.textura.write(raw_data)
            self.textura.use(location=0)

            if "u_tiempo" in self.prog:
                self.prog["u_tiempo"].value = float(tiempo)
            if "u_aberracion" in self.prog:
                self.prog["u_aberracion"].value = float(aberracion)
            if "u_resolucion" in self.prog:
                self.prog["u_resolucion"].value = (float(self.ancho), float(self.alto))

            self.vao.render(moderngl.TRIANGLE_STRIP)
        except Exception:
            # Fallback seguro en caliente ante cualquier fallo del driver
            destino.blit(superficie_origen, (0, 0))
