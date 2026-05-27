#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME/.claude/skills"

for skill_dir in "$REPO_DIR"/skills/*/; do
    skill_name=$(basename "$skill_dir")
    target="$TARGET_DIR/$skill_name"

    if [ -L "$target" ]; then
        current=$(readlink "$target")
        if [ "$current" = "${skill_dir%/}" ] || [ "$current" = "$skill_dir" ]; then
            rm "$target"
            echo "removed $skill_name"
        else
            echo "skip    $skill_name (links elsewhere: $current)"
        fi
    fi
done