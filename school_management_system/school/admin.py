from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ClassRoom, Subject, Teacher, Student

# Register the custom User model with Django's UserAdmin
admin.site.register(User, UserAdmin)

# Register other models with default admin
admin.site.register(ClassRoom)
admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Student)
