from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from .notifications import NotificationManager, get_dashboard_stats


@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """API para obter notificações do usuário"""
    try:
        manager = NotificationManager(user=request.user)
        notifications = manager.get_all_notifications()
        counts = manager.get_notification_counts()
        
        return JsonResponse({
            'success': True,
            'notifications': notifications,
            'counts': counts,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_critical_notifications(request):
    """API para obter notificações críticas"""
    try:
        manager = NotificationManager(user=request.user)
        critical_notifications = manager.get_critical_notifications(limit=10)
        
        return JsonResponse({
            'success': True,
            'notifications': critical_notifications,
            'count': len(critical_notifications)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def mark_notification_read(request):
    """API para marcar notificação como lida"""
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        # Aqui você pode implementar a lógica para marcar como lida
        # Por exemplo, salvar em uma tabela de notificações lidas
        
        return JsonResponse({
            'success': True,
            'message': 'Notificação marcada como lida'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_dashboard_data(request):
    """API para obter dados do dashboard"""
    try:
        stats = get_dashboard_stats()
        manager = NotificationManager(user=request.user)
        critical_notifications = manager.get_critical_notifications(limit=5)
        
        return JsonResponse({
            'success': True,
            'stats': stats,
            'critical_notifications': critical_notifications
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def check_system_health(request):
    """API para verificar saúde do sistema"""
    try:
        from django.db import connection
        from django.core.cache import cache
        
        # Verificar conexão com banco
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Verificar cache (se configurado)
        cache_working = True
        try:
            cache.set('health_check', 'ok', 10)
            cache_working = cache.get('health_check') == 'ok'
        except:
            cache_working = False
        
        # Obter estatísticas do sistema
        stats = get_dashboard_stats()
        
        health_status = {
            'database': True,
            'cache': cache_working,
            'critical_alerts': stats.get('expired_count', 0) + stats.get('unresolved_alerts', 0),
            'warnings': stats.get('low_stock_count', 0) + stats.get('near_expiry_count', 0),
            'timestamp': timezone.now().isoformat()
        }
        
        # Determinar status geral
        overall_status = 'healthy'
        if health_status['critical_alerts'] > 0:
            overall_status = 'critical'
        elif health_status['warnings'] > 5:
            overall_status = 'warning'
        
        health_status['overall'] = overall_status
        
        return JsonResponse({
            'success': True,
            'health': health_status
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'health': {
                'overall': 'error',
                'database': False,
                'cache': False
            }
        }, status=500)
