from django.urls import path, include
from . import views
from .views import register
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),

    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', register, name='register'),  # ✅ Only one signup path

    path('accounts/', include('django.contrib.auth.urls')),  # Good to keep
]
