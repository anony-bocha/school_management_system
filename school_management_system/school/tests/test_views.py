from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('school:login')
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')

    def test_login_view_status_code(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_login_view_successful_login(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

def test_login_view_invalid_credentials(self):
    response = self.client.post(self.login_url, {'username': 'wrong', 'password': 'wrong'})
    self.assertEqual(response.status_code, 200)  # login page redisplayed
    self.assertContains(response, "Please enter a correct username and password")

