"""1D integration: single definite integrals."""

from __future__ import annotations

import logging
import traceback
from typing import Dict, Any, Optional

from sympy import integrate, simplify, latex, N, lambdify
from scipy import integrate as scipy_integrate

from backend.parsers import x, safe_parse, SCALAR_MODULES

logger = logging.getLogger(__name__)


def compute_integral_1d(integrand_expr, a, b) -> Dict[str, Any]:
    """Compute a 1D definite integral symbolically and numerically."""
    try:
        symbolic_result = integrate(integrand_expr, (x, a, b))
        symbolic_value = complex(N(symbolic_result))

        if symbolic_value.imag == 0:
            symbolic_value = symbolic_value.real

        f = lambdify(x, integrand_expr, modules=SCALAR_MODULES)
        numerical_result, error = scipy_integrate.quad(f, float(a), float(b))

        return {
            'symbolic': str(simplify(symbolic_result)),
            'symbolic_latex': latex(simplify(symbolic_result)),
            'numerical': float(numerical_result),
            'error': float(error),
        }
    except Exception as e:
        try:
            f = lambdify(x, integrand_expr, modules=SCALAR_MODULES)
            numerical_result, error = scipy_integrate.quad(f, float(a), float(b))
            return {
                'symbolic': 'Could not compute symbolic result',
                'symbolic_latex': r'\text{Could not compute}',
                'numerical': float(numerical_result),
                'error': float(error),
            }
        except Exception as e2:
            raise ValueError(f"Integration failed: {str(e2)}")


def generate_step_by_step_1d(integrand_expr, a, b) -> list:
    """Generate step-by-step solution for a 1D integral."""
    steps = []
    steps.append({
        'description': 'Set up the definite integral',
        'latex': f'\\int_{{{latex(a)}}}^{{{latex(b)}}} {latex(integrand_expr)} \\, dx'
    })

    antideriv = integrate(integrand_expr, x)
    steps.append({
        'description': 'Find the antiderivative',
        'latex': f'F(x) = {latex(simplify(antideriv))}'
    })

    upper_val = simplify(antideriv.subs(x, b))
    lower_val = simplify(antideriv.subs(x, a))
    steps.append({
        'description': 'Evaluate at the bounds',
        'latex': f'F({latex(b)}) - F({latex(a)}) = {latex(upper_val)} - {latex(lower_val)}'
    })

    result = simplify(upper_val - lower_val)
    steps.append({
        'description': 'Simplify',
        'latex': f'= {latex(result)}'
    })

    try:
        numerical = float(N(result))
        steps.append({
            'description': 'Numerical value',
            'latex': f'\\approx {numerical:.6f}'
        })
    except Exception:
        pass

    return steps
