"""Theorem verification: Green's, Stokes', and Divergence theorems."""

from __future__ import annotations

import traceback
from typing import Dict, Any

from sympy import integrate, simplify, latex, N, lambdify, diff, pi
from scipy import integrate as scipy_integrate

from backend.parsers import x, y, z, t, safe_parse, parse_vector_field, SCALAR_MODULES
from backend.integrators.line import compute_line_integral_vector
from backend.integrators.surface import compute_flux_integral
from backend.integrators.triple import compute_integral_3d
from backend.integrators.vector_ops import compute_curl_field, compute_divergence_field
from backend.visualizers.vectors import generate_line_integral_visualization
from backend.visualizers.surfaces import generate_surface_integral_visualization


def verify_greens_theorem(data: dict) -> Dict[str, Any]:
    """Verify Green's Theorem: oint_C (P dx + Q dy) = iint_D (dQ/dx - dP/dy) dA."""
    P_str = data.get('P', '-y/2')
    Q_str = data.get('Q', 'x/2')
    curve = data.get('curve', {'x': 'cos(t)', 'y': 'sin(t)'})
    t_start = data.get('t_start', 0)
    t_end = data.get('t_end', '2*pi')

    P = safe_parse(P_str)
    Q = safe_parse(Q_str)

    x_t = safe_parse(curve.get('x', 'cos(t)'))
    y_t = safe_parse(curve.get('y', 'sin(t)'))
    t_start_val = safe_parse(str(t_start))
    t_end_val = safe_parse(str(t_end))

    dx_dt = diff(x_t, t)
    dy_dt = diff(y_t, t)

    P_on_curve = P.subs([(x, x_t), (y, y_t)])
    Q_on_curve = Q.subs([(x, x_t), (y, y_t)])

    line_integrand = P_on_curve * dx_dt + Q_on_curve * dy_dt
    line_integral_symbolic = integrate(line_integrand, (t, t_start_val, t_end_val))

    f_line = lambdify(t, line_integrand, modules=SCALAR_MODULES)
    line_integral_numerical, line_error = scipy_integrate.quad(
        f_line, float(N(t_start_val)), float(N(t_end_val))
    )

    dQ_dx = diff(Q, x)
    dP_dy = diff(P, y)
    curl_z = dQ_dx - dP_dy
    curl_z_simplified = simplify(curl_z)

    curve_viz = generate_line_integral_visualization(
        {'x': curve.get('x'), 'y': curve.get('y'), 'z': '0'},
        t_start, t_end,
    )

    return {
        'theorem': "Green's Theorem",
        'P': str(P),
        'Q': str(Q),
        'line_integral': {
            'symbolic': str(simplify(line_integral_symbolic)),
            'numerical': float(line_integral_numerical),
            'error': float(line_error),
        },
        'curl_z': str(curl_z_simplified),
        'curl_z_latex': latex(curl_z_simplified),
        'description': "oint(P dx + Q dy) = iint(dQ/dx - dP/dy) dA",
        'visualization': curve_viz,
    }


def verify_stokes_theorem(data: dict) -> Dict[str, Any]:
    """Verify Stokes' Theorem: oint_C F . dr = iint_S (nabla x F) . dS."""
    vector_field_dict = data.get('vector_field', {'x': '-y', 'y': 'x', 'z': '0'})
    surface = data.get('surface', {'x': 'u*cos(v)', 'y': 'u*sin(v)', 'z': '0'})
    curve = data.get('curve', {'x': 'cos(t)', 'y': 'sin(t)', 'z': '0'})
    u_range = data.get('u_range', [0, 1])
    v_range = data.get('v_range', [0, '2*pi'])
    t_start = data.get('t_start', 0)
    t_end = data.get('t_end', '2*pi')

    vector_field = parse_vector_field(vector_field_dict)
    line_result = compute_line_integral_vector(vector_field, curve, t_start, t_end)
    curl_F = compute_curl_field(vector_field)
    flux_result = compute_flux_integral(curl_F, surface, u_range, v_range)

    curve_viz = generate_line_integral_visualization(curve, t_start, t_end, vector_field)
    surface_viz = generate_surface_integral_visualization(surface, u_range, v_range)

    return {
        'theorem': "Stokes' Theorem",
        'vector_field': vector_field_dict,
        'curl_F': {'x': str(curl_F[0]), 'y': str(curl_F[1]), 'z': str(curl_F[2])},
        'line_integral': line_result,
        'surface_integral': flux_result,
        'verification': {
            'line': float(line_result['numerical']),
            'surface': float(flux_result['numerical']),
            'difference': abs(float(line_result['numerical']) - float(flux_result['numerical'])),
        },
        'description': "oint F.dr = iint(nabla x F).dS",
        'visualization': {'curve': curve_viz, 'surface': surface_viz},
    }


def verify_divergence_theorem(data: dict) -> Dict[str, Any]:
    """Verify Divergence Theorem: iint_S F . n dS = iiint_V (nabla . F) dV."""
    vector_field_dict = data.get('vector_field', {'x': 'x', 'y': 'y', 'z': 'z'})
    surface = data.get('surface', {'x': 'sin(u)*cos(v)', 'y': 'sin(u)*sin(v)', 'z': 'cos(u)'})
    volume_region = data.get('volume_region', {'type': 'sphere', 'center': [0, 0, 0], 'radius': 1})
    u_range = data.get('u_range', [0, 'pi'])
    v_range = data.get('v_range', [0, '2*pi'])

    vector_field = parse_vector_field(vector_field_dict)
    flux_result = compute_flux_integral(vector_field, surface, u_range, v_range)
    div_F = compute_divergence_field(vector_field)
    volume_result = compute_integral_3d(div_F, volume_region)

    surface_viz = generate_surface_integral_visualization(surface, u_range, v_range, vector_field)

    return {
        'theorem': 'Divergence Theorem',
        'vector_field': vector_field_dict,
        'divergence': str(div_F),
        'divergence_latex': latex(div_F),
        'flux_integral': flux_result,
        'volume_integral': volume_result,
        'verification': {
            'surface': float(flux_result['numerical']),
            'volume': float(volume_result['numerical']),
            'difference': abs(float(flux_result['numerical']) - float(volume_result['numerical'])),
        },
        'description': "iint F.n dS = iiint(nabla.F) dV",
        'visualization': surface_viz,
    }
