"""Surface integrals: scalar surface integrals and flux integrals."""

from __future__ import annotations

import logging
import traceback
from typing import Dict, Any, Tuple

from sympy import integrate, simplify, latex, N, lambdify, sqrt, diff, Matrix
from scipy import integrate as scipy_integrate

from backend.parsers import x, y, z, u, v, safe_parse, SCALAR_MODULES

logger = logging.getLogger(__name__)


def compute_surface_integral_scalar(
    integrand_expr, surface: dict, u_range: list, v_range: list
) -> Dict[str, Any]:
    """Compute surface integral of scalar field: double-integral_S f dS."""
    try:
        x_uv = safe_parse(surface.get('x', 'u'))
        y_uv = safe_parse(surface.get('y', 'v'))
        z_uv = safe_parse(surface.get('z', '0'))

        u_start = safe_parse(str(u_range[0]))
        u_end = safe_parse(str(u_range[1]))
        v_start = safe_parse(str(v_range[0]))
        v_end = safe_parse(str(v_range[1]))

        r_u = Matrix([diff(x_uv, u), diff(y_uv, u), diff(z_uv, u)])
        r_v = Matrix([diff(x_uv, v), diff(y_uv, v), diff(z_uv, v)])

        cross_product = r_u.cross(r_v)
        dS = sqrt(cross_product[0]**2 + cross_product[1]**2 + cross_product[2]**2)

        integrand_on_surface = integrand_expr.subs([(x, x_uv), (y, y_uv), (z, z_uv)])
        full_integrand = integrand_on_surface * dS

        symbolic_result = integrate(full_integrand, (v, v_start, v_end), (u, u_start, u_end))

        f_numerical = lambdify((u, v), full_integrand, modules=SCALAR_MODULES)
        numerical_result, error = scipy_integrate.dblquad(
            f_numerical,
            float(u_start), float(u_end),
            lambda _u: float(v_start), lambda _u: float(v_end)
        )

        return {
            'symbolic': str(simplify(symbolic_result)),
            'symbolic_latex': latex(simplify(symbolic_result)),
            'numerical': float(numerical_result),
            'error': float(error),
            'normal_vector': [str(cross_product[i]) for i in range(3)],
            'dS_latex': latex(simplify(dS)),
        }
    except Exception as e:
        traceback.print_exc()
        raise ValueError(f"Surface integral computation failed: {str(e)}")


def compute_flux_integral(
    vector_field: Tuple, surface: dict, u_range: list, v_range: list
) -> Dict[str, Any]:
    """Compute flux integral: double-integral_S F . n dS."""
    try:
        Fx, Fy, Fz = vector_field

        x_uv = safe_parse(surface.get('x', 'u'))
        y_uv = safe_parse(surface.get('y', 'v'))
        z_uv = safe_parse(surface.get('z', '0'))

        u_start = safe_parse(str(u_range[0]))
        u_end = safe_parse(str(u_range[1]))
        v_start = safe_parse(str(v_range[0]))
        v_end = safe_parse(str(v_range[1]))

        r_u = Matrix([diff(x_uv, u), diff(y_uv, u), diff(z_uv, u)])
        r_v = Matrix([diff(x_uv, v), diff(y_uv, v), diff(z_uv, v)])
        cross_product = r_u.cross(r_v)

        Fx_on_surface = Fx.subs([(x, x_uv), (y, y_uv), (z, z_uv)])
        Fy_on_surface = Fy.subs([(x, x_uv), (y, y_uv), (z, z_uv)])
        Fz_on_surface = Fz.subs([(x, x_uv), (y, y_uv), (z, z_uv)])

        integrand = (
            Fx_on_surface * cross_product[0] +
            Fy_on_surface * cross_product[1] +
            Fz_on_surface * cross_product[2]
        )

        symbolic_result = integrate(integrand, (v, v_start, v_end), (u, u_start, u_end))

        f_numerical = lambdify((u, v), integrand, modules=SCALAR_MODULES)
        numerical_result, error = scipy_integrate.dblquad(
            f_numerical,
            float(u_start), float(u_end),
            lambda _u: float(v_start), lambda _u: float(v_end)
        )

        return {
            'symbolic': str(simplify(symbolic_result)),
            'symbolic_latex': latex(simplify(symbolic_result)),
            'numerical': float(numerical_result),
            'error': float(error),
            'normal_vector': [str(simplify(cross_product[i])) for i in range(3)],
            'integrand_latex': latex(simplify(integrand)),
        }
    except Exception as e:
        traceback.print_exc()
        raise ValueError(f"Flux integral computation failed: {str(e)}")
