from django.db import models
from django.core.validators import RegexValidator


class Supplier(models.Model):
    """Modelo para fornecedores de medicamentos"""
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nome',
        help_text='Nome da empresa fornecedora'
    )
    
    email = models.EmailField(
        verbose_name='E-mail',
        blank=True,
        null=True
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Número de telefone deve estar no formato: '+999999999'. Até 15 dígitos permitidos."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name='Telefone',
        blank=True,
        null=True
    )
    
    address = models.TextField(
        verbose_name='Endereço',
        blank=True,
        null=True
    )
    
    contact_person = models.CharField(
        max_length=100,
        verbose_name='Pessoa de Contato',
        blank=True,
        null=True
    )
    
    cnpj = models.CharField(
        max_length=18,
        verbose_name='CNPJ',
        blank=True,
        null=True,
        unique=True
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
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
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['name']
    
    def __str__(self):
        return self.name