/**
 * Real-World Test: Single Page Application
 * Simulates a SPA with no custom JS rules (current custom_rules.json has empty JS)
 *
 * Purpose: Verify that the custom rules system doesn't interfere with
 * built-in JS feature detection in a real-world codebase.
 *
 * Expected custom features: NONE
 * Expected built-in features: const, let, arrow-functions, async-functions,
 *   template-literals, es6, promises, fetch, abortcontroller,
 *   namevalue-storage, json, queryselector, classlist, history,
 *   intersectionobserver, matchmedia, es6-class, use-strict
 */

"use strict";

class Router {
    constructor() {
        this.routes = new Map();
        this.currentRoute = null;
    }

    addRoute(path, handler) {
        this.routes.set(path, handler);
    }

    navigate(path) {
        history.pushState({ path }, '', path);
        this._handleRoute(path);
    }

    _handleRoute(path) {
        const handler = this.routes.get(path);
        if (handler) {
            handler();
        }
    }

    init() {
        window.addEventListener('popstate', (event) => {
            if (event.state) {
                this._handleRoute(event.state.path);
            }
        });
    }
}

class App {
    constructor() {
        this.router = new Router();
        this.state = {};
        this.observers = [];
    }

    async init() {
        // Setup theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.classList.add(`theme-${savedTheme}`);

        // Setup responsive behavior
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
            const theme = e.matches ? 'dark' : 'light';
            document.body.classList.remove('theme-light', 'theme-dark');
            document.body.classList.add(`theme-${theme}`);
            localStorage.setItem('theme', theme);
        });

        // Lazy load sections
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this._loadSection(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('[data-lazy]').forEach(section => {
            observer.observe(section);
        });

        // Load initial data
        await this._fetchInitialData();

        // Setup routes
        this.router.addRoute('/', () => this._renderHome());
        this.router.addRoute('/about', () => this._renderAbout());
        this.router.init();
    }

    async _fetchInitialData() {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 5000);

        try {
            const response = await fetch('/api/init', {
                signal: controller.signal,
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.state = { ...this.state, ...data };

            // Cache in sessionStorage
            sessionStorage.setItem('appState', JSON.stringify(this.state));
        } catch (error) {
            console.error(`Failed to load: ${error.message}`);

            // Try cached data
            const cached = sessionStorage.getItem('appState');
            if (cached) {
                this.state = JSON.parse(cached);
            }
        } finally {
            clearTimeout(timeout);
        }
    }

    _loadSection(element) {
        const { endpoint } = element.dataset;
        if (endpoint) {
            fetch(endpoint)
                .then(r => r.json())
                .then(data => {
                    element.innerHTML = this._renderData(data);
                    element.classList.add('loaded');
                });
        }
    }

    _renderData(data) {
        const items = data.items || [];
        const [first, ...rest] = items;
        return items.map(item => `
            <div class="item" data-id="${item.id}">
                <h3>${item.title}</h3>
                <p>${item.description}</p>
            </div>
        `).join('');
    }

    _renderHome() {
        const root = document.querySelector('#app');
        root.innerHTML = '<h1>Home</h1>';
    }

    _renderAbout() {
        const root = document.querySelector('#app');
        root.innerHTML = '<h1>About</h1>';
    }
}

const app = new App();
app.init();

// Expected features:
// Custom: NONE
// Built-in: const, let, arrow-functions, async-functions, template-literals,
//   es6 (Map, destructuring, spread), promises, fetch, abortcontroller,
//   namevalue-storage, json, queryselector, classlist, history,
//   intersectionobserver, matchmedia, es6-class, use-strict, dataset,
//   addeventlistener
