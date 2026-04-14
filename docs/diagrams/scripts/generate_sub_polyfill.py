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

    g.node('PolyfillService', cn('PolyfillService',
        ['- _loader : PolyfillLoader'],
        ['+ get_recommendations(unsupported, partial, browsers) : List',
         '+ get_aggregate_install_command(recs) : str',
         '+ get_aggregate_imports(recs) : List',
         '+ get_total_size_kb(recs) : float']))

    g.node('PolyfillLoader', cn('PolyfillLoader',
        ['- _data : Dict'],
        ['+ get_polyfill(feature_id) : Dict',
         '+ has_polyfill(feature_id) : bool',
         '+ is_polyfillable(feature_id) : bool',
         '+ reload()',
         '- _load_data()'],
        stereotype='singleton'))

    g.node('PolyfillMap', en('polyfill_map.json', 'src/polyfill/'))

    # Relationships
    g.edge('PolyfillService', 'PolyfillLoader', arrowhead='none', label='  uses  ')
    g.edge('PolyfillLoader', 'PolyfillMap', style='dashed', arrowhead='open', label='  reads  ')

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('sub_polyfill', directory='docs/diagrams/images', cleanup=True)
    print(f"Saved: {path}")
