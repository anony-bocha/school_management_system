from django.shortcuts import render, redirect, get_object_or_404
from .models import Student

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

@login_required
def home(request):
    students = Student.objects.all()  # or filter by something relevant later
    return render(request, 'school/home.html', {'students': students})

@login_required
def submit_student(request):
    if request.method == 'POST':
        name = request.POST['name']
        age = request.POST['age']
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')

        Student.objects.create(name=name, age=age, email=email)
        return redirect('home')
    return render(request, 'school/submit_student.html')  # Use this template

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'registration/register.html', {'form': form})
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
