# Cross Guard -- UML Class Diagram Explained

## What Is a UML Class Diagram?

A UML class diagram is a picture of your software's structure. It shows:
- **Classes** (the building blocks of your code)
- **Attributes** (data each class holds)
- **Methods** (actions each class can do)
- **Relationships** (how classes connect to each other)

---

## The 4 Arrow Types We Use

### 1. Composition ◆──── (Filled Diamond)
**"Owns it. Dies together."**

When class A creates class B inside itself, and B has no reason to exist without A. If A is destroyed, B is destroyed too.

**Example:** CrossGuardAnalyzer ◆── HTMLParser
- CrossGuardAnalyzer creates HTMLParser inside its `__init__`
- HTMLParser only exists inside the analyzer
- If the analyzer is destroyed, the parser goes with it
- Nobody else creates or uses that parser instance

### 2. Aggregation ◇──── (Hollow Diamond)
**"Contains it. But it can live on its own."**

When class A holds a collection of class B, but B has its own identity and can exist independently (like a database record).

**Example:** Analysis ◇── AnalysisFeature (1..*)
- An Analysis contains many AnalysisFeatures
- But each AnalysisFeature is its own row in the database with its own ID
- If the Analysis Python object is deleted, the database rows still exist
- The "1..*" means: one Analysis has one or more AnalysisFeatures

### 3. Dependency - - - -> (Dashed Arrow)
**"Uses it temporarily. No permanent link."**

When class A imports class B, calls one of its methods, and moves on. No permanent connection -- just a temporary interaction.

**Example:** AnalyzerService - - -> AIFixService
- AnalyzerService creates AIFixService inside one method
- Uses it to get fix suggestions
- Then it's done -- no permanent reference stored

### 4. Association ───── (Solid Line)
**"Knows about it permanently."**

When class A stores a reference to class B as a permanent attribute. The link exists for the entire lifetime of the object.

**Example:** Bookmark ── Analysis
- Bookmark has a field `analysis_id` that permanently points to an Analysis
- This isn't a temporary method call -- it's a structural data relationship
- The Bookmark always knows which Analysis it belongs to

---

## Quick Decision Guide

```
Does A create B inside __init__ and B can't exist without A?
  --> Composition ◆

Does A contain a list of B's, but B has its own ID / database row?
  --> Aggregation ◇

Does A store B as a permanent attribute (self._b = B)?
  --> Association ──

Does A only import/call B inside a method and forget about it?
  --> Dependency - ->
```

---

## Visibility Symbols

| Symbol | Meaning | Who can access it? |
|--------|---------|-------------------|
| `+` | Public | Anyone from anywhere |
| `-` | Private | Only the class itself |

**Example:**
```
+ parse_file(path) : Set[str]    <-- anyone can call this
- _reset_state()                  <-- only the class itself calls this
```

---

## Class Box Structure

Every class in the diagram has 3 sections:

```
+---------------------------+
|     <<stereotype>>        |   <-- optional label (facade, singleton, etc.)
|       ClassName           |   <-- the class name, bold
+---------------------------+
| - private_attr : Type     |   <-- attributes (data the class holds)
| + public_attr : Type      |
+---------------------------+
| + public_method() : Type  |   <-- methods (actions the class can do)
| - _private_method()       |
+---------------------------+
```

---

## The Complete Diagram Explained (Top to Bottom)

### Layer 1: Frontends (How users interact with the system)

**MainWindow** -- The desktop GUI application. Built with CustomTkinter. The user opens it, drags files in, clicks analyze, and sees results in a visual dashboard. It OWNS an ExportManager (composition) and DEPENDS on AnalyzerService to do all the real work.

**CLI** -- The command-line interface. Built with Click. Developers run commands like `crossguard analyze style.css`. It also DEPENDS on AnalyzerService and loads settings from ConfigManager.

**ExportManager** -- Handles exporting results to PDF and JSON. OWNED by MainWindow (composition -- it's created inside MainWindow and can't exist without it).

### Layer 2: Data Contracts (What goes in and what comes out)

**AnalysisRequest** -- The input. Contains which files to analyze (HTML, CSS, JS) and which browsers to target. The user fills this in, and it gets passed to AnalyzerService.

**AnalysisResult** -- The output. Contains everything about the analysis: success/failure, scores, browser compatibility data, detected features, recommendations, and any AI suggestions. This is what gets displayed in the GUI or exported as a report.

### Layer 3: Facade (The single entry point)

**AnalyzerService** -- The facade. This is the ONE class that both frontends talk to. It has 28 public methods covering: analysis, history, settings, bookmarks, tags, export, database updates, AI suggestions, polyfill recommendations, and configuration. It CREATES CrossGuardAnalyzer, DatabaseUpdater, and WebFeaturesManager when needed (lazy loading). It USES repositories, statistics service, AI service, and polyfill service.

### Layer 4: Orchestrator (Coordinates everything)

**CrossGuardAnalyzer** -- The brain. It OWNS (composition) all the core components:
- 3 parsers (HTMLParser, CSSParser, JavaScriptParser)
- CompatibilityAnalyzer (checks browser support)
- CompatibilityScorer (calculates scores)

When `run_analysis()` is called, it:
1. Sends files to the right parser
2. Collects all detected features
3. Checks compatibility against target browsers
4. Calculates scores
5. Generates a report

### Layer 4: Services (Support systems the facade uses)

**DatabaseUpdater** -- Downloads the latest Can I Use data from NPM Registry and updates the local copy.

**WebFeaturesManager** -- Checks Baseline status of features (widely available, newly available, or limited).

**ConfigManager** -- Loads settings from `crossguard.config.json`. Things like which browsers to target, output format, AI provider config.

