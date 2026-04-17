"""Generate a clean high-level UML class diagram (class names + relationships only)."""

import graphviz


def cn(name, stereotype=None):
    """Class node box."""
    if stereotype:
        label = (f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="8">'
                 f'<tr><td bgcolor="#e8e8e8" align="center"><i>&lt;&lt;{stereotype}&gt;&gt;</i>'
                 f'<br/><b>{name}</b></td></tr></table>>')
    else:
        label = (f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="8">'
                 f'<tr><td bgcolor="#e8e8e8" align="center"><b>{name}</b></td></tr></table>>')
    return label


def en(name, subtitle=None):
    """External system node."""
    text = f"<b>{name}</b>"
    if subtitle:
        text += f"<br/><font point-size='8'><i>{subtitle}</i></font>"
    return (f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="8" '
            f'bgcolor="#d9d9d9"><tr><td align="center">{text}</td></tr></table>>')


def dep(g, a, b, lbl=''):
    """Dependency: dashed open arrow."""
    g.edge(a, b, style='dashed', arrowhead='open', label=f'  {lbl}  ' if lbl else '')

def comp(g, whole, part):
    """Composition: filled diamond on whole."""
    g.edge(whole, part, arrowhead='none', arrowtail='diamond', dir='both')

def agg(g, whole, part, lbl=''):
    """Aggregation: hollow diamond on whole."""
    g.edge(whole, part, arrowhead='none', arrowtail='odiamond', dir='both',
           label=f'  {lbl}  ' if lbl else '')

def assoc(g, a, b, lbl=''):
    """Association: solid line."""
    g.edge(a, b, arrowhead='none', label=f'  {lbl}  ' if lbl else '')


