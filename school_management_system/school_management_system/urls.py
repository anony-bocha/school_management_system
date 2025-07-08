from django.contrib import admin
from django.urls import path, include
from school import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('school.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),  # ✅ required
]
