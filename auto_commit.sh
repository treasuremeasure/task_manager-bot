#!/bin/bash

while true; do
    git add .
    git commit -m "Auto commit"
    git push origin main  # Укажите нужную вам ветку
    sleep 300  # Задержка в 5 минут (в секундах)
done
