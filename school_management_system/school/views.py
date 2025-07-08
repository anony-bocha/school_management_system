from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView, LogoutView
from django import forms
from functools import wraps
from django.contrib.auth.decorators import login_required

from .models import Grade, ClassRoom, Subject, Teacher, Student, Attendance, User
from .forms import (
    GradeForm, ClassRoomForm, SubjectForm,
    TeacherForm, StudentForm, AttendanceForm,
    CustomUserCreationForm
)
from .decorators import role_required


def no_permission(request):
    return HttpResponseForbidden("You do not have permission to access this page.")


def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('login')
            user_role = getattr(user, 'role', None)
            if user.is_superuser or (user_role and user_role.upper() in [r.upper() for r in allowed_roles]):
                return view_func(request, *args, **kwargs)
            return redirect('no_permission')
        return wrapper
    return decorator


# ---------- USER REGISTRATION ----------
class UserRegistrationForm(CustomUserCreationForm):
    class Meta(CustomUserCreationForm.Meta):
        model = User
        fields = CustomUserCreationForm.Meta.fields + ["email"]


# ---------- AUTH VIEWS ----------
class CustomLoginView(LoginView):
    template_name = 'school/login.html'

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        return redirect('role_redirect')


class CustomLogoutView(LogoutView):
    next_page = 'login'


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'school/register.html', {'form': form})


@login_required
def role_redirect(request):
    user = request.user
    if user.is_superuser or user.role == 'ADMIN':
        return redirect('school:admin_dashboard')
    elif user.role == 'TEACHER':
        return redirect('school:teacher_dashboard')
    elif user.role == 'STUDENT':
        return redirect('school:student_dashboard')
    else:
        return redirect('school:no_permission')


# ---------- HOME DASHBOARD ----------
@login_required
def home(request):
    user = request.user
    is_admin_or_teacher = user.is_superuser or user.groups.filter(name__in=['Admin', 'Teacher']).exists()

    context = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_classrooms': ClassRoom.objects.count(),
        'students': Student.objects.all(),
        'is_admin_or_teacher': is_admin_or_teacher,
    }
    return render(request, 'school/home.html', context)


# ---------- CLASSROOM VIEWS ----------
@role_required(['Admin', 'Teacher'])
def classroom_list(request):
    user = request.user
    if user.is_superuser or user.role == 'ADMIN':
        classrooms = ClassRoom.objects.all()
    elif user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher).distinct()
    else:
        return HttpResponseForbidden()
    return render(request, 'school/classroom_list.html', {'classrooms': classrooms})


@role_required(['Admin', 'Teacher'])
def classroom_detail(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    user = request.user

    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        if not classroom.subjects.filter(teachers=teacher).exists():
            return HttpResponseForbidden()

    students = Student.objects.filter(classroom=classroom)
    subjects = classroom.subjects.all()
    return render(request, 'school/classroom_detail.html', {
        'classroom': classroom,
        'students': students,
        'subjects': subjects,
    })


@role_required(['Admin'])
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


@role_required(['Admin'])
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


@role_required(['Admin'])
def classroom_delete(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == 'POST':
        classroom.delete()
        messages.success(request, f"Classroom '{classroom.name}' deleted successfully.")
        return redirect('classroom_list')
    return render(request, 'school/classroom_confirm_delete.html', {'classroom': classroom})


# ---------- SUBJECT VIEWS ----------
@role_required(['Admin', 'Teacher'])
def subject_list(request):
    user = request.user
    subjects = Subject.objects.all()
    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        subjects = subjects.filter(teachers=teacher)

    query = request.GET.get('q')
    if query:
        subjects = subjects.filter(name__icontains=query) | subjects.filter(teachers__name__icontains=query)

    return render(request, 'school/subject_list.html', {'subjects': subjects})


@role_required(['Admin', 'Teacher'])
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    user = request.user

    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        if not subject.teachers.filter(pk=teacher.pk).exists():
            return HttpResponseForbidden()

    return render(request, 'school/subject_detail.html', {'subject': subject})


@role_required(['Admin'])
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f"Subject '{subject.name}' created successfully.")
            return redirect('school:subject_list')
    else:
        form = SubjectForm()
    return render(request, 'school/subject_form.html', {'form': form, 'title': 'Add Subject'})


@role_required(['Admin'])
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


@role_required(['Admin'])
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, f"Subject '{subject.name}' deleted successfully.")
        return redirect('subject_list')
    return render(request, 'school/subject_confirm_delete.html', {'subject': subject})


