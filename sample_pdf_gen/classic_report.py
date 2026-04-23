"""Classic Browser Compatibility PDF Report — single-file generator.

Usage:
    python classic_report.py [input.json] [output.pdf]

Defaults:
    input  = report.json     (next to this script)
    output = compatibility_report_classic.pdf

Requires:
    pip install weasyprint jinja2
    (+ system Pango/Cairo; on macOS: brew install pango)
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, select_autoescape
from weasyprint import HTML, CSS


# ---- Embedded template ----------------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Browser Compatibility Report</title></head>
<body>

<h1 class="report-title">Browser Compatibility Report</h1>

<section class="block">
  <p><strong>Executive Summary:</strong></p>
  <p>
    The analyzed code demonstrates
    {% if scores.weighted_score >= 90 %}excellent{% elif scores.weighted_score >= 80 %}strong{% elif scores.weighted_score >= 60 %}moderate{% else %}limited{% endif %}
    cross-browser compatibility with an overall score of
    <strong>{{ scores.weighted_score | round(1) }}%</strong>
    (Grade <strong>{{ scores.grade }}</strong>).
    A total of <strong>{{ summary.total_features }} {{ primary_category }} features</strong>
    were detected, with
    {% if summary.critical_issues %}only <strong>{{ summary.critical_issues }} critical {{ "issue" if summary.critical_issues == 1 else "issues" }}</strong> identified{% else %}no critical issues identified{% endif %}.
    The lowest compatibility was observed in {{ lowest_browser.name }}
    ({{ lowest_browser.pct }}%).
  </p>
</section>

<table class="plain-table">
  <thead>
    <tr>
      <th>Browser</th><th>Version</th><th>Compatibility</th>
      <th>Supported</th><th>Partial</th><th>Unsupported</th>
    </tr>
  </thead>
  <tbody>
    {% for row in rows %}
    <tr>
      <td>{{ row.name }}</td>
      <td>{{ row.version }}</td>
      <td>{{ row.pct }}%</td>
      <td>{{ row.supported }}</td>
      <td>{{ row.partial }}</td>
      <td>{{ row.unsupported }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<section class="block">
  <p><strong>Key Compatibility Issues:</strong></p>
  <ul class="dash-list">
    {% for issue in key_issues %}<li>{{ issue }}</li>{% endfor %}
    {% if baseline_summary.limited %}
    <li>{{ baseline_summary.limited }} feature{{ "" if baseline_summary.limited == 1 else "s" }} with limited baseline availability — fallbacks recommended.</li>
    {% endif %}
    {% if baseline_summary.unknown %}
    <li>{{ baseline_summary.unknown }} feature{{ "" if baseline_summary.unknown == 1 else "s" }} not found in the baseline database — verify support manually.</li>
    {% endif %}
  </ul>
</section>

<section class="block">
  <p><strong>Baseline Availability:</strong></p>
  <ul class="dash-list">
    <li><strong>{{ baseline_summary.widely_available }}</strong> widely available feature{{ "" if baseline_summary.widely_available == 1 else "s" }} — safe for production use.</li>
    <li><strong>{{ baseline_summary.newly_available }}</strong> newly available feature{{ "" if baseline_summary.newly_available == 1 else "s" }} — test across older browser versions.</li>
    <li><strong>{{ baseline_summary.limited }}</strong> feature{{ "" if baseline_summary.limited == 1 else "s" }} with limited availability.</li>
    <li><strong>{{ baseline_summary.unknown }}</strong> feature{{ "" if baseline_summary.unknown == 1 else "s" }} with unknown baseline status.</li>
  </ul>
</section>

<section class="block">
  <p><strong>Recommendations:</strong></p>
  <ol class="num-list">
    {% for rec in recommendations %}<li>{{ rec }}</li>{% endfor %}
    <li>Perform cross-browser testing for partially supported features.</li>
    <li>Prioritize fixes for high-severity compatibility gaps.</li>
  </ol>
</section>

<section class="block">
  <p><strong>Report Metadata:</strong></p>
  <p>
    Generated on {{ generated_at }}.
    Analysis covered {{ browser_count }} browsers:
    {{ browser_list }}.
    Simple score: <strong>{{ scores.simple_score }}</strong>.
    Weighted score: <strong>{{ scores.weighted_score }}</strong>.
    Risk level: <strong>{{ scores.risk_level | lower }}</strong>.
  </p>
</section>

{# ---- Page 2: Full Feature Inventory ---- #}
<div class="page-break"></div>

<h2 class="section-title">Appendix A — Feature Inventory</h2>
<p class="section-lead">
  Complete list of all {{ summary.total_features }} feature{{ "" if summary.total_features == 1 else "s" }}
  detected across HTML, CSS and JavaScript, with baseline status.
</p>

{% for cat_label, details in inventories %}
{% if details %}
<h3 class="subsection-title">{{ cat_label }} Features ({{ details | length }})</h3>
<table class="inventory-table">
  <thead>
    <tr>
      <th style="width: 22%">Feature</th>
      <th style="width: 36%">Description</th>
      <th style="width: 28%">Matched Properties</th>
      <th style="width: 14%">Baseline</th>
    </tr>
  </thead>
  <tbody>
    {% for d in details %}
    <tr>
      <td class="mono">{{ d.feature }}</td>
      <td>{{ d.description }}</td>
      <td class="mono">
        {% if d.matched_properties %}{{ d.matched_properties | join(", ") }}{% else %}—{% endif %}
      </td>
      <td>{{ baseline_label(d.feature) }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endif %}
{% endfor %}

{% if unrecognized.total %}
<h3 class="subsection-title">Unrecognized ({{ unrecognized.total }})</h3>
<p>The following items were detected but not matched against the feature database:</p>
<ul class="dash-list">
  {% for cat in ['html', 'css', 'js'] %}
    {% if unrecognized[cat] %}
    <li><strong>{{ cat | upper }}:</strong> {{ unrecognized[cat] | join(", ") }}</li>
    {% endif %}
  {% endfor %}
</ul>
{% endif %}

</body>
</html>
"""

