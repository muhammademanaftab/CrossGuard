/**
 * Comprehensive JavaScript Test File
 *
 * This file contains ALL detectable JavaScript features from the Cross Guard parser.
 * Each section tests specific feature categories from js_feature_maps.py.
 * Total: ~245+ features across all categories.
 */

// ============================================================================
// JS SYNTAX FEATURES (9)
// ============================================================================

// arrow-functions
const arrowFn = () => {};
const arrowWithParams = (a, b) => a + b;
const arrowSingleParam = x => x * 2;

// async-functions
async function asyncFunction() {
    return await Promise.resolve(1);
}
const asyncArrow = async () => {
    return await fetch('/api');
};
const asyncMethod = async x => x;

// const
const constVar = 'immutable';

// let
let letVar = 'block-scoped';

// template-literals
const name = 'World';
const greeting = `Hello ${name}!`;
const multiLine = `Line 1
Line 2 ${1 + 1}`;

// es6 (destructuring, spread, rest)
const { a, b } = { a: 1, b: 2 };
const [first, second] = [1, 2];
const spreadArray = [...[1, 2, 3], 4, 5];
const spreadObj = { ...{ x: 1 }, y: 2 };
const { nested: { deep } } = { nested: { deep: true } };

// rest-parameters
function withRest(...args) {
    return args.length;
}
const arrowRest = (...params) => params;

// es6-class
class MyClass {
    constructor(value) {
        this.value = value;
    }

    getValue() {
        return this.value;
    }

    static create() {
        return new MyClass(0);
    }
}

class ExtendedClass extends MyClass {
    constructor(value, extra) {
        super(value);
        this.extra = extra;
    }
}

// es6-generators
function* generator() {
    yield 1;
    yield 2;
    yield 3;
}
const gen = function* () {
    yield 'a';
};

// ============================================================================
// JS API FEATURES - Part 1 (50+)
// ============================================================================

// promises
new Promise((resolve, reject) => {
    setTimeout(() => resolve('done'), 1000);
});
Promise.resolve(1).then(x => x).catch(e => e);
Promise.all([]).then(() => {});
Promise.race([]).then(() => {});

// fetch
fetch('/api/data')
    .then(response => response.json())
    .then(data => console.log(data));

// bigint
const bigInt = BigInt(9007199254740991);
const bigIntLiteral = 123n;

// intersectionobserver
const intersectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            console.log('visible');
        }
    });
});

// mutationobserver
const mutationObserver = new MutationObserver((mutations) => {
    mutations.forEach(m => console.log(m));
});

// resizeobserver
const resizeObserver = new ResizeObserver((entries) => {
    entries.forEach(e => console.log(e.contentRect));
});

// proxy
const proxy = new Proxy({}, {
    get: (target, prop) => prop in target ? target[prop] : 'default'
});

// es6 (Map, Set, WeakMap, WeakSet, Symbol, Reflect)
const map = new Map();
map.set('key', 'value');
const set = new Set([1, 2, 3]);
const weakMap = new WeakMap();
const weakSet = new WeakSet();
const symbol = Symbol('description');
Reflect.get({}, 'prop');

// json
const jsonString = JSON.stringify({ a: 1 });
const parsed = JSON.parse('{"b": 2}');
JSON.stringify({ c: 3 }, null, 2);

// dragndrop
const draggable = document.createElement('div');
draggable.draggable = true;
draggable.addEventListener('dragstart', (e) => {
    e.dataTransfer.setData('text', 'data');
});
draggable.addEventListener('drop', (e) => {
    e.dataTransfer.getData('text');
});

// es5 (Array methods)
const arr = [1, 2, 3, 4, 5];
arr.forEach(x => console.log(x));
arr.map(x => x * 2);
arr.filter(x => x > 2);
arr.reduce((acc, x) => acc + x, 0);
arr.some(x => x > 3);
arr.every(x => x > 0);

// geolocation
navigator.geolocation.getCurrentPosition(
    pos => console.log(pos),
    err => console.error(err)
);
navigator.geolocation.watchPosition(pos => console.log(pos));

// notifications
new Notification('Hello!', { body: 'Message' });
Notification.permission;

