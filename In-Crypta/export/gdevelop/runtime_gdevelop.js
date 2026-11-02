// ============================================================
// runtime_gdevelop.js — IN CRYPTA jugable dentro de GDevelop
// ============================================================
// Este evento dibuja y simula el juego completo con PixiJS.
// El JSON de niveles se carga como recurso "game_data".
// Marcador para el instalador:
//   INCRYPTA_GDEVELOP_RUNTIME_V1
// ============================================================

(() => {
const INCRYPTA_RUNTIME = "INCRYPTA_GDEVELOP_RUNTIME_V1";
const INCRYPTA_RECURSO = "game_data";
const INCRYPTA_FORMATO = "incrypta.gdevelop-levels";
const ANCHO = 960;
const ALTO = 540;

const ESTILOS_GOTICOS_WEB = {
  monastico: {
    nombre: "Monástico Litúrgico",
    panelBg: 0x120e16,
    borde: 0x8f7330,
    oro: 0xe5b842,
    carmesi: 0x8a151b,
    texto: 0xdfd3b6,
    secundario: 0xa8987a,
    dash: 0xf3d27a,
    alma: 0xe5b842,
    bossColor: 0x8a151b,
    bossSec: 0xe5b842
  },
  hierro: {
    nombre: "Hierro Negro Brutalista",
    panelBg: 0x0e0f12,
    borde: 0x5a6070,
    oro: 0x8a92a3,
    carmesi: 0xc4402e,
    texto: 0xcad1e3,
    secundario: 0x7c8496,
    dash: 0x39d5b8,
    alma: 0x39d5b8,
    bossColor: 0xc4402e,
    bossSec: 0x39d5b8
  },
  espectral: {
    nombre: "Ectoplasma Espectral",
    panelBg: 0x080b10,
    borde: 0x2e4254,
    oro: 0x5af2e5,
    carmesi: 0xa58bff,
    texto: 0xf0fcff,
    secundario: 0x8fa6b8,
    dash: 0x5af2e5,
    alma: 0xa58bff,
    bossColor: 0x5af2e5,
    bossSec: 0xa58bff
  },
  osario: {
    nombre: "Osario Barroco",
    panelBg: 0x0a0809,
    borde: 0x6e2840,
    oro: 0xe8e2d0,
    carmesi: 0x9b101c,
    texto: 0xe8e2d0,
    secundario: 0x9b9480,
    dash: 0xb23b44,
    alma: 0xded7c4,
    bossColor: 0x9b101c,
    bossSec: 0xe8e2d0
  }
};

function colorNum(hex) {
  return parseInt(String(hex).replace("#", ""), 16);
}

function limitar(valor, minimo, maximo) {
  return Math.max(minimo, Math.min(maximo, valor));
}

function solapan(a, b) {
  return (
    a.x < b.x + b.w &&
    a.x + a.w > b.x &&
    a.y < b.y + b.h &&
    a.y + a.h > b.y
  );
}

function obtenerRaizPixi() {
  const capa = runtimeScene.getLayer("");
  const renderer = capa && capa.getRenderer ? capa.getRenderer() : null;
  if (renderer && renderer.getPIXIContainer) {
    return renderer.getPIXIContainer();
  }
  if (capa && typeof capa.getRendererObject === "function") {
    return capa.getRendererObject();
  }
  return null;
}

function crearTexto(padre, contenido, tamano, color, x, y, opciones = {}) {
  const estilo = {
    fontFamily: "Arial",
    fontSize: tamano,
    fill: color,
    fontWeight: "bold",
  };
  if (opciones.wordWrap) {
    estilo.wordWrap = true;
    estilo.wordWrapWidth = opciones.wordWrap;
  }
  if (opciones.family) {
    estilo.fontFamily = opciones.family;
  }
  const texto = new PIXI.Text(contenido, estilo);
  texto.x = x;
  texto.y = y;
  if (opciones.centrado && texto.anchor) {
    texto.anchor.set(0.5, 0);
  }
  padre.addChild(texto);
  return texto;
}

function tecla(nombre) {
  try {
    return gdjs.evtTools.input.isKeyPressed(runtimeScene, nombre);
  } catch (error) {
    return false;
  }
}

function leerTeclas() {
  return {
    izquierda: tecla("Left") || tecla("KeyA") || tecla("a"),
    derecha: tecla("Right") || tecla("KeyD") || tecla("d"),
    salto: tecla("Space") || tecla("Up") || tecla("KeyW") || tecla("w"),
    dash: tecla("Shift") || tecla("LShift") || tecla("RShift") || tecla("KeyX") || tecla("x"),
    ataque: tecla("KeyJ") || tecla("j") || tecla("KeyZ") || tecla("z") || tecla("KeyC") || tecla("c") || tecla("MouseLeft"),
    pausa: tecla("KeyP") || tecla("p") || tecla("Escape"),
    reiniciar: tecla("KeyR") || tecla("r"),
    enter: tecla("Enter") || tecla("Return") || tecla("MouseLeft"),
    silencio: tecla("KeyM") || tecla("m"),
    f2: tecla("F2") || tecla("f2") || tecla("KeyF2") || (typeof window !== "undefined" && Boolean(window.__incrypta_f2_pressed)),
  };
}

function justo(state, nombre) {
  return Boolean(state.keys[nombre]) && !state.prev[nombre];
}

function soltado(state, nombre) {
  return !state.keys[nombre] && Boolean(state.prev[nombre]);
}

function crearParticula(state, x, y, vx, vy, vida, color, tamano, gravedad) {
  state.particles.push({
    x,
    y,
    vx,
    vy,
    vida,
    vidaInicial: vida,
    color,
    tamano,
    gravedad: gravedad === undefined ? 700 : gravedad,
  });
}

function emitir(state, x, y, cantidad, colores, velocidad, vida, tamano, gravedad) {
  for (let i = 0; i < cantidad; i += 1) {
    const angulo = Math.random() * Math.PI * 2;
    const fuerza = (0.35 + Math.random() * 0.65) * velocidad;
    crearParticula(
      state,
      x,
      y,
      Math.cos(angulo) * fuerza,
      Math.sin(angulo) * fuerza,
      vida * (0.55 + Math.random() * 0.45),
      colores[Math.floor(Math.random() * colores.length)],
      tamano * (0.5 + Math.random() * 0.5),
      gravedad
    );
  }
}

function emitirDash(state, x, y, direccion) {
  for (let i = 0; i < 3; i += 1) {
    crearParticula(
      state,
      x + (Math.random() * 16 - 8),
      y + (Math.random() * 24 - 12),
      -direccion * (80 + Math.random() * 140),
      Math.random() * 90 - 45,
      0.18 + Math.random() * 0.18,
      Math.random() < 0.5 ? state.paleta.dash : 0xbafff5,
      2 + Math.random() * 3,
      0
    );
  }
}

function emitirSalto(state, x, y) {
  emitir(state, x, y, 5, [0xffffff, 0xd2f0ff], 90, 0.3, 3, 300);
}

function emitirAlma(state, x, y) {
  emitir(state, x, y, 10, [0xffd23c, 0xfff5b4, 0xf58c32], 150, 0.5, 4, 250);
}

function emitirPala(state, x, y) {
  emitir(state, x, y, 14, [0xd2414b, 0xf58c32, 0xffd23c], 220, 0.55, 5, 600);
}

function emitirDaño(state, x, y) {
  emitir(state, x, y, 16, [0xd2414b, 0xff7864, 0xffffff], 240, 0.6, 5, 700);
}

function emitirMeta(state, x, y) {
  emitir(state, x, y, 30, [0xffd23c, 0xffffff, 0x46dcd2, 0x9669e6], 260, 1.0, 5, 300);
}

function sonido(state, nombre) {
  if (state.muted) {
    return;
  }
  try {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) {
      return;
    }
    if (!state.audioCtx) {
      state.audioCtx = new Ctx();
    }
    const ctx = state.audioCtx;
    if (ctx.state === "suspended") {
      ctx.resume();
    }
    const tabla = {
      salto: [420, 0.10, "sine", 0.05],
      alma: [880, 0.09, "sine", 0.04],
      dash: [260, 0.14, "square", 0.045],
      pala: [150, 0.16, "square", 0.06],
      golpe: [130, 0.16, "square", 0.08],
      onda: [70, 0.35, "sawtooth", 0.08],
      stomp: [135, 0.18, "triangle", 0.09],
      ui: [520, 0.06, "square", 0.04],
      daño: [210, 0.20, "sawtooth", 0.05],
      meta: [520, 0.30, "sine", 0.05],
    };
    const datos = tabla[nombre] || tabla.alma;
    const oscilador = ctx.createOscillator();
    const ganancia = ctx.createGain();
    oscilador.type = datos[2];
    oscilador.frequency.setValueAtTime(datos[0], ctx.currentTime);
    oscilador.frequency.exponentialRampToValueAtTime(
      Math.max(40, datos[0] * 1.6),
      ctx.currentTime + datos[1]
    );
    ganancia.gain.setValueAtTime(datos[3], ctx.currentTime);
    ganancia.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + datos[1]);
    oscilador.connect(ganancia);
    ganancia.connect(ctx.destination);
    oscilador.start();
    oscilador.stop(ctx.currentTime + datos[1]);
  } catch (error) {
    // Si el navegador bloquea el audio, el juego sigue funcionando.
  }
}

function crearEstado() {
  return {
    initialized: false,
    ready: false,
    error: null,
    data: null,
    paleta: null,
    levelIndex: 0,
    level: null,
    player: null,
    souls: [],
    enemies: [],
    enemiesMelee: [],
    platforms: [],
    palas: [],
    powerups: [],
    bosses: [],
    bossWaves: [],
    checkpoints: [],
    respawnX: 0,
    respawnY: 0,
    hintTextMsg: null,
    particles: [],
    lives: 3,
    totalSouls: 0,
    levelSouls: 0,
    levelTime: 0,
    totalTime: 0,
    camX: 0,
    camY: 0,
    shakeTime: 0,
    shakeDuration: 0.18,
    shakeFuerza: 0,
    shakeX: 0,
    shakeY: 0,
    status: "titulo",
    estiloActual: "monastico",
    hintTimer: 0,
    flash: 0,
    flashColor: 0xffffff,
    keys: {},
    prev: {},
    lastTime: 0,
    muted: false,
    audioCtx: null,
    root: null,
    bg: null,
    bgG: null,
    world: null,
    staticG: null,
    dynG: null,
    hud: null,
    hudG: null,
    txtNivel: null,
    txtNivelSub: null,
    txtAlmas: null,
    txtVidas: null,
    txtTiempo: null,
    txtDash: null,
    txtArma: null,
    txtEstilo: null,
    txtBoss: null,
    hintBg: null,
    hintText: null,
    overlayBg: null,
    overlayTitle: null,
    overlaySub: null,
    overlayInfo: null,
    flashG: null,
    loadingBg: null,
    loadingText: null,
  };
}

