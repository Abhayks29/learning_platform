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
  const dot  = (a, b) => a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
  const norm = v => { const l = Math.sqrt(dot(v,v)); return [v[0]/l,v[1]/l,v[2]/l]; };

  function rotY([x,y,z], a) { const c=Math.cos(a),s=Math.sin(a); return [c*x+s*z, y, -s*x+c*z]; }
  function rotX([x,y,z], a) { const c=Math.cos(a),s=Math.sin(a); return [x, c*y-s*z, s*y+c*z]; }

  // Camera at z=+FOV looking toward −z
  function project([x,y,z], fov, cx, cy) {
    const s = fov / (fov - z);
    return [cx + x*s, cy + y*s];
  }

  // ── Geometry ──────────────────────────────────────────────────────────────
  const VERTS = [
    [-0.5,-0.5,-0.5],[0.5,-0.5,-0.5],[0.5,0.5,-0.5],[-0.5,0.5,-0.5],
    [-0.5,-0.5, 0.5],[0.5,-0.5, 0.5],[0.5,0.5, 0.5],[-0.5,0.5, 0.5],
  ];
  const FACES = [
    { vi:[0,1,2,3], n:[0,0,-1] },  // back
    { vi:[5,4,7,6], n:[0,0, 1] },  // front
    { vi:[4,0,3,7], n:[-1,0,0] },  // left
    { vi:[1,5,6,2], n:[ 1,0,0] },  // right
    { vi:[4,5,1,0], n:[0,-1,0] },  // bottom
    { vi:[3,2,6,7], n:[0, 1,0] },  // top
  ];

  const LIGHT   = norm([1.5, -2, 1.2]);   // surface → light direction (world space)
  const AMBIENT = 0.20;
  const DIFFUSE = 0.80;

  const SP = 1.22;
  const OFFSETS = [
    [0,0,0],
    [ SP,0,0],[-SP,0,0],
    [0, SP,0],[0,-SP,0],
    [0,0, SP],[0,0,-SP],
  ];

  // ── Mouse / hover (whole-cube) ────────────────────────────────────────────
  let mx = -1e9, my = -1e9, hovCube = null;

  canvas.addEventListener('mousemove', e => {
    const r = canvas.getBoundingClientRect();
    mx = e.clientX - r.left;
    my = e.clientY - r.top;
  });
  canvas.addEventListener('mouseleave', () => { mx = my = -1e9; });

  function pointInPoly(px, py, pts) {
    let inside = false;
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
      const [xi,yi] = pts[i], [xj,yj] = pts[j];
      if ((yi > py) !== (yj > py) && px < (xj-xi)*(py-yi)/(yj-yi)+xi)
        inside = !inside;
    }
    return inside;
  }

  // ── Rounded quad path ─────────────────────────────────────────────────────
  function roundedQuad(pts, r) {
    ctx.beginPath();
    const n = pts.length;
    for (let i = 0; i < n; i++) {
      const p  = pts[i];
      const pr = pts[(i+n-1)%n];
      const nx = pts[(i+1)%n];
      const d1x=pr[0]-p[0], d1y=pr[1]-p[1], l1=Math.sqrt(d1x*d1x+d1y*d1y);
      const d2x=nx[0]-p[0], d2y=nx[1]-p[1], l2=Math.sqrt(d2x*d2x+d2y*d2y);
      const rr = Math.min(r, l1*0.45, l2*0.45);
      const t1x=p[0]+(d1x/l1)*rr, t1y=p[1]+(d1y/l1)*rr;
      const t2x=p[0]+(d2x/l2)*rr, t2y=p[1]+(d2y/l2)*rr;
      if (i === 0) ctx.moveTo(t1x,t1y); else ctx.lineTo(t1x,t1y);
      ctx.quadraticCurveTo(p[0],p[1],t2x,t2y);
    }
    ctx.closePath();
  }

  // ── Animation ────────────────────────────────────────────────────────────
  let yAngle = 0;
  const TILT  = 0.32;

  function frame() {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);
    yAngle += 0.007;

    const WS      = Math.min(W,H) * 0.115;   // world-unit → pixel
    const FOV     = Math.min(W,H) * 1.6;
    const cx = W/2, cy = H/2;
    const cornerR = WS * 0.36;               // pillowy rounded corners

    // ── Build face list ───────────────────────────────────────────────────
    const faces = [];

    for (let ci = 0; ci < OFFSETS.length; ci++) {
      const [opx,opy,opz] = OFFSETS[ci];

      const tverts = VERTS.map(([vx,vy,vz]) => {
        let p = [(vx+opx)*WS, (vy+opy)*WS, (vz+opz)*WS];
        p = rotX(p, TILT);
        p = rotY(p, yAngle);
        return p;
      });

      for (let fi = 0; fi < FACES.length; fi++) {
        const { vi, n } = FACES[fi];
        let wn = rotX(n, TILT);
        wn = rotY(wn, yAngle);
        if (wn[2] <= 0) continue;                    // backface cull

        const bright = Math.min(1, AMBIENT + Math.max(0, dot(wn, LIGHT)) * DIFFUSE);
        const pts2d  = vi.map(i => project(tverts[i], FOV, cx, cy));
        const fz     = vi.reduce((s,i) => s+tverts[i][2], 0) / vi.length;
        const fcx    = pts2d.reduce((s,p) => s+p[0], 0) / pts2d.length;
        const fcy    = pts2d.reduce((s,p) => s+p[1], 0) / pts2d.length;
        const faceR  = Math.max(...pts2d.map(([px,py]) => Math.hypot(px-fcx, py-fcy))) * 1.25;

        faces.push({ pts2d, bright, ci, fi, fcx, fcy, fz, faceR });
      }
    }

    // Painter's sort: back → front
    faces.sort((a,b) => a.fz - b.fz);

    // ── Hit test (front → back) — track cube, not face ────────────────────
    hovCube = null;
    for (let i = faces.length - 1; i >= 0; i--) {
      if (pointInPoly(mx, my, faces[i].pts2d)) {
        hovCube = faces[i].ci;
        break;
      }
    }

    // ── Glow pass: hovered cube rendered first with large shadow ──────────
    if (hovCube !== null) {
      ctx.save();
      ctx.shadowColor = '#60a5fa';
      ctx.shadowBlur  = 38;
      for (const { pts2d, ci } of faces) {
        if (ci !== hovCube) continue;
        roundedQuad(pts2d, cornerR);
        ctx.fillStyle = 'rgba(96,165,250,0.55)';
        ctx.fill();
      }
      ctx.restore();
    }

    // ── Main draw pass ────────────────────────────────────────────────────
    for (const { pts2d, bright, ci, fcx, fcy, faceR } of faces) {
      const hov = (ci === hovCube);

      roundedQuad(pts2d, cornerR);

      // --- Base flat fill (brightness from light direction) ---
      if (hov) {
        ctx.fillStyle = `rgb(${~~(bright*40)},${~~(bright*105)},${~~(bright*235)})`;
      } else {
        ctx.fillStyle = `rgb(${~~(bright*18)},${~~(bright*58)},${~~(bright*175)})`;
      }
      ctx.fill();   // path remains active for next fill

      // --- Pillow radial gradient overlay (convex highlight) ---
      const g = ctx.createRadialGradient(fcx, fcy, 0, fcx, fcy, faceR);
      if (hov) {
        g.addColorStop(0,   `rgba(180,215,255,${(0.52+bright*0.25).toFixed(2)})`);
        g.addColorStop(0.42,`rgba(90,150,245,0.10)`);
        g.addColorStop(1,   'rgba(0,0,0,0)');
      } else {
        g.addColorStop(0,   `rgba(130,165,240,${(0.40+bright*0.18).toFixed(2)})`);
        g.addColorStop(0.45,'rgba(65,105,200,0.07)');
        g.addColorStop(1,   'rgba(0,0,0,0)');
      }
      ctx.fillStyle = g;
      ctx.fill();   // same path, additive overlay → pillowy look
    }

    requestAnimationFrame(frame);
  }

  requestAnimationFrame(() => { resize(); requestAnimationFrame(frame); });
})();
