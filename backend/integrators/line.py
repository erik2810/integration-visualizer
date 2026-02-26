"""Line integrals: scalar and vector field line integrals."""

from __future__ import annotations

import logging
import traceback
from typing import Dict, Any, Tuple

from sympy import integrate, simplify, latex, N, lambdify, sqrt, diff
from scipy import integrate as scipy_integrate

from backend.parsers import x, y, z, t, safe_parse, SCALAR_MODULES

logger = logging.getLogger(__name__)


def compute_line_integral_scalar(integrand_expr, curve: dict, t_start, t_end) -> Dict[str, Any]:
    """Compute line integral of scalar field: integral_C f ds."""
    try:
        x_t = safe_parse(curve.get('x', 't'))
        y_t = safe_parse(curve.get('y', '0'))
        z_t = safe_parse(curve.get('z', '0'))
        t_start = safe_parse(str(t_start))
        t_end = safe_parse(str(t_end))

        dx_dt = diff(x_t, t)
        dy_dt = diff(y_t, t)
        dz_dt = diff(z_t, t)

        ds = sqrt(dx_dt**2 + dy_dt**2 + dz_dt**2)
        integrand_on_curve = integrand_expr.subs([(x, x_t), (y, y_t), (z, z_t)])
        full_integrand = integrand_on_curve * ds

        symbolic_result = integrate(full_integrand, (t, t_start, t_end))

        f_numerical = lambdify(t, full_integrand, modules=SCALAR_MODULES)
        numerical_result, error = scipy_integrate.quad(
            f_numerical, float(t_start), float(t_end)
        )

        return {
            'symbolic': str(simplify(symbolic_result)),
            'symbolic_latex': latex(simplify(symbolic_result)),
            'numerical': float(numerical_result),
            'error': float(error),
            'integrand_latex': latex(simplify(full_integrand)),
        }
    except Exception as e:
        traceback.print_exc()
        raise ValueError(f"Line integral computation failed: {str(e)}")


def compute_line_integral_vector(
    vector_field: Tuple, curve: dict, t_start, t_end
) -> Dict[str, Any]:
    """Compute line integral of vector field: integral_C F . dr (work integral)."""
    try:
        Fx, Fy, Fz = vector_field

        x_t = safe_parse(curve.get('x', 't'))
        y_t = safe_parse(curve.get('y', '0'))
        z_t = safe_parse(curve.get('z', '0'))
        t_start = safe_parse(str(t_start))
        t_end = safe_parse(str(t_end))

        dx_dt = diff(x_t, t)
        dy_dt = diff(y_t, t)
        dz_dt = diff(z_t, t)

        Fx_on_curve = Fx.subs([(x, x_t), (y, y_t), (z, z_t)])
        Fy_on_curve = Fy.subs([(x, x_t), (y, y_t), (z, z_t)])
        Fz_on_curve = Fz.subs([(x, x_t), (y, y_t), (z, z_t)])

        integrand = Fx_on_curve * dx_dt + Fy_on_curve * dy_dt + Fz_on_curve * dz_dt

        symbolic_result = integrate(integrand, (t, t_start, t_end))

        f_numerical = lambdify(t, integrand, modules=SCALAR_MODULES)
        numerical_result, error = scipy_integrate.quad(
            f_numerical, float(t_start), float(t_end)
        )

        return {
            'symbolic': str(simplify(symbolic_result)),
            'symbolic_latex': latex(simplify(symbolic_result)),
            'numerical': float(numerical_result),
            'error': float(error),
            'integrand_latex': latex(simplify(integrand)),
        }
    except Exception as e:
        traceback.print_exc()
        raise ValueError(f"Vector line integral computation failed: {str(e)}")