function inicializar(state) {
  const root = obtenerRaizPixi();
  if (!root || typeof PIXI === "undefined") {
    console.error("INCRYPTA_GDEVELOP_FAIL: sin contenedor Pixi");
    state.error = "sin Pixi";
    return;
  }
  state.root = root;

  state.bg = new PIXI.Container();
  state.bgG = new PIXI.Graphics();
  state.bg.addChild(state.bgG);
  root.addChild(state.bg);

  state.world = new PIXI.Container();
  state.staticG = new PIXI.Graphics();
  state.dynG = new PIXI.Graphics();
  state.world.addChild(state.staticG);
  state.world.addChild(state.dynG);
  root.addChild(state.world);

  state.hud = new PIXI.Container();
  root.addChild(state.hud);

  state.loadingBg = new PIXI.Graphics();
  state.loadingBg.beginFill(0x0a122d, 1);
  state.loadingBg.drawRect(0, 0, ANCHO, ALTO);
  state.loadingBg.endFill();
  state.hud.addChild(state.loadingBg);

  state.loadingText = crearTexto(
    state.hud,
    "Cargando IN CRYPTA...",
    28,
    0xffd23c,
    ANCHO / 2,
    ALTO / 2 - 14,
    { centrado: true }
  );

  state.hudG = new PIXI.Graphics();
  state.hud.addChild(state.hudG);

  state.txtNivel = crearTexto(state.hud, "", 16, 0xf5f5f5, 480, 14, { centrado: true });
  state.txtNivelSub = crearTexto(state.hud, "", 11, 0xa8987a, 480, 36, { centrado: true });
  state.txtAlmas = crearTexto(state.hud, "", 15, 0xffd23c, 716, 14);
  state.txtVidas = crearTexto(state.hud, "VIDAS", 13, 0xd2414b, 20, 14);
  state.txtTiempo = crearTexto(state.hud, "", 14, 0x96d2f5, 856, 14);
  state.txtDash = crearTexto(state.hud, "DASH LISTO", 12, 0x46dcd2, 20, 34);
  state.txtArma = crearTexto(state.hud, "", 13, 0xffd23c, 716, 42);
  state.txtEstilo = crearTexto(state.hud, "[F2] MONÁSTICO", 11, 0xa8987a, 856, 42);
  state.txtBoss = crearTexto(state.hud, "", 15, 0xd2414b, ANCHO / 2, 14, { centrado: true });

  state.hintBg = new PIXI.Graphics();
  state.hud.addChild(state.hintBg);
  state.hintText = crearTexto(
    state.hud,
    "",
    16,
    0xf5e6be,
    56,
    64,
    { wordWrap: 840 }
  );

  state.overlayBg = new PIXI.Graphics();
  state.overlayBg.beginFill(0x0a0a14, 0.82);
  state.overlayBg.drawRect(0, 0, ANCHO, ALTO);
  state.overlayBg.endFill();
  state.overlayBg.visible = false;
  state.hud.addChild(state.overlayBg);

  state.overlayTitle = crearTexto(
    state.hud,
    "",
    52,
    0xffd23c,
    ANCHO / 2,
    206,
    { centrado: true, family: "Georgia" }
  );
  state.overlayTitle.visible = false;
  state.overlaySub = crearTexto(
    state.hud,
    "",
    22,
    0xf5f5f5,
    ANCHO / 2,
    274,
    { centrado: true }
  );
  state.overlaySub.visible = false;
  state.overlayInfo = crearTexto(
    state.hud,
    "",
    17,
    0xb9c4d0,
    ANCHO / 2,
    318,
    { centrado: true, wordWrap: 760, family: "Georgia" }
  );
  state.overlayInfo.style.align = "center";
  state.overlayInfo.visible = false;

  state.flashG = new PIXI.Graphics();
  state.hud.addChild(state.flashG);

  const jsonManager = runtimeScene.getGame().getJsonManager();
  if (!jsonManager) {
    console.error("INCRYPTA_GDEVELOP_FAIL: no JsonManager");
    state.error = "sin JsonManager";
    state.ready = true;
    return;
  }

  jsonManager.loadJson(INCRYPTA_RECURSO, (error, data) => {
    if (error) {
      console.error("INCRYPTA_GDEVELOP_FAIL: " + error);
      state.error = String(error);
      state.ready = true;
      return;
    }
    if (!data || data.format !== INCRYPTA_FORMATO) {
      console.error("INCRYPTA_GDEVELOP_FAIL: JSON inesperado");
      state.error = "JSON inesperado";
      state.ready = true;
      return;
    }
    state.data = data;
    state.paleta = {
      fondo: colorNum(data.game.palette.fondo),
      fondoBajo: colorNum(data.game.palette.fondo_bajo),
      jugador: colorNum(data.game.palette.jugador),
      jugadorOscuro: colorNum(data.game.palette.jugador_oscuro),
      enemigo: colorNum(data.game.palette.enemigo),
      alma: colorNum(data.game.palette.alma),
      meta: colorNum(data.game.palette.meta),
      piso: colorNum(data.game.palette.piso),
      plataforma: colorNum(data.game.palette.plataforma),
      pasto: colorNum(data.game.palette.pasto),
      dash: colorNum(data.game.palette.dash),
      acento: colorNum(data.game.palette.acento),
    };
    state.loadingBg.visible = false;
    state.loadingText.visible = false;
    state.ready = true;
    cargarNivel(state, 0, false);
    state.status = "titulo";
    state.hintTimer = 0;
    actualizarHud(state);
    state.lastTime = performance.now();
    console.log("INCRYPTA_GDEVELOP_OK levels=" + data.levels.length);
  });
}

function reiniciarJugador(state, nivel) {
  const spawn = nivel.spawn;
  const reglas = state.data.game.rules;
  state.respawnX = spawn.x;
  state.respawnY = spawn.y;
  state.player = {
    x: spawn.x,
    y: spawn.y,
    w: spawn.w,
    h: spawn.h,
    vx: 0,
    vy: 0,
    dir: 1,
    onGround: false,
    onPlatform: null,
    coyote: 0,
    jumpBuffer: 0,
    invuln: 0,
    dashTime: 0,
    dashCooldown: 0,
    dashDir: 1,
    airDash: reglas.dash_usos_aire,
    hasShovel: state.levelIndex >= 1, // En nivel 2 y 3 cuenta con pala
    hasPowerup: false,
    attackTimer: 0,
    attackDuration: 0.12,
    attackHitbox: null,
  };
  state.particles = [];
  state.levelSouls = 0;
  state.levelTime = 0;
  state.hintTimer = 5;
  state.hintTextMsg = null;
  state.flash = 0;
  state.shakeTime = 0;
  state.shakeX = 0;
  state.shakeY = 0;
  state.bossWaves = [];
}

function cargarNivel(state, indice, conservarVidas) {
  state.levelIndex = indice;
  state.level = state.data.levels[indice];
  state.souls = (state.level.souls || []).map((alma) => ({
    x: alma.x,
    y: alma.y,
    w: alma.w,
    h: alma.h,
    collected: false,
  }));
  state.enemies = (state.level.enemies || []).map((enemy) => ({
    x: enemy.x,
    y: enemy.y,
    w: enemy.w,
    h: enemy.h,
    minX: enemy.patrol_min_x,
    maxX: enemy.patrol_max_x,
    dir: enemy.direction || 1,
    speed: enemy.speed,
    alive: true,
  }));
  state.enemiesMelee = (state.level.enemies_melee || []).map((enemy) => ({
    x: enemy.x,
    y: enemy.y,
    w: enemy.w,
    h: enemy.h,
    minX: enemy.patrol_min_x,
    maxX: enemy.patrol_max_x,
    dir: enemy.direction || 1,
    speed: enemy.speed,
    alive: true,
  }));
  state.platforms = (state.level.platforms || []).map((plat) => ({
    id: plat.id,
    x: plat.x,
    y: plat.y,
    w: plat.w,
    h: plat.h,
    origin_x: plat.origin_x,
    origin_y: plat.origin_y,
    axis: plat.axis,
    amplitude: plat.amplitude,
    speed: plat.speed,
    phase: plat.phase,
    time: 0,
    dx: 0,
    dy: 0,
  }));
  state.palas = (state.level.palas || []).map((pala) => ({
    x: pala.x,
    y: pala.y,
    w: pala.w,
    h: pala.h,
    collected: false,
  }));
  state.powerups = (state.level.powerups || []).map((pu) => ({
    x: pu.x,
    y: pu.y,
    w: pu.w,
    h: pu.h,
    collected: false,
  }));
  state.bosses = (state.level.bosses || []).map((boss) => ({
    x: boss.x,
    y: boss.y,
    w: boss.w,
    h: boss.h,
    minX: boss.min_x,
    maxX: boss.max_x,
    hp: boss.hp || 6,
    maxHp: boss.hp || 6,
    fase: boss.fase || 1,
    dir: -1,
    invuln: 0,
    alive: true,
    attackTimer: 2.2,
    charging: false,
    chargeSpeed: 220,
  }));
  state.bossWaves = [];
  state.checkpoints = (state.level.decorations || [])
    .filter((d) => d.type === "s")
    .map((d) => ({
      x: d.x,
      y: d.y,
      w: d.w,
      h: d.h,
      active: false,
    }));
  if (!conservarVidas) {
    state.lives = state.data.game.rules.vidas_iniciales;
  }
  reiniciarJugador(state, state.level);
  state.status = "jugando";
  dibujarNivelEstatico(state);
  actualizarCamara(state, 0, true);
  actualizarHud(state);
}

