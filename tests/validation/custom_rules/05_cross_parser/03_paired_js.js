/**
 * Cross-Parser Test - JavaScript Companion File
 * Pair with 01_mixed_file_project.html for multi-file analysis
 *
 * Uses no custom JS rules from current custom_rules.json (JS section is empty),
 * but tests that built-in JS rules still work when custom rules system is active.
 *
 * Expected custom features: NONE (no custom JS rules defined)
 * Expected built-in features: const, arrow-functions, async-functions, fetch,
 *   promises, queryselector, classlist, es6, template-literals
 */

// ES6+ syntax
const app = {
    init: async () => {
        const root = document.querySelector('#app');
        const { mode, theme } = app.getConfig();

        try {
            const response = await fetch('/api/init');
            const data = await response.json();

            root.classList.add('initialized');
            root.classList.toggle('dark', theme === 'dark');

            const items = data.items.map(item => ({
                ...item,
                label: `Item: ${item.name}`
            }));

            return new Promise((resolve) => resolve(items));
        } catch (error) {
            console.error(`Initialization failed: ${error.message}`);
        }
    },

    getConfig: () => ({
        mode: 'production',
        theme: localStorage.getItem('theme') || 'light'
    })
};

// Arrow functions with destructuring
const [first, ...rest] = [1, 2, 3, 4, 5];
const processItems = (items) => items.filter(i => i.active);

app.init();

// Expected features:
// Custom: NONE
// Built-in: const, arrow-functions, async-functions, fetch, promises,
//   queryselector, classlist, es6, template-literals, namevalue-storage, json
