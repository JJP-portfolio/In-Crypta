// ============================================================
// tests/test_runtime_gdevelop.js — Prueba headless del runtime
// ============================================================
// Simula PixiJS, GDevelop y el JsonManager para ejecutar el
// runtime real sin abrir GDevelop. Uso:
//   node tests/test_runtime_gdevelop.js
// ============================================================

const fs = require("fs");
const path = require("path");
const vm = require("vm");
const RAIZ = path.resolve(__dirname, "..");
const codigo = fs.readFileSync(
  path.join(RAIZ, "export", "gdevelop", "runtime_gdevelop.js"),
  "utf8"
);
const datos = JSON.parse(
  fs.readFileSync(
    path.join(RAIZ, "export", "gdevelop", "game_data.json"),
    "utf8"
  )
);

class Container {
  constructor() {
    this.children = [];
    this.x = 0;
    this.y = 0;
    this.visible = true;
  }
  addChild(hijo) {
    this.children.push(hijo);
    return hijo;
  }
}

class Graphics extends Container {
  clear() {}
  beginFill() {}
  endFill() {}
  drawRect() {}
  drawRoundedRect() {}
  drawCircle() {}
  drawEllipse() {}
  moveTo() {}
  lineTo() {}
  quadraticCurveTo() {}
  closePath() {}
  lineStyle() {}
}

class Text extends Container {
  constructor(texto, estilo) {
    super();
    this.text = texto;
    this.style = estilo;
    this.anchor = { set() {} };
  }
}

const PIXI = { Container, Graphics, Text };
const teclas = {};
let tiempo = 0;
const performance = {
  now() {
    return tiempo;
  },
};
const raiz = new Container();
const capa = {
  setCameraX() {},
  setCameraY() {},
  getRenderer() {
    return { getPIXIContainer: () => raiz };
  },
};
const runtimeScene = {
  getLayer() {
    return capa;
  },
  getGame() {
    return {
      getJsonManager() {
        return {
          loadJson(nombre, callback) {
            if (nombre !== "game_data") {
              callback("recurso inesperado", null);
              return;
            }
            callback(null, datos);
          },
        };
      },
    };
  },
};

const contexto = {
  console,
  performance,
  PIXI,
  runtimeScene,
  gdjs: {
    evtTools: {
      input: {
        isKeyPressed(_scene, nombre) {
          return Boolean(teclas[nombre]);
        },
      },
    },
  },
  Math,
  Object,
  JSON,
};

vm.createContext(contexto);
vm.runInContext(codigo, contexto, { filename: "runtime_gdevelop.js" });

const estado = runtimeScene.__incryptaRuntime;
if (!estado || !estado.ready || !estado.player) {
  throw new Error("el runtime no inicializó");
}
if (estado.status !== "titulo") {
  throw new Error("el runtime no arrancó en la pantalla de título");
}
if (estado.data.format !== "incrypta.gdevelop-levels") {
  throw new Error("formato de datos inesperado");
}
if (estado.data.game.name !== "IN CRYPTA") {
  throw new Error("nombre de juego inesperado");
}
if (estado.data.levels.length !== 3) {
  throw new Error("se esperaban 3 niveles");
}
for (const nivel of estado.data.levels) {
  if (!nivel.theme) {
    throw new Error(`nivel sin tema: ${nivel.id}`);
  }
  if (nivel.souls.length !== nivel.total_souls) {
    throw new Error(`total de almas inconsistente: ${nivel.id}`);
  }
  if (!Array.isArray(nivel.decorations) || !Array.isArray(nivel.hazards)) {
    throw new Error(`nivel sin decoraciones/peligros: ${nivel.id}`);
  }
}

function frame() {
  tiempo += 1000 / 60;
  vm.runInContext(codigo, contexto, { filename: "runtime_gdevelop.js" });
}

function tecla(nombre, valor) {
  teclas[nombre] = Boolean(valor);
}

tecla("Enter", true);
frame();
tecla("Enter", false);
frame();
if (estado.status !== "jugando") {
  throw new Error("ENTER no inició la partida");
}

for (let i = 0; i < 20; i += 1) {
  frame();
}
if (!estado.player.onGround) {
  throw new Error("el jugador no aterrizó");
}

const xInicial = estado.player.x;
tecla("Right", true);
for (let i = 0; i < 30; i += 1) {
  frame();
}
tecla("Right", false);
if (estado.player.x <= xInicial) {
  throw new Error("el jugador no se movió a la derecha");
}

const yAntes = estado.player.y;
tecla("Space", true);
frame();
tecla("Space", false);
frame();
if (estado.player.y >= yAntes) {
  throw new Error("el salto no elevó al jugador");
}
for (let i = 0; i < 60; i += 1) {
  frame();
}

const xDash = estado.player.x;
tecla("Shift", true);
frame();
tecla("Shift", false);
for (let i = 0; i < 5; i += 1) {
  frame();
}
if (estado.player.dashCooldown <= 0) {
  throw new Error("el dash no activó el cooldown");
}
if (estado.player.x - xDash < 20) {
  throw new Error("el dash no desplazó al jugador");
}

for (let i = 0; i < 50; i += 1) {
  frame();
}

estado.player.x = estado.level.goal.x;
estado.player.y = estado.level.goal.y;
frame();
if (estado.status !== "nivel_completado") {
  throw new Error("no se detectó la meta del nivel 1");
}
tecla("Enter", true);
frame();
tecla("Enter", false);
if (estado.levelIndex !== 1 || estado.status !== "jugando") {
  throw new Error("no se pasó al nivel 2");
}
if (!estado.level.hazards.length) {
  throw new Error("el nivel 2 no tiene pinchos");
}
const vidasAntesDelPincho = estado.lives;
const pincho = estado.level.hazards[0];
estado.player.x = pincho.x + 1;
estado.player.y = pincho.y + 1;
estado.player.vx = 0;
estado.player.vy = 0;
estado.player.invuln = 0;
frame();
if (estado.lives !== vidasAntesDelPincho - 1) {
  throw new Error("el pincho no quitó una vida");
}

estado.player.x = estado.level.goal.x;
estado.player.y = estado.level.goal.y;
frame();
tecla("Enter", true);
frame();
tecla("Enter", false);
if (estado.levelIndex !== 2) {
  throw new Error("no se pasó al nivel 3");
}

estado.player.x = estado.level.goal.x;
estado.player.y = estado.level.goal.y;
frame();
if (estado.status !== "victoria") {
  throw new Error("no se detectó la victoria");
}

tecla("Enter", true);
frame();
tecla("Enter", false);
if (estado.status !== "jugando" || estado.levelIndex !== 0) {
  throw new Error("no se reinició después de la victoria");
}

estado.lives = 1;
estado.player.invuln = 0;
estado.player.y = estado.level.size.height + 300;
frame();
if (estado.status !== "derrota") {
  throw new Error("no se detectó la derrota");
}

console.log("TESTS_GDEVELOP_OK levels=3");
