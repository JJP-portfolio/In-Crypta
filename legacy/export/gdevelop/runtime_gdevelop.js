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
    izquierda: tecla("Left") || tecla("KeyA"),
    derecha: tecla("Right") || tecla("KeyD"),
    salto: tecla("Space"),
    dash: tecla("Shift") || tecla("LShift") || tecla("KeyX"),
    pausa: tecla("KeyP"),
    reiniciar: tecla("KeyR"),
    enter: tecla("Enter") || tecla("Return"),
    silencio: tecla("KeyM"),
  };
}

function justo(state, nombre) {
  return Boolean(state.keys[nombre]) && !state.prev[nombre];
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
    txtAlmas: null,
    txtVidas: null,
    txtTiempo: null,
    txtDash: null,
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

  state.txtNivel = crearTexto(state.hud, "", 22, 0xf5f5f5, 18, 12);
  state.txtAlmas = crearTexto(state.hud, "", 22, 0xffd23c, 480, 12);
  state.txtVidas = crearTexto(state.hud, "", 22, 0xd2414b, 690, 12);
  state.txtTiempo = crearTexto(state.hud, "", 20, 0x96d2f5, 842, 12);
  state.txtDash = crearTexto(state.hud, "DASH LISTO", 15, 0x46dcd2, 18, 34);

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
  state.player = {
    x: spawn.x,
    y: spawn.y,
    w: spawn.w,
    h: spawn.h,
    vx: 0,
    vy: 0,
    dir: 1,
    onGround: false,
    coyote: 0,
    jumpBuffer: 0,
    invuln: 0,
    dashTime: 0,
    dashCooldown: 0,
    dashDir: 1,
    airDash: reglas.dash_usos_aire,
  };
  state.particles = [];
  state.levelSouls = 0;
  state.levelTime = 0;
  state.hintTimer = 5;
  state.flash = 0;
  state.shakeTime = 0;
  state.shakeX = 0;
  state.shakeY = 0;
}

