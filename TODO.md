# Cross Guard - Project Checklist

## Custom Rules Testing
- [ ] Manual testing of custom CSS rules
- [ ] Manual testing of custom JavaScript rules
- [ ] Manual testing of custom HTML rules
- [ ] Automated tests for custom rules loader
- [ ] Automated tests for custom rule pattern matching
- [ ] Test custom rules via GUI rules manager

## Scanner/Project Testing
- [ ] Manual testing of HTML parser
- [ ] Manual testing of CSS parser
- [ ] Manual testing of JS parser
- [ ] Run automated parser test suite (`pytest tests/parsers/`)
- [ ] End-to-end manual testing (upload files, check results)
- [ ] Test compatibility scoring accuracy
- [ ] Test browser version range handling
- [ ] Test export functionality (PDF/JSON)

## Polyfills Testing
- [ ] Research polyfill detection requirements
- [ ] Manual testing of polyfill suggestions
- [ ] Automated tests for polyfill recommendations
- [ ] Test polyfill integration with analysis results

## Feature Research
- [ ] Research additional CSS features to detect
- [ ] Research additional JS API features to detect
- [ ] Research additional HTML5 features to detect
- [ ] Look into framework-specific compatibility checks
- [ ] Investigate source map support
- [ ] Research minified code handling improvements

## CLI Integration
- [ ] Design CLI interface structure
- [ ] Create separate CLI entry point
- [ ] Implement file/directory scanning via CLI
- [ ] Add CLI output formatting (table, JSON, plain text)
- [ ] Add CLI configuration options (browser targets, etc.)
- [ ] Make CLI installable as standalone tool
- [ ] Write CLI documentation/help text
- [ ] Test CLI on different platforms

---

## Notes
_Add any notes or discoveries here as you work through the checklist._

