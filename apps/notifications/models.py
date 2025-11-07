from django.db import models
from django.contrib.auth.models import User


class NotificationTemplate(models.Model):
    """Templates para diferentes tipos de notificações"""
    
    TEMPLATE_TYPES = [
        ('low_stock', 'Estoque Baixo'),
        ('expiry_alert', 'Vencimento Próximo'),
        ('expired_medication', 'Medicamento Vencido'),
        ('transfer_request', 'Solicitação de Transferência'),
        ('transfer_completed', 'Transferência Concluída'),
        ('daily_report', 'Relatório Diário'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nome do Template'
    )
    
    template_type = models.CharField(
        max_length=20,
        choices=TEMPLATE_TYPES,
        verbose_name='Tipo de Template'
    )
    
    subject = models.CharField(
        max_length=200,
        verbose_name='Assunto do E-mail'
    )
    
    email_body = models.TextField(
        verbose_name='Corpo do E-mail (HTML)',
        help_text='Use {{variavel}} para dados dinâmicos'
    )
    
    whatsapp_message = models.TextField(
        verbose_name='Mensagem WhatsApp',
        help_text='Use {{variavel}} para dados dinâmicos',
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Template Ativo'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    class Meta:
        verbose_name = 'Template de Notificação'
        verbose_name_plural = 'Templates de Notificação'
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class NotificationLog(models.Model):
    """Log de notificações enviadas"""
    
    NOTIFICATION_TYPES = [
        ('email', 'E-mail'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('sent', 'Enviado'),
        ('failed', 'Falhou'),
        ('delivered', 'Entregue'),
    ]
    
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.CASCADE,
        verbose_name='Template Usado'
    )
    
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        verbose_name='Filial',
        null=True,
        blank=True
    )
    
    recipient_email = models.EmailField(
        verbose_name='E-mail Destinatário',
        blank=True,
        null=True
    )
    
    recipient_phone = models.CharField(
        max_length=20,
        verbose_name='Telefone Destinatário',
        blank=True,
        null=True
    )
    
    notification_type = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPES,
        verbose_name='Tipo de Notificação'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    
    subject = models.CharField(
        max_length=200,
        verbose_name='Assunto'
    )
    
    message = models.TextField(
        verbose_name='Mensagem Enviada'
    )
    
    sent_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Enviado em'
    )
    
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Entregue em'
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensagem de Erro'
    )
    
    class Meta:
        verbose_name = 'Log de Notificação'
        verbose_name_plural = 'Logs de Notificações'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.template.name} - {self.get_notification_type_display()}"
