# CrossGuard — Literature Review & Scientific Papers

> Compiled: 2026-03-11
> Purpose: TDK paper "State of the Art" section and theoretical foundations
> Total papers found: 48 (deduplicated across 3 research sweeps)

---

## How to Use This Document

- **TIER 1 (Must Cite):** Core problem domain — judges expect these
- **TIER 2 (Strongly Recommended):** Theoretical foundations — what your supervisor asked for
- **TIER 3 (Recommended):** Supporting context for specific sections
- **TIER 4 (Optional):** Extra depth if needed
- **For a 10-20 page TDK paper, cite 15-20 papers**

---

## TIER 1 — MUST CITE (Core Problem Domain)

These papers are about the exact same problem CrossGuard solves. Judges will expect to see these.

---

### 1. Static Analysis Technique of Cross-Browser Compatibility Detecting

- **Authors:** Sujuan Xu, Hong-wei Zeng
- **Year:** 2015
- **Published:** IEEE 3rd International Conference on Applied Computing and Information Technology / 2nd International Conference on Computational Science and Intelligence, pp. 103-107
- **URL:** https://ieeexplore.ieee.org/document/7336041/
- **Summary:** Proposes a static analysis technique for detecting cross-browser compatibility problems. Builds a database of HTML5 incompatible features linked to browsers, then uses regex-based detection to find incompatibilities in source code and generates reports with code locations.
- **Why it's critical:** **THE most directly relevant paper.** Uses the exact same paradigm as CrossGuard — static source code analysis against a compatibility database. CrossGuard extends this approach significantly with:
  - AST-based parsing (tinycss2, tree-sitter) instead of regex-only
  - CSS and JavaScript support (not just HTML)
  - Quantitative scoring (0-100 with letter grades)
  - CI/CD integration with 6 export formats
  - Desktop GUI
  - Polyfill recommendations
- **Cite in:** Introduction, State of the Art, Comparison section

---

### 2. Automated Cross-Browser Compatibility Testing

- **Authors:** Ali Mesbah, Mukul R. Prasad
- **Year:** 2011
- **Published:** ICSE 2011 (33rd International Conference on Software Engineering), pp. 561-570
- **URL:** https://dl.acm.org/doi/10.1145/1985793.1985870
- **Summary:** The foundational paper in automated cross-browser testing. Poses the problem as a "functional consistency" check across browsers. Automatically analyzes web applications under different browser environments, captures behavior as finite-state machines, and formally compares them pairwise to expose discrepancies.
- **Why it's critical:** **THE seminal paper** that formally defines the cross-browser compatibility problem. CrossGuard takes a fundamentally different (static) approach to the same problem — comparing feature support via Can I Use data rather than runtime behavioral comparison.
- **Cite in:** Introduction (problem definition), State of the Art

---

### 3. Improved Developer Support for the Detection of Cross-Browser Incompatibilities (wIDE)

- **Authors:** Murolo, A., Stutz, F., Husmann, M., Norrie, M.C.
- **Year:** 2017
- **Published:** ICWE 2017 (Web Engineering), Lecture Notes in Computer Science vol. 10360, Springer
- **URL:** https://link.springer.com/chapter/10.1007/978-3-319-60131-1_15
- **Summary:** Presents wIDE, an IDE extension that detects cross-browser incompatibilities (XBIs) in CSS, JavaScript, and HTML as code is written. Uses a compatibility knowledge base automatically extracted from online resources (like Can I Use) and periodically updated.
- **Why it's critical:** wIDE is the closest academic tool to CrossGuard. Both use compatibility knowledge bases derived from Can I Use to perform source-code-level compatibility checking. CrossGuard differentiates with AST-based parsing, scoring/grading, standalone operation, and CI/CD output formats.
- **Cite in:** State of the Art, Comparison section

---

### 4. A Systematic Literature Review in Cross-browser Testing

- **Authors:** Sabaren, L., Mascheroni, M., Greiner, C., Irrazabal, E.
- **Year:** 2018
- **Published:** Journal of Computer Science & Technology (JCS&T)
- **URL:** https://journal.info.unlp.edu.ar/JCST/article/view/691
- **Summary:** Comprehensive SLR examining 31 primary studies on cross-browser testing. Finds visual analysis is the most used technique (54.8% of articles proposed custom tools). Identifies variable element detection as the biggest challenge.
- **Why it's critical:** Provides the research landscape context. Most tools use visual/dynamic analysis — positions CrossGuard's static approach as filling a clear gap in the literature.
- **Cite in:** State of the Art (opening paragraph)