// serviceworkers
navigator.serviceWorker.register('/sw.js');

// webworkers
const worker = new Worker('worker.js');

// websockets
const socket = new WebSocket('wss://example.com');

// requestanimationframe
requestAnimationFrame(() => {});
cancelAnimationFrame(1);

// fullscreen
document.documentElement.requestFullscreen();
document.exitFullscreen();
document.fullscreenElement;

// pagevisibility
document.hidden;
document.visibilityState;
document.addEventListener('visibilitychange', () => {});

// cryptography
crypto.subtle.digest('SHA-256', new ArrayBuffer(0));
crypto.getRandomValues(new Uint8Array(16));

// stream
const readable = new ReadableStream();
const writable = new WritableStream();
const transform = new TransformStream();

// streams (getUserMedia)
navigator.mediaDevices.getUserMedia({ video: true });

// xhr2
const xhr = new XMLHttpRequest();

// online-status
navigator.onLine;
window.addEventListener('online', () => {});
window.addEventListener('offline', () => {});

// eventsource
const eventSource = new EventSource('/events');

// broadcastchannel
const channel = new BroadcastChannel('my-channel');

// channel-messaging
const messageChannel = new MessageChannel();
const port = new MessagePort();

// x-doc-messaging
window.postMessage('hello', '*');

// ============================================================================
// JS API FEATURES - Part 2 (50+)
// ============================================================================

// indexeddb
indexedDB.open('myDB', 1);
const keyRange = IDBKeyRange.bound(1, 10);

// filereader
const fileReader = new FileReader();

// bloburls
URL.createObjectURL(new Blob());

// filesystem
// Note: This is a non-standard API
// requestFileSystem is deprecated
// webkitRequestFileSystem(TEMPORARY, 1024, () => {});

// native-filesystem-api
// showOpenFilePicker();
// showSaveFilePicker();

// fileapi
const file = new File(['content'], 'file.txt');
const blob = new Blob(['data']);

// atob-btoa
const encoded = btoa('hello');
const decoded = atob(encoded);

// textencoder
const encoder = new TextEncoder();
const decoder = new TextDecoder();

// typedarrays
const int8 = new Int8Array(8);
const uint8 = new Uint8Array(8);
const buffer = new ArrayBuffer(16);
const dataView = new DataView(buffer);

// sharedarraybuffer
const shared = new SharedArrayBuffer(16);
Atomics.add(new Int32Array(shared), 0, 1);

// sharedworkers
const sharedWorker = new SharedWorker('shared.js');

// webrtc / rtcpeerconnection
const pc = new RTCPeerConnection();

// webauthn
navigator.credentials.get({ publicKey: {} });
PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();

// credential-management
navigator.credentials.get({ password: true });
// new PasswordCredential({ id: '', password: '' });

// payment-request
const paymentRequest = new PaymentRequest([{ supportedMethods: 'basic-card' }], {
    total: { label: 'Total', amount: { currency: 'USD', value: '10.00' } }
});

// push-api
// registration.pushManager.subscribe();

// permissions-api
navigator.permissions.query({ name: 'geolocation' });

// battery-status
navigator.getBattery().then(battery => console.log(battery));

// netinfo
navigator.connection;

// vibration
navigator.vibrate(200);

// screen-orientation
screen.orientation.lock('portrait');

// wake-lock
navigator.wakeLock.request('screen');

// gamepad
navigator.getGamepads();

// pointer
document.addEventListener('pointerdown', (e) => console.log(e));
document.addEventListener('pointermove', (e) => console.log(e));
const pointerEvent = new PointerEvent('pointerdown');

// pointerlock
document.body.requestPointerLock();
document.pointerLockElement;

// touch
document.addEventListener('touchstart', (e) => console.log(e));
document.addEventListener('touchend', (e) => console.log(e));
const touchEvent = new TouchEvent('touchstart');

// deviceorientation
window.addEventListener('deviceorientation', (e) => console.log(e));
const orientationEvent = new DeviceOrientationEvent('deviceorientation');

// devicemotion
window.addEventListener('devicemotion', (e) => console.log(e));
const motionEvent = new DeviceMotionEvent('devicemotion');

// ambient-light
const lightSensor = new AmbientLightSensor();

