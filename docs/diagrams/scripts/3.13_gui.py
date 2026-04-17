"""Sub-diagram: GUI Structure (Section 3.15)."""

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


def build():
    g = graphviz.Digraph(
        'GUI',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'LR',
            'splines': 'true',
            'nodesep': '0.3',
            'ranksep': '0.7',
            'fontname': 'Helvetica',
            'label': '',
            'dpi': '200',
            'pad': '0.3',
        },
        node_attr={'shape': 'plaintext', 'fontname': 'Helvetica', 'fontsize': '10'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '9'},
    )

    g.node('MainWindow', cn('MainWindow',
        ['- _analyzer_service : AnalyzerService',
         '- current_report : Dict',
         '- export_manager : ExportManager',
         '- _current_view : str',
         '- sidebar : Sidebar',
         '- header : HeaderBar',
         '- content_frame : CTkFrame',
         '- status_bar : StatusBar'],
        ['- _init_layout()',
         '- _show_view(view_id)',
         '- _build_files_view()',
         '- _build_results_view()',
         '- _build_history_view()',
         '- _build_settings_view()',
         '- _on_files_dropped(files)',
         '- _on_navigate(view_id)',
         '- ...  (35 private methods total)']))

    g.node('ExportManager', cn('ExportManager',
        ['+ parent : CTk'],
        ['+ export_json(report)',
         '+ export_pdf(report)']))

    g.node('AnalyzerService', cn('AnalyzerService',
        ['- _analyzer : CrossGuardAnalyzer',
         '+ DEFAULT_BROWSERS : Dict'],
        ['+ analyze(request) : AnalysisResult',
         '+ get_analysis_history(limit) : List',
         '+ get_statistics() : Dict',
         '+ get_setting(key) : str',
         '+ set_setting(key, value) : bool',
         '+ save_analysis_to_history(result) : int',
         '+ add_bookmark(analysis_id, note) : bool',
         '+ get_all_tags() : List',
         '+ ...  (57 public methods total)'],
        stereotype='facade'))

    # ═══ RELATIONSHIPS ═══════════════════════════════════

    # MainWindow owns ExportManager (composition)
    g.edge('MainWindow', 'ExportManager', arrowhead='none', arrowtail='diamond', dir='both')

    # MainWindow depends on AnalyzerService
    g.edge('MainWindow', 'AnalyzerService', style='dashed', arrowhead='open', label='depends\n\n', minlen='2')

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('3.13_gui', directory='docs/diagrams/images', cleanup=True)
    print(f"Saved: {path}")
