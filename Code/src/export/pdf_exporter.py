"""Professional classic-style PDF report via WeasyPrint + Jinja2.

Public API (unchanged): export_pdf(report, output_path) -> str

Runtime deps: weasyprint, jinja2
System deps: pango + cairo (macOS: brew install pango cairo; Debian: apt install libpango-1.0-0 libcairo2)
"""

from datetime import datetime
from typing import Dict, List

from jinja2 import Environment, select_autoescape
from weasyprint import HTML, CSS


# --- Templates ------------------------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Browser Compatibility Report</title></head>
<body>

<h1 class="report-title">Browser Compatibility Report</h1>

<section class="block">
  <p><strong>Executive Summary:</strong></p>
  <p>
    The analyzed code demonstrates
    {% if score >= 90 %}excellent{% elif score >= 80 %}strong{% elif score >= 60 %}moderate{% else %}limited{% endif %}
    cross-browser compatibility with an overall score of
    <strong>{{ score | round(1) }}%</strong>
    (Grade <strong>{{ grade }}</strong>).
    A total of <strong>{{ total_features }} {{ primary_category }} feature{{ "" if total_features == 1 else "s" }}</strong>
    {{ "was" if total_features == 1 else "were" }} detected, with
    {% if critical_issues %}<strong>{{ critical_issues }} critical {{ "issue" if critical_issues == 1 else "issues" }}</strong> identified{% else %}no critical issues identified{% endif %}.
    {% if lowest_browser %}The lowest compatibility was observed in {{ lowest_browser.name }}
    ({{ lowest_browser.pct }}%).{% endif %}
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
    {% for row in browser_rows %}
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

{% if key_issues or baseline.limited or baseline.unknown %}
<section class="block">
  <p><strong>Key Compatibility Issues:</strong></p>
  <ul class="dash-list">
    {% for issue in key_issues %}<li>{{ issue }}</li>{% endfor %}
    {% if baseline.limited %}
    <li>{{ baseline.limited }} feature{{ "" if baseline.limited == 1 else "s" }} with limited baseline availability — fallbacks recommended.</li>
    {% endif %}
    {% if baseline.unknown %}
    <li>{{ baseline.unknown }} feature{{ "" if baseline.unknown == 1 else "s" }} not found in the baseline database — verify support manually.</li>
    {% endif %}
  </ul>
</section>
{% endif %}

{% if baseline.has_data %}
<section class="block">
  <p><strong>Baseline Availability:</strong></p>
  <ul class="dash-list">
    <li><strong>{{ baseline.widely_available }}</strong> widely available feature{{ "" if baseline.widely_available == 1 else "s" }} — safe for production use.</li>
    <li><strong>{{ baseline.newly_available }}</strong> newly available feature{{ "" if baseline.newly_available == 1 else "s" }} — test across older browser versions.</li>
    <li><strong>{{ baseline.limited }}</strong> feature{{ "" if baseline.limited == 1 else "s" }} with limited availability.</li>
    <li><strong>{{ baseline.unknown }}</strong> feature{{ "" if baseline.unknown == 1 else "s" }} with unknown baseline status.</li>
  </ul>
</section>
{% endif %}

{% if recommendations %}
<section class="block">
  <p><strong>Recommendations:</strong></p>
  <ol class="num-list">
    {% for rec in recommendations %}<li>{{ rec }}</li>{% endfor %}
    <li>Perform cross-browser testing for partially supported features.</li>
    <li>Prioritize fixes for high-severity compatibility gaps.</li>
  </ol>
</section>
{% endif %}

<section class="block">
  <p><strong>Report Metadata:</strong></p>
  <p>
    Generated on {{ generated_at }}.
    Analysis covered {{ browser_count }} browser{{ "" if browser_count == 1 else "s" }}:
    {{ browser_list }}.
    Simple score: <strong>{{ scores.simple_score }}</strong>.
    Weighted score: <strong>{{ scores.weighted_score }}</strong>.
    Risk level: <strong>{{ scores.risk_level | lower }}</strong>.
  </p>
</section>

