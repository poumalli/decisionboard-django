"""Tests — dashboard/views.py : _ChartEncoder (sérialisation JSON pour Chart.js)."""

import json
from datetime import date
from decimal import Decimal

import pytest

from dashboard.views import _to_json


class TestChartEncoder:

    def test_encodes_decimal_as_float(self):
        assert json.loads(_to_json(Decimal("42.5"))) == 42.5

    def test_encodes_date_as_isoformat_string(self):
        assert json.loads(_to_json(date(2026, 1, 15))) == "2026-01-15"

    def test_unsupported_type_raises_type_error(self):
        with pytest.raises(TypeError):
            _to_json({1, 2, 3})
