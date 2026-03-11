'use strict';

// ── State ─────────────────────────────────────────────────────────────────────

const state = {
  N: 40,
  rowSeed: null,
  colSeed: null,
  matrix:  null,
  regions: null,
  nRegions: 0,
  colourMap: null,
  palette:   null,
  mode: 'borders',         // 'borders' | 'coloured'
  strategy: 'random',      // 'random'  | 'greedy'
  showLines: false,
};

// ── DOM ───────────────────────────────────────────────────────────────────────

const canvas       = document.getElementById('canvas');
const ctx          = canvas.getContext('2d');
const sizeInput    = document.getElementById('size');
const stratSelect  = document.getElementById('strategy');
const randomiseBtn = document.getElementById('btn-randomise');
const colourBtn    = document.getElementById('btn-colour');
const downloadBtn  = document.getElementById('btn-download');
const linesBtn     = document.getElementById('btn-lines');
const pngBtn       = document.getElementById('btn-png');
const statsEl      = document.getElementById('stats');

// ── Layout constants ──────────────────────────────────────────────────────────

const MAX_CANVAS_PX = 600;   // logical px for the main grid
const MIN_CELL      = 4;
const MAX_CELL      = 20;
const DPR           = window.devicePixelRatio || 1;

function cellSize(N) {
  return Math.min(MAX_CELL, Math.max(MIN_CELL, Math.floor(MAX_CANVAS_PX / N)));
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function randomSeed(N) {
  return Array.from({ length: N }, () => (Math.random() < 0.5 ? 1 : 0));
}

function recomputeMatrix() {
  state.matrix = generateTextile(state.N, state.rowSeed, state.colSeed);
}

function recomputeColours() {
  const { N, matrix, strategy } = state;
  const { regions, nRegions } = determineRegions(matrix);
  state.regions  = regions;
  state.nRegions = nRegions;

  let colourMap;
  if (strategy === 'greedy') {
    colourMap = greedyColouring(buildAdjacency(regions, nRegions, N), nRegions);
  } else {
    colourMap = randomColouring(nRegions);
  }
  state.colourMap = colourMap;

  const nColours = new Set(Array.from(colourMap).slice(1)).size;
  state.palette  = makeColourPalette(nColours, strategy, seedHash(state.rowSeed, state.colSeed));
}

// ── Initialise ────────────────────────────────────────────────────────────────

function init(N) {
  state.N       = N;
  state.rowSeed = randomSeed(N);
  state.colSeed = randomSeed(N);
  state.mode    = 'borders';
  state.regions = null;
  recomputeMatrix();
  updateColourBtn();
  render();
  updateStats();
  pushURL();
}

// ── Canvas rendering ──────────────────────────────────────────────────────────

let hovered = null;   // { type: 'row'|'col', index }

function render() {
  const { N, rowSeed, colSeed, matrix, mode } = state;
  const cs = cellSize(N);       // cell size in logical px
  const ss = cs;                // seed strip = same as cell

  const logicalW = ss + N * cs;
  const logicalH = ss + N * cs;

  canvas.width        = logicalW * DPR;
  canvas.height       = logicalH * DPR;
  canvas.style.width  = logicalW + 'px';
  canvas.style.height = logicalH + 'px';
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);

  // Background
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, logicalW, logicalH);

  // Seed strips
  drawSeedStrip('col', N, cs, ss);
  drawSeedStrip('row', N, cs, ss);

  // Corner — leave blank

  // Main grid
  if (mode === 'coloured' && state.colourMap) {
    drawColoured(N, cs, ss);
    if (state.showLines) drawBorders(N, cs, ss, matrix);
  } else {
    drawBorders(N, cs, ss, matrix);
  }
}

function drawSeedStrip(type, N, cs, ss) {
  const seed = type === 'col' ? state.colSeed : state.rowSeed;
  const pad = Math.max(2, Math.round(cs * 0.25));  // gap around each pill
  const r   = Math.round((cs - pad * 2) / 2);      // corner radius = half the pill height

  for (let i = 0; i < N; i++) {
    const isActive  = seed[i] === 1;
    const isHovered = hovered && hovered.type === type && hovered.index === i;

    ctx.fillStyle = isHovered ? '#aaaaaa'
                  : isActive  ? '#777777'
                  :             '#e8e8e8';

    let x, y, w, h;
    if (type === 'col') {
      x = ss + i * cs + pad;
      y = pad;
      w = cs - pad * 2;
      h = ss - pad * 2;
    } else {
      x = pad;
      y = ss + i * cs + pad;
      w = ss - pad * 2;
      h = cs - pad * 2;
    }

    ctx.beginPath();
    ctx.roundRect(x, y, w, h, r);
    ctx.fill();
  }
}

