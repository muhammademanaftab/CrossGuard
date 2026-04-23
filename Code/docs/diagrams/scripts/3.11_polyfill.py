"""Sub-diagram: Polyfill System (Section 3.13)."""

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
        'Polyfill',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'LR',
            'splines': 'true',
            'nodesep': '0.4',
            'ranksep': '0.8',
            'fontname': 'Helvetica',
            'label': '',
            'dpi': '200',
            'pad': '0.3',
        },
        node_attr={'shape': 'plaintext', 'fontname': 'Helvetica', 'fontsize': '10'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '9'},
    )

    g.node('PolyfillService', cn('PolyfillService',
        ['- _loader : PolyfillLoader'],
        ['+ get_recommendations(unsupported, partial, browsers) : List',
         '+ get_aggregate_install_command(recs) : str',
         '+ get_aggregate_imports(recs) : List',
         '+ get_total_size_kb(recs) : float',
         '+ categorize_recommendations(recs) : Dict']))

    g.node('PolyfillLoader', cn('PolyfillLoader',
        ['- _data : Dict'],
        ['+ get_polyfill(feature_id) : Dict',
         '+ reload()',
         '- _load_data()'],
        stereotype='singleton'))

    g.node('PolyfillMap', en('polyfill_map.json', 'src/polyfill/'))

    # Relationships
    g.edge('PolyfillService', 'PolyfillLoader', arrowhead='none', label='uses\n\n', minlen='2')
    g.edge('PolyfillLoader', 'PolyfillMap', style='dashed', arrowhead='open', label='reads\n\n', minlen='2')

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('3.11_polyfill', directory='docs/diagrams/images', cleanup=True)
    print(f"Saved: {path}")
