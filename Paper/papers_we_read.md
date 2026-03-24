# Papers We Read for the TDK Paper

> Summary of all papers analyzed for the CrossGuard TDK State of the Art section.
> Ordered chronologically from earliest to latest.
> Date: 2026-03-24

---

## Paper 1: Automated Cross-Browser Compatibility Testing (2011)

- **Authors:** Ali Mesbah, Mukul R. Prasad
- **Year:** 2011
- **Venue:** ICSE 2011 (33rd International Conference on Software Engineering)
- **Link:** https://dl.acm.org/doi/10.1145/1985793.1985870

### What They Did
Formally defined cross-browser compatibility as a **functional consistency** problem. Built CrossT, a tool that automatically crawls web apps in different browsers (IE 8, Firefox 3.5, Chrome 4.1), captures behavior as **finite-state machines**, and compares them pairwise.

### How It Works
1. Crawl a running web app in multiple browsers using Crawljax
2. Capture each browser's navigation model as an FSM (states = screens, transitions = user actions)
3. **Trace-level comparison**: Check if state graphs are isomorphic (linear time algorithm)
4. **Screen-level comparison**: Compare DOM trees of matched states using XMLUnit

### Results
| Case | States | Trace Mismatches | Screen FP Rate |
|------|--------|-----------------|----------------|
| Organizer | 13-14 | 7 (0 FP) | 33% |
| Ind-v1 | 100 | 0 | 18% |
| Ind-v2 | 200 | 7 (2 FP) | 37% |
| Tmms | 24-31 | 14 (0 FP) | 13% |
| CNN | 100 | 16 (0 FP) | 12% |

### Limitations
- **Dynamic approach** -- needs a running, deployed web application
- **Needs real browsers** installed
- Screen-level false positive rate 12-37%
- No CSS property analysis
- Cannot be used pre-deployment
- Crawl depth limits completeness

### Why It Matters for CrossGuard
This is the **seminal paper** that formally defined the CBC problem. CrossGuard takes the opposite approach: static analysis of source files vs. dynamic crawling of running apps. Mesbah's approach finds behavioral differences; CrossGuard finds feature-level compatibility issues before deployment.

### Key Quote for TDK
> "Mesbah and Prasad [2011] pioneered automated cross-browser compatibility testing as a functional consistency problem using dynamic crawling and finite-state machine comparison. However, their approach requires a deployed web application and real browser environments. CrossGuard takes a complementary static analysis approach that operates directly on source files, enabling developers to detect compatibility issues before deployment."

---

## Paper 2: Static Analysis Technique of Cross-Browser Compatibility Detecting (2015)

- **Authors:** Sujuan Xu, Hongwei Zeng
- **Year:** 2015
- **Venue:** IEEE 3rd International Conference on Applied Computing and Information Technology
- **Link:** https://ieeexplore.ieee.org/document/7336041/

### What They Did
Built a database of HTML5 incompatible features for three browsers (IE 11, Chrome 39, Firefox 35) using the HTML5 TEST website. Then used regex to scan HTML source code and report which features are unsupported.

### How It Works
1. Visit html5test.com with each browser to find unsupported HTML5 features
2. Store unsupported elements and attributes in database tables
3. Use regular expressions to scan target HTML source code
4. Output a report listing incompatible features with line numbers

### Limitations
- **HTML only** -- no CSS, no JavaScript
- **Regex only** -- no AST parsing, prone to false positives
- **Manual database** -- built by hand from HTML5 TEST website, not automated
- **Tested on one example page** -- no real evaluation
- Only 3 browsers tested

### Why It Matters for CrossGuard
This is CrossGuard's **direct predecessor** -- the first paper to propose static source code analysis against a compatibility database. CrossGuard extends this massively: HTML + CSS + JS, AST parsing (tinycss2, tree-sitter), Can I Use database (not HTML5 TEST), 0-100 scoring, CI/CD integration, GUI, polyfill suggestions.