function drawBorders(N, cs, ss, M) {
  ctx.strokeStyle = state.mode === 'coloured' ? '#111111' : '#aaaaaa';
  ctx.lineWidth   = state.mode === 'coloured' ? 1.5 : 0.75;
  ctx.lineCap     = 'square';
  ctx.setLineDash([]);

  for (let r = 0; r < N; r++) {
    for (let c = 0; c < N; c++) {
      const v = M[r][c];
      const x = ss + c * cs;
      const y = ss + r * cs;

      if (v === 2 || v === 5) {           // right border
        ctx.beginPath();
        ctx.moveTo(x + cs + 0.5, y);
        ctx.lineTo(x + cs + 0.5, y + cs);
        ctx.stroke();
      }
      if (v === 3 || v === 5) {           // bottom border
        ctx.beginPath();
        ctx.moveTo(x,      y + cs + 0.5);
        ctx.lineTo(x + cs, y + cs + 0.5);
        ctx.stroke();
      }
    }
  }

}

function drawColoured(N, cs, ss) {
  const { regions, colourMap, palette } = state;
  for (let r = 0; r < N; r++) {
    for (let c = 0; c < N; c++) {
      const [rv, gv, bv] = palette[colourMap[regions[r][c]]] ?? [200, 200, 200];
      ctx.fillStyle = `rgb(${rv},${gv},${bv})`;
      ctx.fillRect(ss + c * cs, ss + r * cs, cs, cs);
    }
  }
}

// ── Stats bar ─────────────────────────────────────────────────────────────────

function updateStats() {
  if (state.mode === 'coloured' && state.nRegions > 0) {
    const nColours = new Set(Array.from(state.colourMap).slice(1)).size;
    statsEl.textContent = `${state.nRegions} regions · ${nColours} colours`;
  } else {
    statsEl.textContent = '';
  }
}

function updateColourBtn() {
  if (state.mode === 'coloured') {
    colourBtn.textContent = 'uncolour';
    colourBtn.classList.add('active');
  } else {
    colourBtn.textContent = 'colour';
    colourBtn.classList.remove('active');
  }
}

// ── Hit testing ───────────────────────────────────────────────────────────────

function hitSeed(x, y) {
  const { N } = state;
  const cs = cellSize(N);
  const ss = cs;

  if (y >= 1 && y < ss - 1 && x >= ss && x < ss + N * cs) {
    const i = Math.floor((x - ss) / cs);
    if (i >= 0 && i < N) return { type: 'col', index: i };
  }
  if (x >= 1 && x < ss - 1 && y >= ss && y < ss + N * cs) {
    const i = Math.floor((y - ss) / cs);
    if (i >= 0 && i < N) return { type: 'row', index: i };
  }
  return null;
}

function canvasXY(e) {
  const r = canvas.getBoundingClientRect();
  return [
    (e.clientX - r.left) * (canvas.width  / DPR / r.width),
    (e.clientY - r.top)  * (canvas.height / DPR / r.height),
  ];
}

// ── Canvas events ─────────────────────────────────────────────────────────────

canvas.addEventListener('click', e => {
  const [x, y] = canvasXY(e);
  const hit = hitSeed(x, y);
  if (!hit) return;

  if (hit.type === 'col') state.colSeed[hit.index] ^= 1;
  else                    state.rowSeed[hit.index] ^= 1;

  recomputeMatrix();
  if (state.mode === 'coloured') recomputeColours();
  render();
  updateStats();
  pushURL();
});

canvas.addEventListener('mousemove', e => {
  const [x, y] = canvasXY(e);
  const hit     = hitSeed(x, y);
  const changed = JSON.stringify(hit) !== JSON.stringify(hovered);
  hovered = hit;
  canvas.style.cursor = hit ? 'pointer' : 'default';
  if (changed) render();
});

