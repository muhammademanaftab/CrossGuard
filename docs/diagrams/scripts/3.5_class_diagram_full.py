"""Generate the Cross Guard UML class diagram as a PNG image.

Arrow conventions (UML standard):
  - Association:  solid line, no arrowhead          (knows about)
  - Dependency:   dashed line, open arrow  --->     (uses temporarily)
  - Composition:  solid line, filled diamond ◆──    (owns, dies together)
  - Aggregation:  solid line, hollow diamond ◇──    (contains, can exist alone)
  - Inheritance:  solid line, hollow triangle ──▷   (is a)
"""

import graphviz


def class_box(name, attrs=None, methods=None, stereotype=None):
    """UML 3-compartment class box."""
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


def ext_box(name, subtitle=None):
    """External system box (shaded, no compartments)."""
    text = f"<b>{name}</b>"
    if subtitle:
        text += f"<br/><i>{subtitle}</i>"
    return (f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="6" '
            f'bgcolor="#d9d9d9"><tr><td align="center">{text}</td></tr></table>>')


# ── Relationship helpers (UML-correct arrows) ──────

def dependency(g, src, dst, label=''):
    """Dashed arrow with open head: src - - -> dst  (uses/depends temporarily)."""
    g.edge(src, dst, style='dashed', arrowhead='open', label=f'  {label}  ' if label else '')

def composition(g, whole, part):
    """Solid line, filled diamond on WHOLE side: whole ◆── part."""
    g.edge(whole, part, arrowhead='none', arrowtail='diamond', dir='both')

def aggregation(g, whole, part, label=''):
    """Solid line, hollow diamond on WHOLE side: whole ◇── part."""
    g.edge(whole, part, arrowhead='none', arrowtail='odiamond', dir='both',
           label=f'  {label}  ' if label else '')

def association(g, src, dst, label=''):
    """Solid line, no arrowheads (bidirectional awareness)."""
    g.edge(src, dst, arrowhead='none', label=f'  {label}  ' if label else '')