---

### 5. X-PERT: Accurate Identification of Cross-Browser Issues in Web Applications

- **Authors:** Shauvik Roy Choudhary, Mukul R. Prasad, Alessandro Orso
- **Year:** 2013
- **Published:** ICSE 2013 (35th International Conference on Software Engineering), pp. 702-711
- **URL:** https://dl.acm.org/doi/10.1145/2610384.2628057
- **Summary:** The most comprehensive dynamic XBI detection tool. Combines structural and visual analysis, achieving 76% precision and 95% recall. Automated, no developer effort required. Evaluated on real-world web applications.
- **Why it's critical:** Represents the state-of-the-art in dynamic cross-browser testing. CrossGuard's static approach offers complementary earlier-in-the-pipeline detection (shift-left).
- **Cite in:** State of the Art (dynamic approaches section)

---

### 6. WEBDIFF: Automated Identification of Cross-Browser Issues in Web Applications

- **Authors:** Shauvik Roy Choudhary, Husayn Versee, Alessandro Orso
- **Year:** 2010
- **Published:** IEEE International Conference on Software Maintenance (ICSM 2010)
- **URL:** https://ieeexplore.ieee.org/document/5609723/
- **Summary:** First technique combining computer vision and graph theory to identify cross-browser issues. Compares DOM structure and visual appearance via screen captures across browsers. Identified 121 issues in 9 real web applications with only 21 false positives.
- **Why it's critical:** The first automated visual approach to XBI detection. Foundation for all subsequent dynamic tools (CrossCheck, X-PERT, Browserbite). CrossGuard's static approach catches issues before deployment.
- **Cite in:** State of the Art (dynamic approaches section)

---

## TIER 2 — STRONGLY RECOMMENDED (Theoretical Foundations)

These give your paper its scientific grounding — what your supervisor specifically asked for.

---

### 7. ISO/IEC 25010:2023 — Software Product Quality Model

- **Authors:** ISO/IEC JTC 1/SC 7
- **Year:** 2011 (original), 2023 (revised)
- **Published:** International Organization for Standardization
- **URL:** https://www.iso.org/standard/35733.html
- **Summary:** International standard defining 8 quality characteristics: functional suitability, performance efficiency, **compatibility**, usability, reliability, security, maintainability, portability. "Compatibility" has sub-characteristics for co-existence and interoperability.
- **Why it matters:** **This is the theoretical justification for CrossGuard's 0-100 score.** CrossGuard directly measures the ISO 25010 "Compatibility" quality characteristic. Cite this to ground your scoring methodology in international standards.
- **Cite in:** Introduction (motivation), Methodology (scoring theory)

---

### 8. A Practical Model for Measuring Maintainability (SIG Model)

- **Authors:** I. Heitlager, T. Kuipers, J. Visser
- **Year:** 2007
- **Published:** 6th International Conference on Quality of Information and Communications Technology (QUATIC 2007), IEEE
- **URL:** https://ieeexplore.ieee.org/document/4335232/
- **Summary:** Maps source code metrics to ISO 9126 maintainability sub-characteristics using rating thresholds derived from industry benchmarks. Systems are rated on a 1-5 star scale.
- **Why it matters:** Directly analogous to CrossGuard's approach — both map low-level measurable metrics to a high-level quality rating. CrossGuard maps feature support data to 0-100; SIG maps code metrics to star ratings. Same fundamental methodology.
- **Cite in:** Methodology (scoring design justification)

---

### 9. Browser Feature Usage on the Modern Web

- **Authors:** Peter Snyder, Lara Ansari, Cynthia Taylor, Chris Kanich
- **Year:** 2016
- **Published:** ACM Internet Measurement Conference (IMC 2016)
- **URL:** https://dl.acm.org/doi/10.1145/2987443.2987466
- **Also:** https://arxiv.org/abs/1605.06467
- **Summary:** Large-scale empirical study of how browser features (JavaScript APIs) are actually used across the Alexa 10K websites. Found over 50% of provided JS features are never used, and 83% execute on less than 1% of top sites.
- **Why it matters:** Provides empirical evidence for WHY compatibility checking matters. The uneven adoption of web features creates the compatibility landscape that CrossGuard navigates.
- **Cite in:** Introduction (problem motivation)