**AIFixService** -- Calls OpenAI or Anthropic APIs to generate code fix suggestions for unsupported features.

**PolyfillService** -- Recommends npm polyfill packages for unsupported features. Permanently HOLDS a reference to PolyfillLoader (association).

**PolyfillLoader** -- Singleton that loads polyfill mapping data from `polyfill_map.json`. Caches the data so it's only loaded once.

### Layer 5: Parsers (Extract features from code)

**HTMLParser** -- Takes HTML code, finds elements like `<dialog>`, `<video>`, `<input type="date">` using BeautifulSoup. Returns a set of Can I Use feature IDs.

**CSSParser** -- Takes CSS code, finds properties like `display: grid`, `gap`, `backdrop-filter` using tinycss2 AST parsing. Returns feature IDs.

**JavaScriptParser** -- Takes JS code, finds APIs like `Promise`, `fetch()`, `async/await`, optional chaining `?.` using tree-sitter AST parsing. Returns feature IDs.

**CustomRulesLoader** -- Singleton that loads user-defined detection rules from `custom_rules.json`. All 3 parsers DEPEND on it to merge custom rules with built-in rules.

### Layer 5: Compatibility Engine (Check and score)

**CompatibilityAnalyzer** -- Takes a set of feature IDs and target browsers. For each feature + each browser, it QUERIES CanIUseDatabase to check: "Does Chrome 120 support css-grid?" Returns support data with severity ratings.

**CompatibilityScorer** -- Takes support data and calculates: a simple score (0-100 average), a weighted score (browsers weighted by importance), and a compatibility index with letter grade (A+ through F).

**CanIUseDatabase** -- Singleton that loads the Can I Use JSON data files into memory. Provides fast lookups: "Does browser X version Y support feature Z?" This is the core data source for the entire tool.

### Layer 6: Database Layer (Save and retrieve results)

**AnalysisRepository** -- Saves analysis results to SQLite and loads them back. CRUD operations: save, get all, get by ID, delete, clear, count.

**StatisticsService** -- Queries SQLite to compute aggregated stats: average score, best/worst scores, score trends over time, most problematic features, grade distribution.

### Layer 6: Data Models (What gets stored in the database)

**Analysis** -- One record per file analyzed. Stores: file name, type, score, grade, timestamp. CONTAINS (aggregation) a list of AnalysisFeatures.

**AnalysisFeature** -- One record per detected feature within an analysis. Stores: feature ID, name, category. CONTAINS (aggregation) a list of BrowserResults.

**BrowserResult** -- One record per browser per feature. Stores: browser name, version, support status (y/n/partial).

**Bookmark** -- A bookmarked analysis with an optional note. REFERENCES (association) an Analysis.

**Tag** -- A colored label for categorizing analyses. Has a many-to-many relationship with Analysis (0..*).

### External Systems (Outside the application)

**SQLite Database** (`crossguard.db`) -- Where all analysis history, bookmarks, tags, and settings are stored.

**Can I Use Data** (`data/caniuse/`) -- Local copy of the caniuse.com database. JSON files with browser support data for 500+ web features.

**LLM APIs** (OpenAI / Anthropic) -- External AI services called by AIFixService to generate code fix suggestions.

**NPM Registry** (registry.npmjs.org) -- Where DatabaseUpdater downloads the latest Can I Use data from.

---

## The Complete Flow in One Paragraph

User opens MainWindow (or runs CLI) and drops in some web files. The frontend calls AnalyzerService with an AnalysisRequest. The service creates CrossGuardAnalyzer, which sends HTML to HTMLParser, CSS to CSSParser, and JS to JavaScriptParser. Each parser extracts feature IDs (loading custom rules from CustomRulesLoader). The combined features go to CompatibilityAnalyzer, which queries CanIUseDatabase for each feature against each target browser. CompatibilityScorer calculates the final score and grade. The service wraps everything in an AnalysisResult, saves it to SQLite via AnalysisRepository, and returns it to the frontend. Optionally, AIFixService calls LLM APIs for fix suggestions, and PolyfillService recommends polyfill packages. The user sees their score, browses issues, bookmarks results, exports reports, and checks statistics over time.

---

## Where Each Arrow Type Is Used

### Composition ◆ (6 places)

| Whole | Part | Why? |
|-------|------|------|
| MainWindow | ExportManager | Created in `__init__`, can't exist without the window |
| CrossGuardAnalyzer | HTMLParser | Created in `__init__`, only lives inside the analyzer |
| CrossGuardAnalyzer | CSSParser | Same |
| CrossGuardAnalyzer | JavaScriptParser | Same |
| CrossGuardAnalyzer | CompatibilityAnalyzer | Same |
| CrossGuardAnalyzer | CompatibilityScorer | Same |

### Aggregation ◇ (2 places)

| Whole | Part | Multiplicity | Why? |
|-------|------|-------------|------|
| Analysis | AnalysisFeature | 1..* | Features are separate DB rows with own IDs |
| AnalysisFeature | BrowserResult | 1..* | Results are separate DB rows with own IDs |

### Dependency - -> (20 places)

All the "uses", "creates", "depends", "queries", "reads", "calls" arrows. These are temporary interactions -- one class imports/calls another but doesn't permanently hold a reference.

### Association ── (4 places)

| Class A | Class B | Why? |
|---------|---------|------|
| AnalysisRepository | Analysis | Repository's entire purpose is managing Analysis objects |
| Bookmark | Analysis | Bookmark permanently holds `analysis_id` reference |
| Analysis | Tag | Permanent many-to-many data relationship |
| PolyfillService | PolyfillLoader | Service permanently stores `self._loader` attribute |
