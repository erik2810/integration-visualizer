"""Tests for expression parsing."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from sympy import sin, cos, exp, pi, sqrt, oo

from backend.parsers import (
    safe_parse, validate_expression, parse_vector_field, parse_bounds,
    x, y, z, t
)


class TestValidateExpression:
    def test_valid_expression(self):
        assert validate_expression("x^2 + y") == "x^2 + y"

    def test_empty_expression_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_expression("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_expression("   ")

    def test_non_string_raises(self):
        with pytest.raises(ValueError, match="must be a string"):
            validate_expression(123)

    def test_too_long_expression_raises(self):
        with pytest.raises(ValueError, match="too long"):
            validate_expression("x" * 600)

    def test_blocked_import_raises(self):
        with pytest.raises(ValueError, match="blocked pattern"):
            validate_expression("import os")

    def test_blocked_exec_raises(self):
        with pytest.raises(ValueError, match="blocked pattern"):
            validate_expression("exec('code')")

    def test_blocked_eval_raises(self):
        with pytest.raises(ValueError, match="blocked pattern"):
            validate_expression("eval('code')")

    def test_blocked_dunder_raises(self):
        with pytest.raises(ValueError, match="blocked pattern"):
            validate_expression("x.__class__")

    def test_blocked_os_raises(self):
        with pytest.raises(ValueError, match="blocked pattern"):
            validate_expression("os.system('ls')")


class TestSafeParse:
    def test_simple_polynomial(self):
        result = safe_parse("x^2 + 1")
        assert result == x**2 + 1

    def test_trig_functions(self):
        result = safe_parse("sin(x) + cos(y)")
        assert result == sin(x) + cos(y)

    def test_exponential(self):
        result = safe_parse("exp(x)")
        assert result == exp(x)

    def test_pi_symbol(self):
        result = safe_parse("pi")
        assert result == pi

    def test_sqrt(self):
        result = safe_parse("sqrt(x)")
        assert result == sqrt(x)

    def test_caret_as_power(self):
        result = safe_parse("x^3")
        assert result == x**3

    def test_multivariable(self):
        result = safe_parse("x*y + z")
        assert result == x * y + z


class TestParseVectorField:
    def test_basic_vector_field(self):
        result = parse_vector_field({'x': '-y', 'y': 'x', 'z': '0'})
        assert result == (-y, x, 0)

    def test_default_zeros(self):
        result = parse_vector_field({'x': 'x'})
        assert result[0] == x
        assert result[1] == 0
        assert result[2] == 0

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="must be a dict"):
            parse_vector_field("not a dict")


class TestParseBounds:
    def test_numeric_string(self):
        result = parse_bounds("3")
        assert result == 3

    def test_symbolic(self):
        result = parse_bounds("pi")
        assert result == pi

    def test_expression(self):
        result = parse_bounds("2*pi")
        assert result == 2 * pi

    def test_numeric(self):
        result = parse_bounds(5)
        assert result == 5
