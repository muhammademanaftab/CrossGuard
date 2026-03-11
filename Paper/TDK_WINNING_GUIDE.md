# How to Win Top 3 at TDK (ELTE Informatics) — Complete Professional Guide

> Based on thorough research of official OTDK documents, ELTE IK rules, jury rubrics, winner interviews, and supervisor advice.

---

## Table of Contents
1. [What is TDK — The System](#1-what-is-tdk)
2. [How Judging Works — The Exact Rubric](#2-how-judging-works)
3. [What Separates Winners from Average](#3-what-separates-winners)
4. [Writing a Winning Paper](#4-writing-a-winning-paper)
5. [Giving a Winning Presentation](#5-giving-a-winning-presentation)
6. [Handling Q&A Like a Pro](#6-handling-qa)
7. [Common Mistakes That Kill Your Score](#7-common-mistakes)
8. [Timeline and Logistics](#8-timeline-and-logistics)
9. [LaTeX Template and Formatting](#9-latex-template)
10. [Checklist for Presentation Day](#10-checklist)

---

## 1. What is TDK

**TDK (Tudományos Diákköri Konferencia)** is Hungary's unique academic talent development system, running since the 1950s. Students conduct original research under faculty supervision, write a formal paper, and present at a conference judged by professional academics.

### The Progression
```
ELTE IK Institutional TDK (Kari TDK)
    │
    │  Top placements (I., II., III. place) get nominated
    ▼
OTDK — National Level (Országos TDK)
    │
    │  First-place winners can apply for
    ▼
Pro Scientia Gold Medal (Hungarian Academy of Sciences)
```

### At ELTE IK Specifically
- ~19-40 papers per semester
- Held every semester (spring ~June, autumn ~December)
- Sections: **Szoftvertechnológia** (Software Technology), Jel- és képfeldolgozás, Mesterséges Intelligencia
- **CrossGuard fits in: Szoftvertechnológia section**
- ~68% of papers get recommended for OTDK — the institutional round is achievable with solid preparation
- Venues: hosted at sponsor offices (Morgan Stanley, Siemens, Shapr3D)
- Sponsors provide scholarship money for winners

### What You Get
- Official certificate of participation from ELTE
- CV line: "Presented research paper at ELTE IK TDK Conference 2026"
- Top 3 → nominated to OTDK (national level)
- Scholarship points (ösztöndíj)
- Extra points for MSc/doctoral applications

---

## 2. How Judging Works — The Exact Rubric

### SCORING IS 50/50: Paper + Presentation

**The paper gets you to the competition. The presentation wins you the placement.**

### Written Paper Evaluation (50 points max)

Scored by 2 independent reviewers (average taken). At ELTE IK, the 7-category rubric:

| # | Criterion | Max Points | What They Look For |
|---|-----------|------------|-------------------|
| 1 | **Novelty** (újszerűség) | 8 | Is this genuinely new? Not just applying existing tech |
| 2 | **Topic and Content** (téma és tartalom) | 8 | Is the topic well-chosen? Is content thorough? |
| 3 | **Result Verification** (eredmények igazoltsága) | 8 | Are results proven? Tests? Benchmarks? Real data? |
| 4 | **Literature Review** (irodalom feldolgozása) | 6 | Did you find and properly cite relevant prior work? |
| 5 | **Formal Design & Style** (formai kivitel, stílus) | 6 | Writing quality, formatting, figure quality |
| 6 | **Scientific Value** (tudományos érték) | 6 | Could this be published? Does it advance the field? |
| 7 | **Reviewer Summary** (bírálói összefoglalás) | 8 | Overall impression of strengths and weaknesses |
| | **TOTAL** | **50** | |

### Oral Presentation + Q&A Evaluation (50 points max)

Scored by a jury of 3+ members:

| # | Criterion | What They Evaluate |
|---|-----------|-------------------|
| 1 | **Significance of results** | Does this matter? Who benefits? |
| 2 | **Verification of results** | Can you prove your claims? Evidence? |
| 3 | **Content & professional quality** | Do you understand what you built? Technical depth? |
| 4 | **Result visualization** | Charts, diagrams, demo — are results shown clearly? |
| 5 | **Debating ability (Q&A)** | Can you handle tough questions? Think on your feet? |
| 6 | **Structure, organization, time management** | Was the talk well-organized? Did you stay in time? |

### Key Insight
Q&A performance is **disproportionately important** — worth up to 30% of the presentation score. Many students underestimate this. The jury chairman MUST pose at least 2 questions if the audience doesn't ask enough.

---

## 3. What Separates Winners from Average

Based on interviews with OTDK winners and jury chairs:

### Winners Do This:
1. **Show genuine novelty** — Not "I applied existing tech to a problem" but "I created a unique approach that no existing tool provides"
2. **Have a working prototype with real results** — Every OTDK first-place winner had a concrete implementation with measurable outcomes
3. **Go deep, not wide** — Masters of their specific area, not surface-level coverage of everything
4. **Explicitly state their contribution** — A clear slide showing "THIS is what I built that didn't exist before"
5. **Show publishability** — The paper reads like it could be submitted to a real conference
6. **Own their limitations** — Honestly state what the tool doesn't do. Judges respect intellectual honesty far more than false completeness

### Average Papers Do This:
- Describe what was built, list features, show screenshots (no depth)
- Superficial literature review
- No quantitative evaluation (just "it works")
- Vague language ("in many cases", "quite frequently") instead of precise numbers
- Can't clearly articulate what's novel

### The Quote That Matters
> "Outstanding results can only be achieved by those who don't want to write an average paper, but instead want to research a specialized area with a specialized method and thus create something unique." — OTDK supervisor

---

## 4. Writing a Winning Paper

### Structure (10-20 pages for institutional TDK, 20-60 for OTDK)

```
1. Abstract (200-400 words) — write LAST
2. Introduction (1-2 pages) — problem, motivation, contributions list
3. State of the Art (3-4 pages) — competitor tools + scientific papers
4. CrossGuard Design (3-4 pages) — architecture, parsers, scoring
5. Evaluation (2-3 pages) — real project tests, comparison, metrics
6. Conclusion (1 page) — contributions, limitations, future work
7. References (30-60 citations for a strong paper)
```

### Introduction — The Funnel Structure
1. **Universal hook** — "The modern web platform comprises thousands of features with varying browser support..."
2. **Narrow to the problem** — "Developers lack automated tools that statically analyze source files..."
3. **Existing gaps** — "Current tools check only CSS (doiuse) or only JS (eslint-compat). No tool provides unified analysis..."
4. **Your solution** — "We present Cross Guard, a static analysis tool that..."
5. **Contributions list** — Enumerate 3-5 bullet points of what's new
6. **Paper outline** — "The rest of this paper is organized as follows..."

### State of the Art — How to Write It
- **Organize by category**, not by paper (e.g., "CSS linters", "JS compat tools", "cross-browser testing research")
- For each tool/paper: what it does → how it relates → what gap it leaves
- **End with the master comparison table** + a paragraph summarizing the gap CrossGuard fills
- Pattern: "X does Y, however it does not address Z, which is what our tool provides"
- Be objective and fair — never disparage competing work

### Evaluation — What Makes It Scientific

**Use these metrics for CrossGuard:**
- **Precision**: Of detected features, what fraction are truly present? (false positive rate)
- **Recall**: Of features actually present, what fraction detected? (false negative rate)
- **Performance**: Analysis time vs. file size
- **Real-world case study**: Run on 3-5 GitHub projects, report scores and issues
- **Comparison**: Run a competitor tool (doiuse) on same CSS files, compare results
- **Threats to validity section** — Internal, external, construct validity. This is MANDATORY in rigorous SE research

### References — Quality and Quantity
- **30-60 references** for a strong TDK paper
- Mix: foundational papers (2010-2015) + recent papers (2020-2025) + tool docs + W3C/ECMAScript specs
- Every reference must be actually cited in the text
- Use consistent citation style (IEEE numeric or author-year)

### Language
- Papers can be Hungarian or English at ELTE IK TDK
- If your supervisor advises Hungarian, write in Hungarian
- CS terminology is naturally English-heavy, so either works

---

## 5. Giving a Winning Presentation

### Time: 15 minutes presentation + Q&A discussion

### Slide Count: 11-13 slides (NOT more)

### Slide-by-Slide Blueprint

| # | Section | Time | What to Show |
|---|---------|------|-------------|
| 1 | Title | 0:00-0:15 | Name, supervisor, ELTE, title |
| 2 | Problem & Motivation | 0:15-2:00 | WHY this matters. Concrete example of a real compat bug |
| 3 | Related Work (1 slide!) | 2:00-3:30 | Comparison table. "No tool does all three." |
| 4 | Architecture | 3:30-5:30 | Data flow diagram. High-level design |
| 5-6 | Technical Deep Dive | 5:30-8:30 | Pick ONE parser (JS tree-sitter is most impressive). Show the 3-tier detection |
| 7 | Demo | 8:30-10:00 | 60-90 second demo (live or pre-recorded video) |
| 8-9 | Results & Evaluation | 10:00-12:00 | Test results, project scores, comparison charts. CONCRETE NUMBERS |
| 10 | Conclusions | 12:00-13:30 | 3 key contributions. Limitations. Future work |
| 11 | Thank You | 13:30-14:00 | End with your KEY TAKEAWAY, not "thank you" |
| -- | Buffer | 14:00-15:00 | Safety margin |

### Time Allocation
```
|--- Intro/Motivation ---|--- Technical Core ---|--- Results/Eval ---|-- Conclusions --|
|      3 min (20%)       |     5-6 min (37%)    |    4 min (27%)     |   2 min (13%)   |
```

### The Demo — Your Secret Weapon
For a tool paper, **the demo is the most persuasive evidence**. Do it right:

1. **Pre-record a 60-90 second screencast** as backup (embed as MP4 in slides)
2. **Attempt live demo first** if venue allows your laptop:
   - Terminal pre-opened, command pre-typed, press Enter
   - Show CLI analyzing a real file → table output with scores
   - Show GUI drag-and-drop → results dashboard
3. **If live fails**: switch to video immediately, no apologies
4. Increase terminal font to 18-20pt for readability from back row

### Visual Style
- **Minimum 20pt font** (Obuda TDK guide: this is explicit, not optional)
- Sans-serif font (Arial, Calibri, Helvetica)
- High-contrast colors, max 3-5 colors
- ONE idea per slide
- Architecture diagrams > text. Charts > tables. Screenshots > descriptions
- **No animations** — they break on venue machines and surveys show nobody likes them
- Color-code: green (supported), yellow (partial), red (unsupported) — matches your tool's output naturally

### Delivery
- **Memorize your opening and closing sentences word-for-word**
- Speak naturally in between — don't read from slides
- Make eye contact with the jury
- Signal transitions: "Now that I've shown the problem, let me describe our approach"
- **Do NOT end with "Thank you for your attention"** — end with your key takeaway message

---

## 6. Handling Q&A Like a Pro

### Preparation
- You receive **2 written reviews one week before** the conference. READ THEM CAREFULLY
- Prepare specific answers for every point raised by reviewers
- Prepare **3-5 backup slides** with detailed data (test coverage per parser, performance benchmarks, comparison details, technology choice rationale)
- When a judge asks a specific question and you pull up a backup slide with the exact data — **that's the moment that separates winners**

### Typical Questions for a Tool Paper
- "How does CrossGuard compare to [eslint-plugin-compat / doiuse]?"
- "What is your false positive/negative rate?"
- "What happens when Can I Use database is out of date?"
- "Could this be extended to TypeScript / SCSS?"
- "What was the hardest technical challenge?"
- "Which results are YOUR OWN work vs. the advisor's?" (OTDK explicitly requires this)
- "What are the limitations?"
- "How long does analysis take on a large project?"

### Answering Techniques (ranked best to worst)
1. **Bridge to what you know**: "That specific case hasn't been tested, but a related scenario showed [X]. I'd hypothesize that..."
2. **Acknowledge + add value**: "That's outside our current scope, but it's a natural next step because..."
3. **Reframe as future work**: "We identified this as a limitation. Our planned approach is..."
4. **Buy time**: "Interesting question — let me think about that." Then give a thoughtful partial answer

### Never Do This
- Never bluff or make up data — judges are experts, they WILL catch it
- Never get defensive or argue
- Never say just "I don't know" and stop — always follow with what you DO know
- Never dismiss a question as irrelevant

---

## 7. Common Mistakes That Kill Your Score

### Fatal (Significant Point Loss)
| Mistake | Penalty |
|---------|---------|
| **Exceeding time limit by 30-60 sec** | -5 points |
| **Exceeding time limit by 60+ sec** | -10 points |
| **Exceeding 15 min (no Q&A possible)** | 0 points for discussion skills |
| **Missing contribution-delineation slide** | -10 points |
| **Reading from slides** | Destroys "debating ability" score |
| **No quantitative results** | Kills "result verification" score |

### Serious (Several Points Lost)
- All theory, no results (looks like you're afraid to show your work)
- Superficial literature review
- Unreadable slides (tiny font, wall of text)
- No practice run (what you think is 15 min is often 25 min spoken aloud)
- Not disclosing AI tool usage (new requirement — if you used ChatGPT/Copilot, document in appendix)

### Easily Avoidable
- No clear narrative arc (facts listed sequentially vs. problem→solution story)
- Skipping transitions between sections
- Not testing setup on venue machine beforehand
- Generic ending ("So... that's it")

---

## 8. Timeline and Logistics

### ELTE IK Spring TDK 2026 (Based on Your Roadmap)

| When | What |
|------|------|
| March 11-17 | Research competitor tools + search for scientific papers |
| March 18-24 | Build comparison table + draft State of the Art |
| March 25-31 | Run CrossGuard on real projects + document results |
| April 1-14 | Write full TDK paper draft + send to supervisor |
| April 15-21 | Incorporate supervisor feedback + revise |
| April 22-27 | Submit abstract to tdk.inf.elte.hu |
| **April 28** | **ABSTRACT DEADLINE** |
| ~Mid May | Upload full paper PDF |
| ~June 2026 | Present at TDK conference (15 min + Q&A) |

### Submission Process
1. Submit abstract (200-400 words) at **tdk.inf.elte.hu** before deadline
2. Supervisor must approve it
3. Upload full paper PDF when upload window opens (~mid May)
4. Paper max 10MB
5. Prepare 15-minute presentation slides

---

## 9. LaTeX Template and Formatting

### Official ELTE IK Template: `elteiktdk`
- **Overleaf**: https://www.overleaf.com/latex/templates/tdk-thesis-template-elte-fi/mxnndxkmdmkd
- **GitHub**: https://github.com/mcserep/elteiktdk
- **CTAN**: https://ctan.org/pkg/elteiktdk
- Supports Hungarian and English
- Auto-generates cover page and title page from metadata
- Compliant with OTDK Informatics Section requirements
- Includes theorem environments, code highlighting (minted), algorithm support

### Formatting Standards
- Font: Times New Roman 12pt (or LaTeX default serif)
- Line spacing: 1.5
- Margins: Left 3cm, Right 2cm, Top 3cm, Bottom 3cm
- Justified alignment
- Figures/tables numbered with in-text references
- Consistent citation style throughout

---

## 10. Checklist for Presentation Day

### One Week Before
- [ ] Read both written reviews carefully
- [ ] Prepare specific answers for every reviewer comment
- [ ] Prepare 10+ anticipated jury questions with answers
- [ ] Prepare 3-5 backup slides with detailed data
- [ ] Complete at least 2 full timed rehearsals (must be under 14 minutes)
- [ ] Record demo video and embed in slides as MP4

### The Night Before
- [ ] Save slides as both PPTX and PDF on USB drive
- [ ] Test that embedded video plays correctly
- [ ] Memorize opening and closing sentences
- [ ] Prepare clear statement of YOUR contributions vs. advisor's

### On the Day
- [ ] Arrive 30 minutes early
- [ ] Test slides on venue machine/projector
- [ ] Disable all notifications on any device you use
- [ ] Have a clock/timer visible during your talk
- [ ] Have water available

### During the Talk
- [ ] Stay under 14 minutes (buffer for slide transitions)
- [ ] Make eye contact with jury
- [ ] Speak from memory, don't read slides
- [ ] Signal transitions between sections
- [ ] End with your KEY TAKEAWAY, not "thank you"

### During Q&A
- [ ] Listen to full question before responding
- [ ] Take a breath (2-3 sec pause is fine)
- [ ] Pull up backup slides when relevant
- [ ] Be honest about limitations
- [ ] Never bluff or get defensive

---

## The Bottom Line

**What CrossGuard has that can WIN:**
- It's a **working tool** with **2,394 tests** — this is concrete, measurable, impressive
- It fills a **clear gap**: no existing tool analyzes HTML + CSS + JS together with scoring
- It has **AST-based parsing** (tinycss2, tree-sitter) — technically sophisticated
- It has **6 export formats** and **CI/CD integration** — practical, real-world value
- It has a **GUI and CLI** — shows software engineering maturity

**What you need to add for the paper:**
- Rigorous evaluation with precision/recall metrics
- Real-world case study results (3-5 GitHub projects)
- Comparison data against competitor tools
- Strong literature review (30+ references)
- Threats to validity section

**The winning formula:**
> Genuine novelty + working prototype + rigorous evaluation + strong presentation + confident Q&A = Top 3

---

*Sources: OTDK official documents, ELTE IK TDK calls (2024-2025), University of Szeged jury regulations, Obuda/Corvinus/Semmelweis TDK guides, OTDK winner interviews (Raketa.hu, BME GTK), Mark Hill (UW-Madison) presentation advice, Ten Simple Rules for Presentations (PMC), The Thesis Whisperer, Mary Shaw ICSE framework*
