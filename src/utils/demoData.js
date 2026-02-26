/**
 * Pre-computed demo responses for GitHub Pages (no backend).
 * Each key maps to an API endpoint, values match the real response format.
 */

// ---- 1D: integral of x^2 from 0 to 1 ----
const DEMO_1D = {
  success: true,
  integrand: 'x**2',
  integrand_latex: 'x^{2}',
  bounds: { lower: '0', upper: '1' },
  result: {
    symbolic: '1/3',
    symbolic_latex: '\\frac{1}{3}',
    numerical: 0.333333,
    error: 3.7e-15,
  },
  visualization: {
    curve: {
      x: Array.from({ length: 200 }, (_, i) => i / 199),
      y: Array.from({ length: 200 }, (_, i) => (i / 199) ** 2),
    },
    rectangles: Array.from({ length: 20 }, (_, i) => {
      const x = i / 20;
      const mid = x + 0.025;
      return { x, width: 0.05, height: mid * mid };
    }),
    bounds: { a: 0, b: 1 },
  },
};

// ---- 2D: x^2+y^2 over [0,1]x[0,1] ----
function make2DSurface(n = 30) {
  const vals = Array.from({ length: n }, (_, i) => i / (n - 1));
  const zRows = vals.map(y => vals.map(x => x * x + y * y));
  return {
    x: vals.map(x => vals.map(() => x)),
    y: vals.map(() => [...vals]),
    z: zRows,
  };
}

const DEMO_2D = {
  success: true,
  integrand: 'x**2 + y**2',
  integrand_latex: 'x^{2} + y^{2}',
  region: { type: 'rectangle', x_min: 0, x_max: 1, y_min: 0, y_max: 1 },
  result: {
    symbolic: '2/3',
    symbolic_latex: '\\frac{2}{3}',
    numerical: 0.666667,
    error: 7.4e-15,
  },
  visualization: {
    surface: make2DSurface(),
    boundary: { x: [0, 1, 1, 0, 0], y: [0, 0, 1, 1, 0] },
    region_type: 'rectangle',
  },
};

// ---- 3D: 1 over unit box (volume = 1) ----
const DEMO_3D = {
  success: true,
  integrand: '1',
  integrand_latex: '1',
  region: { type: 'box', x_min: 0, x_max: 1, y_min: 0, y_max: 1, z_min: 0, z_max: 1 },
  result: {
    symbolic: '1',
    symbolic_latex: '1',
    numerical: 1.0,
    error: 0.001,
  },
  visualization: {
    points: [[0.5, 0.5, 0.5]],
    values: [1.0],
    surfaces: [
      { x: [[0, 1], [0, 1]], y: [[0, 0], [1, 1]], z: [[1, 1], [1, 1]], name: 'front' },
      { x: [[0, 1], [0, 1]], y: [[0, 0], [1, 1]], z: [[0, 0], [0, 0]], name: 'back' },
    ],
    region_type: 'box',
  },
};

// ---- Line scalar: arc length of unit circle = 2pi ----
const DEMO_LINE_SCALAR = {
  success: true,
  integral_type: 'line_scalar',
  integrand: '1',
  integrand_latex: '1',
  curve: { x: 'cos(t)', y: 'sin(t)', z: '0' },
  result: {
    symbolic: '2*pi',
    symbolic_latex: '2 \\pi',
    numerical: 6.283185,
    error: 1e-12,
    integrand_latex: '1',
  },
  visualization: {
    curve: {
      x: Array.from({ length: 100 }, (_, i) => Math.cos(2 * Math.PI * i / 99)),
      y: Array.from({ length: 100 }, (_, i) => Math.sin(2 * Math.PI * i / 99)),
      z: Array.from({ length: 100 }, () => 0),
    },
    arrows: [],
    t_range: [0, 6.283185],
  },
};

// ---- Line vector: circulation of (-y,x,0) around unit circle = 2pi ----
const DEMO_LINE_VECTOR = {
  success: true,
  integral_type: 'line_vector',
  vector_field: { x: '-y', y: 'x', z: '0' },
  vector_field_latex: { x: '- y', y: 'x', z: '0' },
  curve: { x: 'cos(t)', y: 'sin(t)', z: '0' },
  result: {
    symbolic: '2*pi',
    symbolic_latex: '2 \\pi',
    numerical: 6.283185,
    error: 1e-12,
    integrand_latex: '1',
  },
  visualization: {
    curve: DEMO_LINE_SCALAR.visualization.curve,
    arrows: Array.from({ length: 10 }, (_, i) => {
      const t = 2 * Math.PI * i / 10;
      const cx = Math.cos(t), sy = Math.sin(t);
      return { origin: [cx, sy, 0], direction: [-sy, cx, 0] };
    }),
    t_range: [0, 6.283185],
  },
};