---

### 10. Continuous Code Quality: Are We (Really) Doing That?

- **Authors:** Vassallo, C., Palomba, F., Bacchelli, A., Gall, H.C.
- **Year:** 2018
- **Published:** ASE 2018 (33rd ACM/IEEE International Conference on Automated Software Engineering)
- **URL:** https://dl.acm.org/doi/10.1145/3238147.3240729
- **Summary:** Reveals only 11% of CI builds include quality checks. Strong gap between theory and practice — developers mostly check quality at sprint end, not continuously.
- **Why it matters:** Directly motivates CrossGuard's CI/CD integration and quality gates (`--fail-on-score`, `--fail-on-errors`). CrossGuard is designed to make continuous compatibility checking practical.
- **Cite in:** Introduction (motivation for CI/CD), Design section

---

### 11. How Developers Engage with Static Analysis Tools in Different Contexts

- **Authors:** Vassallo, C., Panichella, S., Palomba, F., Proksch, S., Zaidman, A., Gall, H.C.
- **Year:** 2020
- **Published:** Empirical Software Engineering, Springer, Vol. 25, pp. 1419-1457
- **URL:** https://link.springer.com/article/10.1007/s10664-019-09750-5
- **Summary:** Studies how developers interact with static analysis tools. 71% pay attention to different warning categories depending on context; 63% rely on team policies; tools perceived as replacing humans in tedious tasks.
- **Why it matters:** Validates CrossGuard's design decisions — dual GUI + CLI frontends, categorizing issues by severity, configurable warning levels, different output contexts.
- **Cite in:** Design decisions section

---

### 12. Efficient and Flexible Incremental Parsing

- **Authors:** Tim A. Wagner, Susan L. Graham
- **Year:** 1998
- **Published:** ACM Transactions on Programming Languages and Systems (TOPLAS), Vol. 20, No. 2
- **URL:** https://dl.acm.org/doi/10.1145/293677.293678
- **Summary:** Presents an algorithm based on parsing LR(k) sentential forms that can incrementally parse arbitrary modifications in optimal time. The foundational paper on incremental parsing algorithms.
- **Why it matters:** **The key academic paper behind tree-sitter's parsing approach.** CrossGuard uses tree-sitter 0.21.3 for JS parsing, which implements this algorithm. Provides academic pedigree.
- **Cite in:** Design section (parser architecture)

---

### 13. Static Analysis at GitHub

- **Authors:** GitHub Engineering Team
- **Year:** 2021
- **Published:** ACM Queue / Communications of the ACM
- **URL:** https://dl.acm.org/doi/fullHtml/10.1145/3487019.3487022
- **Summary:** Describes GitHub's static analysis infrastructure built on tree-sitter, used for code navigation, CodeQL integration, and security analysis across 40+ languages and 6 million repositories.
- **Why it matters:** Industry validation for CrossGuard's use of tree-sitter. If GitHub trusts tree-sitter for code analysis at scale, CrossGuard's use for JavaScript feature detection is well-justified.
- **Cite in:** Design section (technology choices)

---

### 14. A Review of Software Quality Models for the Evaluation of Software Products

- **Authors:** S. A. Fahmy, A. S. Hamouda
- **Year:** 2014
- **Published:** arXiv (1412.2977)
- **URL:** https://arxiv.org/pdf/1412.2977
- **Summary:** Comprehensive review comparing McCall (1977), Boehm (1978), Dromey, FURPS, ISO 9126, and ISO 25010 quality models. Evaluates their characteristics, criteria, and metrics.
- **Why it matters:** Positions CrossGuard's scoring model within the broader quality model landscape. Shows how quality measurement has evolved from McCall's 11 factors to ISO 25010's 8 characteristics.
- **Cite in:** Background / Methodology (scoring theory)

---

## TIER 3 — RECOMMENDED (Supporting Context)

Strengthen specific sections of the paper.

---

### 15. CrossCheck: Combining Crawling and Differencing to Better Detect Cross-Browser Incompatibilities

