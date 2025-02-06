#!/bin/bash
# Проверяем наличие sudo прав
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo privileges"
    exit 1
fi

# Запускаем установщик
python3 install.py 