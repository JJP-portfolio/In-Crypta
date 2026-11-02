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

// Verificación de fidelidad de salto: Salto corto (corte de salto) vs Salto completo
const ySuelo = estado.player.y;
let yMinSaltoCorto = ySuelo;

// 1. Salto corto: pulsar y soltar inmediatamente
tecla("Space", true);
frame();
tecla("Space", false);
for (let i = 0; i < 40; i += 1) {
  frame();
  if (estado.player.y < yMinSaltoCorto) {
    yMinSaltoCorto = estado.player.y;
  }
}
const alturaSaltoCorto = ySuelo - yMinSaltoCorto;

// Esperar a que el jugador aterrice firmemente
for (let i = 0; i < 30; i += 1) {
  frame();
}

// 2. Salto completo: mantener pulsado Space durante la fase ascendente
const ySueloLargo = estado.player.y;
let yMinSaltoLargo = ySueloLargo;
tecla("Space", true);
for (let i = 0; i < 26; i += 1) {
  frame();
  if (estado.player.y < yMinSaltoLargo) {
    yMinSaltoLargo = estado.player.y;
  }
}
tecla("Space", false);
const alturaSaltoLargo = ySueloLargo - yMinSaltoLargo;

// Esperar a aterrizar
for (let i = 0; i < 50; i += 1) {
  frame();
}

console.log(`PARIDAD_SALTO: corto=${alturaSaltoCorto.toFixed(1)}px | largo=${alturaSaltoLargo.toFixed(1)}px`);
if (alturaSaltoCorto <= 0 || alturaSaltoLargo <= 0) {
  throw new Error("el salto no elevó al jugador");
}
if (alturaSaltoCorto >= alturaSaltoLargo * 0.7) {
  throw new Error(`el corte de salto no funcionó: corto=${alturaSaltoCorto.toFixed(1)} vs largo=${alturaSaltoLargo.toFixed(1)}`);
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

// Prueba de Corner Nudge (Celeste style) en Dash:
// Si rozamos una esquina por 4px durante el dash, debe deslizar y no chocar contra la pared
estado.player.dashCooldown = 0;
estado.player.airDash = 1;
estado.player.x = 200;
estado.player.y = 300;
estado.level.solids.push({ x: 220, y: 326, w: 32, h: 32 }); // rozamiento de 4px en la esquina inferior (y=326 vs jugador y+h=330)
tecla("Shift", true);
frame();
tecla("Shift", false);
frame();
if (estado.player.x <= 200) {
  throw new Error("el corner nudge en dash no permitió el paso");
}
estado.level.solids.pop(); // restaurar lista de sólidos

// Prueba: Pisotón sobre enemigo en Nivel 1 sin pala (debe matar y rebotar)
const enemigoPrueba = { x: 250, y: 320, w: 26, h: 26, minX: 200, maxX: 300, dir: 1, speed: 50, alive: true };
estado.enemies.push(enemigoPrueba);
estado.player.dashTime = 0;
estado.player.hasShovel = false;
estado.player.x = enemigoPrueba.x;
estado.player.y = enemigoPrueba.y - 20;
estado.player.vy = 200;
frame();
if (enemigoPrueba.alive) {
  throw new Error("el pisotón sin pala debió matar al enemigo en el nivel 1");
}
if (estado.player.vy >= 0) {
  throw new Error("el pisotón debió rebotar al jugador");
}
estado.enemies.pop();

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

if (!estado.player.hasShovel) {
  throw new Error("el jugador debió iniciar con pala en el nivel 3");
}
tecla("KeyZ", true);
frame();
tecla("KeyZ", false);
frame();
if (estado.player.attackTimer <= 0) {
  throw new Error("el ataque de pala no se activó");
}

estado.player.x = estado.level.goal.x;
estado.player.y = estado.level.goal.y;
frame();
if (estado.status === "victoria") {
  throw new Error("el portón debió estar sellado mientras el Custodio vivía");
}

const custodio = estado.bosses[0];
if (!custodio) {
  throw new Error("no se encontró al Custodio en el nivel 3");
}

custodio.invuln = 0;
estado.player.attackTimer = 0;
estado.player.x = custodio.x - 30;
estado.player.y = custodio.y + 20;
estado.player.dir = 1;
tecla("KeyZ", true);
frame();
tecla("KeyZ", false);
frame();
if (custodio.hp >= 6) {
  throw new Error("la pala no dañó al Custodio en Fase 1");
}

// Pasar a Fase 2 (HP <= 3)
custodio.hp = 3;
custodio.fase = 2;
custodio.invuln = 0;

// En Fase 2, la pala rebota y no baja vida
estado.player.attackTimer = 0;
estado.player.x = custodio.x - 30;
estado.player.y = custodio.y + 20;
estado.player.dir = 1;
tecla("KeyZ", true);
frame();
if (custodio.hp !== 3) {
  throw new Error("la pala no debió dañar al Custodio en Fase 2");
}
if (estado.player.vx >= 0) {
  throw new Error("la pala no rebotó al jugador en Fase 2");
}
tecla("KeyZ", false);
frame();

// Pisotón aéreo en Fase 2 sí daña al Custodio y recarga dash
custodio.invuln = 0;
estado.player.attackTimer = 0;
estado.player.attackHitbox = null;
estado.player.x = custodio.x + 10;
estado.player.y = custodio.y - 12;
estado.player.vy = 200;
estado.player.airDash = 0;
frame();
if (custodio.hp >= 3) {
  throw new Error("el pisotón debió dañar al Custodio en Fase 2");
}
if (estado.player.vy >= 0) {
  throw new Error("el pisotón debió hacer rebotar al jugador");
}
if (estado.player.airDash !== estado.data.game.rules.dash_usos_aire) {
  throw new Error("el pisotón debió recargar el dash aéreo");
}

custodio.hp = 0;
custodio.alive = false;
frame();

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
