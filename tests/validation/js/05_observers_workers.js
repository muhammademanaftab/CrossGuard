/**
 * Observers and Workers Test File
 * Tests detection of Observer APIs and Web Workers
 */

// === Intersection Observer (intersectionobserver) ===
const intersectionObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            console.log('Element is visible');
        }
    });
}, { threshold: 0.5 });
intersectionObserver.observe(element);

// === Intersection Observer V2 (intersectionobserver-v2) ===
const observerV2 = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isVisible) {
            console.log('Element is actually visible');
        }
    });
}, { trackVisibility: true });

// === Mutation Observer (mutationobserver) ===
const mutationObserver = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
        console.log('DOM changed:', mutation.type);
    });
});
mutationObserver.observe(document.body, {
    childList: true,
    subtree: true
});

// === Resize Observer (resizeobserver) ===
const resizeObserver = new ResizeObserver(entries => {
    entries.forEach(entry => {
        console.log('Size changed:', entry.contentRect);
    });
});
resizeObserver.observe(element);

// === Web Workers (webworkers) ===
const worker = new Worker('worker.js');
worker.postMessage({ data: 'hello' });
worker.onmessage = event => {
    console.log('Worker says:', event.data);
};

// === Shared Workers (sharedworkers) ===
const sharedWorker = new SharedWorker('shared-worker.js');
sharedWorker.port.start();
sharedWorker.port.postMessage('hello');

// === Service Workers (serviceworkers) ===
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(registration => {
            console.log('SW registered');
        });
}

// === Background Sync (background-sync) ===
registration.sync.register('mySync');
self.addEventListener('sync', event => {
    if (event.tag === 'mySync') {
        event.waitUntil(doSync());
    }
});

// === Push API (push-api) ===
registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: publicKey
});
registration.pushManager.getSubscription();

// === WebSockets (websockets) ===
const socket = new WebSocket('wss://example.com/socket');
socket.onopen = () => socket.send('Hello');
socket.onmessage = event => console.log(event.data);
socket.onclose = () => console.log('Closed');

// === EventSource/SSE (eventsource) ===
const eventSource = new EventSource('/events');
eventSource.onmessage = event => {
    console.log('SSE:', event.data);
};
eventSource.onerror = () => console.error('SSE error');

// === BroadcastChannel (broadcastchannel) ===
const channel = new BroadcastChannel('my-channel');
channel.postMessage({ type: 'update', data: 'value' });
channel.onmessage = event => console.log(event.data);

// === Channel Messaging (channel-messaging) ===
const messageChannel = new MessageChannel();
const port1 = messageChannel.port1;
const port2 = messageChannel.port2;
port1.onmessage = event => console.log(event.data);

// === Cross-document Messaging (x-doc-messaging) ===
window.postMessage('hello', '*');
iframe.contentWindow.postMessage('data', 'https://example.com');
window.addEventListener('message', event => {
    if (event.origin === 'https://trusted.com') {
        console.log(event.data);
    }
});

// === WebTransport (webtransport) ===
const transport = new WebTransport('https://example.com:443/wt');
await transport.ready;

// Expected features:
// - intersectionobserver
// - intersectionobserver-v2
// - mutationobserver
// - resizeobserver
// - webworkers
// - sharedworkers
// - serviceworkers
// - background-sync
// - push-api
// - websockets
// - eventsource
// - broadcastchannel
// - channel-messaging
// - x-doc-messaging
// - webtransport
