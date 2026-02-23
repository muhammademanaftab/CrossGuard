#!/bin/bash
# Cross Guard CLI — Manual Test Script
# Run: bash test_cli_manual.sh

cd "$(dirname "$0")"
JS="tests/validation/js/comprehensive_test.js"

echo "============================================"
echo "1. VERBOSE OUTPUT"
echo "============================================"
python -m src.cli.main -v analyze "$JS" --format summary
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "2. QUIET MODE (should suppress INFO logs)"
echo "============================================"
python -m src.cli.main -q analyze "$JS" --format summary
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "3. NO COLOR (TABLE FORMAT)"
echo "============================================"
python -m src.cli.main --no-color analyze "$JS" --format table
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "4. TIMING FLAG"
echo "============================================"
python -m src.cli.main --timing analyze "$JS" --format summary
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "5. BROWSER TYPO SUGGESTION (expect exit 2)"
echo "============================================"
python -m src.cli.main analyze "$JS" --browsers "chome:120"
rc=$?; echo ""; echo "Exit code: $rc (expect 2)"; echo ""

echo "============================================"
echo "6. CUSTOM BROWSERS"
echo "============================================"
python -m src.cli.main analyze "$JS" --browsers "chrome:120,firefox:121" --format summary
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "7. FORMAT: SARIF (stdout, first 30 lines)"
echo "============================================"
python -m src.cli.main analyze "$JS" --format sarif 2>/dev/null | python -m json.tool | head -30
rc=${PIPESTATUS[0]}; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "8. FORMAT: SARIF (to file)"
echo "============================================"
python -m src.cli.main analyze "$JS" --format sarif -o /tmp/cg_report.sarif
rc=$?
echo "Exit code: $rc"
echo "File exists: $(test -f /tmp/cg_report.sarif && echo YES || echo NO)"
echo "File size: $(wc -c < /tmp/cg_report.sarif 2>/dev/null || echo 0) bytes"
echo ""

echo "============================================"
echo "9. FORMAT: JUNIT XML (first 20 lines)"
echo "============================================"
python -m src.cli.main analyze "$JS" --format junit 2>/dev/null | head -20
rc=${PIPESTATUS[0]}; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "10. FORMAT: CHECKSTYLE XML (first 20 lines)"
echo "============================================"
python -m src.cli.main analyze "$JS" --format checkstyle 2>/dev/null | head -20
rc=${PIPESTATUS[0]}; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "11. FORMAT: CSV (first 15 lines)"
echo "============================================"
python -m src.cli.main analyze "$JS" --format csv 2>/dev/null | head -15
rc=${PIPESTATUS[0]}; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "12. FORMAT: JSON (first 20 lines)"
echo "============================================"
python -m src.cli.main analyze "$JS" --format json 2>/dev/null | python -m json.tool | head -20
rc=${PIPESTATUS[0]}; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "13. FORMAT: TABLE"
echo "============================================"
python -m src.cli.main analyze "$JS" --format table
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "14. QUALITY GATE: PASS (score >= 0)"
echo "============================================"
python -m src.cli.main analyze "$JS" --format summary --fail-on-score 0
rc=$?; echo ""; echo "Exit code: $rc (expect 0 = PASS)"; echo ""

echo "============================================"
echo "15. QUALITY GATE: FAIL (score >= 100.1)"
echo "============================================"
python -m src.cli.main analyze "$JS" --format summary --fail-on-score 100.1
rc=$?; echo ""; echo "Exit code: $rc (expect 1 = FAIL)"; echo ""

echo "============================================"
echo "16. QUALITY GATE: FAIL ON ERRORS"
echo "============================================"
python -m src.cli.main analyze "$JS" --format summary --fail-on-errors 0
rc=$?; echo ""; echo "Exit code: $rc (expect 1)"; echo ""

