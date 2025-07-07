from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from .models import Grade
from .forms import GradeForm
from .models import ClassRoom, Subject, Teacher, Student
from .forms import ClassRoomForm, SubjectForm, TeacherForm, StudentForm
from .models import Attendance
from .forms import AttendanceForm
# ---------- HOME ----------
def home(request):
    students = Student.objects.all()
    total_students = students.count()
    total_teachers = Teacher.objects.count()
    total_subjects = Subject.objects.count()
    total_classrooms = ClassRoom.objects.count()

    return render(request, 'school/home.html', {
        'students': students,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_subjects': total_subjects,
        'total_classrooms': total_classrooms,
    })






# ---------- CLASSROOM VIEWS ----------
def classroom_list(request):
    classrooms = ClassRoom.objects.all()
    return render(request, 'school/classroom_list.html', {'classrooms': classrooms})

def classroom_detail(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    students = Student.objects.filter(classroom=classroom)
    subjects = Subject.objects.filter(classroom=classroom)
    return render(request, 'school/classroom_detail.html', {
        'classroom': classroom,
        'students': students,
        'subjects': subjects,
    })

def classroom_create(request):
    if request.method == 'POST':
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            classroom = form.save()
            messages.success(request, f"Classroom '{classroom.name}' created successfully.")
            return redirect('classroom_list')
    else:
        form = ClassRoomForm()
    return render(request, 'school/classroom_form.html', {'form': form, 'title': 'Add Classroom'})

def classroom_update(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == 'POST':
        form = ClassRoomForm(request.POST, instance=classroom)
        if form.is_valid():
            classroom = form.save()
            messages.success(request, f"Classroom '{classroom.name}' updated successfully.")
            return redirect('classroom_detail', pk=classroom.pk)
    else:
        form = ClassRoomForm(instance=classroom)
    return render(request, 'school/classroom_form.html', {'form': form, 'title': 'Edit Classroom'})

def classroom_delete(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == 'POST':
        classroom.delete()
        messages.success(request, f"Classroom '{classroom.name}' deleted successfully.")
        return redirect('classroom_list')
    return render(request, 'school/classroom_confirm_delete.html', {'classroom': classroom})

# ---------- SUBJECT VIEWS ----------
def subject_list(request):
    subjects = Subject.objects.all()
    query = request.GET.get('q')
    if query:
        subjects = subjects.filter(name__icontains=query) | subjects.filter(teacher__name__icontains=query)
    return render(request, 'school/subject_list.html', {'subjects': subjects})


def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    return render(request, 'school/subject_detail.html', {'subject': subject})

def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f"Subject '{subject.name}' created successfully.")
            return redirect('subject_list')
    else:
        form = SubjectForm()
    return render(request, 'school/subject_form.html', {'form': form, 'title': 'Add Subject'})

def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f"Subject '{subject.name}' updated successfully.")
            return redirect('subject_detail', pk=subject.pk)
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'school/subject_form.html', {'form': form, 'title': 'Edit Subject'})

def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, f"Subject '{subject.name}' deleted successfully.")
        return redirect('subject_list')
    return render(request, 'school/subject_confirm_delete.html', {'subject': subject})

# ---------- TEACHER VIEWS ----------def teacher_list(request):
def teacher_list(request):
    teachers = Teacher.objects.all()
    query = request.GET.get('q')
    if query:
        teachers = teachers.filter(name__icontains=query)
    return render(request, 'school/teacher_list.html', {'teachers': teachers})


def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, 'school/teacher_detail.html', {'teacher': teacher})

def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f"Teacher '{teacher.name}' created successfully.")
            return redirect('teacher_list')
    else:
        form = TeacherForm()
    return render(request, 'school/teacher_form.html', {'form': form, 'title': 'Add Teacher'})

def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f"Teacher '{teacher.name}' updated successfully.")
            return redirect('teacher_detail', pk=teacher.pk)
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'school/teacher_form.html', {'form': form, 'title': 'Edit Teacher'})

def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, f"Teacher '{teacher.name}' deleted successfully.")
        return redirect('teacher_list')
    return render(request, 'school/teacher_delete_confirm.html', {'teacher': teacher})

# ---------- STUDENT VIEWS ----------
def student_list(request):
    students = Student.objects.all()
    query = request.GET.get('q')
    classroom_id = request.GET.get('classroom')

    if query:
        students = students.filter(name__icontains=query)
    if classroom_id:
        students = students.filter(classroom_id=classroom_id)

    classrooms = ClassRoom.objects.all()
    return render(request, 'school/student_list.html', {
        'students': students,
        'classrooms': classrooms
    })


def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'school/student_detail.html', {'student': student})

def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student '{student.name}' created successfully.")
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'school/student_form.html', {'form': form, 'title': 'Add Student'})

def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student '{student.name}' updated successfully.")
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    return render(request, 'school/student_form.html', {'form': form, 'title': 'Edit Student'})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, f"Student '{student.name}' deleted successfully.")
        return redirect('student_list')
    return render(request, 'school/student_confirm_delete.html', {'student': student})




# ---------- GRADES VIEWS ----------
def grade_list(request):
    grades = Grade.objects.select_related('student', 'subject').order_by('-id')
    return render(request, 'school/grade_list.html', {'grades': grades})

def grade_create(request):
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade added successfully.')
            return redirect('grade_list')
    else:
        form = GradeForm()
    return render(request, 'school/grade_form.html', {'form': form, 'title': 'Add Grade'})

def grade_update(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade updated successfully.')
            return redirect('grade_list')
    else:
        form = GradeForm(instance=grade)
    return render(request, 'school/grade_form.html', {'form': form, 'title': 'Edit Grade'})

def grade_delete(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == 'POST':
        grade.delete()
        messages.success(request, 'Grade deleted successfully.')
        return redirect('grade_list')
    return render(request, 'school/grade_confirm_delete.html', {'grade': grade})



# ---------- ATTENDANCE VIEWS ----------

def attendance_list(request):
    attendances = Attendance.objects.all().order_by('-date')

    query = request.GET.get('q')
    if query:
        attendances = attendances.filter(student__name__icontains=query)

    return render(request, 'school/attendance_list.html', {'attendances': attendances})

def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            messages.success(request, "Attendance recorded successfully.")
            return redirect('attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'school/attendance_form.html', {'form': form, 'title': 'Record Attendance'})

def attendance_update(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance updated successfully.")
            return redirect('attendance_list')
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'school/attendance_form.html', {'form': form, 'title': 'Edit Attendance'})


def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, "Attendance deleted successfully.")
        return redirect('attendance_list')
    return render(request, 'school/attendance_confirm_delete.html', {'attendance': attendance})