from django.db import models
from django.contrib.auth.models import User

class ClassRoom(models.Model):
    name = models.CharField(max_length=50)
    section = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return f"{self.name} {self.section}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    subjects = models.ManyToManyField(Subject)
    contact = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    address = models.TextField(blank=True)
    parent_contact = models.CharField(max_length=20, blank=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.FloatField()
    grade = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.grade}"

class Timetable(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ])
    period_time = models.TimeField()

    def __str__(self):
        return f"{self.classroom} - {self.subject} - {self.day_of_week} - {self.period_time}"

class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')])

    def __str__(self):
        return f"{self.student.name} - {self.amount} - {self.status}"

class Notice(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