echo "============================================"
echo "17. QUALITY GATE: FAIL ON WARNINGS"
echo "============================================"
python -m src.cli.main analyze "$JS" --format summary --fail-on-warnings 0
rc=$?; echo ""; echo "Exit code: $rc (expect 1)"; echo ""

echo "============================================"
echo "18. STDIN SUPPORT (JS)"
echo "============================================"
echo "const x = Promise.resolve(); let y = 2;" | python -m src.cli.main analyze --stdin --stdin-filename test.js --format summary
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "19. STDIN SUPPORT (CSS)"
echo "============================================"
echo "body { display: flex; gap: 10px; }" | python -m src.cli.main analyze --stdin --stdin-filename test.css --format summary
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "20. STDIN MISSING FILENAME (expect exit 2)"
echo "============================================"
echo "const x = 1;" | python -m src.cli.main analyze --stdin --format summary
rc=$?; echo ""; echo "Exit code: $rc (expect 2)"; echo ""

echo "============================================"
echo "21. MULTIPLE OUTPUTS (table + sarif + junit + json + csv)"
echo "============================================"
python -m src.cli.main analyze "$JS" --format table --output-sarif /tmp/cg_multi.sarif --output-junit /tmp/cg_multi.xml --output-json /tmp/cg_multi.json --output-csv /tmp/cg_multi.csv
rc=$?
echo ""
echo "Exit code: $rc"
echo "SARIF: $(test -f /tmp/cg_multi.sarif && echo YES || echo NO) ($(wc -c < /tmp/cg_multi.sarif 2>/dev/null || echo 0) bytes)"
echo "JUnit: $(test -f /tmp/cg_multi.xml && echo YES || echo NO) ($(wc -c < /tmp/cg_multi.xml 2>/dev/null || echo 0) bytes)"
echo "JSON:  $(test -f /tmp/cg_multi.json && echo YES || echo NO) ($(wc -c < /tmp/cg_multi.json 2>/dev/null || echo 0) bytes)"
echo "CSV:   $(test -f /tmp/cg_multi.csv && echo YES || echo NO) ($(wc -c < /tmp/cg_multi.csv 2>/dev/null || echo 0) bytes)"
echo ""

echo "============================================"
echo "22. DIRECTORY SCAN"
echo "============================================"
python -m src.cli.main analyze tests/validation/js/01_syntax/ --format summary
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "23. INIT-CI: GITHUB"
echo "============================================"
python -m src.cli.main init-ci -p github
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "24. INIT-CI: GITLAB"
echo "============================================"
python -m src.cli.main init-ci -p gitlab
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "25. INIT-HOOKS: PRE-COMMIT"
echo "============================================"
python -m src.cli.main init-hooks -t pre-commit
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "26. INIT-CI: MISSING PROVIDER (expect exit 2)"
echo "============================================"
python -m src.cli.main init-ci
rc=$?; echo ""; echo "Exit code: $rc (expect 2)"; echo ""

echo "============================================"
echo "27. COMBINED: TIMING + NO-COLOR + GATES + MULTI-OUTPUT"
echo "============================================"
python -m src.cli.main --timing --no-color analyze "$JS" --format summary --fail-on-score 50 --output-sarif /tmp/cg_final.sarif --output-junit /tmp/cg_final.xml
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "28. SHOW CONFIG"
echo "============================================"
python -m src.cli.main config
rc=$?; echo ""; echo "Exit code: $rc"; echo ""

echo "============================================"
echo "29. HELP"
echo "============================================"
python -m src.cli.main --help
echo ""

echo "============================================"
echo "30. ANALYZE HELP"
echo "============================================"
python -m src.cli.main analyze --help
echo ""

# Cleanup temp files
rm -f /tmp/cg_report.sarif /tmp/cg_multi.sarif /tmp/cg_multi.xml /tmp/cg_multi.json /tmp/cg_multi.csv /tmp/cg_final.sarif /tmp/cg_final.xml

echo "============================================"
echo "ALL 30 TESTS COMPLETE"
echo "============================================"
