from django.test import SimpleTestCase
from django.urls import reverse, resolve
from school import views

class TestUrls(SimpleTestCase):
    def test_login_url_resolves(self):
        url = reverse('school:login')
        self.assertEqual(resolve(url).func.view_class, views.CustomLoginView)

    def test_student_list_url_resolves(self):
        url = reverse('school:student_list')
        resolved = resolve(url)
        if hasattr(resolved.func, 'view_class'):
            self.assertEqual(resolved.func.view_class, views.StudentListView)
        else:
            self.assertEqual(resolved.func, views.student_list)  # Adjust if your view is function-based
