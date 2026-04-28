"""Polyfill recommendation service."""

from typing import Dict, List, Set

from .polyfill_loader import get_polyfill_loader


class PolyfillService:
    """Builds the list of polyfill packages or CSS fallbacks shown on the results page."""

    def __init__(self):
        self._loader = get_polyfill_loader()

    def get_recommendations(
        self,
        unsupported_features: Set[str],
        partial_features: Set[str],
        browsers: Dict[str, str]
    ) -> List[Dict]:
        recommendations = []
        all_problem_features = unsupported_features | partial_features

        for feature_id in sorted(all_problem_features):
            polyfill_info = self._loader.get_polyfill(feature_id)
            if not polyfill_info:
                continue

            if polyfill_info.get('polyfillable'):
                packages = []
                for pkg in polyfill_info.get('packages', []):
                    packages.append({
                        'name': pkg.get('name', ''),
                        'npm_package': pkg.get('npm', ''),
                        'import_statement': pkg.get('import', ''),
                        'cdn_url': pkg.get('cdn'),
                        'size_kb': pkg.get('size_kb'),
                        'note': pkg.get('note'),
                    })

                rec = {
                    'feature_id': feature_id,
                    'feature_name': polyfill_info.get('name', feature_id),
                    'polyfill_type': 'npm',
                    'packages': packages,
                    'fallback_code': None,
                    'fallback_description': None,
                    'browsers_affected': list(browsers.keys()),
                }
                recommendations.append(rec)

            elif 'fallback' in polyfill_info:
                fallback = polyfill_info['fallback']
                rec = {
                    'feature_id': feature_id,
                    'feature_name': polyfill_info.get('name', feature_id),
                    'polyfill_type': 'fallback',
                    'packages': [],
                    'fallback_code': fallback.get('code'),
                    'fallback_description': fallback.get('description'),
                    'browsers_affected': list(browsers.keys()),
                }
                recommendations.append(rec)

        return recommendations

    def get_aggregate_install_command(
        self,
        recommendations: List[Dict]
    ) -> str:
        packages = set()
        for rec in recommendations:
            if rec['polyfill_type'] == 'npm' and rec['packages']:
                packages.add(rec['packages'][0]['npm_package'])

        if not packages:
            return ""

        return f"npm install {' '.join(sorted(packages))}"

    def get_aggregate_imports(
        self,
        recommendations: List[Dict]
    ) -> List[str]:
        imports = []
        for rec in recommendations:
            if rec['polyfill_type'] == 'npm' and rec['packages']:
                imports.append(rec['packages'][0]['import_statement'])
        return imports

    def get_total_size_kb(
        self,
        recommendations: List[Dict]
    ) -> float:
        total = 0.0
        for rec in recommendations:
            if rec['polyfill_type'] == 'npm' and rec['packages']:
                size = rec['packages'][0].get('size_kb')
                if size:
                    total += size
        return total

    def categorize_recommendations(
        self,
        recommendations: List[Dict]
    ) -> Dict[str, List[Dict]]:
        result = {
            'npm': [],
            'fallback': []
        }

        for rec in recommendations:
            if rec['polyfill_type'] == 'npm':
                result['npm'].append(rec)
            elif rec['polyfill_type'] == 'fallback':
                result['fallback'].append(rec)

        return result
