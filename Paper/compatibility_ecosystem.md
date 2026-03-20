# The Browser Compatibility Data Ecosystem

> Compiled: 2026-03-20
> Purpose: TDK paper background — understanding the full landscape of tools and data sources

---

## The Data Flow (Use This Diagram in Your Paper)

```
RAW DATA SOURCES
  QuirksMode.org (1999, retired) — first compat tables by PPK
  kangax/compat-table (2010) — JS language feature tests
  WPT / wpt.fyi (2010) — 56,552 conformance tests
  Chrome UseCounters — real-world CSS/JS/HTML usage %
  StatCounter (2000) — browser market share
  HTTP Archive (2010) — feature adoption across 16M sites
  Browser vendor status pages (Chrome, Firefox, WebKit, Edge)

                    ↓

PRIMARY DATABASES
  Can I Use (2010, Alexis Deveria) — ~500 curated features
  MDN BCD (2017, Mozilla) — 19,221+ granular features
  web-features/Baseline (2022, W3C WebDX) — 1,006 higher-level features

                    ↓

DISTRIBUTION / PACKAGING
  caniuse-lite (compact caniuse for npm)
  Browserslist (shared browser targeting config)
  electron-to-chromium (Electron→Chrome mapping)

                    ↓

CONSUMER TOOLS — Static Analysis
  ★ CrossGuard (HTML+CSS+JS, caniuse, scoring, CI/CD)
  eslint-plugin-compat (JS only, BCD data)
  doiuse (CSS only, caniuse, unmaintained)
  stylelint-browser-compat (CSS only, BCD data)
  Autoprefixer (CSS prefix automation, caniuse)
  Babel preset-env (JS transpilation, kangax+core-js)
  webhint (multi-quality linting, BCD data)

CONSUMER TOOLS — Runtime Detection
  Modernizr (in-browser feature detection, 2009)
  HTML5Test (browser scoring, 2010, retired)
  CSS3Test/BrowserScore (CSS scoring, 2012)

CONSUMER TOOLS — Cloud Browser Testing
  BrowserStack (2011), Sauce Labs (2008), LambdaTest (2017)

META-DASHBOARDS
  webstatus.dev (Google, aggregates BCD+WPT+usage)
  Web Almanac (annual state of the web report)
```

---

## Primary Databases (Most Important for Your Paper)

### 1. Can I Use (caniuse.com)

- **Created by:** Alexis Deveria (@Fyrd)
- **When:** ~2009-2010
- **URL:** https://caniuse.com | https://github.com/Fyrd/caniuse
- **What it tracks:** HTML, CSS, JS, SVG web platform features — ~500 curated feature tables
- **Since 2019 MDN collaboration:** surfaces ~10,500 tables total (original + MDN BCD data)
- **License:** CC BY 4.0
- **Still maintained?** Yes, actively. Funded via Patreon.
- **CrossGuard uses this** as its primary compatibility database (`data/caniuse/data.json`, 571 features loaded)

### 2. MDN Browser Compatibility Data (BCD)

- **Created by:** Mozilla / MDN Web Docs team (led by Florian Scholz)
- **When:** 2017
- **URL:** https://github.com/mdn/browser-compat-data | npm: `@mdn/browser-compat-data`
- **What it tracks:** Web APIs, JS features, CSS properties, HTML elements, HTTP headers, MathML, SVG, WebExtensions — extremely granular (individual methods, properties, sub-features)
- **Data points:** 19,221+ features, 558,000+ weekly npm downloads
- **Still maintained?** Yes, very actively. 5 maintainers, community-contributed.
- **Relation to Can I Use:** In 2019, caniuse integrated BCD data, expanding from ~500 to ~10,500 visible tables. BCD is far more granular.
- **Used by:** eslint-plugin-compat, webhint, stylelint-browser-compat, VS Code, Firefox DevTools, TypeScript

### 3. Web-Features / Baseline (W3C WebDX Community Group)

- **Created by:** W3C WebDX — collaboration of Google, Apple, Mozilla, Microsoft, Igalia
- **When:** 2022 (first complete catalog February 2025)
- **URL:** https://github.com/web-platform-dx/web-features | https://web.dev/baseline
- **What it tracks:** 1,006 higher-level "web features" with Baseline status:
  - **Newly Available:** All core browsers ship it
  - **Widely Available:** 30 months after Newly Available
  - **Discouraged:** Added December 2024
- **CrossGuard already integrates** Baseline data in its reports (`baseline_summary` in analysis output)

---

## The Historical Timeline (For Your Paper's Background Section)

