from django.apps import AppConfig


class WellbeingConfig(AppConfig):
    name = 'student_registration.wellbeing'
    label = 'wellbeing'
    verbose_name = 'Makani child wellbeing flags'
    default_auto_field = 'django.db.models.AutoField'
