from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView, LogoutView
from django import forms
from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db import IntegrityError  # For handling unique constraint errors, e.g., on username
from django.db.models import Q  # For complex queries like OR conditions
from django.shortcuts import redirect
from .models import Grade, ClassRoom, Subject, Teacher, Student, Attendance, User
from .forms import (
    GradeForm, ClassRoomForm, SubjectForm,
    TeacherForm, StudentForm, AttendanceForm,
    CustomUserCreationForm
)
from .forms import CustomUserCreationForm, CustomUserChangeForm

# --- Utility Functions and Decorators ---
@login_required
def force_password_change(request):
    """
    Forces a user to change their password upon first login or admin-forced reset.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Set the flag to False after successful password change
            user.force_password_change = False
            user.save()
            update_session_auth_hash(request, user) # Important to keep the user logged in
            messages.success(request, "Password changed successfully.")
            return redirect('school:role_redirect') # Redirect to role-based dashboard
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'school/force_password_change.html', {'form': form, 'title': 'Change Your Password'})
#--------------------------------------------------------------------------------------------------------------------------
def no_permission(request):
    """
    Renders a 403 Forbidden page for unauthorized access.
    """
    return render(request, 'school/no_permission.html', status=403)
#--------------------------------------------------------------------------------------------------------------------------
def role_required(allowed_roles=None):
    """
    Decorator to restrict access to views based on user roles.
    Superusers always have access.
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # Redirect unauthenticated users to the login page
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())

            user = request.user

            # Superusers always have access
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check if the user has a 'role' attribute and if it's in allowed_roles
            user_role = getattr(user, 'role', None)
            if user_role and user_role.upper() in [r.upper() for r in allowed_roles]:
                return view_func(request, *args, **kwargs)

            # If none of the above, redirect to no_permission page
            from django.shortcuts import redirect
            return redirect('school:no_permission')

        return wrapper
    return decorator

#--------------------------------------------------------------------------------------------------------------------------
# --- Authentication Views ---
class CustomLoginView(LoginView):
    """
    Custom login view to handle post-login redirection based on user role
    or force password change.
    """
    template_name = 'registration/login.html'

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        # After successful login, redirect based on role or password change flag
        # FIX: Ensure to use the namespaced URL for redirection
        return redirect('school:role_redirect')

#--------------------------------------------------------------------------------------------------------------------------
class CustomLogoutView(LogoutView):
    """
    Custom logout view that redirects to the login page after logout.
    """
    next_page = 'login' # Ensure 'login' is a named URL in your urls.py
