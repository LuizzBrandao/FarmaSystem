/**
 * Modern Dashboard JavaScript
 * Funcionalidades e animações para o dashboard modernizado
 */

// Utilitários
(function() {
    if (window.DashboardModerno && window.DashboardModerno.__initialized) {
        return;
    }

    const mdUtils = {
    // Debounce para otimizar eventos
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Animação de números (counter)
    animateCounter: (element, target, duration = 1500) => {
        let start = 0;
        const increment = target / (duration / 16);
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                start = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(start);
        }, 16);
    },

    // Formatação de números
    formatNumber: (num) => {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }
};

// Gerenciador de Animações
const AnimationManager = {
    // Intersection Observer para animações on-scroll
    createScrollObserver: () => {
        return new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    
                    // Animar contadores
                    if (entry.target.hasAttribute('data-count')) {
                        const target = parseInt(entry.target.getAttribute('data-count'));
                        const duration = parseInt(entry.target.getAttribute('data-duration')) || 1500;
                        mdUtils.animateCounter(entry.target, target, duration);
                    }
                }
            });
        }, { 
            threshold: 0.3,
            rootMargin: '50px'
        });
    },

    // Configurar animações de fade-in
    setupFadeInAnimations: () => {
        const observer = AnimationManager.createScrollObserver();
        
        // Elementos com animação fade-in
        document.querySelectorAll('.animate-fade-in-up, .metric-card, .content-card').forEach(el => {
            observer.observe(el);
        });

        // Contadores
        document.querySelectorAll('[data-count]').forEach(counter => {
            observer.observe(counter);
        });
    },

    // Efeitos de hover para cards
    setupHoverEffects: () => {
        const cards = document.querySelectorAll('.metric-card, .branch-card, .content-card');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-4px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    },

    // Animações de loading (skeleton)
    showSkeleton: (container) => {
        container.innerHTML = `
            <div class="skeleton" style="height: 20px; margin-bottom: 10px;"></div>
            <div class="skeleton" style="height: 20px; width: 70%; margin-bottom: 10px;"></div>
            <div class="skeleton" style="height: 20px; width: 50%;"></div>
        `;
    }
};

// Gerenciador de Pesquisa e Filtros
const SearchManager = {
    // Configurar busca em tempo real
    setupSearch: () => {
        const searchInputs = document.querySelectorAll('input[data-search-target]');
        
        searchInputs.forEach(input => {
            const target = input.getAttribute('data-search-target');
            const searchFunction = mdUtils.debounce((query) => {
                SearchManager.filterElements(target, query);
            }, 300);
            
            input.addEventListener('input', (e) => {
                searchFunction(e.target.value);
            });
        });
    },

    // Filtrar elementos
    filterElements: (selector, query) => {
        const elements = document.querySelectorAll(selector);
        const searchTerm = query.toLowerCase();
        
        elements.forEach(element => {
            const text = element.textContent.toLowerCase();
            const isVisible = text.includes(searchTerm);
            
            element.style.display = isVisible ? 'block' : 'none';
            
            // Adicionar classe para animação
            if (isVisible) {
                element.classList.add('search-match');
            } else {
                element.classList.remove('search-match');
            }
        });

        // Mostrar mensagem se nenhum resultado
        SearchManager.toggleNoResults(selector, query);
    },

    // Mostrar/ocultar mensagem de "nenhum resultado"
    toggleNoResults: (selector, query) => {
        const container = document.querySelector(selector)?.parentElement;
        if (!container) return;

        const visibleItems = container.querySelectorAll(`${selector}:not([style*="display: none"])`);
        let noResultsMsg = container.querySelector('.no-results-message');

        if (visibleItems.length === 0 && query.trim() !== '') {
            if (!noResultsMsg) {
                noResultsMsg = document.createElement('div');
                noResultsMsg.className = 'no-results-message empty-state';
                noResultsMsg.innerHTML = `
                    <div class="empty-state-icon">
                        <i class="fas fa-search"></i>
                    </div>
                    <h4>Nenhum resultado encontrado</h4>
                    <p>Tente ajustar sua pesquisa ou limpar os filtros.</p>
                `;
                container.appendChild(noResultsMsg);
            }
            noResultsMsg.style.display = 'block';
        } else if (noResultsMsg) {
            noResultsMsg.style.display = 'none';
        }
    }
};

