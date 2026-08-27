"""
Commande de gestion : crée les groupes Django Administrateur et Consultant.
Idempotent — peut être relancée sans risque.

Usage :
    python manage.py setup_groups
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crée les groupes Django Administrateur et Consultant (idempotent)."

    def handle(self, *args, **options):
        for name in ("Administrateur", "Consultant"):
            _, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Groupe '{name}' créé."))
            else:
                self.stdout.write(f"Groupe '{name}' existe déjà.")