#--------------------------------------------------------------------------------------------------------------------------
def register(request):
    """
    Handles user registration for new accounts.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # You might want to set a default role here if not handled by form/model
            messages.success(request, f"Registration successful for {user.username}. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
#--------------------------------------------------------------------------------------------------------------------------
@login_required
def role_redirect(request):
    """
    Redirects logged-in users to their respective dashboards based on their role
    or forces password change if required.
    """
    user = request.user
    if user.force_password_change:
        return redirect('school:force_password_change') # Redirect to force password change page

    if user.is_superuser or (hasattr(user, 'role') and user.role == 'ADMIN'):
        return redirect('school:admin_dashboard')
    elif hasattr(user, 'role') and user.role == 'TEACHER':
        return redirect('school:teacher_dashboard')
    elif hasattr(user, 'role') and user.role == 'STUDENT':
        return redirect('school:student_dashboard')
    else:
        # Default fallback, perhaps a generic dashboard or an error page
        messages.warning(request, "Your role is not defined. Please contact an administrator.")
        return redirect('school:home') # Or another suitable default

#--------------------------------------------------------------------------------------------------------------------------
# --- Dashboard Views ---
@login_required
@role_required(['ADMIN'])
def admin_dashboard(request):
    context = {
        'teachers_count': Teacher.objects.count(),
        'students_count': Student.objects.count(),
        'classes_count': ClassRoom.objects.count(),
        'subjects_count': Subject.objects.count(),
        'users_count': User.objects.count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
    }
    return render(request, 'school/admin_dashboard.html', context)

@login_required
@role_required(['ADMIN'])
def admin_dashboard_data(request):
    data = {
        'teachers_count': Teacher.objects.count(),
        'students_count': Student.objects.count(),
        'classes_count': ClassRoom.objects.count(),
        'subjects_count': Subject.objects.count(),
        'users_count': User.objects.count(),
        'recent_users': list(User.objects.order_by('-date_joined').values(
            'username', 'email', 'date_joined', 'last_login'
        )[:5])
    }
    return JsonResponse(data)
#--------------------------------------------------------------------------------------------------------------------------
@role_required(['TEACHER']) # Changed to uppercase
def teacher_dashboard(request):
    """Renders the teacher dashboard."""
    return render(request, 'school/teacher_dashboard.html')
#--------------------------------------------------------------------------------------------------------------------------
@role_required(['STUDENT']) # Changed to uppercase
def student_dashboard(request):
    """Renders the student dashboard."""
    return render(request, 'school/student_dashboard.html')
#--------------------------------------------------------------------------------------------------------------------------
@login_required
def home(request):
    """
    Renders the main home page, showing summary statistics.
    Accessible to all logged-in users.
    """
    user = request.user
    # Check if user is authenticated before accessing role/group attributes
    is_admin_or_teacher = False
    if user.is_authenticated:
        # It's better to check user.role or user.is_superuser directly if your User model has 'role'
        is_admin_or_teacher = user.is_superuser or (hasattr(user, 'role') and user.role.upper() in ['ADMIN', 'TEACHER'])

    context = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_classrooms': ClassRoom.objects.count(),
        'students': Student.objects.all(), # Consider limiting this for performance on large datasets
        'is_admin_or_teacher': is_admin_or_teacher,
    }
    return render(request, 'school/home.html', context)

#--------------------------------------------------------------------------------------------------------------------------
# ---------- CLASSROOM VIEWS ----------
@role_required(['ADMIN', 'TEACHER'])
def classroom_list(request):
    """Lists all classrooms, filtered for teachers to show only relevant ones."""
    user = request.user
    if user.is_superuser or (hasattr(user, 'role') and user.role.upper() == 'ADMIN'):
        classrooms = ClassRoom.objects.all()
    elif hasattr(user, 'role') and user.role.upper() == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher).distinct()
    else:
        # This case should ideally be caught by role_required, but defensive check
        return HttpResponseForbidden("You do not have permission to view this page.")
    return render(request, 'school/classroom_list.html', {'classrooms': classrooms})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN', 'TEACHER'])
def classroom_detail(request, pk):
    """Displays details of a specific classroom, with teacher-specific access control."""
    classroom = get_object_or_404(ClassRoom, pk=pk)
    user = request.user

    if hasattr(user, 'role') and user.role.upper() == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        if not classroom.subjects.filter(teachers=teacher).exists():
            return HttpResponseForbidden("You do not have permission to view this classroom.")

    students = Student.objects.filter(classroom=classroom)
    subjects = classroom.subjects.all()
    return render(request, 'school/classroom_detail.html', {
        'classroom': classroom,
        'students': students,
        'subjects': subjects,
    })

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def classroom_create(request):
    """Handles creation of a new classroom."""
    if request.method == 'POST':
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            classroom = form.save()
            messages.success(request, f"Classroom '{classroom.name}' created successfully.")
            return redirect('school:classroom_list')
        else:
            messages.error(request, "Error creating classroom. Please check the form.")
    else:
        form = ClassRoomForm()
    return render(request, 'school/classroom_form.html', {'form': form, 'title': 'Add Classroom'})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def classroom_update(request, pk):
    """Handles updating an existing classroom."""
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == 'POST':
        form = ClassRoomForm(request.POST, instance=classroom)
        if form.is_valid():
            classroom = form.save()
            messages.success(request, f"Classroom '{classroom.name}' updated successfully.")
            return redirect('school:classroom_detail', pk=classroom.pk)
        else:
            messages.error(request, "Error updating classroom. Please check the form.")
    else:
        form = ClassRoomForm(instance=classroom)
    return render(request, 'school/classroom_form.html', {'form': form, 'title': 'Edit Classroom'})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def classroom_delete(request, pk):
    """Handles deletion of a classroom."""
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == 'POST':
        classroom_name = classroom.name # Get name before deletion
        classroom.delete()
        messages.success(request, f"Classroom '{classroom_name}' deleted successfully.")
        return redirect('school:classroom_list')
    return render(request, 'school/classroom_confirm_delete.html', {'classroom': classroom})

#--------------------------------------------------------------------------------------------------------------------------
# ---------- SUBJECT VIEWS ----------
@role_required(['ADMIN', 'TEACHER'])
def subject_list(request):
    """Lists all subjects, filtered for teachers to show only relevant ones. Supports search."""
    user = request.user
    subjects = Subject.objects.all()
    if hasattr(user, 'role') and user.role.upper() == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        subjects = subjects.filter(teachers=teacher)

    query = request.GET.get('q')
    if query:
        # Use Q objects for more complex OR queries
        subjects = subjects.filter(Q(name__icontains=query) | Q(teachers__name__icontains=query)).distinct()

    return render(request, 'school/subject_list.html', {'subjects': subjects})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN', 'TEACHER'])
def subject_detail(request, pk):
    """Displays details of a specific subject, with teacher-specific access control."""
    subject = get_object_or_404(Subject, pk=pk)
    user = request.user

    if hasattr(user, 'role') and user.role.upper() == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        if not subject.teachers.filter(pk=teacher.pk).exists():
            return HttpResponseForbidden("You do not have permission to view this subject.")

    return render(request, 'school/subject_detail.html', {'subject': subject})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def subject_create(request):
    """Handles creation of a new subject."""
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f"Subject '{subject.name}' created successfully.")
            return redirect('school:subject_list')
        else:
            messages.error(request, "Error creating subject. Please check the form.")
    else:
        form = SubjectForm()
    return render(request, 'school/subject_form.html', {'form': form, 'title': 'Add Subject'})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def subject_update(request, pk):
    """Handles updating an existing subject."""
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f"Subject '{subject.name}' updated successfully.")
            return redirect('school:subject_detail', pk=subject.pk)
        else:
            messages.error(request, "Error updating subject. Please check the form.")
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'school/subject_form.html', {'form': form, 'title': 'Edit Subject'})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def subject_delete(request, pk):
    """Handles deletion of a subject."""
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject_name = subject.name # Get name before deletion
        subject.delete()
        messages.success(request, f"Subject '{subject_name}' deleted successfully.")
        return redirect('school:subject_list')
    return render(request, 'school/subject_confirm_delete.html', {'subject': subject})

#--------------------------------------------------------------------------------------------------------------------------
# ---------- TEACHER VIEWS ----------
@role_required(['ADMIN'])
def teacher_list(request):
    """Lists all teachers, with search functionality."""
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

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN', 'TEACHER'])
def teacher_detail(request, pk):
    """Displays details of a specific teacher, with teacher-specific access control."""
    teacher = get_object_or_404(Teacher, pk=pk)
    user = request.user

    # A teacher can only view their own profile unless they are an Admin
    if hasattr(user, 'role') and user.role.upper() == 'TEACHER' and teacher.user != user:
        return HttpResponseForbidden("You do not have permission to view this teacher's details.")

    return render(request, 'school/teacher_detail.html', {'teacher': teacher})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def teacher_create(request):
    """
    Handles creation of a new teacher, including associated User account.
    Generates a temporary password and sends an email.
    """
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        username = request.POST.get('username')
        email = request.POST.get('email')

        if form.is_valid(): # Check form validity first
            if not username or not email: # Check for necessary user fields
                messages.error(request, "Username and Email are required to create a user account for the teacher.")
                return render(request, 'school/teacher_form.html', {'form': form, 'title': 'Add Teacher'})

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, f"User with username '{username}' already exists. Please choose a different username.")
                return render(request, 'school/teacher_form.html', {'form': form, 'title': 'Add Teacher'})

            try:
                # Generate a secure temporary password
                temp_password = get_random_string(length=12) # Longer for better security

                # Create user first
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=temp_password, # Use temp_password
                    role='TEACHER', # Assign the role
                    force_password_change=True # Force password change on first login
                )
                user.save() # Ensure user is saved

                teacher = form.save(commit=False)
                teacher.user = user
                teacher.save()
                form.save_m2m() # Save ManyToMany relationships if any

                # Send email with credentials
                try:
                    send_mail(
                        subject='Your New Teacher Account Credentials',
                        message=f"Hello {user.username},\n\nYour teacher account has been created for the School Management System.\n\n"
                                f"Username: {user.username}\nTemporary Password: {temp_password}\n\n"
                                f"Please log in using these credentials at {request.build_absolute_uri('/')} and "
                                f"change your password immediately for security reasons. You will be prompted to do so.\n\n"
                                f"Thank you.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    messages.success(request, f"Teacher '{teacher.name}' created successfully. Login credentials sent to {user.email}.")
                except Exception as e:
                    messages.warning(request, f"Teacher '{teacher.name}' created, but failed to send email: {e}. Please provide credentials manually.")
                
                return redirect('school:teacher_list')

            except IntegrityError:
                messages.error(request, "A user with this email or username might already exist.")
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
                # Consider deleting the partially created user if teacher creation fails
                if 'user' in locals() and user.pk:
                    user.delete()
        else:
            messages.error(request, "Error creating teacher. Please correct the form errors.")
    else:
        form = TeacherForm()

    return render(request, 'school/teacher_form.html', {'form': form, 'title': 'Add Teacher'})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def teacher_update(request, pk):
    """Handles updating an existing teacher's details."""
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, f"Teacher '{teacher.name}' updated successfully.")
            return redirect('school:teacher_detail', pk=pk)
        else:
            messages.error(request, "Error updating teacher. Please correct the form errors.")
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'school/teacher_form.html', {'form': form, 'title': 'Edit Teacher'})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def teacher_delete(request, pk):
    """Handles deletion of a teacher and their associated user account."""
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher_name = teacher.name # Get name before deletion
        # Optionally, delete the associated User object as well
        if teacher.user:
            teacher.user.delete()
        teacher.delete()
        messages.success(request, f"Teacher '{teacher_name}' and associated user deleted successfully.")
        return redirect('school:teacher_list')
    return render(request, 'school/teacher_confirm_delete.html', {'teacher': teacher})

