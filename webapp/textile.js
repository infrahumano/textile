'use strict';

// ── Generation ────────────────────────────────────────────────────────────────

function generateTextile(N, rowSeed, colSeed) {
  const M = [];
  for (let r = 0; r < N; r++) {
    const row = new Int16Array(N);
    for (let c = 0; c < N; c++) {
      const h = (c % 2 === 0) ? (rowSeed[r] ? 2 : 0) : (rowSeed[r] ? 0 : 2);
      const v = (r % 2 === 0) ? (colSeed[c] ? 3 : 0) : (colSeed[c] ? 0 : 3);
      row[c] = h + v;
    }
    M.push(row);
  }
  return M;
}

// ── Region detection ──────────────────────────────────────────────────────────

function determineRegions(M) {
  const N = M.length;
  const R = Array.from({ length: N }, () => new Int32Array(N));
  let idx = 1;
  for (let r = 0; r < N; r++)
    for (let c = 0; c < N; c++)
      if (R[r][c] === 0) bfs(M, r, c, R, N, idx++);
  return { regions: R, nRegions: idx - 1 };
}

function bfs(M, sr, sc, R, N, idx) {
  const q = [sr * N + sc];
  let head = 0;
  while (head < q.length) {
    const pos = q[head++];
    const r = (pos / N) | 0, c = pos % N;
    if (R[r][c] !== 0) continue;
    R[r][c] = idx;
    const v = M[r][c];
    if (r > 0   && R[r-1][c] === 0 && M[r-1][c] !== 3 && M[r-1][c] !== 5) q.push((r-1)*N+c);
    if (r+1 < N && R[r+1][c] === 0 && v !== 3 && v !== 5)                  q.push((r+1)*N+c);
    if (c > 0   && R[r][c-1] === 0 && M[r][c-1] !== 2 && M[r][c-1] !== 5) q.push(r*N+c-1);
    if (c+1 < N && R[r][c+1] === 0 && v !== 2 && v !== 5)                  q.push(r*N+c+1);
  }
}

// ── Colouring ─────────────────────────────────────────────────────────────────

function buildAdjacency(regions, nRegions, N) {
  const adj = Array.from({ length: nRegions + 1 }, () => new Set());
  for (let r = 0; r < N; r++) {
    for (let c = 0; c < N; c++) {
      const a = regions[r][c];
      if (c+1 < N) { const b = regions[r][c+1];   if (a !== b) { adj[a].add(b); adj[b].add(a); } }
      if (r+1 < N) { const b = regions[r+1][c]; if (a !== b) { adj[a].add(b); adj[b].add(a); } }
    }
  }
  return adj;
}

function greedyColouring(adj, nRegions) {
  const map = new Int32Array(nRegions + 1).fill(-1);
  for (let i = 1; i <= nRegions; i++) {
    const used = new Set();
    for (const nb of adj[i]) if (map[nb] >= 0) used.add(map[nb]);
    let c = 0; while (used.has(c)) c++;
    map[i] = c;
  }
  return map;
}

function randomColouring(nRegions) {
  const map = new Int32Array(nRegions + 1);
  for (let i = 1; i <= nRegions; i++) map[i] = i - 1;
  return map;
}

// ── Palette ───────────────────────────────────────────────────────────────────

function mulberry32(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6D2B79F5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = Math.imul(t ^ (t >>> 7), 61 | t) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 0x100000000;
  };
}

function hslToRgb(h, s, l) {
  s /= 100; l /= 100;
  const k = n => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = n => Math.round((l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)))) * 255);
  return [f(0), f(8), f(4)];
}

// Saturated palette for greedy (~4–6 colours)
const GREEDY_COLOURS = [
  [ 90, 130, 210],  // cobalt
  [225,  80,  80],  // crimson
  [ 60, 175, 120],  // emerald
  [240, 165,  40],  // amber
  [155,  80, 200],  // violet
  [ 40, 185, 200],  // teal
];