function dibujarNivelEstatico(state) {
  const g = state.staticG;
  const p = state.paleta;
  const nivel = state.level;
  const tema = nivel.theme || "camposanto";
  const tile = state.data.game.tile;
  const temaColores = {
    camposanto: { piso: p.piso, borde: p.pasto, plataforma: p.plataforma, piedra: 0x7a8090 },
    cripta: { piso: 0x2a2238, borde: 0x65527c, plataforma: 0x3d304c, piedra: 0x8d7aa3 },
    osario: { piso: 0x3b2a1b, borde: 0x9a7548, plataforma: 0x4b3724, piedra: 0xb79a6e },
  }[tema];
  g.clear();

  for (const solido of nivel.solids) {
    const esPiso = solido.y >= nivel.size.height - 2 * tile;
    g.beginFill(esPiso ? temaColores.piso : temaColores.plataforma, 1);
    g.drawRect(solido.x, solido.y, solido.w, solido.h);
    g.endFill();

    g.beginFill(esPiso ? temaColores.borde : temaColores.piedra, 1);
    g.drawRect(solido.x, solido.y, solido.w, esPiso ? 6 : 4);
    g.endFill();

    if (esPiso) {
      g.beginFill(0x1b1412, 0.55);
      for (let x = solido.x + 18; x < solido.x + solido.w; x += 64) {
        g.drawRect(x, solido.y + 14, 28, 2);
      }
      g.endFill();
    }
  }

  for (const decoracion of nivel.decorations || []) {
    const x = decoracion.x;
    const y = decoracion.y;
    const w = decoracion.w;
    const h = decoracion.h;
    if (decoracion.type === "t") {
      g.beginFill(0x111018, 1);
      g.drawEllipse(x + w / 2, y + h - 3, w + 4, 8);
      g.endFill();
      g.beginFill(0x5d6372, 1);
      g.drawRoundedRect(x + 4, y + 7, w - 8, h - 9, 5);
      g.endFill();
      g.beginFill(0x3f4552, 1);
      g.drawRect(x + 7, y + 9, 3, h - 12);
      g.endFill();
      g.lineStyle(2, 0xb9c4d0, 0.65);
      g.moveTo(x + w / 2, y + 12);
      g.lineTo(x + w / 2, y + h - 10);
      g.moveTo(x + w / 2 - 5, y + 18);
      g.lineTo(x + w / 2 + 5, y + 18);
      g.lineStyle(0, 0, 0);
    } else if (decoracion.type === "c") {
      g.beginFill(0xffd27a, 0.09);
      g.drawCircle(x + w / 2, y + 8, w);
      g.endFill();
      g.beginFill(0xe8d8ad, 1);
      g.drawRect(x + w / 2 - 3, y + 13, 6, h - 14);
      g.endFill();
      g.beginFill(0xffd23c, 1);
      g.drawEllipse(x + w / 2, y + 9, 4, 7);
      g.endFill();
      g.beginFill(0xfff5b4, 1);
      g.drawEllipse(x + w / 2, y + 10, 2, 4);
      g.endFill();
    } else if (decoracion.type === "r") {
      g.lineStyle(3, 0x2f211b, 1);
      g.moveTo(x + w / 2, y);
      g.lineTo(x + w / 2 - 8, y + h * 0.35);
      g.lineTo(x + w / 2 + 4, y + h * 0.65);
      g.lineTo(x + w / 2 - 5, y + h);
      g.moveTo(x + w / 2 - 3, y + h * 0.4);
      g.lineTo(x + w, y + h * 0.7);
      g.lineStyle(0, 0, 0);
    } else if (decoracion.type === "b") {
      g.lineStyle(2, 0xd8c29a, 0.9);
      g.moveTo(x + 5, y + h - 5);
      g.lineTo(x + w - 5, y + 5);
      g.moveTo(x + w - 5, y + h - 5);
      g.lineTo(x + 5, y + 5);
      g.lineStyle(0, 0, 0);
      g.beginFill(0xe8d8ad, 1);
      g.drawCircle(x + 4, y + h - 5, 2);
      g.drawCircle(x + w - 4, y + h - 5, 2);
      g.endFill();
    } else if (decoracion.type === "s") {
      g.beginFill(0x282532, 1);
      g.drawRect(x + 1, y + h - 7, w - 2, 7);
      g.endFill();
      g.beginFill(0x6d7381, 1);
      g.drawRoundedRect(x + w / 2 - 7, y + 8, 14, h - 15, 5);
      g.endFill();
      g.beginFill(0x9aa1ad, 1);
      g.drawCircle(x + w / 2, y + 7, 5);
      g.endFill();
      g.beginFill(0x3a3544, 1);
      g.drawCircle(x + w / 2, y + 7, 3);
      g.endFill();
    }
  }

  for (const peligro of nivel.hazards || []) {
    const cantidad = Math.max(2, Math.floor(peligro.w / 12));
    const paso = peligro.w / cantidad;
    g.beginFill(0x17141d, 1);
    g.drawRect(peligro.x, peligro.y + peligro.h - 3, peligro.w, 3);
    g.endFill();
    g.beginFill(0x9ba4b5, 1);
    for (let i = 0; i < cantidad; i += 1) {
      const x = peligro.x + i * paso;
      g.moveTo(x, peligro.y + peligro.h);
      g.lineTo(x + paso / 2, peligro.y);
      g.lineTo(x + paso, peligro.y + peligro.h);
      g.closePath();
    }
    g.endFill();
    g.beginFill(0xd2414b, 0.65);
    for (let i = 0; i < cantidad; i += 1) {
      const x = peligro.x + i * paso + paso / 2;
      g.drawCircle(x, peligro.y + 3, 1.5);
    }
    g.endFill();
  }

  const meta = nivel.goal;
  g.beginFill(0x111018, 1);
  g.drawRoundedRect(meta.x - 6, meta.y - 8, meta.w + 12, meta.h + 10, 8);
  g.endFill();
  g.beginFill(0x292337, 1);
  g.drawRoundedRect(meta.x - 2, meta.y - 4, meta.w + 4, meta.h + 4, 6);
  g.endFill();
  g.beginFill(0x0a0910, 1);
  g.drawRoundedRect(meta.x + 5, meta.y + 4, meta.w - 10, meta.h - 6, 16);
  g.endFill();
  g.beginFill(p.meta, 0.13);
  g.drawCircle(meta.x + meta.w / 2, meta.y + meta.h / 2, meta.w * 0.42);
  g.endFill();
  g.lineStyle(2, p.meta, 0.8);
  for (let i = 1; i <= 3; i += 1) {
    const x = meta.x + (meta.w / 4) * i;
    g.moveTo(x, meta.y + 8);
    g.lineTo(x, meta.y + meta.h - 4);
  }
  g.lineStyle(0, 0, 0);
  g.beginFill(p.meta, 1);
  g.drawCircle(meta.x + meta.w / 2, meta.y + meta.h / 2, 3);
  g.endFill();
}

function colorMezcla(a, b, t) {
  const ar = (a >> 16) & 255;
  const ag = (a >> 8) & 255;
  const ab = a & 255;
  const br = (b >> 16) & 255;
  const bg = (b >> 8) & 255;
  const bb = b & 255;
  return (
    (Math.round(ar + (br - ar) * t) << 16) |
    (Math.round(ag + (bg - ag) * t) << 8) |
    Math.round(ab + (bb - ab) * t)
  );
}

function dibujarFondo(state) {
  const g = state.bgG;
  const tema = state.level ? state.level.theme : "camposanto";
  const paletas = {
    camposanto: { arriba: 0x050712, abajo: 0x162b34, acento: 0x9fc3d9, bruma: 0x2c5960 },
    cripta: { arriba: 0x08050f, abajo: 0x21112b, acento: 0xa878e8, bruma: 0x321b40 },
    osario: { arriba: 0x0b0706, abajo: 0x2e1c12, acento: 0xd8c29a, bruma: 0x432a1a },
  };
  const c = paletas[tema] || paletas.camposanto;
  const bandas = 12;
  g.clear();

  for (let i = 0; i < bandas; i += 1) {
    const t = i / (bandas - 1);
    g.beginFill(colorMezcla(c.arriba, c.abajo, t), 1);
    g.drawRect(0, Math.floor((ALTO / bandas) * i), ANCHO, Math.ceil(ALTO / bandas) + 1);
    g.endFill();
  }

  const desplazamiento = (state.camX * 0.22) % 280;
  if (tema === "camposanto") {
    g.beginFill(0xffeca0, 0.95);
    g.drawCircle(800, 92, 54);
    g.endFill();
    g.beginFill(0xfffad7, 1);
    g.drawCircle(800, 92, 42);
    g.endFill();
    g.beginFill(0xfffff0, 1);
    g.drawCircle(800, 92, 30);
    g.endFill();
    g.beginFill(0xffffff, 0.08);
    g.drawCircle(800, 92, 72);
    g.endFill();

    const estrellas = [
      [70, 55, 2], [140, 120, 1], [230, 45, 2], [310, 150, 1],
      [390, 70, 1], [470, 30, 2], [560, 130, 1], [640, 58, 2],
      [720, 170, 1], [880, 40, 2], [930, 140, 1], [180, 210, 1],
      [520, 200, 1], [840, 220, 1],
    ];
    g.beginFill(0xdcefff, 0.9);
    for (const estrella of estrellas) {
      g.drawCircle(estrella[0], estrella[1], estrella[2]);
    }
    g.endFill();

    for (let i = -2; i < 6; i += 1) {
      const x = i * 280 - desplazamiento;
      g.beginFill(0x0d2026, 1);
      g.moveTo(x, ALTO);
      g.lineTo(x + 150, 250);
      g.lineTo(x + 300, ALTO);
      g.closePath();
      g.endFill();
      g.beginFill(0x173840, 1);
      g.moveTo(x + 90, ALTO);
      g.lineTo(x + 190, 300);
      g.lineTo(x + 290, ALTO);
      g.closePath();
      g.endFill();
    }

    g.beginFill(0x071016, 1);
    for (let i = -1; i < 7; i += 1) {
      const x = i * 190 - desplazamiento * 1.4;
      g.drawRect(x + 30, 390, 7, 80);
      g.drawRect(x + 18, 410, 31, 6);
      g.drawRect(x + 24, 395, 4, 26);
      g.drawRect(x + 40, 395, 4, 26);
    }
    g.endFill();
  } else if (tema === "cripta") {
    const desplazamientoCripta = (state.camX * 0.13) % 240;
    for (let i = -1; i < 6; i += 1) {
      const x = i * 240 - desplazamientoCripta;
      g.beginFill(0x171021, 1);
      g.drawRect(x, 0, 90, ALTO);
      g.endFill();
      g.beginFill(0x2b1d3a, 1);
      g.drawRect(x + 74, 0, 16, ALTO);
      g.drawRect(x, 0, 16, ALTO);
      g.endFill();
      g.beginFill(0x0e0916, 1);
      g.drawCircle(x + 45, 160, 58);
      g.endFill();
      g.beginFill(0x3f2a55, 0.7);
      g.drawCircle(x + 45, 160, 46);
      g.endFill();
      g.beginFill(0xa878e8, 0.08);
      g.drawCircle(x + 45, 160, 80);
      g.endFill();
    }
    g.beginFill(0xa878e8, 0.06);
    g.drawEllipse(ANCHO / 2, ALTO - 40, 760, 170);
    g.endFill();
  } else {
    const desplazamientoOsario = (state.camX * 0.17) % 320;
    for (let i = -1; i < 5; i += 1) {
      const x = i * 320 - desplazamientoOsario;
      g.beginFill(0x1b100a, 1);
      g.drawRect(x, 0, 250, ALTO);
      g.endFill();
      g.beginFill(0x3a2418, 1);
      g.drawRect(x + 220, 0, 30, ALTO);
      g.endFill();
      g.lineStyle(3, 0xd8c29a, 0.3);
      for (let j = 0; j < 5; j += 1) {
        g.moveTo(x + 16, 70 + j * 64);
        g.quadraticCurveTo(x + 75, 35 + j * 64, x + 134, 70 + j * 64);
      }
      g.lineStyle(0, 0, 0);
      for (let j = 0; j < 4; j += 1) {
        g.beginFill(0xcdb489, 0.65);
        g.drawCircle(x + 30 + j * 44, 255, 9);
        g.drawCircle(x + 30 + j * 44, 258, 5);
        g.endFill();
      }
    }
    g.beginFill(0xd88a3c, 0.05);
    g.drawEllipse(ANCHO / 2, ALTO - 30, 820, 160);
    g.endFill();
  }

  g.beginFill(c.bruma, 0.1);
  for (let i = 0; i < 3; i += 1) {
    const ancho = 760 + i * 110;
    g.drawEllipse(ANCHO / 2, ALTO - 65 + i * 22, ancho, 90);
  }
  g.endFill();
}

function actualizarParticulas(state, dt) {
  for (const particula of state.particles) {
    particula.vida -= dt;
    particula.vy += particula.gravedad * dt;
    particula.x += particula.vx * dt;
    particula.y += particula.vy * dt;
  }
  state.particles = state.particles.filter((particula) => particula.vida > 0);
}

function intentarDash(state) {
  const p = state.player;
  const reglas = state.data.game.rules;
  if (p.dashTime > 0 || p.dashCooldown > 0) {
    return;
  }
  if (!p.onGround && p.airDash <= 0) {
    return;
  }
  p.dashTime = reglas.dash_duracion;
  p.dashCooldown = reglas.dash_cooldown;
  p.dashDir = p.dir;
  if (!p.onGround) {
    p.airDash -= 1;
  }
  p.vx = p.dir * reglas.dash_velocidad;
  p.vy = 0;
  emitirDash(state, p.x + p.w / 2, p.y + p.h / 2, p.dashDir);
  sacudir(state, 3.5, 0.1);
  sonido(state, "dash");
}