#--------------------------------------------------------------------------------------------------------------------------
# ---------- STUDENT VIEWS ----------
@role_required(['ADMIN', 'TEACHER', 'STUDENT'])
def student_list(request):
    """
    Lists all students, filtered by teacher's classrooms or for the individual student.
    Supports searching and filtering by classroom.
    """
    user = request.user
    students = Student.objects.all()

    if hasattr(user, 'role') and user.role.upper() == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher).distinct()
        students = students.filter(classroom__in=classrooms)
    elif hasattr(user, 'role') and user.role.upper() == 'STUDENT':
        students = students.filter(user=user) # Student can only see their own profile

    query = request.GET.get('q')
    classroom_id = request.GET.get('classroom')

    if query:
        students = students.filter(name__icontains=query)
    if classroom_id:
        students = students.filter(classroom_id=classroom_id)

    classrooms = ClassRoom.objects.all() # All classrooms for filtering dropdown

    return render(request, 'school/student_list.html', {
        'students': students,
        'classrooms': classrooms
    })

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN', 'TEACHER', 'STUDENT'])
def student_detail(request, pk):
    """
    Displays details of a specific student, with role-based access control.
    """
    student = get_object_or_404(Student, pk=pk)
    user = request.user

    # Student can only view their own profile
    if hasattr(user, 'role') and user.role.upper() == 'STUDENT' and student.user != user:
        return HttpResponseForbidden("You do not have permission to view this student's details.")

    # Teacher can only view students in classrooms they teach subjects in
    if hasattr(user, 'role') and user.role.upper() == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        # Check if the student's classroom is associated with any subject taught by this teacher
        if not ClassRoom.objects.filter(pk=student.classroom.pk, subjects__teachers=teacher).exists():
            return HttpResponseForbidden("You do not have permission to view this student.")

    return render(request, 'school/student_detail.html', {'student': student})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def student_create(request):
    """
    Handles creation of a new student.
    Note: Ensure your StudentForm and Student model handle image uploads correctly
    if request.FILES is used.
    """
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student '{student.name}' created successfully.")
            return redirect('school:student_list')
        else:
            messages.error(request, "Error creating student. Please check the form.")
    else:
        form = StudentForm()
    return render(request, 'school/student_form.html', {'form': form, 'title': 'Add Student'})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def student_update(request, pk):
    """Handles updating an existing student's details."""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student '{student.name}' updated successfully.")
            return redirect('school:student_detail', pk=student.pk)
        else:
            messages.error(request, "Error updating student. Please check the form.")
    else:
        form = StudentForm(instance=student)
    return render(request, 'school/student_form.html', {'form': form, 'title': 'Edit Student'})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def student_delete(request, pk):
    """Handles deletion of a student."""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student_name = student.name # Get name before deletion
        student.delete()
        messages.success(request, f"Student '{student_name}' deleted successfully.")
        return redirect('school:student_list')
    return render(request, 'school/student_confirm_delete.html', {'student': student})

