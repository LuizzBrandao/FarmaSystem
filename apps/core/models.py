from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone


class MedicationBatch(models.Model):
    """
    FONTE ÚNICA DE VERDADE para todos os lotes de medicamentos
    Substitui tanto inventory.Stock quanto branches.BranchMedicationBatch
    """
    
    # Informações do Lote (imutáveis)
    batch_number = models.CharField(
        max_length=50,
        unique=True,  # GLOBAL UNIQUE - não pode duplicar
        verbose_name='Número do Lote',
        help_text='Código único do lote em todo o sistema'
    )
    
    medication = models.ForeignKey(
        'inventory.Medication',
        on_delete=models.CASCADE,
        verbose_name='Medicamento',
        related_name='unified_batches'
    )
    
    # Datas (fonte única de verdade)
    manufacturing_date = models.DateField(
        verbose_name='Data de Fabricação',
        null=True,
        blank=True
    )
    
    expiry_date = models.DateField(
        verbose_name='Data de Vencimento',
        help_text='Data única válida em todo o sistema'
    )
    
    # Informações comerciais
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço de Compra',
        null=True,
        blank=True
    )
    
    supplier_reference = models.CharField(
        max_length=100,
        verbose_name='Referência do Fornecedor',
        blank=True,
        null=True
    )
    
    # Quantidades originais
    initial_quantity = models.PositiveIntegerField(
        verbose_name='Quantidade Inicial',
        help_text='Quantidade total produzida neste lote'
    )
    
    # Controles
    is_active = models.BooleanField(
        default=True,
        verbose_name='Lote Ativo'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Criado por'
    )
    
    class Meta:
        verbose_name = 'Lote de Medicamento (Unificado)'
        verbose_name_plural = 'Lotes de Medicamentos (Unificados)'
        ordering = ['expiry_date', 'batch_number']
    
    def __str__(self):
        return f"{self.batch_number} - {self.medication.name}"
    
    @property
    def days_until_expiry(self):
        """Calcula quantos dias faltam para o vencimento"""
        if not self.expiry_date:
            return None
        
        today = timezone.now().date()
        delta = self.expiry_date - today
        return delta.days
    
    @property
    def expiry_status(self):
        """Determina o status de vencimento do lote"""
        days = self.days_until_expiry
        
        if days is None:
            return 'normal'
        
        if days < 0:
            return 'expired'
        elif days <= 30:  # 30 dias para vencimento
            return 'near_expiry'
        else:
            return 'normal'
    
    @property
    def expiry_status_display(self):
        """Retorna a descrição do status de vencimento"""
        status_map = {
            'normal': 'Normal',
            'near_expiry': 'Próximo ao Vencimento',
            'expired': 'Vencido'
        }
        return status_map.get(self.expiry_status, 'Normal')
    
    @property
    def is_expired(self):
        """Verifica se o lote está vencido"""
        return self.expiry_status == 'expired'
    
    @property
    def is_near_expiry(self):
        """Verifica se o lote está próximo ao vencimento"""
        return self.expiry_status == 'near_expiry'


class BatchLocation(models.Model):
    """
    CONTROLE DE LOCALIZAÇÃO de cada lote
    """
    
    LOCATION_TYPES = [
        ('general', 'Estoque Geral'),
        ('branch', 'Filial'),
    ]
    
    # Relacionamentos
    batch = models.ForeignKey(
        MedicationBatch,
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name='Lote'
    )
    
    # Localização
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPES,
        verbose_name='Tipo de Local'
    )
    
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Filial',
        help_text='NULL para estoque geral'
    )
    
    # Quantidades
    quantity = models.PositiveIntegerField(
        verbose_name='Quantidade no Local',
        default=0
    )
    
    reserved_quantity = models.PositiveIntegerField(
        verbose_name='Quantidade Reservada',
        default=0
    )
    
    # Controles
    is_active = models.BooleanField(
        default=True,
        verbose_name='Localização Ativa'
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
        verbose_name = 'Localização do Lote'
        verbose_name_plural = 'Localizações dos Lotes'
        unique_together = [('batch', 'location_type', 'branch')]
        ordering = ['batch__expiry_date', 'batch__batch_number']
    
    def __str__(self):
        location_name = self.branch.name if self.branch else 'Estoque Geral'
        return f"{self.batch.batch_number} em {location_name}: {self.quantity}"
    
    @property
    def available_quantity(self):
        """Quantidade disponível (total - reservada)"""
        return max(0, self.quantity - self.reserved_quantity)
    
    @property
    def location_name(self):
        """Nome da localização"""
        return self.branch.name if self.branch else 'Estoque Geral'