"""Sub-diagram: Database Layer (Section 3.11)."""

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
        'Database',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'TB',
            'splines': 'true',
            'nodesep': '0.7',
            'ranksep': '1.2',
            'fontname': 'Helvetica',
            'label': '',
            'dpi': '200',
            'pad': '0.4',
        },
        node_attr={'shape': 'plaintext', 'fontname': 'Helvetica', 'fontsize': '10'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '9'},
    )

    # ── Repositories ────────────────────────────────────

    g.node('AnalysisRepository', cn('AnalysisRepository',
        ['- _conn : Connection'],
        ['+ save_analysis(a) : int',
         '+ get_all_analyses(limit, offset) : List[Analysis]',
         '+ get_analysis_by_id(id) : Analysis',
         '+ delete_analysis(id) : bool',
         '+ clear_all() : int',
         '+ get_count(file_type) : int']))

    g.node('StatisticsService', cn('StatisticsService',
        ['- _conn : Connection'],
        ['+ get_total_analyses() : int',
         '+ get_average_score() : float',
         '+ get_best_score() : float',
         '+ get_worst_score() : float',
         '+ get_score_trend(days) : List',
         '+ get_top_problematic_features(limit) : List',
         '+ get_grade_distribution() : Dict',
         '+ get_file_type_distribution() : Dict',
         '+ get_summary_statistics() : Dict']))

    # ── Data Models ─────────────────────────────────────

    g.node('Analysis', cn('Analysis',
        ['+ id : int',
         '+ file_name : str',
         '+ file_path : str',
         '+ file_type : str',
         '+ overall_score : float',
         '+ grade : str',
         '+ total_features : int',
         '+ analyzed_at : datetime',
         '+ browsers_json : str',
         '+ features : List[AnalysisFeature]'],
        ['+ to_dict() : Dict',
         '+ from_row(row) : Analysis',
         '+ get_formatted_date() : str']))

    g.node('AnalysisFeature', cn('AnalysisFeature',
        ['+ id : int',
         '+ analysis_id : int',
         '+ feature_id : str',
         '+ feature_name : str',
         '+ category : str',
         '+ browser_results : List[BrowserResult]'],
        ['+ to_dict() : Dict',
         '+ from_row(row) : AnalysisFeature']))

    g.node('BrowserResult', cn('BrowserResult',
        ['+ id : int',
         '+ analysis_feature_id : int',
         '+ browser : str',
         '+ version : str',
         '+ support_status : str'],
        ['+ to_dict() : Dict',
         '+ from_row(row) : BrowserResult']))

    g.node('Bookmark', cn('Bookmark',
        ['+ id : int',
         '+ analysis_id : int',
         '+ note : str',
         '+ created_at : datetime',
         '+ analysis : Analysis'],
        ['+ to_dict() : Dict',
         '+ from_row(row) : Bookmark']))

    g.node('Tag', cn('Tag',
        ['+ id : int',
         '+ name : str',
         '+ color : str',
         '+ created_at : datetime'],
        ['+ to_dict() : Dict',
         '+ from_row(row) : Tag']))

    # ── External ────────────────────────────────────────

    g.node('SQLiteDB', en('SQLite Database', 'crossguard.db'))

    # ═══ RELATIONSHIPS ═══════════════════════════════════

    # Repositories -> SQLite (dependency)
    g.edge('AnalysisRepository', 'SQLiteDB', style='dashed', arrowhead='open', label='  stored in  ')
    g.edge('StatisticsService', 'SQLiteDB', style='dashed', arrowhead='open', label='  queries  ')

    # Repository manages Analysis (association)
    g.edge('AnalysisRepository', 'Analysis', arrowhead='none', label='  manages  ')

    # Aggregation: Analysis contains features, features contain results
    g.edge('Analysis', 'AnalysisFeature', arrowhead='none', arrowtail='odiamond', dir='both', label='  1..*  ')
    g.edge('AnalysisFeature', 'BrowserResult', arrowhead='none', arrowtail='odiamond', dir='both', label='  1..*  ')

    # Bookmark references Analysis (association)
    g.edge('Bookmark', 'Analysis', arrowhead='none', label='  references  ')

    # Analysis <-> Tag many-to-many (association)
    g.edge('Analysis', 'Tag', arrowhead='none', label='  0..*  ')

    # ═══ LAYOUT ══════════════════════════════════════════

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('AnalysisRepository')
        s.node('StatisticsService')

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('Bookmark')
        s.node('Analysis')
        s.node('Tag')

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('sub_database', directory='docs/diagrams/images', cleanup=True)
    print(f"Saved: {path}")
