export function triggerExplode(canvas: HTMLCanvasElement, seeds: {x:number, y:number, alpha?: number}[], opts: {
    duration?: number,        // total duration of effect
    eraseDelay?: number,      // time before starting to erase red
    circleMin?: number,       // min circle radius
    circleMax?: number,       // max circle radius
    maxCircles?: number,      // max number of circles to use (if too many red pixels)
    circleAlpha?: number,     // alpha of circles when drawing
}
) {
  const ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
  const W = canvas.width, H = canvas.height;

  const {
    duration = 700,
    eraseDelay = 180,
    circleMin = 10,
    circleMax = 28,
    maxCircles = 900,
    circleAlpha = 1.0
  } = opts;

  const canvasWithContext = (canvas: HTMLCanvasElement) => {
    const c = document.createElement('canvas'); c.width = canvas.width; c.height = canvas.height;
    const cx = c.getContext('2d') as CanvasRenderingContext2D;
    return { canvas: c, context: cx };
  }
  const { canvas: fxCanvas, context: fxCtx } = canvasWithContext(canvas);

  if (seeds.length > maxCircles) {
    // random sample without heavy shuffling
    const keepProb = maxCircles / seeds.length;
    const filtered = [];
    for (const s of seeds) if (Math.random() < keepProb) filtered.push(s);
    while (filtered.length > maxCircles) filtered.pop();
    seeds.length = 0; seeds.push(...filtered);
  }

  const tStart = performance.now();
  let rafId: number;

  const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);

  for (let s of seeds) {
    s.alpha = Math.random() * .3 + .5
  }

  function frame(now: number) {
    const t = now - tStart;
    const done = t >= duration + 150;

    fxCtx.clearRect(0, 0, W, H);
    fxCtx.globalCompositeOperation = 'source-over';
    fxCtx.globalAlpha = circleAlpha;

    const live = Math.min(t, duration);
    for (const s of seeds) {
        const t0 = Math.random() * (duration * .3);
        const rMax = circleMin + Math.random() * (circleMax - circleMin);
        const local = Math.max(0, Math.min(1, (live - t0) / (duration - t0)));
        if (local <= 0) continue;
        const rNow = rMax * easeOutCubic(local);
        fxCtx.beginPath();
        fxCtx.moveTo(s.x + rNow, s.y);
        fxCtx.arc(s.x, s.y, rNow, 0, Math.PI * 2);
        fxCtx.fillStyle = `rgba(255,255,50,${s.alpha})`;
        s.alpha *= 0.96
        fxCtx.fill();
    }
    ctx.clearRect(0,0,W,H);
    ctx.drawImage(fxCanvas, 0, 0);

    if (!done) {
      rafId = requestAnimationFrame(frame);
    } else {
      // Final clean: redraw base only (red fully gone)
      ctx.clearRect(0, 0, W, H);
      cancelAnimationFrame(rafId);
    }
  }

  rafId = requestAnimationFrame(frame);
}
