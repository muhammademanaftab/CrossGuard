/**
 * Web Storage and Data APIs Test File
 * Tests detection of storage and data handling APIs
 */

// === localStorage/sessionStorage (namevalue-storage) ===
localStorage.setItem('key', 'value');
const value = localStorage.getItem('key');
localStorage.removeItem('key');
localStorage.clear();

sessionStorage.setItem('session', 'data');
const sessionData = sessionStorage.getItem('session');

// === IndexedDB (indexeddb) ===
const request = indexedDB.open('myDatabase', 1);
request.onerror = event => console.error('IndexedDB error');
request.onsuccess = event => {
    const db = event.target.result;
};

// === IndexedDB 2.0 (indexeddb2) ===
const keyRange = IDBKeyRange.bound(1, 100);
const range = IDBKeyRange.only('specific');

// === FileReader (filereader) ===
const reader = new FileReader();
reader.onload = event => {
    const content = event.target.result;
};
reader.readAsText(file);
reader.readAsDataURL(file);
reader.readAsArrayBuffer(file);

// === FileReaderSync (filereadersync) ===
const syncReader = new FileReaderSync();
const syncContent = syncReader.readAsText(file);

// === File API (fileapi) ===
const file = new File(['content'], 'filename.txt', { type: 'text/plain' });
const blob = new Blob(['data'], { type: 'application/json' });

// === Blob URLs (bloburls) ===
const blobUrl = URL.createObjectURL(blob);
URL.revokeObjectURL(blobUrl);

// === FileSystem API (filesystem) ===
window.requestFileSystem(window.TEMPORARY, 1024 * 1024, onSuccess);
window.webkitRequestFileSystem(window.PERSISTENT, 1024, callback);

// === File System Access API (native-filesystem-api) ===
const fileHandle = await showOpenFilePicker();
const saveHandle = await showSaveFilePicker();

// === Blob Builder (blobbuilder) ===
const newBlob = new Blob(['Hello', ' ', 'World'], { type: 'text/plain' });

// === Base64 Encoding (atob-btoa) ===
const encoded = btoa('Hello World');
const decoded = atob('SGVsbG8gV29ybGQ=');

// === TextEncoder/TextDecoder (textencoder) ===
const encoder = new TextEncoder();
const encoded2 = encoder.encode('Hello');

const decoder = new TextDecoder('utf-8');
const decoded2 = decoder.decode(uint8array);

// === Typed Arrays (typedarrays) ===
const int8 = new Int8Array(10);
const uint8 = new Uint8Array(buffer);
const buffer = new ArrayBuffer(16);
const view = new DataView(buffer);

// === SharedArrayBuffer (sharedarraybuffer) ===
const shared = new SharedArrayBuffer(1024);
Atomics.wait(int32Array, 0, 0);
Atomics.notify(int32Array, 0, 1);

// === JSON (json) ===
const jsonStr = JSON.stringify({ key: 'value' });
const obj = JSON.parse(jsonStr);
JSON.parse('{"a":1}', reviver);

// === Cookie Store API (cookie-store-api) ===
await cookieStore.set('name', 'value');
const cookie = await cookieStore.get('name');
await navigator.cookieStore.delete('name');

// Expected features:
// - namevalue-storage
// - indexeddb
// - indexeddb2
// - filereader
// - filereadersync
// - fileapi
// - bloburls
// - filesystem
// - native-filesystem-api
// - blobbuilder
// - atob-btoa
// - textencoder
// - typedarrays
// - sharedarraybuffer
// - json
// - cookie-store-api
