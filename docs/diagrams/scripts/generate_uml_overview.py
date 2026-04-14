"""Generate a simplified architecture overview (~10 classes, clean and compact)."""

import graphviz


def cn(name, stereotype=None):
    if stereotype:
        return (f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="10">'
                f'<tr><td bgcolor="#e8e8e8" align="center"><i>&lt;&lt;{stereotype}&gt;&gt;</i>'
                f'<br/><b>{name}</b></td></tr></table>>')
    return (f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="10">'
            f'<tr><td bgcolor="#e8e8e8" align="center"><b>{name}</b></td></tr></table>>')


def en(name, subtitle=None):
    text = f"<b>{name}</b>"
    if subtitle:
        text += f"<br/><font point-size='9'><i>{subtitle}</i></font>"
    return (f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="10" '
            f'bgcolor="#d9d9d9"><tr><td align="center">{text}</td></tr></table>>')


def build():
    g = graphviz.Digraph(
        'Overview',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'TB',
            'splines': 'true',
            'nodesep': '1.0',
            'ranksep': '1.5',
            'fontname': 'Helvetica',
            'label': '',
            'dpi': '200',
            'pad': '0.5',
        },
        node_attr={'shape': 'plaintext', 'fontname': 'Helvetica', 'fontsize': '12'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '10'},
    )

    # ── Row 1: Frontends ────────────────────────────────
    g.node('MainWindow', cn('MainWindow'))
    g.node('CLI', cn('CLI'))

    # ── Row 2: Facade ───────────────────────────────────
    g.node('AnalyzerService', cn('AnalyzerService', 'facade'))

    # ── Row 3: Core backend ─────────────────────────────
    g.node('CrossGuardAnalyzer', cn('CrossGuardAnalyzer', 'orchestrator'))
    g.node('AIFixService', cn('AIFixService'))
    g.node('PolyfillService', cn('PolyfillService'))
    g.node('AnalysisRepository', cn('AnalysisRepository'))

    # ── Row 4: Parsers + Engine ─────────────────────────
    g.node('HTMLParser', cn('HTMLParser'))
    g.node('CSSParser', cn('CSSParser'))
    g.node('JSParser', cn('JavaScriptParser'))
    g.node('CanIUseDatabase', cn('CanIUseDatabase', 'singleton'))

    # ── Row 5: External systems ─────────────────────────
    g.node('CanIUseData', en('Can I Use Data', 'data/caniuse/'))
    g.node('SQLiteDB', en('SQLite Database', 'crossguard.db'))
    g.node('LLMAPIs', en('LLM APIs', 'OpenAI / Anthropic'))

    # ═══ RELATIONSHIPS ═══════════════════════════════════

    # Frontends -> Facade (dependency)
    g.edge('MainWindow', 'AnalyzerService', style='dashed', arrowhead='open', label='  depends  ')
    g.edge('CLI', 'AnalyzerService', style='dashed', arrowhead='open', label='  depends  ')

    # Facade -> Core (dependency)
    g.edge('AnalyzerService', 'CrossGuardAnalyzer', style='dashed', arrowhead='open', label='  creates  ')
    g.edge('AnalyzerService', 'AIFixService', style='dashed', arrowhead='open', label='  uses  ')
    g.edge('AnalyzerService', 'PolyfillService', style='dashed', arrowhead='open', label='  uses  ')
    g.edge('AnalyzerService', 'AnalysisRepository', style='dashed', arrowhead='open', label='  uses  ')

    # Orchestrator -> Parsers (composition)
    g.edge('CrossGuardAnalyzer', 'HTMLParser', arrowhead='none', arrowtail='diamond', dir='both')
    g.edge('CrossGuardAnalyzer', 'CSSParser', arrowhead='none', arrowtail='diamond', dir='both')
    g.edge('CrossGuardAnalyzer', 'JSParser', arrowhead='none', arrowtail='diamond', dir='both')

    # Orchestrator -> CanIUseDatabase (dependency)
    g.edge('CrossGuardAnalyzer', 'CanIUseDatabase', style='dashed', arrowhead='open', label='  uses  ')

    # External systems (dependency)
    g.edge('CanIUseDatabase', 'CanIUseData', style='dashed', arrowhead='open', label='  reads  ')
    g.edge('AnalysisRepository', 'SQLiteDB', style='dashed', arrowhead='open', label='  stored in  ')
    g.edge('AIFixService', 'LLMAPIs', style='dashed', arrowhead='open', label='  calls  ')

    # ═══ LAYOUT ══════════════════════════════════════════

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('MainWindow')
        s.node('CLI')

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('CrossGuardAnalyzer')
        s.node('AIFixService')
        s.node('PolyfillService')
        s.node('AnalysisRepository')

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('HTMLParser')
        s.node('CSSParser')
        s.node('JSParser')
        s.node('CanIUseDatabase')

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('CanIUseData')
        s.node('SQLiteDB')
        s.node('LLMAPIs')

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('uml_overview', directory='docs/diagrams/images', cleanup=True)
    print(f"Saved: {path}")
