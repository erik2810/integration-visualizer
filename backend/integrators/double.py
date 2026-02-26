"""2D integration: double integrals over various region types."""

from __future__ import annotations

import logging
import math
import traceback
from typing import Dict, Any

from sympy import integrate, simplify, latex, N, lambdify, pi, sin, cos
from scipy import integrate as scipy_integrate

from backend.parsers import x, y, r, theta, safe_parse, SCALAR_MODULES

logger = logging.getLogger(__name__)


def compute_integral_2d(integrand_expr, region: dict) -> Dict[str, Any]:
    """Compute a 2D integral over a specified region."""
    try:
        region_type = region.get('type', 'rectangle')
        symbolic_result = None

        if region_type == 'rectangle':
            x_min = safe_parse(str(region['x_min']))
            x_max = safe_parse(str(region['x_max']))
            y_min = safe_parse(str(region['y_min']))
            y_max = safe_parse(str(region['y_max']))
            symbolic_result = integrate(integrand_expr, (y, y_min, y_max), (x, x_min, x_max))

        elif region_type == 'disk':
            cx, cy = region.get('center', [0, 0])
            radius = safe_parse(str(region['radius']))
            polar_integrand = integrand_expr.subs(
                [(x, r * cos(theta) + cx), (y, r * sin(theta) + cy)]
            ) * r
            symbolic_result = integrate(polar_integrand, (r, 0, radius), (theta, 0, 2 * pi))

        elif region_type == 'type_1':
            x_min = safe_parse(str(region['x_min']))
            x_max = safe_parse(str(region['x_max']))
            y_lower = safe_parse(region['y_lower'])
            y_upper = safe_parse(region['y_upper'])
            symbolic_result = integrate(integrand_expr, (y, y_lower, y_upper), (x, x_min, x_max))

        elif region_type == 'type_2':
            y_min = safe_parse(str(region['y_min']))
            y_max = safe_parse(str(region['y_max']))
            x_lower = safe_parse(region['x_lower'])
            x_upper = safe_parse(region['x_upper'])
            symbolic_result = integrate(integrand_expr, (x, x_lower, x_upper), (y, y_min, y_max))

        numerical_result = compute_numerical_2d(integrand_expr, region)

        if symbolic_result is not None:
            try:
                symbolic_value = float(N(symbolic_result))
            except Exception:
                symbolic_value = None

            return {
                'symbolic': str(simplify(symbolic_result)),
                'symbolic_latex': latex(simplify(symbolic_result)),
                'symbolic_value': symbolic_value,
                'numerical': numerical_result['value'],
                'error': numerical_result['error'],
            }
        else:
            return {
                'symbolic': 'Symbolic integration not available for this region type',
                'symbolic_latex': r'\text{N/A}',
                'numerical': numerical_result['value'],
                'error': numerical_result['error'],
            }

    except Exception as e:
        traceback.print_exc()
        try:
            numerical_result = compute_numerical_2d(integrand_expr, region)
            return {
                'symbolic': f'Symbolic integration failed: {str(e)}',
                'symbolic_latex': r'\text{Error}',
                'numerical': numerical_result['value'],
                'error': numerical_result['error'],
            }
        except Exception as e2:
            raise ValueError(f"Integration failed: {str(e2)}")


def compute_numerical_2d(integrand_expr, region: dict) -> Dict[str, float]:
    """Compute a 2D integral numerically."""
    f = lambdify((x, y), integrand_expr, modules=SCALAR_MODULES)
    region_type = region.get('type', 'rectangle')

    if region_type == 'rectangle':
        x_min, x_max = float(region['x_min']), float(region['x_max'])
        y_min, y_max = float(region['y_min']), float(region['y_max'])
        result, error = scipy_integrate.dblquad(
            f, x_min, x_max, lambda _x: y_min, lambda _x: y_max
        )

    elif region_type == 'disk':
        cx, cy = region.get('center', [0, 0])
        radius = float(region['radius'])

        def polar_f(theta_val, r_val):
            xi = cx + r_val * math.cos(theta_val)
            yi = cy + r_val * math.sin(theta_val)
            return f(xi, yi) * r_val

        result, error = scipy_integrate.dblquad(
            polar_f, 0, radius, lambda _r: 0, lambda _r: 2 * math.pi
        )

    elif region_type == 'type_1':
        x_min, x_max = float(region['x_min']), float(region['x_max'])
        y_lower_func = lambdify(x, safe_parse(region['y_lower']), modules=SCALAR_MODULES)
        y_upper_func = lambdify(x, safe_parse(region['y_upper']), modules=SCALAR_MODULES)
        result, error = scipy_integrate.dblquad(f, x_min, x_max, y_lower_func, y_upper_func)

    elif region_type == 'type_2':
        y_min, y_max = float(region['y_min']), float(region['y_max'])
        x_lower_func = lambdify(y, safe_parse(region['x_lower']), modules=SCALAR_MODULES)
        x_upper_func = lambdify(y, safe_parse(region['x_upper']), modules=SCALAR_MODULES)

        def f_swapped(y_val, x_val):
            return f(x_val, y_val)

        result, error = scipy_integrate.dblquad(f_swapped, y_min, y_max, x_lower_func, x_upper_func)

    else:
        raise ValueError(f"Numerical integration not implemented for region type: {region_type}")

    return {'value': float(result), 'error': float(error)}
