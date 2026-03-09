"""Consolidated CSS selector detection tests.

Merged from: selectors/test_selectors.py
"""

import pytest


CSS_SELECTOR_FEATURES = [
    # css-sel2
    pytest.param("[type]{color:red}", "css-sel2", id="attribute-sel"),
    pytest.param("a:hover{color:blue}", "css-sel2", id="hover"),
    pytest.param("button:active{background:gray}", "css-sel2", id="active"),
    pytest.param("input:focus{outline:2px solid blue}", "css-sel2", id="focus"),
    # css-sel3
    pytest.param("li:nth-child(odd){background:#eee}", "css-sel3", id="nth-child"),
    pytest.param("p:nth-of-type(2n){color:gray}", "css-sel3", id="nth-of-type"),
    pytest.param("p:first-of-type{font-weight:bold}", "css-sel3", id="first-of-type"),
    pytest.param("li:last-of-type{border:none}", "css-sel3", id="last-of-type"),
    pytest.param("input:not([type='submit']){border:1px solid}", "css-sel3", id="not"),
    # generated content
    pytest.param(".c::before{content:'x'}", "css-gencontent", id="before"),
    pytest.param(".c::after{content:'x'}", "css-gencontent", id="after"),
    pytest.param(".c:before{content:'x'}", "css-gencontent", id="before-single"),
    pytest.param(".c:after{content:'x'}", "css-gencontent", id="after-single"),
    # first-letter / first-line
    pytest.param("p::first-letter{font-size:2em}", "css-first-letter", id="first-letter"),
    pytest.param("p:first-letter{font-size:2em}", "css-first-letter", id="first-letter-single"),
    pytest.param("p::first-line{font-weight:bold}", "css-first-line", id="first-line"),
    # selection
    pytest.param("::selection{background:yellow}", "css-selection", id="selection"),
    # placeholder
    pytest.param("input::placeholder{color:gray}", "css-placeholder", id="placeholder"),
    pytest.param("input::-webkit-input-placeholder{color:gray}", "css-placeholder", id="webkit-placeholder"),
    # marker
    pytest.param("li::marker{color:red}", "css-marker-pseudo", id="marker"),
    # case-insensitive attribute
    pytest.param("[type='text' i]{border:1px solid}", "css-case-insensitive", id="case-insensitive"),
    # optional / required
    pytest.param("input:optional{border-color:gray}", "css-optional-pseudo", id="optional"),
    pytest.param("input:required{border-color:red}", "css-optional-pseudo", id="required"),
    # placeholder-shown
    pytest.param("input:placeholder-shown{border-style:dashed}", "css-placeholder-shown", id="placeholder-shown"),
    # default
    pytest.param("button:default{font-weight:bold}", "css-default-pseudo", id="default"),
    # indeterminate
    pytest.param("input:indeterminate{opacity:0.5}", "css-indeterminate-pseudo", id="indeterminate"),
    # :dir()
    pytest.param(":dir(ltr){text-align:left}", "css-dir-pseudo", id="dir-ltr"),
    # :any-link
    pytest.param(":any-link{color:blue}", "css-any-link", id="any-link"),
    # read-only / read-write
    pytest.param("input:read-only{background:#eee}", "css-read-only-write", id="read-only"),
    pytest.param("input:read-write{background:white}", "css-read-only-write", id="read-write"),
    # @scope (cascade-scope)
    pytest.param("@scope(.card){h2{color:blue}}", "css-cascade-scope", id="scope-rule"),
    pytest.param("@scope(.card)to(.footer){p{margin:0}}", "css-cascade-scope", id="scope-limit"),
    # :is, :where, :matches
    pytest.param(":is(h1,h2,h3){margin-top:1em}", "css-matches-pseudo", id="is-pseudo"),
    pytest.param(":where(article,section) p{line-height:1.5}", "css-matches-pseudo", id="where-pseudo"),
    pytest.param(":matches(h1,h2){color:navy}", "css-matches-pseudo", id="matches-pseudo"),
    # :has
    pytest.param("article:has(img){padding:20px}", "css-has", id="has"),
    pytest.param("div:has(>p){border:1px solid}", "css-has", id="has-child"),
    # :focus-within
    pytest.param("form:focus-within{box-shadow:0 0 5px blue}", "css-focus-within", id="focus-within"),
    # :focus-visible
    pytest.param("button:focus-visible{outline:2px solid blue}", "css-focus-visible", id="focus-visible"),
    # :in-range / :out-of-range
    pytest.param("input:in-range{border-color:green}", "css-in-out-of-range", id="in-range"),
    pytest.param("input:out-of-range{border-color:red}", "css-in-out-of-range", id="out-of-range"),
    # :not() selector list
    pytest.param("input:not([type='submit'],[type='reset']){width:100%}", "css-not-sel-list", id="not-sel-list"),
    # :nth-child(of)
    pytest.param("li:nth-child(2 of .important){font-weight:bold}", "css-nth-child-of", id="nth-child-of"),
]


@pytest.mark.unit
class TestSelectorDetection:
    @pytest.mark.parametrize("css_input,expected_id", CSS_SELECTOR_FEATURES)
    def test_selector_detected(self, parse_features, css_input, expected_id):
        assert expected_id in parse_features(css_input)