- **Authors:** Shauvik Roy Choudhary, Mukul R. Prasad, Alessandro Orso
- **Year:** 2012
- **Published:** IEEE ICST 2012 (5th International Conference on Software Testing, Verification and Validation), pp. 171-180
- **URL:** https://ieeexplore.ieee.org/document/6200112/
- **Summary:** Combines crawling and differencing to leverage their respective strengths for XBI detection. Extends WEBDIFF with improved crawling strategies.
- **Use in:** State of the Art — dynamic tools evolution

---

### 16. Browserbite: Accurate Cross-Browser Testing via Machine Learning Over Image Features

- **Authors:** Nataliia Semenenko, Marlon Dumas, Tonis Saar
- **Year:** 2014
- **Published:** ICWE 2014, Springer; also ICSM 2013 and Software: Practice and Experience (2016)
- **URL:** https://link.springer.com/chapter/10.1007/978-3-319-08245-5_37
- **Also:** https://ieeexplore.ieee.org/document/6676949
- **Summary:** Uses image processing and machine learning to compare screenshots across browsers and classify differences as incompatibilities. Grew to 10,000+ registered users.
- **Use in:** State of the Art — ML approach

---

### 17. The Adoption of JavaScript Linters in Practice: A Case Study on ESLint

- **Authors:** Kristin Tomasdottir, Mauricio Aniche, Arie van Deursen
- **Year:** 2020
- **Published:** IEEE Transactions on Software Engineering, Vol. 46, No. 8, pp. 863-891
- **URL:** https://research.tudelft.nl/en/publications/the-adoption-of-javascript-linters-in-practice-a-case-study-on-es/
- **Summary:** Interviewed 15 developers, analyzed 9,500+ ESLint configs, surveyed 337 developers. Identified why developers use linters, configuration strategies, and most important rules.
- **Use in:** Design decisions — linter adoption patterns, comparison with eslint-plugin-compat

---

### 18. An Empirical Study of Client-Side JavaScript Bugs

- **Authors:** Frolin S. Ocariza Jr., Kartik Bajaj, Karthik Pattabiraman, Ali Mesbah
- **Year:** 2013 (expanded 2016)
- **Published:** ICSME 2013 / IEEE TSE (journal version)
- **URL:** https://people.ece.ubc.ca/~frolino/projects/js-bugs-study/js_bugs_study_paper.pdf
- **Summary:** Studied 502 bug reports from 19 repositories. Found 68% of JavaScript faults are DOM-related, caused by faulty interactions between JS code and the DOM.
- **Use in:** Motivation — validates checking JS API/DOM compatibility

---

### 19. Discovering Refactoring Opportunities in Cascading Style Sheets

- **Authors:** Davood Mazinanian, Nikolaos Tsantalis, Ali Mesbah
- **Year:** 2014
- **Published:** FSE 2014 (ACM SIGSOFT International Symposium on Foundations of Software Engineering)
- **URL:** https://people.ece.ubc.ca/amesbah/resources/papers/fse14.pdf
- **Summary:** Detects CSS declaration duplication in 38 real-world websites. Found duplication ranges 40-90%. Uses CSS parsing and AST analysis.
- **Use in:** Design section — precedent for AST-based CSS analysis

---

### 20. Battles with False Positives in Static Analysis of JavaScript Web Applications in the Wild

- **Authors:** J. Park, I. Lim, S. Ryu
- **Year:** 2016
- **Published:** ICSE-C 2016 (38th ICSE Companion), pp. 61-70
- **URL:** https://ieeexplore.ieee.org/document/7883289
- **Summary:** Analyzes 30 real-world JS web applications. Classifies 7 reasons for false positives including W3C APIs, browser-specific APIs, and JavaScript library APIs.
- **Use in:** Design section — explains why CrossGuard uses AST-based analysis with filtering

---

### 21. Standardized Code Quality Benchmarking for Improving Software Maintainability

- **Authors:** R. Baggen, J. P. Correia, K. Schill, J. Visser
- **Year:** 2012
- **Published:** Software Quality Journal, Springer, Vol. 20, No. 2
- **URL:** https://link.springer.com/article/10.1007/s11219-011-9144-9
- **Summary:** Extends the SIG model with standardized benchmarking using 100+ assessed systems. Defines how metrics are rated relative to a benchmark population.
- **Use in:** Methodology — validates using external reference data (Can I Use) for scoring

