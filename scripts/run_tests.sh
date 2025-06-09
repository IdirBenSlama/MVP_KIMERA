#!/bin/bash
# Run pytest with lightweight embedding and jobs disabled
export LIGHTWEIGHT_EMBEDDING=1
export ENABLE_JOBS=0
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"
pytest "$@"
