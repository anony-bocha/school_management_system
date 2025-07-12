# Django School Management System

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Project Overview

A comprehensive Django-based School Management System designed to manage users (Admin, Teacher, Student), classrooms, subjects, grades, attendance, and more. The system features role-based access control, secure authentication with forced password change, email notifications, and an intuitive dashboard for each user role.

---

## Features

- User roles: Admin, Teacher, Student
- Custom authentication system with forced password change on first login
- Role-based dashboards and access controls
- CRUD for Teachers, Students, Classrooms, Subjects, Grades, Attendance
- Email notifications for user account credentials
- Search and filter functionalities across lists
- Responsive and user-friendly UI using Bootstrap

---

## Screenshots

<!-- Add your screenshots here -->

![Admin Dashboard](screenshots/admin_dashboard.png)
![Teacher Dashboard](screenshots/teacher_dashboard.png)
![Student Dashboard](screenshots/student_dashboard.png)

---

## Technologies Used

- Python 3.8+
- Django 4.x
- Bootstrap 5
- SQLite / PostgreSQL (depending on setup)
- SMTP for email notifications

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Virtualenv (recommended)
- Email SMTP credentials for sending emails (e.g., Gmail SMTP)

### Setup Steps

```bash
git clone https://github.com/yourusername/school-management-system.git
cd school-management-system

# Create and activate virtual environment
python -m venv env
source env/bin/activate      # Linux/macOS
env\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver
