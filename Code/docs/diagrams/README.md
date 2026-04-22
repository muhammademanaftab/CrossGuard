# Cross Guard — Diagrams

Every diagram is prefixed with the thesis section it illustrates, so they sort in the order they appear in Chapter 3.

## Files

```
diagrams/
├── README.md                  ← you are here
├── uml_explained.md           ← plain-English walkthrough of the UML diagram
├── images/                    ← rendered PNGs (thesis-section-prefixed)
└── scripts/                   ← generators (Graphviz Python + PlantUML)
```

## Diagram map

| Thesis § | Image | Generator |
|---|---|---|
| 3.5 | `3.5_architecture_overview.png` | `3.5_architecture_overview.py` |
| 3.5 | `3.5_architecture_detailed.png` | `3.5_architecture_detailed.py` |
| 3.5 | `3.5_class_diagram_full.png` (Appendix) | `3.5_class_diagram_full.py` |
| 3.6 | `3.6_analysis_pipeline.png` | `3.6_analysis_pipeline.py` |
| 3.7 | `3.7_parsers.png` | `3.7_parsers.py` |
| 3.9 | `3.9_database.png` | `3.9_database.py` |
| 3.11 | `3.11_polyfill.png` | `3.11_polyfill.py` |
| 3.12 | `3.12_ai_fix_service.png` | `3.12_ai_fix_service.py` |
| 3.13 | `3.13_gui.png` | `3.13_gui.py` |
| 3.15 | `3.15_use_case.png` | `3.15_use_case.puml` *(PlantUML)* |
| 3.16 | `3.16_sequence.png` | `3.16_sequence.puml` *(PlantUML)* |
| 3.18 | `3.18_directory_structure.png` | `3.18_directory_structure.py` |

## How to regenerate

All Graphviz diagrams (the `.py` generators):

```bash
# From project root
python docs/diagrams/scripts/3.5_architecture_overview.py
python docs/diagrams/scripts/3.5_architecture_detailed.py
python docs/diagrams/scripts/3.5_class_diagram_full.py
python docs/diagrams/scripts/3.6_analysis_pipeline.py
python docs/diagrams/scripts/3.7_parsers.py
python docs/diagrams/scripts/3.9_database.py
python docs/diagrams/scripts/3.11_polyfill.py
python docs/diagrams/scripts/3.12_ai_fix_service.py
python docs/diagrams/scripts/3.13_gui.py
python docs/diagrams/scripts/3.18_directory_structure.py
```

PlantUML diagrams (requires PlantUML + Java):

```bash
plantuml -tpng docs/diagrams/scripts/3.15_use_case.puml  -o ../images/
plantuml -tpng docs/diagrams/scripts/3.16_sequence.puml  -o ../images/
```

## Where each diagram goes in the thesis

- **Main chapter:** `3.5_architecture_overview`, `3.5_architecture_detailed`, plus all section-specific diagrams (3.6–3.18).
- **Appendix:** `3.5_class_diagram_full` — the full reference with every attribute and method.
- **Reading companion:** `uml_explained.md` — prose explanation of every class, arrow, and relationship.
