"""Consolidated modern CSS feature detection tests.

Merged from: modern/test_modern.py
"""

import pytest


CSS_MODERN_FEATURES = [
    # container queries
    pytest.param("@container(min-width:400px){.c{display:flex}}", "css-container-queries", id="container-at-rule"),
    pytest.param(".c{container-type:inline-size}", "css-container-queries", id="container-type"),
    pytest.param(".c{container-name:sidebar}", "css-container-queries", id="container-name"),
    # container style queries
    pytest.param("@container style(--theme:dark){.c{background:#333}}", "css-container-queries-style", id="container-style"),
    # CSS nesting
    pytest.param(".c{&{padding:10px}}", "css-nesting", id="nesting-amp"),
    pytest.param(".c{&:hover{background:blue}}", "css-nesting", id="nesting-hover"),
    pytest.param(".c{& .item{color:blue}}", "css-nesting", id="nesting-descendant"),
    # anchor positioning
    pytest.param(".c{anchor-name:--my-anchor}", "css-anchor-positioning", id="anchor-name"),
    pytest.param(".c{position-anchor:--my-anchor}", "css-anchor-positioning", id="position-anchor"),
    pytest.param(".c{top:anchor(bottom)}", "css-anchor-positioning", id="anchor-fn"),
    # containment
    pytest.param(".c{contain:layout}", "css-containment", id="contain-layout"),
    pytest.param(".c{contain:paint}", "css-containment", id="contain-paint"),
    pytest.param(".c{contain:strict}", "css-containment", id="contain-strict"),
    # content-visibility
    pytest.param(".c{content-visibility:auto}", "css-content-visibility", id="content-vis-auto"),
    pytest.param(".c{content-visibility:hidden}", "css-content-visibility", id="content-vis-hidden"),
    # motion paths
    pytest.param(".c{offset-path:path('M 0 0 L 100 100')}", "css-motion-paths", id="offset-path"),
    pytest.param(".c{offset-distance:50%}", "css-motion-paths", id="offset-distance"),
    pytest.param(".c{offset-rotate:auto 45deg}", "css-motion-paths", id="offset-rotate"),
    # shapes
    pytest.param(".c{shape-outside:circle(50%)}", "css-shapes", id="shape-outside"),
    pytest.param(".c{shape-margin:10px}", "css-shapes", id="shape-margin"),
    # masks
    pytest.param(".c{mask:url(mask.svg)}", "css-masks", id="mask"),
    pytest.param(".c{mask-image:linear-gradient(black,transparent)}", "css-masks", id="mask-image"),
    pytest.param(".c{mask-border:url(b.png) 30 round}", "css-masks", id="mask-border"),
    # clip-path
    pytest.param(".c{clip-path:circle(50%)}", "css-clip-path", id="clip-path-circle"),
    pytest.param(".c{clip-path:polygon(50% 0%,0% 100%,100% 100%)}", "css-clip-path", id="clip-path-polygon"),
    pytest.param(".c{clip-path:url(#myClip)}", "css-clip-path", id="clip-path-url"),
    # logical properties
    pytest.param(".c{margin-inline:auto}", "css-logical-props", id="margin-inline"),
    pytest.param(".c{padding-block:20px}", "css-logical-props", id="padding-block"),
    pytest.param(".c{inset-inline:0}", "css-logical-props", id="inset-inline"),
    # view transitions
    pytest.param("::view-transition-old(root){animation:fade-out 0.5s}", "view-transitions", id="view-transition-old"),
    pytest.param("::view-transition-new(root){animation:fade-in 0.5s}", "view-transitions", id="view-transition-new"),
    # cross-document view transitions
    pytest.param("@view-transition{navigation:auto}", "cross-document-view-transitions", id="view-transition-at-rule"),
    pytest.param(".c{view-transition-name:header}", "cross-document-view-transitions", id="view-transition-name"),
    # paint API
    pytest.param(".c{background-image:paint(myPainter)}", "css-paint-api", id="paint-fn"),
    # env()
    pytest.param(".c{padding-top:env(safe-area-inset-top)}", "css-env-function", id="env-fn"),
    pytest.param(".c{padding:env(safe-area-inset-top,20px)}", "css-env-function", id="env-fallback"),
]


@pytest.mark.unit
class TestModernCSSDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_MODERN_FEATURES)
    def test_modern_feature_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)
