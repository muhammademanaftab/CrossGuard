/**
 * Modern Web APIs Test File
 * Tests detection of cutting-edge browser APIs
 */

// === WebGL (webgl) ===
const gl = canvas.getContext('webgl');
const webglCtx = canvas.getContext('webgl');
const renderingContext = new WebGLRenderingContext();

// === WebGL 2.0 (webgl2) ===
const gl2 = canvas.getContext('webgl2');
const webgl2Ctx = new WebGL2RenderingContext();

// === WebGPU (webgpu) ===
const adapter = await navigator.gpu.requestAdapter();
const device = await adapter.requestDevice();
const gpuDevice = new GPUDevice();

// === WebXR (webxr) ===
const xrSession = await navigator.xr.requestSession('immersive-vr');
const isSupported = await navigator.xr.isSessionSupported('immersive-ar');

// === WebVR (webvr) ===
navigator.getVRDisplays().then(displays => {
    const vrDisplay = displays[0];
});

// === Web Bluetooth (web-bluetooth) ===
navigator.bluetooth.requestDevice({
    filters: [{ services: ['battery_service'] }]
}).then(device => {
    console.log('Device:', device.name);
});

// === Web Serial (web-serial) ===
const port = await navigator.serial.requestPort();
await port.open({ baudRate: 9600 });

// === WebUSB (webusb) ===
const usbDevice = await navigator.usb.requestDevice({
    filters: [{ vendorId: 0x1234 }]
});

// === WebHID (webhid) ===
const devices = await navigator.hid.requestDevice({
    filters: [{ vendorId: 0x1234 }]
});

// === Web NFC (webnfc) ===
const nfcReader = new NDEFReader();
await nfcReader.scan();
nfcReader.onreading = event => {
    console.log(event.message);
};

// === WebRTC (rtcpeerconnection) ===
const peerConnection = new RTCPeerConnection(config);
const webkitPeer = new webkitRTCPeerConnection(config);
peerConnection.createOffer().then(offer => {
    peerConnection.setLocalDescription(offer);
});

// === Web Animation API (web-animation) ===
element.animate([
    { opacity: 0 },
    { opacity: 1 }
], {
    duration: 1000,
    easing: 'ease-in-out'
});

const animation = new Animation(keyframeEffect);
const keyframes = new KeyframeEffect(element, frames, options);

// === View Transitions API (view-transitions) ===
document.startViewTransition(() => {
    updateDOM();
});

const transition = new ViewTransition();

// === Portals (portals) ===
const portal = document.querySelector('portal');
const portalElement = new HTMLPortalElement();

// === Web Share API (web-share) ===
navigator.share({
    title: 'Title',
    text: 'Description',
    url: 'https://example.com'
});

// === Notifications (notifications) ===
const notification = new Notification('Hello', {
    body: 'World',
    icon: 'icon.png'
});

Notification.permission;
Notification.requestPermission();

// === Clipboard API (clipboard) ===
navigator.clipboard.writeText('Copied text');
navigator.clipboard.readText().then(text => {
    console.log('Clipboard:', text);
});
clipboard.write(data);

// === Async Clipboard API (async-clipboard) ===
navigator.clipboard.read().then(items => {
    for (const item of items) {
        console.log(item.types);
    }
});
clipboard.readText().then(text => console.log(text));

// === Selection API (selection-api) ===
const selection = window.getSelection();
const range = selection.getRangeAt(0);

// === Drag and Drop (dragndrop) ===
element.draggable = true;
element.addEventListener('dragstart', event => {
    event.dataTransfer.setData('text/plain', 'data');
});
element.addEventListener('drop', event => {
    const data = event.dataTransfer.getData('text/plain');
});

// === History API (history) ===
history.pushState({ page: 1 }, 'Title', '/page1');
history.replaceState({ page: 2 }, 'Title', '/page2');
window.addEventListener('popstate', event => {
    console.log('State:', event.state);
});

// === matchMedia (matchmedia) ===
const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
mediaQuery.addEventListener('change', event => {
    console.log('Dark mode:', event.matches);
});

// === getComputedStyle (getcomputedstyle) ===
const styles = getComputedStyle(element);
const color = window.getComputedStyle(element).color;

// === document.execCommand (document-execcommand) ===
document.execCommand('copy');
document.execCommand('bold');

// === Import Maps (import-maps) ===
// <script type="importmap">
const importmap = document.querySelector('script[type="importmap"]');

// === ES6 Modules (es6-module) ===
import { foo } from './module.js';
export const bar = 'baz';
// <script type="module">

// === Dynamic Import (es6-module-dynamic-import) ===
const module = await import('./module.js');
import('./dynamic.js').then(m => console.log(m));

// === Temporal API (temporal) ===
Temporal.Now.instant();
Temporal.Now.plainDateTimeISO();

// Expected features:
// - webgl
// - webgl2
// - webgpu
// - webxr
// - webvr
// - web-bluetooth
// - web-serial
// - webusb
// - webhid
// - webnfc
// - rtcpeerconnection
// - web-animation
// - view-transitions
// - portals
// - web-share
// - notifications
// - clipboard
// - async-clipboard
// - selection-api
// - dragndrop
// - history
// - matchmedia
// - getcomputedstyle
// - document-execcommand
// - import-maps
// - es6-module
// - es6-module-dynamic-import
// - temporal
