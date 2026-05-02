from django.contrib import admin
from .models import Department, Profile, Attendance, Leave, Payroll, Task

admin.site.register(Department)
admin.site.register(Profile)
admin.site.register(Attendance)
admin.site.register(Leave)
admin.site.register(Payroll)
admin.site.register(Task)
