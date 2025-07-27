from django.test import TestCase
from django.contrib.auth import get_user_model
from school.forms import StudentForm
from school.models import ClassRoom, Student

User = get_user_model()

class StudentFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="studentuser", password="testpass")
        self.classroom = ClassRoom.objects.create(name="Grade 10", section="A")

    def test_valid_form(self):
        data = {
            'user': self.user.id,            # Must provide user id (OneToOneField)
            'name': 'John Doe',
            'age': 15,
            'gender': 'Male',                # Must match choices exactly
            'classroom': self.classroom.id,
            'photo': None,
            'address': '',
            'parent_contact': '',
        }
        form = StudentForm(data=data)
        print("Form errors:", form.errors)  # Useful debug info if test fails
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form = StudentForm(data={})
        self.assertFalse(form.is_valid())
