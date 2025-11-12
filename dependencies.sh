#!/bin/bash
# install_dependencies.sh

echo "Установка зависимостей для визуализатора графа зависимостей..."

# Установка Python пакетов
pip install graphviz pydot networkx matplotlib pipdeptree

# Проверка установки Graphviz
if ! command -v dot &> /dev/null; then
    echo "Graphviz не установлен. Пожалуйста, установите вручную:"
    echo "Ubuntu/Debian: sudo apt-get install graphviz"
    echo "macOS: brew install graphviz"
    echo "Windows: скачайте с https://graphviz.org/download/"
else
    echo "Graphviz установлен: $(dot -V)"
fi

echo "Установка завершена!"