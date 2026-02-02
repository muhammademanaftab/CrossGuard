/**
 * Vanilla JS Dashboard Application
 * Real-world patterns for a data dashboard
 *
 * Expected features: const, let, arrow-functions, async-functions, promises,
 * fetch, queryselector, classlist, dataset, addeventlistener,
 * intersectionobserver, mutationobserver, namevalue-storage, json,
 * template-literals, es6, history, matchmedia, getcomputedstyle,
 * requestanimationframe, domcontentloaded
 */

'use strict';

// Configuration
const CONFIG = {
    apiBase: '/api/v1',
    refreshInterval: 30000,
    chartColors: ['#3b82f6', '#ef4444', '#22c55e', '#f59e0b']
};

// Dashboard class
class Dashboard {
    constructor(container) {
        this.container = document.querySelector(container);
        this.widgets = new Map();
        this.observers = new Set();
        this.init();
    }

    async init() {
        await this.loadUserPreferences();
        this.setupEventListeners();
        this.setupObservers();
        this.loadWidgets();
    }

    // Load preferences from localStorage
    async loadUserPreferences() {
        const saved = localStorage.getItem('dashboard-prefs');
        if (saved) {
            this.preferences = JSON.parse(saved);
        } else {
            this.preferences = { layout: 'grid', theme: 'auto' };
        }

        // Apply theme based on system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        this.applyTheme(prefersDark.matches ? 'dark' : 'light');

        prefersDark.addEventListener('change', (e) => {
            if (this.preferences.theme === 'auto') {
                this.applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    applyTheme(theme) {
        document.body.classList.remove('theme-light', 'theme-dark');
        document.body.classList.add(`theme-${theme}`);
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('[data-navigate]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const path = e.target.dataset.navigate;
                history.pushState({ path }, '', path);
                this.navigate(path);
            });
        });

        // Handle back/forward
        window.addEventListener('popstate', (event) => {
            if (event.state?.path) {
                this.navigate(event.state.path);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'r' && e.ctrlKey) {
                e.preventDefault();
                this.refreshAll();
            }
        });

        // Filter input
        const filterInput = document.querySelector('#widget-filter');
        if (filterInput) {
            filterInput.addEventListener('input', (e) => {
                this.filterWidgets(e.target.value);
            });
        }
    }

    setupObservers() {
        // Lazy load widgets when visible
        const intersectionObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const widgetId = entry.target.dataset.widgetId;
                        this.loadWidgetData(widgetId);
                        intersectionObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.1 }
        );

        // Watch for DOM changes
        const mutationObserver = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(node => {
                        if (node.classList?.contains('widget')) {
                            intersectionObserver.observe(node);
                        }
                    });
                }
            });
        });

        mutationObserver.observe(this.container, { childList: true, subtree: true });
        this.observers.add(intersectionObserver);
        this.observers.add(mutationObserver);
    }

    async loadWidgets() {
        try {
            const response = await fetch(`${CONFIG.apiBase}/widgets`);
            const widgets = await response.json();

            widgets.forEach(widget => {
                this.renderWidget(widget);
                this.widgets.set(widget.id, widget);
            });
        } catch (error) {
            console.error('Failed to load widgets:', error);
            this.showError('Could not load dashboard widgets');
        }
    }

    renderWidget(widget) {
        const element = document.createElement('div');
        element.className = 'widget';
        element.dataset.widgetId = widget.id;
        element.innerHTML = `
            <header class="widget-header">
                <h3>${widget.title}</h3>
                <button class="refresh-btn" data-action="refresh">↻</button>
            </header>
            <div class="widget-content">
                <div class="loading-spinner"></div>
            </div>
        `;

        element.querySelector('[data-action="refresh"]').addEventListener('click', () => {
            this.loadWidgetData(widget.id);
        });

        this.container.append(element);
    }

    async loadWidgetData(widgetId) {
        const widget = this.widgets.get(widgetId);
        const element = document.querySelector(`[data-widget-id="${widgetId}"]`);

        if (!widget || !element) return;

        element.classList.add('loading');

        try {
            const response = await fetch(`${CONFIG.apiBase}/widgets/${widgetId}/data`);
            const data = await response.json();

            const content = element.querySelector('.widget-content');
            content.innerHTML = this.formatWidgetData(widget.type, data);

            // Animate the update
            requestAnimationFrame(() => {
                element.classList.remove('loading');
                element.classList.add('updated');
                setTimeout(() => element.classList.remove('updated'), 300);
            });
        } catch (error) {
            console.error(`Failed to load widget ${widgetId}:`, error);
        }
    }

    formatWidgetData(type, data) {
        switch (type) {
            case 'chart':
                return `<canvas class="chart" data-values="${data.values.join(',')}"></canvas>`;
            case 'stats':
                return data.items.map(item => `
                    <div class="stat-item">
                        <span class="stat-label">${item.label}</span>
                        <span class="stat-value">${item.value}</span>
                    </div>
                `).join('');
            default:
                return `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        }
    }

    filterWidgets(query) {
        const lowerQuery = query.toLowerCase();
        this.widgets.forEach((widget, id) => {
            const element = document.querySelector(`[data-widget-id="${id}"]`);
            const matches = widget.title.toLowerCase().includes(lowerQuery);
            element.style.display = matches ? 'block' : 'none';
        });
    }

    navigate(path) {
        // Update active nav state
        document.querySelectorAll('[data-navigate]').forEach(link => {
            const isActive = link.dataset.navigate === path;
            link.classList.toggle('active', isActive);
        });
    }

    async refreshAll() {
        for (const [id] of this.widgets) {
            await this.loadWidgetData(id);
        }
    }

    showError(message) {
        const toast = document.createElement('div');
        toast.className = 'toast error';
        toast.textContent = message;
        document.body.append(toast);
        setTimeout(() => toast.remove(), 5000);
    }

    destroy() {
        this.observers.forEach(observer => observer.disconnect());
        this.widgets.clear();
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard('#dashboard-container');
});