function obtenerSolidos(state) {
  const solidos = (state.level.solids || []).slice();
  if (state.platforms) {
    for (let i = 0; i < state.platforms.length; i += 1) {
      solidos.push(state.platforms[i]);
    }
  }
  return solidos;
}

function moverX(state, dx, solidos) {
  const p = state.player;
  p.x += dx;

  let colision = false;
  for (let i = 0; i < solidos.length; i += 1) {
    if (solapan(p, solidos[i])) {
      colision = true;
      break;
    }
  }

  // Tolerancia de esquinas en dash (corner nudge estilo Celeste):
  // Si durante un dash rozamos una esquina por hasta 6 px, deslizar suavemente hacia el hueco
  if (colision && p.dashTime > 0) {
    const tolerancia = 6;
    for (let dy = 1; dy <= tolerancia; dy += 1) {
      const probe = { x: p.x, y: p.y + dy, w: p.w, h: p.h };
      let choca = false;
      for (let i = 0; i < solidos.length; i += 1) {
        if (solapan(probe, solidos[i])) {
          choca = true;
          break;
        }
      }
      if (!choca) {
        p.y += dy;
        colision = false;
        break;
      }
    }
    if (colision) {
      for (let dy = 1; dy <= tolerancia; dy += 1) {
        const probe = { x: p.x, y: p.y - dy, w: p.w, h: p.h };
        let choca = false;
        for (let i = 0; i < solidos.length; i += 1) {
          if (solapan(probe, solidos[i])) {
            choca = true;
            break;
          }
        }
        if (!choca) {
          p.y -= dy;
          colision = false;
          break;
        }
      }
    }
  }

  if (colision) {
    for (let i = 0; i < solidos.length; i += 1) {
      const s = solidos[i];
      if (!solapan(p, s)) {
        continue;
      }
      if (dx > 0) {
        p.x = s.x - p.w;
      } else if (dx < 0) {
        p.x = s.x + s.w;
      }
      p.vx = 0;
      break;
    }
  }
}

function moverY(state, dy, solidos) {
  const p = state.player;
  p.y += dy;

  for (let i = 0; i < solidos.length; i += 1) {
    const s = solidos[i];
    if (!solapan(p, s)) {
      continue;
    }
    if (dy > 0) {
      p.y = s.y - p.h;
      p.onGround = true;
    } else if (dy < 0) {
      p.y = s.y + s.h;
    }
    p.vy = 0;
    break;
  }

  if (dy >= 0 && !p.onGround) {
    const sonda = { x: p.x, y: p.y + 1, w: p.w, h: p.h };
    for (let i = 0; i < solidos.length; i += 1) {
      if (solapan(sonda, solidos[i])) {
        p.onGround = true;
        p.vy = 0;
        break;
      }
    }
  }
}

function actualizarJugador(state, dt) {
  const p = state.player;
  const reglas = state.data.game.rules;
  const solidos = obtenerSolidos(state);

  p.invuln = Math.max(0, p.invuln - dt);
  p.dashCooldown = Math.max(0, p.dashCooldown - dt);
  p.attackCooldown = Math.max(0, (p.attackCooldown || 0) - dt);

  if (p.attackTimer > 0) {
    p.attackTimer = Math.max(0, p.attackTimer - dt);
    if (p.attackTimer <= 0) {
      p.attackHitbox = null;
    }
  }

  if (p.dashTime > 0) {
    p.dashTime = Math.max(0, p.dashTime - dt);
    p.vx = p.dashDir * reglas.dash_velocidad;
    p.vy = 0;
    moverX(state, p.vx * dt, solidos);
    const choco = p.vx === 0;
    if (choco) {
      p.dashTime = 0;
    }
    if (p.onGround) {
      p.airDash = reglas.dash_usos_aire;
    }
    if (p.dashTime <= 0) {
      p.vx = choco ? 0 : p.dashDir * reglas.velocidad * 0.55;
    }
    emitirDash(state, p.x + p.w / 2, p.y + p.h / 2, p.dashDir);
    return;
  }

  if (state.keys.izquierda && !state.keys.derecha) {
    p.vx = -reglas.velocidad;
    p.dir = -1;
  } else if (state.keys.derecha && !state.keys.izquierda) {
    p.vx = reglas.velocidad;
    p.dir = 1;
  } else {
    p.vx = 0;
  }

  p.jumpBuffer = Math.max(0, p.jumpBuffer - dt);
  if (p.onGround) {
    p.coyote = reglas.coyote_time;
  } else {
    p.coyote = Math.max(0, p.coyote - dt);
  }

  if (p.jumpBuffer > 0 && (p.onGround || p.coyote > 0)) {
    p.vy = reglas.salto;
    p.onGround = false;
    p.onPlatform = null;
    p.coyote = 0;
    p.jumpBuffer = 0;
    emitirSalto(state, p.x + p.w / 2, p.y + p.h);
    sonido(state, "salto");
    if (!state.keys.salto) {
      p.vy *= (reglas.corte_salto || 0.45);
    }
  }

  p.vy = Math.min(reglas.max_caida, p.vy + reglas.gravedad * dt);
  moverX(state, p.vx * dt, solidos);
  p.onGround = false;
  moverY(state, p.vy * dt, solidos);

  if (p.onGround) {
    p.coyote = reglas.coyote_time;
    p.airDash = reglas.dash_usos_aire;
  }
}

function sacudir(state, fuerza, duracion) {
  state.shakeTime = Math.max(state.shakeTime, duracion);
  state.shakeDuration = duracion;
  state.shakeFuerza = Math.max(state.shakeFuerza, fuerza);
}

function actualizarCamara(state, dt, instantanea) {
  const p = state.player;
  const nivel = state.level;
  const maxX = Math.max(0, nivel.size.width - ANCHO);
  const maxY = Math.max(0, nivel.size.height - ALTO);
  let objetivoX = limitar(p.x + p.w / 2 - ANCHO / 2, 0, maxX);
  let objetivoY = limitar(p.y + p.h / 2 - ALTO / 2, 0, maxY);

  if (nivel.size.width < ANCHO) {
    objetivoX = (nivel.size.width - ANCHO) / 2;
  }
  if (nivel.size.height <= ALTO) {
    objetivoY = nivel.size.height - ALTO;
  }

  if (instantanea) {
    state.camX = objetivoX;
    state.camY = objetivoY;
  } else {
    const factor = Math.min(1, 7 * dt);
    state.camX += (objetivoX - state.camX) * factor;
    state.camY += (objetivoY - state.camY) * factor;
  }

  if (nivel.size.height <= ALTO) {
    state.camY = nivel.size.height - ALTO;
  }

  if (state.shakeTime > 0) {
    state.shakeTime = Math.max(0, state.shakeTime - dt);
    const intensidad = state.shakeFuerza * (state.shakeTime / state.shakeDuration);
    state.shakeX = (Math.random() * 2 - 1) * intensidad;
    state.shakeY = (Math.random() * 2 - 1) * intensidad;
  } else {
    state.shakeX = 0;
    state.shakeY = 0;
    state.shakeFuerza = 0;
  }

  const capa = runtimeScene.getLayer("");
  capa.setCameraX(state.camX + ANCHO / 2 + state.shakeX);
  capa.setCameraY(state.camY + ALTO / 2 + state.shakeY);

  state.bg.x = state.camX;
  state.bg.y = state.camY;
  state.hud.x = state.camX;
  state.hud.y = state.camY;
}

function respawn(state) {
  const p = state.player;
  p.x = state.respawnX !== undefined ? state.respawnX : state.level.spawn.x;
  p.y = state.respawnY !== undefined ? state.respawnY : state.level.spawn.y;
  p.vx = 0;
  p.vy = 0;
  p.onGround = false;
  p.onPlatform = null;
  p.coyote = 0;
  p.jumpBuffer = 0;
  p.invuln = state.data.game.rules.invulnerabilidad;
  p.dashTime = 0;
  p.dashCooldown = 0;
  p.airDash = state.data.game.rules.dash_usos_aire;
  p.attackTimer = 0;
  p.attackHitbox = null;
  actualizarCamara(state, 0, true);
}

function dañar(state, ignorarInvulnerabilidad) {
  const p = state.player;
  if (p.invuln > 0 && !ignorarInvulnerabilidad) {
    return;
  }
  state.lives -= 1;
  emitirDaño(state, p.x + p.w / 2, p.y + p.h / 2);
  sonido(state, "daño");
  sacudir(state, 9, 0.22);
  state.flash = 0.16;
  state.flashColor = 0xd2414b;

  if (state.lives <= 0) {
    state.status = "derrota";
    return;
  }
  respawn(state);
}

function actualizarEnemigos(state, dt) {
  const p = state.player;
  const reglas = state.data.game.rules;

  for (const enemigo of state.enemies) {
    if (!enemigo.alive) {
      continue;
    }
    enemigo.x += enemigo.dir * enemigo.speed * dt;
    if (enemigo.x <= enemigo.minX) {
      enemigo.x = enemigo.minX;
      enemigo.dir = 1;
    } else if (enemigo.x + enemigo.w >= enemigo.maxX) {
      enemigo.x = enemigo.maxX - enemigo.w;
      enemigo.dir = -1;
    }

    if (!solapan(p, enemigo)) {
      continue;
    }

    const vieneDeArriba = p.vy > 0 && p.y + p.h - enemigo.y <= 24;
    if (vieneDeArriba) {
      enemigo.alive = false;
      p.vy = -reglas.rebote_enemigo;
      p.onGround = false;
      p.onPlatform = null;
      p.airDash = reglas.dash_usos_aire;
      p.dashCooldown = 0;
      emitirPala(state, enemigo.x + enemigo.w / 2, enemigo.y + enemigo.h / 2);
      sonido(state, "stomp");
      sacudir(state, 6, 0.14);
    } else {
      dañar(state, false);
      return;
    }
  }
}

function actualizarEnemigosMelee(state, dt) {
  const p = state.player;
  const reglas = state.data.game.rules;

  for (const em of (state.enemiesMelee || [])) {
    if (!em.alive) {
      continue;
    }
    em.x += em.dir * em.speed * dt;
    if (em.x <= em.minX) {
      em.x = em.minX;
      em.dir = 1;
    } else if (em.x + em.w >= em.maxX) {
      em.x = em.maxX - em.w;
      em.dir = -1;
    }

    if (!solapan(p, em)) {
      continue;
    }

    const vieneDeArriba = p.vy > 0 && p.y + p.h - em.y <= 24;
    if (vieneDeArriba) {
      em.alive = false;
      p.vy = -reglas.rebote_enemigo;
      p.onGround = false;
      p.onPlatform = null;
      p.airDash = reglas.dash_usos_aire;
      p.dashCooldown = 0;
      emitirPala(state, em.x + em.w / 2, em.y + em.h / 2);
      sonido(state, "stomp");
      sacudir(state, 6, 0.14);
    } else {
      dañar(state, false);
      return;
    }
  }
}

function intentarAtaque(state) {
  const p = state.player;
  if (!p.hasShovel || p.attackTimer > 0) {
    return;
  }
  p.attackTimer = 0.20;
  const esGuadaña = p.hasPowerup;
  const alcance = esGuadaña ? 76 : 36;
  const alto = esGuadaña ? 42 : 26;
  const hx = p.dir > 0 ? p.x + p.w - 4 : p.x - alcance + 4;
  const hy = p.y + p.h / 2 - alto / 2;
  p.attackHitbox = { x: hx, y: hy, w: alcance, h: alto };
  sonido(state, "pala");
}

