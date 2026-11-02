// Compila un proyecto de GDevelop 5.6 a código JS ejecutable, sin el IDE.
//
// Usa el core real de GDevelop (compilado a WebAssembly) para generar el
// `code*.js` de cada escena y el `data.js` con los datos del proyecto. El
// runtime GDJS ejecuta ese código, así que el preview muestra el juego con
// la lógica de eventos real (no una reimplementación).
//
// Uso:
//   node tools/compilar_proyecto_gd.js <proyecto.json> <carpeta_destino> [libgd.js]

const fs = require('fs');
const path = require('path');

const RUTA_PROYECTO = process.argv[2];
const RUTA_DESTINO = process.argv[3];
const RUTA_LIBGD =
  process.argv[4] ||
  path.join(
    process.env.HOME || '/home/sanodesu',
    '.local/share/flatpak/app/io.gdevelop.ide/current/active/files/GDevelop',
    'resources/app.asar'
  );

if (!RUTA_PROYECTO || !RUTA_DESTINO) {
  console.error('Uso: node compilar_proyecto_gd.js <proyecto.json> <destino>');
  process.exit(1);
}

// libGD espera un global `self`.
global.self = global;

/**
 * Extrae `www/libGD.js` y `www/libGD.wasm` del app.asar del flatpak.
 * El formato asar es: [4 bytes de padding][4 bytes de tamaño][4 bytes de
 * padding][header JSON][archivos]. El header empieza en el offset 16.
 */
function extraerDelAsar(rutaAsar, destino) {
  const asar = fs.readFileSync(rutaAsar);
  const tamanoHeader = asar.readUInt32LE(12);
  const header = JSON.parse(
    asar.slice(16, 16 + tamanoHeader).toString('utf8')
  );
  const base = 16 + tamanoHeader;

  const copiar = (nodo, nombre) => {
    const offset = base + parseInt(nodo.offset, 10);
    const size = parseInt(nodo.size, 10);
    fs.writeFileSync(path.join(destino, nombre), asar.slice(offset, offset + size));
  };

  const www = header.files['www'];
  if (!www || !www.files) throw new Error('No se encontró "www" en el app.asar');
  copiar(www.files['libGD.js'], 'libGD.js');
  if (www.files['libGD.wasm']) copiar(www.files['libGD.wasm'], 'libGD.wasm');
}

(async () => {
  let rutaLibGd = RUTA_LIBGD;
  if (rutaLibGd.endsWith('.asar')) {
    const temporal = path.join('/tmp/opencode', 'libgd_preview');
    fs.mkdirSync(temporal, { recursive: true });
    extraerDelAsar(rutaLibGd, temporal);
    rutaLibGd = path.join(temporal, 'libGD.js');
  }

  const init = require(path.resolve(rutaLibGd));
  const gd = await init();

  // Sin esto el proyecto no deserializa: las extensiones de la plataforma JS
  // no están cargadas y el trap de WebAssembly aborta la carga.
  gd.ProjectHelper.initializePlatforms();

  const proyecto = new gd.Project();
  const bruto = fs.readFileSync(RUTA_PROYECTO, 'utf8');
  proyecto.unserializeFrom(gd.Serializer.fromJSON(bruto));

  fs.mkdirSync(RUTA_DESTINO, { recursive: true });

  const datosProyecto = JSON.parse(bruto);
  const mangledNames = datosProyecto.layouts.map(l => l.mangledName);
  const generador = new gd.LayoutCodeGenerator(proyecto);
  let indice = 0;
  let diagnosticos = 0;

  for (let i = 0; i < proyecto.getLayoutsCount(); i++) {
    const layout = proyecto.getLayoutAt(i);
    const includes = new gd.SetString();
    const informe = new gd.DiagnosticReport();
    const codigo = generador.generateLayoutCompleteCode(
      layout,
      includes,
      informe,
      true
    );
    diagnosticos += informe.count();
    for (let j = 0; j < informe.count(); j++) {
      const d = informe.get(j);
      console.error(
        `[${layout.getName()}] ${d.getType()} ${d.getObjectName()} ${d.getActualValue()}`
      );
    }
    let codigoFinal = codigo;
    // GDevelop's LayoutCodeGenerator strips underscores from mangled names
    // (e.g. Nivel_32_1 → Nivel_321). The runtime looks up gdjs.<mangledName>Code,
    // so we must restore the underscores to match data.js.
    const moduleMatch = codigo.match(/gdjs\.(\w+)Code\s*=\s*\{\}/);
    if (moduleMatch) {
        const nombreGenerado = moduleMatch[1];
        const nombreEsperado = mangledNames[indice];
        if (nombreGenerado !== nombreEsperado) {
            const re = new RegExp(`gdjs\\.${nombreGenerado}Code`, 'g');
            codigoFinal = codigoFinal.replace(re, `gdjs.${nombreEsperado}Code`);
        }
    }
    fs.writeFileSync(path.join(RUTA_DESTINO, `code${indice}.js`), codigoFinal);
    indice++;
  }

  // El runtime espera los datos del proyecto en `gdjs.projectData`.
  fs.writeFileSync(
    path.join(RUTA_DESTINO, 'data.js'),
    'gdjs.projectData = ' + JSON.stringify(datosProyecto) + ';',
    'utf8'
  );

  console.log(
    `Compiladas ${indice} escena(s), ${diagnosticos} diagnóstico(s).`
  );
  if (diagnosticos > 0) process.exit(1);
})();
