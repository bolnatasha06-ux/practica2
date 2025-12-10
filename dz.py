# Конфигурационные языки:
# - D2, Mermaid, PlantUML, DOT (языки описания графов)
# - YAML, TOML, JSON, CSV, XML (языки общего назначения)
# - CSS, HTML (языки описания веб-страниц)
# - Lark
# - DSL (Domain Specific Language, предметно-ориентированные языки)


import lark
from typing import Dict, Any

grammar = r"""
start: (assigh | comment)* value+

NUM: /\d+(\.\d+)?/
NAME: /[_a-zA-Z][_a-zA-Z0-9]*/
STR: /"[^"]*"/

comment: /\*[^\n]+/
assigh: "def" NAME "=" (NUM | STR)
ref: "#[" NAME "]"
array: "({" value ("," value)* "})"
value: NUM | STR | array | ref

%ignore /\s/
"""

class ConstantTransformer(lark.Transformer):
    """Трансформер, который сразу вычисляет константы и подставляет их значения"""
    
    def __init__(self):
        super().__init__(visit_tokens=True)
        self.constants: Dict[str, Any] = {}
    
    def assigh(self, items):
        name, value = items
        self.constants[name] = value
        return None  # Удаляем объявление из результата
    
    def ref(self, items):
        name = items[0]
        if name not in self.constants:
            raise ValueError(f"Неизвестная константа: {name}")
        return self.constants[name]
    
    def NUM(self, token):
        return float(token.value)
    
    def STR(self, token):
        return token.value[1:-1]  # Убираем кавычки
    
    def NAME(self, token):
        return str(token.value)
    
    def array(self, items):
        # Пропускаем открывающую скобку
        return {"type": "array", "values": items[1:]}
    
    def value(self, items):
        return items[0]
    
    def start(self, items):
        # Фильтруем None (объявления констант и комментарии)
        filtered = [item for item in items if item is not None]
        return {"type": "root", "children": filtered}
    
    def comment(self, items):
        return None

def to_xml(data, indent=0):
    """Рекурсивно преобразует данные в XML"""
    spaces = "  " * indent
    
    if isinstance(data, dict):
        if data["type"] == "root":
            children = "\n".join(to_xml(child, indent + 1) for child in data["children"])
            return f'{spaces}<root>\n{children}\n{spaces}</root>'
        elif data["type"] == "array":
            values = "\n".join(to_xml(val, indent + 2) for val in data["values"])
            return f'{spaces}<array>\n{values}\n{spaces}</array>'
    
    elif isinstance(data, (int, float)):
        return f'{spaces}<number value="{data}" />'
    
    elif isinstance(data, str):
        return f'{spaces}<string value="{data}" />'
    
    return f'{spaces}<unknown />'

def transform(input_str: str) -> str:
    """Основная функция трансформации"""
    parser = lark.Lark(grammar)
    tree = parser.parse(input_str)
    result = ConstantTransformer().transform(tree)
    return to_xml(result)

# Тестовые примеры
INPUT1 = '''
* Это однострочный комментарий
def name = 1.0
({7.0, ({3.1, #[name] }), 7.1, "Hello world"})
'''

INPUT2 = '''
def pi = 3.14159
def greeting = "Hello"
({#[pi], #[greeting], "World"})
'''

print("=== Тест 1 ===")
print(transform(INPUT1))
print("\n=== Тест 2 ===")
print(transform(INPUT2))