"""
Tests TDD — dashboard/models.py
#5 : BusinessSettings.delete() lève une exception explicite
"""

import pytest
from dashboard.models import BusinessSettings


class TestBusinessSettingsSingleton:
    @pytest.mark.django_db
    def test_load_creates_default_when_table_is_empty(self):
        obj = BusinessSettings.load()
        assert obj.pk == 1

    @pytest.mark.django_db
    def test_load_returns_existing_when_already_created(self):
        BusinessSettings.load()
        BusinessSettings.load()
        assert BusinessSettings.objects.count() == 1

    @pytest.mark.django_db
    def test_save_always_forces_pk_to_1(self):
        settings = BusinessSettings(monthly_revenue_target=99999)
        settings.save()
        assert settings.pk == 1
        assert BusinessSettings.objects.count() == 1

    @pytest.mark.django_db
    def test_delete_raises_permission_error(self):
        """#5 : delete() doit lever une exception, pas être silencieux."""
        settings = BusinessSettings.load()
        with pytest.raises(PermissionError):
            settings.delete()

    @pytest.mark.django_db
    def test_delete_does_not_remove_the_record(self):
        """L'instance doit toujours exister après tentative de suppression."""
        settings = BusinessSettings.load()
        try:
            settings.delete()
        except PermissionError:
            pass
        assert BusinessSettings.objects.filter(pk=1).exists()

    @pytest.mark.django_db
    def test_str_includes_update_date(self):
        settings = BusinessSettings.load()
        assert "Paramètres stratégiques" in str(settings)
