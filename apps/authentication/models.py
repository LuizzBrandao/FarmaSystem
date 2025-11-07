from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(models.Model):
    """Extensão do modelo de usuário padrão do Django"""
    
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('farmaceutico', 'Farmacêutico'),
        ('operador', 'Operador'),
    )
    
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name='Usuário'
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='operador',
        verbose_name='Função'
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Telefone'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Endereço'
    )
    
    photo = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name='Foto'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_farmaceutico(self):
        return self.role == 'farmaceutico'
    
    @property
    def is_operador(self):
        return self.role == 'operador'


# Signal para criar perfil automaticamente ao criar usuário
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()