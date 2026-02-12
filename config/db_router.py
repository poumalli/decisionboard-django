"""Routeur de base de données pour séparer OLTP et DW."""


class DWRouter:
    """Dirige les opérations sur les modèles `dw` vers la base DW."""

    route_app_labels = {"dw"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "dw"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "dw"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "dw"
        return None
