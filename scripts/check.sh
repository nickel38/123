#!/bin/sh
set -eu
python3 -m unittest discover -s tests -v
python3 -m src.main --vfs fixtures/minimal.json --script scripts/startup/stage5.txt </dev/null || test $? -eq 0
echo "Проверки завершены"
