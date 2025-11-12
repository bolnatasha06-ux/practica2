"""
Этап 5: Визуализация графа зависимостей пакетов Python
Автор: [Ваше имя]
Дата: [Дата]
"""

import subprocess
import sys
import json
import pkg_resources
from typing import Dict, List, Set, Tuple
import os

try:
    import graphviz
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError as e:
    print("Ошибка импорта. Убедитесь, что установлены все зависимости:")
    print("pip install graphviz pydot networkx matplotlib")
    sys.exit(1)


class DependencyVisualizer:
    """Класс для визуализации графа зависимостей пакетов Python"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.visited_packages = set()
        
    def get_package_dependencies(self, package_name: str) -> List[str]:
        """Получить зависимости пакета"""
        try:
            dist = pkg_resources.get_distribution(package_name)
            return [str(req) for req in dist.requires()]
        except:
            return []
    
    def build_dependency_graph(self, package_name: str, depth: int = 2, current_depth: int = 0):
        """Рекурсивно построить граф зависимостей"""
        if current_depth > depth or package_name in self.visited_packages:
            return
            
        self.visited_packages.add(package_name)
        
        # Добавляем узел для текущего пакета
        self.graph.add_node(package_name)
        
        # Получаем зависимости
        dependencies = self.get_package_dependencies(package_name)
        
        for dep in dependencies:
            # Извлекаем имя пакета из строки требования
            dep_name = dep.split('[')[0].split('(')[0].strip()
            
            # Добавляем зависимость в граф
            self.graph.add_edge(package_name, dep_name)
            
            # Рекурсивно обрабатываем зависимости
            if current_depth < depth:
                self.build_dependency_graph(dep_name, depth, current_depth + 1)
    
    def generate_graphviz_code(self, package_name: str) -> str:
        """Сгенерировать код Graphviz для графа зависимостей"""
        
        dot = graphviz.Digraph(comment=f'Dependencies for {package_name}')
        dot.attr(rankdir='TB', size='8,8')
        dot.attr('node', shape='box', style='filled', color='lightblue2')
        
        # Добавляем узлы и ребра
        for node in self.graph.nodes():
            if node == package_name:
                # Основной пакет выделяем другим цветом
                dot.node(node, node, shape='ellipse', style='filled', 
                        color='lightcoral', fontsize='14')
            else:
                dot.node(node, node)
        
        for edge in self.graph.edges():
            dot.edge(edge[0], edge[1])
        
        return dot.source
    
    def visualize_with_graphviz(self, package_name: str, output_format: str = 'png'):
        """Визуализировать граф с помощью Graphviz"""
        try:
            dot = graphviz.Digraph(comment=f'Dependencies for {package_name}')
            dot.attr(rankdir='TB', size='8,8')
            dot.attr('node', shape='box', style='filled', color='lightblue2')
            
            # Добавляем узлы и ребра
            for node in self.graph.nodes():
                if node == package_name:
                    dot.node(node, node, shape='ellipse', style='filled', 
                            color='lightcoral', fontsize='14')
                else:
                    dot.node(node, node)
            
            for edge in self.graph.edges():
                dot.edge(edge[0], edge[1])
            
            # Сохраняем и отображаем
            output_file = f"{package_name}_dependencies"
            dot.render(output_file, format=output_format, cleanup=True)
            print(f"Граф сохранен как {output_file}.{output_format}")
            
            # Показываем изображение если возможно
            if output_format == 'png' and os.name == 'posix':
                try:
                    subprocess.run(['xdg-open', f"{output_file}.{output_format}"])
                except:
                    pass
                    
        except Exception as e:
            print(f"Ошибка при визуализации Graphviz: {e}")
    
    def visualize_with_networkx(self, package_name: str):
        """Визуализировать граф с помощью NetworkX и Matplotlib"""
        try:
            plt.figure(figsize=(12, 8))
            
            # Создаем layout для графа
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
            
            # Рисуем граф
            nx.draw_networkx_nodes(self.graph, pos, 
                                 node_color='lightblue', 
                                 node_size=500, 
                                 alpha=0.9)
            
            # Выделяем основной пакет
            nx.draw_networkx_nodes(self.graph, pos, 
                                 nodelist=[package_name], 
                                 node_color='red', 
                                 node_size=700, 
                                 alpha=0.8)
            
            nx.draw_networkx_edges(self.graph, pos, 
                                 arrowstyle='->', 
                                 arrowsize=10, 
                                 edge_color='gray',
                                 width=1)
            
            nx.draw_networkx_labels(self.graph, pos, 
                                  font_size=8, 
                                  font_family='sans-serif')
            
            plt.title(f'Граф зависимостей для {package_name}', size=15)
            plt.axis('off')
            plt.tight_layout()
            
            # Сохраняем изображение
            output_file = f"{package_name}_dependencies_networkx.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Граф NetworkX сохранен как {output_file}")
            
            plt.show()
            
        except Exception as e:
            print(f"Ошибка при визуализации NetworkX: {e}")
    
    def compare_with_pip_tools(self, package_name: str):
        """Сравнить с результатами штатных инструментов"""
        print(f"\n=== Сравнение результатов для {package_name} ===")
        
        # Наш граф
        our_nodes = set(self.graph.nodes())
        our_edges = set(self.graph.edges())
        
        print(f"Наш инструмент: {len(our_nodes)} пакетов, {len(our_edges)} зависимостей")
        
        # Попробуем использовать pipdeptree для сравнения
        try:
            result = subprocess.run(['pipdeptree', '-p', package_name], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("pipdeptree успешно выполнен")
                # Простой анализ вывода pipdeptree
                lines = result.stdout.strip().split('\n')
                pip_packages = set()
                
                for line in lines:
                    if '├──' in line or '└──' in line:
                        dep = line.split('├──')[-1].split('└──')[-1].strip()
                        dep_name = dep.split('==')[0].split('[')[0]
                        pip_packages.add(dep_name)
                
                print(f"pipdeptree: {len(pip_packages)} зависимостей")
                
                # Сравнение
                common = our_nodes.intersection(pip_packages)
                only_our = our_nodes - pip_packages
                only_pip = pip_packages - our_nodes
                
                print(f"Общие зависимости: {len(common)}")
                print(f"Только в нашем инструменте: {len(only_our)}")
                if only_our:
                    print(f"  {list(only_our)}")
                print(f"Только в pipdeptree: {len(only_pip)}")
                if only_pip:
                    print(f"  {list(only_pip)}")
                    
            else:
                print("pipdeptree не установлен. Установите: pip install pipdeptree")
                
        except FileNotFoundError:
            print("pipdeptree не установлен. Установите: pip install pipdeptree")
        except Exception as e:
            print(f"Ошибка при сравнении: {e}")


def main():
    """Основная функция программы"""
    print("=== Визуализатор графа зависимостей пакетов Python ===\n")
    
    # Пакеты для демонстрации
    demo_packages = ['requests', 'flask', 'pandas']
    
    for package in demo_packages:
        print(f"\n{'='*50}")
        print(f"ВИЗУАЛИЗАЦИЯ ДЛЯ ПАКЕТА: {package}")
        print(f"{'='*50}")
        
        try:
            # Создаем визуализатор
            visualizer = DependencyVisualizer()
            
            # Строим граф зависимостей
            print("Построение графа зависимостей...")
            visualizer.build_dependency_graph(package, depth=2)
            
            # Генерируем код Graphviz
            graphviz_code = visualizer.generate_graphviz_code(package)
            print(f"\n1. Graphviz код для {package}:")
            print("```dot")
            print(graphviz_code[:500] + "..." if len(graphviz_code) > 500 else graphviz_code)
            print("```")
            
            # Визуализируем с Graphviz
            print(f"\n2. Создание изображения Graphviz...")
            visualizer.visualize_with_graphviz(package)
            
            # Визуализируем с NetworkX
            print(f"\n3. Создание изображения NetworkX...")
            visualizer.visualize_with_networkx(package)
            
            # Сравниваем с штатными инструментами
            print(f"\n4. Сравнение с штатными инструментами...")
            visualizer.compare_with_pip_tools(package)
            
            # Статистика графа
            print(f"\n5. Статистика графа для {package}:")
            print(f"   - Всего узлов: {len(visualizer.graph.nodes())}")
            print(f"   - Всего рёбер: {len(visualizer.graph.edges())}")
            print(f"   - Максимальная глубина: 2")
            
        except Exception as e:
            print(f"Ошибка при обработке пакета {package}: {e}")
            continue
    
    print(f"\n{'='*50}")
    print("ВИЗУАЛИЗАЦИЯ ЗАВЕРШЕНА")
    print(f"{'='*50}")
    print("\nСозданные файлы:")
    for package in demo_packages:
        print(f"  - {package}_dependencies.png (Graphviz)")
        print(f"  - {package}_dependencies_networkx.png (NetworkX)")
        print(f"  - {package}_dependencies (исходный файл Graphviz)")


if __name__ == "__main__":
    main()