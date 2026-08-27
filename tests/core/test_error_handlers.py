"""Tests — core/views.py : handler404 / handler500.

Appelés directement (plutôt que via une requête HTTP) car DEBUG=True en
environnement de test empêche Django d'invoquer les handlers personnalisés.
"""

from django.test import RequestFactory

from core.views import handler404, handler500


class TestErrorHandlers:

    def test_handler404_renders_404_page(self):
        request = RequestFactory().get("/inexistant/")
        response = handler404(request, Exception("not found"))
        assert response.status_code == 404

    def test_handler500_renders_500_page(self):
        request = RequestFactory().get("/")
        response = handler500(request)
        assert response.status_code == 500
