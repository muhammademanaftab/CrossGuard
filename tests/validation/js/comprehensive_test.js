/**
 * Comprehensive JavaScript Feature Test File
 * Tests detection of ALL major JavaScript features for Cross Guard
 *
 * This file combines features from all categories to provide
 * a complete test of the JS parser's detection capabilities.
 */

// ============================================
// ES6+ SYNTAX FEATURES
// ============================================

// Arrow Functions
const add = (a, b) => a + b;
const greet = name => `Hello, ${name}`;

// Async/Await
async function fetchData() {
    const response = await fetch('/api');
    return await response.json();
}

// Const/Let
const PI = 3.14159;
let counter = 0;

// Template Literals
const message = `Count: ${counter}`;

// Destructuring & Spread
const { x, y } = point;
const [first, ...rest] = items;

// Classes
class Animal {
    constructor(name) {
        this.name = name;
    }
}

// Generators
function* idGenerator() {
    yield 1;
    yield 2;
}

// ============================================
// PROMISES & ASYNC
// ============================================

const promise = new Promise((resolve, reject) => {
    resolve('done');
});

promise
    .then(result => console.log(result))
    .catch(error => console.error(error))
    .finally(() => console.log('cleanup'));

const controller = new AbortController();
fetch('/api', { signal: controller.signal });

requestAnimationFrame(animate);
requestIdleCallback(doWork);

// ============================================
// DOM APIs
// ============================================

document.querySelector('.element');
document.querySelectorAll('div');

element.classList.add('active');
element.dataset.userId = '123';

element.addEventListener('click', handler);
document.addEventListener('DOMContentLoaded', init);

customElements.define('my-element', MyElement);
element.attachShadow({ mode: 'open' });

element.getBoundingClientRect();
element.closest('.parent');
element.matches('.selector');
element.scrollIntoView({ behavior: 'smooth' });

element.textContent = 'text';
element.insertAdjacentHTML('beforeend', '<span/>');
element.remove();

document.createRange();
document.elementFromPoint(100, 200);
document.head.appendChild(el);
document.scrollingElement;

parent.append(child);
parent.prepend(firstChild);

// ============================================
// WEB STORAGE
// ============================================

localStorage.setItem('key', 'value');
sessionStorage.getItem('key');
indexedDB.open('database');

const reader = new FileReader();
const blob = new Blob(['data']);
URL.createObjectURL(blob);

btoa('encode');
atob('decode');

const encoder = new TextEncoder();
const decoder = new TextDecoder();

const buffer = new ArrayBuffer(16);
const view = new Uint8Array(buffer);
const shared = new SharedArrayBuffer(1024);

JSON.stringify(obj);
JSON.parse(str);

// ============================================
// OBSERVERS & WORKERS
// ============================================

new IntersectionObserver(callback);
new MutationObserver(callback);
new ResizeObserver(callback);

new Worker('worker.js');
new SharedWorker('shared.js');
navigator.serviceWorker.register('/sw.js');

new WebSocket('wss://example.com');
new EventSource('/events');
new BroadcastChannel('channel');
new MessageChannel();
window.postMessage('data', '*');

// ============================================
// DEVICE APIs
// ============================================

navigator.geolocation.getCurrentPosition(callback);
navigator.getBattery();
navigator.connection;
navigator.vibrate(100);

screen.orientation.lock('portrait');
navigator.wakeLock.request('screen');

window.addEventListener('deviceorientation', handler);
new Gyroscope();
new Accelerometer();

navigator.getGamepads();
element.addEventListener('pointerdown', handler);
element.requestPointerLock();
element.addEventListener('touchstart', handler);

navigator.hardwareConcurrency;
document.hidden;
document.visibilityState;
navigator.onLine;

element.requestFullscreen();
navigator.doNotTrack;
window.devicePixelRatio;

// ============================================
// MEDIA APIs
// ============================================

new AudioContext();
navigator.mediaDevices.getUserMedia({ video: true });

new MediaRecorder(stream);
new MediaSource();
new ImageCapture(track);
canvas.captureStream();

video.requestPictureInPicture();
navigator.requestMIDIAccess();

new SpeechRecognition();
speechSynthesis.speak(utterance);

new OffscreenCanvas(256, 256);
createImageBitmap(image);

new VideoEncoder(config);
new VideoDecoder(config);

// ============================================
// MODERN APIs
// ============================================

canvas.getContext('webgl');
canvas.getContext('webgl2');
navigator.gpu.requestAdapter();

navigator.xr.requestSession('immersive-vr');
navigator.bluetooth.requestDevice(options);
navigator.serial.requestPort();
navigator.usb.requestDevice(options);
navigator.hid.requestDevice(options);
new NDEFReader();

new RTCPeerConnection(config);

element.animate(keyframes, options);
document.startViewTransition(callback);

navigator.share({ title: 'Title' });
new Notification('Hello');

navigator.clipboard.writeText('text');
navigator.clipboard.read();
window.getSelection();

element.draggable = true;
event.dataTransfer.setData('text', 'data');

history.pushState(state, '', '/url');
window.matchMedia('(prefers-color-scheme: dark)');
getComputedStyle(element);

import('./module.js');
Temporal.Now.instant();

// ============================================
// SECURITY & AUTH
// ============================================

crypto.subtle.generateKey(algorithm, true, ['encrypt']);
crypto.getRandomValues(array);

navigator.credentials.create({ publicKey: options });
navigator.credentials.get({ password: true });

new PaymentRequest(methods, details);
navigator.permissions.query({ name: 'geolocation' });

// ============================================
// ARRAY/STRING/OBJECT METHODS
// ============================================

array.flat();
array.flatMap(fn);
array.includes(item);
array.find(fn);
array.findIndex(fn);
array.findLast(fn);

string.includes(substr);
string.padStart(5, '0');
string.padEnd(5, '-');

Object.entries(obj);
Object.values(obj);

new Map();
new Set();
new WeakMap();
new WeakSet();
Symbol('desc');
Reflect.get(obj, 'prop');

BigInt(123);
new Proxy(target, handler);

Number.isNaN(val);
Number.isFinite(val);

new Intl.NumberFormat('en-US');
new Intl.DateTimeFormat('en-US');
new Intl.PluralRules('en-US');

date.toLocaleDateString('en-US');
string.localeCompare(other);

const lookbehind = /(?<=prefix)/;
new URL('https://example.com');
new URLSearchParams('?a=1');

// ============================================
// PERFORMANCE
// ============================================

performance.now();
performance.mark('start');
performance.measure('op', 'start', 'end');
performance.getEntries();
performance.timing;
performance.navigation;

console.time('op');
console.timeEnd('op');
console.log('message');

navigator.sendBeacon('/analytics', data);

// ============================================
// MISC APIs
// ============================================

WebAssembly.instantiate(bytes);
WebAssembly.compile(bytes);

new XMLSerializer();
new DOMParser();
new DOMMatrix();
new Path2D();

ctx.globalCompositeOperation = 'multiply';

new ReadableStream();
new WritableStream();
new TransformStream();

new CustomEvent('myevent', { detail: {} });
element.dispatchEvent(event);

CSS.supports('display', 'grid');
CSS.paintWorklet.addModule('painter.js');

document.fonts.ready;
new FontFace('Font', 'url(font.woff2)');

new XMLHttpRequest();
event.key;
event.code;
event.which;
event.getModifierState('Shift');

// Expected: ~150+ unique Can I Use features detected
