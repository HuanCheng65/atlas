#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME/.claude/skills"

mkdir -p "$TARGET_DIR"

linked=0
skipped=0
for skill_dir in "$REPO_DIR"/skills/*/; do
    skill_name=$(basename "$skill_dir")
    target="$TARGET_DIR/$skill_name"

    if [ -L "$target" ]; then
        # already a symlink — check if it points to us
        current=$(readlink "$target")
        if [ "$current" = "$skill_dir" ] || [ "$current" = "${skill_dir%/}" ]; then
            echo "ok     $skill_name (already linked)"
            skipped=$((skipped+1))
            continue
        else
            echo "WARN   $skill_name links elsewhere: $current"
            echo "       remove it manually if you want to relink"
            skipped=$((skipped+1))
            continue
        fi
    fi

    if [ -e "$target" ]; then
        echo "WARN   $skill_name exists as a real directory at $target"
        echo "       remove it manually if you want to switch to symlink"
        skipped=$((skipped+1))
        continue
    fi

    ln -s "${skill_dir%/}" "$target"
    echo "linked $skill_name -> $target"
    linked=$((linked+1))
done

echo ""
echo "Done. $linked linked, $skipped skipped."
echo ""
echo "To initialize atlas in a project, either:"
echo "  - Run directly:    $REPO_DIR/bin/atlas-init"
echo "  - Or add to PATH:  export PATH=\"$REPO_DIR/bin:\$PATH\"  (in ~/.zshrc or ~/.bashrc)"