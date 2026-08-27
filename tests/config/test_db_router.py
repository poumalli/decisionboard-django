"""Tests — config/db_router.py : DWRouter."""

from config.db_router import DWRouter
from core.models import Client
from dw.models import DimClient


class TestDWRouter:

    def test_db_for_read_routes_dw_models_to_dw(self):
        assert DWRouter().db_for_read(DimClient) == "dw"

    def test_db_for_read_leaves_core_models_unrouted(self):
        assert DWRouter().db_for_read(Client) is None

    def test_db_for_write_routes_dw_models_to_dw(self):
        assert DWRouter().db_for_write(DimClient) == "dw"

    def test_allow_relation_true_when_either_side_is_dw(self):
        assert DWRouter().allow_relation(DimClient(), DimClient()) is True

    def test_allow_relation_none_when_neither_side_is_dw(self):
        assert DWRouter().allow_relation(Client(), Client()) is None

    def test_allow_migrate_dw_app_only_on_dw_database(self):
        router = DWRouter()
        assert router.allow_migrate("dw", "dw") is True
        assert router.allow_migrate("default", "dw") is False

    def test_allow_migrate_other_apps_unrouted(self):
        assert DWRouter().allow_migrate("default", "core") is None
