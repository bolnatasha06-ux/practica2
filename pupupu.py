import requests
import json
import subprocess
import os
import sys
from typing import Dict, List, Set, Tuple
import re

class DependencyVisualizer:
    def __init__(self):
        self.visited_packages: Set[Tuple[str, str]] = set()
        self.all_dependencies: Dict[Tuple[str, str], List[Tuple[str, str]]] = {}
        
    def get_crate_dependencies(self, crate_name: str, version: str, max_depth: int = 2, current_depth: int = 0) -> List[Tuple[str, str]]:
        """
        Рекурсивно получает зависимости пакета
        """
        if current_depth > max_depth:
            return []
            
        cache_key = (crate_name, version)
        if cache_key in self.all_dependencies:
            return self.all_dependencies[cache_key]
        
        print(f"Получение зависимостей для {crate_name} {version} (уровень {current_depth})...")
        
        # Получаем зависимости через crates.io API
        dependencies = []
        try:
            url = f"https://crates.io/api/v1/crates/{crate_name}/{version}/dependencies"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for dep in data.get('dependencies', []):
                    dep_name = dep['crate_id']
                    dep_version = dep['req']  # Требуемая версия
                    # Нормализуем версию (убираем ^, ~ и т.д.)
                    dep_version = re.sub(r'[\^~>=<*]', '', dep_version)
                    if not dep_version or dep_version == '*':
                        dep_version = 'latest'
                    
                    dependencies.append((dep_name, dep_version))
        except Exception as e:
            print(f"Ошибка при получении зависимостей для {crate_name}: {e}")
        
        self.all_dependencies[cache_key] = dependencies
        
        # Рекурсивно получаем зависимости зависимостей
        if current_depth < max_depth:
            for dep_name, dep_version in dependencies[:5]:  # Ограничиваем для демонстрации
                if dep_version != 'latest' and (dep_name, dep_version) not in self.visited_packages:
                    self.visited_packages.add((dep_name, dep_version))
                    self.get_crate_dependencies(dep_name, dep_version, max_depth, current_depth + 1)
        
        return dependencies
    
    def build_dependency_graph(self, root_crate: str, root_version: str, max_depth: int = 2) -> str:
        """
        Строит текстовое представление графа на языке Graphviz
        """
        print(f"Построение графа зависимостей для {root_crate} {root_version}...")
        
        # Получаем все зависимости
        self.get_crate_dependencies(root_crate, root_version, max_depth)
        
        # Генерируем DOT код
        dot_content = ['digraph Dependencies {']
        dot_content.append('    rankdir=TB;')
        dot_content.append('    node [shape=box, style=filled, fillcolor=lightblue];')
        dot_content.append('    edge [color=darkgreen];')
        dot_content.append('')
        
        # Добавляем корневой узел
        root_node = f'"{root_crate}_{root_version}"'
        dot_content.append(f'    {root_node} [label="{root_crate}\\n{root_version}", fillcolor=orange];')
        dot_content.append('')
        
        # Добавляем все узлы и связи
        added_nodes = {root_node}
        
        for (crate, version), deps in self.all_dependencies.items():
            node_name = f'"{crate}_{version}"'
            node_label = f'"{crate}\\n{version}"'
            
            if node_name not in added_nodes:
                dot_content.append(f'    {node_name} [label={node_label}];')
                added_nodes.add(node_name)
            
            for dep_crate, dep_version in deps:
                dep_node_name = f'"{dep_crate}_{dep_version}"'
                dep_node_label = f'"{dep_crate}\\n{dep_version}"'
                
                if dep_node_name not in added_nodes:
                    dot_content.append(f'    {dep_node_name} [label={dep_node_label}];')
                    added_nodes.add(dep_node_name)
                
                dot_content.append(f'    {node_name} -> {dep_node_name};')
        
        dot_content.append('}')
        
        return '\n'.join(dot_content)
    
    def save_and_visualize_graph(self, dot_content: str, output_filename: str):
        """
        Сохраняет DOT файл и генерирует изображение
        """
        # Сохраняем DOT файл
        dot_filename = f"{output_filename}.dot"
        with open(dot_filename, 'w', encoding='utf-8') as f:
            f.write(dot_content)
        print(f"DOT файл сохранен: {dot_filename}")
        
        # Пробуем сгенерировать изображение с помощью Graphviz
        try:
            # PNG
            png_filename = f"{output_filename}.png"
            subprocess.run(['dot', '-Tpng', dot_filename, '-o', png_filename], check=True)
            print(f"PNG изображение сохранено: {png_filename}")
            
            # Показываем изображение если возможно
            if sys.platform == "win32":
                os.startfile(png_filename)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(['open', png_filename])
            else:  # Linux
                subprocess.run(['xdg-open', png_filename])
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Graphviz не установлен. Установите его для генерации изображений.")
            print("Ubuntu/Debian: sudo apt-get install graphviz")
            print("macOS: brew install graphviz")
            print("Windows: скачайте с https://graphviz.org/download/")
            
            # Выводим DOT код в консоль
            print("\nDOT код графа:")
            print("=" * 50)
            print(dot_content)
    
    def compare_with_cargo(self, crate_name: str, version: str):
        """
        Сравнивает результаты с выводом cargo tree
        """
        print(f"\nСравнение с cargo tree для {crate_name} {version}:")
        print("=" * 50)
        
        try:
            # Пробуем выполнить cargo tree (если cargo установлен)
            result = subprocess.run(
                ['cargo', 'tree', '--package', crate_name, '--depth', '1'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                print("Результат cargo tree:")
                print(result.stdout)
            else:
                print("cargo tree не доступен или пакет не найден локально")
                print("Для установки cargo: https://rustup.rs/")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("Cargo не установлен или команда не выполнена")
        
        print("\nНаши результаты:")
        our_deps = self.all_dependencies.get((crate_name, version), [])
        for dep_name, dep_version in our_deps:
            print(f"  - {dep_name} {dep_version}")

def demonstrate_three_packages():
    """
    Демонстрирует визуализацию для трех различных пакетов
    """
    visualizer = DependencyVisualizer()
    
    # Три различных пакета для демонстрации
    packages = [
        ("serde", "1.0"),      # Популярная библиотека сериализации
        ("tokio", "1.0"),      # Асинхронная runtime
        ("clap", "3.0"),       # Парсер аргументов командной строки
    ]
    
    for crate_name, version in packages:
        print(f"\n{'='*60}")
        print(f"ВИЗУАЛИЗАЦИЯ ДЛЯ: {crate_name} {version}")
        print(f"{'='*60}")
        
        # Строим граф
        dot_content = visualizer.build_dependency_graph(crate_name, version, max_depth=2)
        
        # Сохраняем и визуализируем
        output_filename = f"{crate_name}_{version.replace('.', '_')}_deps"
        visualizer.save_and_visualize_graph(dot_content, output_filename)
        
        # Сравниваем с cargo
        visualizer.compare_with_cargo(crate_name, version)
        
        # Очищаем для следующего пакета
        visualizer.visited_packages.clear()
        visualizer.all_dependencies.clear()

def main():
    """
    Основная функция для интерактивной визуализации
    """
    print("=== ВИЗУАЛИЗАЦИЯ ГРАФА ЗАВИСИМОСТЕЙ RUST ===")
    print("1 - Демонстрация трех пакетов")
    print("2 - Ввести свой пакет")
    
    choice = input("Выберите опцию (1 или 2): ").strip()
    
    visualizer = DependencyVisualizer()
    
    if choice == "1":
        demonstrate_three_packages()
    else:
        crate_name = input("Введите имя пакета: ").strip()
        version = input("Введите версию пакета: ").strip()
        max_depth = input("Введите глубину анализа (по умолчанию 2): ").strip()
        
        if not max_depth:
            max_depth = 2
        else:
            max_depth = int(max_depth)
        
        print(f"\nСтроим граф зависимостей для {crate_name} {version}...")
        dot_content = visualizer.build_dependency_graph(crate_name, version, max_depth)
        
        output_filename = f"{crate_name}_{version.replace('.', '_')}_deps"
        visualizer.save_and_visualize_graph(dot_content, output_filename)
        visualizer.compare_with_cargo(crate_name, version)

if __name__ == "__main__":
    main()