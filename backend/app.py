"""FastAPI backend — msgpack endpoints for integration and visualization."""

import os
import sys
import logging
import math
import time
import traceback
from collections import defaultdict

import msgpack
import torch
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sympy import latex, N, lambdify

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config
from backend.parsers import safe_parse, parse_vector_field, x, y, z, t, u, v, SCALAR_MODULES, TORCH_MODULES
from backend.integrators import (
    compute_integral_1d,
    compute_integral_2d,
    compute_integral_3d,
    compute_line_integral_scalar,
    compute_line_integral_vector,
    compute_surface_integral_scalar,
    compute_flux_integral,
    compute_divergence_field,
    compute_curl_field,
    compute_gradient_field,
)
from backend.integrators.single import generate_step_by_step_1d
from backend.visualizers import (
    generate_1d_visualization_data,
    generate_2d_visualization_data,
    generate_3d_visualization_data,
    generate_surface_integral_visualization,
    generate_vector_field_visualization,
    generate_line_integral_visualization,
)
from backend.theorems import (
    verify_greens_theorem,
    verify_stokes_theorem,
    verify_divergence_theorem,
)
from backend.examples import get_examples

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Integration Visualizer API",
    version="2.0.0",
    docs_url="/api/docs",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS.split(',') if Config.CORS_ORIGINS != '*' else ['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory rate limiter
_rate_limit_store: dict[str, list[float]] = defaultdict(list)

MSGPACK_CONTENT_TYPE = 'application/x-msgpack'


def msgpack_response(data: dict, status_code: int = 200) -> Response:
    """Pack data as msgpack response."""
    return Response(
        content=msgpack.packb(data, use_bin_type=True),
        media_type=MSGPACK_CONTENT_TYPE,
        status_code=status_code,
    )


async def parse_msgpack_body(request: Request) -> dict:
    """Decode msgpack body, fall back to JSON."""
    content_type = request.headers.get('content-type', '')
    body = await request.body()
    if MSGPACK_CONTENT_TYPE in content_type:
        return msgpack.unpackb(body, raw=False)
    else:
        import json
        return json.loads(body)


def check_rate_limit(request: Request) -> bool:
    """True if under rate limit."""
    ip = request.client.host if request.client else 'unknown'
    now = time.time()
    window = 60

    _rate_limit_store[ip] = [
        ts for ts in _rate_limit_store[ip] if now - ts < window
    ]

    if len(_rate_limit_store[ip]) >= Config.RATE_LIMIT_PER_MINUTE:
        return False

    _rate_limit_store[ip].append(now)
    return True


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.debug(f"{request.method} {request.url.path}")
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration:.3f}s)")
    return response


@app.get('/api/health')
async def health_check():
    return msgpack_response({
        'status': 'healthy',
        'message': 'Integration Visualizer API is running',
        'version': '2.0.0',
    })


