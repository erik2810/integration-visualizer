"""Vector field visualization data generation."""

from __future__ import annotations

import math
import traceback
import torch
from sympy import lambdify, N

from backend.parsers import x, y, z, t, safe_parse, SCALAR_MODULES


def generate_vector_field_visualization(vector_field: tuple, region: dict, num_points: int = 8) -> dict:
    """Generate 3D vector field arrows for visualization."""
    try:
        Fx, Fy, Fz = vector_field
        Fx_func = lambdify((x, y, z), Fx, modules=SCALAR_MODULES)
        Fy_func = lambdify((x, y, z), Fy, modules=SCALAR_MODULES)
        Fz_func = lambdify((x, y, z), Fz, modules=SCALAR_MODULES)

        x_min = float(region.get('x_min', -2))
        x_max = float(region.get('x_max', 2))
        y_min = float(region.get('y_min', -2))
        y_max = float(region.get('y_max', 2))
        z_min = float(region.get('z_min', -2))
        z_max = float(region.get('z_max', 2))

        x_vals = torch.linspace(x_min, x_max, num_points)
        y_vals = torch.linspace(y_min, y_max, num_points)
        z_vals = torch.linspace(z_min, z_max, num_points)

        arrows = []
        for xi in x_vals:
            for yi in y_vals:
                for zi in z_vals:
                    try:
                        fx = float(Fx_func(float(xi), float(yi), float(zi)))
                        fy = float(Fy_func(float(xi), float(yi), float(zi)))
                        fz = float(Fz_func(float(xi), float(yi), float(zi)))
                        if all(math.isfinite(val) for val in [fx, fy, fz]):
                            arrows.append({
                                'origin': [float(xi), float(yi), float(zi)],
                                'direction': [fx, fy, fz],
                            })
                    except Exception:
                        pass

        return {'arrows': arrows, 'region': region}
    except Exception as e:
        traceback.print_exc()
        raise ValueError(f"Vector field visualization failed: {str(e)}")


def generate_line_integral_visualization(
    curve: dict, t_start, t_end, vector_field=None, num_points: int = 100
) -> dict:
    """Generate visualization data for line integrals."""
    try:
        x_t = safe_parse(curve.get('x', 't'))
        y_t = safe_parse(curve.get('y', '0'))
        z_t = safe_parse(curve.get('z', '0'))

        t_start_val = float(N(safe_parse(str(t_start))))
        t_end_val = float(N(safe_parse(str(t_end))))

        x_func = lambdify(t, x_t, modules=SCALAR_MODULES)
        y_func = lambdify(t, y_t, modules=SCALAR_MODULES)
        z_func = lambdify(t, z_t, modules=SCALAR_MODULES)

        t_vals = torch.linspace(t_start_val, t_end_val, num_points)
        curve_points = {
            'x': [float(x_func(float(ti))) for ti in t_vals],
            'y': [float(y_func(float(ti))) for ti in t_vals],
            'z': [float(z_func(float(ti))) for ti in t_vals],
        }

        arrows = []
        if vector_field:
            Fx, Fy, Fz = vector_field
            Fx_func = lambdify((x, y, z), Fx, modules=SCALAR_MODULES)
            Fy_func = lambdify((x, y, z), Fy, modules=SCALAR_MODULES)
            Fz_func = lambdify((x, y, z), Fz, modules=SCALAR_MODULES)

            arrow_step = max(1, num_points // 20)
            arrow_indices = list(range(0, num_points, arrow_step))
            for i in arrow_indices:
                xi = curve_points['x'][i]
                yi = curve_points['y'][i]
                zi = curve_points['z'][i]
                try:
                    fx = float(Fx_func(xi, yi, zi))
                    fy = float(Fy_func(xi, yi, zi))
                    fz = float(Fz_func(xi, yi, zi))
                    if all(math.isfinite(val) for val in [fx, fy, fz]):
                        arrows.append({
                            'origin': [xi, yi, zi],
                            'direction': [fx, fy, fz],
                        })
                except Exception:
                    pass

        return {
            'curve': curve_points,
            'arrows': arrows,
            't_range': [t_start_val, t_end_val],
        }
    except Exception as e:
        traceback.print_exc()
        raise ValueError(f"Line integral visualization failed: {str(e)}")
