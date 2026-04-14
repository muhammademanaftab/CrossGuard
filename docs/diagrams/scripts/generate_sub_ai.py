"""Sub-diagram: AI Fix Suggestions (Section 3.14)."""

import graphviz


def cn(name, attrs=None, methods=None, stereotype=None):
    header = f"<b>{name}</b>"
    if stereotype:
        header = f"<i>&lt;&lt;{stereotype}&gt;&gt;</i><br/><b>{name}</b>"
    label = '<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">'
    label += f'<tr><td bgcolor="#e8e8e8" align="center">{header}</td></tr>'
    if attrs:
        label += f'<tr><td align="left" balign="left">{"<br/>".join(attrs)}</td></tr>'
    else:
        label += '<tr><td> </td></tr>'
    if methods:
        label += f'<tr><td align="left" balign="left">{"<br/>".join(methods)}</td></tr>'
    else:
        label += '<tr><td> </td></tr>'
    label += '</table>>'
    return label


def en(name, subtitle=None):
    text = f"<b>{name}</b>"
    if subtitle:
        text += f"<br/><font point-size='9'><i>{subtitle}</i></font>"
    return (f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="8" '
            f'bgcolor="#d9d9d9"><tr><td align="center">{text}</td></tr></table>>')


def build():
    g = graphviz.Digraph(
        'AIFix',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'TB',
            'splines': 'true',
            'nodesep': '1.0',
            'ranksep': '1.3',
            'fontname': 'Helvetica',
            'label': '',
            'dpi': '200',
            'pad': '0.4',
        },
        node_attr={'shape': 'plaintext', 'fontname': 'Helvetica', 'fontsize': '10'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '9'},
    )

    g.node('AIFixService', cn('AIFixService',
        ['- _api_key : str',
         '- _provider : str',
         '- _model : str',
         '- _max_features : int',
         '- _priority : str',
         '+ ANTHROPIC_URL : str',
         '+ OPENAI_URL : str',
         '+ DEFAULT_MODELS : Dict'],
        ['+ is_available() : bool',
         '+ get_fix_suggestions(features, type, browsers) : List',
         '- _build_prompt(features, type) : str',
         '- _call_api(prompt) : str',
         '- _call_anthropic(prompt) : str',
         '- _call_openai(prompt) : str',
         '- _parse_response(raw, features) : List']))

    g.node('LLMAPIs', en('LLM APIs', 'OpenAI / Anthropic'))

    # Relationship
    g.edge('AIFixService', 'LLMAPIs', style='dashed', arrowhead='open', label='  calls  ')

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('sub_ai', directory='docs/diagrams/images', cleanup=True)
    print(f"Saved: {path}")