### Key Quote for TDK
> "Xu and Zeng [2015] proposed the first static analysis approach for cross-browser compatibility detection, scanning HTML source code with regular expressions against a manually built database. CrossGuard extends this paradigm to all three web languages with AST-based parsing, automated Can I Use data, quantitative scoring, and CI/CD integration."

---

## Paper 3: Improved Developer Support for the Detection of Cross-Browser Incompatibilities -- wIDE (2017)

- **Authors:** Alfonso Murolo, Fabian Stutz, Maria Husmann, Moira C. Norrie
- **Year:** 2017
- **Venue:** ICWE 2017 (Web Engineering), Lecture Notes in Computer Science vol. 10360, Springer
- **Link:** https://link.springer.com/chapter/10.1007/978-3-319-60131-1_15

### What They Did
Built wIDE, an **IntelliJ IDEA plugin** that checks HTML, CSS, and JavaScript code for browser compatibility using Can I Use data, and shows MDN documentation inside the IDE.

### How It Works
1. Defines **Elements of Interest (EOI)** per language:
   - HTML: tags (central), attributes (satellite)
   - CSS: properties (central), values (satellite) -- **skips selectors and pseudo-selectors**
   - JS: built-in functions (central), built-in objects (satellite) -- **skips keywords/blocks**
2. Uses IntelliJ's **PSI tree** (Program Structure Interface) to parse code
3. Sends EOIs to a **server** that queries Can I Use API and MDN
4. Server caches results in **MySQL** (7-day expiration)
5. Shows compatibility report with color-coded browser bars

### Their Scoring Formula (Per-Feature Only)
- If any browser doesn't support: `Cs = 0.45 * (supported + partial + prefixed) / total` (max 0.45)
- If all support but some partial: `Cs = 0.5 + 0.45 * (fully_supported / total)` (0.5 to 0.95)
- If all fully support: `Cs = 1.0`
- **No overall file score or letter grade**

### User Study (9 participants)
- All said info was "relevant or very relevant"
- Users requested: automatic background scans, polyfill suggestions, alternative solutions
- wIDE does NOT provide polyfills
- Many struggled with auto-complete based lookup

### Limitations
- **IntelliJ only** -- tied to one IDE
- **Needs server + internet** -- client-server architecture, queries Can I Use API online
- **Skips CSS selectors** entirely
- **No overall score** -- per-feature only
- **No CI/CD integration**
- **No export formats**
- **No polyfill suggestions** (users requested this)
- **No custom rules**
- **No analysis history**

### Why It Matters for CrossGuard
wIDE is the **closest existing academic tool** to CrossGuard. Both use Can I Use data for static source-level analysis. But CrossGuard is standalone, offline, has scoring, CI/CD, polyfills, custom rules, and history.

### Key Quote for TDK
> "wIDE [Murolo et al., 2017] is the most closely related academic work, sharing CrossGuard's use of Can I Use data for static source-level compatibility analysis. However, wIDE is bound to IntelliJ IDEA, requires a server with internet access, excludes CSS selectors from analysis, provides only per-feature scores without an overall compatibility metric, and lacks CI/CD integration, polyfill recommendations, and custom detection rules -- all of which CrossGuard provides."

---

## Paper 4: A Systematic Literature Review in Cross-browser Testing (2018)

- **Authors:** Leandro N. Sabaren, Maximiliano A. Mascheroni, Cristina L. Greiner, Emanuel Irrazabal
- **Year:** 2018
- **Venue:** Journal of Computer Science and Technology (JCS&T), vol. 18, no. 1
- **Link:** https://www.redalyc.org/journal/6380/638067784001/638067784001.pdf

### What They Did
Systematic literature review (SLR) of **31 papers** (2010-2017) about cross-browser testing. Categorized all techniques, tools, validation methods, and challenges.

