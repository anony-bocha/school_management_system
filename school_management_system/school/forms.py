from django import forms
from .models import Grade, Attendance, Student, Teacher, Subject, ClassRoom
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

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
            'subjects': forms.CheckboxSelectMultiple(),  # Multi-select checkbox widget
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

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
