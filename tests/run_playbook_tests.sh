#!/usr/bin/env bash
# Run all integration playbooks in order; do not stop on first failure.
# Writes per-playbook logs and a Markdown summary under tests/reports/.
#
# Usage (from repo root, with venv activated):
#   bash tests/run_playbook_tests.sh
# Or: make test

set -uo pipefail

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$TESTS_DIR" || exit 1

REPORT_DIR="reports"
mkdir -p "$REPORT_DIR/logs"

RUN_ID="$(date +%Y%m%d-%H%M%S)"
TIMESTAMP_UTC="$(date -u +"%Y-%m-%d %H:%M:%S UTC")"
REPORT_MD="${REPORT_DIR}/test-report-${RUN_ID}.md"
LATEST_MD="${REPORT_DIR}/latest-test-report.md"

PLAYBOOKS=(playbooks/[0-9]*.yml)

{
  printf '# Playbook test report\n\n'
  printf '**Run (UTC):** %s  \n' "$TIMESTAMP_UTC"
  printf '**Working directory:** `tests/`  \n'
  printf '**Inventory:** `inventory.yml`  \n\n'
  printf '## Results\n\n'
  printf '| # | Playbook | Result | Seconds | Log |\n'
  printf '|---|----------|--------|---------|-----|\n'
} >"$REPORT_MD"

failures=0
total="${#PLAYBOOKS[@]}"
idx=0

for pb in "${PLAYBOOKS[@]}"; do
  idx=$((idx + 1))
  base="$(basename "$pb" .yml)"
  log_rel="logs/${RUN_ID}-${base}.log"
  log_path="${REPORT_DIR}/${log_rel}"

  printf '==> [%d/%d] %s\n' "$idx" "$total" "$pb"
  start_ts=$(date +%s)
  rc=0
  ansible-playbook -i inventory.yml "$pb" -v >"$log_path" 2>&1 || rc=$?
  end_ts=$(date +%s)
  dur=$((end_ts - start_ts))

  if [ "$rc" -eq 0 ]; then
    result="PASS"
  else
    result="FAIL"
    failures=$((failures + 1))
    printf '    FAILED (exit %d) — see %s\n' "$rc" "$log_path"
  fi

  printf '| %d | `%s` | **%s** | %d | [`%s`](%s) |\n' \
    "$idx" "$pb" "$result" "$dur" "$base" "$log_rel" >>"$REPORT_MD"
done

passed=$((total - failures))

{
  printf '\n## Summary\n\n'
  printf '| Metric | Count |\n'
  printf '|--------|-------|\n'
  printf '| Total | %d |\n' "$total"
  printf '| Passed | %d |\n' "$passed"
  printf '| Failed | %d |\n' "$failures"
  printf '\nFull Markdown report: `%s`\n' "$REPORT_MD"
} >>"$REPORT_MD"

ln -sf "$(basename "$REPORT_MD")" "$LATEST_MD"

echo ""
echo "Report: ${TESTS_DIR}/${REPORT_MD}"
echo "Latest: ${TESTS_DIR}/${LATEST_MD}"
echo "Summary: ${passed}/${total} passed, ${failures} failed."

if [ "$failures" -gt 0 ]; then
  exit 1
fi
exit 0