// proximity
// const proxSensor = new ProximitySensor();

// speech-recognition
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

// speech-synthesis
speechSynthesis.speak(new SpeechSynthesisUtterance('Hello'));

// web-share
navigator.share({ title: 'Title', url: 'https://example.com' });

// web-animation
document.body.animate([{ opacity: 0 }, { opacity: 1 }], 1000);
const animation = new Animation();
const keyframeEffect = new KeyframeEffect(null, [], 1000);

// requestidlecallback
requestIdleCallback(() => {});
cancelIdleCallback(1);

// console-time
console.time('timer');
console.timeEnd('timer');

// high-resolution-time
performance.now();
performance.mark('start');

// user-timing
performance.mark('user-mark');
performance.measure('user-measure');

// resource-timing
performance.getEntries();
// const resourceTiming = new PerformanceResourceTiming();

// nav-timing
performance.timing;
performance.navigation;

// server-timing
// PerformanceServerTiming available in entries

// ============================================================================
// JS API FEATURES - Part 3 (50+)
// ============================================================================

// mediarecorder
const mediaRecorder = new MediaRecorder(new MediaStream());

// mediasource
const mediaSource = new MediaSource();

// midi
navigator.requestMIDIAccess().then(midi => console.log(midi));

// web-bluetooth
navigator.bluetooth.requestDevice({ filters: [] });

// web-serial
navigator.serial.requestPort();

// webusb
navigator.usb.requestDevice({ filters: [] });

// webhid
navigator.hid.requestDevice({ filters: [] });

// webnfc
const ndefReader = new NDEFReader();

// webgpu
navigator.gpu.requestAdapter();

// webxr
navigator.xr.requestSession('immersive-vr');

// webvr (deprecated)
// navigator.getVRDisplays();

// offscreencanvas
const offscreen = new OffscreenCanvas(300, 150);

// webcodecs
const videoEncoder = new VideoEncoder({ output: () => {}, error: () => {} });
const videoDecoder = new VideoDecoder({ output: () => {}, error: () => {} });
const audioEncoder = new AudioEncoder({ output: () => {}, error: () => {} });

// webtransport
const transport = new WebTransport('https://example.com');

// temporal
Temporal.Now.instant();

// url
const url = new URL('https://example.com');
URL.canParse('https://example.com');

// urlsearchparams
const params = new URLSearchParams('a=1&b=2');

// selection-api
window.getSelection();

// clipboard
navigator.clipboard.writeText('copied');

// async-clipboard
navigator.clipboard.read();
navigator.clipboard.readText();

// picture-in-picture
document.createElement('video').requestPictureInPicture();
// PictureInPictureWindow

// view-transitions
document.startViewTransition(() => {});
// ViewTransition

// passkeys
PublicKeyCredential.isConditionalMediationAvailable();

// unhandledrejection
window.addEventListener('unhandledrejection', (e) => console.log(e));
window.addEventListener('rejectionhandled', (e) => console.log(e));

// promise-finally
Promise.resolve(1).finally(() => {});

// es6-number
Number.isNaN(NaN);
Number.isFinite(100);
Number.parseInt('100');

// use-strict
'use strict';

// setimmediate (non-standard)
// setImmediate(() => {});
// clearImmediate(1);

// getrandomvalues
crypto.getRandomValues(new Uint8Array(16));

// gyroscope
const gyro = new Gyroscope();

// accelerometer
const accel = new Accelerometer();

// magnetometer
const mag = new Magnetometer();

// orientation-sensor
const orientSensor = new AbsoluteOrientationSensor();

// hardwareconcurrency
navigator.hardwareConcurrency;

// history
history.pushState({}, '', '/new-url');
history.replaceState({}, '', '/replaced');
window.addEventListener('popstate', () => {});

// ime
// inputMethodContext

// import-maps (HTML attribute, pattern matched)
// <script type="importmap">

// imports (HTML imports - deprecated)
// HTMLImports

// input-event
document.addEventListener('input', () => {});

// input-selection
const input = document.createElement('input');
input.selectionStart;
input.selectionEnd;
input.setSelectionRange(0, 5);

