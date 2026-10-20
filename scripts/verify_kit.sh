#!/usr/bin/env bash
# Runs every reference solution against the exercise's visible tests and hidden tests.
# Usage: scripts/verify_kit.sh   (from anywhere)
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
status=0

for sol in "$ROOT"/*/*/_interviewer/solution; do
  [ -d "$sol" ] || continue
  ex="$(dirname "$(dirname "$sol")")"
  name="${ex#"$ROOT"/}"
  tmp="$(mktemp -d)"

  cp -r "$ex/." "$tmp/"
  rm -rf "$tmp/_interviewer"
  cp -r "$sol/." "$tmp/"
  if [ -d "$ex/_interviewer/hidden_tests" ]; then
    mkdir -p "$tmp/tests"
    cp -r "$ex/_interviewer/hidden_tests/." "$tmp/tests/"
  fi

  if out="$(cd "$tmp" && "$PY" -m pytest -q -p no:cacheprovider 2>&1)"; then
    echo "PASS  $name  ($(echo "$out" | tail -1))"
  else
    echo "FAIL  $name"
    echo "$out" | tail -25
    status=1
  fi
  rm -rf "$tmp"
done

exit $status
