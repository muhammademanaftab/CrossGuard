"""Generate a clean, balanced Use Case diagram."""

import graphviz


def actor(name, subtitle=None):
    text = f'<font point-size="28">&#9673;</font><br/><b>{name}</b>'
    if subtitle:
        text += f'<br/><font point-size="9">({subtitle})</font>'
    return f'<{text}>'


def external(name, subtitle=None):
    text = f"<b>{name}</b>"
    if subtitle:
        text += f"<br/><font point-size='9'><i>{subtitle}</i></font>"
    return (f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="8" '
            f'bgcolor="#d9d9d9"><tr><td align="center">{text}</td></tr></table>>')


def build():
    g = graphviz.Graph(
        'UseCase',
        format='png',
        engine='neato',
        graph_attr={
            'overlap': 'false',
            'splines': 'true',
            'fontname': 'Helvetica',
            'label': '',
            'dpi': '200',
            'pad': '0.4',
        },
        node_attr={'fontname': 'Helvetica', 'fontsize': '11'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '9', 'color': '#444444'},
    )

    uc = {'shape': 'ellipse', 'style': 'filled', 'fillcolor': '#EEEEEE',
          'color': '#444444', 'fontsize': '11', 'width': '2.2', 'height': '0.6'}

    # ── Actors (left and right) ─────────────────────

    g.node('User', label=actor('User', 'GUI'), shape='none', pos='-5.5,4!')
    g.node('Dev', label=actor('Developer', 'CLI / CI'), shape='none', pos='5.5,4!')

    # ── System label ────────────────────────────────

    g.node('Sys', label='<<font point-size="16"><b>Cross Guard System</b></font>>',
           shape='none', pos='0,6.5!')

    # ── Use Cases (3 columns x 3 rows) ──────────────

    # Column 1 (left, x=-2.5) -- User-focused
    g.node('UC1', label='Upload &\nAnalyze Files', pos='-2.5,5!', **uc)
    g.node('UC2', label='View Results\n& Scores', pos='-2.5,3.5!', **uc)
    g.node('UC3', label='Bookmark & Tag\nAnalyses', pos='-2.5,2!', **uc)

    # Column 2 (center, x=0) -- Shared
    g.node('UC4', label='Select Target\nBrowsers', pos='0,5!', **uc)
    g.node('UC5', label='Export Report\nPDF / JSON / SARIF', pos='0,3.5!', **uc)
    g.node('UC6', label='View History\n& Statistics', pos='0,2!', **uc)

    # Column 3 (right, x=2.5) -- Features & CI
    g.node('UC7', label='Get AI Fix\nSuggestions', pos='2.5,5!', **uc)
    g.node('UC8', label='Get Polyfill\nRecommendations', pos='2.5,3.5!', **uc)
    g.node('UC9', label='Manage Rules\n& Update DB', pos='2.5,2!', **uc)

    # Bottom center -- CI only
    g.node('UC10', label='Run CLI Analysis\n& Quality Gates', pos='0,0.5!', **uc)

    # ── External Systems (bottom row) ───────────────

    ext = {'shape': 'none'}
    g.node('SQL', label=external('SQLite'), pos='-3,-1!', **ext)
    g.node('CIU', label=external('Can I Use DB'), pos='-1,-1!', **ext)
    g.node('LLM', label=external('LLM API', 'OpenAI / Anthropic'), pos='1,-1!', **ext)
    g.node('NPM', label=external('NPM Registry'), pos='3,-1!', **ext)

    # ── User connections ────────────────────────────

    for uc_id in ['UC1', 'UC2', 'UC3', 'UC4', 'UC5', 'UC6', 'UC7', 'UC8', 'UC9']:
        g.edge('User', uc_id)

    # ── Developer connections ───────────────────────

    for uc_id in ['UC1', 'UC5', 'UC6', 'UC9', 'UC10']:
        g.edge('Dev', uc_id)

    # ── External system connections (dashed) ─────────

    g.edge('UC1', 'CIU', style='dashed', label='  Check Support  ')
    g.edge('UC1', 'SQL', style='dashed', label='  Save Results  ')
    g.edge('UC6', 'SQL', style='dashed', label='  Query  ')
    g.edge('UC3', 'SQL', style='dashed', label='  Store  ')
    g.edge('UC7', 'LLM', style='dashed', label='  Generate Fixes  ')
    g.edge('UC9', 'NPM', style='dashed', label='  Fetch Latest  ')
    g.edge('UC9', 'CIU', style='dashed', label='  Update  ')

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('usecase_diagram', directory='docs/diagrams/images', cleanup=True)
    print(f"Saved: {path}")
