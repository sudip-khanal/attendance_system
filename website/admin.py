from django.contrib import admin
from .models import User,StudentRecord,Attendance
# Register your models here.
admin.site.register(User)
admin.site.register(StudentRecord)
admin.site.register(Attendance)