### Key Finding: Technique Distribution
| Technique | Papers | % |
|-----------|--------|---|
| **Visual analysis** (screenshots) | 16 | **51.6%** |
| DOM model analysis | 11 | 35.4% |
| Navigation model analysis | 8 | 25.8% |
| Record/replay | 3 | 9.6% |
| **Static analysis** | **1** | **3.2%** |
| Attribute comparison | 2 | 6.4% |
| Heuristic evaluation | 1 | 3.2% |

**Only 1 out of 31 papers used static analysis** -- that was Xu & Zeng (2015).

### Tools
- 54.8% of papers proposed their own custom tools
- **None of the developed tools used static analysis**
- 6 commercial tools became obsolete or unsupported

### Challenges Found
1. **Variable element detection** -- biggest challenge (ads, carousels, animations)
2. **False positives** -- affects all techniques
3. **Triggering state changes** -- hard for navigation models
4. **Interactive elements** -- JavaScript/Web 2.0 makes things dynamic
5. **Need for automation** -- manual testing too costly
6. **Unreachable states** -- crawlers can't reach everything

### Why It Matters for CrossGuard
This is **gold for the TDK**. It proves:
1. Only 3.2% of research used static analysis -- CrossGuard fills a massive gap
2. Most tools are dynamic -- they need running websites and real browsers
3. The challenges they list (variable elements, unreachable states, triggering state changes) **don't apply to static analysis at all**

### Key Quote for TDK
> "A systematic literature review by Sabaren et al. [2018] examined 31 primary studies on cross-browser testing and found that visual analysis (51.6%) and DOM model analysis (35.4%) dominate the field, while only a single study (3.2%) employed static source code analysis. This significant gap in the research landscape motivates CrossGuard's static analysis approach, which avoids the challenges identified in the review -- variable element detection, false positives from dynamic content, and the need for running browser environments."

---

## Paper 5: A Large-Scale Study of Usability Criteria Addressed by Static Analysis Tools (2022)

- **Authors:** Marcus Nachtigall, Michael Schlichtig, Eric Bodden
- **Year:** 2022
- **Venue:** ISSTA 2022 (31st ACM SIGSOFT International Symposium on Software Testing and Analysis)
- **Link:** https://dl.acm.org/doi/10.1145/3533767.3534374 / https://www.bodden.de/pubs/nsb22large.pdf

### What They Did
Evaluated **46 static analysis tools** against **36 usability criteria** derived from scientific literature. First large-scale usability assessment of static analysis tools.

### The 46 Tools They Evaluated

**CLI Tools (22):** Bandit, Cpplint, CScout, Dlint, Flawfinder, Hegel, InferSharp, McCabe, NodeJSScan, Dependency Check, Pycodestyle, Pydocstyle, Pyflakes, Pyre-Check, Pytype, Radon, Semgrep, Vulture, Wemake-Python-Style, Wily, Xenon, Xo

**GUI Tools (24):** Checkstyle, CogniCrypt, one Commercial Tool, CppCheck, DevSkim, ErrorProne, ESLint, Fb-Contrib, FindSecurityBugs, Standard, Mypy, PMD, Puma Scan, PyDev, Pylint, Pyright, Reshift, Roslynator, Security Code Scan, SonarLint, SonarQube, SpotBugs, VisualCodeGrepper, VSDiagnostics

**None of these 46 tools check browser compatibility.** They check bugs, security, code style, complexity, and types.

### Their 6 Categories and Findings
| Category | Finding |
|----------|---------|
| **Warning Messages** | 30 of 46 tools have poor warnings |
| **Fix Support** | 37 of 46 give almost no fix support |
| **False Positives** | 31 tools are weak at handling false positives |
| **User Feedback** | Custom rules exist in some tools, but user knowledge is neglected |
| **Workflow Integration** | 22 tools are CLI-only (problematic); only 2 stand out positively |
| **User Interface** | Only 3 tools have good UI; progress tracking in only 2 tools |

