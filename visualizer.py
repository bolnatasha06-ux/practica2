import subprocess
import os
import sys

class DependencyVisualizer:
    """
    Класс для визуализации графа зависимостей с помощью Graphviz
    """
    
    def __init__(self):
        self.check_graphviz_installation()
    
    def check_graphviz_installation(self):
        """
        Проверяет установлен ли Graphviz
        """
        try:
            subprocess.run(['dot', '-V'], capture_output=True, check=True)
            print("✅ Graphviz установлен и доступен")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Graphviz не установлен или не найден в PATH")
            print("Установите Graphviz: https://graphviz.org/download/")
            return False
    
    def generate_dot_graph(self, crate_name, version, dependencies):
        """
        Генерирует DOT представление графа зависимостей
        """
        dot_content = [
            'digraph dependencies {',
            '    rankdir=TB;',
            '    node [shape=box, style=filled, fillcolor=lightblue];',
            '    edge [color=darkgreen];',
            '    graph [bgcolor=white];',
            '',
            f'    // Центральный узел - основной пакет',
            f'    "{crate_name}_{version}" [',
            f'        label="{crate_name}\\n{version}",',
            '        fillcolor=lightcoral,',
            '        fontsize=16,',
            '        shape=ellipse',
            '    ];',
            ''
        ]
        
        # Добавляем зависимости
        for i, dep in enumerate(dependencies):
            dep_id = f"{dep['name']}_{i}"
            kind_color = "lightyellow" if dep['kind'] == 'dev' else "lightgreen"
            optional_style = ", style=dashed" if dep['optional'] else ""
            
            dot_content.extend([
                f'    // Зависимость: {dep["name"]}',
                f'    "{dep_id}" [',
                f'        label="{dep["name"]}\\n{dep["version"]}",',
                f'        fillcolor="{kind_color}"{optional_style}',
                '    ];',
                '',
                f'    // Связь: {crate_name} -> {dep["name"]}',
                f'    "{crate_name}_{version}" -> "{dep_id}"',
                f'        [label="{dep.get("kind", "normal")}"];',
                ''
            ])
        
        dot_content.append('}')
        
        return '\n'.join(dot_content)
    
    def generate_image(self, dot_source, output_filename, format='png'):
        """
        Генерирует изображение из DOT источника
        """
        try:
            # Сохраняем DOT во временный файл
            temp_dot = 'temp_graph.dot'
            with open(temp_dot, 'w', encoding='utf-8') as f:
                f.write(dot_source)
            
            # Запускаем Graphviz
            result = subprocess.run([
                'dot', 
                f'-T{format}', 
                temp_dot, 
                '-o', output_filename
            ], capture_output=True, check=True)
            
            # Удаляем временный файл
            os.remove(temp_dot)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Ошибка Graphviz: {e}")
            print(f"Stderr: {e.stderr.decode()}")
            return False
        except Exception as e:
            print(f"Ошибка при создании изображения: {e}")
            return False
    
    def compare_with_cargo(self, crate_name, version):
        """
        Сравнивает результаты с выводом cargo tree
        """
        print(f"\n🔍 Сравнение с cargo tree для {crate_name} {version}")
        print("Примечание: Для точного сравнения требуется установленный Rust и Cargo")
        print("В реальных условиях можно выполнить:")
        print(f"  cargo tree -p {crate_name}:{version}")
        print("\nВозможные расхождения:")
        print("1. cargo tree показывает транзитивные зависимости")
        print("2. cargo tree учитывает feature flags")
        print("3. cargo tree показывает актуальные версии из Cargo.lock")
        print("4. Наш анализ основан на данных crates.io API")

def demonstrate_visualizations():
    """
    Демонстрация визуализаций для трех различных пакетов
    """
    visualizer = DependencyVisualizer()
    
    # Примеры DOT графов для демонстрации
    examples = {
        "serde": {
            "dependencies": [
                {"name": "serde_derive", "version": "1.0", "kind": "normal", "optional": False},
                {"name": "proc-macro2", "version": "1.0", "kind": "dev", "optional": False}
            ]
        },
        "tokio": {
            "dependencies": [
                {"name": "tokio-macros", "version": "1.0", "kind": "normal", "optional": False},
                {"name": "libc", "version": "0.2", "kind": "normal", "optional": True},
                {"name": "futures", "version": "0.3", "kind": "normal", "optional": False}
            ]
        },
        "reqwest": {
            "dependencies": [
                {"name": "hyper", "version": "0.14", "kind": "normal", "optional": False},
                {"name": "tokio", "version": "1.0", "kind": "normal", "optional": False},
                {"name": "serde_json", "version": "1.0", "kind": "normal", "optional": True},
                {"name": "log", "version": "0.4", "kind": "dev", "optional": False}
            ]
        }
    }
    
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ВИЗУАЛИЗАЦИЙ ДЛЯ ТРЕХ ПАКЕТОВ")
    print("=" * 60)
    
    for crate_name, data in examples.items():
        print(f"\n📊 Визуализация для пакета: {crate_name}")
        
        dot_source = visualizer.generate_dot_graph(
            crate_name, 
            "1.0.0", 
            data["dependencies"]
        )
        
        # Выводим DOT представление
        print("\nDOT представление графа:")
        print("```dot")
        print(dot_source)
        print("```")
        
        # Генерируем изображение
        image_filename = f"examples/{crate_name}_graph.png"
        success = visualizer.generate_image(dot_source, image_filename)
        
        if success:
            print(f"✅ Изображение сохранено: {image_filename}")
        else:
            print("❌ Ошибка при создании изображения")
        
        # Сравнение с cargo
        visualizer.compare_with_cargo(crate_name, "1.0.0")

if __name__ == "__main__":
    demonstrate_visualizations()