"""Tests — dw/models.py : représentations __str__ des dimensions et faits."""

import pytest


@pytest.mark.django_db(databases=["default", "dw"])
class TestDwModelStrRepresentations:

    def test_dim_date_str_is_the_date(self, dw_dataset):
        assert str(dw_dataset.date) == "2026-01-15"

    def test_dim_client_str_is_company_name(self, dw_dataset):
        assert str(dw_dataset.client) == "Client DW Test"

    def test_dim_employee_str_is_full_name(self, dw_dataset):
        assert str(dw_dataset.employee) == "Consultant DW Test"

    def test_dim_service_str_is_service_name(self, dw_dataset):
        assert str(dw_dataset.service) == "Service DW Test"

    def test_fact_sales_str_includes_appointment_id_and_amount(self, dw_dataset):
        assert str(dw_dataset) == "Vente 1 - 1000.00 CHF HT"
