from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('login')
            
            user_role = getattr(user, 'role', None)
            if user_role:
                if user_role not in allowed_roles:
                    try:
                        return redirect(reverse('home'))
                    except:
                        return redirect('/')
            else:
                user_groups = user.groups.values_list('name', flat=True)
                if not any(role in allowed_roles for role in user_groups):
                    try:
                        return redirect(reverse('home'))
                    except:
                        return redirect('/')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