// ---- Surface scalar: hemisphere area = 2pi ----
function makeHemisphere(n = 20) {
  const uVals = Array.from({ length: n }, (_, i) => (Math.PI / 2) * i / (n - 1));
  const vVals = Array.from({ length: n }, (_, i) => 2 * Math.PI * i / (n - 1));
  return {
    x: uVals.map(u => vVals.map(v => Math.sin(u) * Math.cos(v))),
    y: uVals.map(u => vVals.map(v => Math.sin(u) * Math.sin(v))),
    z: uVals.map(u => vVals.map(() => Math.cos(u))),
  };
}

const DEMO_SURFACE_SCALAR = {
  success: true,
  integral_type: 'surface_scalar',
  integrand: '1',
  integrand_latex: '1',
  surface: { x: 'sin(u)*cos(v)', y: 'sin(u)*sin(v)', z: 'cos(u)' },
  result: {
    symbolic: '2*pi',
    symbolic_latex: '2 \\pi',
    numerical: 6.283185,
    error: 1e-10,
    normal_vector: ['sin(u)**2*cos(v)', 'sin(u)**2*sin(v)', 'sin(u)*cos(u)'],
    dS_latex: '\\sin{\\left(u \\right)}',
  },
  visualization: {
    surface: makeHemisphere(),
    normals: [{ origin: [0, 0, 1], direction: [0, 0, 1] }],
    field_arrows: [],
    u_range: [0, Math.PI / 2],
    v_range: [0, 2 * Math.PI],
  },
};

// ---- Flux: radial field through hemisphere ----
const DEMO_FLUX = {
  success: true,
  integral_type: 'flux',
  vector_field: { x: 'x', y: 'y', z: 'z' },
  vector_field_latex: { x: 'x', y: 'y', z: 'z' },
  surface: { x: 'sin(u)*cos(v)', y: 'sin(u)*sin(v)', z: 'cos(u)' },
  result: {
    symbolic: '2*pi',
    symbolic_latex: '2 \\pi',
    numerical: 6.283185,
    error: 1e-10,
    normal_vector: ['sin(u)**2*cos(v)', 'sin(u)**2*sin(v)', 'sin(u)*cos(u)'],
    integrand_latex: '\\sin^{2}(u)',
  },
  visualization: {
    surface: makeHemisphere(),
    normals: [{ origin: [0, 0, 1], direction: [0, 0, 1] }],
    field_arrows: [{ origin: [1, 0, 0], direction: [1, 0, 0] }],
    u_range: [0, Math.PI / 2],
    v_range: [0, 2 * Math.PI],
  },
};

// ---- Vector operations: gradient of x^2+y^2+z^2 ----
const DEMO_VECTOR_OPS = {
  gradient: {
    success: true,
    operation: 'gradient',
    input: 'x**2 + y**2 + z**2',
    input_latex: 'x^{2} + y^{2} + z^{2}',
    result: { x: '2*x', y: '2*y', z: '2*z' },
    result_latex: { x: '2 x', y: '2 y', z: '2 z' },
  },
  divergence: {
    success: true,
    operation: 'divergence',
    input: { x: 'x', y: 'y', z: 'z' },
    result: '3',
    result_latex: '3',
  },
  curl: {
    success: true,
    operation: 'curl',
    input: { x: '-y', y: 'x', z: '0' },
    result: { x: '0', y: '0', z: '2' },
    result_latex: { x: '0', y: '0', z: '2' },
  },
};

// ---- Vector field viz ----
function makeVectorArrows() {
  const arrows = [];
  for (let xi = -2; xi <= 2; xi += 1) {
    for (let yi = -2; yi <= 2; yi += 1) {
      for (let zi = -2; zi <= 2; zi += 1) {
        arrows.push({ origin: [xi, yi, zi], direction: [-yi, xi, 0] });
      }
    }
  }
  return arrows;
}

const DEMO_VECTOR_FIELD = {
  success: true,
  vector_field: { x: '-y', y: 'x', z: '0' },
  visualization: {
    arrows: makeVectorArrows(),
    region: { x_min: -2, x_max: 2, y_min: -2, y_max: 2, z_min: -2, z_max: 2 },
  },
};

// ---- Theorems ----
const DEMO_GREENS = {
  success: true,
  theorem: "Green's Theorem",
  P: '-y/2',
  Q: 'x/2',
  line_integral: { symbolic: 'pi', numerical: 3.141593, error: 1e-12 },
  curl_z: '1',
  curl_z_latex: '1',
  description: "oint(P dx + Q dy) = iint(dQ/dx - dP/dy) dA",
  visualization: {
    curve: DEMO_LINE_SCALAR.visualization.curve,
    arrows: [],
    t_range: [0, 6.283185],
  },
};

const DEMO_STOKES = {
  success: true,
  theorem: "Stokes' Theorem",
  vector_field: { x: '-y', y: 'x', z: 'z**2' },
  curl_F: { x: '0', y: '0', z: '2' },
  line_integral: { symbolic: '2*pi', numerical: 6.283185, error: 1e-12 },
  surface_integral: { symbolic: '2*pi', numerical: 6.283185, error: 1e-10 },
  verification: { line: 6.283185, surface: 6.283185, difference: 1e-10 },
  description: "oint F.dr = iint(nabla x F).dS",
  visualization: { curve: DEMO_LINE_SCALAR.visualization, surface: DEMO_SURFACE_SCALAR.visualization },
};

