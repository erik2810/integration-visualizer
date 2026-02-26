"""Vector calculus operations: gradient, divergence, curl."""

from __future__ import annotations

from sympy import diff, simplify

from backend.parsers import x, y, z


def compute_gradient_field(scalar_field) -> tuple:
    """Compute gradient of a scalar field: nabla f."""
    grad_x = diff(scalar_field, x)
    grad_y = diff(scalar_field, y)
    grad_z = diff(scalar_field, z)
    return (simplify(grad_x), simplify(grad_y), simplify(grad_z))


def compute_divergence_field(vector_field: tuple):
    """Compute divergence of a vector field: nabla . F."""
    Fx, Fy, Fz = vector_field
    div = diff(Fx, x) + diff(Fy, y) + diff(Fz, z)
    return simplify(div)


def compute_curl_field(vector_field: tuple) -> tuple:
    """Compute curl of a vector field: nabla x F."""
    Fx, Fy, Fz = vector_field
    curl_x = diff(Fz, y) - diff(Fy, z)
    curl_y = diff(Fx, z) - diff(Fz, x)
    curl_z = diff(Fy, x) - diff(Fx, y)
    return (simplify(curl_x), simplify(curl_y), simplify(curl_z))
