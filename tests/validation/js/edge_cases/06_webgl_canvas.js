/**
 * Edge Case: WebGL and Canvas APIs
 * Tests WebGL detection which has special handling due to string content
 *
 * Expected features: webgl, webgl2, canvas-blending, path2d, createimagebitmap
 */

// WebGL via context type
const canvas = document.getElementById('canvas');
const gl = canvas.getContext('webgl');
const gl2 = canvas.getContext('webgl2');

// WebGL via constructor reference (survives string stripping)
if (gl instanceof WebGLRenderingContext) {
    console.log('WebGL 1 supported');
}

if (typeof WebGL2RenderingContext !== 'undefined') {
    console.log('WebGL 2 supported');
}

// Direct constructor (for testing)
const webglCtx = new WebGLRenderingContext();
const webgl2Ctx = new WebGL2RenderingContext();

// WebGL operations
gl.clearColor(0.0, 0.0, 0.0, 1.0);
gl.enable(gl.DEPTH_TEST);
gl.clear(gl.COLOR_BUFFER_BIT);

// Canvas 2D with blend modes
const ctx = canvas.getContext('2d');
ctx.globalCompositeOperation = 'multiply';
ctx.globalCompositeOperation = 'screen';
ctx.globalCompositeOperation = 'overlay';

// Path2D
const path = new Path2D();
path.moveTo(0, 0);
path.lineTo(100, 100);
path.arc(50, 50, 25, 0, Math.PI * 2);
ctx.stroke(path);

// Path2D with SVG path
const svgPath = new Path2D('M10 10 h 80 v 80 h -80 Z');
ctx.fill(svgPath);

// Path2D addPath
const combinedPath = new Path2D();
combinedPath.addPath(path);
combinedPath.addPath(svgPath);

// createImageBitmap
createImageBitmap(canvas).then(bitmap => {
    ctx.drawImage(bitmap, 0, 0);
});

createImageBitmap(blob, 0, 0, 100, 100).then(cropped => {
    // Use cropped bitmap
});

// OffscreenCanvas (if needed)
const offscreen = new OffscreenCanvas(256, 256);
const offCtx = offscreen.getContext('2d');
