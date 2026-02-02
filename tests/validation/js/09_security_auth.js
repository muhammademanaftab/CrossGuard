/**
 * Security and Authentication APIs Test File
 * Tests detection of security-related APIs
 */

// === Web Cryptography (cryptography) ===
const key = await crypto.subtle.generateKey(
    { name: 'AES-GCM', length: 256 },
    true,
    ['encrypt', 'decrypt']
);

const encrypted = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv: iv },
    key,
    data
);

// === crypto.getRandomValues (getrandomvalues) ===
const array = new Uint32Array(10);
crypto.getRandomValues(array);
const randomBytes = crypto.getRandomValues(new Uint8Array(16));

// === Web Authentication (webauthn) ===
const credential = await navigator.credentials.create({
    publicKey: {
        challenge: challenge,
        rp: { name: 'Example' },
        user: { id: userId, name: 'user@example.com' }
    }
});

const publicKeyCredential = new PublicKeyCredential();

// === Credential Management (credential-management) ===
const cred = await navigator.credentials.get({
    password: true,
    federated: { providers: ['https://accounts.google.com'] }
});

const passwordCred = new PasswordCredential(form);

// === Passkeys (passkeys) ===
const passkeyCred = await navigator.credentials.create({
    publicKey: passkeyOptions
});

// === Payment Request API (payment-request) ===
const paymentRequest = new PaymentRequest(
    [{ supportedMethods: 'basic-card' }],
    { total: { label: 'Total', amount: { currency: 'USD', value: '10.00' } } }
);

paymentRequest.show().then(response => {
    response.complete('success');
});

// === Permissions API (permissions-api) ===
navigator.permissions.query({ name: 'geolocation' })
    .then(result => {
        console.log('Permission:', result.state);
    });

// === FIDO U2F (u2f) ===
u2f.register(appId, registerRequests, registeredKeys, callback);
u2f.sign(appId, challenge, registeredKeys, callback);

// === Subresource Integrity ===
// Handled via HTML, but JS can check
const integrityAttr = script.integrity;

// === CORS (cors) ===
const img = new Image();
img.crossOrigin = 'anonymous';

// === Feature Policy (feature-policy) ===
document.featurePolicy.allowsFeature('geolocation');
// Via headers: Feature-Policy

// === Permissions Policy (permissions-policy) ===
// Handled via Permissions-Policy header

// Expected features:
// - cryptography
// - getrandomvalues
// - webauthn
// - credential-management
// - passkeys
// - payment-request
// - permissions-api
// - u2f
// - cors
// - feature-policy
// - permissions-policy