### Most Important Numbers
- **More than half** of tools have poor warning messages
- **Three-quarters (75%)** provide hardly any fix support
- Only **3 out of 46** tools give good warning messages
- Only **3 out of 46** tools give sufficient fix support
- Only **10 tools** offer quick fixes
- Only **2 tools** track progress over time
- **CLI tools are worse in every single category** than GUI tools

### How CrossGuard Addresses Every Problem They Found
| Their Problem | CrossGuard's Solution |
|--------------|----------------------|
| Poor warning messages | Exact feature name, browser, version, support status |
| No fix support | Polyfill recommendations for every unsupported feature |
| No false positive handling | Custom rules (JSON + GUI editor) to add/edit/delete |
| CLI tools lack usability | Both GUI and CLI -- developer chooses |
| No workflow integration | 6 export formats + CI/CD quality gates |
| No dashboard/overview | Score cards, browser cards, issue cards, statistics panel |
| No progress tracking | Analysis history with SQLite, trends, aggregated stats |
| No search through warnings | Searchable history, filterable by type, score, tags |
| No severity classification | 0-100 score + A+ to F grade + per-feature severity |

### Why It Matters for CrossGuard
Not about browser compatibility, but incredibly powerful. Lets you argue: "The static analysis community has a known usability problem. We designed CrossGuard to address the shortcomings that Nachtigall et al. identified across 46 tools."

### Key Quote for TDK
> "Nachtigall et al. [2022] evaluated 46 static analysis tools at ISSTA and found that more than half provide poor warning messages, three-quarters offer no fix support, and CLI-only tools perform worse across all usability criteria. CrossGuard was designed with these findings in mind, providing descriptive per-feature compatibility reports, polyfill recommendations, a dual GUI and CLI architecture, analysis history with progress tracking, and six CI/CD-compatible export formats."

---

## Paper 6: XBIDetective: Leveraging Vision Language Models for Identifying Cross-Browser Visual Inconsistencies (2025)

- **Authors:** Balreet Grewal, Marco Castelluccio, Suhaib Mujahid, Jeff Muizelaar, James Graham, Jan Honza Odvarko, Cor-Paul Bezemer
- **Year:** 2025
- **Venue:** ICSE-SEIP 2026 (submitted), arXiv:2512.15804
- **Link:** https://arxiv.org/html/2512.15804v1

### What They Did
Built XBIDetective, a tool from **Mozilla Corporation + University of Alberta** that takes screenshots of websites in Firefox and Chrome, then uses Google Gemini 2.0 Flash (a Vision Language Model) to identify visual cross-browser inconsistencies.

