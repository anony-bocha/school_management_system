










from django.shortcuts import render, redirect, get_object_or_404
from .models import student
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    students = student.objects.filter(user=request.user)
    return render(request, 'school/home.html', {'students': students})
@login_required
def submit_grade(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        student.objects.create(user=request.user, title=title, content=content)
        return redirect('home')
    return render(request, 'school/submit_grade.html')  # ✅ use this name


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            # show errors on form
            return render(request, 'registration/signup.html', {'form': form})
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})