function hexToRgb(hex) {
  const v = parseInt(hex.slice(1), 16);
  return [(v >> 16) & 255, (v >> 8) & 255, v & 255];
}

function makeColourPalette(nColours, strategy, seed, customPalette) {
  if (strategy === 'greedy') {
    const base = customPalette ? customPalette.map(hexToRgb) : GREEDY_COLOURS;
    return Array.from({ length: nColours }, (_, i) => base[i % base.length]);
  }
  const rng = mulberry32(seed);
  return Array.from({ length: nColours }, () => {
    const h = rng() * 360;
    const s = 42 + rng() * 30;   // 42–72 %
    const l = 46 + rng() * 20;   // 46–66 %
    return hslToRgb(h, s, l);
  });
}

function seedHash(rowSeed, colSeed) {
  let h = 2166136261 >>> 0;
  for (const v of rowSeed) h = Math.imul(h ^ v, 16777619) >>> 0;
  for (const v of colSeed)  h = Math.imul(h ^ v, 16777619) >>> 0;
  return h;
}

// ── OXS export ────────────────────────────────────────────────────────────────

function rgbToHex(r, g, b) {
  return [r, g, b].map(v => v.toString(16).padStart(2, '0').toUpperCase()).join('');
}

function escapeXml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function toOXS(M, regions, nRegions, colourMap, palette, opts = {}) {
  const { title = 'Textile', borders = true, borderColour = '1C1C1C' } = opts;
  const N = M.length;
  const nColours = new Set(Array.from(colourMap).slice(1)).size;
  const bpi = nColours + 1;
  const bc = borderColour.toUpperCase();

  const L = [];
  L.push('<?xml version="1.0" encoding="UTF-8"?>');
  L.push('<chart>');
  L.push(`  <properties oxsversion="1.0" software="textile-web" chartheight="${N}" chartwidth="${N}" charttitle="${escapeXml(title)}" palettecount="${nColours + (borders ? 1 : 0)}"/>`);
  L.push('  <palette>');
  L.push('    <palette_item index="0" number="cloth" name="cloth" color="FFFFFF" printcolor="FFFFFF" blendcolor="nil" strands="2" bsstrands="2" bscolor="FFFFFF"/>');
  for (let i = 0; i < nColours; i++) {
    const [r, g, b] = palette[i] ?? [128, 128, 128];
    const hex = rgbToHex(r, g, b);
    L.push(`    <palette_item index="${i+1}" number="Custom ${i+1}" name="Colour ${i+1}" color="${hex}" printcolor="${hex}" blendcolor="nil" strands="2" bsstrands="2" bscolor="${hex}"/>`);
  }
  if (borders) {
    L.push(`    <palette_item index="${bpi}" number="Border" name="Border" color="${bc}" printcolor="${bc}" blendcolor="nil" strands="1" bsstrands="1" bscolor="${bc}"/>`);
  }
  L.push('  </palette>');

  L.push('  <fullstitches>');
  for (let r = 0; r < N; r++)
    for (let c = 0; c < N; c++)
      L.push(`    <stitch x="${c}" y="${r}" palindex="${colourMap[regions[r][c]] + 1}"/>`);
  L.push('  </fullstitches>');

  L.push('  <backstitches>');
  if (borders) {
    for (let r = 0; r < N; r++) {
      for (let c = 0; c < N; c++) {
        const v = M[r][c];
        if (v === 2 || v === 5) L.push(`    <backstitch x1="${c+1}" y1="${r}" x2="${c+1}" y2="${r+1}" palindex="${bpi}" objecttype="backstitch"/>`);
        if (v === 3 || v === 5) L.push(`    <backstitch x1="${c}" y1="${r+1}" x2="${c+1}" y2="${r+1}" palindex="${bpi}" objecttype="backstitch"/>`);
      }
    }
  }
  L.push('  </backstitches>');
  L.push('</chart>');
  return L.join('\n');
}
