"""1D visualization: curve plots and Riemann sums."""

from __future__ import annotations

import torch
from sympy import lambdify

from backend.parsers import x, SCALAR_MODULES


def generate_1d_visualization_data(
    integrand_expr, a, b, num_points: int = 200, num_rectangles: int = 20
) -> dict:
    """Generate data for 1D integration visualization (area under curve)."""
    try:
        f = lambdify(x, integrand_expr, modules=SCALAR_MODULES)
        x_vals = torch.linspace(float(a), float(b), num_points)
        y_vals = torch.tensor([float(f(float(xi))) for xi in x_vals])
        y_vals = torch.nan_to_num(y_vals, nan=0.0, posinf=1e10, neginf=-1e10)

        rect_width = (float(b) - float(a)) / num_rectangles
        rectangles = []
        for i in range(num_rectangles):
            rect_x = float(a) + i * rect_width
            rect_height = float(f(rect_x + rect_width / 2))
            rectangles.append({
                'x': rect_x,
                'width': rect_width,
                'height': rect_height,
            })

        return {
            'curve': {'x': x_vals.tolist(), 'y': y_vals.tolist()},
            'rectangles': rectangles,
            'bounds': {'a': float(a), 'b': float(b)},
        }
    except Exception as e:
        raise ValueError(f"Error generating 1D visualization: {str(e)}")
