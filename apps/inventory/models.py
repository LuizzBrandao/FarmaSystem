from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Category(models.Model):
    """Modelo para categorias de medicamentos"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nome'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
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
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Medication(models.Model):
    """Modelo para medicamentos"""
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nome'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Categoria'
    )
    
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        verbose_name='Fornecedor'
    )
    
    barcode = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Código de Barras'
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço'
    )
    
    minimum_stock = models.PositiveIntegerField(
        default=10,
        verbose_name='Estoque Mínimo'
    )
    
    image = models.ImageField(
        upload_to='medications/',
        blank=True,
        null=True,
        verbose_name='Imagem'
    )
    
    active_principle = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Princípio Ativo'
    )
    
    dosage = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Dosagem'
    )
    
    pharmaceutical_form = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Forma Farmacêutica'
    )
    
    requires_prescription = models.BooleanField(
        default=False,
        verbose_name='Requer Prescrição'
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
        verbose_name = 'Medicamento'
        verbose_name_plural = 'Medicamentos'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.dosage}"
    
    @property
    def current_stock(self):
        """Retorna o estoque atual do medicamento"""
        from django.db.models import Sum
        total = self.stock_set.aggregate(
            total=Sum('quantity')
        )['total']
        return total or 0
    
    @property
    def is_low_stock(self):
        """Verifica se o estoque está baixo"""
        return self.current_stock <= self.minimum_stock


class Stock(models.Model):
    """Modelo para controle de estoque"""
    
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        verbose_name='Medicamento'
    )
    
    quantity = models.PositiveIntegerField(
        verbose_name='Quantidade'
    )
    
    expiry_date = models.DateField(
        verbose_name='Data de Validade'
    )
    
    batch_number = models.CharField(
        max_length=50,
        verbose_name='Número do Lote'
    )
    
    entry_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Entrada'
    )
    
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço de Compra'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    
    class Meta:
        verbose_name = 'Estoque'
        verbose_name_plural = 'Estoques'
        ordering = ['-entry_date']
    
    def __str__(self):
        return f"{self.medication.name} - Lote: {self.batch_number}"
    
    @property
    def is_expired(self):
        """Verifica se o lote está vencido"""
        from django.utils import timezone
        return self.expiry_date < timezone.now().date()
    
    @property
    def is_near_expiry(self):
        """Verifica se o lote está próximo do vencimento (30 dias)"""
        from django.utils import timezone
        from datetime import timedelta
        return self.expiry_date <= timezone.now().date() + timedelta(days=30)


class StockMovement(models.Model):
    """Modelo para movimentações de estoque"""
    
    MOVEMENT_TYPES = (
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('ajuste', 'Ajuste'),
        ('vencimento', 'Vencimento'),
    )
    
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        verbose_name='Medicamento'
    )
    
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES,
        verbose_name='Tipo de Movimentação'
    )
    
    quantity = models.IntegerField(
        verbose_name='Quantidade'
    )
    
    reason = models.TextField(
        verbose_name='Motivo',
        blank=True,
        null=True
    )
    
    batch_number = models.CharField(
        max_length=50,
        verbose_name='Número do Lote',
        blank=True,
        null=True
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuário'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data da Movimentação'
    )
    
    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.medication.name} - {self.movement_type} - {self.quantity}"


class Alert(models.Model):
    """Modelo para alertas do sistema"""
    
    ALERT_TYPES = (
        ('estoque_baixo', 'Estoque Baixo'),
        ('vencimento_proximo', 'Vencimento Próximo'),
        ('vencido', 'Vencido'),
        ('sistema', 'Sistema'),
    )
    
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        verbose_name='Medicamento',
        blank=True,
        null=True
    )
    
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        verbose_name='Tipo de Alerta'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    
    message = models.TextField(
        verbose_name='Mensagem'
    )
    
    is_resolved = models.BooleanField(
        default=False,
        verbose_name='Resolvido'
    )
    
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Resolvido por',
        related_name='resolved_alerts'
    )
    
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Resolvido em'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.alert_type}"