#--------------------------------------------------------------------------------------------------------------------------
# ---------- GRADES VIEWS ----------
@role_required(['ADMIN', 'TEACHER'])
def grade_list(request):
    """Lists all grades, filtered for teachers to show only relevant ones."""
    user = request.user
    grades = Grade.objects.select_related('student', 'subject').order_by('-id')

    if hasattr(user, 'role') and user.role.upper() == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher)
        grades = grades.filter(student__classroom__in=classrooms)

    return render(request, 'school/grade_list.html', {'grades': grades})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN', 'TEACHER'])
def grade_create(request):
    """Handles creation of a new grade."""
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade added successfully.')
            return redirect('school:grade_list')
        else:
            messages.error(request, "Error adding grade. Please check the form.")
    else:
        form = GradeForm()
    return render(request, 'school/grade_form.html', {'form': form, 'title': 'Add Grade'})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN', 'TEACHER'])
def grade_update(request, pk):
    """Handles updating an existing grade."""
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade updated successfully.')
            return redirect('school:grade_list')
        else:
            messages.error(request, "Error updating grade. Please check the form.")
    else:
        form = GradeForm(instance=grade)
    return render(request, 'school/grade_form.html', {'form': form, 'title': 'Edit Grade'})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN', 'TEACHER'])
