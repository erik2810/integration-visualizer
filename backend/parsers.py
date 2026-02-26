"""Expression parsing and validation."""

from __future__ import annotations

import logging
import math
from functools import lru_cache
from typing import Optional

import torch

from sympy import (
    symbols, sqrt, pi, sin, cos, tan, exp, log, Abs,
    oo, simplify, latex, parse_expr, Matrix, diff,
    atan2, acos, asin, sinh, cosh, tanh, sec, csc, cot, N
)
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor
)

from backend.config import Config

logger = logging.getLogger(__name__)

# Define symbolic variables
x, y, z, t, u, v, r, theta, phi = symbols('x y z t u v r theta phi', real=True)

# Parsing transformations
transformations = standard_transformations + (implicit_multiplication_application, convert_xor)

# Local dictionary for safe parsing
SAFE_LOCAL_DICT = {
    'x': x, 'y': y, 'z': z, 't': t, 'u': u, 'v': v,
    'r': r, 'theta': theta, 'phi': phi,
    'pi': pi, 'e': exp(1), 'inf': oo, 'sqrt': sqrt,
    'sin': sin, 'cos': cos, 'tan': tan, 'exp': exp, 'log': log,
    'abs': Abs, 'ln': log,
    'sinh': sinh, 'cosh': cosh, 'tanh': tanh,
    'asin': asin, 'acos': acos, 'atan': atan2,
    'sec': sec, 'csc': csc, 'cot': cot,
}

# Blocked patterns that could indicate code injection
BLOCKED_PATTERNS = [
    '__', 'import', 'exec', 'eval', 'compile', 'open', 'file',
    'os.', 'sys.', 'subprocess', 'lambda', 'class ', 'def ',
]

# Lambdify module mappings for PyTorch (vectorized tensor evaluation)
TORCH_MODULES = [{
    'sin': torch.sin, 'cos': torch.cos, 'tan': torch.tan,
    'exp': torch.exp, 'log': torch.log, 'sqrt': torch.sqrt,
    'Abs': torch.abs, 'asin': torch.asin, 'acos': torch.acos,
    'atan2': torch.atan2, 'sinh': torch.sinh, 'cosh': torch.cosh,
    'tanh': torch.tanh, 'pi': math.pi, 'sign': torch.sign,
}, 'math']

# Lambdify module mapping for scalar evaluation (scipy integration)
SCALAR_MODULES = ['math']


def validate_expression(expr_str: str) -> str:
    """Check length and blocked patterns."""
    if not isinstance(expr_str, str):
        raise ValueError("Expression must be a string")

    expr_str = expr_str.strip()

    if not expr_str:
        raise ValueError("Expression cannot be empty")

    if len(expr_str) > Config.MAX_EXPRESSION_LENGTH:
        raise ValueError(
            f"Expression too long ({len(expr_str)} chars). "
            f"Maximum is {Config.MAX_EXPRESSION_LENGTH}."
        )

    lowered = expr_str.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in lowered:
            raise ValueError(f"Expression contains blocked pattern: {pattern}")

    return expr_str


def safe_parse(expr_str: str):
    """Parse a math expression string into a sympy expr."""
    expr_str = validate_expression(str(expr_str))

    try:
        # Replace common notation
        expr_str = expr_str.replace('^', '**')
        expr_str = expr_str.replace('\u03c0', 'pi')  # π
        expr_str = expr_str.replace('\u221e', 'oo')   # ∞

        return parse_expr(
            expr_str,
            local_dict=SAFE_LOCAL_DICT,
            transformations=transformations
        )
    except Exception as e:
        raise ValueError(f"Could not parse expression: {expr_str}. Error: {str(e)}")


def parse_vector_field(field_dict: dict) -> tuple:
    """Parse {x, y, z} string components into sympy exprs."""
    if not isinstance(field_dict, dict):
        raise ValueError("Vector field must be a dict with 'x', 'y', 'z' components")

    fx = safe_parse(field_dict.get('x', '0'))
    fy = safe_parse(field_dict.get('y', '0'))
    fz = safe_parse(field_dict.get('z', '0'))
    return (fx, fy, fz)


def parse_bounds(value) -> object:
    """Parse a bound value (could be string or number)."""
    return safe_parse(str(value))