function cargarNivel(state, indice, conservarVidas) {
  state.levelIndex = indice;
  state.level = state.data.levels[indice];
  state.souls = state.level.souls.map((alma) => ({
    x: alma.x,
    y: alma.y,
    w: alma.w,
    h: alma.h,
    collected: false,
  }));
  state.enemies = state.level.enemies.map((enemy) => ({
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

function moverX(state, dx) {
  const p = state.player;
  p.x += dx;
  for (const solido of state.level.solids) {
    if (!solapan(p, solido)) {
      continue;
    }
    if (dx > 0) {
      p.x = solido.x - p.w;
    } else if (dx < 0) {
      p.x = solido.x + solido.w;
    }
    p.vx = 0;
    break;
  }
}

function moverY(state, dy) {
  const p = state.player;
  p.y += dy;
  for (const solido of state.level.solids) {
    if (!solapan(p, solido)) {
      continue;
    }
    if (dy > 0) {
      p.y = solido.y - p.h;
      p.onGround = true;
    } else if (dy < 0) {
      p.y = solido.y + solido.h;
    }
    p.vy = 0;
    break;
  }

  if (dy >= 0 && !p.onGround) {
    const sonda = { x: p.x, y: p.y + 1, w: p.w, h: p.h };
    for (const solido of state.level.solids) {
      if (solapan(sonda, solido)) {
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

  p.invuln = Math.max(0, p.invuln - dt);
  p.dashCooldown = Math.max(0, p.dashCooldown - dt);

  if (p.dashTime > 0) {
    p.dashTime = Math.max(0, p.dashTime - dt);
    p.vx = p.dashDir * reglas.dash_velocidad;
    p.vy = 0;
    moverX(state, p.vx * dt);
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
    p.coyote = 0;
    p.jumpBuffer = 0;
    emitirSalto(state, p.x + p.w / 2, p.y + p.h);
    sonido(state, "salto");
  }

  p.vy = Math.min(reglas.max_caida, p.vy + reglas.gravedad * dt);
  moverX(state, p.vx * dt);
  p.onGround = false;
  moverY(state, p.vy * dt);

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
  const objetivoX = limitar(p.x + p.w / 2 - ANCHO / 2, 0, maxX);
  const objetivoY = limitar(p.y + p.h / 2 - ALTO / 2, 0, maxY);

  if (instantanea) {
    state.camX = objetivoX;
    state.camY = objetivoY;
  } else {
    const factor = Math.min(1, 7 * dt);
    state.camX += (objetivoX - state.camX) * factor;
    state.camY += (objetivoY - state.camY) * factor;
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
  const spawn = state.level.spawn;
  p.x = spawn.x;
  p.y = spawn.y;
  p.vx = 0;
  p.vy = 0;
  p.onGround = false;
  p.coyote = 0;
  p.jumpBuffer = 0;
  p.invuln = state.data.game.rules.invulnerabilidad;
  p.dashTime = 0;
  p.dashCooldown = 0;
  p.airDash = state.data.game.rules.dash_usos_aire;
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

    const vieneDeArriba = p.vy > 0 && p.y + p.h - enemigo.y <= 18;
    if (vieneDeArriba) {
      enemigo.alive = false;
      p.vy = -reglas.rebote_enemigo;
      p.onGround = false;
      p.airDash = reglas.dash_usos_aire;
      p.dashCooldown = 0;
      emitirPala(state, enemigo.x + enemigo.w / 2, enemigo.y + enemigo.h / 2);
      sonido(state, "pala");
      sacudir(state, 6, 0.14);
    } else {
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
  if (justo(state, "enter")) {
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
  if (justo(state, "dash")) {
    intentarDash(state);
  }
}

function actualizarHud(state) {
  const enJuego = state.status !== "titulo";
  state.txtNivel.text = `NIVEL ${state.levelIndex + 1}/${state.data.levels.length} · ${state.level.name}`;
  state.txtAlmas.text = `ALMAS ${state.levelSouls}/${state.level.total_souls}`;
  state.txtVidas.text = "VIDAS";
  state.txtTiempo.text = `${state.levelTime.toFixed(1)}s`;

  const p = state.player;
  const listo =
    p.dashTime <= 0 &&
    p.dashCooldown <= 0 &&
    (p.onGround || p.airDash > 0);
  state.txtDash.text = listo ? "DASH LISTO" : "DASH...";
  state.txtDash.style.fill = listo ? state.paleta.dash : 0x6b7280;

  for (const texto of [
    state.txtNivel,
    state.txtAlmas,
    state.txtVidas,
    state.txtTiempo,
    state.txtDash,
  ]) {
    texto.visible = enJuego;
  }

  state.hudG.clear();
  if (enJuego) {
    state.hudG.beginFill(0x070a12, 0.78);
    state.hudG.drawRect(0, 0, ANCHO, 58);
    state.hudG.endFill();
    state.hudG.beginFill(0x8f7330, 0.8);
    state.hudG.drawRect(0, 56, ANCHO, 2);
    state.hudG.endFill();

    for (let i = 0; i < state.lives; i += 1) {
      const x = 758 + i * 20;
      state.hudG.beginFill(0xd2414b, 1);
      state.hudG.drawCircle(x - 4, 22, 5);
      state.hudG.drawCircle(x + 4, 22, 5);
      state.hudG.moveTo(x - 9, 24);
      state.hudG.lineTo(x, 37);
      state.hudG.lineTo(x + 9, 24);
      state.hudG.closePath();
      state.hudG.endFill();
      state.hudG.beginFill(0xff9aa3, 0.7);
      state.hudG.drawCircle(x - 5, 20, 1.5);
      state.hudG.endFill();
    }

    state.hudG.beginFill(0x1e2d37, 1);
    state.hudG.drawRect(120, 38, 90, 7);
    state.hudG.endFill();
    let progreso = 1;
    if (!listo) {
      progreso = Math.max(0, 1 - p.dashCooldown / state.data.game.rules.dash_cooldown);
      if (p.airDash <= 0 && p.dashCooldown <= 0) {
        progreso = 0;
      }
    }
    state.hudG.beginFill(listo ? state.paleta.dash : 0x6b7280, 1);
    state.hudG.drawRect(120, 38, Math.round(90 * progreso), 7);
    state.hudG.endFill();
  }

  const mostrarPista = state.hintTimer > 0 && state.status === "jugando";
  state.hintBg.visible = mostrarPista;
  state.hintText.visible = mostrarPista;
  if (mostrarPista) {
    state.hintBg.clear();
    state.hintBg.beginFill(0x080c16, 0.86);
    state.hintBg.drawRect(40, 64, 880, 54);
    state.hintBg.endFill();
    state.hintBg.beginFill(state.paleta.dash, 1);
    state.hintBg.drawRect(40, 64, 4, 54);
    state.hintBg.endFill();
    state.hintText.text = "PISTA  " + state.level.hint;
    state.hintText.x = 56;
    state.hintText.y = 72;
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
      state.overlayInfo.text =
        "Equipo 6\n" +
        "Ovelar Alejandro Ezequiel · Joaquín Cardiel Gomez · Jonathan Javier Pietracci\n\n" +
        "Referencias: Blasphemous · Castlevania · Ender Lilies\n\n" +
        "ENTER para entrar a la cripta   ·   M para silenciar";
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

  const jugador = state.player;
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

    g.beginFill(0x08070d, 0.65);
    g.drawEllipse(centroX, baseY - 1, 14, 4);
    g.endFill();

    g.lineStyle(3, 0x4e3a2a, 1);
    g.moveTo(centroX + dir * 6, jy + 8);
    g.lineTo(centroX + dir * 16, baseY - 3);
    g.lineStyle(0, 0, 0);
    g.beginFill(0xb9c4d0, 1);
    g.drawRect(centroX + dir * 14, baseY - 6, 9, 5);
    g.endFill();

    g.beginFill(0x151b2d, 1);
    g.drawRect(jx + 5, jy + 22, 5, 8);
    g.drawRect(jx + 14, jy + 22, 5, 8);
    g.endFill();
    g.beginFill(0x08070d, 1);
    g.drawRect(jx + 4, baseY - 3, 7, 3);
    g.drawRect(jx + 13, baseY - 3, 7, 3);
    g.endFill();

    g.beginFill(p.jugador, 1);
    g.drawRoundedRect(jx + 4, jy + 12, 16, 14, 3);
    g.endFill();
    g.lineStyle(1, p.jugadorOscuro, 1);
    g.drawRoundedRect(jx + 4, jy + 12, 16, 14, 3);
    g.lineStyle(0, 0, 0);
    g.beginFill(0x3a2a22, 1);
    g.drawRect(jx + 4, jy + 21, 16, 3);
    g.endFill();
    g.beginFill(0xb48c14, 1);
    g.drawRect(jx + 12, jy + 21, 3, 3);
    g.endFill();

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

    const lx = jx + (dir > 0 ? 22 : 2);
    g.beginFill(0xffd27a, 0.12);
    g.drawCircle(lx, jy + 18, 11);
    g.endFill();
    g.lineStyle(1, 0xb48c14, 1);
    g.moveTo(lx, jy + 13);
    g.lineTo(lx, jy + 16);
    g.lineStyle(0, 0, 0);
    g.beginFill(0x3a2a22, 1);
    g.drawRect(lx - 3, jy + 16, 6, 7);
    g.endFill();
    g.beginFill(0xffd23c, 1);
    g.drawRect(lx - 2, jy + 17, 4, 4);
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
    }

    actualizarJugador(state, dt);
    if (state.player.y > state.level.size.height + 120) {
      dañar(state, true);
      actualizarCamara(state, dt, false);
      actualizarHud(state);
      return;
    }

    actualizarEnemigos(state, dt);
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
      emitirMeta(state, state.level.goal.x + 10, state.level.goal.y + 10);
      sonido(state, "meta");
      if (state.levelIndex + 1 >= state.data.levels.length) {
        state.totalSouls += state.levelSouls;
        state.status = "victoria";
      } else {
        state.status = "nivel_completado";
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
