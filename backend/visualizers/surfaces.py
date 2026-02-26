"""2D/3D surface visualization data generation."""

from __future__ import annotations

import math
import traceback
import torch
from sympy import lambdify, diff, Matrix, N

from backend.parsers import x, y, z, u, v, safe_parse, TORCH_MODULES, SCALAR_MODULES


def generate_2d_visualization_data(integrand_expr, region: dict, num_points: int = 50) -> dict:
    """Generate data for 2D integration visualization (volume under surface)."""
    try:
        f = lambdify((x, y), integrand_expr, modules=TORCH_MODULES)
        region_type = region.get('type', 'rectangle')

        if region_type == 'rectangle':
            x_min, x_max = float(region['x_min']), float(region['x_max'])
            y_min, y_max = float(region['y_min']), float(region['y_max'])
            x_vals = torch.linspace(x_min, x_max, num_points)
            y_vals = torch.linspace(y_min, y_max, num_points)
            X, Y = torch.meshgrid(x_vals, y_vals, indexing='xy')
            Z = f(X, Y)
            if not isinstance(Z, torch.Tensor):
                Z = torch.full_like(X, float(Z))
            mask = torch.ones_like(Z, dtype=torch.bool)

        elif region_type == 'disk':
            cx, cy = region.get('center', [0, 0])
            radius = float(region['radius'])
            x_vals = torch.linspace(cx - radius, cx + radius, num_points)
            y_vals = torch.linspace(cy - radius, cy + radius, num_points)
            X, Y = torch.meshgrid(x_vals, y_vals, indexing='xy')
            Z = f(X, Y)
            if not isinstance(Z, torch.Tensor):
                Z = torch.full_like(X, float(Z))
            mask = (X - cx)**2 + (Y - cy)**2 <= radius**2
            Z = torch.where(mask, Z, torch.tensor(float('nan')))

        elif region_type == 'type_1':
            x_min, x_max = float(region['x_min']), float(region['x_max'])
            y_lower_expr = safe_parse(region['y_lower'])
            y_upper_expr = safe_parse(region['y_upper'])
            y_lower_func = lambdify(x, y_lower_expr, modules=TORCH_MODULES)
            y_upper_func = lambdify(x, y_upper_expr, modules=TORCH_MODULES)
            x_test = torch.linspace(x_min, x_max, 100)
            y_lowers = y_lower_func(x_test)
            y_uppers = y_upper_func(x_test)
            if not isinstance(y_lowers, torch.Tensor):
                y_lowers = torch.full_like(x_test, float(y_lowers))
            if not isinstance(y_uppers, torch.Tensor):
                y_uppers = torch.full_like(x_test, float(y_uppers))
            y_min_val = float(y_lowers.min())
            y_max_val = float(y_uppers.max())
            x_vals = torch.linspace(x_min, x_max, num_points)
            y_vals = torch.linspace(y_min_val, y_max_val, num_points)
            X, Y = torch.meshgrid(x_vals, y_vals, indexing='xy')
            Z = f(X, Y)
            if not isinstance(Z, torch.Tensor):
                Z = torch.full_like(X, float(Z))
            Y_lower = y_lower_func(X)
            Y_upper = y_upper_func(X)
            if not isinstance(Y_lower, torch.Tensor):
                Y_lower = torch.full_like(X, float(Y_lower))
            if not isinstance(Y_upper, torch.Tensor):
                Y_upper = torch.full_like(X, float(Y_upper))
            mask = (Y >= Y_lower) & (Y <= Y_upper)
            Z = torch.where(mask, Z, torch.tensor(float('nan')))

        elif region_type == 'type_2':
            y_min, y_max = float(region['y_min']), float(region['y_max'])
            x_lower_expr = safe_parse(region['x_lower'])
            x_upper_expr = safe_parse(region['x_upper'])
            x_lower_func = lambdify(y, x_lower_expr, modules=TORCH_MODULES)
            x_upper_func = lambdify(y, x_upper_expr, modules=TORCH_MODULES)
            y_test = torch.linspace(y_min, y_max, 100)
            x_lowers = x_lower_func(y_test)
            x_uppers = x_upper_func(y_test)
            if not isinstance(x_lowers, torch.Tensor):
                x_lowers = torch.full_like(y_test, float(x_lowers))
            if not isinstance(x_uppers, torch.Tensor):
                x_uppers = torch.full_like(y_test, float(x_uppers))
            x_min_val = float(x_lowers.min())
            x_max_val = float(x_uppers.max())
            x_vals = torch.linspace(x_min_val, x_max_val, num_points)
            y_vals = torch.linspace(y_min, y_max, num_points)
            X, Y = torch.meshgrid(x_vals, y_vals, indexing='xy')
            Z = f(X, Y)
            if not isinstance(Z, torch.Tensor):
                Z = torch.full_like(X, float(Z))
            X_lower = x_lower_func(Y)
            X_upper = x_upper_func(Y)
            if not isinstance(X_lower, torch.Tensor):
                X_lower = torch.full_like(Y, float(X_lower))
            if not isinstance(X_upper, torch.Tensor):
                X_upper = torch.full_like(Y, float(X_upper))
            mask = (X >= X_lower) & (X <= X_upper)
            Z = torch.where(mask, Z, torch.tensor(float('nan')))

        elif region_type == 'inequality':
            condition_str = region['condition']
            x_min = float(region.get('x_min', -5))
            x_max = float(region.get('x_max', 5))
            y_min = float(region.get('y_min', -5))
            y_max = float(region.get('y_max', 5))
            x_vals = torch.linspace(x_min, x_max, num_points)
            y_vals = torch.linspace(y_min, y_max, num_points)
            X, Y = torch.meshgrid(x_vals, y_vals, indexing='xy')
            Z = f(X, Y)
            if not isinstance(Z, torch.Tensor):
                Z = torch.full_like(X, float(Z))
            if '<=' in condition_str:
                parts = condition_str.split('<=')
                left = safe_parse(parts[0])
                right = safe_parse(parts[1])
                left_func = lambdify((x, y), left, modules=TORCH_MODULES)
                right_func = lambdify((x, y), right, modules=TORCH_MODULES)
                mask = left_func(X, Y) <= right_func(X, Y)
            elif '>=' in condition_str:
                parts = condition_str.split('>=')
                left = safe_parse(parts[0])
                right = safe_parse(parts[1])
                left_func = lambdify((x, y), left, modules=TORCH_MODULES)
                right_func = lambdify((x, y), right, modules=TORCH_MODULES)
                mask = left_func(X, Y) >= right_func(X, Y)
            else:
                mask = torch.ones_like(Z, dtype=torch.bool)
            Z = torch.where(mask, Z, torch.tensor(float('nan')))
        else:
            raise ValueError(f"Unknown region type: {region_type}")

        Z = torch.nan_to_num(Z, nan=float('nan'), posinf=1e10, neginf=-1e10)
        boundary_points = generate_region_boundary(region, num_points=100)

        return {
            'surface': {'x': X.tolist(), 'y': Y.tolist(), 'z': Z.tolist()},
            'boundary': boundary_points,
            'region_type': region_type,
        }
    except Exception as e:
        traceback.print_exc()
        raise ValueError(f"Error generating 2D visualization: {str(e)}")


