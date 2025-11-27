# Конфигурационные языки:
# - D2, Mermaid, PlantUML, DOT (языки описания графов)
# - YAML, TOML, JSON, CSV, XML (языки общего назначения)
# - CSS, HTML (языки описания веб-страниц)
# - Lark
# - DSL (Domain Specific Language, предметно-ориентированные языки)

import lark

grammar = r"""
start: value+

NUM: /\d+\.\d*/
NAME: /[_a-zA-Z]+/
STR: /"[^"]+"/

assigh: "def" NAME "=" value
array: "({" value (", "value)* "})"
ref: "#["NAME"]"

value: NUM | array | STR | assigh | ref
%ignore /\s/
%ignore /\*[^\n]+/  
"""

class T(lark.Transformer):
    NAME = str
    NUM = str
    STR = str

    def assigh(self, items):
        name, value = items
        return {"type": "assignment", "name": name, "value": value}
    
    def array(self, items):
        return {"type": "array", "values": items}
    
    def value(self, items):
        return items[0]
    
    def ref(self, items):
        name = items[0]
        return {"type": "reference", "name": name}
    
    def start(self, items):
        return {"type": "root", "children": items}

def to_xml(data, indent=0):
    """Рекурсивно преобразует данные в XML"""
    spaces = "  " * indent
    
    if isinstance(data, dict):
        xml_type = data.get("type", "unknown")
        
        if xml_type == "root":
            children_xml = "\n".join(to_xml(child, indent + 1) for child in data["children"])
            return f'{spaces}<root>\n{children_xml}\n{spaces}</root>'
        
        elif xml_type == "assignment":
            value_xml = to_xml(data["value"], indent + 2)
            return f'{spaces}<assignment name="{data["name"]}">\n{value_xml}\n{spaces}</assignment>'
        
        elif xml_type == "array":
            values_xml = "\n".join(to_xml(val, indent + 2) for val in data["values"])
            return f'{spaces}<array>\n{values_xml}\n{spaces}</array>'
        
        elif xml_type == "reference":
            return f'{spaces}<reference name="{data["name"]}" />'
    
    elif isinstance(data, str):
        # Проверяем, является ли строка числом или строковым литералом
        if data.replace('.', '').isdigit():
            return f'{spaces}<number value="{data}" />'
        elif data.startswith('"') and data.endswith('"'):
            return f'{spaces}<string value="{data[1:-1]}" />'
        else:
            return f'{spaces}<value>{data}</value>'
    
    return f'{spaces}<unknown>{data}</unknown>'

def transform(input: str) -> str:
    parser = lark.Lark(grammar)
    treee = parser.parse(input)
    result = T(visit_tokens=True).transform(treee)
    xml_output = to_xml(result)
    return xml_output

INPUT = '''
* Это однострочный комментарий
def name = 1.0

({7.0, ({3.1, #[name] }), 7.1, "Hello world"})
'''

print(transform(INPUT))