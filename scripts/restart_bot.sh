#!/bin/bash
set -e

pkill -f "python -m bot.main" 2>/dev/null && echo "Остановлен старый процесс бота" || echo "Старых процессов не найдено"
sleep 1

PYTHONPATH=. python -m bot.main
