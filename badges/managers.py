from django.db import models

class BadgeManager(models.Manager):
    def active(self):
        import badges
        return self.get_query_set().filter(name__in=badges.registered_badges.keys())
        