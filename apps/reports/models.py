from django.db import models
from django.contrib.auth.models import User


class Report(models.Model):
    """Modelo para relatórios gerados"""
    
    REPORT_TYPES = (
        ('estoque', 'Relatório de Estoque'),
        ('movimentacao', 'Relatório de Movimentação'),
        ('vencimento', 'Relatório de Vencimentos'),
        ('vendas', 'Relatório de Vendas'),
        ('fornecedores', 'Relatório de Fornecedores'),
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPES,
        verbose_name='Tipo de Relatório'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    
    file_path = models.FileField(
        upload_to='reports/',
        blank=True,
        null=True,
        verbose_name='Arquivo'
    )
    
    generated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Gerado por'
    )
    
    date_from = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data Inicial'
    )
    
    date_to = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data Final'
    )
    
    parameters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Parâmetros'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Gerado em'
    )
    
    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%d/%m/%Y')}"