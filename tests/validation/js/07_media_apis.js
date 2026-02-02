/**
 * Media and Audio/Video APIs Test File
 * Tests detection of media-related APIs
 */

// === Web Audio API (audio-api) ===
const audioCtx = new AudioContext();
const webkitCtx = new webkitAudioContext();
const oscillator = audioCtx.createOscillator();
oscillator.connect(audioCtx.destination);
oscillator.start();

// === getUserMedia/Stream API (streams) ===
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then(stream => {
        video.srcObject = stream;
    });

// === MediaRecorder (mediarecorder) ===
const mediaRecorder = new MediaRecorder(stream);
mediaRecorder.start();
mediaRecorder.ondataavailable = event => {
    chunks.push(event.data);
};
mediaRecorder.stop();

// === Media Source Extensions (mediasource) ===
const mediaSource = new MediaSource();
video.src = URL.createObjectURL(mediaSource);
mediaSource.addEventListener('sourceopen', () => {
    const sourceBuffer = mediaSource.addSourceBuffer('video/mp4');
});

// === ImageCapture (imagecapture) ===
const imageCapture = new ImageCapture(videoTrack);
imageCapture.takePhoto().then(blob => {
    img.src = URL.createObjectURL(blob);
});

// === captureStream (mediacapture-fromelement) ===
const canvasStream = canvas.captureStream(30);
const videoStream = video.captureStream();

// === Video Tracks (videotracks) ===
const videoTracks = video.videoTracks;
video.videoTracks[0].selected = true;
const videoTrackList = new VideoTrackList();

// === Audio Tracks (audiotracks) ===
const audioTracks = video.audioTracks;
video.audioTracks[0].enabled = true;
const audioTrackList = new AudioTrackList();

// === Picture-in-Picture (picture-in-picture) ===
video.requestPictureInPicture()
    .then(pipWindow => {
        console.log('PiP window:', pipWindow);
    });

// === Encrypted Media Extensions (eme) ===
navigator.requestMediaKeySystemAccess('com.widevine.alpha', config)
    .then(keySystemAccess => {
        return keySystemAccess.createMediaKeys();
    });
const mediaKeys = new MediaKeys();

// === Web MIDI API (midi) ===
navigator.requestMIDIAccess()
    .then(midiAccess => {
        const inputs = midiAccess.inputs;
        const outputs = midiAccess.outputs;
    });

// === Speech Recognition (speech-recognition) ===
const recognition = new SpeechRecognition();
const webkitRecognition = new webkitSpeechRecognition();
recognition.onresult = event => {
    console.log(event.results[0][0].transcript);
};
recognition.start();

// === Speech Synthesis (speech-synthesis) ===
const utterance = new SpeechSynthesisUtterance('Hello World');
speechSynthesis.speak(utterance);
const voices = speechSynthesis.getVoices();

// === OffscreenCanvas (offscreencanvas) ===
const offscreen = new OffscreenCanvas(256, 256);
const offscreenCtx = offscreen.getContext('2d');
const transferred = canvas.transferControlToOffscreen();

// === createImageBitmap (createimagebitmap) ===
createImageBitmap(image).then(bitmap => {
    ctx.drawImage(bitmap, 0, 0);
});

createImageBitmap(blob, 0, 0, 100, 100).then(bitmap => {
    // Use cropped bitmap
});

// === WebCodecs (webcodecs) ===
const videoEncoder = new VideoEncoder({
    output: chunk => console.log(chunk),
    error: e => console.error(e)
});

const videoDecoder = new VideoDecoder({
    output: frame => console.log(frame),
    error: e => console.error(e)
});

const audioEncoder = new AudioEncoder({
    output: chunk => console.log(chunk),
    error: e => console.error(e)
});

// Expected features:
// - audio-api
// - streams
// - mediarecorder
// - mediasource
// - imagecapture
// - mediacapture-fromelement
// - videotracks
// - audiotracks
// - picture-in-picture
// - eme
// - midi
// - speech-recognition
// - speech-synthesis
// - offscreencanvas
// - createimagebitmap
// - webcodecs
