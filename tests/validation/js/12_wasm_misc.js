/**
 * WebAssembly and Misc APIs Test File
 * Tests detection of WASM and other miscellaneous APIs
 */

// === WebAssembly (wasm) ===
WebAssembly.instantiate(wasmBytes, imports)
    .then(result => {
        const instance = result.instance;
        const exports = instance.exports;
    });

WebAssembly.compile(wasmBytes).then(module => {
    console.log('Compiled');
});

const wasmModule = await WebAssembly.compileStreaming(fetch('module.wasm'));

// === WASM BigInt (wasm-bigint) ===
// WebAssembly with BigInt i64 conversion
const i64Result = WebAssembly.instantiate(wasmWithBigInt);

// === WASM Threads (wasm-threads) ===
const sharedMemory = new SharedArrayBuffer(1024);
Atomics.wait(int32Array, 0, 0);
Atomics.notify(int32Array, 0, 1);
Atomics.add(int32Array, 0, 1);

// === WASM SIMD (wasm-simd) ===
// v128 SIMD operations in WASM

// === WASM Bulk Memory (wasm-bulk-memory) ===
// memory.copy, memory.fill operations

// === WASM Multi-Value (wasm-multi-value) ===
// Functions returning multiple values

// === WASM Mutable Globals (wasm-mutable-globals) ===
const wasmGlobal = new WebAssembly.Global({ value: 'i32', mutable: true }, 42);

// === WASM Reference Types (wasm-reference-types) ===
// externref, funcref types

// === asm.js (asmjs) ===
"use asm";
function asmModule(stdlib, foreign, heap) {
    'use asm';
    // asm.js code
}

// === XML Serializer/DOMParser (xml-serializer) ===
const serializer = new XMLSerializer();
const xmlString = serializer.serializeToString(document);

const parser = new DOMParser();
const doc = parser.parseFromString('<root/>', 'text/xml');

// === DOMMatrix (dommatrix) ===
const matrix = new DOMMatrix();
matrix.translateSelf(10, 20);
matrix.rotateSelf(45);

// === Path2D (path2d) ===
const path = new Path2D();
path.moveTo(0, 0);
path.lineTo(100, 100);
path.addPath(otherPath);

ctx.stroke(path);

// === Canvas Blending (canvas-blending) ===
ctx.globalCompositeOperation = 'multiply';
ctx.globalCompositeOperation = 'screen';

// === Streams API (stream) ===
const readable = new ReadableStream({
    start(controller) {
        controller.enqueue('chunk');
    }
});

const writable = new WritableStream({
    write(chunk) {
        console.log(chunk);
    }
});

const transform = new TransformStream();

// === CustomEvent (customevent) ===
const event = new CustomEvent('myevent', {
    detail: { key: 'value' }
});
element.dispatchEvent(event);

// === dispatchEvent (dispatchevent) ===
element.dispatchEvent(new Event('click'));
document.dispatchEvent(customEvent);

// === Data URIs (datauri) ===
const dataUrl = 'data:image/png;base64,iVBOR...';
const textData = 'data:text/plain;charset=utf-8,Hello';
const jsonData = 'data:application/json,{"key":"value"}';

// === CSS.supports() (css-supports-api) ===
CSS.supports('display', 'grid');
CSS.supports('(display: flex) and (gap: 10px)');

// === CSS Paint API (css-paint-api) ===
CSS.paintWorklet.addModule('paint-worklet.js');
registerPaint('myPainter', class {
    paint(ctx, geom) {}
});

// === CSS Module Scripts (css-module-scripts) ===
import styles from './styles.css' assert { type: 'css' };

// === Font Loading API (font-loading) ===
document.fonts.ready.then(() => {
    console.log('Fonts loaded');
});

const font = new FontFace('MyFont', 'url(font.woff2)');
await font.load();
document.fonts.add(font);

// === registerProtocolHandler (registerprotocolhandler) ===
navigator.registerProtocolHandler('web+custom', 'https://example.com/?uri=%s');

// === XHR Level 2 (xhr2) ===
const xhr = new XMLHttpRequest();
xhr.responseType = 'arraybuffer';
xhr.upload.onprogress = event => {
    console.log('Upload progress:', event.loaded);
};

// === Keyboard Events ===
// KeyboardEvent.key (keyboardevent-key)
element.addEventListener('keydown', event => {
    console.log('Key:', event.key);
});

// KeyboardEvent.code (keyboardevent-code)
element.addEventListener('keyup', event => {
    console.log('Code:', event.code);
});

// KeyboardEvent.which (keyboardevent-which)
element.addEventListener('keypress', event => {
    console.log('Which:', event.which);
});

// KeyboardEvent.charCode (keyboardevent-charcode)
console.log('Char code:', event.charCode);

// KeyboardEvent.getModifierState (keyboardevent-getmodifierstate)
event.getModifierState('Shift');
event.getModifierState('Control');

// KeyboardEvent.location (keyboardevent-location)
console.log('Location:', event.location);

// Expected features:
// - wasm
// - wasm-bigint
// - wasm-threads (sharedarraybuffer)
// - asmjs
// - xml-serializer
// - dommatrix
// - path2d
// - canvas-blending
// - stream
// - customevent
// - dispatchevent
// - datauri
// - css-supports-api
// - css-paint-api
// - css-module-scripts
// - font-loading
// - registerprotocolhandler
// - xhr2
// - keyboardevent-key
// - keyboardevent-code
// - keyboardevent-which
// - keyboardevent-charcode
// - keyboardevent-getmodifierstate
// - keyboardevent-location
