from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile


@login_required
def profile(request):
    """Visualizar e editar perfil do usuário"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Atualizar dados do usuário
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Atualizar perfil
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.save()
        
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('authentication:profile')
    
    context = {
        'profile': profile,
    }
    
    return render(request, 'auth/profile.html', context)