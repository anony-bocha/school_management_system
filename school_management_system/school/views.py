from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Grade, ClassRoom, Subject, Teacher, Student, Attendance
from .forms import (
    GradeForm,
    ClassRoomForm,
    SubjectForm,
    TeacherForm,
    StudentForm,
    AttendanceForm,
)
from .decorators import role_required
from django.contrib.auth.views import LoginView, LogoutView

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Save role to profile
            role = form.cleaned_data['role']
            user.profile.role = role
            user.profile.save()
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'school/register.html', {'form': form})
class CustomLoginView(LoginView):
    template_name = 'school/login.html'

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        role = self.request.user.profile.role
        if role == 'student':
            return redirect('student_dashboard')
        elif role == 'teacher':
            return redirect('teacher_dashboard')
        else:
            return redirect('home')
# ---------- HOME ----------
@role_required(['ADMIN', 'TEACHER', 'STUDENT'])
def home(request):
    user = request.user
    context = {}

    if user.role == 'ADMIN':
        context = {
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(),
            'total_subjects': Subject.objects.count(),
            'total_classrooms': ClassRoom.objects.count(),
            'students': Student.objects.order_by('-id')[:10],
        }
    elif user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, name=user.get_full_name() or user.username)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher).distinct()
        students = Student.objects.filter(classroom__in=classrooms)
        context = {
            'classrooms': classrooms,
            'students': students,
        }
    else:  # STUDENT
        student = get_object_or_404(Student, name=user.get_full_name() or user.username)
        context = {
            'student': student,
        }

    return render(request, 'school/home.html', context)


# ---------- CLASSROOM VIEWS ----------
@role_required(['ADMIN', 'TEACHER'])
def classroom_list(request):
    user = request.user
    if user.role == 'ADMIN':
        classrooms = ClassRoom.objects.all()
    elif user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, name=user.get_full_name() or user.username)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher).distinct()
    else:
        return HttpResponseForbidden()

    return render(request, 'school/classroom_list.html', {'classrooms': classrooms})


@role_required(['ADMIN', 'TEACHER'])
def classroom_detail(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)

    user = request.user
    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, name=user.get_full_name() or user.username)
        if not classroom.subjects.filter(teachers=teacher).exists():
            return HttpResponseForbidden()

    students = Student.objects.filter(classroom=classroom)
    subjects = classroom.subjects.all()
    return render(
        request,
        'school/classroom_detail.html',
        {'classroom': classroom, 'students': students, 'subjects': subjects},
    )


@role_required(['ADMIN'])
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


@role_required(['ADMIN'])
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


@role_required(['ADMIN'])
def classroom_delete(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == 'POST':
        classroom.delete()
        messages.success(request, f"Classroom '{classroom.name}' deleted successfully.")
        return redirect('classroom_list')
    return render(request, 'school/classroom_confirm_delete.html', {'classroom': classroom})


# ---------- SUBJECT VIEWS ----------
@role_required(['ADMIN', 'TEACHER'])
def subject_list(request):
    subjects = Subject.objects.all()
    user = request.user
    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, name=user.get_full_name() or user.username)
        subjects = subjects.filter(teachers=teacher)

    query = request.GET.get('q')
    if query:
        subjects = subjects.filter(name__icontains=query) | subjects.filter(teachers__name__icontains=query)

    return render(request, 'school/subject_list.html', {'subjects': subjects})


@role_required(['ADMIN', 'TEACHER'])
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)

    user = request.user
    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, name=user.get_full_name() or user.username)
        if not subject.teachers.filter(pk=teacher.pk).exists():
            return HttpResponseForbidden()

    return render(request, 'school/subject_detail.html', {'subject': subject})


@role_required(['ADMIN'])
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


@role_required(['ADMIN'])
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


@role_required(['ADMIN'])
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, f"Subject '{subject.name}' deleted successfully.")
        return redirect('subject_list')
    return render(request, 'school/subject_confirm_delete.html', {'subject': subject})


