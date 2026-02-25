"""Generates polyfill recommendations from compatibility results."""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

from .polyfill_loader import get_polyfill_loader


@dataclass
class PolyfillPackage:
    name: str
    npm_package: str
    import_statement: str
    cdn_url: Optional[str] = None
    size_kb: Optional[float] = None
    note: Optional[str] = None


@dataclass
class PolyfillRecommendation:
    feature_id: str
    feature_name: str
    polyfill_type: str  # 'npm' or 'fallback'
    packages: List[PolyfillPackage] = field(default_factory=list)
    fallback_code: Optional[str] = None
    fallback_description: Optional[str] = None
    browsers_affected: List[str] = field(default_factory=list)


class PolyfillService:
    """Turns compatibility issues into actionable polyfill recommendations."""

    def __init__(self):
        self._loader = get_polyfill_loader()

    def get_recommendations(
        self,
        unsupported_features: Set[str],
        partial_features: Set[str],
        browsers: Dict[str, str]
    ) -> List[PolyfillRecommendation]:
        """Build recommendations for all unsupported/partial features."""
        recommendations = []
        all_problem_features = unsupported_features | partial_features

        for feature_id in sorted(all_problem_features):
            polyfill_info = self._loader.get_polyfill(feature_id)
            if not polyfill_info:
                continue

            if polyfill_info.get('polyfillable'):
                packages = []
                for pkg in polyfill_info.get('packages', []):
                    packages.append(PolyfillPackage(
                        name=pkg.get('name', ''),
                        npm_package=pkg.get('npm', ''),
                        import_statement=pkg.get('import', ''),
                        cdn_url=pkg.get('cdn'),
                        size_kb=pkg.get('size_kb'),
                        note=pkg.get('note'),
                    ))

                rec = PolyfillRecommendation(
                    feature_id=feature_id,
                    feature_name=polyfill_info.get('name', feature_id),
                    polyfill_type='npm',
                    packages=packages,
                    browsers_affected=list(browsers.keys())
                )
                recommendations.append(rec)

            elif 'fallback' in polyfill_info:
                fallback = polyfill_info['fallback']
                rec = PolyfillRecommendation(
                    feature_id=feature_id,
                    feature_name=polyfill_info.get('name', feature_id),
                    polyfill_type='fallback',
                    packages=[],
                    fallback_code=fallback.get('code'),
                    fallback_description=fallback.get('description'),
                    browsers_affected=list(browsers.keys())
                )
                recommendations.append(rec)

        return recommendations

    def get_aggregate_install_command(
        self,
        recommendations: List[PolyfillRecommendation]
    ) -> str:
        """Build a single `npm install` command for all recommended packages."""
        packages = set()
        for rec in recommendations:
            if rec.polyfill_type == 'npm' and rec.packages:
                # first package is the recommended one
                packages.add(rec.packages[0].npm_package)

        if not packages:
            return ""

        return f"npm install {' '.join(sorted(packages))}"

    def get_aggregate_imports(
        self,
        recommendations: List[PolyfillRecommendation]
    ) -> List[str]:
        """Collect import statements for all npm polyfill packages."""
        imports = []
        for rec in recommendations:
            if rec.polyfill_type == 'npm' and rec.packages:
                imports.append(rec.packages[0].import_statement)
        return imports

    def get_total_size_kb(
        self,
        recommendations: List[PolyfillRecommendation]
    ) -> float:
        """Sum up estimated bundle size (KB) of all recommended polyfills."""
        total = 0.0
        for rec in recommendations:
            if rec.polyfill_type == 'npm' and rec.packages:
                size = rec.packages[0].size_kb
                if size:
                    total += size
        return total

    def categorize_recommendations(
        self,
        recommendations: List[PolyfillRecommendation]
    ) -> Dict[str, List[PolyfillRecommendation]]:
        """Split recommendations into 'npm' vs 'fallback' buckets."""
        result = {
            'npm': [],
            'fallback': []
        }

        for rec in recommendations:
            if rec.polyfill_type == 'npm':
                result['npm'].append(rec)
            elif rec.polyfill_type == 'fallback':
                result['fallback'].append(rec)

        return result