def generate_region_boundary(region: dict, num_points: int = 100) -> dict:
    """Generate boundary points for a 2D region."""
    region_type = region.get('type', 'rectangle')

    if region_type == 'rectangle':
        x_min, x_max = float(region['x_min']), float(region['x_max'])
        y_min, y_max = float(region['y_min']), float(region['y_max'])
        return {
            'x': [x_min, x_max, x_max, x_min, x_min],
            'y': [y_min, y_min, y_max, y_max, y_min],
        }
    elif region_type == 'disk':
        cx, cy = region.get('center', [0, 0])
        radius = float(region['radius'])
        theta_vals = torch.linspace(0, 2 * math.pi, num_points)
        return {
            'x': (cx + radius * torch.cos(theta_vals)).tolist(),
            'y': (cy + radius * torch.sin(theta_vals)).tolist(),
        }
    elif region_type == 'type_1':
        x_min, x_max = float(region['x_min']), float(region['x_max'])
        y_lower_func = lambdify(x, safe_parse(region['y_lower']), modules=SCALAR_MODULES)
        y_upper_func = lambdify(x, safe_parse(region['y_upper']), modules=SCALAR_MODULES)
        x_vals = torch.linspace(x_min, x_max, num_points // 2)
        lower_y = torch.tensor([float(y_lower_func(float(xi))) for xi in x_vals])
        upper_y = torch.tensor([float(y_upper_func(float(xi))) for xi in x_vals])
        boundary_x = torch.cat([x_vals, x_vals.flip(0), x_vals[:1]])
        boundary_y = torch.cat([lower_y, upper_y.flip(0), lower_y[:1]])
        return {'x': boundary_x.tolist(), 'y': boundary_y.tolist()}
    elif region_type == 'type_2':
        y_min, y_max = float(region['y_min']), float(region['y_max'])
        x_lower_func = lambdify(y, safe_parse(region['x_lower']), modules=SCALAR_MODULES)
        x_upper_func = lambdify(y, safe_parse(region['x_upper']), modules=SCALAR_MODULES)
        y_vals = torch.linspace(y_min, y_max, num_points // 2)
        lower_x = torch.tensor([float(x_lower_func(float(yi))) for yi in y_vals])
        upper_x = torch.tensor([float(x_upper_func(float(yi))) for yi in y_vals])
        boundary_x = torch.cat([lower_x, upper_x.flip(0), lower_x[:1]])
        boundary_y = torch.cat([y_vals, y_vals.flip(0), y_vals[:1]])
        return {'x': boundary_x.tolist(), 'y': boundary_y.tolist()}
    return {'x': [], 'y': []}


def generate_3d_visualization_data(integrand_expr, region: dict, num_points: int = 25) -> dict:
    """Generate data for 3D integration visualization."""
    try:
        f = lambdify((x, y, z), integrand_expr, modules=SCALAR_MODULES)
        region_type = region.get('type', 'box')

        if region_type == 'box':
            x_min, x_max = float(region['x_min']), float(region['x_max'])
            y_min, y_max = float(region['y_min']), float(region['y_max'])
            z_min, z_max = float(region['z_min']), float(region['z_max'])
            x_vals = torch.linspace(x_min, x_max, num_points)
            y_vals = torch.linspace(y_min, y_max, num_points)
            z_vals = torch.linspace(z_min, z_max, num_points)
            points = []
            values = []
            for xi in x_vals:
                for yi in y_vals:
                    for zi in z_vals:
                        points.append([float(xi), float(yi), float(zi)])
                        values.append(float(f(float(xi), float(yi), float(zi))))
            surfaces = generate_box_surfaces(x_min, x_max, y_min, y_max, z_min, z_max)

        elif region_type == 'sphere':
            cx, cy, cz = region.get('center', [0, 0, 0])
            radius = float(region['radius'])
            phi_vals = torch.linspace(0, math.pi, num_points)
            theta_vals = torch.linspace(0, 2 * math.pi, num_points)
            r_vals = torch.linspace(0, radius, num_points // 2)
            points = []
            values = []
            for ri in r_vals:
                for phi_i in phi_vals[::2]:
                    for theta_i in theta_vals[::2]:
                        xi = float(cx + ri * math.sin(float(phi_i)) * math.cos(float(theta_i)))
                        yi = float(cy + ri * math.sin(float(phi_i)) * math.sin(float(theta_i)))
                        zi = float(cz + ri * math.cos(float(phi_i)))
                        points.append([xi, yi, zi])
                        values.append(float(f(xi, yi, zi)))
            surfaces = generate_sphere_surface(cx, cy, cz, radius)

        elif region_type == 'cylinder':
            cx, cy = region.get('center', [0, 0])
            radius = float(region['radius'])
            z_min, z_max = float(region['z_min']), float(region['z_max'])
            theta_vals = torch.linspace(0, 2 * math.pi, num_points)
            r_vals = torch.linspace(0, radius, num_points // 2)
            z_vals = torch.linspace(z_min, z_max, num_points // 2)
            points = []
            values = []
            for ri in r_vals:
                for theta_i in theta_vals[::2]:
                    for zi in z_vals:
                        xi = float(cx + ri * math.cos(float(theta_i)))
                        yi = float(cy + ri * math.sin(float(theta_i)))
                        points.append([xi, yi, float(zi)])
                        values.append(float(f(xi, yi, float(zi))))
            surfaces = generate_cylinder_surface(cx, cy, radius, z_min, z_max)
        else:
            raise ValueError(f"Unknown 3D region type: {region_type}")

        values_tensor = torch.tensor(values)
        values_tensor = torch.nan_to_num(values_tensor, nan=0.0, posinf=1e10, neginf=-1e10)

        return {
            'points': points,
            'values': values_tensor.tolist(),
            'surfaces': surfaces,
            'region_type': region_type,
        }
    except Exception as e:
        traceback.print_exc()
        raise ValueError(f"Error generating 3D visualization: {str(e)}")


def generate_box_surfaces(x_min, x_max, y_min, y_max, z_min, z_max, n: int = 20) -> list:
    """Generate surface mesh data for a box."""
    surfaces = []
    x_vals = torch.linspace(x_min, x_max, n)
    y_vals = torch.linspace(y_min, y_max, n)
    z_vals = torch.linspace(z_min, z_max, n)

    X, Y = torch.meshgrid(x_vals, y_vals, indexing='xy')
    Z = torch.full_like(X, z_max)
    surfaces.append({'x': X.tolist(), 'y': Y.tolist(), 'z': Z.tolist(), 'name': 'front'})
    Z = torch.full_like(X, z_min)
    surfaces.append({'x': X.tolist(), 'y': Y.tolist(), 'z': Z.tolist(), 'name': 'back'})

    X, Z = torch.meshgrid(x_vals, z_vals, indexing='xy')
    Y = torch.full_like(X, y_max)
    surfaces.append({'x': X.tolist(), 'y': Y.tolist(), 'z': Z.tolist(), 'name': 'top'})
    Y = torch.full_like(X, y_min)
    surfaces.append({'x': X.tolist(), 'y': Y.tolist(), 'z': Z.tolist(), 'name': 'bottom'})

    Y, Z = torch.meshgrid(y_vals, z_vals, indexing='xy')
    X = torch.full_like(Y, x_max)
    surfaces.append({'x': X.tolist(), 'y': Y.tolist(), 'z': Z.tolist(), 'name': 'right'})
    X = torch.full_like(Y, x_min)
    surfaces.append({'x': X.tolist(), 'y': Y.tolist(), 'z': Z.tolist(), 'name': 'left'})
    return surfaces


def generate_sphere_surface(cx, cy, cz, radius, n: int = 30) -> list:
    """Generate surface mesh data for a sphere."""
    phi_arr = torch.linspace(0, math.pi, n)
    theta_arr = torch.linspace(0, 2 * math.pi, n)
    PHI, THETA = torch.meshgrid(phi_arr, theta_arr, indexing='xy')
    X = cx + radius * torch.sin(PHI) * torch.cos(THETA)
    Y = cy + radius * torch.sin(PHI) * torch.sin(THETA)
    Z = cz + radius * torch.cos(PHI)
    return [{'x': X.tolist(), 'y': Y.tolist(), 'z': Z.tolist(), 'name': 'sphere'}]


def generate_cylinder_surface(cx, cy, radius, z_min, z_max, n: int = 30) -> list:
    """Generate surface mesh data for a cylinder."""
    surfaces = []
    theta_arr = torch.linspace(0, 2 * math.pi, n)
    z_arr = torch.linspace(z_min, z_max, n)
    THETA, Z = torch.meshgrid(theta_arr, z_arr, indexing='xy')
    X = cx + radius * torch.cos(THETA)
    Y = cy + radius * torch.sin(THETA)
    surfaces.append({'x': X.tolist(), 'y': Y.tolist(), 'z': Z.tolist(), 'name': 'lateral'})

    r_arr = torch.linspace(0, radius, n // 2)
    R, THETA2 = torch.meshgrid(r_arr, theta_arr, indexing='xy')
    X = cx + R * torch.cos(THETA2)
    Y = cy + R * torch.sin(THETA2)
    Z = torch.full_like(X, z_max)
    surfaces.append({'x': X.tolist(), 'y': Y.tolist(), 'z': Z.tolist(), 'name': 'top'})
    Z = torch.full_like(X, z_min)
    surfaces.append({'x': X.tolist(), 'y': Y.tolist(), 'z': Z.tolist(), 'name': 'bottom'})
    return surfaces


def generate_surface_integral_visualization(
    surface: dict, u_range: list, v_range: list,
    vector_field=None, num_points: int = 30
) -> dict:
    """Generate visualization data for surface integrals."""
    try:
        x_uv = safe_parse(surface.get('x', 'u'))
        y_uv = safe_parse(surface.get('y', 'v'))
        z_uv = safe_parse(surface.get('z', '0'))

        x_func = lambdify((u, v), x_uv, modules=SCALAR_MODULES)
        y_func = lambdify((u, v), y_uv, modules=SCALAR_MODULES)
        z_func = lambdify((u, v), z_uv, modules=SCALAR_MODULES)

        u_start = float(N(safe_parse(str(u_range[0]))))
        u_end = float(N(safe_parse(str(u_range[1]))))
        v_start = float(N(safe_parse(str(v_range[0]))))
        v_end = float(N(safe_parse(str(v_range[1]))))

        u_vals = torch.linspace(u_start, u_end, num_points)
        v_vals = torch.linspace(v_start, v_end, num_points)

        # Evaluate surface point by point for scalar lambdify
        X = torch.zeros(num_points, num_points)
        Y = torch.zeros(num_points, num_points)
        Z = torch.zeros(num_points, num_points)
        for i, ui in enumerate(u_vals):
            for j, vi in enumerate(v_vals):
                X[j, i] = float(x_func(float(ui), float(vi)))
                Y[j, i] = float(y_func(float(ui), float(vi)))
                Z[j, i] = float(z_func(float(ui), float(vi)))

        X = torch.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
        Y = torch.nan_to_num(Y, nan=0.0, posinf=1e10, neginf=-1e10)
        Z = torch.nan_to_num(Z, nan=0.0, posinf=1e10, neginf=-1e10)

        from sympy import diff as sym_diff, Matrix as SymMatrix
        r_u = SymMatrix([sym_diff(x_uv, u), sym_diff(y_uv, u), sym_diff(z_uv, u)])
        r_v = SymMatrix([sym_diff(x_uv, v), sym_diff(y_uv, v), sym_diff(z_uv, v)])
        normal = r_u.cross(r_v)
        normal_funcs = [lambdify((u, v), normal[i], modules=SCALAR_MODULES) for i in range(3)]

        normals = []
        arrow_u = torch.linspace(u_start, u_end, 8)
        arrow_v = torch.linspace(v_start, v_end, 8)
        for ui in arrow_u:
            for vi in arrow_v:
                try:
                    xi = float(x_func(float(ui), float(vi)))
                    yi = float(y_func(float(ui), float(vi)))
                    zi = float(z_func(float(ui), float(vi)))
                    nx = float(normal_funcs[0](float(ui), float(vi)))
                    ny = float(normal_funcs[1](float(ui), float(vi)))
                    nz = float(normal_funcs[2](float(ui), float(vi)))
                    mag = math.sqrt(nx**2 + ny**2 + nz**2)
                    if mag > 1e-10 and all(math.isfinite(val) for val in [xi, yi, zi, nx, ny, nz]):
                        normals.append({
                            'origin': [xi, yi, zi],
                            'direction': [nx / mag, ny / mag, nz / mag],
                        })
                except Exception:
                    pass

        field_arrows = []
        if vector_field:
            from backend.parsers import x as sym_x, y as sym_y, z as sym_z
            Fx, Fy, Fz = vector_field
            Fx_func = lambdify((sym_x, sym_y, sym_z), Fx, modules=SCALAR_MODULES)
            Fy_func = lambdify((sym_x, sym_y, sym_z), Fy, modules=SCALAR_MODULES)
            Fz_func = lambdify((sym_x, sym_y, sym_z), Fz, modules=SCALAR_MODULES)
            for ui in arrow_u:
                for vi in arrow_v:
                    try:
                        xi = float(x_func(float(ui), float(vi)))
                        yi = float(y_func(float(ui), float(vi)))
                        zi = float(z_func(float(ui), float(vi)))
                        fx = float(Fx_func(xi, yi, zi))
                        fy = float(Fy_func(xi, yi, zi))
                        fz = float(Fz_func(xi, yi, zi))
                        if all(math.isfinite(val) for val in [fx, fy, fz]):
                            field_arrows.append({
                                'origin': [xi, yi, zi],
                                'direction': [fx, fy, fz],
                            })
                    except Exception:
                        pass

        return {
            'surface': {'x': X.tolist(), 'y': Y.tolist(), 'z': Z.tolist()},
            'normals': normals,
            'field_arrows': field_arrows,
            'u_range': [u_start, u_end],
            'v_range': [v_start, v_end],
        }
    except Exception as e:
        traceback.print_exc()
        raise ValueError(f"Surface visualization failed: {str(e)}")
