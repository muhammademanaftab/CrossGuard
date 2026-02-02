/**
 * Device and Hardware APIs Test File
 * Tests detection of device-related APIs
 */

// === Geolocation (geolocation) ===
navigator.geolocation.getCurrentPosition(
    position => {
        console.log(position.coords.latitude, position.coords.longitude);
    },
    error => console.error(error)
);

const watchId = navigator.geolocation.watchPosition(callback);
navigator.geolocation.clearWatch(watchId);

// === Battery Status (battery-status) ===
navigator.getBattery().then(battery => {
    console.log('Battery level:', battery.level);
    console.log('Charging:', battery.charging);
});

// === Network Information (netinfo) ===
const connection = navigator.connection;
console.log('Effective type:', connection.effectiveType);
console.log('Downlink:', connection.downlink);

// === Vibration API (vibration) ===
navigator.vibrate(200);
navigator.vibrate([100, 50, 100]);
navigator.vibrate(0); // Stop

// === Screen Orientation (screen-orientation) ===
screen.orientation.lock('portrait');
screen.orientation.unlock();
const angle = screen.orientation.angle;

// === Wake Lock (wake-lock) ===
const wakeLock = await navigator.wakeLock.request('screen');
wakeLock.release();

// === Device Orientation (deviceorientation) ===
window.addEventListener('deviceorientation', event => {
    console.log(event.alpha, event.beta, event.gamma);
});

const orientationEvent = new DeviceOrientationEvent('deviceorientation');

window.addEventListener('devicemotion', event => {
    console.log(event.acceleration);
});

const motionEvent = new DeviceMotionEvent('devicemotion');

// === Ambient Light Sensor (ambient-light) ===
const lightSensor = new AmbientLightSensor();
lightSensor.addEventListener('reading', () => {
    console.log('Illuminance:', lightSensor.illuminance);
});
lightSensor.start();

// === Proximity Sensor (proximity) ===
const proximitySensor = new ProximitySensor();
window.addEventListener('deviceproximity', event => {
    console.log('Distance:', event.value);
});

// === Gyroscope (gyroscope) ===
const gyroscope = new Gyroscope({ frequency: 60 });
gyroscope.addEventListener('reading', () => {
    console.log(gyroscope.x, gyroscope.y, gyroscope.z);
});
gyroscope.start();

// === Accelerometer (accelerometer) ===
const accelerometer = new Accelerometer({ frequency: 60 });
accelerometer.addEventListener('reading', () => {
    console.log(accelerometer.x, accelerometer.y, accelerometer.z);
});
accelerometer.start();

// === Magnetometer (magnetometer) ===
const magnetometer = new Magnetometer({ frequency: 10 });
magnetometer.addEventListener('reading', () => {
    console.log(magnetometer.x, magnetometer.y, magnetometer.z);
});

// === Orientation Sensor (orientation-sensor) ===
const absoluteSensor = new AbsoluteOrientationSensor();
const relativeSensor = new RelativeOrientationSensor();

// === Gamepad API (gamepad) ===
const gamepads = navigator.getGamepads();
window.addEventListener('gamepadconnected', event => {
    console.log('Gamepad connected:', event.gamepad.id);
});

// === Pointer Events (pointer) ===
element.addEventListener('pointerdown', event => {
    console.log('Pointer:', event.pointerId);
});
element.addEventListener('pointerup', handler);
const pointerEvent = new PointerEvent('pointerdown');

// === Pointer Lock (pointerlock) ===
element.requestPointerLock();
document.exitPointerLock();
const locked = document.pointerLockElement;

// === Touch Events (touch) ===
element.addEventListener('touchstart', event => {
    const touch = event.touches[0];
    console.log(touch.clientX, touch.clientY);
});
element.addEventListener('touchend', handler);
const touchEvent = new TouchEvent('touchstart');

// === Hardware Concurrency (hardwareconcurrency) ===
const cpuCores = navigator.hardwareConcurrency;
console.log('CPU cores:', cpuCores);

// === Page Visibility (pagevisibility) ===
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Page hidden');
    }
    console.log('Visibility state:', document.visibilityState);
});

// === Online/Offline Status (online-status) ===
console.log('Online:', navigator.onLine);
window.addEventListener('online', () => console.log('Back online'));
window.addEventListener('offline', () => console.log('Gone offline'));

// === Fullscreen API (fullscreen) ===
element.requestFullscreen();
document.exitFullscreen();
const fullscreenEl = document.fullscreenElement;

// === Do Not Track (do-not-track) ===
const dnt = navigator.doNotTrack;

// === devicePixelRatio (devicepixelratio) ===
const dpr = window.devicePixelRatio;
console.log('Device pixel ratio:', dpr);

// Expected features:
// - geolocation
// - battery-status
// - netinfo
// - vibration
// - screen-orientation
// - wake-lock
// - deviceorientation
// - ambient-light
// - proximity
// - gyroscope
// - accelerometer
// - magnetometer
// - orientation-sensor
// - gamepad
// - pointer
// - pointerlock
// - touch
// - hardwareconcurrency
// - pagevisibility
// - online-status
// - fullscreen
// - do-not-track
// - devicepixelratio
