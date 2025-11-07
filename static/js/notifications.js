/**
 * Sistema de Notificações Funcionais - FarmaSystem
 * Para uso em ambiente de saúde pública municipal
 */

/**
 * Sistema de Notificações Completo
 */
function initNotificationsSystem() {
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationDropdown = document.getElementById('notificationDropdown');
    const notificationList = document.getElementById('notificationList');
    const notificationBadge = document.getElementById('notificationBadge');
    const notificationCount = document.getElementById('notificationCount');
    const refreshBtn = document.getElementById('refreshNotifications');
    const markAllReadBtn = document.getElementById('markAllRead');
    
    if (!notificationBtn) return;
    
    // Estado das notificações
    let notifications = [];
    let isLoading = false;
    
    // Abrir/fechar dropdown
    notificationBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        if (notificationDropdown && notificationDropdown.classList.contains('show')) {
            closeNotificationDropdown();
        } else {
            openNotificationDropdown();
        }
    });
    
    // Botão de refresh
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            loadNotifications(true);
        });
    }
    
    // Marcar todas como lidas
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            markAllNotificationsAsRead();
        });
    }
    
    // Fechar dropdown ao clicar fora
    document.addEventListener('click', function(e) {
        if (!notificationBtn.contains(e.target) && 
            notificationDropdown && !notificationDropdown.contains(e.target)) {
            closeNotificationDropdown();
        }
    });
    
    // Carregar notificações iniciais
    loadNotifications();
    
    // Auto-refresh a cada 30 segundos
    setInterval(() => {
        if (!notificationDropdown || !notificationDropdown.classList.contains('show')) {
            loadNotifications();
        }
    }, 30000);
    
    function openNotificationDropdown() {
        if (notificationDropdown) {
            notificationDropdown.classList.add('show');
            loadNotifications();
        }
    }
    
    function closeNotificationDropdown() {
        if (notificationDropdown) {
            notificationDropdown.classList.remove('show');
        }
    }
    
    function loadNotifications(force = false) {
        if (isLoading && !force) return;
        
        isLoading = true;
        
        // Mostrar loading se forçado
        if (force && refreshBtn) {
            refreshBtn.classList.add('spinning');
        }
        
        fetch('/api/notifications/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    notifications = data.notifications;
                    updateNotificationUI(data.notifications, data.counts);
                } else {
                    showNotificationError('Erro ao carregar notificações');
                }
            })
            .catch(error => {
                console.error('Erro ao carregar notificações:', error);
                showNotificationError('Erro de conexão');
            })
            .finally(() => {
                isLoading = false;
                if (refreshBtn) {
                    refreshBtn.classList.remove('spinning');
                }
            });
    }
    
    function updateNotificationUI(notifications, counts) {
        // Atualizar badge
        if (notificationBadge) {
            const totalCount = counts.danger + counts.warning;
            notificationBadge.textContent = totalCount;
            notificationBadge.style.display = totalCount > 0 ? 'block' : 'none';
            
            // Animar sino se há notificações
            const bell = notificationBtn.querySelector('.notification-bell');
            if (bell) {
                if (totalCount > 0) {
                    bell.classList.add('has-notifications');
                } else {
                    bell.classList.remove('has-notifications');
                }
            }
        }
        
        // Atualizar contador
        if (notificationCount) {
            if (notifications.length === 0) {
                notificationCount.textContent = 'Nenhuma notificação';
            } else {
                notificationCount.textContent = `${notifications.length} notificações`;
            }
        }
        
        // Renderizar lista
        renderNotificationList(notifications);
    }
    
    function renderNotificationList(notifications) {
        if (!notificationList) return;
        
        if (notifications.length === 0) {
            notificationList.innerHTML = `
                <div class="empty-notifications">
                    <i class="fas fa-bell-slash"></i>
                    <p>Nenhuma notificação</p>
                </div>
            `;
            return;
        }
        
        const notificationsHTML = notifications.map(notification => {
            const timeAgo = getTimeAgo(notification.timestamp);
            
            return `
                <div class="notification-item ${notification.type} clickable" 
                     data-notification-id="${notification.id}"
                     data-action-url="${notification.action_url || '#'}"
                     onclick="handleNotificationClick(this)">
                    <i class="${notification.icon}"></i>
                    <div>
                        <strong>${notification.title}</strong>
                        <p>${notification.message}</p>
                        <div class="notification-time">${timeAgo}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        notificationList.innerHTML = notificationsHTML;
    }
    
    function showNotificationError(message) {
        if (notificationList) {
            notificationList.innerHTML = `
                <div class="empty-notifications">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>${message}</p>
                </div>
            `;
        }
    }
    
    function markAllNotificationsAsRead() {
        fetch('/api/notifications/mark-read/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ all: true })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadNotifications(true);
                showToast('Todas as notificações foram marcadas como lidas', 'success');
            }
        })
        .catch(error => {
            console.error('Erro ao marcar notificações:', error);
            showToast('Erro ao marcar notificações como lidas', 'error');
        });
    }
    
    // Expor funções globalmente
    window.NotificationSystem = {
        refresh: () => loadNotifications(true),
        markAllRead: markAllNotificationsAsRead
    };
}

/**
 * Ações Rápidas Funcionais
 */
function initQuickActions() {
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    
    quickActionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const href = this.getAttribute('href');
            const isDropdown = this.closest('.quick-action-dropdown');
            
            // Se é um dropdown, não redirecionar
            if (isDropdown && !href) {
                return;
            }
            
            // Adicionar efeito de loading
            this.classList.add('loading');
            
            // Feedback visual
            const icon = this.querySelector('i');
            const originalClass = icon.className;
            icon.className = 'fas fa-spinner fa-spin';
            
            // Simular loading breve para UX
            setTimeout(() => {
                if (href && href !== '#') {
                    window.location.href = href;
                } else {
                    this.classList.remove('loading');
                    icon.className = originalClass;
                }
            }, 500);
        });
    });
}

/**
 * Alertas Interativos no Dashboard
 */
function initInteractiveAlerts() {
    // Tornar cards de estatísticas clicáveis
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach(card => {
        const bgClass = card.classList.toString();
        let actionUrl = '';
        
        if (bgClass.includes('bg-primary')) {
            actionUrl = '/inventory/medications/';
        } else if (bgClass.includes('bg-success')) {
            actionUrl = '/inventory/stock/';
        } else if (bgClass.includes('bg-warning')) {
            actionUrl = '/inventory/alerts/';
        } else if (bgClass.includes('bg-info')) {
            actionUrl = '/suppliers/';
        }
        
        if (actionUrl) {
            card.style.cursor = 'pointer';
            card.dataset.actionUrl = actionUrl;
            
            card.addEventListener('click', function(e) {
                // Não redirecionar se clicou em um link ou botão
                if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || e.target.closest('a, button')) {
                    return;
                }
                
                // Adicionar efeito visual
                this.classList.add('clicking');
                
                setTimeout(() => {
                    window.location.href = actionUrl;
                }, 150);
            });
        }
    });
    
    // Tornar alertas importantes clicáveis
    const alertCards = document.querySelectorAll('.alert-card');
    
    alertCards.forEach(card => {
        const alertType = card.classList.toString();
        let actionUrl = '';
        
        if (alertType.includes('danger')) {
            actionUrl = '/reports/expiry/'; // Vencidos
        } else if (alertType.includes('warning')) {
            actionUrl = '/reports/expiry/'; // Próximos ao vencimento
        }
        
        if (actionUrl) {
            card.style.cursor = 'pointer';
            card.dataset.actionUrl = actionUrl;
            
            card.addEventListener('click', function(e) {
                if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || e.target.closest('a, button')) {
                    return;
                }
                
                this.classList.add('clicking');
                
                setTimeout(() => {
                    window.location.href = actionUrl;
                }, 150);
            });
        }
    });
}

/**
 * Manipular clique em notificação
 */
function handleNotificationClick(element) {
    const notificationId = element.dataset.notificationId;
    const actionUrl = element.dataset.actionUrl;
    
    // Marcar como lida
    if (notificationId && notificationId !== 'undefined') {
        fetch('/api/notifications/mark-read/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ notification_id: notificationId })
        }).catch(error => console.error('Erro ao marcar notificação:', error));
    }
    
    // Redirecionar se há URL
    if (actionUrl && actionUrl !== '#') {
        window.location.href = actionUrl;
    }
}

/**
 * Função para obter tempo relativo
 */
function getTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInSeconds = Math.floor((now - time) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Agora mesmo';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `há ${minutes} minuto${minutes > 1 ? 's' : ''}`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `há ${hours} hora${hours > 1 ? 's' : ''}`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `há ${days} dia${days > 1 ? 's' : ''}`;
    }
}

/**
 * Sistema de Toast para feedback
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Adicionar estilos inline se não existirem
    if (!document.querySelector('#toast-styles')) {
        const toastStyles = document.createElement('style');
        toastStyles.id = 'toast-styles';
        toastStyles.textContent = `
            .toast {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                min-width: 300px;
                padding: 1rem;
                border-radius: 8px;
                color: white;
                transform: translateX(100%);
                transition: transform 0.3s ease;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            .toast.show { transform: translateX(0); }
            .toast-success { background: #10b981; }
            .toast-error { background: #ef4444; }
            .toast-warning { background: #f59e0b; }
            .toast-info { background: #3b82f6; }
            .toast-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .toast-close {
                background: none;
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                margin-left: 1rem;
                opacity: 0.8;
            }
            .toast-close:hover { opacity: 1; }
            .clicking {
                transform: scale(0.98);
                transition: transform 0.1s ease;
            }
            .loading {
                opacity: 0.7;
                pointer-events: none;
            }
        `;
        document.head.appendChild(toastStyles);
    }
    
    document.body.appendChild(toast);
    
    // Animar entrada
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Auto remover
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Função utilitária para obter CSRF token
 */
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}
