from django.contrib import admin
from .models import NotificationTemplate, NotificationLog


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'subject']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Template', {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('E-mail', {
            'fields': ('subject', 'email_body'),
            'description': 'Use {{variavel}} para dados dinâmicos'
        }),
        ('WhatsApp', {
            'fields': ('whatsapp_message',),
            'description': 'Mensagem para WhatsApp (opcional)'
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['template', 'notification_type', 'status', 'recipient_email', 'recipient_phone', 'sent_at']
    list_filter = ['notification_type', 'status', 'sent_at', 'template__template_type']
    search_fields = ['recipient_email', 'recipient_phone', 'subject', 'template__name']
    readonly_fields = ['sent_at', 'delivered_at']
    
    fieldsets = (
        ('Notificação', {
            'fields': ('template', 'branch', 'notification_type', 'status')
        }),
        ('Destinatário', {
            'fields': ('recipient_email', 'recipient_phone')
        }),
        ('Conteúdo', {
            'fields': ('subject', 'message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Erro', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        # Não permitir criação manual de logs
        return False