// internationalization
new Intl.Collator();
new Intl.NumberFormat();
new Intl.DateTimeFormat();

// intersectionobserver-v2
// entry.isVisible

// intl-pluralrules
new Intl.PluralRules('en');

// js-regexp-lookbehind
const lookbehind = /(?<=@)\w+/;
const negativeLookbehind = /(?<!@)\w+/;

// keyboardevent-charcode
document.addEventListener('keypress', (e) => e.charCode);

// keyboardevent-getmodifierstate
document.addEventListener('keydown', (e) => e.getModifierState('Control'));

// keyboardevent-location
document.addEventListener('keydown', (e) => e.location);

// localecompare
'a'.localeCompare('b');

// matchesselector
document.body.matches('.class');
// document.body.matchesSelector('.class');

// matchmedia
window.matchMedia('(min-width: 768px)');

// mutation-events (deprecated)
document.addEventListener('DOMAttrModified', () => {});
document.addEventListener('DOMNodeInserted', () => {});
document.addEventListener('DOMNodeRemoved', () => {});

// ============================================================================
// JS ARRAY METHODS (4)
// ============================================================================

// array-flat
[[1, 2], [3, 4]].flat();
[1, 2, 3].flatMap(x => [x, x * 2]);

// array-includes
[1, 2, 3].includes(2);

// array-find
[1, 2, 3].find(x => x > 1);
[1, 2, 3].findIndex(x => x > 1);

// array-find-last
[1, 2, 3].findLast(x => x > 1);
[1, 2, 3].findLastIndex(x => x > 1);

// ============================================================================
// JS STRING METHODS (2)
// ============================================================================

// es6-string-includes
'hello'.includes('ell');

// pad-start-end
'5'.padStart(3, '0');
'5'.padEnd(3, '0');

// ============================================================================
// JS OBJECT METHODS (3)
// ============================================================================

// object-entries
Object.entries({ a: 1, b: 2 });

// object-values
Object.values({ a: 1, b: 2 });

// object-observe (deprecated)
// Object.observe({}, () => {});

// ============================================================================
// JS STORAGE APIS (2)
// ============================================================================

// namevalue-storage
localStorage.setItem('key', 'value');
localStorage.getItem('key');
sessionStorage.setItem('session', 'data');

// indexeddb (already covered above)

// ============================================================================
// JS DOM APIS - Part 1 (30+)
// ============================================================================

// queryselector
document.querySelector('.class');
document.querySelectorAll('div');

// classlist
document.body.classList.add('active');
document.body.classList.remove('inactive');
document.body.classList.toggle('visible');

// dataset
document.body.dataset.customData = 'value';

// custom-elements / custom-elementsv1
customElements.define('my-element', class extends HTMLElement {});
customElements.get('my-element');

// addeventlistener
document.addEventListener('click', () => {});
document.removeEventListener('click', () => {});

// domcontentloaded
document.addEventListener('DOMContentLoaded', () => {});

// hashchange
window.addEventListener('hashchange', () => {});

// page-transition-events
window.addEventListener('pageshow', () => {});
window.addEventListener('pagehide', () => {});

// beforeafterprint
window.addEventListener('beforeprint', () => {});
window.addEventListener('afterprint', () => {});

// focusin-focusout-events
document.addEventListener('focusin', () => {});
document.addEventListener('focusout', () => {});

// getboundingclientrect
document.body.getBoundingClientRect();

// element-from-point
document.elementFromPoint(100, 100);

// textcontent
document.body.textContent = 'text';

// innertext
document.body.innerText = 'inner';

// insertadjacenthtml
document.body.insertAdjacentHTML('beforeend', '<div></div>');

// insert-adjacent
document.body.insertAdjacentElement('beforeend', document.createElement('div'));
document.body.insertAdjacentText('beforeend', 'text');

// childnode-remove
document.createElement('div').remove();

// dom-range
document.createRange();
const range = new Range();

// comparedocumentposition
document.body.compareDocumentPosition(document.head);

// keyboardevent-key
document.addEventListener('keydown', (e) => console.log(e.key));

// keyboardevent-code
document.addEventListener('keydown', (e) => console.log(e.code));

// keyboardevent-which
document.addEventListener('keydown', (e) => console.log(e.which));