@app.post('/api/parse')
async def parse_expression(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        from sympy import simplify
        expr = safe_parse(data.get('expression', ''))
        return msgpack_response({
            'success': True, 'parsed': str(expr), 'latex': latex(expr),
            'simplified': str(simplify(expr)), 'simplified_latex': latex(simplify(expr)),
        })
    except Exception as e:
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/integrate/1d')
async def integrate_1d(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        a = safe_parse(str(data.get('lower_bound', 0)))
        b = safe_parse(str(data.get('upper_bound', 1)))
        integrand_expr = safe_parse(data.get('integrand', 'x'))
        result = compute_integral_1d(integrand_expr, a, b)
        viz_data = generate_1d_visualization_data(integrand_expr, a, b)
        response_data = {
            'success': True, 'integrand': str(integrand_expr),
            'integrand_latex': latex(integrand_expr),
            'bounds': {'lower': str(a), 'upper': str(b)},
            'result': result, 'visualization': viz_data,
        }
        if data.get('include_steps', False):
            try:
                response_data['steps'] = generate_step_by_step_1d(integrand_expr, a, b)
            except Exception:
                response_data['steps'] = []
        return msgpack_response(response_data)
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/integrate/2d')
async def integrate_2d(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        integrand_expr = safe_parse(data.get('integrand', '1'))
        region = data.get('region', {'type': 'rectangle', 'x_min': 0, 'x_max': 1, 'y_min': 0, 'y_max': 1})
        result = compute_integral_2d(integrand_expr, region)
        viz_data = generate_2d_visualization_data(integrand_expr, region)
        return msgpack_response({
            'success': True, 'integrand': str(integrand_expr),
            'integrand_latex': latex(integrand_expr),
            'region': region, 'result': result, 'visualization': viz_data,
        })
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/integrate/3d')
async def integrate_3d(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        integrand_expr = safe_parse(data.get('integrand', '1'))
        region = data.get('region', {'type': 'box', 'x_min': 0, 'x_max': 1, 'y_min': 0, 'y_max': 1, 'z_min': 0, 'z_max': 1})
        result = compute_integral_3d(integrand_expr, region)
        viz_data = generate_3d_visualization_data(integrand_expr, region)
        return msgpack_response({
            'success': True, 'integrand': str(integrand_expr),
            'integrand_latex': latex(integrand_expr),
            'region': region, 'result': result, 'visualization': viz_data,
        })
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/integrate/line/scalar')
async def integrate_line_scalar(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        integrand_expr = safe_parse(data.get('integrand', '1'))
        curve = data.get('curve', {'x': 't', 'y': '0', 'z': '0'})
        result = compute_line_integral_scalar(integrand_expr, curve, data.get('t_start', 0), data.get('t_end', 1))
        viz_data = generate_line_integral_visualization(curve, data.get('t_start', 0), data.get('t_end', 1))
        return msgpack_response({
            'success': True, 'integral_type': 'line_scalar',
            'integrand': str(integrand_expr), 'integrand_latex': latex(integrand_expr),
            'curve': curve, 'result': result, 'visualization': viz_data,
        })
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/integrate/line/vector')
async def integrate_line_vector(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        vf = parse_vector_field(data.get('vector_field', {'x': '1', 'y': '0', 'z': '0'}))
        curve = data.get('curve', {'x': 't', 'y': '0', 'z': '0'})
        result = compute_line_integral_vector(vf, curve, data.get('t_start', 0), data.get('t_end', 1))
        viz_data = generate_line_integral_visualization(curve, data.get('t_start', 0), data.get('t_end', 1), vf)
        return msgpack_response({
            'success': True, 'integral_type': 'line_vector',
            'vector_field': {k: str(c) for k, c in zip('xyz', vf)},
            'vector_field_latex': {k: latex(c) for k, c in zip('xyz', vf)},
            'curve': curve, 'result': result, 'visualization': viz_data,
        })
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/integrate/surface/scalar')
async def integrate_surface_scalar(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        integrand_expr = safe_parse(data.get('integrand', '1'))
        surface = data.get('surface', {'x': 'u', 'y': 'v', 'z': '0'})
        u_range, v_range = data.get('u_range', [0, 1]), data.get('v_range', [0, 1])
        result = compute_surface_integral_scalar(integrand_expr, surface, u_range, v_range)
        viz_data = generate_surface_integral_visualization(surface, u_range, v_range)
        return msgpack_response({
            'success': True, 'integral_type': 'surface_scalar',
            'integrand': str(integrand_expr), 'integrand_latex': latex(integrand_expr),
            'surface': surface, 'result': result, 'visualization': viz_data,
        })
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/integrate/flux')
async def integrate_flux(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        vf = parse_vector_field(data.get('vector_field', {'x': '0', 'y': '0', 'z': '1'}))
        surface = data.get('surface', {'x': 'u', 'y': 'v', 'z': '0'})
        u_range, v_range = data.get('u_range', [0, 1]), data.get('v_range', [0, 1])
        result = compute_flux_integral(vf, surface, u_range, v_range)
        viz_data = generate_surface_integral_visualization(surface, u_range, v_range, vf)
        return msgpack_response({
            'success': True, 'integral_type': 'flux',
            'vector_field': {k: str(c) for k, c in zip('xyz', vf)},
            'vector_field_latex': {k: latex(c) for k, c in zip('xyz', vf)},
            'surface': surface, 'result': result, 'visualization': viz_data,
        })
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/vector/operations')
async def vector_operations(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        operation = data.get('operation', 'divergence')
        if operation == 'gradient':
            sf = safe_parse(data.get('scalar_field', 'x^2 + y^2 + z^2'))
            grad = compute_gradient_field(sf)
            return msgpack_response({
                'success': True, 'operation': 'gradient',
                'input': str(sf), 'input_latex': latex(sf),
                'result': {k: str(c) for k, c in zip('xyz', grad)},
                'result_latex': {k: latex(c) for k, c in zip('xyz', grad)},
            })
        elif operation == 'divergence':
            vf = parse_vector_field(data.get('vector_field', {'x': 'x', 'y': 'y', 'z': 'z'}))
            div = compute_divergence_field(vf)
            return msgpack_response({
                'success': True, 'operation': 'divergence',
                'input': {k: str(c) for k, c in zip('xyz', vf)},
                'result': str(div), 'result_latex': latex(div),
            })
        elif operation == 'curl':
            vf = parse_vector_field(data.get('vector_field', {'x': '-y', 'y': 'x', 'z': '0'}))
            curl = compute_curl_field(vf)
            return msgpack_response({
                'success': True, 'operation': 'curl',
                'input': {k: str(c) for k, c in zip('xyz', vf)},
                'result': {k: str(c) for k, c in zip('xyz', curl)},
                'result_latex': {k: latex(c) for k, c in zip('xyz', curl)},
            })
        else:
            return msgpack_response({'success': False, 'error': f'Unknown operation: {operation}'}, 400)
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/visualize/vector_field')
async def visualize_vector_field(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        vf = parse_vector_field(data.get('vector_field', {'x': '-y', 'y': 'x', 'z': '0'}))
        region = data.get('region', {'x_min': -2, 'x_max': 2, 'y_min': -2, 'y_max': 2, 'z_min': -2, 'z_max': 2})
        viz_data = generate_vector_field_visualization(vf, region)
        return msgpack_response({
            'success': True,
            'vector_field': {k: str(c) for k, c in zip('xyz', vf)},
            'visualization': viz_data,
        })
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/theorem/greens')
async def api_verify_greens(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        return msgpack_response({'success': True, **verify_greens_theorem(data)})
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/theorem/stokes')
async def api_verify_stokes(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        return msgpack_response({'success': True, **verify_stokes_theorem(data)})
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/theorem/divergence')
async def api_verify_divergence(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        return msgpack_response({'success': True, **verify_divergence_theorem(data)})
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/physics/field_lines')
async def compute_field_lines(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        vf = parse_vector_field(data.get('vector_field', {'x': 'x', 'y': 'y', 'z': '0'}))
        start_points = data.get('start_points', None)
        region = data.get('region', {'x_min': -2, 'x_max': 2, 'y_min': -2, 'y_max': 2, 'z_min': -1, 'z_max': 1})
        num_lines = data.get('num_lines', 20)
        steps = data.get('steps', 100)
        step_size = data.get('step_size', 0.05)

        Fx_func = lambdify((x, y, z), vf[0], modules=SCALAR_MODULES)
        Fy_func = lambdify((x, y, z), vf[1], modules=SCALAR_MODULES)
        Fz_func = lambdify((x, y, z), vf[2], modules=SCALAR_MODULES)

        if start_points is None:
            x_min, x_max = float(region['x_min']), float(region['x_max'])
            y_min, y_max = float(region['y_min']), float(region['y_max'])
            z_val = (float(region.get('z_min', 0)) + float(region.get('z_max', 0))) / 2
            n_side = int(math.sqrt(num_lines))
            xs = torch.linspace(x_min + 0.2, x_max - 0.2, max(n_side, 1))
            ys = torch.linspace(y_min + 0.2, y_max - 0.2, max(n_side, 1))
            start_points = [[float(xi), float(yi), z_val] for xi in xs for yi in ys]

        field_lines = []
        for start in start_points[:num_lines]:
            line = [start]
            pos = [float(start[0]), float(start[1]), float(start[2])]
            for _ in range(steps):
                try:
                    fx = float(Fx_func(pos[0], pos[1], pos[2]))
                    fy = float(Fy_func(pos[0], pos[1], pos[2]))
                    fz = float(Fz_func(pos[0], pos[1], pos[2]))
                    mag = math.sqrt(fx**2 + fy**2 + fz**2)
                    if mag < 1e-10 or not math.isfinite(mag):
                        break
                    pos = [
                        pos[0] + step_size * fx / mag,
                        pos[1] + step_size * fy / mag,
                        pos[2] + step_size * fz / mag,
                    ]
                    if not (float(region['x_min']) <= pos[0] <= float(region['x_max']) and
                            float(region['y_min']) <= pos[1] <= float(region['y_max']) and
                            float(region['z_min']) <= pos[2] <= float(region['z_max'])):
                        break
                    line.append(list(pos))
                except Exception:
                    break
            if len(line) > 5:
                field_lines.append(line)

        return msgpack_response({
            'success': True, 'field_lines': field_lines,
            'num_lines': len(field_lines), 'region': region,
        })
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.post('/api/physics/equipotential')
async def compute_equipotential(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        scalar_field = safe_parse(data.get('scalar_field', 'x^2 + y^2'))
        region = data.get('region', {'x_min': -2, 'x_max': 2, 'y_min': -2, 'y_max': 2})
        num_levels = data.get('num_levels', 10)
        resolution = data.get('resolution', 50)

        f_func = lambdify((x, y), scalar_field.subs(z, 0), modules=TORCH_MODULES)
        x_min, x_max = float(region.get('x_min', -2)), float(region.get('x_max', 2))
        y_min, y_max = float(region.get('y_min', -2)), float(region.get('y_max', 2))

        X_arr = torch.linspace(x_min, x_max, resolution)
        Y_arr = torch.linspace(y_min, y_max, resolution)
        XX, YY = torch.meshgrid(X_arr, Y_arr, indexing='xy')
        ZZ = f_func(XX, YY)
        if not isinstance(ZZ, torch.Tensor):
            ZZ = torch.full_like(XX, float(ZZ))
        ZZ = torch.nan_to_num(ZZ, nan=0.0, posinf=1e10, neginf=-1e10)

        grad = compute_gradient_field(scalar_field.subs(z, 0))
        grad_x_func = lambdify((x, y), grad[0].subs(z, 0), modules=SCALAR_MODULES)
        grad_y_func = lambdify((x, y), grad[1].subs(z, 0), modules=SCALAR_MODULES)

        gradient_arrows = []
        for xi in torch.linspace(x_min, x_max, 10):
            for yi in torch.linspace(y_min, y_max, 10):
                try:
                    gx = float(grad_x_func(float(xi), float(yi)))
                    gy = float(grad_y_func(float(xi), float(yi)))
                    if math.isfinite(gx) and math.isfinite(gy) and (abs(gx) > 1e-10 or abs(gy) > 1e-10):
                        gradient_arrows.append({'origin': [float(xi), float(yi), 0], 'direction': [gx, gy, 0]})
                except Exception:
                    pass

        return msgpack_response({
            'success': True, 'scalar_field': str(scalar_field),
            'contour_data': {'x': X_arr.tolist(), 'y': Y_arr.tolist(), 'z': ZZ.tolist()},
            'gradient_arrows': gradient_arrows,
            'z_min': float(ZZ.min()), 'z_max': float(ZZ.max()), 'num_levels': num_levels,
        })
    except Exception as e:
        traceback.print_exc()
        return msgpack_response({'success': False, 'error': str(e)}, 400)


@app.get('/api/examples')
async def api_get_examples():
    return msgpack_response(get_examples())


@app.post('/api/export/latex')
async def export_latex(request: Request):
    if not check_rate_limit(request):
        return msgpack_response({
            'success': False,
            'error': 'Rate limit exceeded. Please wait before making more requests.',
        }, 429)
    try:
        data = await parse_msgpack_body(request)
        integrand_expr = safe_parse(data.get('integrand', 'x^2'))
        integrand_ltx = latex(integrand_expr)
        integral_type = data.get('integral_type', '1d')
        result = data.get('result', {})

        if integral_type == '1d':
            latex_str = f"\\int_{{{data.get('lower_bound', '0')}}}^{{{data.get('upper_bound', '1')}}} {integrand_ltx} \\, dx"
        elif integral_type == '2d':
            latex_str = f"\\iint_D {integrand_ltx} \\, dA"
        elif integral_type == '3d':
            latex_str = f"\\iiint_V {integrand_ltx} \\, dV"
        else:
            latex_str = integrand_ltx

        if result.get('symbolic_latex'):
            latex_str += f" = {result['symbolic_latex']}"
        elif result.get('symbolic'):
            latex_str += f" = {result['symbolic']}"

        return msgpack_response({'success': True, 'latex': latex_str})
    except Exception as e:
        return msgpack_response({'success': False, 'error': str(e)}, 400)


if __name__ == '__main__':
    import uvicorn
    logger.info(f"Starting Integration Visualizer API on {Config.HOST}:{Config.PORT}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    uvicorn.run(
        "backend.app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
    )
