#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/deploy-to-vault.sh [--dry-run] /path/to/obsidian-vault

Copies Visual Blocks runtime files and Python renderer files into an Obsidian
vault. The deploy is additive/update-only: it never deletes cache files,
data.json, node_modules, or any other vault file.
EOF
}

DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=1
  shift
fi

if [ "$#" -ne 1 ]; then
  usage >&2
  exit 2
fi

VAULT_ROOT="$1"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_DEST="$VAULT_ROOT/.obsidian/plugins/visual-blocks"
PY_DEST="$VAULT_ROOT/resources/scripts/python_single"

if [ ! -d "$VAULT_ROOT" ]; then
  echo "Vault root does not exist: $VAULT_ROOT" >&2
  exit 1
fi

copy_file() {
  src="$1"
  dest="$2"
  if [ ! -f "$src" ]; then
    echo "Missing source file: $src" >&2
    exit 1
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY RUN copy file: $src -> $dest"
  else
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    echo "copied file: $src -> $dest"
  fi
}

copy_tree() {
  src_dir="$1"
  dest_dir="$2"
  if [ ! -d "$src_dir" ]; then
    echo "Missing source directory: $src_dir" >&2
    exit 1
  fi
  find "$src_dir" -type f \
    ! -path '*/__pycache__/*' \
    ! -path '*/.pytest_cache/*' \
    ! -name '*.pyc' \
    ! -name '*.pyo' \
    | sort \
    | while IFS= read -r src; do
        rel="${src#$src_dir/}"
        copy_file "$src" "$dest_dir/$rel"
      done
}

echo "Visual Blocks deploy"
echo "repo:  $REPO_ROOT"
echo "vault: $VAULT_ROOT"
if [ "$DRY_RUN" -eq 1 ]; then
  echo "mode:  dry-run"
else
  echo "mode:  copy"
fi
echo

echo "Protected paths are never copied or deleted:"
echo "- $PLUGIN_DEST/cache"
echo "- $PLUGIN_DEST/data.json"
echo "- $PLUGIN_DEST/node_modules"
echo

copy_file "$REPO_ROOT/manifest.json" "$PLUGIN_DEST/manifest.json"
copy_file "$REPO_ROOT/main.js" "$PLUGIN_DEST/main.js"
copy_file "$REPO_ROOT/styles.css" "$PLUGIN_DEST/styles.css"
copy_file "$REPO_ROOT/README.md" "$PLUGIN_DEST/README.md"
copy_tree "$REPO_ROOT/docs/assets" "$PLUGIN_DEST/docs/assets"

copy_file \
  "$REPO_ROOT/resources/scripts/python_single/render_cache.py" \
  "$PY_DEST/render_cache.py"
copy_file \
  "$REPO_ROOT/resources/scripts/python_single/tikz_cache.py" \
  "$PY_DEST/tikz_cache.py"
copy_file \
  "$REPO_ROOT/resources/scripts/python_single/migrate_to_render_cache.py" \
  "$PY_DEST/migrate_to_render_cache.py"
copy_tree \
  "$REPO_ROOT/resources/scripts/python_single/render_cache" \
  "$PY_DEST/render_cache"

echo
echo "Deploy plan complete. No files were deleted."
