from django.shortcuts import render, get_object_or_404, redirect
from .models import ClassRoom, Subject, Teacher, Student
from django.http import HttpResponse
from .forms import ClassRoomForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import SubjectForm
from .models import Teacher
from .forms import TeacherForm





def delete_classroom(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == 'POST':
        classroom.delete()
        return redirect('classroom_list')
    return render(request, 'school/classroom_confirm_delete.html', {'classroom': classroom})

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
    return render(request, 'school/classroom_create.html', {'form': form})
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
    subjects = Subject.objects.all()
    return render(request, 'school/subject_list.html', {'subjects': subjects})

def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    return render(request, 'school/subject_detail.html', {'subject': subject})


def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subject_list')
    else:
        form = SubjectForm()
    return render(request, 'school/subject_create.html', {'form': form})

def subject_update(request, pk):
    return HttpResponse(f"Subject Update Placeholder for ID {pk}")

def subject_delete(request, pk):
    return HttpResponse(f"Subject Delete Placeholder for ID {pk}")

# ---------- TEACHER VIEWS ----------
def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'school/teacher_list.html', {'teachers': teachers})

def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, 'school/teacher_detail.html', {'teacher': teacher})


def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm()
    return render(request, 'school/teacher_form.html', {'form': form, 'title': 'Add Teacher'})

def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'school/teacher_form.html', {'form': form, 'title': 'Edit Teacher'})

def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        return redirect('teacher_list')
    return render(request, 'school/teacher_delete_confirm.html', {'teacher': teacher})

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
