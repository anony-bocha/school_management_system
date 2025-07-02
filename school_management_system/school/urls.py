from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit/', views.submit_student, name='submit_student'),
    path('register/', views.register, name='register'),
]