### How It Works (3-Stage Pipeline)
1. **Stage 1 -- Ad detection**: Ask VLM to identify advertisements (so they don't get flagged as XBIs)
2. **Stage 2 -- Dynamic element detection**: Ask VLM to identify carousels, videos, live content
3. **Stage 3 -- XBI detection**: Ask VLM to compare screenshots, ignoring ads and dynamic elements, classify as minor-visual, significant-visual, or blocked-unsupported

### Results
| VLM Version | Accuracy | Precision | Recall |
|-------------|----------|-----------|--------|
| Base (Gemini 2.0 Flash) | 42% | 57% | 54% |
| Thinking (Gemini 2.0 Flash Thinking) | 77% | 69% | 48% |
| **Fine-tuned** | **79%** | **72%** | **59%** |

- Tested on 1,052 bug reports from Mozilla Bugzilla and WebCompat
- Fine-tuned on just 88 examples
- Large-scale run on 1,695 websites

### Limitations
- **Needs deployed websites** -- cannot analyze source code
- **Needs Selenium + real browsers** running in headless mode
- **79% accuracy** -- 21% wrong (AI hallucinations)
- **Misses pop-ups** (31 false negatives from pop-ups alone)
- **Cannot identify root cause** -- says "something looks different" but NOT which feature caused it
- **Blocked by bot detectors** -- many websites blocked Selenium
- **Expensive** -- needs Google Gemini API calls for every website
- **No overall compatibility score**

### Why It Matters for CrossGuard
This is the **absolute latest research** (Dec 2025, ICSE 2026). It's from Mozilla -- industry research, not just academic. Shows the field is moving toward AI, but still dynamic/visual. CrossGuard's static approach is fundamentally different and complementary -- it identifies exact features, works offline, and is deterministic.

### Key Quote for TDK
> "The most recent work, XBIDetective [Grewal et al., 2025], applies vision language models to compare browser screenshots, achieving 79% accuracy. However, this approach requires deployed websites, cannot identify specific source code features causing incompatibilities, and depends on costly cloud AI services. CrossGuard analyzes source code directly, providing deterministic results, identifying exact features and their support status, and operating entirely offline within CI/CD pipelines."

---

## Additional Papers Worth Citing (One Sentence Each, No Full Read Needed)

### Snyder et al. -- Browser Feature Usage on the Modern Web (2016)
- **Venue:** ACM Internet Measurement Conference (IMC 2016)
- **Link:** https://dl.acm.org/doi/10.1145/2987443.2987466
- **Citation:** "Snyder et al. [2016] found that over 50% of browser-provided JavaScript features are never used on the web's 10,000 most popular sites, demonstrating the uneven feature adoption landscape that creates cross-browser compatibility risks."

### Vassallo et al. -- How Developers Engage with Static Analysis Tools (2020)
- **Venue:** Empirical Software Engineering, Springer, Vol. 25
- **Link:** https://link.springer.com/article/10.1007/s10664-019-09750-5
- **Citation:** "Vassallo et al. [2020] found that 71% of developers pay attention to different warning categories depending on context, motivating CrossGuard's dual GUI (for interactive exploration) and CLI (for automated CI/CD pipelines) architecture."

### Static Analysis at GitHub (2021)
- **Venue:** ACM Queue / Communications of the ACM
- **Link:** https://dl.acm.org/doi/fullHtml/10.1145/3487019.3487022
- **Citation:** "GitHub's static analysis infrastructure is built on tree-sitter, used for code navigation and security analysis across 6 million repositories [GitHub Engineering, 2021], validating CrossGuard's use of tree-sitter for JavaScript feature detection."

---

## The Complete Story for the State of the Art

### Timeline of Approaches

| Era | Approach | Representative Work |
|-----|----------|-------------------|
| 2010-2013 | Dynamic: crawl + compare DOM/screenshots | Mesbah (2011), WebDiff (2010), X-PERT (2013) |
| 2015-2017 | Static: check source code against DB | Xu & Zeng (2015), wIDE (2017) |
| 2019-2025 | AI/ML: vision models + screenshots | XBIDetective (2025) |
| **2026** | **Static + AST + CI/CD + scoring** | **CrossGuard** |

### The Argument

1. **The problem exists and persists** (Mesbah 2011, Sabaren 2018)
2. **Most solutions are dynamic/visual** -- 51.6% visual, 35.4% DOM analysis (Sabaren 2018)
3. **Only 3.2% of research used static analysis** (Sabaren 2018)
4. **The one static analysis paper was very limited** -- HTML only, regex only (Xu & Zeng 2015)
5. **The closest tool (wIDE) is IDE-dependent, needs internet, no scoring, no CI/CD** (Murolo 2017)
6. **Even the latest AI approach needs deployed sites and has 79% accuracy** (XBIDetective 2025)
7. **Static analysis tools in general have poor usability** -- 75% no fix support (Nachtigall 2022)
8. **CrossGuard fills ALL of these gaps**: static analysis + AST parsing + all 3 languages + scoring + CI/CD + polyfills + GUI + offline + custom rules + history

### Total Citations: ~10
- 6 core papers (fully read and understood)
- 3 support papers (cited with one sentence)
- Perfect for a TDK paper
