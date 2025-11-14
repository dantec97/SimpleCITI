from django.apps import AppConfig


class InvestorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'investors'

    def ready(self):
        from django.db.models.signals import pre_save
        from django.core.exceptions import ValidationError
        from django.contrib.auth.models import User

        def require_email(sender, instance, **kwargs):
            if not instance.email:
                raise ValidationError("Email is required for all users.")

        pre_save.connect(require_email, sender=User)
