/**
 * Sistema de Farmácia - JavaScript Principal
 * Responsável por interações, animações e funcionalidades gerais
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Ocultar loading screen
    hideLoadingScreen();
    
    // Inicializar componentes
    initSidebar();
    initModals();
    initAlerts();
    initSearch();
    // initNotificationsSystem();
    initTooltips();
    initProgressBars();
    initRippleEffect();
    initAnimatedCounters();
    initParallaxEffects();
    initQuickActions();
    initInteractiveAlerts();
    
    // Aplicar animações
    animateElements();
    startAutoAnimations();
    
    // Monitor contínuo para ícones das ações rápidas
    startIconMonitor();
}

/**
 * Monitor contínuo para prevenir desaparecimento de ícones
 */
function startIconMonitor() {
    // Verificar ícones periodicamente
    setInterval(ensureIconsVisible, 1000);
    
    // Verificar ícones ao retornar para a página
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            setTimeout(ensureIconsVisible, 100);
        }
    });
    
    // Verificar ícones após mudanças no DOM
    const observer = new MutationObserver(function(mutations) {
        let shouldCheck = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' || mutation.type === 'attributes') {
                shouldCheck = true;
            }
        });
        
        if (shouldCheck) {
            setTimeout(ensureIconsVisible, 50);
        }
    });
    
    // Observar mudanças no container das ações rápidas
    const quickActionsContainer = document.querySelector('.quick-actions');
    if (quickActionsContainer) {
        observer.observe(quickActionsContainer, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class', 'style']
        });
    }
}

/**
 * Loading Screen
 */
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        setTimeout(() => {
            loadingScreen.classList.add('hidden');
            setTimeout(() => {
                loadingScreen.remove();
            }, 300);
        }, 500);
    }
}

/**
 * Sidebar Toggle
 */
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            if (mainContent) {
                mainContent.classList.toggle('sidebar-collapsed');
            }
            
            // Salvar estado no localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
        
        // Restaurar estado do sidebar
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (sidebarCollapsed) {
            sidebar.classList.add('collapsed');
            if (mainContent) {
                mainContent.classList.add('sidebar-collapsed');
            }
        }
    }
    
    // Responsive sidebar para mobile
    if (window.innerWidth <= 768) {
        if (sidebar) {
            sidebar.classList.add('collapsed');
        }
        if (mainContent) {
            mainContent.classList.add('sidebar-collapsed');
        }
    }
}

/**
 * Modals
 */
function initModals() {
    // Fechar modal ao clicar no overlay
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target);
        }
    });
    
    // Fechar modal com botão close
    document.querySelectorAll('.modal-close').forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            closeModal(modal);
        });
    });
    
    // Fechar modal com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                closeModal(openModal);
            }
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // Focus no primeiro input do modal
        const firstInput = modal.querySelector('input, textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
}

function closeModal(modal) {
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

/**
 * Alerts
 */
function initAlerts() {
    document.querySelectorAll('.alert-close').forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.animation = 'slideUp 0.3s ease-out reverse';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        });
    });
    
    // Auto-dismiss alerts após 5 segundos
    document.querySelectorAll('.alert').forEach(alert => {
        if (!alert.hasAttribute('data-no-auto-dismiss')) {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.style.animation = 'slideUp 0.3s ease-out reverse';
                    setTimeout(() => {
                        alert.remove();
                    }, 300);
                }
            }, 5000);
        }
    });
}

/**
 * Search Box
 */
function initSearch() {
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 300);
            }
        });
    }
}

function performSearch(query) {
    // Implementar busca de medicamentos
    console.log('Buscando:', query);
    // Aqui você pode fazer uma requisição AJAX para buscar medicamentos
}

/**
 * Notificações
 */
function initNotifications() {
    const notificationBtn = document.querySelector('.notification-btn');
    if (notificationBtn) {
        // Verificar novas notificações periodicamente
        checkNotifications();
        setInterval(checkNotifications, 30000); // A cada 30 segundos
    }
}

function checkNotifications() {
    // Aqui você pode fazer uma requisição AJAX para verificar novas notificações
    console.log('Verificando notificações...');
}

/**
 * Tooltips
 */
function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const text = e.target.getAttribute('data-tooltip');
    if (!text) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        z-index: 1000;
        pointer-events: none;
        white-space: nowrap;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + 'px';
    tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
    
    e.target._tooltip = tooltip;
}

