"""Generate the Cross Guard Use Case diagram as a PNG image."""

import graphviz


def build():
    g = graphviz.Digraph(
        'CrossGuard_UseCase',
        format='png',
        engine='neato',
        graph_attr={
            'fontname': 'Helvetica',
            'label': 'Cross Guard — Use Case Diagram\n\n',
            'labelloc': 't',
            'fontsize': '18',
            'dpi': '200',
            'pad': '0.5',
            'overlap': 'false',
            'splines': 'true',
        },
        node_attr={'fontname': 'Helvetica', 'fontsize': '10'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '8', 'arrowhead': 'none'},
    )

    # ── Actors ──────────────────────────────────────────

    g.node('User',
        label='<<table border="0"><tr><td><font point-size="28">&#9673;</font></td></tr>'
              '<tr><td><b>User</b></td></tr><tr><td><font point-size="8">(GUI)</font></td></tr></table>>',
        shape='none', pos='-6,8!')

    g.node('Developer',
        label='<<table border="0"><tr><td><font point-size="28">&#9673;</font></td></tr>'
              '<tr><td><b>Developer</b></td></tr><tr><td><font point-size="8">(CLI / CI)</font></td></tr></table>>',
        shape='none', pos='6,8!')

    # ── Use Cases ───────────────────────────────────────

    uc = {'shape': 'ellipse', 'style': 'filled', 'fillcolor': '#e8e8e8',
          'fontsize': '9', 'width': '1.8', 'height': '0.5'}

    # Row 1 - Core
    g.node('UC_Upload', label='Upload Files\n(drag-drop / picker)', pos='-5,5.5!', **uc)
    g.node('UC_Analyze', label='Analyze\nCompatibility', pos='-2,5.5!', **uc)
    g.node('UC_ViewResults', label='View Results\n(scores, issues)', pos='1,5.5!', **uc)
    g.node('UC_SelectBrowsers', label='Select Target\nBrowsers', pos='4,5.5!', **uc)

    # Row 2 - History & Export
    g.node('UC_ViewHistory', label='View Analysis\nHistory', pos='-4.5,4!', **uc)
    g.node('UC_Bookmark', label='Bookmark\nAnalysis', pos='-1.5,4!', **uc)
    g.node('UC_Tag', label='Tag Analysis', pos='1.5,4!', **uc)
    g.node('UC_Export', label='Export Report\n(PDF/JSON/SARIF/CSV)', pos='4.5,4!', **uc)

    # Row 3 - AI & Config
    g.node('UC_AIFix', label='Get AI Fix\nSuggestions', pos='-4.5,2.5!', **uc)
    g.node('UC_Polyfill', label='Get Polyfill\nRecommendations', pos='-1.5,2.5!', **uc)
    g.node('UC_CustomRules', label='Manage Custom\nDetection Rules', pos='1.5,2.5!', **uc)
    g.node('UC_Stats', label='View Statistics\n(trends, top issues)', pos='4.5,2.5!', **uc)

    # Row 4 - CI/CD
    g.node('UC_CLI', label='Run CLI Analysis\n(CI/CD pipeline)', pos='-2,1!', **uc)
    g.node('UC_QualityGate', label='Quality Gate\n(fail on score)', pos='1,1!', **uc)
    g.node('UC_GenCI', label='Generate CI Config\n(GitHub/GitLab)', pos='4,1!', **uc)
    g.node('UC_UpdateDB', label='Update Can I Use\nDatabase', pos='7,2.5!', **uc)

    # ── System Boundary (drawn as a background box) ─────

    g.node('SysBoundary',
        label='<<table border="1" cellpadding="0" cellspacing="0" color="#333333">'
              '<tr><td width="750" height="350" bgcolor="#fafafa00" align="center" valign="top">'
              '<font point-size="12"><b>Cross Guard System</b></font>'
              '</td></tr></table>>',
        shape='none', pos='1,3.25!', width='0', height='0')

    # ── External Systems ────────────────────────────────

    ext = {'shape': 'none'}

    g.node('CanIUseDB',
        label='<<table border="0"><tr><td><font point-size="20">&#9676;</font></td></tr>'
              '<tr><td><font point-size="9"><b>Can I Use DB</b></font></td></tr></table>>',
        pos='-2,-1!', **ext)

    g.node('SQLite',
        label='<<table border="0"><tr><td><font point-size="20">&#9676;</font></td></tr>'
              '<tr><td><font point-size="9"><b>SQLite</b></font></td></tr></table>>',
        pos='0,-1!', **ext)

    g.node('LLMApi',
        label='<<table border="0"><tr><td><font point-size="20">&#9676;</font></td></tr>'
              '<tr><td><font point-size="9"><b>LLM API</b></font></td></tr>'
              '<tr><td><font point-size="8">(OpenAI/Anthropic)</font></td></tr></table>>',
        pos='-5,-1!', **ext)

    g.node('NPM',
        label='<<table border="0"><tr><td><font point-size="20">&#9676;</font></td></tr>'
              '<tr><td><font point-size="9"><b>NPM Registry</b></font></td></tr></table>>',
        pos='5,-1!', **ext)

    # ═══════════════════════════════════════════════════════
    #  CONNECTIONS
    # ═══════════════════════════════════════════════════════

    # User -> Use Cases
    for uc_name in ['UC_Upload', 'UC_Analyze', 'UC_ViewResults', 'UC_SelectBrowsers',
                     'UC_ViewHistory', 'UC_Bookmark', 'UC_Tag', 'UC_Export',
                     'UC_AIFix', 'UC_Polyfill', 'UC_CustomRules', 'UC_Stats']:
        g.edge('User', uc_name)

    # Developer -> Use Cases
    for uc_name in ['UC_CLI', 'UC_QualityGate', 'UC_GenCI',
                     'UC_Analyze', 'UC_Export', 'UC_UpdateDB', 'UC_Stats']:
        g.edge('Developer', uc_name)

    # Use Cases -> External Systems (dashed)
    g.edge('UC_Analyze', 'CanIUseDB', label=' Check Support', style='dashed', arrowhead='vee')
    g.edge('UC_Analyze', 'SQLite', label=' Save Results', style='dashed', arrowhead='vee')
    g.edge('UC_ViewHistory', 'SQLite', label=' Load', style='dashed', arrowhead='vee')
    g.edge('UC_Bookmark', 'SQLite', label=' Store', style='dashed', arrowhead='vee')
    g.edge('UC_Stats', 'SQLite', label=' Query', style='dashed', arrowhead='vee')
    g.edge('UC_AIFix', 'LLMApi', label=' Generate Fixes', style='dashed', arrowhead='vee')
    g.edge('UC_UpdateDB', 'NPM', label=' Fetch Latest', style='dashed', arrowhead='vee')
    g.edge('UC_UpdateDB', 'CanIUseDB', label=' Update', style='dashed', arrowhead='vee')

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('usecase_diagram', directory='docs', cleanup=True)
    print(f"Saved: {path}")
