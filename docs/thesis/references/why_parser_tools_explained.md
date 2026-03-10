# Why Each Parser Needs Its Tools — Explained Simply

## The Big Question

Each of our 3 parsers uses a **combination** of tools, never just one tool alone:

| Parser | Tool 1 (Structure) | Tool 2 (Detection) |
|--------|-------------------|-------------------|
| **HTML** | BeautifulSoup | Dictionary lookups |
| **CSS** | tinycss2 | Regex patterns |
| **JS** | tree-sitter | 3 tiers (AST types + AST names + regex) |

Why can't we just use one tool? Why do we need these combinations?

The answer is always the same pattern:
- **Tool 1** understands the STRUCTURE of the language (what's a comment, what's a string, what's real code, what belongs to what)
- **Tool 2** DETECTS the features in the clean, structured code

Neither can do the other's job well.

---

## Part 1: CSS Parser — Why tinycss2 + Regex?

### What tinycss2 does

tinycss2 is a Python library that **reads CSS and understands its structure**. It knows:
- What's a comment and what's real code
- What's inside a string and what's outside
- Which `{ }` block a property belongs to
- How blocks are nested inside other blocks (like `@media` containing `.card`)

### What regex does

Regex (regular expressions) is a **pattern matching tool**. It checks: "does this text match this pattern?" We have 150+ CSS features, each with its own regex pattern.

### Why not ONLY regex (no tinycss2)?

#### Problem 1: Comments vs real code

```css
body {
    /* color: red; */
    color: blue;
}
```

We want to find `color`. There are TWO `color` lines — one is inside a **comment** and one is real code.

With only regex, you might try to remove comments first by removing everything between `/*` and `*/`. But what about this:

```css
body {
    background-image: url("/* not a comment */");
    /* real comment */
    color: blue;
}
```

That `/* not a comment */` is inside a **string** (inside `url()`). It's NOT a real comment. But regex doesn't know the difference. It sees `/*` and `*/` and thinks it's a comment. It would delete part of the URL and break everything.

**tinycss2 knows the difference.** It understands that text inside `url("...")` is a string, not a comment.

#### Problem 2: Nested blocks

```css
@media (max-width: 768px) {
    .card {
        display: grid;
    }
}
```

With only regex, how do you know `display: grid` is INSIDE `@media`? Regex reads characters left to right. It doesn't understand that one `{ }` block is nested inside another `{ }` block.

**tinycss2 understands nesting.** It knows `.card` is inside `@media`, and `display: grid` is inside `.card`.

#### Problem 3: Same property, different context

```css
.flex-container {
    display: flex;
    gap: 20px;        /* This is FLEXBOX gap */
}

.grid-container {
    display: grid;
    gap: 20px;        /* This is GRID gap */
}
```

`gap` appears twice but means different things depending on what block it's in. With only regex, you can't tell which `gap` belongs to which block.

**tinycss2 tracks which block each property belongs to** (using something called `block_id` in our code), so we can tell them apart.

### Why not ONLY tinycss2 (no regex)?

tinycss2 breaks CSS into structured pieces. It tells us: "this property is `display`, this value is `grid`".

But we need to check **150+ features**. Without regex, we'd need 150+ `if` statements:

```python
# This would be terrible:
if property == 'display' and 'grid' in value:
    found.add('css-grid')
if property == 'display' and 'flex' in value:
    found.add('flexbox')
if 'oklch' in value:
    found.add('css-oklch')
if 'clamp' in value:
    found.add('css-clamp')
# ... 150 more if statements
```

Instead, we store patterns in a dictionary and let regex check them:

```python
'css-grid': {
    'patterns': [r'display\s*:\s*[^;]*\bgrid\b', r'\bgrid-template']
}
'flexbox': {
    'patterns': [r'display\s*:\s*[^;]*\bflex\b']
}
```

Regex is **perfect for pattern matching** — checking "does this text match this pattern?" across many patterns efficiently. That's literally what regex was invented for.

Also, some features need **flexible matching** that simple `if` statements can't do easily:

```css
/* All of these should detect CSS Grid: */
display: grid;
display: inline-grid;
grid-template-columns: 1fr 1fr;
grid-template-rows: auto;
grid-area: header;
```

One regex pattern `r'\bgrid-template'` catches both `grid-template-columns` and `grid-template-rows` and `grid-template-areas`. An `if` statement would need to list each one separately.

### How they work together

```
CSS text
   |
   v
tinycss2: "I'll understand the structure.
           I know what's a comment, what's a string,
           which block each property belongs to."
   |
   v
Clean, structured text pieces
   |
   v
Regex: "I'll check these clean pieces against
        150+ feature patterns efficiently."
   |
   v
Found features: {css-grid, flexbox, css-calc}
```

### Analogy

Think of it like cooking:
- **tinycss2** = washing and cutting vegetables (preparing clean ingredients)
- **regex** = the recipe (knowing what to look for in those ingredients)

You need both. Clean ingredients without a recipe = you don't know what to cook. A recipe without clean ingredients = you might accidentally cook the plastic wrapper along with the food.

---

## Part 2: JS Parser — Why tree-sitter + 3 Tiers?

### Why JavaScript is the hardest to parse

JavaScript is much more complex than HTML or CSS because:

1. **Same syntax, different meaning** — `entries()` could be `Object.entries()` (feature!) or `myArray.entries()` (different feature!) or `getEntries()` (not a feature at all)
2. **Features hidden in syntax** — optional chaining `?.`, nullish coalescing `??`, arrow functions `=>` are syntax, not names you can search for
3. **278 features to detect** — more than HTML (~100) and CSS (~150)
4. **Comments and strings are tricky** — template literals `` `hello ${code}` `` have real code INSIDE strings

### What tree-sitter does

tree-sitter is a library that **reads JavaScript and builds a tree** (called an AST — Abstract Syntax Tree). Every piece of code becomes a "node" in the tree with a **type** and sometimes a **name**.

For example:

```javascript
fetch("https://api.com")
```

tree-sitter builds:
```
call_expression          <-- type: "call_expression"
  ├── identifier: "fetch"    <-- name inside the node
  └── arguments
       └── string: "https://api.com"
```

### Why not ONLY regex (no tree-sitter)?

#### Problem 1: Comments and strings

```javascript
// This is real code (should detect):
const data = new Promise((resolve) => { resolve(42); });

// This is a COMMENT (should ignore):
// const old = new Promise((resolve) => { resolve(0); });

// This is a STRING (should ignore):
const message = "new Promise is cool";
```

With only regex, the pattern `new Promise` matches ALL THREE lines. But only the first one is real code!

You could try removing comments and strings with regex first. But JavaScript strings are tricky:

```javascript
const a = "it's a test";           // single quote inside double quotes
const b = 'he said "hello"';      // double quotes inside single quotes
const c = `template ${value}`;    // template literal with CODE inside it!
const d = /regex\/pattern/;       // regex literal with escaped slash
```

Writing regex to correctly handle ALL of these edge cases is extremely error-prone. **tree-sitter handles all of them perfectly** because it actually understands JavaScript grammar.

#### Problem 2: Same word, different meaning

```javascript
const entries = Object.entries(data);    // Object.entries API (feature!)
const entries = myList.entries();         // Array entries method (different!)
const entries = getEntries();            // Just a function you wrote (NOT a feature)
```

Regex sees `entries` in all three lines. It can't tell the difference.

tree-sitter knows:
- Line 1: the receiver is `Object` -> this is `Object.entries`
- Line 2: the receiver is `myList` -> this is a method on a variable
- Line 3: this is just a standalone function call

### The 3 Tiers — Why not just 1 tier?

Now we know tree-sitter builds a tree. But we still need to **search** that tree for features. We do this in 3 tiers, each catching what the previous one missed.

---

### Tier 1: AST Node Types (reading the label on the box)

Tier 1 looks at the **type** of each node in the tree. Just the type, nothing else.

```javascript
obj?.name        // tree-sitter type: "optional_chain"
x ?? y           // tree-sitter type: "binary_expression" with operator "??"
#secret          // tree-sitter type: "private_property_identifier"
```

`optional_chain` is a **unique** type. ONLY the optional chaining operator `?.` creates this type. So when Tier 1 sees `optional_chain`, it knows 100% — this is the optional chaining feature.

**But most features DON'T have unique types.** Look:

```javascript
fetch("url")           // type: call_expression
alert("hello")         // type: call_expression
console.log("test")    // type: call_expression
myFunction(42)         // type: call_expression
```

ALL function calls have the SAME type: `call_expression`. Tier 1 sees `call_expression` and has NO IDEA if it's `fetch` or `alert` or anything else. They all look identical from the outside.

**Analogy:** Imagine 100 boxes arrive at a warehouse. They ALL have the same label: "PACKAGE". Only 10 boxes have unique labels like "FRAGILE-GLASS". Tier 1 can only identify those 10 unique ones.

**Tier 1 catches: ~10 features** (only the ones with unique node types)

---

### Tier 2: AST Name Lookups (opening the box and reading what's inside)

Tier 2 says: "OK, I see a `call_expression`. Let me **read the actual name** inside it."

```javascript
fetch("https://api.com")
```

- Tier 1 sees: `call_expression` -> "could be anything, I can't tell" -> **skips it**
- Tier 2 sees: `call_expression` -> reads inside -> function name = `"fetch"` -> looks up `"fetch"` in our dictionary -> **found! It's the Fetch API!**

```javascript
alert("hello")
```

- Tier 1 sees: `call_expression` -> **skips it**
- Tier 2 sees: `call_expression` -> reads inside -> function name = `"alert"` -> looks up `"alert"` in dictionary -> **not in our feature dictionary, skip**

```javascript
new IntersectionObserver(callback)
```

- Tier 1 sees: `new_expression` -> **skips it**
- Tier 2 sees: `new_expression` -> reads inside -> class name = `"IntersectionObserver"` -> looks up in dictionary -> **found!**

**Analogy:** The warehouse worker opens each box and reads the product name inside. Then checks it against the inventory list. If the name is on the list, the box is marked.

**Tier 2 catches: ~200 features** (any feature whose name is in our dictionaries)

But Tier 2 can't catch everything...

---

### Why Tier 2 can't catch everything (why we need Tier 3)

#### Problem 1: Aliased / renamed variables

```javascript
const f = fetch;
f("https://api.com");
```

Tier 2 reads the function name: `"f"`. Looks up `"f"` in the dictionary. NOT found. Because the dictionary has `"fetch"`, not `"f"`. The developer renamed it.

But regex (Tier 3) scanning the clean text sees `const f = fetch` — the pattern `\bfetch\b` matches the word `fetch` on that line. **Caught!**

#### Problem 2: Custom rules from users

Users can add their own detection rules in `custom_rules.json`:

```json
{
  "javascript": {
    "some-feature": {
      "patterns": ["myCompanyAPI\\.track"],
      "description": "Company tracking API"
    }
  }
}
```

We have NO IDEA what patterns users will add. We can't put them in the AST dictionaries because those are pre-built for known features. Custom rules are **always regex patterns**. Only Tier 3 can run them.

#### Problem 3: Complex multi-word patterns

Some features need to match a **combination** of words:

```javascript
window.CSS.supports("display", "grid")
```

The AST maps work by looking up single names. But `supports` alone could mean anything. The regex `CSS\.supports` matches the specific combination, which is easier to express as a regex pattern than as a complex AST dictionary lookup.

#### Problem 4: ~70 features not in AST maps

We have ~278 total JS features. Tier 1 covers ~10, Tier 2 covers ~200. That leaves **~70 features** that simply aren't in the AST dictionaries. Some patterns are just easier to express as regex.

**Tier 3 catches: ~70+ remaining features plus all custom rules**

---

### The 3 Tiers Together

**Analogy: School attendance with 3 methods**

**Method 1 (Tier 1):** "Anyone wearing a unique uniform? Only band kids have red jackets."
-> Catches 10 students instantly. 100% accurate.

**Method 2 (Tier 2):** "Let me call names from my class list."
-> Catches 200 students. Very accurate.

**Method 3 (Tier 3):** "Let me walk through the room and check everyone I missed — kids who changed their name, new transfer students not on my list, kids sitting in the wrong section."
-> Catches the remaining 70.

Together they get (almost) everyone.

### How they work together (JS full flow)

```
JavaScript text
   |
   v
tree-sitter: "I'll parse this into a tree (AST).
              I understand comments, strings, code structure."
   |
   v
AST (tree of nodes, each with type + name)
   |
   ├── Tier 1: Check node TYPES
   |   "optional_chain found! That's optional chaining."
   |   -> catches ~10 features with unique node types
   |
   ├── Tier 2: Read node NAMES, look up in dictionary
   |   "call_expression contains 'fetch' -> that's the Fetch API!"
   |   -> catches ~200 features by name
   |
   ├── Also from tree-sitter: Build clean text
   |   (comments replaced with spaces, strings emptied)
   |
   └── Tier 3: Run regex on clean text
       "Pattern \bfetch\b matches! Pattern CSS\.supports matches!"
       -> catches ~70 remaining features + custom rules
   |
   v
All found features: {fetch, promises, optional-chaining, ...}
```

---

## Part 3: Comparing All Three Parsers

### Why HTML is simplest

HTML is the simplest language to parse. Elements have clear tags (`<dialog>`, `<video>`), attributes have clear names (`loading`, `draggable`), and there's no nesting ambiguity.

BeautifulSoup understands the structure (what's an element, what's an attribute). Simple dictionary lookups find the features (if element name is in the dictionary, it's a feature). No regex needed because HTML features are found by exact names, not patterns.

### Why CSS needs regex but HTML doesn't

CSS features are identified by **patterns**, not just exact names:

```css
/* All of these are CSS Grid: */
display: grid;
display: inline-grid;
grid-template-columns: 1fr 1fr;
grid-template-rows: auto;
grid-gap: 10px;
```

One regex `r'\bgrid-template'` catches `grid-template-columns`, `grid-template-rows`, AND `grid-template-areas`. You'd need separate dictionary entries for each without regex.

HTML features are identified by **exact names**: `<dialog>` is always just `dialog`. No patterns needed.

### Why JS needs 3 tiers but CSS needs only 1

CSS only has **one kind of thing** to look for: text patterns in declarations. So one tool (regex) for detection is enough.

JavaScript has **three different kinds of things** to look for:
1. **Syntax features** identified by node shape (optional chaining `?.`) -> Tier 1
2. **API features** identified by name (`fetch`, `Promise`) -> Tier 2
3. **Everything else** including custom rules -> Tier 3

Each tier is specialized for its kind of detection.

---

## Summary Table

| Question | HTML | CSS | JS |
|----------|------|-----|-----|
| **Structure tool** | BeautifulSoup | tinycss2 | tree-sitter |
| **Why need it?** | Understands HTML tags and attributes | Understands comments, strings, nested blocks | Understands comments, strings, code meaning |
| **Detection tool** | Dictionary lookups | Regex patterns | 3 tiers (AST types + AST names + regex) |
| **Why need it?** | Features are exact names | Features are 150+ text patterns | 278 features: some are syntax, some are names, some are patterns |
| **Why not only regex?** | Don't need it, names are exact | Can't tell comments from strings, can't track nesting | Can't tell comments from strings, can't tell `fetch` from `myFunc` |
| **Why not only structure tool?** | Actually HTML DOES use only lookups | Can't efficiently match 150+ patterns | Can't catch aliases, custom rules, complex patterns |

---

## The Universal Pattern

Every parser follows the same two-step pattern:

```
Step 1: UNDERSTAND the structure
        (What's a comment? What's a string? What's real code? What belongs where?)

Step 2: DETECT the features
        (Is this CSS Grid? Is this the Fetch API? Is this a dialog element?)
```

**Step 1 needs a parser library** (BeautifulSoup, tinycss2, tree-sitter) because these languages have complex syntax rules that are hard to handle correctly with simple text processing.

**Step 2 needs a detection method** (dictionary lookups, regex, AST lookups) because we have hundreds of features to check and each one has its own pattern.

Neither step can do the other's job:
- Parser libraries understand structure but don't know what features to look for
- Detection methods know what to look for but can't tell real code from comments/strings

**Together, they give us accurate feature detection.**
