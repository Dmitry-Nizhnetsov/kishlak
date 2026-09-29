#!/bin/bash
# Запуск эмулятора со стартовым скриптом
cd "$(dirname "$0")/.."
python3 -m src.main --script scripts/test_stage2.txt