function actualizarPlataformas(state, dt) {
  const p = state.player;
  let soporte = null;
  if (p && p.onGround) {
    for (const plat of (state.platforms || [])) {
      if (
        Math.abs((p.y + p.h) - plat.y) <= 2 &&
        p.x + p.w > plat.x &&
        p.x < plat.x + plat.w
      ) {
        soporte = plat;
        break;
      }
    }
  }

  for (const plat of (state.platforms || [])) {
    const prevX = plat.x;
    const prevY = plat.y;
    plat.time = (plat.time || 0) + dt;
    const desp = Math.sin(plat.time * plat.speed + plat.phase) * plat.amplitude;
    if (plat.axis === "h" || plat.axis === "H") {
      plat.x = Math.round(plat.origin_x + desp);
    } else {
      plat.y = Math.round(plat.origin_y + desp);
    }
    plat.dx = plat.x - prevX;
    plat.dy = plat.y - prevY;
  }

  if (p && soporte) {
    p.x += soporte.dx;
    p.y += soporte.dy;
  }
}

function actualizarObjetos(state) {
  const p = state.player;

  for (const pala of (state.palas || [])) {
    if (pala.collected || !solapan(p, pala)) {
      continue;
    }
    pala.collected = true;
    p.hasShovel = true;
    state.hintTimer = 4.0;
    state.hintTextMsg = "¡PALA OBTENIDA! [Z/J/A] para atacar · Pisotón habilitado";
    emitirPala(state, pala.x + pala.w / 2, pala.y + pala.h / 2);
    sonido(state, "pala");
  }

  for (const pu of (state.powerups || [])) {
    if (pu.collected || !solapan(p, pu)) {
      continue;
    }
    pu.collected = true;
    p.hasPowerup = true;
    p.hasShovel = true;
    state.hintTimer = 4.5;
    state.hintTextMsg = "¡GUADAÑA MÍSTICA OBTENIDA! Alcance extendido de 72px";
    emitirAlma(state, pu.x + pu.w / 2, pu.y + pu.h / 2);
    sonido(state, "alma");
    sacudir(state, 6, 0.16);
  }

  for (const cp of (state.checkpoints || [])) {
    if (!cp.active && solapan(p, cp)) {
      cp.active = true;
      state.respawnX = cp.x;
      state.respawnY = cp.y - p.h + cp.h;
      state.hintTimer = 3.5;
      state.hintTextMsg = "PUNTO DE CONTROL ACTIVADO";
      sonido(state, "ui");
      emitirAlma(state, cp.x + cp.w / 2, cp.y + cp.h / 2);
    }
  }

  for (const boss of (state.bosses || [])) {
    if (boss.alive) {
      const limite = boss.minX - 3 * 32;
      if (p.x > limite && state.respawnX < limite) {
        state.respawnX = limite;
        state.respawnY = state.level.spawn.y;
        state.hintTimer = 3.5;
        state.hintTextMsg = "PUNTO DE CONTROL · LA ANTESALA DEL CUSTODIO";
        sonido(state, "ui");
      }
    }
  }
}

function actualizarCombate(state) {
  const p = state.player;
  const reglas = state.data.game.rules;
  if (!p.attackHitbox) {
    return;
  }

  for (const enemigo of (state.enemies || [])) {
    if (enemigo.alive && solapan(p.attackHitbox, enemigo)) {
      enemigo.alive = false;
      p.airDash = reglas.dash_usos_aire;
      p.dashCooldown = 0;
      emitirPala(state, enemigo.x + enemigo.w / 2, enemigo.y + enemigo.h / 2);
      sonido(state, "pala");
      sacudir(state, 5, 0.12);
      state.flash = 0.06;
      state.flashColor = 0xffd23c;
    }
  }

  for (const em of (state.enemiesMelee || [])) {
    if (em.alive && solapan(p.attackHitbox, em)) {
      em.alive = false;
      p.airDash = reglas.dash_usos_aire;
      p.dashCooldown = 0;
      emitirPala(state, em.x + em.w / 2, em.y + em.h / 2);
      sonido(state, "pala");
      sacudir(state, 5, 0.12);
      state.flash = 0.06;
      state.flashColor = 0xffd23c;
    }
  }

  for (const boss of (state.bosses || [])) {
    if (!boss.alive || !solapan(p.attackHitbox, boss)) {
      continue;
    }
    if (boss.invuln > 0) {
      continue;
    }

    if (boss.fase === 1) {
      boss.hp -= 1;
      boss.invuln = 0.55;
      p.airDash = reglas.dash_usos_aire;
      p.dashCooldown = 0;
      emitirPala(state, boss.x + boss.w / 2, boss.y + boss.h / 2);
      sonido(state, "golpe");
      sacudir(state, 6, 0.14);
      state.flash = 0.08;
      state.flashColor = 0xffd23c;

      if (boss.hp <= 3) {
        boss.fase = 2;
        state.hintTimer = 4.5;
        state.hintTextMsg = "¡FASE II! LA PALA REBOTA — SOLO EL PISOTÓN LO DAÑA";
        sacudir(state, 11, 0.26);
        sonido(state, "onda");
      }
    } else {
      boss.invuln = 0.3;
      p.vx = -p.dir * 220;
      p.vy = -160;
      p.invuln = 0.25;
      sacudir(state, 5, 0.12);
      state.flash = 0.08;
      state.flashColor = 0xd2414b;
      sonido(state, "pala");
      state.hintTimer = 3.0;
      state.hintTextMsg = "¡LA PALA REBOTA! Salta desde arriba (PISOTÓN)";
    }
  }
}

function crearOndasJefe(state, boss) {
  const vel = boss.fase >= 2 ? 220 : 160;
  state.bossWaves.push({
    x: boss.x - 10,
    y: boss.y + boss.h - 22,
    w: 20,
    h: 22,
    dir: -1,
    speed: vel,
    life: 3.2,
  });
  state.bossWaves.push({
    x: boss.x + boss.w - 10,
    y: boss.y + boss.h - 22,
    w: 20,
    h: 22,
    dir: 1,
    speed: vel,
    life: 3.2,
  });
  if (boss.fase >= 2) {
    state.bossWaves.push({
      x: boss.x - 24,
      y: boss.y + boss.h - 22,
      w: 20,
      h: 22,
      dir: -1,
      speed: vel * 1.35,
      life: 3.2,
    });
    state.bossWaves.push({
      x: boss.x + boss.w + 4,
      y: boss.y + boss.h - 22,
      w: 20,
      h: 22,
      dir: 1,
      speed: vel * 1.35,
      life: 3.2,
    });
  }
  sonido(state, "onda");
  sacudir(state, 7, 0.18);
}

function actualizarOndasJefe(state, dt) {
  const p = state.player;
  for (const onda of (state.bossWaves || [])) {
    onda.x += onda.dir * onda.speed * dt;
    onda.life -= dt;
    if (onda.life > 0 && p.invuln <= 0 && solapan(p, onda)) {
      dañar(state, false);
      return;
    }
  }
  state.bossWaves = (state.bossWaves || []).filter((o) => o.life > 0);
}

function actualizarJefe(state, dt) {
  const p = state.player;
  const reglas = state.data.game.rules;

  for (const boss of (state.bosses || [])) {
    if (!boss.alive) {
      continue;
    }
    if (state.respawnX === state.level.spawn.x) {
      const limite = boss.minX - 3 * 32;
      if (p.x + p.w > limite) {
        state.respawnX = limite;
        state.respawnY = state.level.spawn.y;
        state.hintTimer = 4.0;
        state.hintTextMsg = "PUNTO DE CONTROL · LA ANTESALA DEL CUSTODIO";
        sonido(state, "ui");
      }
    }
    boss.invuln = Math.max(0, boss.invuln - dt);
    boss.attackTimer -= dt;

    if (boss.charging) {
      boss.x += boss.dir * boss.chargeSpeed * dt;
      let choco = false;
      if (boss.x <= boss.minX) {
        boss.x = boss.minX;
        choco = true;
      } else if (boss.x + boss.w >= boss.maxX) {
        boss.x = boss.maxX - boss.w;
        choco = true;
      }
      if (choco || boss.attackTimer <= 0) {
        boss.charging = false;
        boss.attackTimer = 1.6;
        crearOndasJefe(state, boss);
      }
    } else {
      if (Math.abs((p.x + p.w / 2) - (boss.x + boss.w / 2)) > 50) {
        boss.dir = p.x > boss.x ? 1 : -1;
        boss.x += boss.dir * 45 * dt;
        boss.x = limitar(boss.x, boss.minX, boss.maxX - boss.w);
      }

      if (boss.attackTimer <= 0) {
        if (boss.fase >= 2 && Math.random() < 0.45) {
          boss.charging = true;
          boss.dir = p.x > boss.x ? 1 : -1;
          boss.attackTimer = 1.2;
          sonido(state, "onda");
          sacudir(state, 5, 0.16);
        } else {
          crearOndasJefe(state, boss);
          boss.attackTimer = boss.fase >= 2 ? 1.8 : 2.4;
        }
      }
    }

    if (!solapan(p, boss)) {
      continue;
    }

    const vieneDeArriba = p.vy > 0 && p.y + p.h - boss.y <= 24;
    if (vieneDeArriba && boss.invuln <= 0) {
      boss.hp -= 1;
      boss.invuln = 0.65;
      p.vy = -reglas.rebote_enemigo;
      p.onGround = false;
      p.onPlatform = null;
      p.invuln = 0.4;
      p.airDash = reglas.dash_usos_aire;
      p.dashCooldown = 0;
      emitirPala(state, boss.x + boss.w / 2, boss.y + 16);
      sonido(state, "stomp");
      sacudir(state, 8, 0.2);
      state.flash = 0.1;
      state.flashColor = 0xffd23c;

      if (boss.hp <= 3 && boss.fase === 1) {
        boss.fase = 2;
        state.hintTimer = 4.5;
        state.hintTextMsg = "¡FASE II! LA PALA REBOTA — SOLO EL PISOTÓN LO DAÑA";
        sacudir(state, 11, 0.26);
        sonido(state, "onda");
      }

      if (boss.hp <= 0) {
        boss.alive = false;
        emitirMeta(state, boss.x + boss.w / 2, boss.y + boss.h / 2);
        sonido(state, "meta");
        sacudir(state, 9, 0.25);
        state.flash = 0.2;
        state.flashColor = 0xe8c15a;
        state.hintTimer = 4.0;
        state.hintTextMsg = "¡EL CUSTODIO CAYÓ! El portón de salida se abre...";
      }
    } else if (p.invuln <= 0 && boss.alive) {
      dañar(state, false);
      return;
    }
  }
}

function actualizarAlmas(state) {
  const p = state.player;
  for (const alma of state.souls) {
    if (alma.collected || !solapan(p, alma)) {
      continue;
    }
    alma.collected = true;
    state.levelSouls += 1;
    emitirAlma(state, alma.x + alma.w / 2, alma.y + alma.h / 2);
    sonido(state, "alma");
  }
}

function siguienteNivel(state) {
  state.totalSouls += state.levelSouls;
  if (state.levelIndex + 1 >= state.data.levels.length) {
    state.status = "victoria";
    return;
  }
  cargarNivel(state, state.levelIndex + 1, true);
}

