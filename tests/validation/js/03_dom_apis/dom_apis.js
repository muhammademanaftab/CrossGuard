/**
 * DOM APIs Test File
 * Tests detection of DOM manipulation and query APIs
 */

// === querySelector/querySelectorAll (queryselector) ===
const element = document.querySelector('.my-class');
const elements = document.querySelectorAll('div.container');
const nested = element.querySelector('span');
const all = document.querySelectorAll('[data-id]');

// === classList (classlist) ===
element.classList.add('active');
element.classList.remove('hidden');
element.classList.toggle('open');
element.classList.contains('selected');
element.classList.replace('old', 'new');

// === dataset (dataset) ===
element.dataset.id = '123';
const userId = element.dataset.userId;
delete element.dataset.temp;

// === addEventListener (addeventlistener) ===
element.addEventListener('click', handleClick);
element.addEventListener('mouseover', handleHover, { passive: true });
element.removeEventListener('click', handleClick);
document.addEventListener('DOMContentLoaded', init);

// === DOMContentLoaded (domcontentloaded) ===
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded');
});

// === Hashchange (hashchange) ===
window.addEventListener('hashchange', event => {
    console.log('Hash changed to:', location.hash);
});

// === Custom Elements (custom-elementsv1) ===
customElements.define('my-element', MyElement);
customElements.get('my-element');
customElements.whenDefined('my-element').then(() => {
    console.log('Element defined');
});

// === Shadow DOM V1 (shadowdomv1) ===
const shadow = element.attachShadow({ mode: 'open' });
shadow.innerHTML = '<slot></slot>';
const root = element.shadowRoot;

// === Declarative Shadow DOM (declarative-shadow-dom) ===
const template = document.querySelector('template[shadowrootmode]');

// === Templates (template) ===
const templateContent = document.querySelector('template').content;
const clone = document.importNode(templateContent, true);

// === Element Methods ===
// getBoundingClientRect (getboundingclientrect)
const rect = element.getBoundingClientRect();
console.log(rect.top, rect.left, rect.width, rect.height);

// closest (element-closest)
const parent = element.closest('.wrapper');
const ancestor = element.closest('[data-root]');

// matches (matchesselector)
if (element.matches('.active')) {
    console.log('Element is active');
}
element.matchesSelector('.test'); // Legacy

// scrollIntoView (scrollintoview)
element.scrollIntoView();
element.scrollIntoView({ behavior: 'smooth', block: 'center' });

// scrollIntoViewIfNeeded (scrollintoviewifneeded)
element.scrollIntoViewIfNeeded();
element.scrollIntoViewIfNeeded(true);

// Scroll methods (element-scroll-methods)
element.scroll({ top: 100, behavior: 'smooth' });
element.scrollTo(0, 500);
element.scrollBy({ top: 50, left: 0 });

// === Text Content (textcontent) ===
element.textContent = 'New text';
const text = element.textContent;

// === Inner Text (innertext) ===
element.innerText = 'Visible text only';
const visible = element.innerText;

// === insertAdjacentHTML (insertadjacenthtml) ===
element.insertAdjacentHTML('beforeend', '<span>New</span>');
element.insertAdjacentHTML('afterbegin', '<div>First</div>');

// === insertAdjacentElement (insert-adjacent) ===
element.insertAdjacentElement('beforebegin', newElement);
element.insertAdjacentText('afterend', 'Text node');

// === ChildNode.remove (childnode-remove) ===
element.remove();

// === DOM Range (dom-range) ===
const range = document.createRange();
range.selectNode(element);
const newRange = new Range();

// === compareDocumentPosition (comparedocumentposition) ===
const position = node1.compareDocumentPosition(node2);

// === elementFromPoint (element-from-point) ===
const elementAtPoint = document.elementFromPoint(100, 200);

// === document.head (documenthead) ===
document.head.appendChild(styleElement);

// === document.scrollingElement (document-scrollingelement) ===
const scrollEl = document.scrollingElement;

// === document.currentScript (document-currentscript) ===
const currentScript = document.currentScript;
const scriptSrc = document.currentScript.src;

// === document.evaluate (document-evaluate-xpath) ===
const xpathResult = document.evaluate('//div[@class="test"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);

// === DOM Manipulation Convenience (dom-manip-convenience) ===
parent.append(child1, child2);
parent.prepend(firstChild);
element.before(sibling);
element.after(nextSibling);

// === relList (rellist) ===
const link = document.querySelector('link');
link.relList.add('preload');
link.relList.contains('stylesheet');

// === Once Event Listener (once-event-listener) ===
element.addEventListener('click', handler, { once: true });

// === Passive Event Listener (passive-event-listener) ===
element.addEventListener('touchstart', handler, { passive: true });

// === Auxclick (auxclick) ===
element.addEventListener('auxclick', event => {
    if (event.button === 1) {
        // Middle click
    }
});

// === Page Transition Events (page-transition-events) ===
window.addEventListener('pageshow', event => {
    if (event.persisted) {
        console.log('Page restored from bfcache');
    }
});
window.addEventListener('pagehide', event => {
    console.log('Page hiding');
});

// === focusin/focusout (focusin-focusout-events) ===
element.addEventListener('focusin', () => console.log('Focus in'));
element.addEventListener('focusout', () => console.log('Focus out'));

// === Printing Events (beforeafterprint) ===
window.addEventListener('beforeprint', () => {
    console.log('About to print');
});
window.addEventListener('afterprint', () => {
    console.log('Print finished');
});

// === Trusted Types (trusted-types) ===
if (window.trustedTypes) {
    const policy = trustedTypes.createPolicy('default', {
        createHTML: input => input
    });
}
const trustedHTML = new TrustedHTML();

// Expected features:
// - queryselector
// - classlist
// - dataset
// - addeventlistener
// - domcontentloaded
// - hashchange
// - custom-elementsv1
// - shadowdomv1
// - declarative-shadow-dom
// - template
// - getboundingclientrect
// - element-closest
// - matchesselector
// - scrollintoview
// - scrollintoviewifneeded
// - element-scroll-methods
// - textcontent
// - innertext
// - insertadjacenthtml
// - insert-adjacent
// - childnode-remove
// - dom-range
// - comparedocumentposition
// - element-from-point
// - documenthead
// - document-scrollingelement
// - document-currentscript
// - document-evaluate-xpath
// - dom-manip-convenience
// - rellist
// - once-event-listener
// - passive-event-listener
// - auxclick
// - page-transition-events
// - focusin-focusout-events
// - beforeafterprint
// - trusted-types