// devicepixelratio
window.devicePixelRatio;

// getcomputedstyle
getComputedStyle(document.body);
window.getComputedStyle(document.body);

// document-execcommand
document.execCommand('copy');

// xml-serializer
const serializer = new XMLSerializer();
const parser = new DOMParser();

// ============================================================================
// JS DOM APIS - Part 2 (30+)
// ============================================================================

// trusted-types
// trustedTypes.createPolicy('default', {});

// shadowdomv1
document.createElement('div').attachShadow({ mode: 'open' });
// element.shadowRoot

// shadowdom (deprecated v0)
// document.createElement('div').createShadowRoot();

// imagecapture
const imageCapture = new ImageCapture(new MediaStreamTrack());

// mediacapture-fromelement
document.createElement('video').captureStream();

// rellist
document.createElement('a').relList;

// scrollintoview
document.body.scrollIntoView();

// scrollintoviewifneeded
document.body.scrollIntoViewIfNeeded();

// once-event-listener
document.addEventListener('click', () => {}, { once: true });

// passive-event-listener
document.addEventListener('scroll', () => {}, { passive: true });

// auxclick
document.addEventListener('auxclick', () => {});

// registerprotocolhandler
navigator.registerProtocolHandler('web+custom', '/handle?url=%s');

// documenthead
document.head;

// document-scrollingelement
document.scrollingElement;

// document-evaluate-xpath
document.evaluate('//div', document, null, XPathResult.ANY_TYPE, null);

// declarative-shadow-dom (HTML attribute)
// shadowrootmode="open"

// dom-manip-convenience
document.body.append(document.createElement('div'));
document.body.prepend(document.createElement('span'));
document.body.before(document.createComment('comment'));
document.body.after(document.createTextNode('text'));

// element-closest
document.body.closest('html');

// element-scroll-methods
document.body.scroll({ top: 0 });
document.body.scrollTo({ top: 100 });
document.body.scrollBy({ top: 50 });

// ============================================================================
// JS MODULE & MISC FEATURES (15+)
// ============================================================================

// es6-module (via script tag with type="module")
import defaultExport from './module.js';
import { namedExport } from './module.js';
export default function() {}
export const exported = 1;

// es6-module-dynamic-import
import('./dynamic-module.js').then(module => console.log(module));

// abortcontroller
const controller = new AbortController();
const signal = controller.signal;
controller.abort();

// canvas-blending
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
ctx.globalCompositeOperation = 'multiply';

// webgl
canvas.getContext('webgl');
// WebGLRenderingContext

// webgl2
canvas.getContext('webgl2');
// WebGL2RenderingContext

// customevent
const customEvent = new CustomEvent('myevent', { detail: { key: 'value' } });

// dispatchevent
document.dispatchEvent(customEvent);

// do-not-track
navigator.doNotTrack;

// document-currentscript
document.currentScript;

// dommatrix
const matrix = new DOMMatrix();

// date-tolocaledatestring
new Date().toLocaleDateString('en-US', { weekday: 'long' });
new Date().toLocaleTimeString();

// eme (Encrypted Media Extensions)
navigator.requestMediaKeySystemAccess('org.w3.clearkey', []);
// MediaKeys

// getelementsbyclassname
document.getElementsByClassName('class');

// img-naturalwidth-naturalheight
const img = document.createElement('img');
img.naturalWidth;
img.naturalHeight;

// constraint-validation
input.validity;
input.checkValidity();
input.setCustomValidity('Invalid');

// cookie-store-api
// cookieStore.get('name');

// cors
img.crossOrigin = 'anonymous';

// createimagebitmap
createImageBitmap(new Blob());

// blobbuilder
new Blob(['content'], { type: 'text/plain' });

// console-basic
console.log('log');
console.warn('warn');
console.error('error');

// path2d
const path = new Path2D();
path.addPath(new Path2D());

// videotracks / audiotracks
const video = document.createElement('video');
video.videoTracks;
video.audioTracks;

// svg-filters (HTML/SVG content)
// <filter>, <feGaussianBlur>, etc.

// svg-smil (HTML/SVG content)
// <animate>, <animateTransform>, etc.
