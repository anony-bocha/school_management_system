# school/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # This import isn't strictly necessary if only using CustomLoginView/CustomLogoutView

app_name = 'school'  # Optional but recommended for namespacing

urlpatterns = [
    path('', views.home, name='home'),

    # --- Authentication & User Management ---
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('role-redirect/', views.role_redirect, name='role_redirect'), # Keep one instance
    path('force-password-change/', views.force_password_change, name='force_password_change'),
    path('no-permission/', views.no_permission, name='no_permission'), # Keep one instance

    # User Management (Admin only)
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create_by_admin, name='user_create_by_admin'), # Keep one instance

    # --- Dashboards ---
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),

    # --- Classrooms ---
    path('classrooms/', views.classroom_list, name='classroom_list'),
    path('classrooms/create/', views.classroom_create, name='classroom_create'),
    path('classrooms/<int:pk>/', views.classroom_detail, name='classroom_detail'),
    path('classrooms/<int:pk>/update/', views.classroom_update, name='classroom_update'),
    path('classrooms/<int:pk>/delete/', views.classroom_delete, name='classroom_delete'),

    # --- Subjects ---
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('subjects/<int:pk>/update/', views.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),

    # --- Teachers ---
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:pk>/update/', views.teacher_update, name='teacher_update'),
    path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),

    # --- Students ---
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/update/', views.student_update, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),

    # --- Attendances ---
    path('attendances/', views.attendance_list, name='attendance_list'),
    path('attendances/create/', views.attendance_create, name='attendance_create'),
    path('attendances/<int:pk>/update/', views.attendance_update, name='attendance_update'),
    path('attendances/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),

    # --- Grades ---
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/create/', views.grade_create, name='grade_create'),
    path('grades/<int:pk>/update/', views.grade_update, name='grade_update'),
    path('grades/<int:pk>/delete/', views.grade_delete, name='grade_delete'),
]