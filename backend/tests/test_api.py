"""Tests for FastAPI API endpoints with MessagePack protocol."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from backend.tests.conftest import msgpack_post, msgpack_get


class TestHealthEndpoint:
    def test_health_check(self, client):
        response, data = msgpack_get(client, '/api/health')
        assert response.status_code == 200
        assert data['status'] == 'healthy'


class TestParseEndpoint:
    def test_parse_expression(self, client):
        response, data = msgpack_post(client, '/api/parse', {'expression': 'x^2 + 1'})
        assert response.status_code == 200
        assert data['success'] is True
        assert 'parsed' in data
        assert 'latex' in data

    def test_parse_invalid(self, client):
        response, data = msgpack_post(client, '/api/parse', {'expression': '+++'})
        assert response.status_code == 400

    def test_parse_blocked(self, client):
        response, data = msgpack_post(client, '/api/parse', {'expression': 'import os'})
        assert response.status_code == 400


class TestIntegrate1D:
    def test_basic_integral(self, client):
        response, data = msgpack_post(client, '/api/integrate/1d', {
            'integrand': 'x^2',
            'lower_bound': '0',
            'upper_bound': '1',
        })
        assert response.status_code == 200
        assert data['success'] is True
        assert abs(data['result']['numerical'] - 1/3) < 1e-6

    def test_with_steps(self, client):
        response, data = msgpack_post(client, '/api/integrate/1d', {
            'integrand': 'x^2',
            'lower_bound': '0',
            'upper_bound': '1',
            'include_steps': True,
        })
        assert data['success'] is True
        assert 'steps' in data

    def test_visualization_data(self, client):
        response, data = msgpack_post(client, '/api/integrate/1d', {
            'integrand': 'x',
            'lower_bound': '0',
            'upper_bound': '1',
        })
        assert 'visualization' in data
        assert 'curve' in data['visualization']
        assert 'rectangles' in data['visualization']


class TestIntegrate2D:
    def test_rectangle(self, client):
        response, data = msgpack_post(client, '/api/integrate/2d', {
            'integrand': '1',
            'region': {'type': 'rectangle', 'x_min': '0', 'x_max': '1', 'y_min': '0', 'y_max': '1'},
        })
        assert data['success'] is True
        assert abs(data['result']['numerical'] - 1.0) < 1e-6


class TestIntegrate3D:
    def test_box(self, client):
        response, data = msgpack_post(client, '/api/integrate/3d', {
            'integrand': '1',
            'region': {'type': 'box', 'x_min': '0', 'x_max': '1', 'y_min': '0', 'y_max': '1', 'z_min': '0', 'z_max': '1'},
        })
        assert data['success'] is True
        assert abs(data['result']['numerical'] - 1.0) < 1e-6


class TestVectorOperations:
    def test_gradient(self, client):
        response, data = msgpack_post(client, '/api/vector/operations', {
            'operation': 'gradient',
            'scalar_field': 'x^2 + y^2 + z^2',
        })
        assert data['success'] is True
        assert data['operation'] == 'gradient'
        assert 'result' in data

    def test_divergence(self, client):
        response, data = msgpack_post(client, '/api/vector/operations', {
            'operation': 'divergence',
            'vector_field': {'x': 'x', 'y': 'y', 'z': 'z'},
        })
        assert data['success'] is True
        assert data['result'] == '3'

    def test_curl(self, client):
        response, data = msgpack_post(client, '/api/vector/operations', {
            'operation': 'curl',
            'vector_field': {'x': '-y', 'y': 'x', 'z': '0'},
        })
        assert data['success'] is True


class TestExamples:
    def test_get_examples(self, client):
        response, data = msgpack_get(client, '/api/examples')
        assert response.status_code == 200
        assert '1d' in data
        assert '2d' in data
        assert '3d' in data


class TestExportLatex:
    def test_export_1d(self, client):
        response, data = msgpack_post(client, '/api/export/latex', {
            'integrand': 'x^2',
            'integral_type': '1d',
            'lower_bound': '0',
            'upper_bound': '1',
        })
        assert data['success'] is True
        assert 'latex' in data
        assert 'int' in data['latex']


class TestVectorFieldVisualization:
    def test_visualize(self, client):
        response, data = msgpack_post(client, '/api/visualize/vector_field', {
            'vector_field': {'x': '-y', 'y': 'x', 'z': '0'},
        })
        assert data['success'] is True
        assert 'visualization' in data
