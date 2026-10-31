// Extrae la tabla real de metadatos de acciones/condiciones/expresiones de
// GDevelop 5.6 desde el core compilado a WebAssembly (libGD) del IDE.
//
// Por qué: la tabla escrita a mano se desincronizó de la API real y provocó
// que el exportador omitiera los parámetros "code-only" (objectsContext,
// currentScene, conditionInverted), lo que desplazaba TODOS los parámetros de
// las acciones al leerlas en el IDE.
//
// Uso:
//   node tools/exportador/extraer_metadatos.js <ruta_libgd.js> <salida.json>
//
// Requiere tener GDevelop 5.6 instalado (flatpak) o el par libGD.js/libGD.wasm
// a mano. No se ejecuta durante el export normal: el JSON que produce queda
// versionado en tools/exportador/datos/.

const fs = require('fs');
const path = require('path');

const RUTA_LIBGD = process.argv[2];
const RUTA_SALIDA = process.argv[3];

if (!RUTA_LIBGD || !RUTA_SALIDA) {
  console.error(
    'Uso: node extraer_metadatos.js <ruta_libgd.js> <salida.json>'
  );
  process.exit(1);
}

// libGD espera un global `self`.
global.self = global;

const init = require(path.resolve(RUTA_LIBGD));

const TIPOS_OBJETO = ['', 'Sprite', 'TextObject', 'TextObject::Text'];
const TIPOS_COMPORTAMIENTO = [
  'PlatformBehavior::PlatformerObjectBehavior',
  'TopDownMovementBehavior',
  'AnchorBehavior',
  'DestroyOutsideBehavior',
  'DraggableBehavior',
  'PhysicsBehavior',
  'PathfindingBehavior',
  'TweenBehavior',
  'TextContainerBehavior',
  'ResizableBehavior',
  'ScalableBehavior',
  'FlippableBehavior',
  'EffectBehavior',
  'OpacityBehavior',
  'AnimatableCapability',
];

(async () => {
  const gd = await init();

  // Sin esto, el proyecto no puede deserializar: las extensiones de la
  // plataforma JS no están cargadas y el trap de WebAssembly aborta.
  gd.ProjectHelper.initializePlatforms();

  const proyecto = gd.ProjectHelper.createNewGDJSProject();
  const extensiones = proyecto.getCurrentPlatform().getAllPlatformExtensions();

  const tabla = {};

  const volcar = (mapa, tipo) => {
    if (!mapa || !mapa.keys) return;
    const claves = mapa.keys();
    for (let i = 0; i < claves.size(); i++) {
      const clave = claves.get(i);
      const meta = mapa.get(clave);
      const parametros = [];
      for (let j = 0; j < meta.getParametersCount(); j++) {
        const param = meta.getParameter(j);
        parametros.push({
          t: param.getType(),
          // Los parámetros "code-only" (objectsContext, currentScene,
          // conditionInverted) SÍ se serializan en el JSON del proyecto,
          // como cadenas vacías, en su posición exacta.
          c: param.isCodeOnly() ? 1 : 0,
        });
      }
      tabla[`${tipo}:${clave}`] = {
        kind: tipo,
        fn: meta.getFunctionName(),
        params: parametros,
      };
    }
  };

  for (let i = 0; i < extensiones.size(); i++) {
    const extension = extensiones.get(i);
    volcar(extension.getAllActions(), 'action');
    volcar(extension.getAllConditions(), 'condition');
    volcar(extension.getAllExpressions(), 'expression');
    volcar(extension.getAllStrExpressions(), 'strExpression');
    for (const tipo of TIPOS_OBJETO) {
      volcar(extension.getAllActionsForObject(tipo), 'action');
      volcar(extension.getAllConditionsForObject(tipo), 'condition');
      volcar(extension.getAllExpressionsForObject(tipo), 'expression');
      volcar(extension.getAllStrExpressionsForObject(tipo), 'strExpression');
    }
    for (const tipo of TIPOS_COMPORTAMIENTO) {
      volcar(extension.getAllActionsForBehavior(tipo), 'action');
      volcar(extension.getAllConditionsForBehavior(tipo), 'condition');
      volcar(extension.getAllExpressionsForBehavior(tipo), 'expression');
      volcar(extension.getAllStrExpressionsForBehavior(tipo), 'strExpression');
    }
  }

  fs.writeFileSync(RUTA_SALIDA, JSON.stringify(tabla));
  console.log(`Entradas extraídas: ${Object.keys(tabla).length}`);
})();