def grade_delete(request, pk):
    """Handles deletion of a grade."""
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == 'POST':
        grade.delete()
        messages.success(request, 'Grade deleted successfully.')
        return redirect('school:grade_list')
    return render(request, 'school/grade_confirm_delete.html', {'grade': grade})

#--------------------------------------------------------------------------------------------------------------------------
# ---------- ATTENDANCE VIEWS ----------
@role_required(['ADMIN', 'TEACHER'])
def attendance_list(request):
    """Lists all attendance records, filtered for teachers to show only relevant ones. Supports search."""
    attendances = Attendance.objects.all().order_by('-date')
    user = request.user

    if hasattr(user, 'role') and user.role.upper() == 'TEACHER':
        teacher = get_object_or_404(Teacher, user=user)
        classrooms = ClassRoom.objects.filter(subjects__teachers=teacher)
        attendances = attendances.filter(student__classroom__in=classrooms)

    query = request.GET.get('q')
    if query:
        attendances = attendances.filter(student__name__icontains=query)

    return render(request, 'school/attendance_list.html', {'attendances': attendances})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN', 'TEACHER'])
def attendance_create(request):
    """Handles creation of a new attendance record."""
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance recorded successfully.")
            return redirect('school:attendance_list')
        else:
            messages.error(request, "Error recording attendance. Please check the form.")
    else:
        form = AttendanceForm()
    return render(request, 'school/attendance_form.html', {'form': form, 'title': 'Record Attendance'})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN', 'TEACHER'])
def attendance_update(request, pk):
    """Handles updating an existing attendance record."""
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance updated successfully.")
            return redirect('school:attendance_list')
        else:
            messages.error(request, "Error updating attendance. Please check the form.")
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'school/attendance_form.html', {'form': form, 'title': 'Edit Attendance'})

#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN', 'TEACHER'])
def attendance_delete(request, pk):
    """Handles deletion of an attendance record."""
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, "Attendance deleted successfully.")
        return redirect('school:attendance_list')
    return render(request, 'school/attendance_confirm_delete.html', {'attendance': attendance})

#--------------------------------------------------------------------------------------------------------------------------
# --- User Management (Admin Only) ---
@role_required(['ADMIN'])
def user_list(request):
    """Lists all users (Admin only)."""
    users = User.objects.all()
    return render(request, 'school/user_list.html', {'users': users})
@role_required(['ADMIN'])
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User '{user.username}' updated successfully.")
            return redirect('school:user_list')
        else:
            messages.error(request, "Error updating user. Please correct the form errors.")
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'school/user_form.html', {'form': form, 'title': f"Edit User: {user.username}"})

@role_required(['ADMIN'])
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f"User '{user.username}' deleted successfully.")
        return redirect('school:user_list')
    return render(request, 'school/user_confirm_delete.html', {'user': user})
#--------------------------------------------------------------------------------------------------------------------------
@role_required(['ADMIN'])
def user_create_by_admin(request):
    """
    Handles creation of new user accounts by an admin.
    Generates a temporary password, forces password change on first login,
    and sends credentials via email.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            temp_password = get_random_string(length=12) # Generate a secure temporary password
            user.set_password(temp_password)
            user.force_password_change = True # Set flag to force password change
            user.save()

            # Send email with credentials
            try:
                send_mail(
                    subject='Your Account Credentials for School Management System',
                    message=f"Hello {user.username},\n\nYour account has been created.\n\n"
                            f"Username: {user.username}\nTemporary Password: {temp_password}\n\n"
                            f"Please log in using these credentials at {request.build_absolute_uri('/')} and "
                            f"change your password immediately. You will be prompted to do so.\n\n"
                            f"If you have any questions, please contact the administrator.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False, # Set to True in production to avoid crashing on email errors
                )
                messages.success(request, f"User '{user.username}' created and email sent successfully.")
            except Exception as e:
                messages.warning(request, f"User '{user.username}' created, but failed to send email: {e}. Please provide credentials manually.")
            
            return redirect('school:user_list')
        else:
            messages.error(request, "Error creating user. Please correct the form errors.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'school/user_form.html', {'form': form, 'title': 'Create User'})

