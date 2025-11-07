import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.core.mail import send_mail
from django.template import Template, Context
from .models import NotificationTemplate, NotificationLog
import logging

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Serviço para envio de notificações por email"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'EMAIL_PORT', 587)
        self.email_user = getattr(settings, 'EMAIL_HOST_USER', '')
        self.email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        self.use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
    
    def send_notification(self, template_type, recipient_email, context_data, branch=None):
        """Enviar notificação por email"""
        try:
            # Buscar template
            template = NotificationTemplate.objects.get(
                template_type=template_type,
                is_active=True
            )
            
            # Renderizar template
            subject = self._render_template(template.subject, context_data)
            body = self._render_template(template.email_body, context_data)
            
            # Enviar email
            success = send_mail(
                subject=subject,
                message='',  # Texto plano vazio
                html_message=body,
                from_email=self.email_user,
                recipient_list=[recipient_email],
                fail_silently=False
            )
            
            # Registrar log
            log = NotificationLog.objects.create(
                template=template,
                branch=branch,
                recipient_email=recipient_email,
                notification_type='email',
                status='sent' if success else 'failed',
                subject=subject,
                message=body
            )
            
            logger.info(f"Email enviado para {recipient_email}: {subject}")
            return True
            
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Template não encontrado: {template_type}")
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            # Registrar erro no log
            NotificationLog.objects.create(
                template_id=1,  # Template padrão
                branch=branch,
                recipient_email=recipient_email,
                notification_type='email',
                status='failed',
                subject='Erro no envio',
                message='',
                error_message=str(e)
            )
            return False
    
    def _render_template(self, template_string, context_data):
        """Renderizar template com dados dinâmicos"""
        template = Template(template_string)
        context = Context(context_data)
        return template.render(context)


class WhatsAppNotificationService:
    """Serviço para envio de notificações por WhatsApp"""
    
    def __init__(self):
        # Configurações para API do WhatsApp (ex: Twilio, WhatsApp Business API)
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', '')
        self.api_token = getattr(settings, 'WHATSAPP_API_TOKEN', '')
        self.from_number = getattr(settings, 'WHATSAPP_FROM_NUMBER', '')
    
    def send_notification(self, template_type, recipient_phone, context_data, branch=None):
        """Enviar notificação por WhatsApp"""
        try:
            # Buscar template
            template = NotificationTemplate.objects.get(
                template_type=template_type,
                is_active=True
            )
            
            if not template.whatsapp_message:
                logger.warning(f"Template {template_type} não possui mensagem WhatsApp")
                return False
            
            # Renderizar mensagem
            message = self._render_template(template.whatsapp_message, context_data)
            
            # Enviar via API (exemplo usando Twilio)
            success = self._send_whatsapp_message(recipient_phone, message)
            
            # Registrar log
            NotificationLog.objects.create(
                template=template,
                branch=branch,
                recipient_phone=recipient_phone,
                notification_type='whatsapp',
                status='sent' if success else 'failed',
                subject=f"WhatsApp - {template.name}",
                message=message
            )
            
            logger.info(f"WhatsApp enviado para {recipient_phone}")
            return success
            
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Template não encontrado: {template_type}")
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {str(e)}")
            return False
    
    def _send_whatsapp_message(self, to_number, message):
        """Enviar mensagem via API do WhatsApp"""
        if not self.api_url or not self.api_token:
            logger.warning("Configurações do WhatsApp não definidas")
            return False
        
        try:
            # Exemplo usando Twilio
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'from': f'whatsapp:{self.from_number}',
                'to': f'whatsapp:{to_number}',
                'body': message
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erro na API WhatsApp: {str(e)}")
            return False
    
    def _render_template(self, template_string, context_data):
        """Renderizar template com dados dinâmicos"""
        template = Template(template_string)
        context = Context(context_data)
        return template.render(context)


class NotificationManager:
    """Gerenciador principal de notificações"""
    
    def __init__(self):
        self.email_service = EmailNotificationService()
        self.whatsapp_service = WhatsAppNotificationService()
    
    def send_low_stock_alert(self, branch, medication, current_stock):
        """Enviar alerta de estoque baixo"""
        context = {
            'branch_name': branch.name,
            'medication_name': medication.name,
            'current_stock': current_stock,
            'minimum_stock': medication.minimum_stock,
            'supplier': medication.supplier.name
        }
        
        # Enviar por email se configurado
        if branch.email_notifications and branch.email:
            self.email_service.send_notification(
                'low_stock',
                branch.email,
                context,
                branch
            )
        
        # Enviar por WhatsApp se configurado
        if branch.whatsapp_notifications and branch.whatsapp_number:
            self.whatsapp_service.send_notification(
                'low_stock',
                branch.whatsapp_number,
                context,
                branch
            )
    
    def send_expiry_alert(self, branch, medications_expiring):
        """Enviar alerta de medicamentos próximos ao vencimento"""
        context = {
            'branch_name': branch.name,
            'medications_count': len(medications_expiring),
            'medications': medications_expiring
        }
        
        if branch.email_notifications and branch.email:
            self.email_service.send_notification(
                'expiry_alert',
                branch.email,
                context,
                branch
            )
        
        if branch.whatsapp_notifications and branch.whatsapp_number:
            self.whatsapp_service.send_notification(
                'expiry_alert',
                branch.whatsapp_number,
                context,
                branch
            )
    
    def send_transfer_notification(self, transfer):
        """Enviar notificação de transferência"""
        context = {
            'from_branch': transfer.from_branch.name,
            'to_branch': transfer.to_branch.name,
            'medication': transfer.medication.name,
            'quantity': transfer.quantity,
            'status': transfer.get_status_display(),
            'requested_by': transfer.requested_by.get_full_name()
        }
        
        # Notificar filial de destino
        if transfer.to_branch.email_notifications and transfer.to_branch.email:
            self.email_service.send_notification(
                'transfer_request',
                transfer.to_branch.email,
                context,
                transfer.to_branch
            )
