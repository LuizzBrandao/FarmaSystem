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
        """Total de medicamentos únicos na filial"""
        return self.branch_stocks.values('medication').distinct().count()
    
    @property
    def total_stock_quantity(self):
        """Quantidade total de itens em estoque"""
        from django.db.models import Sum
        total = self.branch_stocks.aggregate(
            total=Sum('quantity')
        )['total']
        return total or 0
    
    @property
    def low_stock_count(self):
        """Medicamentos com estoque baixo nesta filial"""
        count = 0
        for stock in self.branch_stocks.select_related('medication'):
            if stock.quantity <= stock.medication.minimum_stock:
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
    
    @property
    def total_batches(self):
        """Retorna o total de lotes"""
        return self.batches.filter(is_active=True).count()
    
    @property
    def expired_batches_count(self):
        """Conta lotes vencidos"""
        return sum(1 for batch in self.batches.filter(is_active=True) if batch.is_expired)
    
    @property
    def near_expiry_batches_count(self):
        """Conta lotes próximos ao vencimento"""
        return sum(1 for batch in self.batches.filter(is_active=True) if batch.is_near_expiry)
    
    @property
    def expiry_status(self):
        """Determina o status geral de vencimento do medicamento"""
        if self.expired_batches_count > 0:
            return 'expired'
        elif self.near_expiry_batches_count > 0:
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
    def expiry_status_class(self):
        """Retorna a classe CSS para o status"""
        return f"status-{self.expiry_status.replace('_', '-')}"
    
    @property
    def has_expiry_issues(self):
        """Verifica se há problemas de vencimento"""
        return self.expiry_status != 'normal'
    
    def get_batches_by_status(self, status):
        """Retorna lotes filtrados por status de vencimento"""
        return [batch for batch in self.batches.filter(is_active=True) if batch.expiry_status == status]
    
    def get_earliest_expiry_batch(self):
        """Retorna o lote com vencimento mais próximo"""
        active_batches = self.batches.filter(is_active=True).order_by('expiry_date')
        return active_batches.first() if active_batches.exists() else None


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


class BranchMedicationBatch(models.Model):
    """Modelo para lotes de medicamentos por filial"""
    
    EXPIRY_STATUS_CHOICES = [
        ('normal', 'Normal'),
        ('near_expiry', 'Próximo ao Vencimento'),
        ('expired', 'Vencido'),
    ]
    
    branch_stock = models.ForeignKey(
        BranchStock,
        on_delete=models.CASCADE,
        related_name='batches',
        verbose_name='Estoque da Filial'
    )
    
    batch_number = models.CharField(
        max_length=50,
        verbose_name='Número do Lote'
    )
    
    quantity = models.PositiveIntegerField(
        verbose_name='Quantidade do Lote'
    )
    
    manufacturing_date = models.DateField(
        verbose_name='Data de Fabricação',
        null=True,
        blank=True
    )
    
    expiry_date = models.DateField(
        verbose_name='Data de Vencimento'
    )
    
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
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
    
    class Meta:
        verbose_name = 'Lote de Medicamento'
        verbose_name_plural = 'Lotes de Medicamentos'
        unique_together = ('branch_stock', 'batch_number')
        ordering = ['expiry_date', 'batch_number']
    
    def __str__(self):
        return f"{self.batch_number} - {self.branch_stock.medication.name} ({self.branch_stock.branch.name})"
    
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
    def expiry_status_class(self):
        """Retorna a classe CSS para o status"""
        return f"status-{self.expiry_status.replace('_', '-')}"
    
    @property
    def is_expired(self):
        """Verifica se o lote está vencido"""
        return self.expiry_status == 'expired'
    
    @property
    def is_near_expiry(self):
        """Verifica se o lote está próximo ao vencimento"""
        return self.expiry_status == 'near_expiry'
    
    def get_expiry_alert_level(self):
        """Retorna o nível de alerta para o vencimento"""
        if self.is_expired:
            return 'danger'
        elif self.is_near_expiry:
            return 'warning'
        else:
            return 'success'
