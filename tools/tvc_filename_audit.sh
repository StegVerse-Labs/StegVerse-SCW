#!/usr/bin/env bash
set -euo pipefail

ORG="${1:-StegVerse-Labs}"

# Space-separated list of repos to audit.
# You can also export TARGET_REPOS in a workflow and call this script.
TARGET_REPOS="${TARGET_REPOS:-"TVC TV FREE-DOM hybrid-collab-bridge StegVerse-SCW"}"

REQUIRED=("stegtvc_config.json" "tv_config.json")
TYPO=("stegvtc_config.json")

echo "=== StegTVC filename audit ==="
echo "Org:   $ORG"
echo "Repos: $TARGET_REPOS"
echo

for REPO in $TARGET_REPOS; do
  echo ">>> $ORG/$REPO"

  CLONE_DIR="audit_${REPO}"
  if ! gh repo clone "$ORG/$REPO" "$CLONE_DIR" -- --depth 1 >/dev/null 2>&1; then
    echo "  ⚠️  Could not clone – skipping."
    echo
    continue
  fi

  cd "$CLONE_DIR"

  FOUND_DIRS=()
  [[ -d "TVC/data" ]] && FOUND_DIRS+=("TVC/data")
  [[ -d "data" ]] && FOUND_DIRS+=("data")

  if [[ ${#FOUND_DIRS[@]} -eq 0 ]]; then
    echo "  ⚠️  No 'TVC/data' or 'data' directory – nothing to audit."
    cd ..
    rm -rf "$CLONE_DIR"
    echo
    continue
  fi

  for DIR in "${FOUND_DIRS[@]}"; do
    echo "  Checking $DIR"

    for f in "${REQUIRED[@]}"; do
      if [[ -f "$DIR/$f" ]]; then
        echo "    ✅ $f present"
      else
        echo "    ❌ $f MISSING"
      fi
    done

    for f in "${TYPO[@]}"; do
      if [[ -f "$DIR/$f" ]]; then
        echo "    ❌ TYPO present: $f"
      fi
    done
  done

  cd ..
  rm -rf "$CLONE_DIR"
  echo
done

echo "=== Audit complete ==="
