# ARQUITECTURA DEL EXPORTADOR AUTOMÁTICO DE PYGAME A GDEVELOP 5.6

## 1. ARQUITECTURA DEL SOFTWARE

El exportador automático de Pygame a GDevelop 5.6 sigue una arquitectura modular diseñada para facilitar la conversión sin pérdida de información. La arquitectura se compone de los siguientes componentes:

### 1.1. Manifiesto

El manifiesto es un archivo JSON que define la estructura del proyecto Pygame y las configuraciones específicas para la exportación. Contiene metadatos como el título del juego, versión, autores y configuraciones de exportación.

```json
{
  "title": "Mi Juego",
  "version": "1.0.0",
  "authors": ["Desarrollador 1", "Desarrollador 2"],
  "export_config": {
    "gdevelop_version": "5.6",
    "assets_path": "assets",
    "levels_path": "levels"
  }
}
```

### 1.2. Modelo

El modelo es una representación intermedia del proyecto Pygame. Se genera a partir del manifiesto y contiene todas las entidades, texturas, sonidos, niveles, salas de prueba, HUD, estados de juego y reglas de física/eventos.

```python
class GameModel:
    def __init__(self):
        self.entities = []
        self.textures = {}
        self.sounds = {}
        self.levels = {}
        self.test_rooms = {}
        self.hud = {}
        self.game_states = {}
        self.physics_rules = {}
        self.event_rules = {}
```

### 1.3. Adaptadores

Los adaptadores son componentes que se encargan de mapear las entidades, texturas, sonidos, niveles, salas de prueba, HUD, estados de juego y reglas de física/eventos del modelo a la estructura de GDevelop. Cada adaptador es responsable de una parte específica del modelo.

```python
class EntityAdapter:
    def adapt(self, entity):
        # Mapea la entidad de Pygame a la estructura de GDevelop
        pass

class TextureAdapter:
    def adapt(self, texture):
        # Mapea la textura de Pygame a la estructura de GDevelop
        pass

# ...
```

### 1.4. Generación de Assets y Reglas

La generación de assets y reglas se encarga de crear los assets y reglas necesarios para el proyecto GDevelop. Utiliza los adaptadores para mapear las entidades, texturas, sonidos, niveles, salas de prueba, HUD, estados de juego y reglas de física/eventos del modelo a la estructura de GDevelop.

```python
class AssetGenerator:
    def generate(self, model):
        # Genera los assets necesarios para el proyecto GDevelop
        pass

class RuleGenerator:
    def generate(self, model):
        # Genera las reglas necesarias para el proyecto GDevelop
        pass
```

### 1.5. Proyecto GDevelop

El proyecto GDevelop es el resultado final del proceso de exportación. Contiene todos los assets y reglas generados por el generador de assets y reglas.

### 1.6. Verificación de Paridad

La verificación de paridad se encarga de asegurarse de que el proyecto GDevelop generado sea idéntico al proyecto Pygame original. Utiliza pruebas automatizadas para comparar las entidades, texturas, sonidos, niveles, salas de prueba, HUD, estados de juego y reglas de física/eventos del proyecto Pygame con los del proyecto GDevelop.

```python
class ParityVerifier:
    def verify(self, pygame_project, gdevelop_project):
        # Verifica que el proyecto GDevelop sea idéntico al proyecto Pygame
        pass
```

## 2. PRINCIPIO 'SINGLE SOURCE OF TRUTH': PYGAME ES LA ÚNICA FUENTE DE VERDAD

El principio 'Single Source of Truth' establece que Pygame es la única fuente de verdad para el proyecto. Esto significa que todas las configuraciones, niveles, entidades, audio y otros elementos del juego deben definirse en Pygame y luego exportarse a GDevelop.

### 2.1. Configuración

La configuración del juego se define en el archivo `config.py`. Contiene configuraciones como el título del juego, versión, autores y configuraciones de exportación.

```python
# config.py

TITLE = "Mi Juego"
VERSION = "1.0.0"
AUTHORS = ["Desarrollador 1", "Desarrollador 2"]

EXPORT_CONFIG = {
    "gdevelop_version": "5.6",
    "assets_path": "assets",
    "levels_path": "levels"
}
```

### 2.2. Niveles

Los niveles del juego se definen en el archivo `nivel.py`. Cada nivel contiene entidades, texturas, sonidos, salas de prueba, HUD, estados de juego y reglas de física/eventos.

```python
# nivel.py

class Nivel:
    def __init__(self, name):
        self.name = name
        self.entities = []
        self.textures = {}
        self.sounds = {}
        self.test_rooms = {}
        self.hud = {}
        self.game_states = {}
        self.physics_rules = {}
        self.event_rules = {}
```

### 2.3. Entidades

Las entidades del juego se definen en el archivo `entidades.py`. Cada entidad contiene configuraciones como el nombre, textura, sonido, reglas de física/eventos y otros elementos.

```python
# entidades.py

class Entidad:
    def __init__(self, name, texture, sound, physics_rules, event_rules):
        self.name = name
        self.texture = texture
        self.sound = sound
        self.physics_rules = physics_rules
        self.event_rules = event_rules
```

### 2.4. Audio

El audio del juego se define en el archivo `audio.py`. Contiene configuraciones como el nombre, ruta del archivo y otros elementos.

```python
# audio.py

class Audio:
    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path
```

