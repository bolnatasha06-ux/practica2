import json
import struct
import sys
from typing import List, Dict, Any, Tuple

class VMAssembler:
    """
    Ассемблер для учебной виртуальной машины (УВМ)
    """
    
    # Коды операций
    OP_READ_MEM = 0    # Чтение из памяти
    OP_BINARY_OP = 3   # Бинарная операция
    OP_WRITE_MEM = 5   # Запись в память  
    OP_LOAD_CONST = 7  # Загрузка константы
    
    def __init__(self):
        self.labels = {}
        self.program = []
        
    def parse_instruction(self, instr: Dict[str, Any]) -> List[int]:
        """
        Парсинг одной инструкции в байт-код
        """
        op = instr.get("op", "").upper()
        bytes_result = []
        
        if op == "LOAD_CONST":
            # Загрузка константы: 5 байт
            const_value = instr["value"]
            a_byte = (self.OP_LOAD_CONST & 0x7)  # Биты 0-2
            b_value = const_value & 0xFFFFFFFF  # 32 бита
            
            # Формируем 5 байт
            byte1 = (a_byte << 5) | ((b_value >> 27) & 0x1F)
            byte2 = (b_value >> 22) & 0x1F
            byte3 = (b_value >> 17) & 0x1F  
            byte4 = (b_value >> 12) & 0x1F
            byte5 = (b_value >> 7) & 0x1F
            
            bytes_result = [byte1, byte2, byte3, byte4, byte5]
            
        elif op == "READ_MEM":
            # Чтение из памяти: 1 байт
            a_byte = (self.OP_READ_MEM & 0x7) << 5
            bytes_result = [a_byte]
            
        elif op == "WRITE_MEM":
            # Запись в память: 3 байта
            address = instr["address"]
            a_byte = (self.OP_WRITE_MEM & 0x7) << 5
            b_value = address & 0x1FFFFF  # 21 бит
            
            byte1 = a_byte | ((b_value >> 16) & 0x1F)
            byte2 = (b_value >> 11) & 0x1F
            byte3 = (b_value >> 6) & 0x1F
            
            bytes_result = [byte1, byte2, byte3]
            
        elif op == "BINARY_OP":
            # Бинарная операция: 3 байта
            address = instr["address"] 
            a_byte = (self.OP_BINARY_OP & 0x7) << 5
            b_value = address & 0x1FFFFF  # 21 бит
            
            byte1 = a_byte | ((b_value >> 16) & 0x1F)
            byte2 = (b_value >> 11) & 0x1F  
            byte3 = (b_value >> 6) & 0x1F
            
            bytes_result = [byte1, byte2, byte3]
            
        else:
            raise ValueError(f"Неизвестная операция: {op}")
            
        return bytes_result
    
    def assemble_to_binary(self, source_file: str, output_file: str, test_mode: bool = False):
        """
        Ассемблирование в бинарный формат
        """
        with open(source_file, 'r', encoding='utf-8') as f:
            program_data = json.load(f)
        
        instructions = program_data.get("instructions", [])
        binary_output = []
        internal_representation = []
        
        for i, instr in enumerate(instructions):
            bytes_result = self.parse_instruction(instr)
            binary_output.extend(bytes_result)
            
            if test_mode:
                op = instr.get("op", "")
                if op == "LOAD_CONST":
                    internal_representation.append({
                        'instruction': f'LOAD_CONST {instr["value"]}',
                        'bytes': bytes_result,
                        'A': self.OP_LOAD_CONST,
                        'B': instr["value"]
                    })
                elif op == "READ_MEM":
                    internal_representation.append({
                        'instruction': 'READ_MEM',
                        'bytes': bytes_result, 
                        'A': self.OP_READ_MEM,
                        'B': None
                    })
                elif op == "WRITE_MEM":
                    internal_representation.append({
                        'instruction': f'WRITE_MEM {instr["address"]}',
                        'bytes': bytes_result,
                        'A': self.OP_WRITE_MEM, 
                        'B': instr["address"]
                    })
                elif op == "BINARY_OP":
                    internal_representation.append({
                        'instruction': f'BINARY_OP {instr["address"]}',
                        'bytes': bytes_result,
                        'A': self.OP_BINARY_OP,
                        'B': instr["address"]
                    })
        
        with open(output_file, 'wb') as f:
            f.write(bytes(binary_output))
        
        if test_mode:
            print("=== ВНУТРЕННЕЕ ПРЕДСТАВЛЕНИЕ ПРОГРАММЫ ===")
            for ir in internal_representation:
                print(f"Инструкция: {ir['instruction']}")
                print(f"Байты: {[f'0x{b:02X}' for b in ir['bytes']]}")
                print(f"Поле A: {ir['A']}")
                if ir['B'] is not None:
                    print(f"Поле B: {ir['B']}")
                print("---")
            
            print(f"Всего байт: {len(binary_output)}")
            print(f"Бинарный вывод: {[f'0x{b:02X}' for b in binary_output]}")
        
        return binary_output, internal_representation

    def assemble_to_intermediate(self, source_file: str, output_file: str):
        """
        Ассемблирование в промежуточное представление для интерпретатора
        """
        with open(source_file, 'r', encoding='utf-8') as f:
            program_data = json.load(f)
        
        instructions = program_data.get("instructions", [])
        intermediate_repr = []
        
        for i, instr in enumerate(instructions):
            op = instr.get("op", "").upper()
            intermediate_instr = {"op": op}
            
            if op == "LOAD_CONST":
                intermediate_instr["value"] = instr["value"]
            elif op in ["WRITE_MEM", "BINARY_OP"]:
                intermediate_instr["address"] = instr["address"]
            elif op == "READ_MEM":
                pass  # Нет дополнительных параметров
                
            intermediate_repr.append(intermediate_instr)
        
        # Сохраняем промежуточное представление
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "program": intermediate_repr,
                "metadata": {
                    "instruction_count": len(intermediate_repr),
                    "source_file": source_file
                }
            }, f, indent=2, ensure_ascii=False)
        
        return intermediate_repr