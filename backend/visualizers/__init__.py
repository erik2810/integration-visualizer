"""Visualization data generation modules."""

from backend.visualizers.curves import generate_1d_visualization_data
from backend.visualizers.surfaces import (
    generate_2d_visualization_data,
    generate_3d_visualization_data,
    generate_surface_integral_visualization,
    generate_region_boundary,
    generate_box_surfaces,
    generate_sphere_surface,
    generate_cylinder_surface,
)
from backend.visualizers.vectors import (
    generate_vector_field_visualization,
    generate_line_integral_visualization,
)

__all__ = [
    'generate_1d_visualization_data',
    'generate_2d_visualization_data',
    'generate_3d_visualization_data',
    'generate_surface_integral_visualization',
    'generate_region_boundary',
    'generate_box_surfaces',
    'generate_sphere_surface',
    'generate_cylinder_surface',
    'generate_vector_field_visualization',
    'generate_line_integral_visualization',
]
