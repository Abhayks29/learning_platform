(function () {
  'use strict';

  const canvas = document.getElementById('cube-cluster-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // ── Resize ───────────────────────────────────────────────────────────────
  function resize() {
    canvas.width  = canvas.offsetWidth  || 420;
    canvas.height = canvas.offsetHeight || 360;
  }
  window.addEventListener('resize', resize);

  // ── 3-D math ─────────────────────────────────────────────────────────────
  function rotY([x,y,z], a) { const c=Math.cos(a),s=Math.sin(a); return [c*x+s*z, y, -s*x+c*z]; }
  function rotX([x,y,z], a) { const c=Math.cos(a),s=Math.sin(a); return [x, c*y-s*z, s*y+c*z]; }
  function project([x,y,z], fov, cx, cy) {
    const s = fov / (fov - z);
    return [cx + x*s, cy + y*s, s];
  }

  // ── Network topology ──────────────────────────────────────────────────────
  const LAYER_SIZES  = [4, 5, 5, 3];
  const LAYER_X      = [-3.2, -1.0, 1.0, 3.2];

  const LAYER_COLORS = [          // [highlight, dark]
    ['#c084fc', '#581c87'],       // input  — purple
    ['#60a5fa', '#1e3a8a'],       // h-1    — blue
    ['#38bdf8', '#0c4a6e'],       // h-2    — cyan
    ['#34d399', '#064e3b'],       // output — emerald
  ];
  const SIGNAL_COLORS = ['#c084fc', '#60a5fa', '#38bdf8', '#34d399'];

  // ── Build nodes ───────────────────────────────────────────────────────────
  const nodes = [];
  for (let l = 0; l < LAYER_SIZES.length; l++) {
    const count = LAYER_SIZES[l];
    for (let i = 0; i < count; i++) {
      const y = (i - (count - 1) / 2) * 1.5;
      const z = Math.sin(l * 2.1 + i * 1.7) * 0.5;
      nodes.push({ x: LAYER_X[l], y, z, layer: l });
    }
  }

  // ── Build edges (fully connected between adjacent layers) ─────────────────
  const edges = [];
  let offset = 0;
  for (let l = 0; l < LAYER_SIZES.length - 1; l++) {
    for (let i = 0; i < LAYER_SIZES[l]; i++)
      for (let j = 0; j < LAYER_SIZES[l + 1]; j++)
        edges.push({ from: offset + i, to: offset + LAYER_SIZES[l] + j,
                     weight: 0.25 + Math.random() * 0.75 });
    offset += LAYER_SIZES[l];
  }

  // ── Adjacency lists ───────────────────────────────────────────────────────
  const allEdgesOf = nodes.map(() => []);   // all edges touching node (hover)
  const outEdgesOf  = nodes.map(() => []);   // outgoing edges only (cascade)
  edges.forEach((e, ei) => {
    allEdgesOf[e.from].push(ei);
    allEdgesOf[e.to].push(ei);
    outEdgesOf[e.from].push(ei);
  });

  // ── Node activation levels (0..1, drives flash pulse) ─────────────────────
  const nodeAct = new Float32Array(nodes.length);

  // ── Signal particles ──────────────────────────────────────────────────────
  const signals = [];

  function spawnSignal(ei) {
    if (signals.length >= 100) return;
    signals.push({
      ei,
      progress: 0,
      speed: 0.0038 + Math.random() * 0.004,
      hue:  SIGNAL_COLORS[nodes[edges[ei].from].layer],
      r:    2.5 + Math.random() * 1.8,
    });
  }

  // Called when a signal finishes travelling its edge
  function onSignalArrive(ei) {
    const dest = edges[ei].to;
    nodeAct[dest] = 1.0;                    // trigger activation flash
    outEdgesOf[dest].forEach(spawnSignal);  // cascade to next layer
  }

  // ── Wave management ───────────────────────────────────────────────────────
  let waveTimer = 50;   // first wave fires after 50 frames (~0.8 s)

  function startWave() {
    // Fire one signal per edge from every input node
    for (let ni = 0; ni < nodes.length; ni++)
      if (nodes[ni].layer === 0) outEdgesOf[ni].forEach(spawnSignal);
    waveTimer = 210;    // ~3.5 s until next wave
  }

  // ── Mouse hover ───────────────────────────────────────────────────────────
  let mx = -1e9, my = -1e9, hovNode = null;
  canvas.addEventListener('mousemove', e => {
    const r = canvas.getBoundingClientRect();
    mx = e.clientX - r.left; my = e.clientY - r.top;
  });
  canvas.addEventListener('mouseleave', () => { mx = my = -1e9; });

  // ── Animation ─────────────────────────────────────────────────────────────
  let yAngle = 0;
  const TILT  = 0.28;

  function frame() {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);
    yAngle += 0.006;

    // Wave countdown
    if (--waveTimer <= 0) startWave();

    // Decay activations each frame
    for (let i = 0; i < nodeAct.length; i++)
      nodeAct[i] = nodeAct[i] > 0.005 ? nodeAct[i] * 0.88 : 0;

    const SCALE  = Math.min(W, H) * 0.10;
    const FOV    = Math.min(W, H) * 2.0;
    const cx = W / 2, cy = H / 2;
    const NODE_R = SCALE * 0.14;

    // Project all nodes
    const proj = nodes.map(n => {
      let p = [n.x * SCALE, n.y * SCALE, n.z * SCALE];
      p = rotX(p, TILT);
      p = rotY(p, yAngle);
      return project(p, FOV, cx, cy);
    });

    // Hover: nearest node within threshold
    hovNode = null;
    let bestD = NODE_R * 2.8;
    for (let i = 0; i < proj.length; i++) {
      const d = Math.hypot(proj[i][0] - mx, proj[i][1] - my);
      if (d < bestD) { bestD = d; hovNode = i; }
    }

    const hlEdges = new Set(), hlNodes = new Set();
    if (hovNode !== null) {
      hlNodes.add(hovNode);
      allEdgesOf[hovNode].forEach(ei => {
        hlEdges.add(ei);
        hlNodes.add(edges[ei].from);
        hlNodes.add(edges[ei].to);
      });
    }

    // ── 1. Edges ─────────────────────────────────────────────────────────────
    for (let ei = 0; ei < edges.length; ei++) {
      const e  = edges[ei];
      const [ax, ay] = proj[e.from];
      const [bx, by] = proj[e.to];
      const hl = hlEdges.has(ei);

      ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(bx, by);
      ctx.strokeStyle = hl
        ? `rgba(96,165,250,${(e.weight * 0.85).toFixed(2)})`
        : `rgba(55,95,200,${(e.weight * 0.18).toFixed(2)})`;
      ctx.lineWidth   = hl ? 1.6 : 0.8;
      if (hl) { ctx.shadowColor = '#3b82f6'; ctx.shadowBlur = 8; }
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    // ── 2. Signals ────────────────────────────────────────────────────────────
    for (let i = signals.length - 1; i >= 0; i--) {
      const sig = signals[i];
      sig.progress += sig.speed;

      if (sig.progress >= 1) {
        onSignalArrive(sig.ei);
        signals.splice(i, 1);
        continue;
      }

      const e  = edges[sig.ei];
      const [ax, ay, as_] = proj[e.from];
      const [bx, by, bs]  = proj[e.to];
      const t  = sig.progress;
      const sx = ax + (bx - ax) * t;
      const sy = ay + (by - ay) * t;
      const sr = sig.r * (as_ * (1 - t) + bs * t);

      // Soft trailing tail
      const t0  = Math.max(0, t - 0.07);
      const tx0 = ax + (bx - ax) * t0;
      const ty0 = ay + (by - ay) * t0;
      const tg  = ctx.createLinearGradient(tx0, ty0, sx, sy);
      tg.addColorStop(0, sig.hue + '00');
      tg.addColorStop(1, sig.hue + 'bb');
      ctx.beginPath(); ctx.moveTo(tx0, ty0); ctx.lineTo(sx, sy);
      ctx.strokeStyle = tg; ctx.lineWidth = sr * 0.9; ctx.stroke();

      // Glowing head dot
      ctx.beginPath(); ctx.arc(sx, sy, sr, 0, Math.PI * 2);
      ctx.fillStyle   = sig.hue;
      ctx.shadowColor = sig.hue;
      ctx.shadowBlur  = 14;
      ctx.fill();
      ctx.shadowBlur  = 0;
    }

    // ── 3. Nodes (back → front) ───────────────────────────────────────────────
    const order = nodes.map((_, i) => i).sort((a, b) => proj[a][2] - proj[b][2]);

    for (const i of order) {
      const n   = nodes[i];
      const [px, py, ps] = proj[i];
      const hl  = hlNodes.has(i);
      const act = nodeAct[i];
      const r   = NODE_R * ps;
      const [bright, dark] = LAYER_COLORS[n.layer];

      // Activation burst ring (expands and fades as act decays)
      if (act > 0.01) {
        const burstR = r * (1 + (1 - act) * 3.5);
        ctx.beginPath(); ctx.arc(px, py, burstR, 0, Math.PI * 2);
        const ag = ctx.createRadialGradient(px, py, r * 0.4, px, py, burstR);
        const hex = Math.round(act * 140).toString(16).padStart(2, '0');
        ag.addColorStop(0, bright + hex);
        ag.addColorStop(1, bright + '00');
        ctx.fillStyle = ag; ctx.fill();
      }

      // Hover glow halo
      if (hl) {
        ctx.beginPath(); ctx.arc(px, py, r * 2.8, 0, Math.PI * 2);
        const hg = ctx.createRadialGradient(px, py, r * 0.5, px, py, r * 2.8);
        hg.addColorStop(0, bright + '55'); hg.addColorStop(1, bright + '00');
        ctx.fillStyle = hg; ctx.fill();
      }

      // Node body with radial shading
      ctx.beginPath(); ctx.arc(px, py, r, 0, Math.PI * 2);
      const ng = ctx.createRadialGradient(px - r * 0.3, py - r * 0.35, 0, px, py, r);
      ng.addColorStop(0,   (hl || act > 0.35) ? '#ffffff' : bright);
      ng.addColorStop(0.4, bright);
      ng.addColorStop(1,   dark);
      ctx.fillStyle   = ng;
      ctx.shadowColor = bright;
      ctx.shadowBlur  = hl ? 20 : act > 0.05 ? 8 + act * 22 : 10;
      ctx.fill();
      ctx.shadowBlur  = 0;

      // White flash overlay fades as activation decays
      if (act > 0.01) {
        ctx.beginPath(); ctx.arc(px, py, r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,255,255,${(act * 0.68).toFixed(2)})`;
        ctx.fill();
      }

      // Bright rim
      ctx.beginPath(); ctx.arc(px, py, r, 0, Math.PI * 2);
      ctx.strokeStyle = (hl || act > 0.08) ? bright : bright + '55';
      ctx.lineWidth   = (hl || act > 0.08) ? 1.5 : 0.6;
      ctx.stroke();
    }

    requestAnimationFrame(frame);
  }

  requestAnimationFrame(() => { resize(); requestAnimationFrame(frame); });
})();
