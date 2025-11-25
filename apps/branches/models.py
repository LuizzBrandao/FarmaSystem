# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import datetime, timedelta
from django.utils import timezone


class Branch(models.Model):
    """Modelo para filiais da farmácia"""
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nome da Filial',
        help_text='Ex: Filial Centro, Filial Shopping, etc.'
    )
    
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Código da Filial',
        help_text='Código único da filial (ex: FIL001)'
    )
    
    address = models.TextField(
        verbose_name='Endereço Completo'
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Formato: '+999999999'. Até 15 dígitos."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name='Telefone'
    )
    
    email = models.EmailField(
        verbose_name='E-mail da Filial',
        blank=True,
        null=True
    )
    
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Gerente Responsável',
        related_name='managed_branches'
    )
    
    # Configurações de notificação
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='Receber notificações por email'
    )
    
    whatsapp_notifications = models.BooleanField(
        default=False,
        verbose_name='Receber notificações por WhatsApp'
    )
    
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Número WhatsApp',
        help_text='Formato: +5511999999999'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Filial Ativa'
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
        verbose_name = 'Filial'
        verbose_name_plural = 'Filiais'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def total_medications(self):
        """Total de medicamentos únicos na filial - sempre calculado do banco"""
        # Forçar query fresh do banco para garantir sincronização
        return BranchStock.objects.filter(branch=self).values('medication').distinct().count()
    
    @property
    def total_stock_quantity(self):
        """Quantidade total de itens em estoque - sempre calculado do banco"""
        from django.db.models import Sum
        # Forçar query fresh do banco para garantir sincronização
        total = BranchStock.objects.filter(branch=self).aggregate(
            total=Sum('quantity')
        )['total']
        return total or 0
    
    @property
    def low_stock_count(self):
        """Medicamentos com estoque baixo nesta filial (baseado em available_quantity) - sempre calculado do banco"""
        count = 0
        # Forçar query fresh do banco para garantir sincronização
        for stock in BranchStock.objects.filter(branch=self).select_related('medication'):
            # Usar available_quantity (quantity - reserved_quantity) para verificar estoque baixo
            if stock.available_quantity <= stock.medication.minimum_stock:
                count += 1
        return count


class BranchStock(models.Model):
    """Estoque específico por filial"""
    
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        verbose_name='Filial',
        related_name='branch_stocks'
    )
    
    medication = models.ForeignKey(
        'inventory.Medication',
        on_delete=models.CASCADE,
        verbose_name='Medicamento'
    )
    
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Quantidade em Estoque'
    )
    
    reserved_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Quantidade Reservada',
        help_text='Medicamentos reservados para vendas'
    )
    
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )
    
    class Meta:
        verbose_name = 'Estoque por Filial'
        verbose_name_plural = 'Estoques por Filial'
        unique_together = ['branch', 'medication']
        ordering = ['branch', 'medication__name']
    
    def __str__(self):
        return f"{self.medication.name} - {self.branch.name}: {self.quantity}"
    
    @property
    def available_quantity(self):
        """Quantidade disponível (total - reservada)"""
        return max(0, self.quantity - self.reserved_quantity)
    
    @property
    def is_low_stock(self):
        """Verifica se está com estoque baixo"""
        return self.available_quantity <= self.medication.minimum_stock
    
    # Propriedades relacionadas a lotes foram removidas
    # Funcionalidade de lotes removida do sistema


class StockTransfer(models.Model):
    """Transferências de estoque entre filiais"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('in_transit', 'Em Trânsito'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
    ]
    
    from_branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='transfers_sent',
        verbose_name='Filial Origem'
    )
    
    to_branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='transfers_received',
        verbose_name='Filial Destino'
    )
    
    medication = models.ForeignKey(
        'inventory.Medication',
        on_delete=models.CASCADE,
        verbose_name='Medicamento'
    )
    
    quantity = models.PositiveIntegerField(
        verbose_name='Quantidade'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    
    reason = models.TextField(
        verbose_name='Motivo da Transferência',
        help_text='Descreva o motivo da transferência'
    )
    
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='requested_transfers',
        verbose_name='Solicitado por'
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_transfers',
        verbose_name='Aprovado por'
    )
    
    requested_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data da Solicitação'
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Conclusão'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    class Meta:
        verbose_name = 'Transferência de Estoque'
        verbose_name_plural = 'Transferências de Estoque'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.medication.name}: {self.from_branch.code} → {self.to_branch.code}"

# Modelo BranchMedicationBatch foi removido
# A funcionalidade de lotes foi completamente removida do sistema
