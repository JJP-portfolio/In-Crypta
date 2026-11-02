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

function tieneSprites() {
  return (
    typeof PIXI !== "undefined" &&
    typeof PIXI.Sprite === "function" &&
    typeof PIXI.Texture === "function" &&
    typeof PIXI.Texture.from === "function"
  );
}

function obtenerTextura(state, archivo) {
  if (!tieneSprites()) return null;
  if (!state.texCache) state.texCache = {};
  if (!state.texCache[archivo]) {
    try {
      state.texCache[archivo] = PIXI.Texture.from("../gdevelop_nativo/assets/" + archivo);
    } catch (e) {
      return null;
    }
  }
  return state.texCache[archivo];
}

function ocultarPoolSprites(pool) {
  if (!pool) return;
  for (const k of Object.keys(pool)) {
    if (pool[k]) pool[k].visible = false;
  }
}

function colocarSprite(state, contenedor, pool, clave, archivo, x, y, w, h, flipX = false, alpha = 1, tint = 0xffffff) {
  if (!tieneSprites() || !contenedor || !pool) return false;
  const tex = obtenerTextura(state, archivo);
  if (!tex) return false;
  let spr = pool[clave];
  if (!spr) {
    spr = new PIXI.Sprite(tex);
    pool[clave] = spr;
    contenedor.addChild(spr);
  } else if (spr.texture !== tex) {
    spr.texture = tex;
  }
  spr.visible = true;
  spr.alpha = alpha;
  spr.tint = tint;
  spr.width = w;
  spr.height = h;
  if (flipX) {
    spr.scale.x = -Math.abs(spr.scale.x);
    spr.x = Math.round(x + w);
  } else {
    spr.scale.x = Math.abs(spr.scale.x);
    spr.x = Math.round(x);
  }
  spr.y = Math.round(y);
  return true;
}

