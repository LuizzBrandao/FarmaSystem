from django.utils.deprecation import MiddlewareMixin
from .models import UserProfile


class UserProfileMiddleware(MiddlewareMixin):
    """
    Middleware para adicionar informações do perfil do usuário
    ao contexto de todas as requisições
    """
    
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                request.user_profile = request.user.userprofile
            except UserProfile.DoesNotExist:
                # Criar perfil se não existir
                request.user_profile = UserProfile.objects.create(user=request.user)
        else:
            request.user_profile = None
        
        return None


def user_profile_context_processor(request):
    """
    Context processor para disponibilizar informações do perfil
    em todos os templates
    """
    if hasattr(request, 'user_profile') and request.user_profile:
        return {
            'user_profile': request.user_profile,
            'user_role': request.user_profile.role,
            'user_role_display': request.user_profile.get_role_display(),
            'is_admin': request.user_profile.is_admin,
            'is_farmaceutico': request.user_profile.is_farmaceutico,
            'is_operador': request.user_profile.is_operador,
        }
    return {
        'user_profile': None,
        'user_role': None,
        'user_role_display': None,
        'is_admin': False,
        'is_farmaceutico': False,
        'is_operador': False,
    }