CSS_TEMPLATE = """
@page {
  size: Letter;
  margin: 18mm 22mm 18mm 22mm;
}

html, body {
  margin: 0;
  padding: 0;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.45;
  color: #000;
  hyphens: none;
}

h1.report-title {
  text-align: center;
  font-size: 18pt;
  font-weight: 700;
  margin: 4mm 0 8mm 0;
}

.block { margin-bottom: 4mm; }
.block p { margin: 0 0 1.5mm 0; }

strong { font-weight: 700; }

.plain-table {
  border-collapse: collapse;
  margin: 3mm auto 4mm auto;
  font-size: 10pt;
}
.plain-table th,
.plain-table td {
  border: 1px solid #000;
  padding: 2mm 5mm;
  text-align: center;
  vertical-align: middle;
}
.plain-table thead th {
  background: #D9D9D9;
  font-weight: 700;
}

.dash-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.dash-list li {
  position: relative;
  padding-left: 5mm;
  margin: 0.5mm 0;
}
.dash-list li::before {
  content: "-";
  position: absolute;
  left: 0;
  top: 0;
}

.num-list {
  list-style: decimal;
  padding-left: 7mm;
  margin: 0;
}
.num-list li { margin: 0.5mm 0; }

/* ---- Page 2: Appendix inventory ---- */
.page-break { page-break-after: always; }

h2.section-title {
  font-size: 15pt;
  font-weight: 700;
  margin: 0 0 2mm 0;
}
.section-lead {
  margin: 0 0 5mm 0;
  color: #000;
}
h3.subsection-title {
  font-size: 12pt;
  font-weight: 700;
  margin: 5mm 0 2mm 0;
}

.inventory-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 9.5pt;
  margin-bottom: 4mm;
}
.inventory-table th,
.inventory-table td {
  border: 1px solid #000;
  padding: 1.8mm 3mm;
  text-align: left;
  vertical-align: top;
}
.inventory-table thead th {
  background: #D9D9D9;
  font-weight: 700;
  text-align: left;
}
.mono {
  font-family: "Courier New", Courier, monospace;
  font-size: 9pt;
}
"""


# ---- Baseline classifier --------------------------------------------------

