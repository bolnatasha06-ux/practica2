import subprocess
import sys
import json
from pathlib import Path
import pkg_resources
from packaging.requirements import Requirement

class DependencyVisualizer:
    def __init__(self):
        self.graphviz_installed = self.check_graphviz_installed()
        
    def check_graphviz_installed(self):
        """Проверяет, установлен ли Graphviz в системе"""
        try:
            subprocess.run(['dot', '-V'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_package_dependencies(self, package_name):
        """Получает зависимости пакета"""
        try:
            # Получаем информацию о пакете
            dist = pkg_resources.get_distribution(package_name)
            dependencies = []
            
            # Получаем зависимости
            for requirement in dist.requires():
                req = Requirement(str(requirement))
                dependencies.append(req.name)
            
            return dependencies, dist.version
        except Exception as e:
            print(f"Ошибка при получении зависимостей для {package_name}: {e}")
            return [], None
    
    def build_dependency_graph(self, package_name, max_depth=3):
        """Строит граф зависимостей рекурсивно"""
        graph = {}
        self._collect_dependencies(package_name, graph, 0, max_depth)
        return graph
    
    def _collect_dependencies(self, package_name, graph, current_depth, max_depth):
        """Рекурсивно собирает зависимости"""
        if current_depth >= max_depth or package_name in graph:
            return
        
        dependencies, version = self.get_package_dependencies(package_name)
        graph[package_name] = {
            'version': version,
            'dependencies': dependencies
        }
        
        for dep in dependencies:
            if dep not in graph:
                self._collect_dependencies(dep, graph, current_depth + 1, max_depth)
    
    def generate_graphviz_code(self, graph, main_package):
        """Генерирует код Graphviz для визуализации"""
        dot_code = ['digraph Dependencies {', '    rankdir=TB;', '    node [shape=box, style=filled, fillcolor=lightblue];']
        
        # Добавляем основной пакет
        dot_code.append(f'    "{main_package}" [fillcolor=orange];')
        
        # Добавляем узлы и связи
        for package, info in graph.items():
            version = info['version'] or 'unknown'
            dot_code.append(f'    "{package}" [label="{package}\\n{version}"];')
            
            for dep in info['dependencies']:
                dot_code.append(f'    "{package}" -> "{dep}";')
        
        dot_code.append('}')
        return '\n'.join(dot_code)
    
    def save_and_render_graph(self, dot_code, filename):
        """Сохраняет и рендерит граф"""
        # Сохраняем DOT файл
        dot_filename = f"{filename}.dot"
        with open(dot_filename, 'w', encoding='utf-8') as f:
            f.write(dot_code)
        print(f"DOT файл сохранен: {dot_filename}")
        
        # Рендерим изображение если установлен Graphviz
        if self.graphviz_installed:
            for format in ['png', 'svg']:
                output_file = f"{filename}.{format}"
                try:
                    subprocess.run([
                        'dot', '-T', format, dot_filename, '-o', output_file
                    ], check=True, capture_output=True)
                    print(f"Изображение сохранено: {output_file}")
                except subprocess.CalledProcessError as e:
                    print(f"Ошибка при создании {format}: {e}")
        else:
            print("Graphviz не установлен. Установите его для генерации изображений.")
    
    def compare_with_pip_tools(self, package_name):
        """Сравнивает с результатами pip-tools"""
        try:
            # Пытаемся использовать pipdeptree если установлен
            import pipdeptree
            from pipdeptree import get_installed_distributions
            
            print(f"\nСравнение с pipdeptree для {package_name}:")
            
            # Получаем дерево зависимостей через pipdeptree
            distributions = get_installed_distributions()
            tree = pipdeptree.PackageDAG.from_pkgs(distributions)
            
            # Ищем наш пакет в дереве
            for node in tree:
                if node.key == package_name.lower():
                    print(f"pipdeptree нашел пакет: {node}")
                    break
            else:
                print(f"pipdeptree не нашел пакет {package_name}")
                
        except ImportError:
            print("pipdeptree не установлен. Установите: pip install pipdeptree")
    
    def visualize_package(self, package_name, max_depth=2):
        """Основная функция визуализации для одного пакета"""
        print(f"\n{'='*50}")
        print(f"Визуализация зависимостей для: {package_name}")
        print(f"{'='*50}")
        
        # Строим граф зависимостей
        graph = self.build_dependency_graph(package_name, max_depth)
        
        if not graph:
            print(f"Не удалось построить граф для {package_name}")
            return
        
        print(f"Найдено пакетов в графе: {len(graph)}")
        
        # Генерируем код Graphviz
        dot_code = self.generate_graphviz_code(graph, package_name)
        
        # Сохраняем и рендерим
        filename = f"dependency_graph_{package_name.replace('-', '_')}"
        self.save_and_render_graph(dot_code, filename)
        
        # Выводим DOT код на экран
        print(f"\nDOT код для {package_name}:")
        print(dot_code)
        
        # Сравниваем с pip-tools
        self.compare_with_pip_tools(package_name)
        
        return graph

def main():
    """Основная функция программы"""
    visualizer = DependencyVisualizer()
    
    # Список пакетов для демонстрации
    demo_packages = ['requests', 'flask', 'numpy']
    
    all_graphs = {}
    
    for package in demo_packages:
        try:
            graph = visualizer.visualize_package(package)
            all_graphs[package] = graph
        except Exception as e:
            print(f"Ошибка при обработке {package}: {e}")
    
    # Сводная информация
    print(f"\n{'='*50}")
    print("СВОДНАЯ ИНФОРМАЦИЯ")
    print(f"{'='*50}")
    
    for package, graph in all_graphs.items():
        if graph:
            print(f"{package}: {len(graph)} пакетов в графе")
    
    print(f"\nДля просмотра графов:")
    print("1. Установите Graphviz: https://graphviz.org/download/")
    print("2. Откройте сгенерированные .png файлы")
    print("3. Или используйте онлайн визуализатор для .dot файлов")

if __name__ == "__main__":
    main()