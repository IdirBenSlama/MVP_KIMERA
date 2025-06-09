#!/bin/bash
# Run pytest with lightweight embedding and jobs disabled
set -e

LIGHTWEIGHT_EMBEDDING=1 ENABLE_JOBS=0 pytest "$@"