---

### 22. How Open Source Projects Use Static Code Analysis Tools in Continuous Integration Pipelines

- **Authors:** Zampetti, F., Scalabrino, S., Oliveto, R., Canfora, G., Di Penta, M.
- **Year:** 2017
- **Published:** IEEE MSR 2017 (14th International Conference on Mining Software Repositories)
- **URL:** https://ieeexplore.ieee.org/document/7962383/
- **Summary:** Studies static analysis tool usage in 20 Java OSS projects using Travis CI. Investigates configuration, build breakage patterns, and resolution times.
- **Use in:** Design — informs CrossGuard's CI/CD quality gate design

---

### 23. Usage, Costs, and Benefits of Continuous Integration in Open-Source Projects

- **Authors:** Michael Hilton, Timothy Tunnell, Kai Huang, Darko Marinov, Danny Dig
- **Year:** 2016
- **Published:** ASE 2016 (31st IEEE/ACM International Conference on Automated Software Engineering)
- **URL:** https://dl.acm.org/doi/abs/10.1145/2970276.2970358
- **Summary:** Studied CI usage across 34,544 GitHub projects. CI helps projects release more often, widely adopted by popular projects.
- **Use in:** Motivation — validates CI integration is critical for tool adoption

---

### 24. Towards Cross-browser Incompatibilities Detection: A Systematic Literature Review

- **Authors:** (Multiple authors)
- **Year:** 2019
- **Published:** International Journal of Software Engineering & Applications (IJSEA), Vol. 10, No. 6
- **URL:** https://aircconline.com/ijsea/V10N6/10619ijsea02.pdf
- **Summary:** SLR focused on automatic XBI detection strategies. Identifies 7 detection strategies: structural DOM, screenshot comparison, graph isomorphism, ML, relative layout, adaptive random testing, record/replay.
- **Use in:** State of the Art — CrossGuard adds an 8th strategy not in this review (static + compat DB)

---

### 25. Automated Analysis of CSS Rules to Support Style Maintenance

- **Authors:** Ali Mesbah, Shabnam Mirshokraie
- **Year:** 2012
- **Published:** ICSE 2012 (34th International Conference on Software Engineering)
- **URL:** https://dl.acm.org/doi/10.5555/2337223.2337272
- **Summary:** Automated CSS maintenance technique analyzing runtime relationships between CSS rules and DOM elements. Implemented in open-source tool Cilla. Found average 60% unused CSS selectors.
- **Use in:** State of the Art — CSS analysis tools

---

### 26. Modeling the HTML DOM and Browser API in Static Analysis of JavaScript Web Applications

- **Authors:** Simon Holm Jensen, Anders Moller, Peter Thiemann
- **Year:** 2011
- **Published:** ESEC/FSE 2011 (19th ACM SIGSOFT Symposium)
- **URL:** https://dl.acm.org/doi/10.1145/2025113.2025125
- **Summary:** Static analysis framework (TAJS) reasoning about control and data flow in JavaScript applications that interact with the HTML DOM and browser API. Found undiscovered bugs in wikipedia.org and amazon.com.
- **Use in:** Design — foundational work on JS static analysis in browser context

---

### 27. The 2022 Web Almanac (HTTP Archive)

- **Authors:** Rick Viscomi, Rachel Andrew, Jeremy Wagner, et al. (100+ contributors)
- **Year:** 2022
- **Published:** HTTP Archive / Google Books
- **URL:** https://almanac.httparchive.org/en/2022/
- **Summary:** Comprehensive annual report on the state of the web. CSS chapter: flexbox used on 74% of pages, grid on 12%. JS chapter: median 22 JS requests per page. Tracks adoption of modern web features.
- **Use in:** Introduction — empirical data on which features are actually used

---

### 28. SARIF 2.1.0 — Static Analysis Results Interchange Format

- **Authors:** M. C. Fanning, L. J. Golding (editors)
- **Year:** 2023
- **Published:** OASIS Standard
- **URL:** https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
- **Summary:** OASIS standard JSON format for static analysis tool output. Enables interoperability between analysis tools, IDEs, and CI/CD systems.
- **Use in:** Design section — export format standard CrossGuard implements

