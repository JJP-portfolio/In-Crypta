const fs = require("fs");
const path = require("path");
const assert = require("assert");

const PROJECT_PATH = path.resolve(__dirname, "..", "export", "gdevelop_nativo", "IN_CRYPTA_NATIVO.json");
const DONOR_PATH = path.resolve(__dirname, "..", "In-Crypta", "export", "gdevelop_nativo", "IN_CRYPTA_NATIVO.json");

assert.ok(fs.existsSync(PROJECT_PATH), "No existe export/gdevelop_nativo/IN_CRYPTA_NATIVO.json");
const project = JSON.parse(fs.readFileSync(PROJECT_PATH, "utf8"));

// 1. Comparar claves raíz obligatorias con el JSON sano de In-Crypta/
if (fs.existsSync(DONOR_PATH)) {
  const donor = JSON.parse(fs.readFileSync(DONOR_PATH, "utf8"));
  for (const key of Object.keys(donor)) {
    assert.ok(key in project, `Falta la clave raíz obligatoria '${key}' presente en In-Crypta`);
  }
  for (const propKey of Object.keys(donor.properties || {})) {
    assert.ok(propKey in (project.properties || {}), `Falta properties.${propKey} presente en In-Crypta`);
  }
}

assert.strictEqual(project.gdVersion && project.gdVersion.major, 5, "gdVersion.major debe ser 5");
assert.strictEqual(project.gdVersion && project.gdVersion.minor, 6, "gdVersion.minor debe ser 6");
assert.strictEqual(project.properties.currentPlatform, "GDevelop JS platform");
console.log("PASS esquema_projectfile_gdevelop_5_6_285_paridad_con_InCrypta");

// 2. Verificar T305
const rawJson = JSON.stringify(project);
assert.ok(!rawJson.includes('"Jefe.Y() - 10"'), "Aún queda Jefe.Y() - 10 sin corregir (T305)");
console.log("PASS T305_pisoton_jefe");

// 3. Simulación de física PlatformerObject + bloque_gravedad
const nivel1 = project.layouts.find((l) => l.name === "Nivel 1");
const jugadorObj = [...(project.objects || []), ...(nivel1.objects || [])].find((o) => o.name === "Jugador");
const plat = jugadorObj.behaviors.find((b) => b.name === "PlatformerObject");
const GRAVITY_BASE = Number(plat.gravity);
const JUMP_SPEED_BASE = Number(plat.jumpSpeed);
const MAX_FALL_SPEED = Number(plat.maxFallingSpeed);

function simularSalto({ mantenerTecla = true, cortarEnFrame = null, iniciarPostDash = false }) {
  const dt = 1 / 60;
  let y = 0;
  let currentJumpSpeed = JUMP_SPEED_BASE;
  let currentFallSpeed = 0;
  let isOnFloor = false;
  let isJumping = !iniciarPostDash;
  let post_dash = iniciarPostDash ? 0.06 : 0;
  let gravedad_actual = GRAVITY_BASE;
  let minY = 0;
  const historialGravedad = [];

  for (let frame = 0; frame < 90; frame++) {
    const tecla = mantenerTecla && (cortarEnFrame === null || frame < cortarEnFrame);
    const isFalling = !isOnFloor && !isJumping && currentFallSpeed > 0;
    if (cortarEnFrame !== null && frame === cortarEnFrame && isJumping) {
      currentJumpSpeed = 0;
      isJumping = false;
    }
    gravedad_actual = GRAVITY_BASE;
    if (!isOnFloor && tecla && isJumping && currentJumpSpeed < 70) gravedad_actual = Math.floor(GRAVITY_BASE * 0.55);
    if (!isOnFloor && tecla && isFalling && currentFallSpeed < 70) gravedad_actual = Math.floor(GRAVITY_BASE * 0.55);
    if (post_dash > 0) gravedad_actual = Math.floor(GRAVITY_BASE * 0.5);
    historialGravedad.push(gravedad_actual);

    y += (currentFallSpeed - currentJumpSpeed) * dt;
    if (y < minY) minY = y;

    if (isJumping) {
      currentJumpSpeed -= gravedad_actual * dt;
      if (currentJumpSpeed <= 0) {
        currentJumpSpeed = 0;
        isJumping = false;
      }
    } else if (!isOnFloor) {
      currentFallSpeed = Math.min(MAX_FALL_SPEED, currentFallSpeed + gravedad_actual * dt);
    }
    if (post_dash > 0) post_dash = Math.max(0, post_dash - dt);
    if (frame > 0 && y >= 0) {
      y = 0;
      isOnFloor = true;
      historialGravedad.push(GRAVITY_BASE);
      break;
    }
  }
  return { alturaMax: -minY, historialGravedad };
}

const sSinApice = simularSalto({ mantenerTecla: false });
assert.ok(sSinApice.alturaMax >= 120 && sSinApice.alturaMax <= 136);
assert.ok(sSinApice.historialGravedad.every((g) => g === 1500));

const sConApice = simularSalto({ mantenerTecla: true });
assert.strictEqual(sConApice.historialGravedad[0], 1500);
assert.ok(sConApice.historialGravedad.includes(825));
assert.strictEqual(sConApice.historialGravedad[sConApice.historialGravedad.length - 1], 1500);

const sPostDash = simularSalto({ mantenerTecla: false, iniciarPostDash: true });
assert.strictEqual(sPostDash.historialGravedad[0], 750);
assert.strictEqual(sPostDash.historialGravedad[5], 1500);

const sCorto = simularSalto({ mantenerTecla: true, cortarEnFrame: 6 });
assert.ok(sCorto.alturaMax >= 45 && sCorto.alturaMax <= 75);

console.log("TESTS_FISICA_GDJS_OK");
