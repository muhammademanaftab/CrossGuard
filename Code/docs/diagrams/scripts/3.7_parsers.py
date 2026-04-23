"""Sub-diagram: Parsers (Section 3.8)."""

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
        'Parsers',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'TB',
            'splines': 'true',
            'nodesep': '0.8',
            'ranksep': '1.3',
            'fontname': 'Helvetica',
            'label': '',
            'dpi': '200',
            'pad': '0.4',
        },
        node_attr={'shape': 'plaintext', 'fontname': 'Helvetica', 'fontsize': '10'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '9'},
    )

    # ── Parsers ─────────────────────────────────────────

    g.node('HTMLParser', cn('HTMLParser',
        ['+ features_found : Set[str]',
         '+ elements_found : List[Dict]',
         '+ attributes_found : List[Dict]',
         '+ feature_details : List[Dict]',
         '+ unrecognized_patterns : Set[str]'],
        ['+ parse_file(path) : Set[str]',
         '+ parse_string(html) : Set[str]',
         '+ get_detailed_report() : Dict',
         '- _detect_elements(soup)',
         '- _detect_input_types(soup)',
         '- _detect_attributes(soup)',
         '- _detect_attribute_values(soup)',
         '- _detect_special_patterns(soup)',
         '- _find_unrecognized_patterns(soup)',
         '- ...  (other private methods)']))

    g.node('CSSParser', cn('CSSParser',
        ['+ features_found : Set[str]',
         '+ feature_details : List[Dict]',
         '+ unrecognized_patterns : Set[str]',
         '- _all_features : Dict'],
        ['+ parse_file(path) : Set[str]',
         '+ parse_string(css) : Set[str]',
         '+ get_detailed_report() : Dict',
         '- _extract_components(rules) : Tuple',
         '- _build_matchable_text(decl, rules, sel) : str',
         '- _detect_features(css_content)',
         '- _find_unrecognized_patterns_structured(decl, rules)',
         '- ...  (other private methods)']))

    g.node('JSParser', cn('JavaScriptParser',
        ['+ features_found : Set[str]',
         '+ feature_details : List[Dict]',
         '+ unrecognized_patterns : Set[str]',
         '- _all_features : Dict',
         '- _matched_apis : Set[str]'],
        ['+ parse_file(path) : Set[str]',
         '+ parse_string(js) : Set[str]',
         '+ get_detailed_report() : Dict',
         '- _detect_directives(js_content)',
         '- _parse_with_tree_sitter(js_content) : Tree',
         '- _detect_ast_syntax_features(root, src)',
         '- _detect_ast_api_features(root, src)',
         '- _build_matchable_text_from_ast(root, src) : str',
         '- _detect_features(js_content)',
         '- _find_unrecognized_patterns(js_content)',
         '- ...  (other private methods)']))

    g.node('CustomRulesLoader', cn('CustomRulesLoader',
        ['- _css_rules : Dict',
         '- _js_rules : Dict',
         '- _html_rules : Dict'],
        ['+ get_custom_css_rules() : Dict',
         '+ get_custom_js_rules() : Dict',
         '+ get_custom_html_rules() : Dict',
         '+ reload()',
         '- _load_rules()'],
        stereotype='singleton'))

    # ═══ RELATIONSHIPS ═══════════════════════════════════

    g.edge('HTMLParser', 'CustomRulesLoader', style='dashed', arrowhead='open', label='  loads rules  ')
    g.edge('CSSParser', 'CustomRulesLoader', style='dashed', arrowhead='open', label='  loads rules  ')
    g.edge('JSParser', 'CustomRulesLoader', style='dashed', arrowhead='open', label='  loads rules  ')

    # ═══ LAYOUT ══════════════════════════════════════════

    with g.subgraph() as s:
        s.attr(rank='same')
        s.node('HTMLParser')
        s.node('CSSParser')
        s.node('JSParser')

    return g


if __name__ == '__main__':
    d = build()
    path = d.render('3.7_parsers', directory='docs/diagrams/images', cleanup=True)
    print(f"Saved: {path}")