---

### 29. Polyfills and the Evolution of the Web (W3C TAG Finding)

- **Authors:** W3C Technical Architecture Group
- **Year:** 2017
- **Published:** W3C
- **URL:** https://www.w3.org/2001/tag/doc/polyfills/
- **Summary:** W3C's official guidance on polyfills — best practices for feature detection, deferring to native implementations, performance implications. Defines the term "polyfill" (coined by Remy Sharp in 2009).
- **Use in:** Design section — authoritative framework for polyfill recommendations

---

### 30. Interop 2022 — Browsers Working Together to Improve the Web for Developers

- **Authors:** Google, Mozilla, Apple, Microsoft, Igalia (collaboration)
- **Year:** 2022-present (annual)
- **Published:** web.dev / Mozilla Hacks / WebKit blogs
- **URL:** https://web.dev/blog/interop-2022
- **Also:** https://github.com/web-platform-tests/interop
- **Summary:** Joint initiative among major browser vendors to identify and fix important cross-browser inconsistencies. Uses automated tests to score browser compliance. Covers flexbox, grid, cascade layers, color spaces.
- **Use in:** Introduction — browser vendors themselves acknowledge the compat problem

---

## TIER 4 — OPTIONAL (Extra Depth)

Use these if you need more references for specific sections.

---

### 31. XBIDetective: Leveraging Vision Language Models for Identifying Cross-Browser Visual Inconsistencies

- **Authors:** (Multiple authors)
- **Year:** 2025
- **Published:** arXiv
- **URL:** https://arxiv.org/html/2512.15804v1
- **Summary:** Uses vision language models (VLMs) to detect cross-browser inconsistencies from screenshots, achieving 77-79% accuracy.
- **Use for:** Cutting-edge AI-based approach comparison

---

### 32. ReDeCheck: An Automatic Layout Failure Checking Tool for Responsively Designed Web Pages

- **Authors:** Thomas A. Walsh, Gregory M. Kapfhammer, Phil McMinn
- **Year:** 2017
- **Published:** ISSTA 2017
- **URL:** https://dl.acm.org/doi/10.1145/3092703.3098221
- **Summary:** Automated tool detecting responsive design layout issues using a Responsive Layout Graph (RLG) representation.
- **Use for:** Layout compatibility / responsive design

---

### 33. JANUS: Detecting Rendering Bugs in Web Browsers via Visual Delta Consistency

- **Authors:** WingTecher Research Group
- **Year:** 2025
- **Published:** ICSE 2025
- **URL:** https://ieeexplore.ieee.org/document/11029880/
- **Summary:** Detected 31 rendering bugs in Chrome, Safari, and Firefox (24 confirmed, 8 fixed). Browser rendering inconsistencies remain active in 2025.
- **Use for:** Evidence that compat problems are still current

---

### 34. Weighted Software Metrics Aggregation and Its Application to Defect Prediction

- **Authors:** R. Salfner, M. Felderer
- **Year:** 2021
- **Published:** Empirical Software Engineering, Springer, Vol. 26
- **URL:** https://link.springer.com/article/10.1007/s10664-021-09984-2
- **Summary:** Proposes defining weights automatically for aggregating software metrics into composite scores.
- **Use for:** Scoring methodology depth — CrossGuard's weighted scoring in `scorer.py`

---

### 35. Software Quality Metrics Aggregation in Industry

- **Authors:** Mordal, K., Anquetil, N., Laval, J., Serebrenik, A., Vasilescu, B., Ducasse, S.
- **Year:** 2013
- **Published:** Journal of Software: Evolution and Process
- **URL:** https://www.researchgate.net/publication/258316385
- **Summary:** Addresses summarizing metric results at system level and combining metrics with different output ranges into unified quality assessments.
- **Use for:** Aggregation theory — how CrossGuard combines per-feature results into one score

---

### 36. JavaScript Dead Code Identification, Elimination, and Empirical Assessment

- **Authors:** Malavolta, I., et al.
- **Year:** 2023
- **Published:** IEEE Transactions on Software Engineering, Vol. 49, No. 7
- **URL:** https://ieeexplore.ieee.org/document/10108937/
- **Summary:** Presents Lacuna for detecting/eliminating JS dead code using static+dynamic analysis on 30 mobile web apps.
- **Use for:** JS static analysis comparison

