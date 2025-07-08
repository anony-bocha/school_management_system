from django.apps import AppConfig
from django.db.models.signals import post_migrate

class SchoolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'school'

    def ready(self):
        from django.contrib.auth.models import Group
        from django.db.models.signals import post_migrate

        def create_user_groups(sender, **kwargs):
            Group.objects.get_or_create(name='Admin')
            Group.objects.get_or_create(name='Teacher')
            Group.objects.get_or_create(name='Student')

        post_migrate.connect(create_user_groups, sender=self)