const DEMO_DIVERGENCE = {
  success: true,
  theorem: 'Divergence Theorem',
  vector_field: { x: 'x', y: 'y', z: 'z' },
  divergence: '3',
  divergence_latex: '3',
  flux_integral: { symbolic: '4*pi', numerical: 12.566371, error: 0.01 },
  volume_integral: { symbolic: '4*pi', numerical: 12.566371, error: 0.05 },
  verification: { surface: 12.566371, volume: 12.566371, difference: 0.001 },
  description: "iint F.n dS = iiint(nabla.F) dV",
  visualization: DEMO_SURFACE_SCALAR.visualization,
};

// ---- Physics ----
const DEMO_FIELD_LINES = {
  success: true,
  field_lines: Array.from({ length: 8 }, (_, i) => {
    const angle = (2 * Math.PI * i) / 8;
    return Array.from({ length: 30 }, (_, j) => {
      const r = 0.3 + j * 0.05;
      const a = angle + j * 0.1;
      return [r * Math.cos(a), r * Math.sin(a), 0];
    });
  }),
  num_lines: 8,
  region: { x_min: -2, x_max: 2, y_min: -2, y_max: 2, z_min: -1, z_max: 1 },
};

const DEMO_EQUIPOTENTIAL = {
  success: true,
  scalar_field: 'x**2 + y**2',
  contour_data: {
    x: Array.from({ length: 50 }, (_, i) => -2 + 4 * i / 49),
    y: Array.from({ length: 50 }, (_, i) => -2 + 4 * i / 49),
    z: Array.from({ length: 50 }, (_, i) => {
      const y = -2 + 4 * i / 49;
      return Array.from({ length: 50 }, (_, j) => {
        const x = -2 + 4 * j / 49;
        return x * x + y * y;
      });
    }),
  },
  gradient_arrows: [
    { origin: [1, 0, 0], direction: [2, 0, 0] },
    { origin: [0, 1, 0], direction: [0, 2, 0] },
    { origin: [-1, 0, 0], direction: [-2, 0, 0] },
    { origin: [0, -1, 0], direction: [0, -2, 0] },
  ],
  z_min: 0,
  z_max: 8,
  num_levels: 10,
};

// ---- Parse ----
const DEMO_PARSE = {
  success: true,
  parsed: 'x**2',
  latex: 'x^{2}',
  simplified: 'x**2',
  simplified_latex: 'x^{2}',
};

// ---- Health ----
const DEMO_HEALTH = {
  status: 'healthy',
  message: 'Integration Visualizer API (demo mode)',
  version: '2.0.0',
};

// ---- Examples (same as backend) ----
import { DEMO_EXAMPLES } from './demoExamples';

// ---- LaTeX export ----
const DEMO_LATEX_EXPORT = {
  success: true,
  latex: '\\int_{0}^{1} x^{2} \\, dx = \\frac{1}{3}',
};

/**
 * Look up a pre-computed response for the given endpoint + body.
 * Returns null if no match (caller should show an error).
 */
export function getDemoResponse(method, path, body) {
  // GET endpoints
  if (method === 'GET') {
    if (path === '/api/health') return DEMO_HEALTH;
    if (path === '/api/examples') return DEMO_EXAMPLES;
    return null;
  }

  // POST endpoints
  if (path === '/api/parse') return DEMO_PARSE;
  if (path === '/api/integrate/1d') return DEMO_1D;
  if (path === '/api/integrate/2d') return DEMO_2D;
  if (path === '/api/integrate/3d') return DEMO_3D;
  if (path === '/api/integrate/line/scalar') return DEMO_LINE_SCALAR;
  if (path === '/api/integrate/line/vector') return DEMO_LINE_VECTOR;
  if (path === '/api/integrate/surface/scalar') return DEMO_SURFACE_SCALAR;
  if (path === '/api/integrate/flux') return DEMO_FLUX;

  if (path === '/api/vector/operations') {
    const op = body?.operation || 'gradient';
    return DEMO_VECTOR_OPS[op] || DEMO_VECTOR_OPS.gradient;
  }

  if (path === '/api/visualize/vector_field') return DEMO_VECTOR_FIELD;
  if (path === '/api/theorem/greens') return DEMO_GREENS;
  if (path === '/api/theorem/stokes') return DEMO_STOKES;
  if (path === '/api/theorem/divergence') return DEMO_DIVERGENCE;
  if (path === '/api/physics/field_lines') return DEMO_FIELD_LINES;
  if (path === '/api/physics/equipotential') return DEMO_EQUIPOTENTIAL;
  if (path === '/api/export/latex') return DEMO_LATEX_EXPORT;

  return null;
}
