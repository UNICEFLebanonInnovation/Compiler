from django.contrib import admin
from .models import Bank, Certificate, University, Staffs
from student_registration.users.models import Login
# Register your models here.


admin.site.register(Bank)
admin.site.register(Certificate)
admin.site.register(University)
admin.site.register(Staffs)
admin.site.register(Login)