| Year | Event | Significance |
|------|-------|-------------|
| 1999 | **QuirksMode.org** launched (PPK) | First browser compat tables. Hand-tested. "MDN and caniuse rolled into one" in its era |
| 2008 | **Sauce Labs** founded (Jason Huggins, creator of Selenium) | First cloud cross-browser testing platform |
| 2009 | **Modernizr** launched (Faruk Ates) | Runtime feature detection in browser. Won .net Award 2010 & 2011 |
| 2010 | **Can I Use** launched (Alexis Deveria) | The definitive browser compatibility reference. ~500 curated features |
| 2010 | **HTML5Test** launched (Niels Leenheer) | Browser scoring out of 555 points — predecessor to CrossGuard's 0-100 scoring |
| 2010 | **Web Platform Tests (WPT)** founded | Conformance test suite, now 56,552+ tests |
| 2010 | **kangax ECMAScript compat table** | JS language feature support across browsers and runtimes |
| 2011 | **BrowserStack** founded | Cloud-based real device/browser testing |
| 2012 | **CSS3Test** launched (Lea Verou) | Runtime CSS feature scoring |
| ~2013 | **Autoprefixer** created (Andrey Sitnik) | First tool to consume caniuse data programmatically for CSS prefixing |
| ~2014 | **doiuse** created (Anand Thakker) | First CSS linter using caniuse data — closest predecessor to CrossGuard |
| ~2015 | **eslint-plugin-compat** created (Amila Welihinda) | JS API linting using BCD data |
| 2016 | **HTML5Test retired** | Server went down, no incentive to continue |
| 2017 | **MDN BCD** launched (Mozilla) | 19,221+ granular features, open source. Game-changer for the ecosystem |
| 2017 | **Browserslist 2.0** (Andrey Sitnik) | Shared browser targeting config, used by caniuse-lite, Autoprefixer, Babel |
| 2019 | **Can I Use + MDN BCD collaboration** | caniuse surfaces 10,500+ tables by integrating BCD data |
| 2019 | **webhint v1** (Microsoft) | Multi-quality web linter using BCD. Built into Edge DevTools |
| 2022 | **Interop project** launched | Apple, Google, Mozilla, Microsoft collaborate on browser interop. Score: 49%→83% |
| 2022 | **web-features/Baseline** project started | W3C WebDX group defines "Newly Available" and "Widely Available" statuses |
| 2024 | **webstatus.dev** (Google) | Meta-dashboard aggregating BCD + WPT + usage data |
| 2024 | **Interop 2024** achieves 95% | Browser vendors closing compat gaps |
| 2024 | **Baseline 2024** adds "Discouraged" status | Feature lifecycle tracking matures |
| 2024 | **polyfill.io compromised** | Supply chain attack injected malware into 100,000+ sites. Cautionary tale for polyfill CDNs |
| 2025 | **Interop 2025** reaches 97% | 19 focus areas, experimental browsers at 99% |
| 2025 | **web-features catalog completed** | 1,006 features mapped |
| 2026 | **CrossGuard** | Fills the gap: first tool combining static analysis + multi-language + scoring + CI/CD |

---

## Who Uses What Data Source

| Tool | Data Source | Languages | Approach |
|------|-----------|-----------|----------|
| **CrossGuard** | **Can I Use** | HTML + CSS + JS | Static analysis, scoring, CI/CD |
| doiuse | Can I Use | CSS only | CSS linting (unmaintained) |
| Autoprefixer | Can I Use (via caniuse-lite) | CSS only | Adds vendor prefixes |
| eslint-plugin-compat | MDN BCD | JS only | ESLint plugin |
| stylelint-browser-compat | MDN BCD | CSS only | Stylelint plugin |
| webhint | MDN BCD | Multi | DevTools/runtime linter |
| Babel preset-env | kangax + core-js | JS only | Transpilation |
| Browserslist | Can I Use + StatCounter | Config only | Browser target queries |
| Modernizr | Runtime tests | JS (runtime) | Feature detection |
| BrowserStack/Sauce Labs | Real browsers | All | Cloud runtime testing |

---

## Key People in the Ecosystem

| Person | Role | Contribution |
|--------|------|-------------|
| **Alexis Deveria** (@Fyrd) | Creator of Can I Use | Built and maintains the primary compat reference since 2010 |
| **Florian Scholz** | Led MDN BCD | Created the 19,221+ feature database at Mozilla |
| **Andrey Sitnik** | Created Browserslist, Autoprefixer, PostCSS | Built the infrastructure layer (caniuse-lite, browser targeting) |
| **Peter-Paul Koch** (PPK) | Created QuirksMode.org | Pioneer — first compat tables (1999), predecessor to everything |
| **Juriy Zaytsev** (kangax) | Created ECMAScript compat table | Definitive JS language feature testing |
| **Denis Pushkarev** (zloirock) | Created core-js | Polyfill library + compat data, used by Babel |
| **Lea Verou** | Created CSS3Test | CSS feature testing in browsers |
| **Niels Leenheer** | Created HTML5Test | Browser scoring (predecessor to CrossGuard's scoring) |
| **Faruk Ates** | Created Modernizr | Runtime feature detection (2009) |
| **Anand Thakker** | Created doiuse | Closest predecessor to CrossGuard's CSS analysis |
| **Amila Welihinda** | Created eslint-plugin-compat | JS compat linting via ESLint |

---

## Why This Matters for Your TDK Paper

### The narrative:

1. **QuirksMode (1999)** proved developers need compat data → manual, one-person effort
2. **Can I Use (2010)** made it accessible → curated database, community contributions
3. **MDN BCD (2017)** made it granular → 19,221+ features, machine-readable
4. **Baseline (2022)** made it actionable → clear "supported/not supported" signals
5. **Interop (2022-2025)** made vendors collaborate → 97% interop achieved
6. **BUT:** No tool combines all this into a single static analysis pipeline with scoring and CI/CD
7. **CrossGuard (2026)** fills this gap → AST parsing + Can I Use + scoring + 6 export formats

### What to cite:
- Can I Use: Deveria, A. (2010). caniuse.com
- MDN BCD: Mozilla (2017). mdn/browser-compat-data. GitHub.
- Baseline: W3C WebDX Community Group (2022). web-features. GitHub.
- Interop: Apple, Google, Mozilla, Microsoft (2022-2025). Interop Project. web-platform-tests.
- The 2019 collaboration: Mozilla Hacks blog post