---

### 37. Technical Debt Management: The Road Ahead for Successful Software Delivery

- **Authors:** (Multiple authors)
- **Year:** 2024
- **Published:** arXiv
- **URL:** https://arxiv.org/html/2403.06484v1
- **Summary:** Comprehensive overview of technical debt management including measurement, prioritization, and repayment strategies.
- **Use for:** Framing compatibility issues as "compatibility debt"

---

### 38. Practical Static Analysis of JavaScript Applications in the Presence of Frameworks and Libraries

- **Authors:** Madsen, M., Livshits, B., Fanning, M.
- **Year:** 2013
- **Published:** ESEC/FSE 2013
- **URL:** https://dl.acm.org/doi/10.1145/2491411.2491417
- **Summary:** Addresses analyzing real-world JS that uses frameworks — proposes practical static analysis techniques that scale.
- **Use for:** JS analysis challenges CrossGuard faces

---

### 39. Abstract Syntax Tree for Programming Language Understanding and Representation: How Far Are We?

- **Authors:** Jingquan Sun, Hao Fang, et al.
- **Year:** 2023
- **Published:** arXiv (2312.00413)
- **URL:** https://arxiv.org/html/2312.00413v1
- **Summary:** Comprehensive survey of AST-based code representation. Reviews 4 parsing methods, 6 preprocessing methods, 4 encoding methods.
- **Use for:** AST theory — academic grounding for parser choice

---

### 40. Evaluating the Impact of Source Code Parsers on ML4SE Models

- **Authors:** Ilya Utkin et al.
- **Year:** 2022
- **Published:** arXiv (2206.08713)
- **URL:** https://arxiv.org/pdf/2206.08713
- **Summary:** Evaluates how different parsers (including tree-sitter) affect downstream analysis quality.
- **Use for:** tree-sitter validation — parser accuracy comparison

---

### 41. Crawling Ajax-Based Web Applications through Dynamic Analysis of User Interface State Changes (Crawljax)

- **Authors:** Ali Mesbah, Arie van Deursen, Stefan Lenselink
- **Year:** 2012
- **Published:** ACM Transactions on the Web
- **URL:** https://dl.acm.org/doi/10.1145/2109205.2109208
- **Summary:** Novel technique for crawling Ajax applications. Implements Crawljax used by many cross-browser testing tools.
- **Use for:** State of the Art — dynamic testing infrastructure

---

### 42. A Survey on Web Application Testing — A Decade of Evolution

- **Authors:** (Multiple authors)
- **Year:** 2024
- **Published:** arXiv (2412.10476)
- **URL:** https://arxiv.org/abs/2412.10476
- **Summary:** Comprehensive survey examining web application testing steps (generation, execution, evaluation) over the past decade.
- **Use for:** Broad context — web application testing landscape

---

### 43. Layout Cross-Browser Failure Classification for Mobile Responsive Design Web Applications

- **Authors:** (Multiple authors)
- **Year:** 2023
- **Published:** ACM Transactions on the Web (TWEB), Vol. 17, Issue 4
- **URL:** https://dl.acm.org/doi/10.1145/3580518
- **Summary:** Combines DOM-based and computer vision classification models for layout XBI detection. F1-score of 0.65 on 72 responsive web apps.
- **Use for:** ML for layout failures

---

### 44. GitHub Actions: The Impact on the Pull Request Process

- **Authors:** Mairieli Wessel et al.
- **Year:** 2023
- **Published:** Empirical Software Engineering, Springer
- **URL:** https://link.springer.com/article/10.1007/s10664-023-10369-w
- **Summary:** ~30% of top 5,000 GitHub repos adopt GitHub Actions. Adoption led to more PR rejections and changed communication.
- **Use for:** CI adoption context

---

### 45. Design Patterns: Elements of Reusable Object-Oriented Software

- **Authors:** E. Gamma, R. Helm, R. Johnson, J. Vlissides (Gang of Four)
- **Year:** 1994
- **Published:** Addison-Wesley Professional
- **ISBN:** 978-0201633610
- **Summary:** The foundational text defining 23 design patterns including Facade, Singleton, Repository.
- **Use for:** Architecture section — CrossGuard uses Facade (AnalyzerService), Singleton (DB connection), Repository (CRUD)