## 3. CÓMO EL EXPORTADOR MAPEA AUTOMÁTICAMENTE ENTIDADES, TEXTURAS, SONIDOS, NIVELES, SALAS DE PRUEBA, HUD, ESTADOS DE JUEGO Y REGLAS DE FÍSICA/EVENTOS SIN HARDCODEAR NIVELES ESPECÍFICOS

El exportador mapea automáticamente entidades, texturas, sonidos, niveles, salas de prueba, HUD, estados de juego y reglas de física/eventos sin hardcodear niveles específicos. Utiliza adaptadores para mapear las entidades, texturas, sonidos, niveles, salas de prueba, HUD, estados de juego y reglas de física/eventos del modelo a la estructura de GDevelop.

### 3.1. Adaptadores

Los adaptadores son componentes que se encargan de mapear las entidades, texturas, sonidos, niveles, salas de prueba, HUD, estados de juego y reglas de física/eventos del modelo a la estructura de GDevelop. Cada adaptador es responsable de una parte específica del modelo.

```python
class EntityAdapter:
    def adapt(self, entity):
        # Mapea la entidad de Pygame a la estructura de GDevelop
        pass

class TextureAdapter:
    def adapt(self, texture):
        # Mapea la textura de Pygame a la estructura de GDevelop
        pass

# ...
```

## 4. CÓMO FUNCIONA EL PIPELINE: MANIFIESTO -> MODELO -> ADAPTADORES -> GENERACIÓN DE ASSETS Y REGLAS -> PROYECTO GDEVELOP -> VERIFICACIÓN DE PARIDAD

El pipeline del exportador automático de Pygame a GDevelop 5.6 se compone de los siguientes pasos:

### 4.1. Manifiesto

El manifiesto es un archivo JSON que define la estructura del proyecto Pygame y las configuraciones específicas para la exportación. Contiene metadatos como el título del juego, versión, autores y configuraciones de exportación.

```json
{
  "title": "Mi Juego",
  "version": "1.0.0",
  "authors": ["Desarrollador 1", "Desarrollador 2"],
  "export_config": {
    "gdevelop_version": "5.6",
    "assets_path": "assets",
    "levels_path": "levels"
  }
}
```

### 4.2. Modelo

El modelo es una representación intermedia del proyecto Pygame. Se genera a partir del manifiesto y contiene todas las entidades, texturas, sonidos, niveles, salas de prueba, HUD, estados de juego y reglas de física/eventos.

```python
class GameModel:
    def __init__(self):
        self.entities = []
        self.textures = {}
        self.sounds = {}
        self.levels = {}
        self.test_rooms = {}
        self.hud = {}
        self.game_states = {}
        self.physics_rules = {}
        self.event_rules = {}
```

### 4.3. Adaptadores

Los adaptadores son componentes que se encargan de mapear las entidades, texturas, sonidos, niveles, salas de prueba, HUD, estados de juego y reglas de física/eventos del modelo a la estructura de GDevelop. Cada adaptador es responsable de una parte específica del modelo.

```python
class EntityAdapter:
    def adapt(self, entity):
        # Mapea la entidad de Pygame a la estructura de GDevelop
        pass

class TextureAdapter:
    def adapt(self, texture):
        # Mapea la textura de Pygame a la estructura de GDevelop
        pass

# ...
```

### 4.4. Generación de Assets y Reglas

La generación de assets y reglas se encarga de crear los assets y reglas necesarios para el proyecto GDevelop. Utiliza los adaptadores para mapear las entidades, texturas, sonidos, niveles, salas de prueba, HUD, estados de juego y reglas de física/eventos del modelo a la estructura de GDevelop.

```python
class AssetGenerator:
    def generate(self, model):
        # Genera los assets necesarios para el proyecto GDevelop
        pass

class RuleGenerator:
    def generate(self, model):
        # Genera las reglas necesarias para el proyecto GDevelop
        pass
```

### 4.5. Proyecto GDevelop

El proyecto GDevelop es el resultado final del proceso de exportación. Contiene todos los assets y reglas generados por el generador de assets y reglas.

### 4.6. Verificación de Paridad

La verificación de paridad se encarga de asegurarse de que el proyecto GDevelop generado sea idéntico al proyecto Pygame original. Utiliza pruebas automatizadas para comparar las entidades, texturas, sonidos, niveles, salas de prueba, HUD, estados de juego y reglas de física/eventos del proyecto Pygame con los del proyecto GDevelop.

```python
class ParityVerifier:
    def verify(self, pygame_project, gdevelop_project):
        # Verifica que el proyecto GDevelop sea idéntico al proyecto Pygame
        pass
```

## 5. INSTRUCCIONES DE USO

Para ejecutar el exportador y verificar paridad:

```bash
# Genera el proyecto GDevelop nativo y los assets
.venv/bin/python tools/generar_proyecto_nativo.py

# Valida la forma de los eventos contra el núcleo de GDevelop 5.6
.venv/bin/python tools/validar_eventos_gd.py

# Compara el JSON exportado contra el modelo vivo de Pygame
.venv/bin/python tools/verificar_paridad.py

# Suite de certificación completa (incluye tests del juego y del HUD)
.venv/bin/python tools/exportar_todo.py
```

Todo el exportador vive en `tools/`: `generar_proyecto_nativo.py` (CLI),
`tools/exportador/` (paquete modular), `tools/verificar_paridad.py`,
`tools/validar_eventos_gd.py` y `tools/exportar_todo.py` (orquestador). No hay
paquete pip separado ni CLI externo.