function hideTooltip(e) {
    if (e.target._tooltip) {
        e.target._tooltip.remove();
        delete e.target._tooltip;
    }
}

/**
 * Animações
 */
function animateElements() {
    // Animar elementos quando entram na viewport
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    document.querySelectorAll('.card, .table-responsive').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Formulários
 */
function initForms() {
    // Validação em tempo real
    document.querySelectorAll('input, textarea, select').forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });
        
        field.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    const required = field.hasAttribute('required');
    const type = field.getAttribute('type');
    
    let isValid = true;
    let message = '';
    
    if (required && !value) {
        isValid = false;
        message = 'Este campo é obrigatório';
    } else if (type === 'email' && value && !isValidEmail(value)) {
        isValid = false;
        message = 'Digite um e-mail válido';
    } else if (type === 'number' && value && isNaN(value)) {
        isValid = false;
        message = 'Digite um número válido';
    }
    
    if (isValid) {
        field.classList.remove('is-invalid');
        const feedback = field.parentNode.querySelector('.invalid-feedback');
        if (feedback) feedback.remove();
    } else {
        field.classList.add('is-invalid');
        showFieldError(field, message);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
    if (existingFeedback) {
        existingFeedback.textContent = message;
    } else {
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        field.parentNode.appendChild(feedback);
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Utilitários
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible slide-up`;
    notification.innerHTML = `
        <button class="alert-close">&times;</button>
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        ${message}
    `;
    
    const container = document.querySelector('.messages') || document.querySelector('.content');
    if (container) {
        container.insertBefore(notification, container.firstChild);
        
        // Auto-dismiss
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideUp 0.3s ease-out reverse';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
        
        // Botão de fechar
        notification.querySelector('.alert-close').addEventListener('click', function() {
            notification.style.animation = 'slideUp 0.3s ease-out reverse';
            setTimeout(() => notification.remove(), 300);
        });
    }
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
}

/**
 * AJAX Helper
 */
function fetchAPI(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    };
    
    return fetch(url, { ...defaultOptions, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Erro na requisição:', error);
            showNotification('Erro na comunicação com o servidor', 'error');
            throw error;
        });
}

function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

/**
 * Progress Bars Animadas
 */
function initProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressFill = entry.target.querySelector('.progress-fill');
                const targetWidth = progressFill.getAttribute('data-width') || '100%';
                
                setTimeout(() => {
                    progressFill.style.width = targetWidth;
                }, 200);
                
                observer.unobserve(entry.target);
            }
        });
    });
    
    progressBars.forEach(bar => observer.observe(bar));
}

/**
 * Efeito Ripple nos Botões
 */
function initRippleEffect() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('ripple')) {
            createRipple(e);
        }
    });
}

function createRipple(event) {
    const button = event.currentTarget;
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
    circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
    circle.classList.add('ripple-effect');
    
    const ripple = button.getElementsByClassName('ripple-effect')[0];
    if (ripple) {
        ripple.remove();
    }
    
    button.appendChild(circle);
}

/**
 * Contadores Animados
 */
function initAnimatedCounters() {
    const counters = document.querySelectorAll('[data-count]');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    });
    
    counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-count'));
    const duration = parseInt(element.getAttribute('data-duration') || '2000');
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (ease-out-cubic)
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        
        const currentValue = Math.floor(easeProgress * target);
        element.textContent = currentValue.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target.toLocaleString();
        }
    }
    
    requestAnimationFrame(updateCounter);
}

/**
 * Efeitos de Parallax
 */
function initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    
    if (parallaxElements.length === 0) return;
    
    function updateParallax() {
        const scrolled = window.pageYOffset;
        
        parallaxElements.forEach(element => {
            const rate = scrolled * (parseFloat(element.getAttribute('data-parallax')) || 0.5);
            element.style.transform = `translateY(${rate}px)`;
        });
    }
    
    window.addEventListener('scroll', updateParallax);
}

/**
 * Auto Animações
 */
function startAutoAnimations() {
    // Floating pills animation
    animateFloatingPills();
    
    // Pulse effect nos alertas críticos
    const criticalAlerts = document.querySelectorAll('.alert.danger, .notification-item.danger');
    criticalAlerts.forEach(alert => {
        alert.classList.add('pulse');
    });
    
    // Shimmer effect nos loading skeletons
    const skeletons = document.querySelectorAll('.loading-skeleton');
    skeletons.forEach(skeleton => {
        skeleton.style.backgroundImage = 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)';
        skeleton.style.backgroundSize = '200% 100%';
        skeleton.style.animation = 'loading 1.5s infinite';
    });
}

function animateFloatingPills() {
    const pills = document.querySelectorAll('.floating-pills i');
    
    pills.forEach((pill, index) => {
        const duration = 6 + (index * 2); // Diferentes durações
        const delay = index * 0.5; // Delays escalonados
        
        pill.style.animation = `float ${duration}s ease-in-out infinite ${delay}s`;
    });
}

/**
 * Intersection Observer para animações
 */
function animateElements() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                
                // Diferentes tipos de animação baseados em classes
                if (element.classList.contains('slide-up-on-scroll')) {
                    element.classList.add('slide-up');
                } else if (element.classList.contains('fade-in-on-scroll')) {
                    element.classList.add('fade-in');
                } else if (element.classList.contains('zoom-in-on-scroll')) {
                    element.classList.add('zoom-in');
                } else if (element.classList.contains('bounce-in-on-scroll')) {
                    element.classList.add('bounce-in');
                } else {
                    // Animação padrão
                    element.classList.add('fade-in');
                }
                
                observer.unobserve(element);
            }
        });
    }, observerOptions);
    
    // Observar elementos que devem animar
    document.querySelectorAll('.card, .stat-card, .table-responsive, .alert').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Smooth Scroll
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Lazy Loading para Imagens
 */
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

/**
 * Filtros e Busca Avançada
 */
function initAdvancedSearch() {
    const searchInputs = document.querySelectorAll('[data-search-target]');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const target = this.getAttribute('data-search-target');
            const filter = this.value.toLowerCase();
            const items = document.querySelectorAll(target);
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                const shouldShow = text.includes(filter);
                
                item.style.display = shouldShow ? '' : 'none';
                
                // Animação suave
                if (shouldShow) {
                    item.classList.add('fade-in');
                }
            });
        });
    });
}

/**
 * Theme Switcher (Dark/Light Mode)
 */
function initThemeSwitcher() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    themeToggle.addEventListener('click', function() {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Animação de transição
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    });
}

/**
 * Responsive handlers
 */
window.addEventListener('resize', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (window.innerWidth <= 768) {
        if (sidebar && !sidebar.classList.contains('collapsed')) {
            sidebar.classList.add('collapsed');
        }
        if (mainContent && !mainContent.classList.contains('sidebar-collapsed')) {
            mainContent.classList.add('sidebar-collapsed');
        }
    }
});

/**
 * Performance Monitoring
 */
function initPerformanceMonitoring() {
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = performance.timing;
                const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
                
                console.log(`Page Load Time: ${pageLoadTime}ms`);
                
                // Enviar dados para analytics se necessário
                if (pageLoadTime > 3000) {
                    console.warn('Page load time is slow');
                }
            }, 0);
        });
    }
}

/**
 * ===================================
 * AÇÕES RÁPIDAS - SISTEMA REFATORADO
 * ===================================
 */

/**
 * Correção crítica: Garantir que ícones nunca desapareçam
 */
function ensureIconsVisible() {
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    
    quickActionBtns.forEach((btn, index) => {
        const icon = btn.querySelector('i');
        const btnText = btn.querySelector('span')?.textContent || 'Unknown';
        
        if (icon) {
            // Verificar se ícone está oculto
            const computedStyle = window.getComputedStyle(icon);
            const isHidden = computedStyle.display === 'none' || 
                           computedStyle.visibility === 'hidden' || 
                           computedStyle.opacity === '0';
            
            if (isHidden) {
                console.warn(`🔧 CORREÇÃO: Ícone oculto detectado em "${btnText}" - restaurando visibilidade`);
            }
            
            // Forçar propriedades CSS para manter ícone visível
            icon.style.display = 'inline-block';
            icon.style.visibility = 'visible';
            icon.style.opacity = '1';
            icon.style.fontFamily = '"Font Awesome 6 Free"';
            icon.style.fontWeight = '900';
            icon.style.fontSize = '1.75rem';
            
            // Garantir que classes Font Awesome estejam presentes
            if (!icon.classList.contains('fas') && !icon.classList.contains('far')) {
                icon.classList.add('fas');
                console.log(`🔧 DEBUG: Classe 'fas' adicionada ao ícone de "${btnText}"`);
            }
            
            // Verificar se o ícone tem conteúdo (::before)
            const iconClasses = Array.from(icon.classList);
            const hasIconClass = iconClasses.some(cls => cls.startsWith('fa-'));
            
            if (!hasIconClass) {
                console.warn(`🚨 ALERTA: Ícone de "${btnText}" sem classe de ícone específica!`);
            }
        } else {
            console.error(`❌ ERRO: Ícone não encontrado no botão "${btnText}"`);
        }
    });
}

/**
 * Inicializar sistema de ações rápidas
 */
function initQuickActions() {
    // Garantir ícones visíveis imediatamente
    ensureIconsVisible();
    
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    const dropdowns = document.querySelectorAll('.quick-action-dropdown');
    
    // Debounce para prevenir múltiplos cliques
    const debounce = (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
    
    // Handler para cliques em ações rápidas
    const handleQuickActionClick = debounce((event) => {
        const btn = event.currentTarget;
        
        // Prevenir comportamento padrão se necessário
        if (btn.tagName === 'BUTTON') {
            event.preventDefault();
        }
        
        // Verificar se está desabilitado ou carregando
        if (btn.classList.contains('disabled') || btn.classList.contains('loading')) {
            event.preventDefault();
            return false;
        }
        
        // Adicionar efeito visual de clique
        addClickEffect(btn);
        
        // Adicionar ripple effect
        createRippleEffect(event);
        
        // Se for um link, adicionar estado de loading
        if (btn.tagName === 'A' && btn.href) {
            addLoadingState(btn);
            
            // Remover loading após navegação (fallback)
            setTimeout(() => {
                removeLoadingState(btn);
            }, 3000);
        }
        
        // Log para debugging
        console.log('Quick action clicked:', btn.querySelector('span')?.textContent || 'Unknown');
        
    }, 300); // Debounce de 300ms
    
    // Adicionar event listeners
    quickActionBtns.forEach(btn => {
        // Remover listeners existentes para evitar duplicação
        btn.removeEventListener('click', handleQuickActionClick);
        btn.addEventListener('click', handleQuickActionClick);
        
        // Adicionar suporte a teclado
        btn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleQuickActionClick(e);
            }
        });
        
        // Adicionar atributos de acessibilidade
        if (!btn.getAttribute('role')) {
            btn.setAttribute('role', 'button');
        }
        if (!btn.getAttribute('tabindex')) {
            btn.setAttribute('tabindex', '0');
        }
    });
    
    // Gerenciar dropdowns
    dropdowns.forEach(dropdown => {
        const btn = dropdown.querySelector('.quick-action-btn');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (btn && menu) {
            // Toggle dropdown no clique
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                // Fechar outros dropdowns
                dropdowns.forEach(other => {
                    if (other !== dropdown) {
                        other.classList.remove('active');
                    }
                });
                
                // Toggle atual
                dropdown.classList.toggle('active');
            });
            
            // Fechar dropdown ao clicar fora
            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target)) {
                    dropdown.classList.remove('active');
                }
            });
            
            // Fechar dropdown com ESC
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    dropdown.classList.remove('active');
                }
            });
        }
    });
}

/**
 * Criar efeito ripple
 */
function createRippleEffect(event) {
    const btn = event.currentTarget;
    
    // Verificar se o elemento suporta ripple
    if (!btn.classList.contains('ripple')) {
        return;
    }
    
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    // Remover ripples existentes
    const existingRipples = btn.querySelectorAll('.ripple-effect');
    existingRipples.forEach(ripple => ripple.remove());
    
    // Criar novo ripple
    const ripple = document.createElement('span');
    ripple.classList.add('ripple-effect');
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    
    btn.appendChild(ripple);
    
    // Remover ripple após animação
    setTimeout(() => {
        if (ripple.parentNode) {
            ripple.remove();
        }
    }, 600);
}

/**
 * Adicionar efeito visual de clique
 */
function addClickEffect(btn) {
    btn.classList.add('clicking');
    
    setTimeout(() => {
        btn.classList.remove('clicking');
    }, 150);
}

/**
 * Adicionar estado de loading
 */
function addLoadingState(btn) {
    if (btn.classList.contains('loading')) {
        return;
    }
    
    btn.classList.add('loading');
    btn.setAttribute('aria-busy', 'true');
    
    // Salvar texto original
    const originalText = btn.querySelector('span')?.textContent;
    if (originalText) {
        btn.setAttribute('data-original-text', originalText);
        const span = btn.querySelector('span');
        if (span) {
            span.textContent = 'Carregando...';
        }
    }
}

/**
 * Remover estado de loading
 */
function removeLoadingState(btn) {
    btn.classList.remove('loading');
    btn.removeAttribute('aria-busy');
    
    // Restaurar texto original
    const originalText = btn.getAttribute('data-original-text');
    if (originalText) {
        const span = btn.querySelector('span');
        if (span) {
            span.textContent = originalText;
        }
        btn.removeAttribute('data-original-text');
    }
}

/**
 * ===================================
 * ALERTAS INTERATIVOS - SISTEMA REFATORADO
 * ===================================
 */

/**
 * Inicializar alertas interativos
 */
function initInteractiveAlerts() {
    const clickableAlerts = document.querySelectorAll('.clickable-alert');
    
    // Debounce para alertas
    const debounce = (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
    
    const handleAlertClick = debounce((event) => {
        const alert = event.currentTarget;
        const actionUrl = alert.getAttribute('data-action-url');
        
        if (!actionUrl) {
            console.warn('Alert sem URL de ação:', alert);
            return;
        }
        
        // Adicionar efeito visual
        alert.classList.add('clicking');
        
        // Adicionar estado de loading
        alert.classList.add('loading');
        
        // Navegar após pequeno delay para mostrar feedback visual
        setTimeout(() => {
            window.location.href = actionUrl;
        }, 200);
        
        // Fallback para remover estados após timeout
        setTimeout(() => {
            alert.classList.remove('clicking', 'loading');
        }, 3000);
        
    }, 250);
    
    clickableAlerts.forEach(alert => {
        // Remover listeners existentes
        alert.removeEventListener('click', handleAlertClick);
        alert.addEventListener('click', handleAlertClick);
        
        // Adicionar suporte a teclado
        alert.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleAlertClick(e);
            }
        });
        
        // Adicionar atributos de acessibilidade
        alert.setAttribute('role', 'button');
        alert.setAttribute('tabindex', '0');
        
        // Melhorar tooltip
        const actionText = alert.querySelector('.alert-action')?.textContent;
        if (actionText && !alert.getAttribute('title')) {
            alert.setAttribute('title', actionText);
        }
    });
}

/**
 * ===================================
 * UTILITÁRIOS GERAIS
 * ===================================
 */

/**
 * Função para desabilitar temporariamente um botão
 */
function disableButton(btn, duration = 1000) {
    btn.classList.add('disabled');
    btn.setAttribute('disabled', 'true');
    
    setTimeout(() => {
        btn.classList.remove('disabled');
        btn.removeAttribute('disabled');
    }, duration);
}

/**
 * Função para mostrar feedback visual de sucesso
 */
function showSuccessFeedback(element, message = 'Sucesso!') {
    const feedback = document.createElement('div');
    feedback.className = 'success-feedback';
    feedback.textContent = message;
    feedback.style.cssText = `
        position: absolute;
        top: -30px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--success-color);
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 1000;
        animation: fadeInOut 2s ease-in-out;
    `;
    
    element.style.position = 'relative';
    element.appendChild(feedback);
    
    setTimeout(() => {
        if (feedback.parentNode) {
            feedback.remove();
        }
    }, 2000);
}

// Adicionar CSS para animação de feedback
if (!document.querySelector('#success-feedback-styles')) {
    const style = document.createElement('style');
    style.id = 'success-feedback-styles';
    style.textContent = `
        @keyframes fadeInOut {
            0%, 100% { opacity: 0; transform: translateX(-50%) translateY(-10px); }
            20%, 80% { opacity: 1; transform: translateX(-50%) translateY(0); }
        }
    `;
    document.head.appendChild(style);
}

// Exportar funções para uso global
window.PharmacySystem = {
    openModal,
    closeModal,
    showNotification,
    formatCurrency,
    formatDate,
    fetchAPI,
    getCsrfToken,
    // Novas funções
    addLoadingState,
    removeLoadingState,
    disableButton,
    showSuccessFeedback,
    createRippleEffect
};
