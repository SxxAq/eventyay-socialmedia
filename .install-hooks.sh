#!/usr/bin/env bash
REPO_DIR=$(git rev-parse --show-toplevel)
GIT_DIR="$REPO_DIR/.git"
VENV_ACTIVATE="$VIRTUAL_ENV/bin/activate"
if [[ ! -f "$VENV_ACTIVATE" ]]
then
    echo "Could not find your virtual environment"
    exit 1
fi

echo "#!/bin/sh" > "$GIT_DIR/hooks/pre-commit"
echo "set -e" >> "$GIT_DIR/hooks/pre-commit"
echo "source \"$VENV_ACTIVATE\"" >> "$GIT_DIR/hooks/pre-commit"
echo "ruff check --select I ." >> "$GIT_DIR/hooks/pre-commit"
echo "ruff format --check ." >> "$GIT_DIR/hooks/pre-commit"
echo "flake8 ." >> "$GIT_DIR/hooks/pre-commit"
chmod +x "$GIT_DIR/hooks/pre-commit"

