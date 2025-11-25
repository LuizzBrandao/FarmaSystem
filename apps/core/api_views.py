from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from .notifications import NotificationManager, get_dashboard_stats


@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """API para obter notificações do usuário (filtrando as já marcadas como lidas na sessão)"""
    try:
        manager = NotificationManager(user=request.user)
        all_notifications = manager.get_all_notifications()

        # Filtrar notificações já marcadas como lidas (armazenadas na sessão)
        read_ids = set(request.session.get('read_notifications', []))
        notifications = [n for n in all_notifications if n.get('id') not in read_ids]

        # Recalcular contagens após filtro
        counts = {
            'total': len(notifications),
            'danger': len([n for n in notifications if n['type'] == 'danger']),
            'warning': len([n for n in notifications if n['type'] == 'warning']),
            'info': len([n for n in notifications if n['type'] == 'info']),
            'success': len([n for n in notifications if n['type'] == 'success']),
        }
        
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
@require_http_methods(["POST"])
def mark_notification_read(request):
    """API para marcar notificação como lida (individual ou todas), usando sessão do usuário"""
    try:
        data = json.loads(request.body or '{}')
        read_ids = set(request.session.get('read_notifications', []))

        # Marcar todas como lidas: pega IDs atuais do gerenciador
        if data.get('all'):
            manager = NotificationManager(user=request.user)
            current_notifications = manager.get_all_notifications()
            for n in current_notifications:
                if n.get('id'):
                    read_ids.add(n['id'])
            request.session['read_notifications'] = list(read_ids)
            request.session.modified = True
            return JsonResponse({'success': True, 'message': 'Todas as notificações foram marcadas como lidas', 'marked_count': len(current_notifications)})

        # Marcar uma notificação específica
        notification_id = data.get('notification_id')
        if notification_id:
            read_ids.add(notification_id)
            request.session['read_notifications'] = list(read_ids)
            request.session.modified = True
            return JsonResponse({'success': True, 'message': 'Notificação marcada como lida', 'notification_id': notification_id})
        
        return JsonResponse({'success': False, 'error': 'Dados inválidos'}, status=400)
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
