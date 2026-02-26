"""Tests for integration modules."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
import math
from sympy import pi, sin, cos, exp

from backend.parsers import safe_parse, x, y, z, t
from backend.integrators.single import compute_integral_1d, generate_step_by_step_1d
from backend.integrators.double import compute_integral_2d
from backend.integrators.triple import compute_integral_3d
from backend.integrators.vector_ops import compute_gradient_field, compute_divergence_field, compute_curl_field


class TestIntegral1D:
    def test_polynomial(self):
        result = compute_integral_1d(x**2, 0, 1)
        assert abs(result['numerical'] - 1/3) < 1e-6

    def test_trig(self):
        result = compute_integral_1d(sin(x), 0, pi)
        assert abs(result['numerical'] - 2.0) < 1e-6

    def test_exponential(self):
        result = compute_integral_1d(exp(x), 0, 1)
        expected = math.e - 1
        assert abs(result['numerical'] - expected) < 1e-6

    def test_constant(self):
        result = compute_integral_1d(safe_parse('5'), 0, 3)
        assert abs(result['numerical'] - 15.0) < 1e-6

    def test_symbolic_result(self):
        result = compute_integral_1d(x**2, 0, 1)
        assert result['symbolic'] is not None

    def test_step_by_step(self):
        steps = generate_step_by_step_1d(x**2, 0, 1)
        assert isinstance(steps, list)
        assert len(steps) > 0


class TestIntegral2D:
    def test_rectangle_constant(self):
        result = compute_integral_2d(safe_parse('1'), {
            'type': 'rectangle', 'x_min': '0', 'x_max': '1', 'y_min': '0', 'y_max': '1'
        })
        assert abs(result['numerical'] - 1.0) < 1e-6

    def test_rectangle_polynomial(self):
        result = compute_integral_2d(x * y, {
            'type': 'rectangle', 'x_min': '0', 'x_max': '1', 'y_min': '0', 'y_max': '1'
        })
        assert abs(result['numerical'] - 0.25) < 1e-6

    def test_disk(self):
        # Area of unit disk = pi
        result = compute_integral_2d(safe_parse('1'), {
            'type': 'disk', 'center': [0, 0], 'radius': '1'
        })
        assert abs(result['numerical'] - math.pi) < 0.1


class TestIntegral3D:
    def test_box_constant(self):
        result = compute_integral_3d(safe_parse('1'), {
            'type': 'box', 'x_min': '0', 'x_max': '1', 'y_min': '0', 'y_max': '1', 'z_min': '0', 'z_max': '1'
        })
        assert abs(result['numerical'] - 1.0) < 1e-6

    def test_sphere_volume(self):
        # Volume of unit sphere = 4/3 * pi
        result = compute_integral_3d(safe_parse('1'), {
            'type': 'sphere', 'center': [0, 0, 0], 'radius': '1'
        })
        expected = 4/3 * math.pi
        assert abs(result['numerical'] - expected) < 0.5  # Monte Carlo has variance


class TestVectorOperations:
    def test_gradient_of_x2_y2_z2(self):
        grad = compute_gradient_field(x**2 + y**2 + z**2)
        assert grad[0] == 2*x
        assert grad[1] == 2*y
        assert grad[2] == 2*z

    def test_divergence_of_xyz(self):
        div = compute_divergence_field((x, y, z))
        assert div == 3

    def test_curl_of_rotation(self):
        # curl of (-y, x, 0) = (0, 0, 2)
        curl = compute_curl_field((-y, x, safe_parse('0')))
        assert curl[2] == 2

    def test_divergence_of_curl_is_zero(self):
        # div(curl F) = 0 for any F
        vf = (x*y, y*z, z*x)
        curl = compute_curl_field(vf)
        div_curl = compute_divergence_field(curl)
        from sympy import simplify
        assert simplify(div_curl) == 0
