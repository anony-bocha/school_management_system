from django.contrib import admin
from .models import ClassRoom, Subject, Teacher, Student
from django.contrib.auth.admin import UserAdmin
from .models import User

admin.site.register(User, UserAdmin)

admin.site.register(ClassRoom)
admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Student)
