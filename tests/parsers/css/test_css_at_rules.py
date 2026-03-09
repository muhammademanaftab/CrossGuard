"""Consolidated CSS at-rule and media query detection tests.

Merged from: at_rules/test_at_rules.py, media_queries/test_media_queries.py
"""

import pytest


CSS_AT_RULE_FEATURES = [
    # @supports (feature queries)
    pytest.param("@supports(display:grid){.g{display:grid}}", "css-featurequeries", id="supports-basic"),
    pytest.param("@supports not(display:grid){.f{display:flex}}", "css-featurequeries", id="supports-not"),
    pytest.param("@supports(display:grid)and(gap:20px){.m{gap:20px}}", "css-featurequeries", id="supports-and"),
    pytest.param("@supports selector(:has(*)){.p:has(img){padding:10px}}", "css-featurequeries", id="supports-selector"),
    # counters
    pytest.param("body{counter-reset:section}", "css-counters", id="counter-reset"),
    pytest.param("h2{counter-increment:section}", "css-counters", id="counter-increment"),
    pytest.param("h2::before{content:counter(section) '. '}", "css-counters", id="counter-fn"),
    # page-break
    pytest.param(".ch{page-break-before:always}", "css-page-break", id="page-break-before"),
    pytest.param(".s{page-break-after:avoid}", "css-page-break", id="page-break-after"),
    pytest.param("table{page-break-inside:avoid}", "css-page-break", id="page-break-inside"),
    # paged media
    pytest.param("@page{margin:1in}", "css-paged-media", id="page-rule"),
    pytest.param("@page :first{margin-top:2in}", "css-paged-media", id="page-first"),
    # @when/@else
    pytest.param("@when media(width >= 400px){.e{display:block}}", "css-when-else", id="when-rule"),
    pytest.param("@else{.e{display:none}}", "css-when-else", id="else-rule"),
    # cascade layers
    pytest.param("@layer base{body{margin:0}}", "css-cascade-layers", id="layer-rule"),
    pytest.param("@layer reset,base,components,utilities;", "css-cascade-layers", id="layer-order"),
    # namespaces
    pytest.param('@namespace svg url("http://www.w3.org/2000/svg");', "css-namespaces", id="namespace"),
    # counter-style
    pytest.param("@counter-style thumbs{system:cyclic;symbols:'\\1F44D'}", "css-at-counter-style", id="counter-style"),
    # device adaptation
    pytest.param("@viewport{width:device-width}", "css-deviceadaptation", id="viewport"),
    # cascade-scope (at-rule form)
    pytest.param("@scope(.card){h2{color:blue}}", "css-cascade-scope", id="scope-at-rule"),
]

CSS_MEDIA_QUERY_FEATURES = [
    # basic media queries
    pytest.param("@media screen{body{color:black}}", "css-mediaqueries", id="media-screen"),
    pytest.param("@media(min-width:768px){.c{width:750px}}", "css-mediaqueries", id="media-min-width"),
    pytest.param("@media(max-width:480px){.m{display:block}}", "css-mediaqueries", id="media-max-width"),
    # prefers-color-scheme
    pytest.param("@media(prefers-color-scheme:dark){body{background:#1a1a1a}}", "prefers-color-scheme", id="color-scheme-dark"),
    pytest.param("@media(prefers-color-scheme:light){body{background:white}}", "prefers-color-scheme", id="color-scheme-light"),
    # prefers-reduced-motion
    pytest.param("@media(prefers-reduced-motion:reduce){*{animation:none!important}}", "prefers-reduced-motion", id="reduced-motion"),
    # resolution
    pytest.param("@media(min-resolution:2dppx){.r{background-image:url(img@2x.png)}}", "css-media-resolution", id="min-resolution"),
    pytest.param("@media(max-resolution:150dpi){.l{background-image:url(img.png)}}", "css-media-resolution", id="max-resolution"),
    # range syntax
    pytest.param("@media(width < 600px){.m{display:block}}", "css-media-range-syntax", id="range-lt"),
    pytest.param("@media(width > 900px){.d{display:block}}", "css-media-range-syntax", id="range-gt"),
    pytest.param("@media(width <= 768px){.t{display:block}}", "css-media-range-syntax", id="range-lte"),
    pytest.param("@media(600px <= width <= 900px){.t{display:block}}", "css-media-range-syntax", id="range-between"),
    # interaction
    pytest.param("@media(hover:hover){.h:hover{background:blue}}", "css-media-interaction", id="hover-media"),
    pytest.param("@media(pointer:coarse){.b{min-height:44px}}", "css-media-interaction", id="pointer-media"),
    pytest.param("@media(any-hover:hover){.l:hover{text-decoration:underline}}", "css-media-interaction", id="any-hover"),
    pytest.param("@media(any-pointer:fine){.s{padding:5px}}", "css-media-interaction", id="any-pointer"),
    # scripting
    pytest.param("@media(scripting:enabled){.js{display:block}}", "css-media-scripting", id="scripting-enabled"),
    pytest.param("@media(scripting:none){.noscript{display:block}}", "css-media-scripting", id="scripting-none"),
]


@pytest.mark.unit
class TestAtRuleDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_AT_RULE_FEATURES)
    def test_at_rule_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)


@pytest.mark.unit
class TestMediaQueryDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_MEDIA_QUERY_FEATURES)
    def test_media_query_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)