function reiniciarJuego(state) {
  state.totalSouls = 0;
  state.totalTime = 0;
  cargarNivel(state, 0, false);
}

function manejarEntrada(state) {
  if (justo(state, "f2")) {
    const lista = ["monastico", "hierro", "espectral", "osario"];
    const idx = lista.indexOf(state.estiloActual);
    state.estiloActual = lista[(idx + 1) % lista.length];
    const est = ESTILOS_GOTICOS_WEB[state.estiloActual];
    state.hintTimer = 4.0;
    state.hintTextMsg = "ESTILO GÓTICO: " + est.nombre.toUpperCase() + "  ·  [F2] para cambiar";
    sonido(state, "ui");
    actualizarHud(state);
  }
  if (justo(state, "pausa")) {
    if (state.status === "jugando") {
      state.status = "pausa";
    } else if (state.status === "pausa") {
      state.status = "jugando";
    }
  }
  if (justo(state, "reiniciar")) {
    reiniciarJuego(state);
  }
  if (justo(state, "silencio")) {
    state.muted = !state.muted;
  }
  if (justo(state, "enter") || justo(state, "salto") || justo(state, "ataque")) {
    if (state.status === "titulo") {
      state.status = "jugando";
      state.hintTimer = 5;
      sonido(state, "meta");
    } else if (state.status === "nivel_completado") {
      siguienteNivel(state);
    } else if (state.status === "derrota" || state.status === "victoria") {
      reiniciarJuego(state);
    }
  }
  if (state.status !== "jugando") {
    return;
  }
  if (justo(state, "salto")) {
    state.player.jumpBuffer = state.data.game.rules.jump_buffer;
  }
  if (soltado(state, "salto")) {
    if (state.player && state.player.vy < 0) {
      state.player.vy *= (state.data.game.rules.corte_salto || 0.45);
    }
  }
  if (justo(state, "dash")) {
    intentarDash(state);
  }
  if (justo(state, "ataque")) {
    intentarAtaque(state);
  }
}

function actualizarHud(state) {
  const enJuego = state.status !== "titulo";
  const est = ESTILOS_GOTICOS_WEB[state.estiloActual] || ESTILOS_GOTICOS_WEB.monastico;
  const p = state.player;
  const listo =
    p.dashTime <= 0 &&
    p.dashCooldown <= 0 &&
    (p.onGround || p.airDash > 0);

  const jefeActivo = (state.bosses || []).find((b) => b.alive);

  // Textos
  state.txtNivel.text = `NIVEL ${state.levelIndex + 1}/${state.data.levels.length} — ${state.level.name.toUpperCase()}`;
  state.txtNivel.style.fill = est.oro;

  state.txtNivelSub.text = "CRIPTA DE LOS CAÍDOS";
  state.txtNivelSub.style.fill = est.secundario;

  state.txtAlmas.text = `ALMAS ${state.levelSouls}/${state.level.total_souls}`;
  state.txtAlmas.style.fill = est.alma;

  state.txtVidas.text = "VIDAS";
  state.txtVidas.style.fill = est.carmesi;

  state.txtTiempo.text = `${state.levelTime.toFixed(1)}s`;
  state.txtTiempo.style.fill = est.texto;

  state.txtDash.text = listo ? "DASH LISTO" : "DASH...";
  state.txtDash.style.fill = listo ? est.dash : 0x6b7280;

  if (p.hasPowerup) {
    state.txtArma.text = "GUADAÑA [Z/J]";
    state.txtArma.style.fill = 0xc084fc;
  } else if (p.hasShovel) {
    state.txtArma.text = "PALA [Z/J]";
    state.txtArma.style.fill = est.oro;
  } else {
    state.txtArma.text = "SIN ARMA";
    state.txtArma.style.fill = 0x6b7280;
  }

  state.txtEstilo.text = `[F2] ${est.nombre.toUpperCase().split(" ")[0]}`;
  state.txtEstilo.style.fill = est.secundario;

  if (jefeActivo) {
    state.txtBoss.visible = enJuego;
    state.txtBoss.text = `EL CUSTODIO DEL OSARIO (FASE ${jefeActivo.fase >= 2 ? "II" : "I"})`;
    state.txtBoss.style.fill = jefeActivo.fase >= 2 ? est.carmesi : est.oro;
    state.txtNivel.visible = false;
    state.txtNivelSub.visible = false;
  } else {
    state.txtBoss.visible = false;
    state.txtNivel.visible = enJuego;
    state.txtNivelSub.visible = enJuego;
  }

  for (const texto of [
    state.txtAlmas,
    state.txtVidas,
    state.txtTiempo,
    state.txtDash,
    state.txtArma,
    state.txtEstilo,
  ]) {
    texto.visible = enJuego;
  }

  state.hudG.clear();
  if (enJuego) {
    // 1. Riel superior continuo de 72px
    state.hudG.beginFill(est.panelBg, 0.94);
    state.hudG.drawRect(0, 0, ANCHO, 72);
    state.hudG.endFill();

    // Doble reborde inferior
    state.hudG.lineStyle(2, est.borde, 0.9);
    state.hudG.moveTo(0, 70);
    state.hudG.lineTo(ANCHO, 70);
    state.hudG.lineStyle(1, est.oro, 0.4);
    state.hudG.moveTo(0, 72);
    state.hudG.lineTo(ANCHO, 72);
    state.hudG.lineStyle(0, 0, 0);

    // Divisores de filigrana entre las 3 zonas (x = 280 y x = 680)
    for (const divX of [280, 680]) {
      state.hudG.lineStyle(1, est.borde, 0.5);
      state.hudG.moveTo(divX, 8);
      state.hudG.lineTo(divX, 64);
      state.hudG.lineStyle(0, 0, 0);

      // Diamante ornamental central en divisor
      state.hudG.beginFill(est.oro, 0.7);
      state.hudG.moveTo(divX, 32);
      state.hudG.lineTo(divX + 3, 36);
      state.hudG.lineTo(divX, 40);
      state.hudG.lineTo(divX - 3, 36);
      state.hudG.closePath();
      state.hudG.endFill();
    }

    // Ornamentos específicos de estilo
    if (state.estiloActual === "monastico") {
      const cx = 12, cy = 18;
      state.hudG.beginFill(est.oro, 0.8);
      state.hudG.drawRect(cx - 1, cy - 6, 3, 13);
      state.hudG.drawRect(cx - 5, cy - 3, 11, 3);
      state.hudG.endFill();
    } else if (state.estiloActual === "hierro") {
      for (let rx = 16; rx < ANCHO; rx += 48) {
        state.hudG.beginFill(0x8a92a3, 0.9);
        state.hudG.drawCircle(rx, 70, 2);
        state.hudG.endFill();
        state.hudG.beginFill(0x181a20, 0.9);
        state.hudG.drawCircle(rx, 70, 1);
        state.hudG.endFill();
      }
    } else if (state.estiloActual === "espectral") {
      const rx = 12, ry = 18;
      state.hudG.lineStyle(1, est.oro, 0.85);
      state.hudG.moveTo(rx, ry - 6);
      state.hudG.lineTo(rx + 5, ry);
      state.hudG.lineTo(rx, ry + 6);
      state.hudG.lineTo(rx - 5, ry);
      state.hudG.closePath();
      state.hudG.lineStyle(0, 0, 0);
    } else if (state.estiloActual === "osario") {
      const ox = 12, oy = 18;
      state.hudG.beginFill(est.oro, 0.85);
      state.hudG.drawCircle(ox, oy - 2, 4);
      state.hudG.drawRect(ox - 2, oy + 2, 5, 3);
      state.hudG.endFill();
      state.hudG.beginFill(0x0a0809, 1);
      state.hudG.drawCircle(ox - 1.5, oy - 2, 1);
      state.hudG.drawCircle(ox + 1.5, oy - 2, 1);
      state.hudG.endFill();
    }

    // --- ZONA IZQUIERDA: Vidas y Dash ---
    for (let i = 0; i < 3; i += 1) {
      const vx = 76 + i * 26;
      const lleno = i < state.lives;

      state.hudG.lineStyle(1, lleno ? est.oro : 0x3d3545, 0.8);
      state.hudG.beginFill(lleno ? est.carmesi : 0x18121a, 0.9);
      state.hudG.moveTo(vx - 7, 14);
      state.hudG.lineTo(vx, 7);
      state.hudG.lineTo(vx + 7, 14);
      state.hudG.lineTo(vx, 23);
      state.hudG.closePath();
      state.hudG.endFill();
      state.hudG.lineStyle(0, 0, 0);

      if (lleno) {
        state.hudG.beginFill(0xffffff, 0.6);
        state.hudG.drawCircle(vx - 2, 12, 1.2);
        state.hudG.endFill();
      }
    }

    // Gauge de Dash
    state.hudG.beginFill(0x0a0d14, 0.9);
    state.hudG.drawRect(20, 50, 240, 12);
    state.hudG.endFill();
    state.hudG.lineStyle(1, est.borde, 0.7);
    state.hudG.drawRect(20, 50, 240, 12);
    state.hudG.lineStyle(0, 0, 0);

    let progreso = 1;
    if (!listo) {
      progreso = Math.max(0, 1 - p.dashCooldown / state.data.game.rules.dash_cooldown);
      if (p.airDash <= 0 && p.dashCooldown <= 0) {
        progreso = 0;
      }
    }
    const dashW = Math.max(0, Math.min(236, Math.round(236 * progreso)));
    if (dashW > 0) {
      state.hudG.beginFill(listo ? est.dash : 0x475569, 0.95);
      state.hudG.drawRect(22, 52, dashW, 8);
      state.hudG.endFill();
      if (listo) {
        state.hudG.beginFill(0xffffff, 0.4);
        state.hudG.drawRect(22, 52, dashW, 2);
        state.hudG.endFill();
      }
    }

    // --- ZONA CENTRAL: Boss Bar facetada de 6 rubíes ---
    if (jefeActivo) {
      const maxHp = jefeActivo.maxHp || 6;
      const segW = 52, segH = 14, gap = 6;
      const totalW = maxHp * segW + (maxHp - 1) * gap;
      const startX = Math.round(480 - totalW / 2);
      const startY = 36;

      for (let s = 0; s < maxHp; s += 1) {
        const sx = startX + s * (segW + gap);
        const activo = s < jefeActivo.hp;

        state.hudG.lineStyle(1, activo ? (jefeActivo.fase >= 2 ? 0xff4444 : est.oro) : 0x282030, 0.9);
        state.hudG.beginFill(activo ? (jefeActivo.fase >= 2 ? 0xd22030 : est.bossColor) : 0x120c16, 0.95);
        state.hudG.moveTo(sx + 4, startY);
        state.hudG.lineTo(sx + segW - 4, startY);
        state.hudG.lineTo(sx + segW, startY + segH / 2);
        state.hudG.lineTo(sx + segW - 4, startY + segH);
        state.hudG.lineTo(sx + 4, startY + segH);
        state.hudG.lineTo(sx, startY + segH / 2);
        state.hudG.closePath();
        state.hudG.endFill();
        state.hudG.lineStyle(0, 0, 0);

        if (activo) {
          state.hudG.beginFill(0xffffff, 0.5);
          state.hudG.drawRect(sx + 6, startY + 2, segW - 12, 2);
          state.hudG.endFill();
        }
      }
    }

    // Mini icono de alma a la derecha
    const sax = 702, say = 22;
    state.hudG.beginFill(est.alma, 0.3);
    state.hudG.drawCircle(sax, say, 8);
    state.hudG.endFill();
    state.hudG.beginFill(est.alma, 0.9);
    state.hudG.drawCircle(sax, say, 4);
    state.hudG.endFill();
  }

  const mostrarPista = state.hintTimer > 0 && state.status === "jugando";
  state.hintBg.visible = mostrarPista;
  state.hintText.visible = mostrarPista;
  if (mostrarPista) {
    state.hintBg.clear();
    state.hintBg.beginFill(0x080c16, 0.90);
    state.hintBg.drawRect(40, 78, 880, 50);
    state.hudG.lineStyle(1, est.borde, 0.8);
    state.hintBg.drawRect(40, 78, 880, 50);
    state.hudG.lineStyle(0, 0, 0);
    state.hintBg.endFill();
    state.hintBg.beginFill(est.dash, 1);
    state.hintBg.drawRect(40, 78, 4, 50);
    state.hintBg.endFill();
    state.hintText.text = state.hintTextMsg || ("PISTA  " + state.level.hint);
    state.hintText.x = 56;
    state.hintText.y = 88;
  }

  const mostrarOverlay = state.status !== "jugando";
  state.overlayBg.visible = mostrarOverlay;
  state.overlayTitle.visible = mostrarOverlay;
  state.overlaySub.visible = mostrarOverlay;
  state.overlayInfo.visible = false;

  if (mostrarOverlay) {
    state.overlayTitle.style.fontSize = 52;
    state.overlayTitle.y = 206;
    state.overlaySub.y = 274;
    state.overlaySub.style.fontSize = 22;
    state.overlayInfo.y = 330;

    if (state.status === "titulo") {
      state.overlayTitle.style.fontSize = 68;
      state.overlayTitle.y = 96;
      state.overlayTitle.text = "IN CRYPTA";
      state.overlayTitle.style.fill = 0xe8c15a;
      state.overlaySub.y = 184;
      state.overlaySub.style.fontSize = 26;
      state.overlaySub.text = "El sepulturero de la cripta";
      state.overlaySub.style.fill = 0xcfd8e3;
      state.overlayInfo.y = 248;
      const estNom = (ESTILOS_GOTICOS_WEB[state.estiloActual] || ESTILOS_GOTICOS_WEB.monastico).nombre;
      state.overlayInfo.text =
        "Equipo 6\n" +
        "Ovelar Alejandro Ezequiel · Joaquín Cardiel Gomez · Jonathan Javier Pietracci\n\n" +
        "Estilo Gótico: " + estNom.toUpperCase() + "  [Presiona F2 para alternar]\n\n" +
        "ENTER para entrar a la cripta   ·   F2 cambiar estilo   ·   M silenciar";
      state.overlayInfo.visible = true;
    } else if (state.status === "pausa") {
      state.overlayTitle.text = "PAUSA";
      state.overlayTitle.style.fill = 0xe8c15a;
      state.overlaySub.text = "P para continuar · R para reiniciar";
      state.overlaySub.style.fill = 0xf5f5f5;
    } else if (state.status === "nivel_completado") {
      state.overlayTitle.text = "¡Nivel completado!";
      state.overlayTitle.style.fill = 0xe8c15a;
      state.overlaySub.text = "ENTER para seguir · el portón te espera";
      state.overlaySub.style.fill = 0xf5f5f5;
    } else if (state.status === "derrota") {
      state.overlayTitle.text = "La luz se apagó";
      state.overlayTitle.style.fill = 0xd2414b;
      state.overlaySub.text = "ENTER para reiniciar · R para volver al inicio";
      state.overlaySub.style.fill = 0xf5f5f5;
    } else if (state.status === "victoria") {
      state.overlayTitle.text = "¡Escapaste de la cripta!";
      state.overlayTitle.style.fill = 0xe8c15a;
      state.overlaySub.text =
        `Almas: ${state.totalSouls} · Tiempo: ${state.totalTime.toFixed(1)}s`;
      state.overlaySub.style.fill = 0xf5f5f5;
      state.overlayInfo.y = 326;
      state.overlayInfo.text = "Equipo 6 · Gracias por jugar IN CRYPTA";
      state.overlayInfo.visible = true;
    }
  }

  state.flashG.clear();
  if (state.flash > 0) {
    state.flashG.beginFill(state.flashColor, Math.min(0.45, state.flash * 2.4));
    state.flashG.drawRect(0, 0, ANCHO, ALTO);
    state.flashG.endFill();
  }
}