BASELINE_MAP = {
    "flexbox": "Widely", "css-grid": "Widely", "css3-colors": "Widely",
    "calc": "Widely", "css-variables": "Widely", "minmaxwh": "Widely",
    "css-filters": "Widely", "css-backdrop-filter": "Widely",
    "css-math-functions": "Widely", "css-logical-props": "Widely",
    "css-has": "Widely",
    "css-container-queries": "Newly", "css-subgrid": "Newly",
    "css-lch-lab": "Newly",
    "css-filter-function": "Limited",
}

def baseline_label(feature_name: str) -> str:
    return BASELINE_MAP.get(feature_name, "Unknown")


# ---- Data prep ------------------------------------------------------------

def _prepare_context(data: dict) -> dict:
    browsers = data["browsers"]

    rows = sorted(
        [{
            "name": name.capitalize(),
            "version": info["version"],
            "pct": info["compatibility_percentage"],
            "supported": info["supported"],
            "partial": info["partial"],
            "unsupported": info["unsupported"],
        } for name, info in browsers.items()],
        key=lambda r: r["pct"],
        reverse=True,
    )

    worst = min(browsers.items(), key=lambda kv: kv[1]["compatibility_percentage"])
    lowest_browser = {
        "name": worst[0].capitalize(),
        "pct": worst[1]["compatibility_percentage"],
    }

    counts = {
        "CSS": data["summary"]["css_features"],
        "HTML": data["summary"]["html_features"],
        "JavaScript": data["summary"]["js_features"],
    }
    primary_category = (
        max(counts, key=counts.get) if any(counts.values()) else "web platform"
    )

    # Unsupported feature → plain-English bullets.
    issue_map: dict[str, list[str]] = {}
    for name, info in browsers.items():
        for feat in info.get("unsupported_features", []):
            issue_map.setdefault(feat, []).append(name.capitalize())

    css_details = data.get("feature_details", {}).get("css", [])
    key_issues = []
    for feat, where in issue_map.items():
        desc = next(
            (d["description"] for d in css_details if d["feature"] == feat),
            feat,
        )
        if len(where) == len(browsers):
            key_issues.append(f"{desc} ({feat}): Unsupported across all browsers.")
        else:
            key_issues.append(
                f"{desc} ({feat}): Unsupported in {', '.join(where)}."
            )

    # Strip leading counts from recommendations like "1 features are not…".
    cleaned_recs = []
    for rec in data.get("recommendations", []):
        stripped = rec.lstrip()
        if stripped and stripped[0].isdigit():
            parts = stripped.split(" ", 1)
            stripped = parts[1] if len(parts) == 2 else stripped
            if stripped:
                stripped = stripped[0].upper() + stripped[1:]
        cleaned_recs.append(stripped)

    feature_details = data.get("feature_details", {})
    inventories = [
        ("CSS", feature_details.get("css", [])),
        ("HTML", feature_details.get("html", [])),
        ("JavaScript", feature_details.get("js", [])),
    ]

    return {
        **{k: v for k, v in data.items() if k != "recommendations"},
        "recommendations": cleaned_recs,
        "rows": rows,
        "lowest_browser": lowest_browser,
        "primary_category": primary_category,
        "key_issues": key_issues,
        "browser_count": len(browsers),
        "browser_list": ", ".join(n.capitalize() for n in browsers),
        "generated_at": datetime.now().strftime("%B %d, %Y"),
        "inventories": inventories,
    }


# ---- Main -----------------------------------------------------------------

def build(json_path: Path, output_path: Path) -> None:
    data = json.loads(json_path.read_text())
    context = _prepare_context(data)

    env = Environment(autoescape=select_autoescape(["html"]))
    env.globals["baseline_label"] = baseline_label
    html_string = env.from_string(HTML_TEMPLATE).render(**context)

    HTML(string=html_string).write_pdf(
        str(output_path),
        stylesheets=[CSS(string=CSS_TEMPLATE)],
    )


def main(argv: list[str]) -> None:
    here = Path(__file__).parent
    json_path = Path(argv[1]) if len(argv) >= 2 else here / "report.json"
    output_path = (
        Path(argv[2]) if len(argv) >= 3
        else here / "compatibility_report_classic.pdf"
    )

    if not json_path.exists():
        print(f"Input not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    build(json_path, output_path)
    print(f"PDF generated: {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main(sys.argv)
