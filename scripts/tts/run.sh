#!/bin/sh
# Runs narrate_tts.py with the arabic-video-studio interpreter + toolkit on the path.
TK="${AVS_HOME:-$HOME/.claude/skills/arabic-video-studio}"
PY="${AVS_PYTHON:-$HOME/.local/share/arabic-video-studio/venv/bin/python}"
export PYTHONPATH="$TK${PYTHONPATH:+:$PYTHONPATH}"
exec "$PY" "$(dirname "$0")/narrate_tts.py" "$@"
