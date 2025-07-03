from django.shortcuts import render, get_object_or_404, redirect
from .models import ClassRoom, Subject, Teacher, Student
from django.http import HttpResponse
from .forms import ClassRoomForm





# Home page (students listing for now)
def home(request):
    return HttpResponse("Home Page - Students List Placeholder")

# ---------- CLASSROOM VIEWS ----------
def classroom_list(request):
    classrooms = ClassRoom.objects.all()
    return render(request, 'school/classroom_list.html', {'classrooms': classrooms})



def classroom_detail(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    students = Student.objects.filter(classroom=classroom)
    subjects = Subject.objects.filter(classroom=classroom)

    context = {
        'classroom': classroom,
        'students': students,
        'subjects': subjects,
    }
    return render(request, 'school/classroom_detail.html', context)


def classroom_create(request):
    if request.method == 'POST':
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('classroom_list')
    else:
        form = ClassRoomForm()
    return render(request, 'school/classroom_form.html', {'form': form})
def classroom_update(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == 'POST':
        form = ClassRoomForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            return redirect('classroom_detail', pk=classroom.pk)
    else:
        form = ClassRoomForm(instance=classroom)
    return render(request, 'school/classroom_update.html', {'form': form})


def classroom_delete(request, pk):
    return HttpResponse(f"Classroom Delete Placeholder for ID {pk}")

# ---------- SUBJECT VIEWS ----------
def subject_list(request):
    return HttpResponse("Subject List Placeholder")

def subject_detail(request, pk):
    return HttpResponse(f"Subject Detail Placeholder for ID {pk}")

def subject_create(request):
    return HttpResponse("Subject Create Placeholder")

def subject_update(request, pk):
    return HttpResponse(f"Subject Update Placeholder for ID {pk}")

def subject_delete(request, pk):
    return HttpResponse(f"Subject Delete Placeholder for ID {pk}")

# ---------- TEACHER VIEWS ----------
def teacher_list(request):
    return HttpResponse("Teacher List Placeholder")

def teacher_detail(request, pk):
    return HttpResponse(f"Teacher Detail Placeholder for ID {pk}")

def teacher_create(request):
    return HttpResponse("Teacher Create Placeholder")

def teacher_update(request, pk):
    return HttpResponse(f"Teacher Update Placeholder for ID {pk}")

def teacher_delete(request, pk):
    return HttpResponse(f"Teacher Delete Placeholder for ID {pk}")

# ---------- STUDENT VIEWS ----------
def student_list(request):
    return HttpResponse("Student List Placeholder")

def student_detail(request, pk):
    return HttpResponse(f"Student Detail Placeholder for ID {pk}")

def student_create(request):
    return HttpResponse("Student Create Placeholder")

def student_update(request, pk):
    return HttpResponse(f"Student Update Placeholder for ID {pk}")

def student_delete(request, pk):
    return HttpResponse(f"Student Delete Placeholder for ID {pk}")

# ---------- ATTENDANCE VIEWS ----------
def attendance_list(request):
    return HttpResponse("Attendance List Placeholder")

def attendance_create(request):
    return HttpResponse("Attendance Create Placeholder")

# ---------- GRADES VIEWS ----------
def grade_list(request):
    return HttpResponse("Grades List Placeholder")

def grade_create(request):
    return HttpResponse("Grade Create Placeholder")
