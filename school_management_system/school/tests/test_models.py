from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from datetime import time, date
from decimal import Decimal

from school.models import (
    User, ClassRoom, Subject, Teacher, Student, Attendance,
    Grade, Timetable, Fee, Notice
)

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user_with_role(self):
        user = User.objects.create_user(username='user1', password='pass1234', role='TEACHER')
        self.assertEqual(user.role, 'TEACHER')
        self.assertFalse(user.force_password_change)

class ClassRoomModelTest(TestCase):
    def test_create_classroom(self):
        classroom = ClassRoom.objects.create(name='Grade 1', section='A')
        self.assertEqual(str(classroom), 'Grade 1 - A')

class SubjectModelTest(TestCase):
    def test_create_subject(self):
        subject = Subject.objects.create(name='Mathematics', code='MATH101')
        self.assertEqual(str(subject), 'Mathematics')

class TeacherModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teacher1', password='pass1234', role='TEACHER')
        self.subject = Subject.objects.create(name='English', code='ENG101')

    def test_create_teacher_and_assign_subject(self):
        teacher = Teacher.objects.create(user=self.user, name='Mr. Smith', gender='Male', contact='123456')
        teacher.subjects.add(self.subject)
        self.assertEqual(str(teacher), 'Mr. Smith')
        self.assertIn(self.subject, teacher.subjects.all())

class StudentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student1', password='pass1234', role='STUDENT')
        self.classroom = ClassRoom.objects.create(name='Grade 1', section='A')

    def test_create_student(self):
        student = Student.objects.create(
            user=self.user,
            name='Jane Doe',
            age=12,
            gender='Female',
            classroom=self.classroom
        )
        self.assertEqual(str(student), 'Jane Doe')
        self.assertEqual(student.classroom, self.classroom)

class AttendanceModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='student2', password='pass1234', role='STUDENT')
        classroom = ClassRoom.objects.create(name='Grade 2', section='B')
        self.student = Student.objects.create(user=user, name='John Doe', age=13, gender='Male', classroom=classroom)

    def test_create_attendance(self):
        attendance = Attendance.objects.create(student=self.student, date=date.today(), status='Present')
        self.assertEqual(str(attendance), f"{self.student.name} - {attendance.date} - Present")

    def test_unique_constraint_on_attendance(self):
        Attendance.objects.create(student=self.student, date=date.today(), status='Present')
        duplicate = Attendance(student=self.student, date=date.today(), status='Absent')
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

class GradeModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='student3', password='pass1234', role='STUDENT')
        classroom = ClassRoom.objects.create(name='Grade 3', section='C')
        self.student = Student.objects.create(user=user, name='Alice', age=14, gender='Female', classroom=classroom)
        self.subject = Subject.objects.create(name='Science', code='SCI101')

    def test_create_grade(self):
        grade = Grade.objects.create(student=self.student, subject=self.subject, marks=85, grade='A')
        self.assertEqual(str(grade), 'Alice - Science - A')

    def test_unique_constraint_on_grade(self):
        Grade.objects.create(student=self.student, subject=self.subject, marks=85, grade='A')
        duplicate = Grade(student=self.student, subject=self.subject, marks=90, grade='A+')
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

class TimetableModelTest(TestCase):
    def setUp(self):
        self.classroom = ClassRoom.objects.create(name='Grade 4', section='D')
        self.subject = Subject.objects.create(name='History', code='HIS101')
        user = User.objects.create_user(username='teacher2', password='pass1234', role='TEACHER')
        self.teacher = Teacher.objects.create(user=user, name='Mrs. Smith', gender='Female')

    def test_create_timetable(self):
        timetable = Timetable.objects.create(
            classroom=self.classroom,
            subject=self.subject,
            teacher=self.teacher,
            day_of_week='Monday',
            period_time=time(9, 0)
        )
        self.assertEqual(str(timetable), 'Grade 4 (D) - History - Monday at 09:00')

    def test_unique_constraint_on_timetable(self):
        Timetable.objects.create(
            classroom=self.classroom,
            subject=self.subject,
            teacher=self.teacher,
            day_of_week='Monday',
            period_time=time(9, 0)
        )
        duplicate = Timetable(
            classroom=self.classroom,
            subject=self.subject,
            teacher=self.teacher,
            day_of_week='Monday',
            period_time=time(9, 0)
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

class FeeModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='student4', password='pass1234', role='STUDENT')
        classroom = ClassRoom.objects.create(name='Grade 5', section='E')
        self.student = Student.objects.create(user=user, name='Bob', age=15, gender='Male', classroom=classroom)

    def test_create_fee(self):
        fee = Fee.objects.create(student=self.student, amount=Decimal('1000.00'), status='Paid')
        self.assertEqual(str(fee), "Bob - 1000.00 - Paid")

class NoticeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='pass1234', role='ADMIN')

    def test_create_notice(self):
        notice = Notice.objects.create(title='Holiday', content='School closed on Friday', posted_by=self.user)
        self.assertEqual(str(notice), 'Holiday')
        self.assertEqual(notice.posted_by, self.user)
