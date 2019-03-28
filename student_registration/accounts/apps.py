from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'student_registration.accounts'
    # This function is the only new thing in this file
    # it just imports the signal file when the app is ready
    def ready(self):
        import student_registration.accounts.signals