def build():
    g = graphviz.Digraph(
        'CrossGuard_HighLevel',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'TB',
            'splines': 'true',
            'nodesep': '0.8',
            'ranksep': '1.3',
            'fontname': 'Helvetica',
            'label': 'Cross Guard — High-Level Class Diagram\n\n',
            'labelloc': 't',
            'fontsize': '18',
            'dpi': '200',
            'pad': '0.5',
        },
        node_attr={'shape': 'plaintext', 'fontname': 'Helvetica', 'fontsize': '11'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '9'},
    )

    # ═══ NODES ═══════════════════════════════════════════

    # Row 1: Frontends
    g.node('MainWindow', cn('MainWindow'))
    g.node('ExportManager', cn('ExportManager'))
    g.node('CLI', cn('CLI', 'Click commands'))

    # Row 2: Facade
    g.node('AnalyzerService', cn('AnalyzerService', 'facade'))

    # Row 3: Left = Orchestrator + data contracts, Right = services
    g.node('CrossGuardAnalyzer', cn('CrossGuardAnalyzer', 'orchestrator'))
    g.node('AnalysisRequest', cn('AnalysisRequest'))
    g.node('AnalysisResult', cn('AnalysisResult'))
    g.node('DatabaseUpdater', cn('DatabaseUpdater'))
    g.node('WebFeaturesManager', cn('WebFeaturesManager'))
    g.node('ConfigManager', cn('ConfigManager'))
    g.node('AIFixService', cn('AIFixService'))
    g.node('PolyfillService', cn('PolyfillService'))

    # Row 4: Parsers (left), Engine + Repos (right)
    g.node('HTMLParser', cn('HTMLParser'))
    g.node('CSSParser', cn('CSSParser'))
    g.node('JSParser', cn('JavaScriptParser'))
    g.node('CompatibilityAnalyzer', cn('CompatibilityAnalyzer'))
    g.node('CompatibilityScorer', cn('CompatibilityScorer'))
    g.node('AnalysisRepository', cn('AnalysisRepository'))
    g.node('StatisticsService', cn('StatisticsService'))

    # Row 5: Singletons + Data models
    g.node('CustomRulesLoader', cn('CustomRulesLoader', 'singleton'))
    g.node('CanIUseDatabase', cn('CanIUseDatabase', 'singleton'))
    g.node('PolyfillLoader', cn('PolyfillLoader', 'singleton'))
    g.node('Analysis', cn('Analysis'))
    g.node('Bookmark', cn('Bookmark'))
    g.node('Tag', cn('Tag'))

    # Row 6: Nested models
    g.node('AnalysisFeature', cn('AnalysisFeature'))
    g.node('BrowserResult', cn('BrowserResult'))

    # Row 7: External systems
    g.node('CanIUseData', en('Can I Use Data', 'data/caniuse/'))
    g.node('NPMRegistry', en('NPM Registry'))
    g.node('SQLiteDB', en('SQLite Database', 'crossguard.db'))
    g.node('LLMAPIs', en('LLM APIs', 'OpenAI / Anthropic'))

    # ═══ RELATIONSHIPS ═══════════════════════════════════

    # -- Composition ◆ --
    comp(g, 'MainWindow', 'ExportManager')
    comp(g, 'CrossGuardAnalyzer', 'HTMLParser')
    comp(g, 'CrossGuardAnalyzer', 'CSSParser')
    comp(g, 'CrossGuardAnalyzer', 'JSParser')
    comp(g, 'CrossGuardAnalyzer', 'CompatibilityAnalyzer')
    comp(g, 'CrossGuardAnalyzer', 'CompatibilityScorer')

    # -- Aggregation ◇ --
    agg(g, 'Analysis', 'AnalysisFeature', '1..*')
    agg(g, 'AnalysisFeature', 'BrowserResult', '1..*')

    # -- Association ── --
    assoc(g, 'AnalysisRepository', 'Analysis', 'manages')
    assoc(g, 'Bookmark', 'Analysis', 'references')
    assoc(g, 'Analysis', 'Tag', '0..*')
    assoc(g, 'PolyfillService', 'PolyfillLoader', 'uses')

    # -- Dependencies - -> --
    dep(g, 'MainWindow', 'AnalyzerService', 'depends')
    dep(g, 'CLI', 'AnalyzerService', 'depends')
    dep(g, 'CLI', 'ConfigManager', 'loads config')

    dep(g, 'AnalyzerService', 'AnalysisRequest', 'accepts')
    dep(g, 'AnalyzerService', 'AnalysisResult', 'returns')
    dep(g, 'AnalyzerService', 'CrossGuardAnalyzer', 'creates')
    dep(g, 'AnalyzerService', 'DatabaseUpdater', 'creates')
    dep(g, 'AnalyzerService', 'WebFeaturesManager', 'creates')
    dep(g, 'AnalyzerService', 'ConfigManager', 'uses')
    dep(g, 'AnalyzerService', 'AnalysisRepository', 'uses')
    dep(g, 'AnalyzerService', 'StatisticsService', 'uses')
    dep(g, 'AnalyzerService', 'AIFixService', 'uses')
    dep(g, 'AnalyzerService', 'PolyfillService', 'uses')

    dep(g, 'CrossGuardAnalyzer', 'CanIUseDatabase', 'uses')
    dep(g, 'HTMLParser', 'CustomRulesLoader', 'loads rules')
    dep(g, 'CSSParser', 'CustomRulesLoader', 'loads rules')
    dep(g, 'JSParser', 'CustomRulesLoader', 'loads rules')
    dep(g, 'CompatibilityAnalyzer', 'CanIUseDatabase', 'queries')

    dep(g, 'CanIUseDatabase', 'CanIUseData', 'reads')
    dep(g, 'DatabaseUpdater', 'CanIUseData', 'updates')
    dep(g, 'DatabaseUpdater', 'NPMRegistry', 'fetches')
    dep(g, 'AnalysisRepository', 'SQLiteDB', 'stored in')
    dep(g, 'StatisticsService', 'SQLiteDB', 'queries')
    dep(g, 'AIFixService', 'LLMAPIs', 'calls')

    # ═══ LAYOUT ══════════════════════════════════════════

    # Row 1
    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('MainWindow')
        s.node('ExportManager')
        s.node('CLI')

    # Row 3: Orchestrator + services on same level
    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('AnalysisResult')
        s.node('CrossGuardAnalyzer')
        s.node('DatabaseUpdater')
        s.node('WebFeaturesManager')
        s.node('AIFixService')
        s.node('PolyfillService')
        s.node('AnalysisRequest')
        s.node('ConfigManager')

    # Row 4: Parsers + engine + repos
    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('HTMLParser')
        s.node('CSSParser')
        s.node('JSParser')
        s.node('CompatibilityAnalyzer')
        s.node('CompatibilityScorer')
        s.node('AnalysisRepository')
        s.node('StatisticsService')

    # Row 5: Singletons + models
    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('CustomRulesLoader')
        s.node('CanIUseDatabase')
        s.node('PolyfillLoader')
        s.node('Bookmark')
        s.node('Analysis')
        s.node('Tag')

    # Row 6
    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('AnalysisFeature')

    # Row 7: External systems
    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('CanIUseData')
        s.node('NPMRegistry')
        s.node('SQLiteDB')
        s.node('LLMAPIs')
        s.node('BrowserResult')

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('3.5_architecture_detailed', directory='docs/diagrams/images', cleanup=True)
    print(f"Saved: {path}")
