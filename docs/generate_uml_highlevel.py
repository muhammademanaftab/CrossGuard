"""Generate a clean high-level UML diagram (class names + relationships only, no methods/attrs)."""

import graphviz


def class_node(name, stereotype=None):
    """Simple class box with just the name."""
    if stereotype:
        label = f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="8"><tr><td bgcolor="#e8e8e8" align="center">&lt;&lt;{stereotype}&gt;&gt;<br/><b>{name}</b></td></tr></table>>'
    else:
        label = f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="8"><tr><td bgcolor="#e8e8e8" align="center"><b>{name}</b></td></tr></table>>'
    return label


def ext_node(name, subtitle=None):
    """External system box."""
    text = f"<b>{name}</b>"
    if subtitle:
        text += f"<br/><font point-size='8'><i>{subtitle}</i></font>"
    return f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="8" bgcolor="#d9d9d9"><tr><td align="center">{text}</td></tr></table>>'


def build():
    g = graphviz.Digraph(
        'CrossGuard_HighLevel',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'TB',
            'splines': 'true',
            'nodesep': '0.6',
            'ranksep': '1.0',
            'fontname': 'Helvetica',
            'label': 'Cross Guard — High-Level Class Diagram\n\n',
            'labelloc': 't',
            'fontsize': '18',
            'dpi': '200',
            'pad': '0.4',
            'margin': '0.3',
        },
        node_attr={'shape': 'plaintext', 'fontname': 'Helvetica', 'fontsize': '11'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '9'},
    )

    # ── Classes ─────────────────────────────────────────

    g.node('MainWindow', class_node('MainWindow'))
    g.node('ExportManager', class_node('ExportManager'))
    g.node('CLI', class_node('CLI', 'Click commands'))

    g.node('AnalysisRequest', class_node('AnalysisRequest'))
    g.node('AnalysisResult', class_node('AnalysisResult'))

    g.node('AnalyzerService', class_node('AnalyzerService', 'facade'))

    g.node('CrossGuardAnalyzer', class_node('CrossGuardAnalyzer', 'orchestrator'))

    g.node('HTMLParser', class_node('HTMLParser'))
    g.node('CSSParser', class_node('CSSParser'))
    g.node('JSParser', class_node('JavaScriptParser'))
    g.node('CustomRulesLoader', class_node('CustomRulesLoader', 'singleton'))

    g.node('CompatibilityAnalyzer', class_node('CompatibilityAnalyzer'))
    g.node('CompatibilityScorer', class_node('CompatibilityScorer'))
    g.node('CanIUseDatabase', class_node('CanIUseDatabase', 'singleton'))

    g.node('DatabaseUpdater', class_node('DatabaseUpdater'))
    g.node('WebFeaturesManager', class_node('WebFeaturesManager'))
    g.node('ConfigManager', class_node('ConfigManager'))

    g.node('AIFixService', class_node('AIFixService'))
    g.node('PolyfillService', class_node('PolyfillService'))
    g.node('PolyfillLoader', class_node('PolyfillLoader', 'singleton'))

    g.node('AnalysisRepository', class_node('AnalysisRepository'))
    g.node('StatisticsService', class_node('StatisticsService'))

    g.node('Analysis', class_node('Analysis'))
    g.node('AnalysisFeature', class_node('AnalysisFeature'))
    g.node('BrowserResult', class_node('BrowserResult'))
    g.node('Bookmark', class_node('Bookmark'))
    g.node('Tag', class_node('Tag'))

    # ── External Systems ────────────────────────────────

    g.node('SQLiteDB', ext_node('SQLite Database', 'crossguard.db'))
    g.node('CanIUseData', ext_node('Can I Use Data', 'data/caniuse/'))
    g.node('LLMAPIs', ext_node('LLM APIs', 'OpenAI / Anthropic'))
    g.node('NPMRegistry', ext_node('NPM Registry'))

    # ── Edges ───────────────────────────────────────────

    # Frontends
    g.edge('MainWindow', 'ExportManager', arrowhead='diamond', dir='back', label=' composition')
    g.edge('MainWindow', 'AnalyzerService', style='dashed', arrowhead='vee', label=' depends')
    g.edge('CLI', 'AnalyzerService', style='dashed', arrowhead='vee', label=' depends')
    g.edge('CLI', 'ConfigManager', style='dashed', arrowhead='vee', label=' loads config')

    # Facade I/O
    g.edge('AnalyzerService', 'AnalysisRequest', style='dashed', arrowhead='vee', label=' accepts')
    g.edge('AnalyzerService', 'AnalysisResult', style='dashed', arrowhead='vee', label=' returns')

    # Facade -> Backend
    g.edge('AnalyzerService', 'CrossGuardAnalyzer', style='dashed', arrowhead='vee', label=' creates')
    g.edge('AnalyzerService', 'DatabaseUpdater', style='dashed', arrowhead='vee', label=' creates')
    g.edge('AnalyzerService', 'WebFeaturesManager', style='dashed', arrowhead='vee', label=' creates')
    g.edge('AnalyzerService', 'ConfigManager', style='dashed', arrowhead='vee', label=' uses')
    g.edge('AnalyzerService', 'AnalysisRepository', style='dashed', arrowhead='vee', label=' uses')
    g.edge('AnalyzerService', 'StatisticsService', style='dashed', arrowhead='vee', label=' uses')
    g.edge('AnalyzerService', 'AIFixService', style='dashed', arrowhead='vee', label=' uses')
    g.edge('AnalyzerService', 'PolyfillService', style='dashed', arrowhead='vee', label=' uses')

    # Orchestrator compositions
    g.edge('CrossGuardAnalyzer', 'HTMLParser', arrowhead='diamond', dir='back')
    g.edge('CrossGuardAnalyzer', 'CSSParser', arrowhead='diamond', dir='back')
    g.edge('CrossGuardAnalyzer', 'JSParser', arrowhead='diamond', dir='back')
    g.edge('CrossGuardAnalyzer', 'CompatibilityAnalyzer', arrowhead='diamond', dir='back')
    g.edge('CrossGuardAnalyzer', 'CompatibilityScorer', arrowhead='diamond', dir='back')
    g.edge('CrossGuardAnalyzer', 'CanIUseDatabase', style='dashed', arrowhead='vee', label=' uses')

    # Parsers -> rules
    g.edge('HTMLParser', 'CustomRulesLoader', style='dashed', arrowhead='vee', label=' loads rules')
    g.edge('CSSParser', 'CustomRulesLoader', style='dashed', arrowhead='vee', label=' loads rules')
    g.edge('JSParser', 'CustomRulesLoader', style='dashed', arrowhead='vee', label=' loads rules')

    # Compatibility
    g.edge('CompatibilityAnalyzer', 'CanIUseDatabase', style='dashed', arrowhead='vee', label=' queries')
    g.edge('CanIUseDatabase', 'CanIUseData', style='dashed', arrowhead='vee', label=' reads')

    # Database updater
    g.edge('DatabaseUpdater', 'CanIUseData', style='dashed', arrowhead='vee', label=' updates')
    g.edge('DatabaseUpdater', 'NPMRegistry', style='dashed', arrowhead='vee', label=' fetches')

    # Persistence
    g.edge('AnalysisRepository', 'SQLiteDB', style='dashed', arrowhead='vee', label=' stored in')
    g.edge('StatisticsService', 'SQLiteDB', style='dashed', arrowhead='vee', label=' queries')
    g.edge('AnalysisRepository', 'Analysis', style='dashed', arrowhead='vee', label=' manages')

    # Data model
    g.edge('Analysis', 'AnalysisFeature', arrowhead='odiamond', dir='back', label=' 1..*')
    g.edge('AnalysisFeature', 'BrowserResult', arrowhead='odiamond', dir='back', label=' 1..*')
    g.edge('Bookmark', 'Analysis', style='dashed', arrowhead='vee', label=' references')
    g.edge('Analysis', 'Tag', style='dashed', arrowhead='vee', label=' 0..*')

    # Polyfill
    g.edge('PolyfillService', 'PolyfillLoader', style='dashed', arrowhead='vee', label=' uses')

    # AI
    g.edge('AIFixService', 'LLMAPIs', style='dashed', arrowhead='vee', label=' calls')

    # ── Layout ──────────────────────────────────────────

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('MainWindow')
        s.node('ExportManager')
        s.node('CLI')

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('AnalysisRequest')
        s.node('AnalysisResult')

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('DatabaseUpdater')
        s.node('WebFeaturesManager')
        s.node('ConfigManager')
        s.node('AIFixService')
        s.node('PolyfillService')

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('HTMLParser')
        s.node('CSSParser')
        s.node('JSParser')
        s.node('CompatibilityAnalyzer')
        s.node('CompatibilityScorer')
        s.node('AnalysisRepository')
        s.node('StatisticsService')

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('CustomRulesLoader')
        s.node('CanIUseDatabase')
        s.node('Analysis')
        s.node('PolyfillLoader')
        s.node('Bookmark')
        s.node('Tag')

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('CanIUseData')
        s.node('NPMRegistry')
        s.node('SQLiteDB')
        s.node('LLMAPIs')
        s.node('AnalysisFeature')

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('uml_class_diagram_highlevel', directory='docs', cleanup=True)
    print(f"Saved: {path}")
