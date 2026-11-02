---
name: gdevelop-schema
description: Contrato del esquema ProjectFile de GDevelop 5.6.285 extraído de In-Crypta/export/gdevelop_nativo/IN_CRYPTA_NATIVO.json
---
1. El JSON raíz DEBE incluir `"gdVersion": {"build": 285, "major": 5, "minor": 6, "revision": 0}` e `"initialGDVersion": "5.6.285"`.
2. `properties` DEBE incluir `"platforms": [{"name": "GDevelop JS platform"}]` y `"currentPlatform": "GDevelop JS platform"`.
3. El JSON raíz DEBE incluir `"objectsFolderStructure": {"folderName": "__ROOT", "children": []}` y `"eventsFunctionsExtensions": []`.
4. `properties.platforms`, `properties.currentPlatform`, `objectsFolderStructure` y `eventsFunctionsExtensions` deben existir para que `validar_eventos_gd.py` acepte el proyecto.
