from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=True, blank=True)
    force_password_change = models.BooleanField(default=False)  # Add this field

class ClassRoom(models.Model):
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=1)
    subjects = models.ManyToManyField('Subject', related_name='classrooms', blank=True)

    def __str__(self):
        return f"{self.name} - {self.section}"

    class Meta:
        ordering = ['name', 'section']
        verbose_name_plural = 'Classrooms'

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]

    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    subjects = models.ManyToManyField(Subject, related_name='teachers')
    contact = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    address = models.TextField(blank=True)
    parent_contact = models.CharField(max_length=20, blank=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='students')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Attendance(models.Model):
    STATUS_CHOICES = [('Present', 'Present'), ('Absent', 'Absent')]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"

    def clean(self):
        if Attendance.objects.filter(student=self.student, date=self.date).exclude(pk=self.pk).exists():
            raise ValidationError('Attendance for this student on this date already exists.')

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    marks = models.FloatField()
    grade = models.CharField(max_length=2)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.grade}"

    def clean(self):
        if Grade.objects.filter(student=self.student, subject=self.subject).exclude(pk=self.pk).exists():
            raise ValidationError('Grade for this student and subject already exists.')

class Timetable(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='timetables')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    period_time = models.TimeField()

    class Meta:
        unique_together = ('classroom', 'day_of_week', 'period_time')

    def __str__(self):
        return f"{self.classroom.name} ({self.classroom.section}) - {self.subject.name} - {self.day_of_week} at {self.period_time.strftime('%H:%M')}"

class Fee(models.Model):
    STATUS_CHOICES = [('Paid', 'Paid'), ('Unpaid', 'Unpaid')]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.student.name} - {self.amount} - {self.status}"

class Notice(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notices')
    date_posted = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_posted']
