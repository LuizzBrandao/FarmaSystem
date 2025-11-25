from django.contrib.auth import get_user_model
from apps.authentication.models import UserProfile

User = get_user_model()

u, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
    }
)

# Garantir privilégios de admin
u.is_staff = True
u.is_superuser = True
u.set_password('admin123')
u.save()

# Garantir perfil com role de administrador
try:
    profile = u.userprofile
except UserProfile.DoesNotExist:
    profile = UserProfile.objects.create(user=u)

profile.role = 'admin'
profile.save()

print('[OK] Usuário admin', 'criado' if created else 'atualizado', 'com senha: admin123')