# ---------- TEACHER VIEWS ----------
@role_required(['Admin'])
def teacher_list(request):
    query = request.GET.get('q', '')
    if query:
        teachers = Teacher.objects.filter(name__icontains=query)
    else:
        teachers = Teacher.objects.all()
    context = {
        'teachers': teachers,
        'query': query,
    }
    return render(request, 'school/teacher_list.html', context)


@role_required(['Admin', 'Teacher'])
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    user = request.user

    if user.role == 'TEACHER' and teacher.user != user:
        return HttpResponseForbidden()

    return render(request, 'school/teacher_detail.html', {'teacher': teacher})


@role_required(['Admin'])
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if form.is_valid() and username and email and password:
            # Create user first
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='TEACHER'
            )

            teacher = form.save(commit=False)
            teacher.user = user
            teacher.save()
            form.save_m2m()

            messages.success(request, "Teacher created successfully.")
            return redirect('school:teacher_list')
    else:
        form = TeacherForm()

    return render(request, 'school/teacher_form.html', {'form': form, 'title': 'Add Teacher'})

@role_required(['Admin'])
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher updated successfully.")
            return redirect('school:teacher_detail', pk=pk)
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'school/teacher_form.html', {'form': form})


@role_required(['Admin'])
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, "Teacher deleted successfully.")
        return redirect('teacher_list')
    return render(request, 'school/teacher_confirm_delete.html', {'teacher': teacher})


# ---------- STUDENT VIEWS ----------
@role_required(['Admin', 'Teacher', 'Student'])
def student_list(request):
    user = request.user
    students = Student.objects.all()

    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher).distinct()
        students = students.filter(classroom__in=classrooms)
    elif user.role == 'STUDENT':
        students = students.filter(user=user)

    query = request.GET.get('q')
    classroom_id = request.GET.get('classroom')

    if query:
        students = students.filter(name__icontains=query)
    if classroom_id:
        students = students.filter(classroom_id=classroom_id)

    classrooms = ClassRoom.objects.all()
    return render(request, 'school/student_list.html', {'students': students, 'classrooms': classrooms})


@role_required(['Admin', 'Teacher', 'Student'])
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    user = request.user

    if user.role == 'STUDENT' and student.user != user:
        return HttpResponseForbidden()

    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        if student.classroom not in ClassRoom.objects.filter(subjects__teachers=teacher):
            return HttpResponseForbidden()

    return render(request, 'school/student_detail.html', {'student': student})


@role_required(['Admin'])
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


@role_required(['Admin'])
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


@role_required(['Admin'])
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, f"Student '{student.name}' deleted successfully.")
        return redirect('student_list')
    return render(request, 'school/student_confirm_delete.html', {'student': student})


# ---------- GRADES VIEWS ----------
@role_required(['Admin', 'Teacher'])
def grade_list(request):
    user = request.user
    grades = Grade.objects.select_related('student', 'subject').order_by('-id')

    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher)
        grades = grades.filter(student__classroom__in=classrooms)

    return render(request, 'school/grade_list.html', {'grades': grades})


@role_required(['Admin', 'Teacher'])
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


@role_required(['Admin', 'Teacher'])
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


@role_required(['Admin', 'Teacher'])
def grade_delete(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == 'POST':
        grade.delete()
        messages.success(request, 'Grade deleted successfully.')
        return redirect('grade_list')
    return render(request, 'school/grade_confirm_delete.html', {'grade': grade})


# ---------- ATTENDANCE VIEWS ----------
@role_required(['Admin', 'Teacher'])
def attendance_list(request):
    attendances = Attendance.objects.all().order_by('-date')
    user = request.user

    if user.role == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher)
        attendances = attendances.filter(student__classroom__in=classrooms)

    query = request.GET.get('q')
    if query:
        attendances = attendances.filter(student__name__icontains=query)

    return render(request, 'school/attendance_list.html', {'attendances': attendances})


@role_required(['Admin', 'Teacher'])
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance recorded successfully.")
            return redirect('school:attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'school/attendance_form.html', {'form': form, 'title': 'Record Attendance'})


@role_required(['Admin', 'Teacher'])
def attendance_update(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance updated successfully.")
            return redirect('school:attendance_list')
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'school/attendance_form.html', {'form': form, 'title': 'Edit Attendance'})


@role_required(['Admin', 'Teacher'])
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, "Attendance deleted successfully.")
        return redirect('school:attendance_list')
    return render(request, 'school/attendance_confirm_delete.html', {'attendance': attendance})
