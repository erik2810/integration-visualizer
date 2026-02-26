"""Integration computation modules."""

from backend.integrators.single import compute_integral_1d
from backend.integrators.double import compute_integral_2d, compute_numerical_2d
from backend.integrators.triple import compute_integral_3d, compute_numerical_3d
from backend.integrators.line import compute_line_integral_scalar, compute_line_integral_vector
from backend.integrators.surface import compute_surface_integral_scalar, compute_flux_integral
from backend.integrators.vector_ops import (
    compute_divergence_field, compute_curl_field, compute_gradient_field
)

__all__ = [
    'compute_integral_1d',
    'compute_integral_2d', 'compute_numerical_2d',
    'compute_integral_3d', 'compute_numerical_3d',
    'compute_line_integral_scalar', 'compute_line_integral_vector',
    'compute_surface_integral_scalar', 'compute_flux_integral',
    'compute_divergence_field', 'compute_curl_field', 'compute_gradient_field',
]
