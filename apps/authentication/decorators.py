from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile


def role_required(allowed_roles):
    """
    Decorador para controlar acesso baseado em roles do usuário
    
    Usage:
    @role_required(['admin', 'farmaceutico'])
    def minha_view(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            try:
                user_profile = request.user.userprofile
                if user_profile.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(
                        request, 
                        f'Acesso negado. Você não tem permissão para acessar esta página. '
                        f'Função necessária: {", ".join(allowed_roles)}'
                    )
                    return redirect('core:dashboard')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Perfil de usuário não encontrado.')
                return redirect('core:dashboard')
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Decorador para acesso apenas de administradores"""
    return role_required(['admin'])(view_func)


def farmaceutico_required(view_func):
    """Decorador para acesso de farmacêuticos e administradores"""
    return role_required(['admin', 'farmaceutico'])(view_func)


def staff_required(view_func):
    """Decorador para acesso de todos os usuários logados (qualquer role)"""
    return role_required(['admin', 'farmaceutico', 'operador'])(view_func)


class RoleRequiredMixin:
    """
    Mixin para Class-Based Views que requer determinados roles
    
    Usage:
    class MinhaView(RoleRequiredMixin, ListView):
        allowed_roles = ['admin', 'farmaceutico']
        ...
    """
    allowed_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('authentication:login')
        
        try:
            user_profile = request.user.userprofile
            if user_profile.role not in self.allowed_roles:
                messages.error(
                    request,
                    f'Acesso negado. Função necessária: {", ".join(self.allowed_roles)}'
                )
                return redirect('core:dashboard')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Perfil de usuário não encontrado.')
            return redirect('core:dashboard')
        
        return super().dispatch(request, *args, **kwargs)