canvas.addEventListener('mouseleave', () => {
  hovered = null;
  canvas.style.cursor = 'default';
  render();
});

// ── Button events ─────────────────────────────────────────────────────────────

randomiseBtn.addEventListener('click', () => {
  state.rowSeed = randomSeed(state.N);
  state.colSeed = randomSeed(state.N);
  recomputeMatrix();
  if (state.mode === 'coloured') recomputeColours();
  render();
  updateStats();
  pushURL();
});

colourBtn.addEventListener('click', () => {
  if (state.mode === 'borders') {
    recomputeColours();
    state.mode = 'coloured';
  } else {
    state.mode = 'borders';
  }
  updateColourBtn();
  render();
  updateStats();
});

downloadBtn.addEventListener('click', () => {
  if (!state.regions) recomputeColours();
  const oxs = toOXS(
    state.matrix, state.regions, state.nRegions,
    state.colourMap, state.palette,
    { title: `Textile ${state.N}×${state.N}` }
  );
  const p = new URLSearchParams(location.search);
  const a = Object.assign(document.createElement('a'), {
    href:     URL.createObjectURL(new Blob([oxs], { type: 'text/xml' })),
    download: `textile_${p.toString().replace(/&/g, '_')}.oxs`,
  });
  a.click();
  URL.revokeObjectURL(a.href);
});

pngBtn.addEventListener('click', () => {
  const p = new URLSearchParams(location.search);
  const a = Object.assign(document.createElement('a'), {
    href:     canvas.toDataURL('image/png'),
    download: `textile_${p.toString().replace(/&/g, '_')}.png`,
  });
  a.click();
});

linesBtn.addEventListener('click', () => {
  state.showLines = !state.showLines;
  linesBtn.classList.toggle('active', state.showLines);
  render();
});

stratSelect.addEventListener('change', () => {
  state.strategy = stratSelect.value;
  if (state.mode === 'coloured') {
    recomputeColours();
    render();
    updateStats();
  }
  pushURL();
});

sizeInput.addEventListener('change', () => {
  let N = parseInt(sizeInput.value, 10);
  if (isNaN(N) || N < 4)   N = 4;
  if (N > 100)              N = 100;
  sizeInput.value = N;
  init(N);
});

// ── URL encoding ─────────────────────────────────────────────────────────────

function seedToHex(seed) {
  const bytes = [];
  for (let i = 0; i < seed.length; i += 8) {
    let byte = 0;
    for (let b = 0; b < 8; b++)
      byte = (byte << 1) | (i + b < seed.length ? seed[i + b] & 1 : 0);
    bytes.push(byte);
  }
  return bytes.map(b => b.toString(16).padStart(2, '0')).join('');
}

function hexToSeed(hex, N) {
  const seed = [];
  for (let i = 0; i < hex.length && seed.length < N; i += 2) {
    const byte = parseInt(hex.slice(i, i + 2), 16);
    for (let b = 7; b >= 0 && seed.length < N; b--)
      seed.push((byte >> b) & 1);
  }
  return seed;
}

function pushURL() {
  const p = new URLSearchParams({
    n: state.N,
    c: state.strategy,
    r: seedToHex(state.rowSeed),
    h: seedToHex(state.colSeed),
  });
  history.replaceState(null, '', '?' + p.toString());
}

function stateFromURL() {
  const p = new URLSearchParams(location.search);
  const n = parseInt(p.get('n'), 10);
  const c = p.get('c');
  const r = p.get('r');
  const h = p.get('h');
  if (n && r && h) {
    state.N        = Math.min(100, Math.max(4, n));
    state.strategy = (c === 'greedy') ? 'greedy' : 'random';
    state.rowSeed  = hexToSeed(r, state.N);
    state.colSeed  = hexToSeed(h, state.N);
    sizeInput.value   = state.N;
    stratSelect.value = state.strategy;
    return true;
  }
  return false;
}

// ── Boot ──────────────────────────────────────────────────────────────────────

window.addEventListener('load', () => {
  if (stateFromURL()) {
    state.mode = 'borders';
    recomputeMatrix();
    updateColourBtn();
    render();
    updateStats();
  } else {
    init(state.N);
  }
});
