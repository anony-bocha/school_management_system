from django import forms
from .models import Subject, ClassRoom
from .models import Teacher

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'gender', 'subjects', 'contact']
        widgets = {
            'subjects': forms.CheckboxSelectMultiple()
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'classroom']

class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ['name', 'section', 'description']
