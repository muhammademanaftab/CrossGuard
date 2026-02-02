/**
 * Edge Case: Directive Strings
 * Tests "use strict" and "use asm" detection
 *
 * Expected features: use-strict, asmjs, const, arrow-functions
 */

// File-level strict mode
"use strict";

// Function-level strict mode
function strictFn() {
    'use strict';
    return true;
}

// Method with strict mode
const obj = {
    method() {
        "use strict";
        // strict mode code
    }
};

// Class with strict mode (classes are always strict, but directive might appear)
class StrictClass {
    constructor() {
        "use strict";
    }
}

// asm.js module (example pattern)
function asmModule(stdlib, foreign, heap) {
    "use asm";

    var imul = stdlib.Math.imul;

    function multiply(x, y) {
        x = x | 0;
        y = y | 0;
        return imul(x, y) | 0;
    }

    return { multiply: multiply };
}

// Another asm.js example with single quotes
function anotherAsmModule() {
    'use asm';
    function add(x, y) {
        x = +x;
        y = +y;
        return +(x + y);
    }
    return { add: add };
}

// Regular code
const add = (a, b) => a + b;
