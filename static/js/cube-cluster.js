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
    return [cx + x*s, cy + y*s, s];   // [screenX, screenY, perspectiveScale]
  }

  // ── Network topology: 4 layers ────────────────────────────────────────────
  const LAYER_SIZES = [4, 5, 5, 3];
  const LAYER_X     = [-3.2, -1.0, 1.0, 3.2];

  // Layer accent colours  [bright, dark]
  const LAYER_COLORS = [
    ['#c084fc', '#581c87'],   // input  — purple
    ['#60a5fa', '#1e3a8a'],   // h-1    — blue
    ['#38bdf8', '#0c4a6e'],   // h-2    — cyan-blue
    ['#34d399', '#064e3b'],   // output — emerald
  ];

  // Build nodes
  const nodes = [];
  for (let l = 0; l < LAYER_SIZES.length; l++) {
    const count = LAYER_SIZES[l];
    for (let i = 0; i < count; i++) {
      const y  = (i - (count - 1) / 2) * 1.5;
      const z  = Math.sin(l * 2.1 + i * 1.7) * 0.5;   // slight Z scatter
      nodes.push({ x: LAYER_X[l], y, z, layer: l, localIdx: i });
    }
  }

  // Build fully-connected edges between adjacent layers
  const edges = [];
  let offset = 0;
  for (let l = 0; l < LAYER_SIZES.length - 1; l++) {
    for (let i = 0; i < LAYER_SIZES[l]; i++) {
      for (let j = 0; j < LAYER_SIZES[l + 1]; j++) {
        edges.push({
          from:   offset + i,
          to:     offset + LAYER_SIZES[l] + j,
          weight: 0.25 + Math.random() * 0.75,
        });
      }
    }
    offset += LAYER_SIZES[l];
  }

  // Build adjacency for hover highlight
  const nodeEdges = nodes.map(() => []);
  edges.forEach((e, ei) => { nodeEdges[e.from].push(ei); nodeEdges[e.to].push(ei); });

  // ── Signal particles (travel from→to along an edge) ───────────────────────
  const signals = [];

  function spawnSignal(edgeIdx) {
    signals.push({
      ei:       edgeIdx,
      progress: 0,
      speed:    0.0035 + Math.random() * 0.005,
      hue:      Math.random() < 0.55 ? '#60a5fa' : '#a78bfa',
      r:        2.5 + Math.random() * 2,
    });
  }

  // Seed initial signals staggered across all edges
  for (let i = 0; i < 14; i++) {
    spawnSignal(Math.floor(Math.random() * edges.length));
    signals[i].progress = Math.random();
  }

  // ── Mouse hover ───────────────────────────────────────────────────────────
  let mx = -1e9, my = -1e9, hovNode = null;
  canvas.addEventListener('mousemove', e => {
    const r = canvas.getBoundingClientRect();
    mx = e.clientX - r.left;
    my = e.clientY - r.top;
  });
  canvas.addEventListener('mouseleave', () => { mx = my = -1e9; });

  // ── Animation state ───────────────────────────────────────────────────────
  let yAngle = 0;
  const TILT  = 0.28;

  // ── Frame ─────────────────────────────────────────────────────────────────
  function frame() {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);
    yAngle += 0.006;

    const SCALE = Math.min(W, H) * 0.10;
    const FOV   = Math.min(W, H) * 2.0;
    const cx = W / 2, cy = H / 2;
    const NODE_R = SCALE * 0.14;   // base node radius (world-space px)

    // Project all nodes
    const proj = nodes.map(n => {
      let p = [n.x * SCALE, n.y * SCALE, n.z * SCALE];
      p = rotX(p, TILT);
      p = rotY(p, yAngle);
      return project(p, FOV, cx, cy);
    });

    // Hit-test: nearest node within threshold
    hovNode = null;
    let bestD = NODE_R * 2.5;
    for (let i = 0; i < proj.length; i++) {
      const d = Math.hypot(proj[i][0] - mx, proj[i][1] - my);
      if (d < bestD) { bestD = d; hovNode = i; }
    }

    // Highlighted set for hovered node
    const hlEdges = new Set();
    const hlNodes = new Set();
    if (hovNode !== null) {
      hlNodes.add(hovNode);
      nodeEdges[hovNode].forEach(ei => {
        hlEdges.add(ei);
        hlNodes.add(edges[ei].from);
        hlNodes.add(edges[ei].to);
      });
    }

    // ── 1. Draw edges ────────────────────────────────────────────────────────
    for (let ei = 0; ei < edges.length; ei++) {
      const e    = edges[ei];
      const [ax, ay] = proj[e.from];
      const [bx, by] = proj[e.to];
      const hl   = hlEdges.has(ei);
      const base = hl ? e.weight * 0.85 : e.weight * 0.18;

      ctx.beginPath();
      ctx.moveTo(ax, ay);
      ctx.lineTo(bx, by);

      if (hl) {
        ctx.strokeStyle  = `rgba(96,165,250,${base.toFixed(2)})`;
        ctx.lineWidth    = 1.6;
        ctx.shadowColor  = '#3b82f6';
        ctx.shadowBlur   = 8;
      } else {
        ctx.strokeStyle = `rgba(55,95,200,${base.toFixed(2)})`;
        ctx.lineWidth   = 0.8;
        ctx.shadowBlur  = 0;
      }
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    // ── 2. Update + draw signal particles ────────────────────────────────────
    for (let i = signals.length - 1; i >= 0; i--) {
      const sig = signals[i];
      sig.progress += sig.speed;
      if (sig.progress >= 1) {
        signals.splice(i, 1);
        spawnSignal(Math.floor(Math.random() * edges.length));
        continue;
      }
      const e  = edges[sig.ei];
      const [ax, ay, as_] = proj[e.from];
      const [bx, by, bs]  = proj[e.to];
      const t   = sig.progress;
      const sx  = ax + (bx - ax) * t;
      const sy  = ay + (by - ay) * t;
      const sr  = sig.r * (as_ * (1-t) + bs * t);  // perspective-scaled radius

      // Soft trail
      const trailLen = 0.06;
      const t0 = Math.max(0, t - trailLen);
      const tx0 = ax + (bx - ax) * t0;
      const ty0 = ay + (by - ay) * t0;
      const trailGrad = ctx.createLinearGradient(tx0, ty0, sx, sy);
      trailGrad.addColorStop(0, `${sig.hue}00`);
      trailGrad.addColorStop(1, `${sig.hue}cc`);
      ctx.beginPath();
      ctx.moveTo(tx0, ty0);
      ctx.lineTo(sx, sy);
      ctx.strokeStyle = trailGrad;
      ctx.lineWidth   = sr * 0.9;
      ctx.stroke();

      // Head dot
      ctx.beginPath();
      ctx.arc(sx, sy, sr, 0, Math.PI * 2);
      ctx.fillStyle   = sig.hue;
      ctx.shadowColor = sig.hue;
      ctx.shadowBlur  = 14;
      ctx.fill();
      ctx.shadowBlur  = 0;
    }

    // ── 3. Draw nodes (back → front by perspective scale) ────────────────────
    const order = nodes.map((n,i) => i).sort((a,b) => proj[a][2] - proj[b][2]);

    for (const i of order) {
      const n    = nodes[i];
      const [px, py, ps] = proj[i];
      const hl   = hlNodes.has(i);
      const r    = NODE_R * ps;    // perspective-scaled radius
      const [bright, dark] = LAYER_COLORS[n.layer];

      // Outer glow ring
      if (hl) {
        ctx.beginPath();
        ctx.arc(px, py, r * 2.8, 0, Math.PI * 2);
        const glowG = ctx.createRadialGradient(px, py, r * 0.5, px, py, r * 2.8);
        glowG.addColorStop(0, bright + '55');
        glowG.addColorStop(1, bright + '00');
        ctx.fillStyle = glowG;
        ctx.fill();
      }

      // Node body with radial gradient
      ctx.beginPath();
      ctx.arc(px, py, r, 0, Math.PI * 2);
      const ng = ctx.createRadialGradient(
        px - r * 0.3, py - r * 0.35, 0,
        px,           py,            r
      );
      ng.addColorStop(0,   hl ? '#ffffff' : bright);
      ng.addColorStop(0.4, bright);
      ng.addColorStop(1,   dark);
      ctx.fillStyle   = ng;
      ctx.shadowColor = bright;
      ctx.shadowBlur  = hl ? 20 : 10;
      ctx.fill();
      ctx.shadowBlur  = 0;

      // Thin bright rim
      ctx.beginPath();
      ctx.arc(px, py, r, 0, Math.PI * 2);
      ctx.strokeStyle = hl ? bright : bright + '66';
      ctx.lineWidth   = hl ? 1.5 : 0.6;
      ctx.stroke();
    }

    requestAnimationFrame(frame);
  }

  requestAnimationFrame(() => { resize(); requestAnimationFrame(frame); });
})();
