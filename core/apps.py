from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        from django.db.models.signals import post_migrate

        post_migrate.connect(_create_default_groups, sender=self)


def _create_default_groups(sender, **kwargs):
    """Crée les groupes Django par défaut après chaque migrate."""
    from django.contrib.auth.models import Group

    for name in ("Administrateur", "Consultant"):
        Group.objects.get_or_create(name=name)
