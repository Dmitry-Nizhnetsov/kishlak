#!/bin/bash
cd "$(dirname "$0")/.."
python3 -m src.main --vfs vfs/deep.zip --script scripts/test_stage3.txt