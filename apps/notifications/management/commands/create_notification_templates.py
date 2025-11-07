from django.core.management.base import BaseCommand
from apps.notifications.models import NotificationTemplate


class Command(BaseCommand):
    help = 'Criar templates padrão de notificações'

    def handle(self, *args, **options):
        """Criar templates de notificação padrão"""
        
        templates = [
            {
                'name': 'Alerta de Estoque Baixo',
                'template_type': 'low_stock',
                'subject': '🚨 ALERTA: Estoque Baixo - {{medication_name}} - {{branch_name}}',
                'email_body': '''
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                        .header { background: #ef4444; color: white; padding: 20px; border-radius: 5px; text-align: center; }
                        .content { padding: 20px 0; }
                        .alert-box { background: #fef2f2; border: 1px solid #ef4444; padding: 15px; border-radius: 5px; margin: 15px 0; }
                        .footer { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #666; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🚨 ALERTA DE ESTOQUE BAIXO</h1>
                        </div>
                        <div class="content">
                            <p><strong>Filial:</strong> {{branch_name}}</p>
                            
                            <div class="alert-box">
                                <h3>⚠️ {{medication_name}}</h3>
                                <p><strong>Estoque Atual:</strong> {{current_stock}} unidades</p>
                                <p><strong>Estoque Mínimo:</strong> {{minimum_stock}} unidades</p>
                                <p><strong>Fornecedor:</strong> {{supplier}}</p>
                            </div>
                            
                            <p><strong>Ação Necessária:</strong></p>
                            <ul>
                                <li>Verificar necessidade de nova compra</li>
                                <li>Contactar fornecedor: {{supplier}}</li>
                                <li>Considerar transferência de outras filiais</li>
                            </ul>
                        </div>
                        <div class="footer">
                            <p>FarmaSystem - Sistema de Gestão de Farmácia</p>
                            <p>Este é um email automático. Não responda.</p>
                        </div>
                    </div>
                </body>
                </html>
                ''',
                'whatsapp_message': '''🚨 *ALERTA ESTOQUE BAIXO*

📍 *Filial:* {{branch_name}}
💊 *Medicamento:* {{medication_name}}
📦 *Estoque Atual:* {{current_stock}} unidades
⚠️ *Estoque Mínimo:* {{minimum_stock}} unidades
🏭 *Fornecedor:* {{supplier}}

*Ação necessária:* Verificar necessidade de reposição

_FarmaSystem - Notificação Automática_'''
            },
            
            {
                'name': 'Medicamentos Próximos ao Vencimento',
                'template_type': 'expiry_alert',
                'subject': '⏰ ALERTA: Medicamentos Próximos ao Vencimento - {{branch_name}}',
                'email_body': '''
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                        .header { background: #f59e0b; color: white; padding: 20px; border-radius: 5px; text-align: center; }
                        .content { padding: 20px 0; }
                        .warning-box { background: #fffbeb; border: 1px solid #f59e0b; padding: 15px; border-radius: 5px; margin: 15px 0; }
                        .medication-list { background: #f8f9fa; padding: 15px; border-radius: 5px; }
                        .footer { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #666; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>⏰ ALERTA DE VENCIMENTO</h1>
                        </div>
                        <div class="content">
                            <p><strong>Filial:</strong> {{branch_name}}</p>
                            
                            <div class="warning-box">
                                <h3>⚠️ {{medications_count}} medicamento(s) próximo(s) ao vencimento</h3>
                                <p>Os seguintes medicamentos vencem em até 30 dias:</p>
                            </div>
                            
                            <div class="medication-list">
                                {% for med in medications %}
                                <p>• <strong>{{med.name}}</strong> - Vence em: {{med.days_to_expire}} dias</p>
                                {% endfor %}
                            </div>
                            
                            <p><strong>Ações Recomendadas:</strong></p>
                            <ul>
                                <li>Priorizar venda destes medicamentos</li>
                                <li>Verificar possibilidade de devolução ao fornecedor</li>
                                <li>Considerar transferência para outras filiais</li>
                                <li>Atualizar sistema de compras</li>
                            </ul>
                        </div>
                        <div class="footer">
                            <p>FarmaSystem - Sistema de Gestão de Farmácia</p>
                        </div>
                    </div>
                </body>
                </html>
                ''',
                'whatsapp_message': '''⏰ *ALERTA VENCIMENTO*

📍 *Filial:* {{branch_name}}
📊 *Medicamentos:* {{medications_count}} próximos ao vencimento

*Ação necessária:* Verificar medicamentos que vencem em 30 dias

_FarmaSystem - Notificação Automática_'''
            },
            
            {
                'name': 'Solicitação de Transferência',
                'template_type': 'transfer_request',
                'subject': '📦 Nova Solicitação de Transferência - {{medication}}',
                'email_body': '''
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                        .header { background: #2563eb; color: white; padding: 20px; border-radius: 5px; text-align: center; }
                        .content { padding: 20px 0; }
                        .transfer-box { background: #eff6ff; border: 1px solid #2563eb; padding: 15px; border-radius: 5px; margin: 15px 0; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>📦 SOLICITAÇÃO DE TRANSFERÊNCIA</h1>
                        </div>
                        <div class="content">
                            <div class="transfer-box">
                                <h3>{{medication}}</h3>
                                <p><strong>De:</strong> {{from_branch}}</p>
                                <p><strong>Para:</strong> {{to_branch}}</p>
                                <p><strong>Quantidade:</strong> {{quantity}} unidades</p>
                                <p><strong>Solicitado por:</strong> {{requested_by}}</p>
                                <p><strong>Status:</strong> {{status}}</p>
                            </div>
                            
                            <p>Uma nova solicitação de transferência foi criada e aguarda aprovação.</p>
                        </div>
                    </div>
                </body>
                </html>
                ''',
                'whatsapp_message': '''📦 *NOVA TRANSFERÊNCIA*

💊 *Medicamento:* {{medication}}
📍 *De:* {{from_branch}}
📍 *Para:* {{to_branch}}
📦 *Quantidade:* {{quantity}} unidades
👤 *Solicitado por:* {{requested_by}}

_Aguardando aprovação_'''
            }
        ]
        
        created_count = 0
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                template_type=template_data['template_type'],
                defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Template criado: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Template já existe: {template.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'🎉 Processo concluído! {created_count} templates criados.')
        )
