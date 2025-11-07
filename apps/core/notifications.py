from django.utils import timezone
from django.db.models import Q, Sum, F
from datetime import datetime, timedelta
from apps.inventory.models import Medication, Stock, Alert
from apps.suppliers.models import Supplier


class NotificationManager:
    """Gerenciador de notificações do sistema"""
    
    def __init__(self, user=None):
        self.user = user
        self.notifications = []
    
    def get_all_notifications(self):
        """Obter todas as notificações do sistema"""
        self.notifications = []
        
        # Verificar estoque baixo
        self._check_low_stock()
        
        # Verificar vencimentos próximos
        self._check_near_expiry()
        
        # Verificar medicamentos vencidos
        self._check_expired_medications()
        
        # Verificar fornecedores inativos
        self._check_inactive_suppliers()
        
        # Verificar alertas não resolvidos
        self._check_unresolved_alerts()
        
        return sorted(self.notifications, key=lambda x: x['priority'], reverse=True)
    
    def _check_low_stock(self):
        """Verificar medicamentos com estoque baixo"""
        # Buscar todos os medicamentos ativos e verificar estoque usando a propriedade
        medications = Medication.objects.filter(is_active=True).select_related('category')
        
        for med in medications:
            if med.is_low_stock:  # Usa a propriedade is_low_stock que já verifica current_stock
                self.notifications.append({
                    'id': f'low_stock_{med.id}',
                    'type': 'warning',
                    'priority': 3,
                    'title': 'Estoque Baixo',
                    'message': f'{med.name} com apenas {med.current_stock} unidades',
                    'icon': 'fas fa-exclamation-triangle',
                    'color': 'warning',
                    'timestamp': timezone.now(),
                    'action_url': f'/inventory/medications/{med.id}/',
                    'action_text': 'Ver Medicamento',
                    'category': 'estoque'
                })
    
    def _check_near_expiry(self):
        """Verificar medicamentos próximos ao vencimento"""
        near_expiry_date = timezone.now().date() + timedelta(days=30)
        
        near_expiry_stock = Stock.objects.filter(
            is_active=True,
            expiry_date__lte=near_expiry_date,
            expiry_date__gte=timezone.now().date()
        ).select_related('medication')
        
        count = near_expiry_stock.count()
        if count > 0:
            self.notifications.append({
                'id': 'near_expiry',
                'type': 'warning',
                'priority': 4,
                'title': 'Vencimento Próximo',
                'message': f'{count} medicamentos vencem em 30 dias',
                'icon': 'fas fa-clock',
                'color': 'warning',
                'timestamp': timezone.now(),
                'action_url': '/reports/expiry/',
                'action_text': 'Gerar Relatório',
                'category': 'vencimento'
            })
    
    def _check_expired_medications(self):
        """Verificar medicamentos vencidos"""
        expired_stock = Stock.objects.filter(
            is_active=True,
            expiry_date__lt=timezone.now().date()
        ).select_related('medication')
        
        count = expired_stock.count()
        if count > 0:
            self.notifications.append({
                'id': 'expired',
                'type': 'danger',
                'priority': 5,
                'title': 'Medicamentos Vencidos',
                'message': f'{count} lotes vencidos requerem ação imediata',
                'icon': 'fas fa-calendar-times',
                'color': 'danger',
                'timestamp': timezone.now(),
                'action_url': '/reports/expiry/',
                'action_text': 'Ação Imediata',
                'category': 'vencimento'
            })
    
    def _check_inactive_suppliers(self):
        """Verificar fornecedores inativos há muito tempo"""
        inactive_suppliers = Supplier.objects.filter(
            is_active=False,
            updated_at__lt=timezone.now() - timedelta(days=90)
        )
        
        count = inactive_suppliers.count()
        if count > 0:
            self.notifications.append({
                'id': 'inactive_suppliers',
                'type': 'info',
                'priority': 2,
                'title': 'Fornecedores Inativos',
                'message': f'{count} fornecedores inativos há mais de 90 dias',
                'icon': 'fas fa-truck',
                'color': 'info',
                'timestamp': timezone.now(),
                'action_url': '/suppliers/',
                'action_text': 'Revisar',
                'category': 'fornecedores'
            })
    
    def _check_unresolved_alerts(self):
        """Verificar alertas não resolvidos"""
        unresolved_alerts = Alert.objects.filter(
            is_resolved=False,
            created_at__lt=timezone.now() - timedelta(hours=24)
        )
        
        count = unresolved_alerts.count()
        if count > 0:
            self.notifications.append({
                'id': 'unresolved_alerts',
                'type': 'warning',
                'priority': 3,
                'title': 'Alertas Pendentes',
                'message': f'{count} alertas não resolvidos há mais de 24h',
                'icon': 'fas fa-bell',
                'color': 'warning',
                'timestamp': timezone.now(),
                'action_url': '/inventory/alerts/',
                'action_text': 'Ver Alertas',
                'category': 'alertas'
            })
    
    def get_notification_counts(self):
        """Obter contadores de notificações por tipo"""
        notifications = self.get_all_notifications()
        
        counts = {
            'total': len(notifications),
            'danger': len([n for n in notifications if n['type'] == 'danger']),
            'warning': len([n for n in notifications if n['type'] == 'warning']),
            'info': len([n for n in notifications if n['type'] == 'info']),
            'success': len([n for n in notifications if n['type'] == 'success']),
        }
        
        return counts
    
    def get_critical_notifications(self, limit=5):
        """Obter notificações mais críticas"""
        all_notifications = self.get_all_notifications()
        return all_notifications[:limit]


def get_dashboard_stats():
    """Obter estatísticas para o dashboard"""
    from django.db.models import Count, Sum, Q
    
    # Estatísticas básicas
    total_medications = Medication.objects.filter(is_active=True).count()
    total_stock = Stock.objects.filter(is_active=True).aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    # Estoque baixo - contar usando a propriedade is_low_stock
    medications = Medication.objects.filter(is_active=True)
    low_stock_count = sum(1 for med in medications if med.is_low_stock)
    
    # Próximos ao vencimento (30 dias)
    near_expiry_date = timezone.now().date() + timedelta(days=30)
    near_expiry_count = Stock.objects.filter(
        is_active=True,
        expiry_date__lte=near_expiry_date,
        expiry_date__gte=timezone.now().date()
    ).count()
    
    # Vencidos
    expired_count = Stock.objects.filter(
        is_active=True,
        expiry_date__lt=timezone.now().date()
    ).count()
    
    # Fornecedores ativos
    total_suppliers = Supplier.objects.filter(is_active=True).count()
    
    # Alertas não resolvidos
    unresolved_alerts = Alert.objects.filter(is_resolved=False).count()
    
    return {
        'total_medications': total_medications,
        'total_stock': total_stock,
        'low_stock_count': low_stock_count,
        'near_expiry_count': near_expiry_count,
        'expired_count': expired_count,
        'total_suppliers': total_suppliers,
        'unresolved_alerts': unresolved_alerts,
    }
