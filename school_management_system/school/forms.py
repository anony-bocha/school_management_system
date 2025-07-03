from django import forms
from .models import Subject, ClassRoom

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'classroom']

class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ['name', 'section', 'description']