{# ---- Appendix A: Feature Inventory ---- #}
{% if has_any_features %}
<div class="page-break"></div>

<h2 class="section-title">Appendix A — Feature Inventory</h2>
<p class="section-lead">
  Complete list of all {{ total_features }} feature{{ "" if total_features == 1 else "s" }}
  detected across HTML, CSS and JavaScript, with baseline status.
</p>

{% for cat_label, entries in inventories %}
{% if entries %}
<h3 class="subsection-title">{{ cat_label }} Features ({{ entries | length }})</h3>
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
    {% for d in entries %}
    <tr>
      <td class="mono">{{ d.feature }}</td>
      <td>{{ d.description or "—" }}</td>
      <td class="mono">
        {% if d.matched_properties %}{{ d.matched_properties | join(", ") }}{% else %}—{% endif %}
      </td>
      <td>{{ d.baseline or "Unknown" }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endif %}
{% endfor %}

{% if unrecognized_total %}
<h3 class="subsection-title">Unrecognized ({{ unrecognized_total }})</h3>
<p>The following items were detected but not matched against the feature database:</p>
<ul class="dash-list">
  {% for cat, items in unrecognized_by_cat %}
  {% if items %}
  <li><strong>{{ cat }}:</strong> {{ items | join(", ") }}</li>
  {% endif %}
  {% endfor %}
</ul>
{% endif %}
{% endif %}

{# ---- Appendix B: AI Fix Suggestions (conditional) ---- #}
{% if ai_suggestions %}
<div class="page-break"></div>

<h2 class="section-title">Appendix B — AI Fix Suggestions</h2>
<p class="section-lead">
  Code-level suggestions generated by a language model for the most impactful
  compatibility issues detected in the analyzed source.
</p>

{% for s in ai_suggestions %}
<div class="ai-card">
  <p class="ai-name"><strong>{{ s.feature_name or s.feature_id }}</strong></p>
  {% if s.browsers_affected %}
  <p class="ai-meta">Affects: {{ s.browsers_affected | join(", ") }}</p>
  {% endif %}
  {% if s.suggestion %}
  <p>{{ s.suggestion }}</p>
  {% endif %}
  {% if s.code_example %}
  <pre class="ai-code">{{ s.code_example }}</pre>
  {% endif %}
</div>
{% endfor %}
{% endif %}

</body>
</html>
"""

CSS_TEMPLATE = """
@page {
  size: Letter;
  margin: 18mm 22mm 18mm 22mm;
  @bottom-right {
    content: counter(page) " / " counter(pages);
    font-size: 9pt;
    color: #555;
  }
  @bottom-left {
    content: "Cross Guard — Browser Compatibility Report";
    font-size: 9pt;
    color: #555;
  }
}

html, body {
  margin: 0;
  padding: 0;
  font-family: "Cambria", "Georgia", "Times New Roman", serif;
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
  content: "–";
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

/* Appendices */
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
}
.mono {
  font-family: "Courier New", Courier, monospace;
  font-size: 9pt;
}

/* AI Suggestions */
.ai-card {
  border: 1px solid #AAA;
  padding: 3mm 4mm;
  margin-bottom: 3mm;
  page-break-inside: avoid;
}
.ai-name { margin: 0 0 1mm 0; font-size: 11pt; }
.ai-meta { margin: 0 0 1mm 0; font-size: 9pt; color: #444; }
.ai-code {
  font-family: "Courier New", Courier, monospace;
  font-size: 9pt;
  background: #F5F5F5;
  border: 1px solid #CCC;
  padding: 2mm 3mm;
  margin: 1mm 0 0 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
"""


# --- Context preparation --------------------------------------------------

def _prepare_context(report: Dict) -> Dict:
    browsers = report.get('browsers') or {}
    summary = report.get('summary') or {}
    scores = report.get('scores') or {}

    browser_rows = sorted(
        [
            {
                'name': name.capitalize(),
                'version': info.get('version', ''),
                'pct': info.get('compatibility_percentage', 0),
                'supported': info.get('supported', 0),
                'partial': info.get('partial', 0),
                'unsupported': info.get('unsupported', 0),
            }
            for name, info in browsers.items() if isinstance(info, dict)
        ],
        key=lambda r: r['pct'],
        reverse=True,
    )

    lowest_browser = None
    if browsers:
        worst = min(browsers.items(), key=lambda kv: kv[1].get('compatibility_percentage', 100))
        lowest_browser = {
            'name': worst[0].capitalize(),
            'pct': worst[1].get('compatibility_percentage', 0),
        }

    # Primary category = the file type with the most features (for prose).
    counts = {
        'CSS': summary.get('css_features', 0),
        'HTML': summary.get('html_features', 0),
        'JavaScript': summary.get('js_features', 0),
    }
    # Use uppercase for CSS/HTML/JS acronyms; lowercase for generic fallback.
    primary_category = max(counts, key=counts.get) if any(counts.values()) else 'web platform'

    key_issues = _build_key_issues(browsers, report.get('feature_details') or {})
    recommendations = _clean_recommendations(report.get('recommendations') or [])

    # feature_details may be either a dict of lists or a plain list depending on source.
    fd = report.get('feature_details') or {}
    if isinstance(fd, list):
        fd = {'css': fd, 'html': [], 'js': []}
    inventories = [
        ('CSS', fd.get('css') or []),
        ('HTML', fd.get('html') or []),
        ('JavaScript', fd.get('js') or []),
    ]
    total_features = summary.get('total_features') or sum(len(x) for _, x in inventories)

    unrecognized = report.get('unrecognized') or {}
    unrecognized_total = unrecognized.get('total', 0) if isinstance(unrecognized, dict) else 0
    unrecognized_by_cat = [
        (cat.upper(), unrecognized.get(cat, []) if isinstance(unrecognized, dict) else [])
        for cat in ('html', 'css', 'js')
    ]

    baseline_ctx = _build_baseline_ctx(report.get('baseline_summary'))

    return {
        'scores': {
            'simple_score': scores.get('simple_score', 0),
            'weighted_score': scores.get('weighted_score', 0),
            'risk_level': scores.get('risk_level', 'none'),
        },
        'score': float(scores.get('weighted_score', 0) or 0),
        'grade': scores.get('grade', 'N/A'),
        'total_features': total_features,
        'critical_issues': summary.get('critical_issues', 0),
        'primary_category': primary_category,
        'browser_rows': browser_rows,
        'lowest_browser': lowest_browser,
        'key_issues': key_issues,
        'recommendations': recommendations,
        'baseline': baseline_ctx,
        'inventories': inventories,
        'has_any_features': any(bool(entries) for _, entries in inventories),
        'unrecognized_total': unrecognized_total,
        'unrecognized_by_cat': unrecognized_by_cat,
        'ai_suggestions': report.get('ai_suggestions') or [],
        'browser_count': len(browsers),
        'browser_list': ', '.join(n.capitalize() for n in browsers) if browsers else 'none',
        'generated_at': datetime.now().strftime('%B %d, %Y'),
    }


def _build_key_issues(browsers: Dict, feature_details: Dict) -> List[str]:
    # description lookup by feature id (first match across categories wins)
    descriptions = {}
    if isinstance(feature_details, dict):
        for cat_entries in feature_details.values():
            if isinstance(cat_entries, list):
                for entry in cat_entries:
                    fid = entry.get('feature')
                    desc = entry.get('description')
                    if fid and desc and fid not in descriptions:
                        descriptions[fid] = desc

    issue_map: Dict[str, List[str]] = {}
    for name, info in browsers.items():
        if not isinstance(info, dict):
            continue
        for feat in info.get('unsupported_features') or []:
            issue_map.setdefault(feat, []).append(name.capitalize())

    issues = []
    total_browsers = len(browsers)
    for feat, where in issue_map.items():
        desc = descriptions.get(feat, feat)
        if len(where) == total_browsers and total_browsers > 0:
            issues.append(f"{desc} ({feat}): unsupported across all browsers.")
        else:
            issues.append(f"{desc} ({feat}): unsupported in {', '.join(where)}.")
    return issues


def _clean_recommendations(recs: List[str]) -> List[str]:
    """Strip leading 'N ' counts and capitalize so prose flows naturally."""
    cleaned = []
    for rec in recs:
        s = rec.lstrip()
        if s and s[0].isdigit():
            parts = s.split(' ', 1)
            s = parts[1] if len(parts) == 2 else s
            if s:
                s = s[0].upper() + s[1:]
        cleaned.append(s)
    return cleaned


def _build_baseline_ctx(baseline_summary) -> Dict:
    if not isinstance(baseline_summary, dict):
        return {
            'has_data': False,
            'widely_available': 0,
            'newly_available': 0,
            'limited': 0,
            'unknown': 0,
        }
    return {
        'has_data': True,
        'widely_available': baseline_summary.get('widely_available', 0),
        'newly_available': baseline_summary.get('newly_available', 0),
        'limited': baseline_summary.get('limited', 0),
        'unknown': baseline_summary.get('unknown', 0),
    }


# --- Public API -----------------------------------------------------------

def export_pdf(report: Dict, output_path: str) -> str:
    if not report:
        raise ValueError("No analysis report to export")

    context = _prepare_context(report)

    env = Environment(autoescape=select_autoescape(['html']))
    html_string = env.from_string(HTML_TEMPLATE).render(**context)

    HTML(string=html_string).write_pdf(
        str(output_path),
        stylesheets=[CSS(string=CSS_TEMPLATE)],
    )
    return output_path
