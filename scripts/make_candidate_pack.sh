#!/usr/bin/env bash
# Zips one exercise for a candidate, without the interviewer-only folder.
# Usage: scripts/make_candidate_pack.sh cloud-swe/2-mid-order-service
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: $0 <exercise-folder>" >&2
  exit 1
fi

SRC="$(cd "$1" && pwd)"
NAME="$(basename "$SRC")"
OUT="$(pwd)/${NAME}-candidate.zip"
TMP="$(mktemp -d)"

cp -r "$SRC" "$TMP/$NAME"
rm -rf "$TMP/$NAME/_interviewer"
find "$TMP" -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$TMP" -name ".pytest_cache" -type d -prune -exec rm -rf {} + 2>/dev/null || true

rm -f "$OUT"
(cd "$TMP" && zip -qr "$OUT" "$NAME")
rm -rf "$TMP"
echo "Wrote $OUT"
