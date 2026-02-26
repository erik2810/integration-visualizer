import { useEffect, useRef } from 'react';
import { COLORS } from '../utils/constants';

export const Visualization1D = ({ data }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!data || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * 2;
    canvas.height = rect.height * 2;
    ctx.scale(2, 2);

    const { curve, rectangles, bounds } = data;
    const padding = 40;
    const plotWidth = rect.width - 2 * padding;
    const plotHeight = rect.height - 2 * padding;
    const xMin = bounds.a, xMax = bounds.b;
    const yVals = curve.y.filter(v => isFinite(v));
    const yMin = Math.min(0, Math.min(...yVals));
    const yMax = Math.max(0, Math.max(...yVals));
    const yRange = yMax - yMin || 1;
    const toX = (x) => padding + ((x - xMin) / (xMax - xMin)) * plotWidth;
    const toY = (y) => padding + plotHeight - ((y - yMin) / yRange) * plotHeight;

    // Background
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, rect.width, rect.height);

    // Grid
    ctx.strokeStyle = COLORS.border;
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 4; i++) {
      ctx.beginPath();
      ctx.moveTo(padding + i * plotWidth / 4, padding);
      ctx.lineTo(padding + i * plotWidth / 4, padding + plotHeight);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(padding, padding + i * plotHeight / 4);
      ctx.lineTo(padding + plotWidth, padding + i * plotHeight / 4);
      ctx.stroke();
    }

    // Riemann rectangles
    ctx.fillStyle = `${COLORS.primary}40`;
    ctx.strokeStyle = COLORS.primary;
    ctx.lineWidth = 1;
    rectangles.forEach(r => {
      const x = toX(r.x);
      const w = (r.width / (xMax - xMin)) * plotWidth;
      const yB = toY(0), yT = toY(r.height);
      ctx.fillRect(x, Math.min(yB, yT), w, Math.abs(yB - yT));
      ctx.strokeRect(x, Math.min(yB, yT), w, Math.abs(yB - yT));
    });

    // Axes
    ctx.strokeStyle = COLORS.textMuted;
    ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(padding, toY(0)); ctx.lineTo(padding + plotWidth, toY(0)); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(padding, padding); ctx.lineTo(padding, padding + plotHeight); ctx.stroke();

    // Curve
    ctx.strokeStyle = COLORS.accent;
    ctx.lineWidth = 2;
    ctx.beginPath();
    let started = false;
    curve.x.forEach((xi, i) => {
      const yi = curve.y[i];
      if (!isFinite(yi)) return;
      if (!started) { ctx.moveTo(toX(xi), toY(yi)); started = true; }
      else ctx.lineTo(toX(xi), toY(yi));
    });
    ctx.stroke();

    // Labels
    ctx.fillStyle = COLORS.textMuted;
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'center';
    for (let i = 0; i <= 4; i++) {
      ctx.fillText((xMin + (i / 4) * (xMax - xMin)).toFixed(2), padding + i * plotWidth / 4, padding + plotHeight + 14);
    }
  }, [data]);

  return (
    <div style={{ width: '100%', height: '300px', background: COLORS.bg, borderRadius: '8px' }}>
      <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
};
