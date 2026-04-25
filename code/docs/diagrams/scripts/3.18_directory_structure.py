"""Directory Structure diagram -- same style as other sub-diagrams."""

import graphviz


def build():
    g = graphviz.Digraph(
        'DirectoryStructure',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'TB',
            'fontname': 'Helvetica',
            'label': '',
            'dpi': '200',
            'pad': '0.3',
            'bgcolor': 'white',
        },
        node_attr={'fontname': 'Helvetica', 'fontsize': '10', 'shape': 'plaintext'},
    )

    dirs = [
        ('api/',      'Service',  'Service facade (49 methods) and data contracts'),
        ('cli/',      'Frontend', 'Click CLI (8 commands, quality gates, CI generators)'),
        ('config/',   'Backend',  'Config file support (crossguard.config.json)'),
        ('export/',   'Backend',  '6 export formats (JSON, PDF, SARIF, JUnit, Checkstyle, CSV)'),
        ('analyzer/', 'Backend',  'Compatibility engine (scoring, Can I Use lookup)'),
        ('database/', 'Backend',  'SQLite persistence (4 repositories, migrations)'),
        ('gui/',      'Frontend', 'CustomTkinter GUI (22 widgets)'),
        ('polyfill/', 'Backend',  'Polyfill recommendation engine'),
        ('parsers/',  'Backend',  'HTML/CSS/JS parsers and feature maps'),
        ('utils/',    'Utilities','Logging, constants, and feature-name helpers'),
    ]

    rows = ''
    for name, layer, desc in dirs:
        rows += (
            f'<tr>'
            f'<td align="left"><b>{name}</b></td>'
            f'<td align="left"><i>{layer}</i></td>'
            f'<td align="left">{desc}</td>'
            f'</tr>'
        )

    label = (
        '<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">'
        '<tr><td colspan="3" bgcolor="#e8e8e8" align="center">'
        '<b>src/</b></td></tr>'
        f'{rows}'
        '</table>>'
    )

    g.node('table', label)

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('3.18_directory_structure', directory='docs/diagrams/images', cleanup=True)
    print(f"Saved: {path}")
