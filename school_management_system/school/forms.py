from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, ReadOnlyPasswordHashField

from .models import Grade, Attendance, Student, Teacher, Subject, ClassRoom, User

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for creating users with additional fields.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'is_active']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        user.is_active = self.cleaned_data['is_active']
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    """
    Custom form for updating users in admin/user edit views.
    """
    password = ReadOnlyPasswordHashField(help_text="Passwords are not stored raw. You can change it using <a href=\"../password/\">this form</a>.")

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'is_active', 'password']

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'subject', 'marks', 'grade']

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'  # Use 'exclude = [...]' if you want to omit any fields

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'gender', 'subjects', 'contact']
        widgets = {
            'subjects': forms.CheckboxSelectMultiple(),
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code']

class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ['name', 'section', 'subjects']
        widgets = {
            'subjects': forms.CheckboxSelectMultiple(),
        }