function crearTexto(padre, contenido, tamano, color, x, y, opciones = {}) {
  const esTitulo = tamano >= 17 || Boolean(opciones.family);
  const estilo = {
    fontFamily: opciones.family || (esTitulo ? '"Noto Serif Display", Georgia, serif' : '"DejaVu Sans", "Liberation Sans", Arial, sans-serif'),
    fontSize: tamano,
    fill: color,
    fontWeight: "bold",
    stroke: 0x08060c,
    strokeThickness: tamano >= 24 ? 4 : 3,
    dropShadow: true,
    dropShadowColor: 0x050308,
    dropShadowDistance: tamano >= 24 ? 2 : 1,
    dropShadowBlur: 0,
  };
  if (opciones.wordWrap) {
    estilo.wordWrap = true;
    estilo.wordWrapWidth = opciones.wordWrap;
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
    arriba: tecla("Up") || tecla("KeyW") || tecla("w"),
    abajo: tecla("Down") || tecla("KeyS") || tecla("s"),
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
    activeLevels: [],
    modoPartida: "campania",
    menuModoIndice: 0,
    menuSalaIndice: 0,
    player: null,
    souls: [],
    enemies: [],
    enemiesMelee: [],
    platforms: [],
    palas: [],
    powerupsDash: [],
    powerups: [],
    minibosses: [],
    bosses: [],
    bossWaves: [],
    checkpoints: [],
    respawnX: 0,
    respawnY: 0,
    escudoFarol: false,
    almasVidaAcumuladas: 0,
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
    texCache: {},
    worldPool: {},
    hudPool: {},
    root: null,
    bg: null,
    bgG: null,
    world: null,
    bgSpriteCont: null,
    staticG: null,
    dynG: null,
    worldSprites: null,
    fxG: null,
    hud: null,
    hudG: null,
    hudSprites: null,
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
  state.bgSpriteCont = new PIXI.Container();
  state.staticG = new PIXI.Graphics();
  state.dynG = new PIXI.Graphics();
  state.worldSprites = new PIXI.Container();
  state.fxG = new PIXI.Graphics();
  state.world.addChild(state.bgSpriteCont);
  state.world.addChild(state.staticG);
  state.world.addChild(state.dynG);
  state.world.addChild(state.worldSprites);
  state.world.addChild(state.fxG);
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
  state.hudSprites = new PIXI.Container();
  state.hud.addChild(state.hudG);
  state.hud.addChild(state.hudSprites);

  state.txtNivel = crearTexto(state.hud, "", 16, 0xf5f5f5, 480, 12, { centrado: true });
  state.txtNivelSub = crearTexto(state.hud, "", 11, 0xa8987a, 480, 34, { centrado: true });
  state.txtAlmas = crearTexto(state.hud, "", 14, 0xffd23c, 718, 12);
  state.txtVidas = crearTexto(state.hud, "VIDAS", 13, 0xd2414b, 22, 12);
  state.txtTiempo = crearTexto(state.hud, "", 13, 0x96d2f5, 864, 12);
  state.txtDash = crearTexto(state.hud, "DASH LISTO", 11, 0x46dcd2, 42, 34);
  state.txtArma = crearTexto(state.hud, "", 12, 0xffd23c, 718, 42);
  state.txtEstilo = crearTexto(state.hud, "[F2] MONÁSTICO", 11, 0xa8987a, 850, 42);
  state.txtBoss = crearTexto(state.hud, "", 15, 0xd2414b, ANCHO / 2, 12, { centrado: true });

  state.hintBg = new PIXI.Graphics();
  state.hud.addChild(state.hintBg);
  state.hintText = crearTexto(
    state.hud,
    "",
    15,
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
    hasShovel: Boolean(nivel.pala_inicial) || (state.modoPartida === "campania" && state.levelIndex >= 2),
    hasDashRelic:
      (state.modoPartida === "campania" && state.levelIndex >= 1) ||
      (state.modoPartida === "salas" && state.menuSalaIndice >= 1),
    hasPowerup: false,
    attackTimer: 0,
    attackDuration: 0.14,
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

function obtenerNivelesActivos(state) {
  if (state.modoPartida === "tutorial") {
    return state.data.tutorial ? [state.data.tutorial] : [];
  }
  if (state.modoPartida === "salas") {
    return state.data.rooms || [];
  }
  return state.data.levels || [];
}

function cargarNivel(state, indice, conservarVidas) {
  state.activeLevels = obtenerNivelesActivos(state);
  if (!state.activeLevels.length || !state.activeLevels[indice]) {
    state.status = "titulo";
    state.error = "No hay niveles disponibles para el modo seleccionado";
    return;
  }
  state.levelIndex = indice;
  state.level = state.activeLevels[indice];
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
  const rawPalas = state.level.shovels || state.level.palas || [];
  state.palas = rawPalas.map((pala) => ({
    x: pala.x,
    y: pala.y,
    w: pala.w,
    h: pala.h,
    collected: false,
  }));
  const rawDash = state.level.powerups_dash || [];
  state.powerupsDash = rawDash.map((pu) => ({
    x: pu.x,
    y: pu.y,
    w: pu.w,
    h: pu.h,
    collected: false,
  }));
  const rawRange = state.level.powerups_range || state.level.powerups || [];
  state.powerups = rawRange.map((pu) => ({
    x: pu.x,
    y: pu.y,
    w: pu.w,
    h: pu.h,
    collected: false,
  }));
  const rawMinibosses = state.level.minibosses || [];
  state.minibosses = rawMinibosses.map((mb) => ({
    x: mb.x,
    y: mb.y,
    w: mb.w,
    h: mb.h,
    minX: mb.min_x,
    maxX: mb.max_x,
    hp: mb.hp || mb.vida || 4,
    maxHp: mb.hp || mb.vida || 4,
    dir: -1,
    estado: "patrulla",
    timer: 1.8,
    invuln: 0,
    alive: true,
    engaged: false,
  }));
  state.bosses = (state.level.bosses || []).map((boss) => ({
    x: boss.x,
    y: boss.y,
    w: boss.w,
    h: boss.h,
    minX: boss.min_x,
    maxX: boss.max_x,
    hp: boss.hp || boss.vida || 6,
    maxHp: boss.hp || boss.vida || 6,
    fase: boss.fase || 1,
    dir: -1,
    invuln: 0,
    alive: true,
    engaged: false,
    vulnerableTimer: 0,
    attackTimer: 2.2,
    charging: false,
    chargeSpeed: 225,
  }));
  state.bossWaves = [];
  const rawCheckpoints = state.level.checkpoints && state.level.checkpoints.length
    ? state.level.checkpoints
    : (state.level.decorations || []).filter((d) => d.type === "s");
  state.checkpoints = rawCheckpoints.map((cp) => ({
    x: cp.x,
    y: cp.y,
    w: cp.w,
    h: cp.h,
    active: false,
  }));
  if (!conservarVidas) {
    state.lives = state.data.game.rules.vidas_iniciales;
    state.escudoFarol = false;
    state.almasVidaAcumuladas = 0;
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

  // Si están disponibles las texturas horneadas 1:1 de Pygame (fondo_nivel_X.png),
  // montar el lienzo completo del nivel como sprite 1:1.
  const usarFondoHorneado = tieneSprites() && state.bgSpriteCont;
  if (usarFondoHorneado) {
    const archivoFondo = "fondo_" + (nivel.id || ("nivel_" + (state.levelIndex + 1))) + ".png";
    colocarSprite(
      state,
      state.bgSpriteCont,
      state.worldPool,
      "__level_bg__",
      archivoFondo,
      0,
      0,
      nivel.size.width,
      nivel.size.height,
      false,
      1,
      0xffffff
    );
    return;
  }

  for (const solido of nivel.solids) {
    const esPiso = solido.y >= nivel.size.height - 2 * tile;
    const esTecho = solido.y <= tile;
    if (!esPiso && !esTecho && solido.w >= 64) {
      g.beginFill(0x1a1c26, 0.9);
      g.moveTo(solido.x + 2, solido.y + solido.h);
      g.lineTo(solido.x + 14, solido.y + solido.h);
      g.lineTo(solido.x + 6, solido.y + solido.h + 10);
      g.closePath();
      g.moveTo(solido.x + solido.w - 2, solido.y + solido.h);
      g.lineTo(solido.x + solido.w - 14, solido.y + solido.h);
      g.lineTo(solido.x + solido.w - 6, solido.y + solido.h + 10);
      g.closePath();
      g.endFill();
    }
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

  // Rieles horizontales y travesaños de polea para plataformas móviles (fallback vectorial)
  for (const plat of (state.platforms || [])) {
    if (plat.axis === "h" || plat.axis === "H") {
      const rx1 = plat.origin_x - plat.amplitude + 8;
      const rx2 = plat.origin_x + plat.w + plat.amplitude - 8;
      const ry = plat.origin_y + Math.floor(plat.h / 2);
      g.beginFill(0x232530, 1);
      g.drawRect(rx1, ry - 2, Math.max(8, rx2 - rx1), 4);
      g.drawRect(rx1 - 3, ry - 5, 6, 10);
      g.drawRect(rx2 - 3, ry - 5, 6, 10);
      g.endFill();
    } else {
      const vigaY = Math.max(6, plat.origin_y - plat.amplitude - 18);
      g.beginFill(0x262936, 1);
      g.drawRect(plat.origin_x + 4, vigaY - 4, plat.w - 8, 8);
      g.drawCircle(plat.origin_x + 14, vigaY, 5);
      g.drawCircle(plat.origin_x + plat.w - 14, vigaY, 5);
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
  if (state.escudoFarol && !ignorarInvulnerabilidad) {
    state.escudoFarol = false;
    p.invuln = state.data.game.rules.invulnerabilidad;
    emitirAlma(state, p.x + p.w / 2, p.y + p.h / 2);
    sonido(state, "alma");
    sacudir(state, 6, 0.16);
    state.flash = 0.14;
    state.flashColor = 0xe5b842;
    state.hintTimer = 3.0;
    state.hintTextMsg = "EL MANTO DEL FAROL ABSORBIÓ EL GOLPE";
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
      emitirPala(state, em.x + enemigoWidth(em) / 2, em.y + em.h / 2);
      sonido(state, "stomp");
      sacudir(state, 6, 0.14);
    } else {
      dañar(state, false);
      return;
    }
  }
}

function enemigoWidth(e) {
  return e.w || 28;
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
  const reglas = state.data.game.rules;

  for (const pala of (state.palas || [])) {
    if (pala.collected || !solapan(p, pala)) {
      continue;
    }
    pala.collected = true;
    p.hasShovel = true;
    state.hintTimer = 4.0;
    state.hintTextMsg = "¡PALA OBTENIDA! [Z / J / CLICK] Golpe cuerpo a cuerpo y Pisotón letal";
    emitirPala(state, pala.x + pala.w / 2, pala.y + pala.h / 2);
    sonido(state, "pala");
  }

  for (const pud of (state.powerupsDash || [])) {
    if (pud.collected || !solapan(p, pud)) {
      continue;
    }
    pud.collected = true;
    p.hasDashRelic = true;
    p.airDash = reglas.dash_usos_aire;
    p.dashCooldown = 0;
    state.hintTimer = 4.2;
    state.hintTextMsg = "¡RELIQUIA DE SOMBRA OBTENIDA! Dash aéreo consagrado [SHIFT / X]";
    emitirAlma(state, pud.x + pud.w / 2, pud.y + pud.h / 2);
    sonido(state, "alma");
    sacudir(state, 5, 0.14);
  }

  const carceleroVivo = (state.minibosses || []).some((mb) => mb.alive);
  for (const pu of (state.powerups || [])) {
    if (pu.collected || !solapan(p, pu)) {
      continue;
    }
    if (carceleroVivo) {
      state.hintTimer = 2.8;
      state.hintTextMsg = "LA GUADAÑA ESTÁ SELLADA · DERROTÁ AL CARCELERO DEL OSARIO";
      continue;
    }
    pu.collected = true;
    p.hasPowerup = true;
    p.hasShovel = true;
    state.hintTimer = 4.5;
    state.hintTextMsg = "¡GUADAÑA CONSAGRADA OBTENIDA! Alcance extendido y daño sagrado en Fase II";
    emitirAlma(state, pu.x + pu.w / 2, pu.y + pu.h / 2);
    sonido(state, "alma");
    sacudir(state, 6, 0.16);
  }

  for (const cp of (state.checkpoints || [])) {
    if (!cp.active && solapan(p, cp)) {
      cp.active = true;
      state.respawnX = cp.x;
      state.respawnY = cp.y - p.h + cp.h;
      const vidasInit = reglas.vidas_iniciales || 3;
      if (state.lives < vidasInit) {
        state.lives = vidasInit;
      }
      if ((state.totalSouls + state.levelSouls) >= 5) {
        state.escudoFarol = true;
        state.hintTextMsg = "FAROL CONSAGRADO · VIDAS RESTAURADAS Y MANTO DEL FAROL ACTIVO";
      } else {
        state.hintTextMsg = "FAROL CONSAGRADO · PUNTO DE CONTROL Y VIDAS RESTAURADAS";
      }
      state.hintTimer = 3.8;
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

  for (const mb of (state.minibosses || [])) {
    if (!mb.alive || mb.invuln > 0 || !solapan(p.attackHitbox, mb)) {
      continue;
    }
    if (mb.estado === "cansado") {
      mb.hp -= 1;
      mb.invuln = 0.55;
      p.airDash = reglas.dash_usos_aire;
      p.dashCooldown = 0;
      emitirPala(state, mb.x + mb.w / 2, mb.y + mb.h / 2);
      sonido(state, "golpe");
      sacudir(state, 7, 0.16);
      state.flash = 0.08;
      state.flashColor = 0xffd23c;
      if (mb.hp <= 0) {
        mb.alive = false;
        emitirMeta(state, mb.x + mb.w / 2, mb.y + mb.h / 2);
        sonido(state, "meta");
        state.hintTimer = 4.2;
        state.hintTextMsg = "¡EL CARCELERO CAYÓ! El sello de la Guadaña Consagrada se ha roto";
      }
    } else {
      mb.invuln = 0.28;
      p.vx = -p.dir * 190;
      sacudir(state, 4, 0.1);
      sonido(state, "pala");
      state.hintTimer = 2.8;
      state.hintTextMsg = "¡ARMADURA PESADA! Esquivá su embestida y atacá cuando quede CANSADO";
    }
  }

  for (const boss of (state.bosses || [])) {
    if (!boss.alive || !solapan(p.attackHitbox, boss)) {
      continue;
    }
    if (boss.invuln > 0) {
      continue;
    }

    if (boss.fase === 1 || p.hasPowerup) {
      boss.hp -= 1;
      boss.invuln = 0.55;
      p.airDash = reglas.dash_usos_aire;
      p.dashCooldown = 0;
      emitirPala(state, boss.x + boss.w / 2, boss.y + boss.h / 2);
      sonido(state, "golpe");
      sacudir(state, 6, 0.14);
      state.flash = 0.08;
      state.flashColor = p.hasPowerup ? 0xc084fc : 0xffd23c;

      if (boss.hp <= 3 && boss.fase === 1) {
        boss.fase = 2;
        state.hintTimer = 4.5;
        state.hintTextMsg = p.hasPowerup
          ? "¡FASE II DESATADA! Tu Guadaña Consagrada perfora su coraza"
          : "¡FASE II! LA PALA REBOTA — Usá la Guadaña Consagrada o Pisotón";
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
      state.hintTextMsg = "¡LA PALA REBOTA! Usá la Guadaña Consagrada o Pisotón";
    }
  }
}

function actualizarMinijefe(state, dt) {
  const p = state.player;
  const reglas = state.data.game.rules;

  for (const mb of (state.minibosses || [])) {
    if (!mb.alive) {
      continue;
    }
    if (p.x + p.w >= mb.minX - 64 && p.x <= mb.maxX + 64) {
      mb.engaged = true;
    }
    mb.invuln = Math.max(0, mb.invuln - dt);
    mb.timer -= dt;

    if (mb.estado === "patrulla") {
      mb.x += mb.dir * 75 * dt;
      if (mb.x <= mb.minX) {
        mb.x = mb.minX;
        mb.dir = 1;
      } else if (mb.x + mb.w >= mb.maxX) {
        mb.x = mb.maxX - mb.w;
        mb.dir = -1;
      }
      if (mb.timer <= 0 && Math.abs((p.x + p.w / 2) - (mb.x + mb.w / 2)) < 360) {
        mb.estado = "telegrafo";
        mb.dir = p.x >= mb.x ? 1 : -1;
        mb.timer = 0.55;
        sacudir(state, 4, 0.12);
      }
    } else if (mb.estado === "telegrafo") {
      if (mb.timer <= 0) {
        mb.estado = "carga";
        mb.timer = 1.05;
        sonido(state, "onda");
        sacudir(state, 6, 0.16);
      }
    } else if (mb.estado === "carga") {
      mb.x += mb.dir * 235 * dt;
      let chocoBorde = false;
      if (mb.x <= mb.minX) {
        mb.x = mb.minX;
        chocoBorde = true;
      } else if (mb.x + mb.w >= mb.maxX) {
        mb.x = mb.maxX - mb.w;
        chocoBorde = true;
      }
      if (chocoBorde || mb.timer <= 0) {
        mb.estado = "cansado";
        mb.timer = 1.65;
        sacudir(state, 7, 0.18);
      }
    } else if (mb.estado === "cansado") {
      if (mb.timer <= 0) {
        mb.estado = "patrulla";
        mb.timer = 1.7;
      }
    }

    if (!solapan(p, mb)) {
      continue;
    }

    const vieneDeArriba = p.vy > 0 && p.y + p.h - mb.y <= 24;
    if (vieneDeArriba && mb.invuln <= 0) {
      mb.hp -= 1;
      mb.invuln = 0.65;
      p.vy = -reglas.rebote_enemigo * 0.92;
      const empujonDir = (p.x + p.w / 2) < (mb.x + mb.w / 2) ? -1 : 1;
      p.vx = empujonDir * 230;
      p.onGround = false;
      p.onPlatform = null;
      p.invuln = 0.35;
      p.airDash = reglas.dash_usos_aire;
      p.dashCooldown = 0;
      if (mb.estado === "patrulla") {
        mb.estado = "telegrafo";
        mb.dir = p.x >= mb.x ? 1 : -1;
        mb.timer = 0.45;
      }
      emitirPala(state, mb.x + mb.w / 2, mb.y + 12);
      sonido(state, "stomp");
      sacudir(state, 7, 0.18);
      state.flash = 0.09;
      state.flashColor = 0xffd23c;
      if (mb.hp <= 0) {
        mb.alive = false;
        emitirMeta(state, mb.x + mb.w / 2, mb.y + mb.h / 2);
        sonido(state, "meta");
        state.hintTimer = 4.2;
        state.hintTextMsg = "¡EL CARCELERO CAYÓ! El sello de la Guadaña Consagrada se ha roto";
      }
    } else if (p.invuln <= 0 && mb.alive) {
      dañar(state, false);
      return;
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
    const limite = boss.minX - 3 * 32;
    if (p.x + p.w > limite && p.x <= boss.maxX + 32) {
      boss.engaged = true;
      if (state.respawnX === state.level.spawn.x) {
        state.respawnX = limite;
        state.respawnY = state.level.spawn.y;
        state.hintTimer = 4.0;
        state.hintTextMsg = "PUNTO DE CONTROL · LA ANTESALA DEL CUSTODIO";
        sonido(state, "ui");
      }
    }
    boss.invuln = Math.max(0, boss.invuln - dt);
    boss.vulnerableTimer = Math.max(0, (boss.vulnerableTimer || 0) - dt);
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
        boss.vulnerableTimer = 1.5;
        boss.attackTimer = 1.6;
        crearOndasJefe(state, boss);
      }
    } else {
      if (Math.abs((p.x + p.w / 2) - (boss.x + boss.w / 2)) > 50) {
        boss.dir = p.x > boss.x ? 1 : -1;
        const velPatrulla = boss.vulnerableTimer > 0 ? 22 : (boss.fase >= 2 ? 62 : 48);
        boss.x += boss.dir * velPatrulla * dt;
        boss.x = limitar(boss.x, boss.minX, boss.maxX - boss.w);
      }

      if (boss.attackTimer <= 0) {
        if (boss.fase >= 2 && Math.random() < 0.48) {
          boss.charging = true;
          boss.dir = p.x > boss.x ? 1 : -1;
          boss.attackTimer = 1.2;
          sonido(state, "onda");
          sacudir(state, 5, 0.16);
        } else {
          crearOndasJefe(state, boss);
          boss.vulnerableTimer = 1.4;
          boss.attackTimer = boss.fase >= 2 ? 1.8 : 2.3;
        }
      }
    }

    if (!solapan(p, boss)) {
      continue;
    }

    const vieneDeArriba = p.vy > 0 && p.y + p.h - boss.y <= 24;
    if (vieneDeArriba && boss.invuln <= 0) {
      boss.hp -= 1;
      boss.invuln = 0.75;
      p.vy = -reglas.rebote_enemigo * 0.92;
      const empujonDir = (p.x + p.w / 2) < (boss.x + boss.w / 2) ? -1 : 1;
      p.vx = empujonDir * 245;
      p.onGround = false;
      p.onPlatform = null;
      p.invuln = 0.42;
      p.airDash = reglas.dash_usos_aire;
      p.dashCooldown = 0;
      if (!boss.charging && boss.hp > 0) {
        boss.attackTimer = Math.min(boss.attackTimer, 0.35);
      }
      emitirPala(state, boss.x + boss.w / 2, boss.y + 16);
      sonido(state, "stomp");
      sacudir(state, 8, 0.2);
      state.flash = 0.1;
      state.flashColor = 0xffd23c;

      if (boss.hp <= 3 && boss.fase === 1) {
        boss.fase = 2;
        state.hintTimer = 4.5;
        state.hintTextMsg = p.hasPowerup
          ? "¡FASE II DESATADA! Tu Guadaña Consagrada perfora su coraza"
          : "¡FASE II! LA PALA REBOTA — Usá la Guadaña Consagrada o Pisotón";
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
  const reglas = state.data.game.rules;
  const almasPorVida = reglas.almas_por_vida || 10;
  const vidasMax = reglas.vidas_maximas || 5;

  for (const alma of state.souls) {
    if (alma.collected || !solapan(p, alma)) {
      continue;
    }
    alma.collected = true;
    state.levelSouls += 1;
    state.almasVidaAcumuladas = (state.almasVidaAcumuladas || 0) + 1;
    if (state.almasVidaAcumuladas >= almasPorVida) {
      state.almasVidaAcumuladas -= almasPorVida;
      if (state.lives < vidasMax) {
        state.lives += 1;
        state.hintTimer = 3.2;
        state.hintTextMsg = "¡RELICARIO DE ALMAS COMPLETO! +1 VIDA CONSAGRADA";
      }
    }
    emitirAlma(state, alma.x + alma.w / 2, alma.y + alma.h / 2);
    sonido(state, "alma");
  }
}

function siguienteNivel(state) {
  if (state.modoPartida !== "campania") {
    state.status = state.modoPartida === "tutorial" ? "tutorial_completado" : "sala_completada";
    return;
  }
  state.totalSouls += state.levelSouls;
  if (state.levelIndex + 1 >= state.activeLevels.length) {
    state.status = "victoria";
    return;
  }
  cargarNivel(state, state.levelIndex + 1, true);
}

function iniciarModoSeleccionado(state) {
  const modos = ["campania", "tutorial", "salas"];
  state.modoPartida = modos[state.menuModoIndice] || "campania";
  if (state.modoPartida === "salas") {
    const cantidad = (state.data.rooms || []).length;
    state.menuSalaIndice = cantidad ? ((state.menuSalaIndice % cantidad) + cantidad) % cantidad : 0;
  }
  state.totalSouls = 0;
  state.totalTime = 0;
  cargarNivel(state, state.modoPartida === "salas" ? state.menuSalaIndice : 0, false);
}

function reiniciarJuego(state) {
  state.totalSouls = 0;
  state.totalTime = 0;
  cargarNivel(state, state.modoPartida === "salas" ? state.menuSalaIndice : 0, false);
}

function volverAlTitulo(state) {
  state.status = "titulo";
  state.modoPartida = "campania";
  state.menuModoIndice = 0;
  state.menuSalaIndice = 0;
  state.totalSouls = 0;
  state.totalTime = 0;
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
  if (justo(state, "reiniciar") && state.status !== "titulo") {
    reiniciarJuego(state);
  }
  if (justo(state, "silencio")) {
    state.muted = !state.muted;
  }
  if (state.status === "titulo") {
    if (justo(state, "izquierda")) {
      state.menuModoIndice = (state.menuModoIndice + 2) % 3;
      sonido(state, "ui");
    }
    if (justo(state, "derecha")) {
      state.menuModoIndice = (state.menuModoIndice + 1) % 3;
      sonido(state, "ui");
    }
    if (state.menuModoIndice === 2 && (state.data.rooms || []).length) {
      if (justo(state, "arriba")) {
        state.menuSalaIndice = (state.menuSalaIndice + state.data.rooms.length - 1) % state.data.rooms.length;
        sonido(state, "ui");
      }
      if (justo(state, "abajo")) {
        state.menuSalaIndice = (state.menuSalaIndice + 1) % state.data.rooms.length;
        sonido(state, "ui");
      }
    }
    if (justo(state, "enter")) {
      iniciarModoSeleccionado(state);
      sonido(state, "meta");
    }
    return;
  }
  if (justo(state, "enter") || justo(state, "salto") || justo(state, "ataque")) {
    if (state.status === "nivel_completado") {
      siguienteNivel(state);
    } else if (["tutorial_completado", "sala_completada", "victoria"].includes(state.status)) {
      volverAlTitulo(state);
    } else if (state.status === "derrota") {
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

  const jefeActivo = (state.bosses || []).find((b) => b.alive && b.engaged) ||
                     (state.bosses || []).find((b) => b.alive && Math.abs(p.x - b.x) < 480);
  const minijefeActivo = (state.minibosses || []).find((m) => m.alive && m.engaged) ||
                         (state.minibosses || []).find((m) => m.alive && Math.abs(p.x - m.x) < 420);
  const entidadJefe = jefeActivo || minijefeActivo;

  // Textos
  const totalNiveles = (state.activeLevels || obtenerNivelesActivos(state)).length || 1;
  if (state.modoPartida === "tutorial") {
    state.txtNivel.text = "TUTORIAL — " + state.level.name.toUpperCase();
    state.txtNivelSub.text = "RITUAL DEL SEPULTURERO";
  } else if (state.modoPartida === "salas") {
    state.txtNivel.text = `SALA ${state.menuSalaIndice + 1}/${(state.data.rooms || []).length} — ${state.level.name.toUpperCase()}`;
    state.txtNivelSub.text = "DESAFÍO DE PRUEBA";
  } else {
    state.txtNivel.text = `NIVEL ${state.levelIndex + 1}/${totalNiveles} — ${state.level.name.toUpperCase()}`;
    state.txtNivelSub.text = "CRIPTA DE LOS CAÍDOS";
  }
  state.txtNivel.style.fill = est.oro;

  
  state.txtNivelSub.style.fill = est.secundario;

  state.txtAlmas.text = `ALMAS ${state.levelSouls}/${state.level.total_souls}`;
  state.txtAlmas.style.fill = est.alma;

  state.txtVidas.text = "VIDAS";
  state.txtVidas.style.fill = est.carmesi;

  state.txtTiempo.text = `${state.levelTime.toFixed(1)}s`;
  state.txtTiempo.style.fill = est.texto;

  state.txtDash.text = listo ? "DASH LISTO" : "RECARGANDO...";
  state.txtDash.style.fill = listo ? est.dash : 0x8b95a5;

  if (p.hasPowerup) {
    state.txtArma.text = "GUADAÑA [Z/J]";
    state.txtArma.style.fill = 0xc084fc;
  } else if (p.hasShovel) {
    state.txtArma.text = "PALA [Z/J]";
    state.txtArma.style.fill = est.oro;
  } else {
    state.txtArma.text = "SIN ARMA";
    state.txtArma.style.fill = 0x8b95a5;
  }

  state.txtEstilo.text = `[F2] ${est.nombre.toUpperCase().split(" ")[0]}`;
  state.txtEstilo.style.fill = est.secundario;

  if (entidadJefe) {
    state.txtBoss.visible = enJuego;
    if (jefeActivo) {
      state.txtBoss.text = `EL CUSTODIO DEL OSARIO (FASE ${jefeActivo.fase >= 2 ? "II" : "I"})`;
      state.txtBoss.style.fill = jefeActivo.fase >= 2 ? est.carmesi : est.oro;
    } else {
      state.txtBoss.text = `EL CARCELERO DEL OSARIO (${minijefeActivo.estado.toUpperCase()})`;
      state.txtBoss.style.fill = minijefeActivo.estado === "cansado" ? 0x46dcd2 : est.oro;
    }
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
  ocultarPoolSprites(state.hudPool);

  if (enJuego) {
    const usarSpritesHud = tieneSprites() && state.hudSprites;
    if (usarSpritesHud) {
      colocarSprite(state, state.hudSprites, state.hudPool, "hud_panel", "barra_hud.png", 0, 0, ANCHO, 72);
    } else {
      state.hudG.beginFill(est.panelBg, 0.94);
      state.hudG.drawRect(0, 0, ANCHO, 72);
      state.hudG.endFill();
      state.hudG.lineStyle(2, est.borde, 0.9);
      state.hudG.moveTo(0, 70);
      state.hudG.lineTo(ANCHO, 70);
      state.hudG.lineStyle(0, 0, 0);
    }

    // Divisores de filigrana entre las 3 zonas (x = 280 y x = 680)
    for (const divX of [280, 680]) {
      state.hudG.lineStyle(1, est.borde, 0.55);
      state.hudG.moveTo(divX, 8);
      state.hudG.lineTo(divX, 64);
      state.hudG.lineStyle(0, 0, 0);

      state.hudG.beginFill(est.oro, 0.8);
      state.hudG.moveTo(divX, 32);
      state.hudG.lineTo(divX + 3, 36);
      state.hudG.lineTo(divX, 40);
      state.hudG.lineTo(divX - 3, 36);
      state.hudG.closePath();
      state.hudG.endFill();
    }

    // --- ZONA IZQUIERDA: Vidas + Manto del Farol + Dash ---
    const maxCorazones = Math.max(3, state.lives);
    for (let i = 0; i < maxCorazones; i += 1) {
      const vx = 78 + i * 24;
      const lleno = i < state.lives;
      if (usarSpritesHud) {
        colocarSprite(
          state,
          state.hudSprites,
          state.hudPool,
          `heart_${i}`,
          lleno ? "corazon_lleno.png" : "corazon_vacio.png",
          vx - 9,
          9,
          18,
          18
        );
      } else {
        state.hudG.lineStyle(1, lleno ? est.oro : 0x3d3545, 0.8);
        state.hudG.beginFill(lleno ? est.carmesi : 0x18121a, 0.9);
        state.hudG.moveTo(vx - 7, 14);
        state.hudG.lineTo(vx, 7);
        state.hudG.lineTo(vx + 7, 14);
        state.hudG.lineTo(vx, 23);
        state.hudG.closePath();
        state.hudG.endFill();
        state.hudG.lineStyle(0, 0, 0);
      }
    }
    if (state.escudoFarol) {
      const mx = 78 + maxCorazones * 24;
      if (usarSpritesHud) {
        colocarSprite(state, state.hudSprites, state.hudPool, "heart_manto", "corazon_manto.png", mx - 9, 9, 18, 18);
      } else {
        state.hudG.lineStyle(1, 0xffffff, 0.9);
        state.hudG.beginFill(0xe5b842, 0.95);
        state.hudG.drawCircle(mx, 17, 7);
        state.hudG.endFill();
        state.hudG.lineStyle(0, 0, 0);
      }
    }

    if (usarSpritesHud) {
      colocarSprite(state, state.hudSprites, state.hudPool, "icon_dash", "icono_dash.png", 20, 32, 16, 16);
      const iconoArma = p.hasPowerup ? "icono_guadana.png" : "icono_pala.png";
      colocarSprite(
        state,
        state.hudSprites,
        state.hudPool,
        "icon_arma",
        iconoArma,
        696,
        40,
        18,
        18,
        false,
        p.hasShovel || p.hasPowerup ? 1.0 : 0.35
      );
      colocarSprite(state, state.hudSprites, state.hudPool, "icon_alma", "icono_alma.png", 696, 12, 16, 16);
    }

    // Gauge de Dash
    state.hudG.beginFill(0x0a0d14, 0.92);
    state.hudG.drawRect(20, 52, 240, 11);
    state.hudG.endFill();
    state.hudG.lineStyle(1, est.borde, 0.75);
    state.hudG.drawRect(20, 52, 240, 11);
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
      state.hudG.drawRect(22, 54, dashW, 7);
      state.hudG.endFill();
      if (listo) {
        state.hudG.beginFill(0xffffff, 0.45);
        state.hudG.drawRect(22, 54, dashW, 2);
        state.hudG.endFill();
      }
    }

    // --- ZONA CENTRAL: Boss Bar / MiniJefe Bar o Rosario de 10 cuentas ---
    if (entidadJefe) {
      const maxHp = entidadJefe.maxHp || 6;
      const segW = Math.floor(310 / maxHp) - 6;
      const segH = 14, gap = 6;
      const totalW = maxHp * segW + (maxHp - 1) * gap;
      const startX = Math.round(480 - totalW / 2);
      const startY = 38;

      for (let s = 0; s < maxHp; s += 1) {
        const sx = startX + s * (segW + gap);
        const activo = s < entidadJefe.hp;
        const esFase2 = Boolean(jefeActivo && jefeActivo.fase >= 2);
        const esVulnerable = Boolean(minijefeActivo && minijefeActivo.estado === "cansado");

        state.hudG.lineStyle(1, activo ? (esVulnerable ? 0x46dcd2 : (esFase2 ? 0xff4444 : est.oro)) : 0x282030, 0.9);
        state.hudG.beginFill(activo ? (esVulnerable ? 0x1f9ea8 : (esFase2 ? 0xd22030 : est.bossColor)) : 0x120c16, 0.95);
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
    } else {
      // Rosario de 10 cuentas de ánima en la parte baja central del HUD
      const cuentas = (state.almasVidaAcumuladas || 0) % 10;
      const startX = 480 - (9 * 14) / 2;
      for (let c = 0; c < 10; c += 1) {
        const cx = startX + c * 14;
        const activa = c < cuentas;
        state.hudG.lineStyle(1, activa ? est.oro : 0x3b3546, 0.85);
        state.hudG.beginFill(activa ? est.alma : 0x14101c, 0.95);
        state.hudG.drawCircle(cx, 56, activa ? 4 : 3);
        state.hudG.endFill();
        state.hudG.lineStyle(0, 0, 0);
      }
    }
  }

  const mostrarPista = state.hintTimer > 0 && state.status === "jugando";
  state.hintBg.visible = mostrarPista;
  state.hintText.visible = mostrarPista;
  if (mostrarPista) {
    state.hintBg.clear();
    state.hintBg.beginFill(0x080c16, 0.92);
    state.hintBg.drawRect(40, 78, 880, 48);
    state.hintBg.endFill();
    state.hintBg.lineStyle(2, est.borde, 0.9);
    state.hintBg.drawRect(40, 78, 880, 48);
    state.hintBg.lineStyle(0, 0, 0);
    state.hintBg.beginFill(est.oro, 1);
    state.hintBg.drawRect(40, 78, 5, 48);
    state.hintBg.drawRect(915, 78, 5, 48);
    state.hintBg.endFill();
    state.hintText.text = state.hintTextMsg || ("PISTA · " + state.level.hint);
    state.hintText.x = 58;
    state.hintText.y = 91;
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
      const modos = ["CAMPAÑA", "TUTORIAL", "SALAS DE PRUEBA"];
      const modoElegido = modos[state.menuModoIndice] || modos[0];
      const salaElegida = (state.data.rooms || [])[state.menuSalaIndice];
      const detalleSala = state.menuModoIndice === 2 && salaElegida
        ? `\nSala ${state.menuSalaIndice + 1}/${state.data.rooms.length}: ${salaElegida.name}`
        : "";
      state.overlayInfo.text =
        "MODO: " + modoElegido + detalleSala + "\n\n" +
        "←/→ elegir modo   ·   ↑/↓ elegir sala   ·   ENTER comenzar\n" +
        "F2 estilo: " + estNom.toUpperCase() + "   ·   M silenciar";
      state.overlayInfo.visible = true;
    } else if (state.status === "tutorial_completado") {
      state.overlayTitle.text = "¡Ritual completado!";
      state.overlayTitle.style.fill = 0xe8c15a;
      state.overlaySub.text = "ENTER para volver a la portada";
      state.overlaySub.style.fill = 0xf5f5f5;
    } else if (state.status === "sala_completada") {
      state.overlayTitle.text = "Desafío completado";
      state.overlayTitle.style.fill = 0xe8c15a;
      state.overlaySub.text = "ENTER para volver a la portada";
      state.overlaySub.style.fill = 0xf5f5f5;
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
  const fx = state.fxG || g;
  const p = state.paleta;
  const tiempo = state.totalTime;
  const tema = (state.level && state.level.theme) || "camposanto";
  const usarSprites = tieneSprites() && state.worldSprites;

  g.clear();
  if (state.fxG) state.fxG.clear();
  for (const k of Object.keys(state.worldPool || {})) {
    if (k !== "__level_bg__" && state.worldPool[k]) {
      state.worldPool[k].visible = false;
    }
  }

  const f4 = (Math.floor(tiempo * 7) % 4) + 1;
  const f6 = (Math.floor(tiempo * 10) % 6) + 1;

  // 1. Plataformas móviles y sus cadenas dinámicas ancladas al travesaño superior
  for (let i = 0; i < (state.platforms || []).length; i += 1) {
    const plat = state.platforms[i];
    if (plat.axis !== "h" && plat.axis !== "H") {
      const topeY = Math.max(6, plat.origin_y - plat.amplitude - 16);
      g.lineStyle(2, 0x4a5062, 0.9);
      for (const cx of [plat.x + 14, plat.x + plat.w - 14]) {
        for (let y = plat.y - 4; y >= topeY; y -= 8) {
          g.drawRect(cx - 2, y, 4, 5);
        }
      }
      g.lineStyle(0, 0, 0);
    }
    if (usarSprites) {
      colocarSprite(
        state,
        state.worldSprites,
        state.worldPool,
        `plat_${i}`,
        `plataformamovil_${tema}.png`,
        plat.x,
        plat.y,
        plat.w,
        plat.h
      );
    } else {
      g.beginFill(0x282c37, 1);
      g.drawRect(plat.x, plat.y, plat.w, plat.h);
      g.endFill();
      g.beginFill(0x5a6375, 1);
      g.drawRect(plat.x, plat.y, plat.w, 4);
      g.endFill();
    }
  }

  // 2. Pinchos (si usamos sprites horneados)
  if (usarSprites) {
    for (let i = 0; i < (state.level.hazards || []).length; i += 1) {
      const pel = state.level.hazards[i];
      colocarSprite(state, state.worldSprites, state.worldPool, `haz_${i}`, "pinchos.png", pel.x, pel.y, pel.w, pel.h);
    }
    const meta = state.level.goal;
    colocarSprite(
      state,
      state.worldSprites,
      state.worldPool,
      "goal_door",
      "puerta.png",
      meta.x + meta.w / 2 - 21,
      meta.y + meta.h - 58,
      42,
      58
    );
  }

  // 3. Palas recogibles (W)
  for (let i = 0; i < (state.palas || []).length; i += 1) {
    const pala = state.palas[i];
    if (pala.collected) continue;
    const flot = Math.sin(tiempo * 5 + pala.x * 0.05) * 3;
    const cx = pala.x + pala.w / 2;
    const cy = pala.y + pala.h / 2 + flot;
    g.beginFill(0xffd23c, 0.14);
    g.drawCircle(cx, cy, 18);
    g.endFill();
    if (usarSprites) {
      colocarSprite(state, state.worldSprites, state.worldPool, `pala_${i}`, `pala_${f4}.png`, pala.x, pala.y + flot, pala.w, pala.h);
    } else {
      g.lineStyle(3, 0x8a6234, 1);
      g.moveTo(cx - 4, cy - 8);
      g.lineTo(cx + 4, cy + 8);
      g.lineStyle(0, 0, 0);
      g.beginFill(0xc0c8d8, 1);
      g.drawRect(cx + 2, cy + 5, 8, 6);
      g.endFill();
    }
  }

  // 4. Reliquia de Dash (D)
  for (let i = 0; i < (state.powerupsDash || []).length; i += 1) {
    const pud = state.powerupsDash[i];
    if (pud.collected) continue;
    const flot = Math.sin(tiempo * 5 + pud.x * 0.05) * 3;
    const cx = pud.x + pud.w / 2;
    const cy = pud.y + pud.h / 2 + flot;
    g.beginFill(0x46dcd2, 0.18);
    g.drawCircle(cx, cy, 20);
    g.endFill();
    if (usarSprites) {
      colocarSprite(state, state.worldSprites, state.worldPool, `pud_${i}`, `powerupdash_${f4}.png`, pud.x, pud.y + flot, pud.w, pud.h);
    } else {
      g.lineStyle(2, 0x46dcd2, 1);
      g.drawCircle(cx, cy, 10);
      g.lineStyle(0, 0, 0);
    }
  }

  // 5. Guadaña Consagrada (X) + Jaula de sello si el Carcelero vive
  const carceleroVivo = (state.minibosses || []).some((mb) => mb.alive);
  for (let i = 0; i < (state.powerups || []).length; i += 1) {
    const pu = state.powerups[i];
    if (pu.collected) continue;
    const flot = Math.sin(tiempo * 5 + pu.x * 0.05) * 3;
    const cx = pu.x + pu.w / 2;
    const cy = pu.y + pu.h / 2 + flot;
    g.beginFill(0xa855f7, 0.22);
    g.drawCircle(cx, cy, 20);
    g.endFill();
    if (usarSprites) {
      colocarSprite(state, state.worldSprites, state.worldPool, `pur_${i}`, `poweruprango_${f4}.png`, pu.x, pu.y + flot, pu.w, pu.h);
    } else {
      g.lineStyle(2, 0xc084fc, 1);
      g.drawCircle(cx, cy, 10);
      g.lineStyle(0, 0, 0);
    }
    if (carceleroVivo) {
      fx.lineStyle(2, 0x8a151b, 0.9);
      fx.drawRect(pu.x - 4, pu.y - 4, pu.w + 8, pu.h + 8);
      for (let bx = pu.x; bx <= pu.x + pu.w; bx += 8) {
        fx.moveTo(bx, pu.y - 4);
        fx.lineTo(bx, pu.y + pu.h + 4);
      }
      fx.lineStyle(0, 0, 0);
    }
  }

  // 6. Faroles Checkpoint (F)
  for (let i = 0; i < (state.checkpoints || []).length; i += 1) {
    const cp = state.checkpoints[i];
    if (cp.active) {
      const llama = Math.sin(tiempo * 8 + cp.x) * 2;
      g.beginFill(0xffd23c, 0.16);
      g.drawCircle(cp.x + cp.w / 2, cp.y + 10 + llama, 24);
      g.endFill();
    }
    if (usarSprites) {
      const texCp = cp.active ? `farolcheckpoint_on_${f4}.png` : "farolcheckpoint_off.png";
      colocarSprite(state, state.worldSprites, state.worldPool, `cp_${i}`, texCp, cp.x, cp.y, cp.w, cp.h);
    } else if (cp.active) {
      g.beginFill(0x38bdf8, 0.5);
      g.drawCircle(cp.x + cp.w / 2, cp.y + 6, 7);
      g.endFill();
    }
  }

  // 7. Almas (o)
  for (let i = 0; i < state.souls.length; i += 1) {
    const alma = state.souls[i];
    if (alma.collected) continue;
    const flotacion = Math.sin(tiempo * 5 + alma.x * 0.03) * 3;
    const cx = alma.x + alma.w / 2;
    const cy = alma.y + alma.h / 2 + flotacion;
    g.beginFill(0xffd23c, 0.14);
    g.drawCircle(cx, cy, 16);
    g.endFill();
    if (usarSprites) {
      colocarSprite(
        state,
        state.worldSprites,
        state.worldPool,
        `alma_${i}`,
        `alma_${f4}.png`,
        cx - 12,
        cy - 12,
        24,
        24
      );
    } else {
      g.beginFill(0xffd23c, 1);
      g.drawEllipse(cx, cy, 7, 8);
      g.endFill();
    }
  }

  // 8. Enemigos (E)
  for (let i = 0; i < state.enemies.length; i += 1) {
    const enemigo = state.enemies[i];
    if (!enemigo.alive) continue;
    if (usarSprites) {
      colocarSprite(
        state,
        state.worldSprites,
        state.worldPool,
        `enemy_${i}`,
        `enemy_walk_${f4}.png`,
        enemigo.x,
        enemigo.y,
        enemigo.w,
        enemigo.h,
        enemigo.dir < 0
      );
    } else {
      const cx = enemigo.x + enemigo.w / 2;
      const cy = enemigo.y + enemigo.h / 2;
      g.beginFill(p.enemigo, 1);
      g.drawEllipse(cx, cy, enemigo.w / 2, enemigo.h / 2);
      g.endFill();
    }
  }

  // 9. Enemigos Melee (L)
  for (let i = 0; i < (state.enemiesMelee || []).length; i += 1) {
    const em = state.enemiesMelee[i];
    if (!em.alive) continue;
    if (usarSprites) {
      colocarSprite(
        state,
        state.worldSprites,
        state.worldPool,
        `emelee_${i}`,
        `enemymelee_walk_${f4}.png`,
        em.x,
        em.y,
        em.w,
        em.h,
        em.dir < 0
      );
    } else {
      const cx = em.x + em.w / 2;
      const cy = em.y + em.h / 2;
      g.beginFill(0x1a1215, 1);
      g.drawEllipse(cx, cy, em.w / 2, em.h / 2);
      g.endFill();
    }
  }

  // 10. MiniJefe (K - El Carcelero del Osario)
  for (let i = 0; i < (state.minibosses || []).length; i += 1) {
    const mb = state.minibosses[i];
    if (!mb.alive) continue;
    const parpadea = mb.invuln > 0 && Math.floor(tiempo * 20) % 2 === 0;
    if (!parpadea) {
      const tintMb = mb.estado === "cansado" ? 0x99f6e4 : (mb.estado === "telegrafo" ? 0xfca5a5 : 0xffffff);
      if (usarSprites) {
        colocarSprite(
          state,
          state.worldSprites,
          state.worldPool,
          `miniboss_${i}`,
          `minijefe_walk_${f4}.png`,
          mb.x,
          mb.y,
          mb.w,
          mb.h,
          mb.dir < 0,
          1,
          tintMb
        );
      } else {
        g.beginFill(mb.estado === "cansado" ? 0x2dd4bf : 0x5c2434, 1);
        g.drawRoundedRect(mb.x, mb.y, mb.w, mb.h, 5);
        g.endFill();
      }
    }
  }

  // 11. Jefe Final (B - El Custodio)
  for (let i = 0; i < (state.bosses || []).length; i += 1) {
    const boss = state.bosses[i];
    if (!boss.alive) continue;
    const parpadea = boss.invuln > 0 && Math.floor(tiempo * 20) % 2 === 0;
    if (!parpadea) {
      const tintBoss = boss.fase >= 2 ? 0xffb4b4 : 0xffffff;
      if (usarSprites) {
        colocarSprite(
          state,
          state.worldSprites,
          state.worldPool,
          `boss_${i}`,
          `jefe_walk_${f4}.png`,
          boss.x,
          boss.y,
          boss.w,
          boss.h,
          boss.dir < 0,
          1,
          tintBoss
        );
      } else {
        g.beginFill(boss.fase >= 2 ? 0x2e111a : 0x1b1322, 1);
        g.drawRoundedRect(boss.x + 4, boss.y + 12, boss.w - 8, boss.h - 14, 6);
        g.endFill();
      }
    }
  }

  // 12. Ondas de choque del Jefe
  for (let i = 0; i < (state.bossWaves || []).length; i += 1) {
    const onda = state.bossWaves[i];
    if (usarSprites) {
      colocarSprite(
        state,
        state.worldSprites,
        state.worldPool,
        `wave_${i}`,
        "onda_jefe.png",
        onda.x,
        onda.y,
        onda.w,
        onda.h,
        onda.dir < 0
      );
    } else {
      g.beginFill(0xd8c29a, 0.7);
      g.drawEllipse(onda.x + onda.w / 2, onda.y + onda.h / 2, onda.w / 2, onda.h / 2);
      g.endFill();
    }
  }

  // 13. Jugador (El Sepulturero)
  const jugador = state.player;
  const estiloWeb = ESTILOS_GOTICOS_WEB[state.estiloActual] || ESTILOS_GOTICOS_WEB.monastico;
  const parpadea = jugador.invuln > 0 && Math.floor(tiempo * 16) % 2 === 0;
  if (!parpadea) {
    const jx = jugador.x;
    const jy = jugador.y;
    const centroX = jx + jugador.w / 2;
    const dir = jugador.dir;

    // Halo cálido de la linterna del Sepulturero
    const lx = jx + (dir > 0 ? 22 : 2);
    const ly = jy + 18 + Math.sin(tiempo * 6) * 2;
    g.beginFill(estiloWeb.oro || 0xffd27a, 0.08);
    g.drawCircle(lx, ly, 30);
    g.endFill();
    g.beginFill(estiloWeb.oro || 0xffd27a, 0.16);
    g.drawCircle(lx, ly, 15);
    g.endFill();

    if (usarSprites) {
      let pose = "idle";
      let frameIdx = f4;
      if (jugador.dashTime > 0) {
        pose = "dash";
        frameIdx = (Math.floor(tiempo * 15) % 3) + 1;
      } else if (jugador.attackTimer > 0) {
        pose = "ataque";
        frameIdx = (Math.floor((0.20 - jugador.attackTimer) / 0.07) % 3) + 1;
      } else if (!jugador.onGround) {
        pose = jugador.vy < 0 ? "jump" : "caida";
        frameIdx = (Math.floor(tiempo * 8) % 2) + 1;
      } else if (Math.abs(jugador.vx) > 10) {
        pose = "run";
        frameIdx = f6;
      }
      const sufijoArma = jugador.hasShovel ? "" : "_sin_pala";
      const sufijoDir = dir < 0 ? "_izq" : "";
      const archivoJugador = `jugador_${pose}${sufijoDir}${sufijoArma}_${frameIdx}.png`;
      colocarSprite(
        state,
        state.worldSprites,
        state.worldPool,
        "player_main",
        archivoJugador,
        jx - 4,
        jy - 2,
        32,
        32,
        false
      );
    } else {
      g.beginFill(p.jugador, 1);
      g.drawRoundedRect(jx + 4, jy + 12, 16, 14, 3);
      g.endFill();
      g.beginFill(0xf0c9a0, 1);
      g.drawCircle(centroX, jy + 9, 7);
      g.endFill();
    }
  }

  // 14. Arco de ataque cuerpo a cuerpo (Pala / Guadaña Consagrada)
  if (jugador.attackTimer > 0) {
    const alcance = jugador.hasPowerup ? 76 : 36;
    const alto = jugador.hasPowerup ? 42 : 26;
    const ax = jugador.dir > 0 ? jugador.x + jugador.w - 4 : jugador.x - alcance + 4;
    const ay = jugador.y + jugador.h / 2 - alto / 2;
    if (usarSprites) {
      const fGolpe = Math.min(3, Math.max(1, Math.floor((0.20 - jugador.attackTimer) / 0.065) + 1));
      const texGolpe = jugador.dir > 0 ? `golpe_der_${fGolpe}.png` : `golpe_izq_${fGolpe}.png`;
      colocarSprite(
        state,
        state.worldSprites,
        state.worldPool,
        "player_slash",
        texGolpe,
        ax,
        ay,
        alcance,
        alto,
        false,
        0.92,
        jugador.hasPowerup ? 0xc084fc : 0xffffff
      );
    }
    fx.lineStyle(3, jugador.hasPowerup ? 0xc084fc : 0xffe9b0, 0.85);
    fx.moveTo(ax, ay + alto);
    fx.quadraticCurveTo(ax + alcance / 2, ay, ax + alcance, ay + alto / 2);
    fx.lineStyle(0, 0, 0);
  }

  for (const particula of state.particles) {
    const proporcion = Math.max(0, particula.vida / particula.vidaInicial);
    fx.beginFill(particula.color, proporcion);
    fx.drawCircle(particula.x, particula.y, Math.max(1, particula.tamano * proporcion));
    fx.endFill();
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
    actualizarMinijefe(state, dt);
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
      const jefeVivo = (state.bosses || []).some((b) => b.alive && b.engaged);
      if (jefeVivo) {
        state.hintTimer = 2.0;
        state.hintTextMsg = "LA SALIDA ESTÁ SELLADA · DERROTÁ AL CUSTODIO";
      } else {
        emitirMeta(state, state.level.goal.x + 10, state.level.goal.y + 10);
        sonido(state, "meta");
        if (state.modoPartida !== "campania") {
          state.status = state.modoPartida === "tutorial" ? "tutorial_completado" : "sala_completada";
        } else if (state.levelIndex + 1 >= state.activeLevels.length) {
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
