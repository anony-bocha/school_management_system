from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Decorator to restrict view access to users with specific roles or groups.
    - Checks if user is authenticated.
    - Checks user.role if exists.
    - If no role attribute, checks Django groups.
    - Redirects unauthorized users to 'home' URL or fallback '/'.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('login')

            user_role = getattr(user, 'role', None)

            # If user has a role attribute, check it
            if user_role:
                if user_role not in allowed_roles:
                    try:
                        return redirect(reverse('home'))
                    except Exception:
                        return redirect('/')
            else:
                # Check Django groups if no role attribute
                user_groups = user.groups.values_list('name', flat=True)
                if not any(role in allowed_roles for role in user_groups):
                    try:
                        return redirect(reverse('home'))
                    except Exception:
                        return redirect('/')

            # Authorized - proceed to the view
            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator
