# Django School Management System

A comprehensive Django-based School Management System that manages users (Admin, Teacher, Student), classrooms, subjects, grades, attendance, and more — with role-based access control and secure authentication.

---

## Features

- **User Roles:** Admin, Teacher, Student with customized dashboards
- **Authentication:** Custom login, logout, registration, forced password change on first login
- **Admin Dashboard:** Overview statistics and recent user activity
- **CRUD Operations:** Manage Teachers, Students, Classrooms, Subjects, Grades, Attendance
- **Role-based Permissions:** Access control with decorators and group checks
- **Email Notifications:** Sends temporary passwords on account creation
- **Search & Filter:** Efficient searching in lists (Teachers, Students, Subjects, etc.)
- **Responsive UI:** Bootstrap-based clean and user-friendly interface

---

## Installation & Setup

### Prerequisites

- Python 3.8+
- Django 4.x
- Virtualenv (recommended)
- Email SMTP credentials (for sending emails)

### Steps

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/school-management-system.git
   cd school-management-system
2. **Create and activate a virtual environment:**
   python -m venv env
3. **Activate the virtual environment:

On Linux/macOS:source env/bin/activate
On Windows (CMD):env\Scripts\activate.bat
On Windows (PowerShell):env\Scripts\Activate.ps1
4. **Install dependencies:

pip install -r requirements.txt