def build():
    g = graphviz.Digraph(
        'CrossGuard',
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'TB',
            'splines': 'true',
            'nodesep': '0.5',
            'ranksep': '1.1',
            'fontname': 'Helvetica',
            'label': 'Cross Guard — UML Class Diagram\n\n',
            'labelloc': 't',
            'fontsize': '20',
            'dpi': '150',
            'pad': '0.5',
        },
        node_attr={'shape': 'plaintext', 'fontname': 'Helvetica', 'fontsize': '9'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '8'},
    )

    # ═══════════════════════════════════════════════════════
    #  CLASS DEFINITIONS (26 classes + 4 external systems)
    # ═══════════════════════════════════════════════════════

    # ── Frontends ───────────────────────────────────────

    g.node('MainWindow', class_box('MainWindow',
        ['- _analyzer_service : AnalyzerService',
         '- current_report : Dict',
         '- export_manager : ExportManager',
         '- _current_view : str',
         '- sidebar : Sidebar',
         '- header : HeaderBar'],
        ['- _init_layout()',
         '- _show_view(view_id)',
         '- _build_files_view()',
         '- _build_results_view()',
         '- _build_history_view()',
         '- _build_settings_view()',
         '- _on_files_dropped(files)',
         '- ...  (35 private methods total)']))

    g.node('ExportManager', class_box('ExportManager',
        ['+ parent : CTk'],
        ['+ export_json(report)',
         '+ export_pdf(report)']))

    g.node('CLI', class_box('CLI',
        [''],
        ['+ analyze(target, browsers, format)',
         '+ export_cmd(analysis_id, format)',
         '+ history(limit)',
         '+ stats()',
         '+ config_cmd()',
         '+ update_db()',
         '+ init_ci(provider)',
         '+ init_hooks(hook_type)'],
        stereotype='Click commands'))

    # ── Data Contracts ──────────────────────────────────

    g.node('AnalysisRequest', class_box('AnalysisRequest',
        ['+ html_files : List[str]',
         '+ css_files : List[str]',
         '+ js_files : List[str]',
         '+ target_browsers : Dict[str, str]'],
        ['+ has_files() : bool',
         '+ total_files() : int']))

    g.node('AnalysisResult', class_box('AnalysisResult',
        ['+ success : bool',
         '+ summary : Dict',
         '+ scores : Dict',
         '+ browsers : Dict',
         '+ detected_features : Dict',
         '+ feature_details : Dict',
         '+ unrecognized_patterns : Dict',
         '+ recommendations : List[str]',
         '+ baseline_summary : Dict',
         '+ ai_suggestions : List',
         '+ error : str'],
        ['+ from_dict(data) : AnalysisResult',
         '+ to_dict() : Dict']))

    # ── Facade ──────────────────────────────────────────

    g.node('AnalyzerService', class_box('AnalyzerService',
        ['- _analyzer : CrossGuardAnalyzer',
         '- _database_updater : DatabaseUpdater',
         '- _web_features : WebFeaturesManager',
         '+ DEFAULT_BROWSERS : Dict'],
        ['+ analyze(request) : AnalysisResult',
         '+ analyze_files(html, css, js, browsers) : AnalysisResult',
         '+ save_analysis_to_history(result, file_name)',
         '+ get_analysis_history(limit, offset) : List',
         '+ get_analysis_by_id(id) : Dict',
         '+ delete_from_history(id) : bool',
         '+ clear_history() : bool',
         '+ get_statistics() : Dict',
         '+ get_setting(key) : str',
         '+ set_setting(key, value) : bool',
         '+ add_bookmark(analysis_id, note) : bool',
         '+ remove_bookmark(analysis_id) : bool',
         '+ toggle_bookmark(analysis_id) : bool',
         '+ get_all_bookmarks(limit) : List',
         '+ create_tag(name, color) : int',
         '+ get_all_tags() : List',
         '+ delete_tag(tag_id) : bool',
         '+ add_tag_to_analysis(analysis_id, tag_id) : bool',
         '+ export_to_json(result, path)',
         '+ export_to_pdf(result, path)',
         '+ get_database_info() : Dict',
         '+ update_database(callback) : Dict',
         '+ get_ai_fix_suggestions(features) : List',
         '+ get_polyfill_suggestions(features) : List',
         '+ reload_custom_rules()',
         '+ load_config(path) : Dict',
         '+ get_custom_rules() : Dict',
         '+ save_custom_rules(rules) : bool',
         '+ classify_file(path) : str'],
        stereotype='facade'))

    # ── Orchestrator ────────────────────────────────────

    g.node('CrossGuardAnalyzer', class_box('CrossGuardAnalyzer',
        ['+ html_parser : HTMLParser',
         '+ css_parser : CSSParser',
         '+ js_parser : JavaScriptParser',
         '+ database : CanIUseDatabase',
         '+ compatibility_analyzer : CompatibilityAnalyzer',
         '+ scorer : CompatibilityScorer',
         '+ all_features : Set[str]',
         '+ errors : List[str]',
         '+ warnings : List[str]'],
        ['+ run_analysis(html, css, js, browsers) : Dict',
         '+ analyze_single_file(path, type, browsers) : Dict',
         '- _reset_state()',
         '- _parse_html_files(files)',
         '- _parse_css_files(files)',
         '- _parse_js_files(files)',
         '- _check_compatibility(browsers) : Dict',
         '- _calculate_scores(results, browsers) : Dict',
         '- _generate_report(results, scores, browsers) : Dict',
         '- ...  (10 private methods total)'],
        stereotype='orchestrator'))

    # ── Services ────────────────────────────────────────

    g.node('DatabaseUpdater', class_box('DatabaseUpdater',
        ['+ caniuse_dir : Path',
         '+ data_json_path : Path'],
        ['+ update_database(callback) : Dict',
         '+ check_npm_update() : Dict',
         '+ download_npm_update(callback) : Dict',
         '+ get_database_info() : Dict',
         '+ get_local_npm_version() : str',
         '+ ...  (8 public methods total)']))

    g.node('WebFeaturesManager', class_box('WebFeaturesManager',
        ['- _data : Dict',
         '- _reverse_map : Dict'],
        ['+ download() : bool',
         '+ has_data() : bool',
         '+ get_baseline_status(feature_id) : Dict',
         '+ get_baseline_summary(features) : Dict',
         '+ ...  (5 public methods total)']))

    g.node('ConfigManager', class_box('ConfigManager',
        ['- _config : Dict',
         '- _config_path : Path'],
        ['+ browsers : Dict (property)',
         '+ output_format : str (property)',
         '+ rules_path : str (property)',
         '+ ai_config : Dict (property)',
         '+ get(key, default) : Any',
         '+ to_dict() : Dict',
         '+ create_default_config(dir) : str',
         '+ ...  (8 public methods total)']))

    g.node('AIFixService', class_box('AIFixService',
        ['- _api_key : str',
         '- _provider : str',
         '- _model : str',
         '- _max_features : int'],
        ['+ is_available() : bool',
         '+ get_fix_suggestions(features, type, browsers) : List',
         '- _build_prompt(features, type) : str',
         '- _call_api(prompt) : str',
         '- _parse_response(raw, features) : List',
         '- ...  (5 private methods total)']))

    g.node('PolyfillService', class_box('PolyfillService',
        ['- _loader : PolyfillLoader'],
        ['+ get_recommendations(unsupported, partial, browsers) : List',
         '+ get_aggregate_install_command(recs) : str',
         '+ get_aggregate_imports(recs) : List',
         '+ get_total_size_kb(recs) : float',
         '+ categorize_recommendations(recs) : Dict']))

    g.node('PolyfillLoader', class_box('PolyfillLoader',
        ['- _data : Dict'],
        ['+ get_polyfill(feature_id) : Dict',
         '+ has_polyfill(feature_id) : bool',
         '+ is_polyfillable(feature_id) : bool',
         '+ reload()'],
        stereotype='singleton'))

    # ── Parsers ─────────────────────────────────────────

    g.node('HTMLParser', class_box('HTMLParser',
        ['+ features_found : Set[str]',
         '+ elements_found : List[Dict]',
         '+ attributes_found : List[Dict]',
         '+ feature_details : List[Dict]',
         '+ unrecognized_patterns : Set[str]'],
        ['+ parse_file(path) : Set[str]',
         '+ parse_string(html) : Set[str]',
         '+ parse_multiple_files(paths) : Set[str]',
         '+ get_detailed_report() : Dict',
         '+ get_statistics() : Dict',
         '+ validate_html(content) : bool',
         '- ...  (17 private methods total)']))

    g.node('CSSParser', class_box('CSSParser',
        ['+ features_found : Set[str]',
         '+ feature_details : List[Dict]',
         '+ unrecognized_patterns : Set[str]'],
        ['+ parse_file(path) : Set[str]',
         '+ parse_string(css) : Set[str]',
         '+ parse_multiple_files(paths) : Set[str]',
         '+ get_detailed_report() : Dict',
         '+ get_statistics() : Dict',
         '+ validate_css(content) : bool',
         '- ...  (5 private methods total)']))

    g.node('JSParser', class_box('JavaScriptParser',
        ['+ features_found : Set[str]',
         '+ feature_details : List[Dict]',
         '+ unrecognized_patterns : Set[str]'],
        ['+ parse_file(path) : Set[str]',
         '+ parse_string(js) : Set[str]',
         '+ parse_multiple_files(paths) : Set[str]',
         '+ get_detailed_report() : Dict',
         '+ get_statistics() : Dict',
         '+ validate_javascript(content) : bool',
         '- ...  (13 private methods total)']))

    g.node('CustomRulesLoader', class_box('CustomRulesLoader',
        ['- _css_rules : Dict',
         '- _js_rules : Dict',
         '- _html_rules : Dict'],
        ['+ get_custom_css_rules() : Dict',
         '+ get_custom_js_rules() : Dict',
         '+ get_custom_html_rules() : Dict',
         '+ reload()'],
        stereotype='singleton'))

    # ── Compatibility Engine ────────────────────────────

    g.node('CompatibilityAnalyzer', class_box('CompatibilityAnalyzer',
        ['+ database : CanIUseDatabase'],
        ['+ analyze(features, browsers) : Dict',
         '- _analyze_browser(features, browser, ver) : Dict',
         '- _calculate_overall_score(scores) : float',
         '- _calculate_severity(status, total) : str',
         '- ...  (6 private methods total)']))

    g.node('CompatibilityScorer', class_box('CompatibilityScorer',
        ['+ browser_weights : Dict',
         '+ DEFAULT_WEIGHTS : Dict',
         '+ STATUS_SCORES : Dict'],
        ['+ calculate_simple_score(status) : float',
         '+ calculate_weighted_score(status) : Dict',
         '+ calculate_compatibility_index(status) : Dict']))

    g.node('CanIUseDatabase', class_box('CanIUseDatabase',
        ['+ data : Dict',
         '+ features : Dict',
         '+ feature_index : Dict',
         '+ loaded : bool'],
        ['+ load() : bool',
         '+ get_feature(feature_id) : Dict',
         '+ check_support(feature, browser, ver) : str',
         '+ get_all_features() : List[str]',
         '+ get_feature_info(feature_id) : Dict',
         '+ get_browser_versions(browser) : List[str]',
         '- ...  (5 private methods total)'],
        stereotype='singleton'))

    # ── Database Layer ──────────────────────────────────

    g.node('AnalysisRepository', class_box('AnalysisRepository',
        ['- _conn : Connection'],
        ['+ save_analysis(a) : int',
         '+ get_all_analyses(limit, offset) : List[Analysis]',
         '+ get_analysis_by_id(id) : Analysis',
         '+ delete_analysis(id) : bool',
         '+ clear_all() : int',
         '+ get_count(file_type) : int',
         '+ ...  (7 public methods total)']))

    g.node('StatisticsService', class_box('StatisticsService',
        ['- _conn : Connection'],
        ['+ get_total_analyses() : int',
         '+ get_average_score() : float',
         '+ get_best_score() : float',
         '+ get_worst_score() : float',
         '+ get_score_trend(days) : List',
         '+ get_top_problematic_features(limit) : List',
         '+ get_grade_distribution() : Dict',
         '+ get_file_type_distribution() : Dict',
         '+ get_summary_statistics() : Dict',
         '+ ...  (13 public methods total)']))

    # ── Data Models ─────────────────────────────────────

    g.node('Analysis', class_box('Analysis',
        ['+ id : int', '+ file_name : str', '+ file_path : str',
         '+ file_type : str', '+ overall_score : float', '+ grade : str',
         '+ total_features : int', '+ analyzed_at : datetime',
         '+ browsers_json : str', '+ features : List[AnalysisFeature]'],
        ['+ to_dict() : Dict', '+ from_row(row) : Analysis',
         '+ get_formatted_date() : str']))

    g.node('AnalysisFeature', class_box('AnalysisFeature',
        ['+ id : int', '+ analysis_id : int', '+ feature_id : str',
         '+ feature_name : str', '+ category : str',
         '+ browser_results : List[BrowserResult]'],
        ['+ to_dict() : Dict', '+ from_row(row) : AnalysisFeature']))

    g.node('BrowserResult', class_box('BrowserResult',
        ['+ id : int', '+ analysis_feature_id : int',
         '+ browser : str', '+ version : str', '+ support_status : str'],
        ['+ to_dict() : Dict', '+ from_row(row) : BrowserResult']))

    g.node('Bookmark', class_box('Bookmark',
        ['+ id : int', '+ analysis_id : int', '+ note : str',
         '+ created_at : datetime', '+ analysis : Analysis'],
        ['+ to_dict() : Dict', '+ from_row(row) : Bookmark']))

    g.node('Tag', class_box('Tag',
        ['+ id : int', '+ name : str', '+ color : str',
         '+ created_at : datetime'],
        ['+ to_dict() : Dict', '+ from_row(row) : Tag']))

    # ── External Systems ────────────────────────────────

    g.node('SQLiteDB', ext_box('SQLite Database', 'crossguard.db'))
    g.node('CanIUseData', ext_box('Can I Use Data', 'data/caniuse/'))
    g.node('LLMAPIs', ext_box('LLM APIs', 'OpenAI / Anthropic'))
    g.node('NPMRegistry', ext_box('NPM Registry', 'registry.npmjs.org'))

    # ═══════════════════════════════════════════════════════
    #  RELATIONSHIPS (UML-correct arrow types)
    # ═══════════════════════════════════════════════════════

    # ── Composition: filled diamond ◆ (whole owns part) ──

    composition(g, 'MainWindow', 'ExportManager')
    composition(g, 'CrossGuardAnalyzer', 'HTMLParser')
    composition(g, 'CrossGuardAnalyzer', 'CSSParser')
    composition(g, 'CrossGuardAnalyzer', 'JSParser')
    composition(g, 'CrossGuardAnalyzer', 'CompatibilityAnalyzer')
    composition(g, 'CrossGuardAnalyzer', 'CompatibilityScorer')

    # ── Aggregation: hollow diamond ◇ (contains, can exist alone) ──

    aggregation(g, 'Analysis', 'AnalysisFeature', '1..*')
    aggregation(g, 'AnalysisFeature', 'BrowserResult', '1..*')

    # ── Dependency: dashed arrow ---> (uses/creates temporarily) ──

    # Frontends -> Facade
    dependency(g, 'MainWindow', 'AnalyzerService', 'depends')
    dependency(g, 'CLI', 'AnalyzerService', 'depends')
    dependency(g, 'CLI', 'ConfigManager', 'loads config')

    # Facade -> Data contracts
    dependency(g, 'AnalyzerService', 'AnalysisRequest', 'accepts')
    dependency(g, 'AnalyzerService', 'AnalysisResult', 'returns')

    # Facade -> Backend (creates)
    dependency(g, 'AnalyzerService', 'CrossGuardAnalyzer', 'creates')
    dependency(g, 'AnalyzerService', 'DatabaseUpdater', 'creates')
    dependency(g, 'AnalyzerService', 'WebFeaturesManager', 'creates')

    # Facade -> Backend (uses)
    dependency(g, 'AnalyzerService', 'ConfigManager', 'uses')
    dependency(g, 'AnalyzerService', 'AnalysisRepository', 'uses')
    dependency(g, 'AnalyzerService', 'StatisticsService', 'uses')
    dependency(g, 'AnalyzerService', 'AIFixService', 'uses')
    dependency(g, 'AnalyzerService', 'PolyfillService', 'uses')

    # Orchestrator -> dependencies
    dependency(g, 'CrossGuardAnalyzer', 'CanIUseDatabase', 'uses')

    # Parsers -> rules
    dependency(g, 'HTMLParser', 'CustomRulesLoader', 'loads rules')
    dependency(g, 'CSSParser', 'CustomRulesLoader', 'loads rules')
    dependency(g, 'JSParser', 'CustomRulesLoader', 'loads rules')

    # Compatibility engine
    dependency(g, 'CompatibilityAnalyzer', 'CanIUseDatabase', 'queries')

    # ── Association: solid line (structural link) ──

    association(g, 'AnalysisRepository', 'Analysis', 'manages')
    association(g, 'Bookmark', 'Analysis', 'references')
    association(g, 'Analysis', 'Tag', '0..*')
    association(g, 'PolyfillService', 'PolyfillLoader', 'uses')

    # ── Dependency to external systems ──

    dependency(g, 'CanIUseDatabase', 'CanIUseData', 'reads')
    dependency(g, 'DatabaseUpdater', 'CanIUseData', 'updates')
    dependency(g, 'DatabaseUpdater', 'NPMRegistry', 'fetches')
    dependency(g, 'AnalysisRepository', 'SQLiteDB', 'stored in')
    dependency(g, 'StatisticsService', 'SQLiteDB', 'queries')
    dependency(g, 'AIFixService', 'LLMAPIs', 'calls')

    # ═══════════════════════════════════════════════════════
    #  LAYOUT RANKS
    # ═══════════════════════════════════════════════════════

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
    path = d.render('3.5_class_diagram_full', directory='docs/diagrams/images', cleanup=True)
    print(f"Saved: {path}")