// Gerenciador de Notificações Toast
const ToastManager = {
    container: null,

    // Inicializar container de toasts
    init: () => {
        if (!ToastManager.container) {
            ToastManager.container = document.createElement('div');
            ToastManager.container.className = 'toast-container';
            ToastManager.container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
            `;
            document.body.appendChild(ToastManager.container);
        }
    },

    // Mostrar toast
    show: (message, type = 'info', duration = 4000) => {
        ToastManager.init();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            background: white;
            border-radius: var(--radius-md);
            padding: var(--space-4);
            box-shadow: var(--shadow-lg);
            border-left: 4px solid var(--primary-${type === 'success' ? 'green' : type === 'error' ? 'red' : 'blue'});
            min-width: 300px;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;

        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-circle' : 
                    type === 'warning' ? 'exclamation-triangle' : 'info-circle';

        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: var(--space-2);">
                <i class="fas fa-${icon}" style="color: var(--primary-${type === 'success' ? 'green' : type === 'error' ? 'red' : 'blue'});"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="margin-left: auto; background: none; border: none; color: var(--neutral-400); cursor: pointer;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        ToastManager.container.appendChild(toast);

        // Animar entrada
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 10);

        // Auto-remover
        if (duration > 0) {
            setTimeout(() => {
                toast.style.transform = 'translateX(100%)';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
    }
};

// Gerenciador de Estado da Aplicação
const AppStateManager = {
    // Dados em cache
    cache: new Map(),

    // Salvar no localStorage
    saveToStorage: (key, data) => {
        try {
            localStorage.setItem(`dashboard_${key}`, JSON.stringify(data));
        } catch (e) {
            console.warn('Não foi possível salvar no localStorage:', e);
        }
    },

    // Carregar do localStorage
    loadFromStorage: (key) => {
        try {
            const data = localStorage.getItem(`dashboard_${key}`);
            return data ? JSON.parse(data) : null;
        } catch (e) {
            console.warn('Não foi possível carregar do localStorage:', e);
            return null;
        }
    },

    // Atualizar métricas em tempo real
    updateMetrics: async () => {
        try {
            // Simular chamada AJAX para atualizar métricas
            // Em produção, fazer fetch('/api/dashboard/metrics/')
            
            const metrics = {
                branches: Math.floor(Math.random() * 10) + 3,
                medications: Math.floor(Math.random() * 50) + 20,
                alerts: Math.floor(Math.random() * 5),
                transfers: Math.floor(Math.random() * 8)
            };

            // Atualizar UI
            Object.entries(metrics).forEach(([key, value]) => {
                const element = document.querySelector(`.metric-card.${key} .metric-value`);
                if (element) {
                    mdUtils.animateCounter(element, value, 1000);
                }
            });

            AppStateManager.saveToStorage('last_metrics', {
                data: metrics,
                timestamp: Date.now()
            });

        } catch (error) {
            console.error('Erro ao atualizar métricas:', error);
            ToastManager.show('Erro ao atualizar dados', 'error');
        }
    }
};

// Gerenciador de Temas
const ThemeManager = {
    // Alternar tema escuro/claro
    toggleTheme: () => {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        AppStateManager.saveToStorage('theme', isDark ? 'dark' : 'light');
        
        ToastManager.show(
            `Tema ${isDark ? 'escuro' : 'claro'} ativado`, 
            'success', 
            2000
        );
    },

    // Aplicar tema salvo
    applyStoredTheme: () => {
        const savedTheme = AppStateManager.loadFromStorage('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
        }
    }
};

// Inicialização do Dashboard
const DashboardInit = {
    // Configurar tudo
    init: () => {
        console.log('🚀 Inicializando Dashboard Moderno...');

        // Aguardar DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', DashboardInit.setup);
        } else {
            DashboardInit.setup();
        }
    },

    // Configurar funcionalidades
    setup: () => {
        // Aplicar tema salvo
        ThemeManager.applyStoredTheme();

        // Configurar animações
        AnimationManager.setupFadeInAnimations();
        AnimationManager.setupHoverEffects();

        // Configurar pesquisa
        SearchManager.setupSearch();

        // Inicializar toasts
        ToastManager.init();

        // Atualizar métricas periodicamente (5 minutos)
        setInterval(AppStateManager.updateMetrics, 5 * 60 * 1000);

        // Configurar keyboard shortcuts
        DashboardInit.setupKeyboardShortcuts();

        // Feedback de carregamento concluído
        setTimeout(() => {
            ToastManager.show('Dashboard carregado com sucesso!', 'success', 3000);
        }, 1000);

        console.log('✅ Dashboard Moderno inicializado!');
    },

    // Atalhos de teclado
    setupKeyboardShortcuts: () => {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K para pesquisa
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('input[data-search-target]');
                if (searchInput) {
                    searchInput.focus();
                    ToastManager.show('Digite para pesquisar...', 'info', 2000);
                }
            }

            // Ctrl/Cmd + D para toggle theme
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                ThemeManager.toggleTheme();
            }

            // Escape para limpar pesquisa
            if (e.key === 'Escape') {
                const searchInput = document.querySelector('input[data-search-target]:focus');
                if (searchInput) {
                    searchInput.value = '';
                    searchInput.dispatchEvent(new Event('input'));
                }
            }
        });
    }
};

// Auto-inicializar
DashboardInit.init();

// Exportar para uso global
window.DashboardModerno = {
    utils: mdUtils,
    AnimationManager,
    SearchManager,
    ToastManager,
    AppStateManager,
    ThemeManager,
    init: DashboardInit.init,
    animateCounter: mdUtils.animateCounter,
    __initialized: true
};
})();

// Compatibilidade: se o objeto global já existir sem init (por cache/versão antiga), definir um init seguro
if (window.DashboardModerno && typeof window.DashboardModerno.init !== 'function') {
    window.DashboardModerno.init = function() {
        try {
            // Executa apenas se os managers estiverem disponíveis
            if (window.DashboardModerno.ThemeManager && window.DashboardModerno.ThemeManager.applyStoredTheme) {
                window.DashboardModerno.ThemeManager.applyStoredTheme();
            }
            if (window.DashboardModerno.AnimationManager) {
                if (window.DashboardModerno.AnimationManager.setupFadeInAnimations) {
                    window.DashboardModerno.AnimationManager.setupFadeInAnimations();
                }
                if (window.DashboardModerno.AnimationManager.setupHoverEffects) {
                    window.DashboardModerno.AnimationManager.setupHoverEffects();
                }
            }
            if (window.DashboardModerno.SearchManager && window.DashboardModerno.SearchManager.setupSearch) {
                window.DashboardModerno.SearchManager.setupSearch();
            }
            if (window.DashboardModerno.ToastManager && window.DashboardModerno.ToastManager.init) {
                window.DashboardModerno.ToastManager.init();
            }
            if (window.DashboardModerno.AppStateManager && window.DashboardModerno.AppStateManager.updateMetrics) {
                setInterval(window.DashboardModerno.AppStateManager.updateMetrics, 5 * 60 * 1000);
            }
            // No-op fallback concluído
            console.log('DashboardModerno.init (fallback) executado');
        } catch (e) {
            console.warn('Fallback init falhou:', e);
        }
    };
}
