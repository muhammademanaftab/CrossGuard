# Cross Guard -- Diagrams

## Files

```
diagrams/
├── README.md                  ← you are here
├── uml_explained.md           ← full explanation of the UML diagram in simple English
├── images/
│   ├── uml_class_diagram.png           ← detailed UML (all attrs + methods) -- for Appendix
│   ├── uml_class_diagram_highlevel.png ← clean UML (class names only) -- for main chapter
│   └── usecase.png                     ← use case diagram -- for main chapter
└── scripts/
    ├── generate_uml.py            ← generates the detailed UML diagram
    ├── generate_uml_highlevel.py  ← generates the high-level UML diagram
    ├── generate_usecase.py        ← generates the use case diagram (graphviz, unused)
    └── usecase.puml               ← PlantUML source for the use case diagram
```

## How to Regenerate

```bash
# From project root:

# Detailed UML class diagram (all attributes and methods)
python docs/diagrams/scripts/generate_uml.py

# High-level UML class diagram (class names + relationships only)
python docs/diagrams/scripts/generate_uml_highlevel.py

# Use case diagram (requires PlantUML + Java)
plantuml -tpng docs/diagrams/scripts/usecase.puml -o ../images/
```

## Where to Use in Thesis

| Diagram | Where | Purpose |
|---------|-------|---------|
| `uml_class_diagram_highlevel.png` | Main chapter (Design section) | Shows the architecture at a glance |
| `usecase.png` | Main chapter (Requirements section) | Shows what users and developers can do |
| `uml_class_diagram.png` | Appendix | Full technical reference with every attribute and method |
| `uml_explained.md` | Reference for writing | Explains every class, arrow, and relationship in plain English |
