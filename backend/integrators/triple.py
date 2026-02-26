"""3D integration via Monte Carlo."""

from __future__ import annotations

import logging
import math
import traceback
from typing import Dict, Any

import torch
from sympy import integrate, simplify, latex, N, lambdify, pi, sin, cos

from backend.parsers import x, y, z, r, theta, phi, safe_parse, TORCH_MODULES
from backend.config import Config

logger = logging.getLogger(__name__)


def compute_integral_3d(integrand_expr, region: dict) -> Dict[str, Any]:
    """Compute a 3D integral over a specified region."""
    try:
        region_type = region.get('type', 'box')
        symbolic_result = None

        if region_type == 'box':
            x_min = safe_parse(str(region['x_min']))
            x_max = safe_parse(str(region['x_max']))
            y_min = safe_parse(str(region['y_min']))
            y_max = safe_parse(str(region['y_max']))
            z_min = safe_parse(str(region['z_min']))
            z_max = safe_parse(str(region['z_max']))
            symbolic_result = integrate(
                integrand_expr, (z, z_min, z_max), (y, y_min, y_max), (x, x_min, x_max)
            )

        elif region_type == 'sphere':
            cx, cy, cz = region.get('center', [0, 0, 0])
            radius = safe_parse(str(region['radius']))
            spherical_integrand = integrand_expr.subs([
                (x, cx + r * sin(phi) * cos(theta)),
                (y, cy + r * sin(phi) * sin(theta)),
                (z, cz + r * cos(phi))
            ]) * r**2 * sin(phi)
            symbolic_result = integrate(
                spherical_integrand, (r, 0, radius), (phi, 0, pi), (theta, 0, 2 * pi)
            )

        elif region_type == 'cylinder':
            cx, cy = region.get('center', [0, 0])
            radius = safe_parse(str(region['radius']))
            z_min = safe_parse(str(region['z_min']))
            z_max = safe_parse(str(region['z_max']))
            cylindrical_integrand = integrand_expr.subs([
                (x, cx + r * cos(theta)),
                (y, cy + r * sin(theta))
            ]) * r
            symbolic_result = integrate(
                cylindrical_integrand, (z, z_min, z_max), (r, 0, radius), (theta, 0, 2 * pi)
            )

        numerical_result = compute_numerical_3d(integrand_expr, region)

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
                'symbolic': 'Symbolic integration not available',
                'symbolic_latex': r'\text{N/A}',
                'numerical': numerical_result['value'],
                'error': numerical_result['error'],
            }

    except Exception as e:
        traceback.print_exc()
        try:
            numerical_result = compute_numerical_3d(integrand_expr, region)
            return {
                'symbolic': 'Symbolic integration failed',
                'symbolic_latex': r'\text{Error}',
                'numerical': numerical_result['value'],
                'error': numerical_result['error'],
            }
        except Exception as e2:
            raise ValueError(f"Integration failed: {str(e2)}")


def compute_numerical_3d(integrand_expr, region: dict) -> Dict[str, float]:
    """Monte Carlo integration in 3D."""
    f = lambdify((x, y, z), integrand_expr, modules=TORCH_MODULES)
    region_type = region.get('type', 'box')
    n_samples = Config.MAX_MONTE_CARLO_SAMPLES

    if region_type == 'box':
        x_min, x_max = float(region['x_min']), float(region['x_max'])
        y_min, y_max = float(region['y_min']), float(region['y_max'])
        z_min, z_max = float(region['z_min']), float(region['z_max'])
        volume = (x_max - x_min) * (y_max - y_min) * (z_max - z_min)
        xs = torch.rand(n_samples) * (x_max - x_min) + x_min
        ys = torch.rand(n_samples) * (y_max - y_min) + y_min
        zs = torch.rand(n_samples) * (z_max - z_min) + z_min
        values = f(xs, ys, zs)

    elif region_type == 'sphere':
        cx, cy, cz = region.get('center', [0, 0, 0])
        radius = float(region['radius'])
        volume = (4 / 3) * math.pi * radius**3

        # Direct spherical coordinate sampling (no rejection needed)
        rs = radius * torch.rand(n_samples).pow(1.0 / 3.0)
        cos_phi = torch.rand(n_samples) * 2 - 1
        sin_phi = torch.sqrt(1 - cos_phi**2)
        thetas = torch.rand(n_samples) * (2 * math.pi)

        xs = cx + rs * sin_phi * torch.cos(thetas)
        ys = cy + rs * sin_phi * torch.sin(thetas)
        zs = cz + rs * cos_phi
        values = f(xs, ys, zs)

    elif region_type == 'cylinder':
        cx, cy = region.get('center', [0, 0])
        radius = float(region['radius'])
        z_min, z_max = float(region['z_min']), float(region['z_max'])
        volume = math.pi * radius**2 * (z_max - z_min)

        rs = torch.sqrt(torch.rand(n_samples) * radius**2)
        thetas = torch.rand(n_samples) * (2 * math.pi)
        xs = cx + rs * torch.cos(thetas)
        ys = cy + rs * torch.sin(thetas)
        zs = torch.rand(n_samples) * (z_max - z_min) + z_min
        values = f(xs, ys, zs)

    else:
        raise ValueError(f"Unknown region type: {region_type}")

    if not isinstance(values, torch.Tensor):
        values = torch.tensor(values, dtype=torch.float64)
    values = torch.nan_to_num(values, nan=0.0, posinf=1e10, neginf=-1e10)
    mean_value = values.mean()
    std_value = values.std()

    result = volume * float(mean_value)
    error = volume * float(std_value) / math.sqrt(n_samples)

    return {'value': float(result), 'error': float(error)}
