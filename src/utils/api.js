import { encode, decode } from '@msgpack/msgpack';
import { getDemoResponse } from './demoData';

const API_BASE = '/api';
const MSGPACK_CONTENT_TYPE = 'application/x-msgpack';

// Demo mode: true when running on GitHub Pages (no backend)
const isDemo = typeof window !== 'undefined' && (
  window.location.hostname.endsWith('.github.io') ||
  window.location.search.includes('demo=1')
);

export function isDemoMode() {
  return isDemo;
}

async function realApiRequest(endpoint, body) {
  const encoded = encode(body);
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': MSGPACK_CONTENT_TYPE },
    body: encoded,
  });
  const buffer = await response.arrayBuffer();
  const data = decode(new Uint8Array(buffer));
  if (!data.success) {
    throw new Error(data.error || 'Computation failed');
  }
  return data;
}

function demoApiRequest(endpoint, body) {
  const data = getDemoResponse('POST', `/api${endpoint}`, body);
  if (!data) {
    throw new Error('This endpoint is not available in demo mode');
  }
  return data;
}

export async function apiRequest(endpoint, body) {
  if (isDemo) {
    // Simulate a small delay so the UI loading state is visible
    await new Promise(r => setTimeout(r, 300));
    return demoApiRequest(endpoint, body);
  }
  return realApiRequest(endpoint, body);
}

export async function fetchExamples() {
  if (isDemo) {
    const data = getDemoResponse('GET', '/api/examples');
    return data;
  }
  const response = await fetch(`${API_BASE}/examples`);
  const buffer = await response.arrayBuffer();
  return decode(new Uint8Array(buffer));
}

export function getComputeConfig(integralType, state) {
  const {
    integrand, bounds1D, region2D, region3D, vectorField, curve, tRange,
    surface, uRange, vRange, scalarField, vectorOp, theoremType, P_field, Q_field,
  } = state;

  switch (integralType) {
    case '1d':
      return { endpoint: '/integrate/1d', body: { integrand, lower_bound: bounds1D.lower, upper_bound: bounds1D.upper } };
    case '2d':
      return { endpoint: '/integrate/2d', body: { integrand, region: region2D } };
    case '3d':
      return { endpoint: '/integrate/3d', body: { integrand, region: region3D } };
    case 'line_scalar':
      return { endpoint: '/integrate/line/scalar', body: { integrand, curve, t_start: tRange.start, t_end: tRange.end } };
    case 'line_vector':
      return { endpoint: '/integrate/line/vector', body: { vector_field: vectorField, curve, t_start: tRange.start, t_end: tRange.end } };
    case 'surface_scalar':
      return { endpoint: '/integrate/surface/scalar', body: { integrand, surface, u_range: uRange, v_range: vRange } };
    case 'flux':
      return { endpoint: '/integrate/flux', body: { vector_field: vectorField, surface, u_range: uRange, v_range: vRange } };
    case 'vector_operations':
      return {
        endpoint: '/vector/operations',
        body: vectorOp === 'gradient'
          ? { operation: vectorOp, scalar_field: scalarField }
          : { operation: vectorOp, vector_field: vectorField },
      };
    case 'vector_fields':
    case 'physics':
      return { endpoint: '/visualize/vector_field', body: { vector_field: vectorField, region: { x_min: -2, x_max: 2, y_min: -2, y_max: 2, z_min: -2, z_max: 2 } } };
    case 'theorems': {
      if (theoremType === 'greens') {
        return { endpoint: '/theorem/greens', body: { P: P_field, Q: Q_field, curve: { x: curve.x, y: curve.y }, t_start: tRange.start, t_end: tRange.end } };
      } else if (theoremType === 'stokes') {
        return { endpoint: '/theorem/stokes', body: { vector_field: vectorField, surface, curve, u_range: uRange, v_range: vRange, t_start: tRange.start, t_end: tRange.end } };
      } else {
        return { endpoint: '/theorem/divergence', body: { vector_field: vectorField, surface, volume_region: region3D, u_range: uRange, v_range: vRange } };
      }
    }
    case 'field_lines':
      return { endpoint: '/physics/field_lines', body: { vector_field: vectorField, region: { x_min: -2, x_max: 2, y_min: -2, y_max: 2, z_min: -1, z_max: 1 }, num_lines: 25, steps: 150 } };
    default:
      throw new Error('Unknown integral type');
  }
}