function dibujarDinamico(state) {
  const g = state.dynG;
  const p = state.paleta;
  const tiempo = state.totalTime;
  g.clear();

  for (const plat of (state.platforms || [])) {
    g.beginFill(0x282c37, 1);
    g.drawRect(plat.x, plat.y, plat.w, plat.h);
    g.endFill();
    g.beginFill(0x5a6375, 1);
    g.drawRect(plat.x, plat.y, plat.w, 4);
    g.endFill();
    g.lineStyle(1, 0x1a1e24, 1);
    g.drawRect(plat.x, plat.y, plat.w, plat.h);
    g.lineStyle(0, 0, 0);
  }

  for (const pala of (state.palas || [])) {
    if (pala.collected) continue;
    const flot = Math.sin(tiempo * 5 + pala.x * 0.05) * 3;
    const cx = pala.x + pala.w / 2;
    const cy = pala.y + pala.h / 2 + flot;
    g.lineStyle(3, 0x8a6234, 1);
    g.moveTo(cx - 4, cy - 8);
    g.lineTo(cx + 4, cy + 8);
    g.lineStyle(0, 0, 0);
    g.beginFill(0xc0c8d8, 1);
    g.drawRect(cx + 2, cy + 5, 8, 6);
    g.endFill();
  }

  for (const pu of (state.powerups || [])) {
    if (pu.collected) continue;
    const flot = Math.sin(tiempo * 5 + pu.x * 0.05) * 4;
    const cx = pu.x + pu.w / 2;
    const cy = pu.y + pu.h / 2 + flot;
    g.beginFill(0xa855f7, 0.3);
    g.drawCircle(cx, cy, 16);
    g.endFill();
    g.lineStyle(2, 0xc084fc, 1);
    g.drawCircle(cx, cy, 10);
    g.lineStyle(0, 0, 0);
    g.beginFill(0xf3e8ff, 1);
    g.drawCircle(cx, cy, 4);
    g.endFill();
  }

  for (const cp of (state.checkpoints || [])) {
    if (cp.active) {
      const llama = Math.sin(tiempo * 10 + cp.x) * 2;
      g.beginFill(0x38bdf8, 0.4);
      g.drawCircle(cp.x + cp.w / 2, cp.y + 2 + llama, 7);
      g.endFill();
      g.beginFill(0xe0f2fe, 1);
      g.drawCircle(cp.x + cp.w / 2, cp.y + 3 + llama, 3);
      g.endFill();
    }
  }

  for (const alma of state.souls) {
    if (alma.collected) {
      continue;
    }
    const flotacion = Math.sin(tiempo * 5 + alma.x * 0.03) * 3;
    const cx = alma.x + alma.w / 2;
    const cy = alma.y + alma.h / 2 + flotacion;
    g.beginFill(0xb48c14, 0.11);
    g.drawCircle(cx, cy, 20);
    g.endFill();
    g.beginFill(p.alma, 0.26);
    g.drawCircle(cx, cy, 13);
    g.endFill();
    g.beginFill(0xffd23c, 1);
    g.drawEllipse(cx, cy, 7, 8);
    g.endFill();
    g.beginFill(0xfff5b4, 1);
    g.drawEllipse(cx - 1, cy - 2, 4, 5);
    g.endFill();
    g.beginFill(0xffffff, 1);
    g.drawCircle(cx + 2, cy - 3, 1.5);
    g.endFill();
    g.beginFill(0x8b5bd6, 0.5);
    g.moveTo(cx, cy + 8);
    g.lineTo(cx - 4, cy + 17);
    g.lineTo(cx + 4, cy + 14);
    g.closePath();
    g.endFill();
  }

  for (const enemigo of state.enemies) {
    if (!enemigo.alive) {
      continue;
    }
    const salto = Math.sin(tiempo * 7 + enemigo.x * 0.02) * 2;
    const cx = enemigo.x + enemigo.w / 2;
    const cy = enemigo.y + enemigo.h / 2 + salto;
    g.beginFill(0x08070d, 0.7);
    g.drawEllipse(cx, enemigo.y + enemigo.h - 1, enemigo.w / 2, 4);
    g.endFill();
    g.beginFill(0x1e1324, 1);
    g.drawEllipse(cx, cy + 2, enemigo.w / 2, enemigo.h / 2);
    g.endFill();
    g.beginFill(p.enemigo, 1);
    g.moveTo(cx - 12, cy + 8);
    g.lineTo(cx - 9, cy - 8);
    g.lineTo(cx - 3, cy - 12);
    g.lineTo(cx + 3, cy - 9);
    g.lineTo(cx + 9, cy - 12);
    g.lineTo(cx + 12, cy + 8);
    g.closePath();
    g.endFill();
    g.beginFill(0x2a1524, 1);
    g.drawEllipse(cx, cy + 4, 8, 10);
    g.endFill();
    g.beginFill(0xd2414b, 0.7);
    g.drawCircle(cx - 5, cy - 2, 6);
    g.drawCircle(cx + 5, cy - 2, 6);
    g.endFill();
    g.beginFill(0xffe9b0, 1);
    g.drawCircle(cx - 5, cy - 2, 2);
    g.drawCircle(cx + 5, cy - 2, 2);
    g.endFill();
    g.beginFill(0x0c0c12, 1);
    g.drawCircle(cx - 5, cy - 2, 1);
    g.drawCircle(cx + 5, cy - 2, 1);
    g.endFill();
    g.lineStyle(2, p.enemigo, 0.8);
    g.moveTo(cx - 10, cy + 5);
    g.lineTo(cx - 17, cy + 13 + salto);
    g.moveTo(cx + 10, cy + 5);
    g.lineTo(cx + 17, cy + 13 + salto);
    g.lineStyle(0, 0, 0);
  }

  for (const em of (state.enemiesMelee || [])) {
    if (!em.alive) continue;
    const salto = Math.sin(tiempo * 7 + em.x * 0.02) * 2;
    const cx = em.x + em.w / 2;
    const cy = em.y + em.h / 2 + salto;
    g.beginFill(0x1a1215, 1);
    g.drawEllipse(cx, cy + 2, em.w / 2, em.h / 2);
    g.endFill();
    g.beginFill(0xd2414b, 1);
    g.drawCircle(cx - 4, cy - 2, 2.5);
    g.drawCircle(cx + 4, cy - 2, 2.5);
    g.endFill();
    g.lineStyle(2, 0xd8c29a, 1);
    g.moveTo(cx + em.dir * 4, cy + 2);
    g.lineTo(cx + em.dir * 14, cy - 6);
    g.lineStyle(0, 0, 0);
  }

  for (const boss of (state.bosses || [])) {
    if (!boss.alive) continue;
    const bx = boss.x;
    const by = boss.y;
    const parpadea = boss.invuln > 0 && Math.floor(tiempo * 20) % 2 === 0;
    if (!parpadea) {
      g.beginFill(boss.fase >= 2 ? 0x2e111a : 0x1b1322, 1);
      g.drawRoundedRect(bx + 4, by + 12, boss.w - 8, boss.h - 14, 6);
      g.endFill();
      g.beginFill(boss.fase >= 2 ? 0x8a2336 : 0x483a54, 1);
      g.drawRect(bx + 8, by + 20, boss.w - 16, 18);
      g.endFill();
      g.beginFill(0xdec89e, 1);
      g.drawCircle(bx + boss.w / 2, by + 14, 12);
      g.endFill();
      g.lineStyle(3, 0x8a7250, 1);
      g.moveTo(bx + boss.w / 2 - 8, by + 12);
      g.lineTo(bx + boss.w / 2 - 14, by + 2);
      g.moveTo(bx + boss.w / 2 + 8, by + 12);
      g.lineTo(bx + boss.w / 2 + 14, by + 2);
      g.lineStyle(0, 0, 0);
      g.beginFill(boss.fase >= 2 ? 0xff2222 : 0xffaa22, 1);
      g.drawCircle(bx + boss.w / 2 + boss.dir * 3, by + 13, 2.5);
      g.drawCircle(bx + boss.w / 2 + boss.dir * 7, by + 13, 2.5);
      g.endFill();
      g.lineStyle(4, 0x5a483a, 1);
      g.moveTo(bx + boss.w / 2 + boss.dir * 12, by + 6);
      g.lineTo(bx + boss.w / 2 + boss.dir * 20, by + boss.h - 4);
      g.lineStyle(0, 0, 0);
      g.beginFill(0xa8b4c2, 1);
      g.drawRect(bx + boss.w / 2 + boss.dir * 16, by + 4, 12, 14);
      g.endFill();
    }
  }

  for (const onda of (state.bossWaves || [])) {
    g.beginFill(0xd8c29a, 0.7);
    g.drawEllipse(onda.x + onda.w / 2, onda.y + onda.h / 2, onda.w / 2, onda.h / 2);
    g.endFill();
    g.beginFill(0xffffff, 0.9);
    g.drawCircle(onda.x + onda.w / 2, onda.y + 4, 3);
    g.endFill();
  }

  const jugador = state.player;
  const estiloWeb = ESTILOS_GOTICOS_WEB[state.estiloActual] || ESTILOS_GOTICOS_WEB.monastico;
  const parpadea = jugador.invuln > 0 && Math.floor(tiempo * 16) % 2 === 0;
  if (!parpadea) {
    const jx = jugador.x;
    const jy = jugador.y;
    const baseY = jy + jugador.h;
    const centroX = jx + jugador.w / 2;
    const dir = jugador.dir;

    if (jugador.dashTime > 0) {
      for (let i = 0; i < 3; i += 1) {
        g.beginFill([0x1e7882, 0x23a5aa, 0x2dd2c5][i], 0.5);
        g.drawRect(
          jx - jugador.dashDir * (10 + i * 9),
          jy,
          jugador.w,
          jugador.h
        );
        g.endFill();
      }
    }

    // Sombra proyectada
    g.beginFill(0x08070d, 0.65);
    g.drawEllipse(centroX, baseY - 1, 14, 4);
    g.endFill();

    // Capa con inercia y oscilación
    const capaOsc = Math.sin(tiempo * 8 + (Math.abs(jugador.vx) > 10 ? tiempo * 10 : 0)) * 4;
    g.beginFill(estiloWeb.carmesi || 0x7c1822, 0.85);
    g.moveTo(centroX - dir * 2, jy + 13);
    g.lineTo(centroX - dir * (12 + capaOsc), baseY - 2);
    g.lineTo(centroX - dir * (6 + capaOsc * 0.5), baseY + 1);
    g.lineTo(centroX + dir * 2, jy + 17);
    g.closePath();
    g.endFill();

    // Arma (Pala / Guadaña)
    if (jugador.hasShovel) {
      g.lineStyle(3, 0x4e3a2a, 1);
      g.moveTo(centroX + dir * 6, jy + 8);
      g.lineTo(centroX + dir * 16, baseY - 3);
      g.lineStyle(0, 0, 0);
      g.beginFill(jugador.hasPowerup ? 0xc084fc : 0xb9c4d0, 1);
      g.drawRect(centroX + dir * 14, baseY - 6, 9, 5);
      g.endFill();
    }

    // Piernas
    g.beginFill(0x151b2d, 1);
    g.drawRect(jx + 5, jy + 22, 5, 8);
    g.drawRect(jx + 14, jy + 22, 5, 8);
    g.endFill();
    g.beginFill(0x08070d, 1);
    g.drawRect(jx + 4, baseY - 3, 7, 3);
    g.drawRect(jx + 13, baseY - 3, 7, 3);
    g.endFill();

    // Torso y cinto
    g.beginFill(p.jugador, 1);
    g.drawRoundedRect(jx + 4, jy + 12, 16, 14, 3);
    g.endFill();
    g.lineStyle(1, p.jugadorOscuro, 1);
    g.drawRoundedRect(jx + 4, jy + 12, 16, 14, 3);
    g.lineStyle(0, 0, 0);
    g.beginFill(0x3a2a22, 1);
    g.drawRect(jx + 4, jy + 21, 16, 3);
    g.endFill();
    g.beginFill(estiloWeb.oro || 0xb48c14, 1);
    g.drawRect(jx + 12, jy + 21, 3, 3);
    g.endFill();

    // Cabeza y sombrero de sepulturero
    g.beginFill(0xf0c9a0, 1);
    g.drawCircle(centroX, jy + 9, 7);
    g.endFill();
    g.beginFill(0x2a2230, 1);
    g.drawRect(jx + 4, jy + 6, 16, 4);
    g.endFill();
    g.beginFill(0x15121c, 1);
    g.drawRect(jx + 1, jy + 8, 22, 3);
    g.endFill();
    g.beginFill(0x0c0c12, 1);
    g.drawCircle(centroX + dir * 3, jy + 10, 1.5);
    g.endFill();
    g.beginFill(0x5c4435, 1);
    g.drawRect(centroX - 2, jy + 13, 4, 3);
    g.endFill();

    // Farol pendular con halo translúcido circular
    const linternaOsc = Math.sin(tiempo * 6) * 3;
    const lx = jx + (dir > 0 ? 22 : 2);
    const ly = jy + 18 + linternaOsc;
    // 3 capas de halo
    g.beginFill(estiloWeb.oro || 0xffd27a, 0.08);
    g.drawCircle(lx, ly, 28);
    g.endFill();
    g.beginFill(estiloWeb.oro || 0xffd27a, 0.20);
    g.drawCircle(lx, ly, 15);
    g.endFill();
    g.beginFill(0xfffbe6, 0.35);
    g.drawCircle(lx, ly, 7);
    g.endFill();
    g.lineStyle(1, estiloWeb.borde || 0xb48c14, 1);
    g.moveTo(lx, ly - 5);
    g.lineTo(lx, ly - 2);
    g.lineStyle(0, 0, 0);
    g.beginFill(0x3a2a22, 1);
    g.drawRect(lx - 3, ly - 2, 6, 7);
    g.endFill();
    g.beginFill(estiloWeb.oro || 0xffd23c, 1);
    g.drawRect(lx - 2, ly - 1, 4, 4);
    g.endFill();
  }

  if (jugador.attackTimer > 0) {
    const alcance = jugador.hasPowerup ? 72 : 36;
    const alto = jugador.hasPowerup ? 42 : 26;
    const ax = jugador.dir > 0 ? jugador.x + jugador.w - 4 : jugador.x - alcance + 4;
    const ay = jugador.y + jugador.h / 2 - alto / 2;
    g.lineStyle(3, jugador.hasPowerup ? 0xc084fc : 0xffe9b0, 0.85);
    g.moveTo(ax, ay + alto);
    g.quadraticCurveTo(ax + alcance / 2, ay, ax + alcance, ay + alto / 2);
    g.lineStyle(0, 0, 0);
    g.beginFill(jugador.hasPowerup ? 0xa855f7 : 0xffd23c, 0.35);
    g.drawEllipse(ax + alcance / 2, ay + alto / 2, alcance / 2, alto / 2);
    g.endFill();
  }

  for (const particula of state.particles) {
    const proporcion = Math.max(0, particula.vida / particula.vidaInicial);
    g.beginFill(particula.color, proporcion);
    g.drawCircle(particula.x, particula.y, Math.max(1, particula.tamano * proporcion));
    g.endFill();
  }
}