---

### 46. HTML5 and the Evolution of HTML: Tracing the Origins of Digital Platforms

- **Authors:** (Multiple authors)
- **Year:** 2021
- **Published:** Technology in Society (ScienceDirect)
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S0160791X2100004X
- **Summary:** Historical analysis of HTML's evolution from versioned specs to the "Living Standard." Explains why features land at different times in different browsers.
- **Use for:** Introduction — historical context for the compatibility problem

---

### 47. What Happens When Software Developers Are (Un)happy

- **Authors:** Daniel Graziotin, Fabian Fagerholm, Xiaofeng Wang, Pekka Abrahamsson
- **Year:** 2018
- **Published:** Journal of Systems and Software (ScienceDirect)
- **URL:** https://www.sciencedirect.com/science/article/pii/S0164121218300323
- **Summary:** Survey of 2,220 developers. Identified 219 causes of developer unhappiness. Unhappy developers produce lower code quality.
- **Use for:** Motivation — compat issues cause frustration, tools reduce it

---

### 48. A Meta-Model to Support Compatibility Testing of Cross-Browser Web Application

- **Authors:** (Multiple authors)
- **Year:** 2025
- **Published:** IEEE ICACS 2025 (6th International Conference on Advancements in Computational Sciences)
- **URL:** https://ieeexplore.ieee.org/document/10937860
- **Summary:** Proposes a meta-model using checklist-IFML integration to systematically generate test cases targeting compatibility issues.
- **Use for:** Recent related work

---

## Additional References (Not Academic Papers)

### Can I Use (caniuse.com)

- **URL:** https://caniuse.com/
- **Summary:** Primary data source for browser compatibility information. 10,500+ feature support tables. CC BY 4.0 license. CrossGuard's compatibility database.
- **Cite as:** Data source

---

### MDN Browser Compatibility Data (BCD)

- **URL:** https://github.com/mdn/browser-compat-data
- **Summary:** Machine-readable browser compatibility data with 10,000+ data points, 500+ contributors. Used by VS Code, webhint, and Can I Use itself.
- **Cite as:** Alternative data source used by competitors (webhint, eslint-plugin-compat)

---

### Caniuse and MDN Compat Data Collaboration

- **Authors:** Mozilla, Fyrd (Can I Use project)
- **Year:** 2019
- **Published:** Mozilla Hacks blog
- **URL:** https://hacks.mozilla.org/2019/09/caniuse-and-mdn-compat-data-collaboration/
- **Summary:** Documents the collaboration between Can I Use (500 features) and MDN BCD (10,000+ features) projects.
- **Cite as:** Data ecosystem context

---

## Recommended Citation Strategy for the TDK Paper

### For a 10-20 page paper, cite 15-20 papers:

**Must read and cite (10):**
Papers #1, #2, #3, #4, #7, #8, #9, #10, #12, #13

**Should cite (5-8):**
Papers #5, #6, #11, #17, #18, #21, #27, #28

### The Key Narrative for Your Paper:

1. **The problem is real:** Browsers implement features at different rates (#9, #27, #30)
2. **Existing solutions use dynamic/visual analysis** (#2, #5, #6, #15, #16) — requires deployment first
3. **Only ONE prior paper uses static analysis for this** (#1) — but regex-only, HTML-only, no scoring
4. **CrossGuard extends static approach** with AST parsing, multi-language, ISO 25010-grounded scoring (#7, #8, #12, #13)
5. **CI/CD integration addresses known gap** in continuous quality (#10, #11, #22)

### Research Gaps CrossGuard Fills:

1. **Static vs. Dynamic:** Most academic tools use dynamic/runtime analysis. Only Xu & Zeng (2015) and wIDE (2017) use static analysis, but with simpler detection.
2. **AST-based parsing for compatibility:** No existing academic tool uses AST-based parsing (tinycss2, tree-sitter) specifically for browser compatibility checking. This is a novel contribution.
3. **Multi-format coverage:** Most tools focus on one language. CrossGuard covers HTML+CSS+JS with dedicated parsers.
4. **Quantitative scoring:** No existing academic tool provides a 0-100 compatibility score with letter grades.
5. **CI/CD-native output:** SARIF/JUnit integration is novel for browser compatibility checking.
