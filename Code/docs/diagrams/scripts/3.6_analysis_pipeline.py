"""Sub-diagram: Analysis Pipeline (Section 3.6) -- clean centered layout."""

import graphviz


def cn(name, attrs=None, methods=None, stereotype=None):
    header = f"<b>{name}</b>"
    if stereotype:
        header = f"<i>&lt;&lt;{stereotype}&gt;&gt;</i><br/><b>{name}</b>"
    label = '<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">'
    label += f'<tr><td bgcolor="#e8e8e8" align="center">{header}</td></tr>'
    if attrs:
        label += f'<tr><td align="left" balign="left">{"<br/>".join(attrs)}</td></tr>'
    if methods:
        label += f'<tr><td align="left" balign="left">{"<br/>".join(methods)}</td></tr>'
    label += '</table>>'
    return label


def build():
    g = graphviz.Digraph(
        'AnalysisPipeline',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'TB',
            'splines': 'true',
            'nodesep': '0.4',
            'ranksep': '0.9',
            'fontname': 'Helvetica',
            'label': '',
            'dpi': '200',
            'pad': '0.3',
        },
        node_attr={'shape': 'plaintext', 'fontname': 'Helvetica', 'fontsize': '10'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '9'},
    )

    # ── Row 1: Data Contracts + Facade ──────────────────

    g.node('AnalysisRequest', cn('AnalysisRequest',
        ['+ html_files : List[str]',
         '+ css_files : List[str]',
         '+ js_files : List[str]',
         '+ target_browsers : Dict'],
        ['+ has_files() : bool',
         '+ total_files() : int']))

    g.node('AnalyzerService', cn('AnalyzerService',
        ['- _analyzer : CrossGuardAnalyzer',
         '+ DEFAULT_BROWSERS : Dict'],
        ['+ analyze(request) : AnalysisResult',
         '+ analyze_files(html, css, js, browsers) : AnalysisResult',
         '+ ...  (49 public methods total)'],
        stereotype='facade'))

    g.node('AnalysisResult', cn('AnalysisResult',
        ['+ success : bool',
         '+ summary : Dict',
         '+ scores : Dict',
         '+ browsers : Dict',
         '+ detected_features : Dict',
         '+ recommendations : List[str]'],
        ['+ from_dict(data) : AnalysisResult',
         '+ to_dict() : Dict']))

    # ── Row 2: Orchestrator ─────────────────────────────

    g.node('CrossGuardAnalyzer', cn('CrossGuardAnalyzer',
        ['+ html_parser : HTMLParser',
         '+ css_parser : CSSParser',
         '+ js_parser : JavaScriptParser',
         '+ compatibility_analyzer : CompatibilityAnalyzer',
         '+ scorer : CompatibilityScorer',
         '+ all_features : Set[str]'],
        ['+ run_analysis(html, css, js, browsers) : Dict',
         '- _parse_html_files(files)',
         '- _parse_css_files(files)',
         '- _parse_js_files(files)',
         '- _check_compatibility(browsers) : Dict',
         '- _calculate_scores(results, browsers) : Dict',
         '- _generate_report(results, scores, browsers) : Dict',
         '- ...  (11 private methods total)'],
        stereotype='orchestrator'))

    # ── Row 3: Parsers + Engine ─────────────────────────

    g.node('HTMLParser', cn('HTMLParser',
        ['+ features_found : Set[str]'],
        ['+ parse_file(path) : Set[str]',
         '+ parse_string(html) : Set[str]',
         '+ ...  (6 public methods total)',
         '- ...  (17 private methods total)']))

    g.node('CSSParser', cn('CSSParser',
        ['+ features_found : Set[str]'],
        ['+ parse_file(path) : Set[str]',
         '+ parse_string(css) : Set[str]',
         '+ ...  (6 public methods total)',
         '- ...  (5 private methods total)']))

    g.node('JSParser', cn('JavaScriptParser',
        ['+ features_found : Set[str]'],
        ['+ parse_file(path) : Set[str]',
         '+ parse_string(js) : Set[str]',
         '+ ...  (6 public methods total)',
         '- ...  (13 private methods total)']))

    g.node('CompatibilityAnalyzer', cn('CompatibilityAnalyzer',
        ['+ database : CanIUseDatabase'],
        ['+ classify_features(features, browsers) : Dict']))

    g.node('CompatibilityScorer', cn('CompatibilityScorer',
        ['+ STATUS_SCORES : Dict'],
        ['+ score_statuses(statuses) : float',
         '+ overall_score(browser_pcts) : float',
         '+ grade(score) : str',
         '+ risk_level(score, unsup) : str']))

    # ── Row 4: Database ─────────────────────────────────

    g.node('CanIUseDatabase', cn('CanIUseDatabase',
        ['+ features : Dict',
         '+ loaded : bool'],
        ['+ load() : bool',
         '+ get_feature(feature_id) : Dict',
         '+ check_support(feature, browser, ver) : str',
         '- ...  (5 private methods total)'],
        stereotype='singleton'))

    # ═══ RELATIONSHIPS ═══════════════════════════════════

    # Facade <-> data contracts
    g.edge('AnalysisRequest', 'AnalyzerService', style='dashed', arrowhead='open', label=' accepts ')
    g.edge('AnalyzerService', 'AnalysisResult', style='dashed', arrowhead='open', label=' returns ')

    # Facade -> orchestrator
    g.edge('AnalyzerService', 'CrossGuardAnalyzer', style='dashed', arrowhead='open', label=' creates ')

    # Orchestrator -> composed parts
    g.edge('CrossGuardAnalyzer', 'HTMLParser', arrowhead='none', arrowtail='diamond', dir='both')
    g.edge('CrossGuardAnalyzer', 'CSSParser', arrowhead='none', arrowtail='diamond', dir='both')
    g.edge('CrossGuardAnalyzer', 'JSParser', arrowhead='none', arrowtail='diamond', dir='both')
    g.edge('CrossGuardAnalyzer', 'CompatibilityAnalyzer', arrowhead='none', arrowtail='diamond', dir='both')
    g.edge('CrossGuardAnalyzer', 'CompatibilityScorer', arrowhead='none', arrowtail='diamond', dir='both')

    # CompatibilityAnalyzer -> database (orchestrator delegates all DB lookups here)
    g.edge('CompatibilityAnalyzer', 'CanIUseDatabase', style='dashed', arrowhead='open', label=' queries ')

    # ═══ LAYOUT ══════════════════════════════════════════

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('AnalysisRequest')
        s.node('AnalyzerService')
        s.node('AnalysisResult')

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('HTMLParser')
        s.node('CSSParser')
        s.node('JSParser')
        s.node('CompatibilityAnalyzer')
        s.node('CompatibilityScorer')

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('3.6_analysis_pipeline', directory='docs/diagrams/images', cleanup=True)
    print(f"Saved: {path}")