function actualizar(state, dt) {
  if (state.status === "jugando") {
    state.levelTime += dt;
    state.totalTime += dt;
    if (state.hintTimer > 0) {
      state.hintTimer = Math.max(0, state.hintTimer - dt);
      if (state.hintTimer <= 0) {
        state.hintTextMsg = null;
      }
    }

    actualizarPlataformas(state, dt);
    actualizarJugador(state, dt);
    if (state.player.y > state.level.size.height + 120) {
      dañar(state, true);
      actualizarCamara(state, dt, false);
      actualizarHud(state);
      return;
    }

    actualizarObjetos(state);
    actualizarCombate(state);
    actualizarJefe(state, dt);
    actualizarOndasJefe(state, dt);
    actualizarEnemigos(state, dt);
    actualizarEnemigosMelee(state, dt);
    actualizarAlmas(state);
    actualizarParticulas(state, dt);

    for (const peligro of state.level.hazards || []) {
      if (solapan(state.player, peligro)) {
        dañar(state, true);
        actualizarCamara(state, dt, false);
        actualizarHud(state);
        return;
      }
    }

    if (solapan(state.player, state.level.goal)) {
      const jefeVivo = (state.bosses || []).some((b) => b.alive);
      if (jefeVivo) {
        state.hintTimer = 2.0;
        state.hintTextMsg = "LA SALIDA ESTÁ SELLADA · DERROTÁ AL CUSTODIO";
      } else {
        emitirMeta(state, state.level.goal.x + 10, state.level.goal.y + 10);
        sonido(state, "meta");
        if (state.levelIndex + 1 >= state.data.levels.length) {
          state.totalSouls += state.levelSouls;
          state.status = "victoria";
        } else {
          state.status = "nivel_completado";
        }
      }
    }

    actualizarCamara(state, dt, false);
  } else {
    actualizarParticulas(state, dt);
  }

  actualizarHud(state);
  dibujarFondo(state);
  dibujarDinamico(state);
}

function frame(state) {
  if (!state.ready) {
    return;
  }
  if (state.error) {
    if (state.loadingBg) {
      state.loadingBg.visible = true;
    }
    if (state.loadingText) {
      state.loadingText.visible = true;
      state.loadingText.text = "Error: " + state.error;
      state.loadingText.style.fill = 0xd2414b;
    }
    return;
  }

  const ahora = performance.now();
  const dt = Math.min(0.033, Math.max(0, (ahora - state.lastTime) / 1000));
  state.lastTime = ahora;
  state.keys = leerTeclas();
  manejarEntrada(state);

  if (state.flash > 0) {
    state.flash = Math.max(0, state.flash - dt);
  }

  actualizar(state, dt);
  state.prev = Object.assign({}, state.keys);
}

if (!runtimeScene.__incryptaRuntime) {
  const estado = crearEstado();
  runtimeScene.__incryptaRuntime = estado;
  inicializar(estado);
} else {
  const estado = runtimeScene.__incryptaRuntime;
  if (estado.initialized) {
    frame(estado);
  }
}

const estadoGlobal = runtimeScene.__incryptaRuntime;
if (estadoGlobal) {
  estadoGlobal.initialized = true;
}
})();
