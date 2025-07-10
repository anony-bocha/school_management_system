from django.shortcuts import redirect
from django.urls import reverse

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.force_password_change and request.path != reverse('school:force_password_change'):
                return redirect('school:force_password_change')
        return self.get_response(request)