# ---------- TEACHER VIEWS ----------
@role_required(['ADMIN'])
def teacher_list(request):
    query = request.GET.get('q', '')  # get search query or empty string
    if query:
        teachers = Teacher.objects.filter(name__icontains=query)
    else:
        teachers = Teacher.objects.all()
    context = {
        'teachers': teachers,
        'query': query,
    }
    return render(request, 'school/teacher_list.html', context)


@role_required(['ADMIN', 'TEACHER'])
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)

    user = request.user
    if user.role == 'TEACHER' and teacher.name != (user.get_full_name() or user.username):
        return HttpResponseForbidden()

    return render(request, 'school/teacher_detail.html', {'teacher': teacher})


@role_required(['ADMIN'])
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm()
    return render(request, 'school/teacher_form.html', {'form': form})


@role_required(['ADMIN'])
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_detail', pk=pk)
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'school/teacher_form.html', {'form': form})


@role_required(['ADMIN'])
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        return redirect('teacher_list')
    return render(request, 'school/teacher_confirm_delete.html', {'teacher': teacher})


# ---------- STUDENT VIEWS ----------
@role_required(['ADMIN', 'TEACHER', 'STUDENT'])
def student_list(request):
    user = request.user
    students = Student.objects.all()

    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, name=user.get_full_name() or user.username)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher).distinct()
        students = students.filter(classroom__in=classrooms)
    elif user.role == 'STUDENT':
        students = students.filter(name=user.get_full_name() or user.username)

    query = request.GET.get('q')
    classroom_id = request.GET.get('classroom')

    if query:
        students = students.filter(name__icontains=query)
    if classroom_id:
        students = students.filter(classroom_id=classroom_id)

    classrooms = ClassRoom.objects.all()
    return render(request, 'school/student_list.html', {'students': students, 'classrooms': classrooms})


@role_required(['ADMIN', 'TEACHER', 'STUDENT'])
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    user = request.user

    if user.role == 'STUDENT' and student.name != (user.get_full_name() or user.username):
        return HttpResponseForbidden()

    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, name=user.get_full_name() or user.username)
        if student.classroom not in ClassRoom.objects.filter(subjects__teachers=teacher):
            return HttpResponseForbidden()

    return render(request, 'school/student_detail.html', {'student': student})


@role_required(['ADMIN'])
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


@role_required(['ADMIN'])
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


@role_required(['ADMIN'])
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, f"Student '{student.name}' deleted successfully.")
        return redirect('student_list')
    return render(request, 'school/student_confirm_delete.html', {'student': student})


# ---------- GRADES VIEWS ----------
@role_required(['ADMIN', 'TEACHER'])
def grade_list(request):
    user = request.user
    grades = Grade.objects.select_related('student', 'subject').order_by('-id')

    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, name=user.get_full_name() or user.username)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher)
        grades = grades.filter(student__classroom__in=classrooms)

    return render(request, 'school/grade_list.html', {'grades': grades})


@role_required(['ADMIN', 'TEACHER'])
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


@role_required(['ADMIN', 'TEACHER'])
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


@role_required(['ADMIN', 'TEACHER'])
def grade_delete(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == 'POST':
        grade.delete()
        messages.success(request, 'Grade deleted successfully.')
        return redirect('grade_list')
    return render(request, 'school/grade_confirm_delete.html', {'grade': grade})


# ---------- ATTENDANCE VIEWS ----------
@role_required(['ADMIN', 'TEACHER'])
def attendance_list(request):
    attendances = Attendance.objects.all().order_by('-date')
    user = request.user

    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, name=user.get_full_name() or user.username)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher)
        attendances = attendances.filter(student__classroom__in=classrooms)

    query = request.GET.get('q')
    if query:
        attendances = attendances.filter(student__name__icontains=query)

    return render(request, 'school/attendance_list.html', {'attendances': attendances})


@role_required(['ADMIN', 'TEACHER'])
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance recorded successfully.")
            return redirect('attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'school/attendance_form.html', {'form': form, 'title': 'Record Attendance'})


@role_required(['ADMIN', 'TEACHER'])
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


@role_required(['ADMIN', 'TEACHER'])
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, "Attendance deleted successfully.")
        return redirect('attendance_list')
    return render(request, 'school/attendance_confirm_delete.html', {'attendance': attendance})
