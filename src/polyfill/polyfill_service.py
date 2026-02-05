"""Service for generating polyfill recommendations.

This module analyzes compatibility results and recommends appropriate polyfills
for features that have issues in target browsers.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

from .polyfill_loader import get_polyfill_loader


@dataclass
class PolyfillPackage:
    """Information about a single polyfill package option."""
    name: str
    npm_package: str
    import_statement: str
    cdn_url: Optional[str] = None
    size_kb: Optional[float] = None
    note: Optional[str] = None


@dataclass
class PolyfillRecommendation:
    """A single polyfill recommendation."""
    feature_id: str
    feature_name: str
    polyfill_type: str  # 'npm', 'fallback'
    packages: List[PolyfillPackage] = field(default_factory=list)
    fallback_code: Optional[str] = None
    fallback_description: Optional[str] = None
    browsers_affected: List[str] = field(default_factory=list)


class PolyfillService:
    """Generates polyfill recommendations based on analysis results."""

    def __init__(self):
        self._loader = get_polyfill_loader()

    def get_recommendations(
        self,
        unsupported_features: Set[str],
        partial_features: Set[str],
        browsers: Dict[str, str]
    ) -> List[PolyfillRecommendation]:
        """
        Get polyfill recommendations for features with compatibility issues.

        Args:
            unsupported_features: Set of feature IDs that are unsupported
            partial_features: Set of feature IDs with partial support
            browsers: Dict of browser name to version

        Returns:
            List of PolyfillRecommendation objects
        """
        recommendations = []
        all_problem_features = unsupported_features | partial_features

        for feature_id in sorted(all_problem_features):
            polyfill_info = self._loader.get_polyfill(feature_id)
            if not polyfill_info:
                continue

            if polyfill_info.get('polyfillable'):
                # This feature can be polyfilled with npm packages
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
                # This feature has a CSS/code fallback strategy
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
        """Generate a single npm install command for all recommendations.

        Args:
            recommendations: List of polyfill recommendations

        Returns:
            npm install command string (empty if no packages needed)
        """
        packages = set()
        for rec in recommendations:
            if rec.polyfill_type == 'npm' and rec.packages:
                # Use first package option (recommended one)
                packages.add(rec.packages[0].npm_package)

        if not packages:
            return ""

        return f"npm install {' '.join(sorted(packages))}"

    def get_aggregate_imports(
        self,
        recommendations: List[PolyfillRecommendation]
    ) -> List[str]:
        """Generate import statements for all recommendations.

        Args:
            recommendations: List of polyfill recommendations

        Returns:
            List of import statement strings
        """
        imports = []
        for rec in recommendations:
            if rec.polyfill_type == 'npm' and rec.packages:
                # Use first package option (recommended one)
                imports.append(rec.packages[0].import_statement)
        return imports

    def get_total_size_kb(
        self,
        recommendations: List[PolyfillRecommendation]
    ) -> float:
        """Calculate total estimated size of all polyfills.

        Args:
            recommendations: List of polyfill recommendations

        Returns:
            Total size in KB
        """
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
        """Categorize recommendations by type.

        Args:
            recommendations: List of polyfill recommendations

        Returns:
            Dict with 'npm' and 'fallback' keys
        """
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
