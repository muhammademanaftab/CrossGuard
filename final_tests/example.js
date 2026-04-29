/*
    ============================================================
    Cross Guard detection cross-check list — JavaScript
    ============================================================
    Run:  python -m src.cli.main analyze ../final_test/example.js --format json
    Expected ~22 JS features detected from the Can I Use database:

      1.  es6                                             from class declaration / let / const
      2.  es5                                             from forEach, find, etc.
      3.  const                                           from const declarations
      4.  es6-class                                       from class TravelDiary
      5.  mdn-javascript_classes_private_class_fields     from #stories, #cache
      6.  arrow-functions                                 from s => s.id === id
      7.  template-literals                               from `${this.apiUrl}/stories`
      8.  async-functions                                 from async loadStories()
      9.  promises                                        (implicit via async/await)
      10. mdn-javascript_operators_optional_chaining      from data?.items, form?.addEventListener
      11. mdn-javascript_operators_nullish_coalescing     from ?? operator
      12. fetch                                           from fetch(...)
      13. json                                            from JSON.parse / JSON.stringify
      14. namevalue-storage                               from localStorage
      15. intersectionobserver                            from new IntersectionObserver
      16. queryselector                                   from document.querySelector / querySelectorAll
      17. classlist                                       from element.classList
      18. dataset                                         from element.dataset
      19. addeventlistener                                from addEventListener
      20. domcontentloaded                                from 'DOMContentLoaded' event
      21. array-find                                      from .find(...)
      22. dialog                                          from dialog.showModal()
      23. console-basic                                   from console.error

    Heads-up:
    The current parser may also flag "form-attribute" because the regex
    matches the line "const form = document.querySelector(...)". That's a
    known false positive — the JS variable name "form" trips a pattern
    intended for the HTML form="..." attribute. Note it if it appears.
*/

class TravelDiary {
    #stories = [];
    #cache = new Map();

    constructor(apiUrl) {
        this.apiUrl = apiUrl;
    }

    async loadStories() {
        try {
            const response = await fetch(`${this.apiUrl}/stories`);
            const data = await response.json();
            this.#stories = data?.items ?? [];
            return this.#stories;
        } catch (error) {
            console.error('Failed to load stories:', error);
            return [];
        }
    }

    findStory(id) {
        if (this.#cache.has(id)) {
            return this.#cache.get(id);
        }
        const story = this.#stories.find(s => s.id === id);
        if (story) this.#cache.set(id, story);
        return story;
    }

    get count() {
        return this.#stories.length;
    }
}

const diary = new TravelDiary('https://api.example.com');

document.addEventListener('DOMContentLoaded', async () => {
    const stories = await diary.loadStories();

    const articles = document.querySelectorAll('[data-story-id]');
    articles.forEach(article => {
        const id = article.dataset?.storyId;
        const story = diary.findStory(id);
        article.classList.toggle('has-content', !!story);
    });

    const form = document.querySelector('form');
    form?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const data = new FormData(event.target);
        const payload = Object.fromEntries(data.entries());

        const stored = JSON.parse(localStorage.getItem('drafts') ?? '[]');
        stored.push({ ...payload, savedAt: new Date().toISOString() });
        localStorage.setItem('drafts', JSON.stringify(stored));
    });

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('article').forEach(el => observer.observe(el));

    const dialog = document.querySelector('#confirmDialog');
    document.querySelector('my-widget')?.addEventListener('click', () => {
        dialog?.showModal();
    });
});
