import json
import sys
from typing import List, Dict, Any, Tuple, Optional

class VMInterpreter:
    """
    Интерпретатор для учебной виртуальной машины с раздельной памятью
    """
    
    # Коды операций
    OP_READ_MEM = 0
    OP_BINARY_OP = 3  
    OP_WRITE_MEM = 5
    OP_LOAD_CONST = 7
    
    def __init__(self, code_memory_size=4096, data_memory_size=4096):
        # Раздельная память: код и данные
        self.code_memory = [0] * code_memory_size
        self.data_memory = [0] * data_memory_size
        self.stack = []
        self.pc = 0  # Program counter
        self.halted = False
        self.instructions_executed = 0
        
    def load_program_from_binary(self, program_bytes: bytes):
        """
        Загрузка программы из бинарного файла в память команд
        """
        for i, byte in enumerate(program_bytes):
            if i < len(self.code_memory):
                self.code_memory[i] = byte
        print(f"Загружено {len(program_bytes)} байт в память команд")
                
    def load_program_from_intermediate(self, intermediate_file: str):
        """
        Загрузка программы из промежуточного представления
        """
        with open(intermediate_file, 'r', encoding='utf-8') as f:
            program_data = json.load(f)
        
        self.intermediate_program = program_data.get("program", [])
        self.pc = 0
        print(f"Загружена программа из {intermediate_file}: {len(self.intermediate_program)} инструкций")
        
    def read_instruction_from_binary(self) -> Tuple[Optional[int], Optional[int]]:
        """
        Чтение инструкции из бинарной памяти команд
        """
        if self.pc >= len(self.code_memory):
            return None, None
            
        first_byte = self.code_memory[self.pc]
        a_field = (first_byte >> 5) & 0x7
        
        if a_field == 7:  # LOAD_CONST - 5 байт
            if self.pc + 4 >= len(self.code_memory):
                return None, None
                
            b_field = ((first_byte & 0x1F) << 27) | \
                     (self.code_memory[self.pc + 1] << 22) | \
                     (self.code_memory[self.pc + 2] << 17) | \
                     (self.code_memory[self.pc + 3] << 12) | \
                     (self.code_memory[self.pc + 4] << 7)
            self.pc += 5
            
        elif a_field == 0:  # READ_MEM - 1 байт
            b_field = 0
            self.pc += 1
            
        elif a_field in [3, 5]:  # BINARY_OP, WRITE_MEM - 3 байта
            if self.pc + 2 >= len(self.code_memory):
                return None, None
                
            b_field = ((first_byte & 0x1F) << 16) | \
                     (self.code_memory[self.pc + 1] << 11) | \
                     (self.code_memory[self.pc + 2] << 6)
            self.pc += 3
            
        else:
            self.pc += 1
            return None, None
            
        return a_field, b_field
        
    def read_instruction_from_intermediate(self) -> Optional[Dict[str, Any]]:
        """
        Чтение инструкции из промежуточного представления
        """
        if self.pc >= len(self.intermediate_program):
            return None
            
        instruction = self.intermediate_program[self.pc]
        self.pc += 1
        return instruction
        
    def execute_instruction(self, a: int, b: int):
        """
        Выполнение инструкции из бинарного формата
        """
        self.instructions_executed += 1
        
        if a == 7:  # LOAD_CONST
            self.stack.append(b)
            print(f"LOAD_CONST: загружена константа {b} в стек")
            
        elif a == 0:  # READ_MEM
            if self.stack:
                addr = self.stack.pop()
                if 0 <= addr < len(self.data_memory):
                    value = self.data_memory[addr]
                    self.stack.append(value)
                    print(f"READ_MEM: прочитано значение {value} из адреса {addr}")
                else:
                    self.stack.append(0)
                    print(f"READ_MEM: ошибка - адрес {addr} вне диапазона")
            else:
                print("READ_MEM: ошибка - стек пуст")
                    
        elif a == 5:  # WRITE_MEM
            if self.stack:
                value = self.stack.pop()
                if 0 <= b < len(self.data_memory):
                    self.data_memory[b] = value & 0xFF
                    print(f"WRITE_MEM: записано значение {value} по адресу {b}")
                else:
                    print(f"WRITE_MEM: ошибка - адрес {b} вне диапазона")
            else:
                print("WRITE_MEM: ошибка - стек пуст")
                    
        elif a == 3:  # BINARY_OP
            if len(self.stack) >= 2:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                result = op1 + op2  # Простая операция - сложение
                self.stack.append(result)
                print(f"BINARY_OP: {op1} + {op2} = {result}")
            else:
                print("BINARY_OP: ошибка - недостаточно операндов в стеке")
                
    def execute_intermediate_instruction(self, instruction: Dict[str, Any]):
        """
        Выполнение инструкции из промежуточного представления
        """
        self.instructions_executed += 1
        op = instruction.get("op", "").upper()
        
        if op == "LOAD_CONST":
            value = instruction["value"]
            self.stack.append(value)
            print(f"LOAD_CONST: загружена константа {value} в стек")
            
        elif op == "READ_MEM":
            if self.stack:
                addr = self.stack.pop()
                if 0 <= addr < len(self.data_memory):
                    value = self.data_memory[addr]
                    self.stack.append(value)
                    print(f"READ_MEM: прочитано значение {value} из адреса {addr}")
                else:
                    self.stack.append(0)
                    print(f"READ_MEM: ошибка - адрес {addr} вне диапазона")
            else:
                print("READ_MEM: ошибка - стек пуст")
                
        elif op == "WRITE_MEM":
            if self.stack:
                value = self.stack.pop()
                address = instruction["address"]
                if 0 <= address < len(self.data_memory):
                    self.data_memory[address] = value & 0xFF
                    print(f"WRITE_MEM: записано значение {value} по адресу {address}")
                else:
                    print(f"WRITE_MEM: ошибка - адрес {address} вне диапазона")
            else:
                print("WRITE_MEM: ошибка - стек пуст")
                
        elif op == "BINARY_OP":
            if len(self.stack) >= 2:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                result = op1 + op2
                self.stack.append(result)
                print(f"BINARY_OP: {op1} + {op2} = {result}")
            else:
                print("BINARY_OP: ошибка - недостаточно операндов в стеке")
                
    def run_from_binary(self, max_steps=1000):
        """
        Запуск интерпретатора из бинарного формата
        """
        steps = 0
        while not self.halted and steps < max_steps:
            a, b = self.read_instruction_from_binary()
            if a is None:
                break
            self.execute_instruction(a, b)
            steps += 1
            
        print(f"Выполнено {steps} инструкций")
        
    def run_from_intermediate(self, max_steps=1000):
        """
        Запуск интерпретатора из промежуточного представления
        """
        steps = 0
        while not self.halted and steps < max_steps:
            instruction = self.read_instruction_from_intermediate()
            if instruction is None:
                break
            self.execute_intermediate_instruction(instruction)
            steps += 1
            
        print(f"Выполнено {steps} инструкций")
        
    def dump_memory(self, start_addr: int = 0, end_addr: int = None) -> Dict[str, Any]:
        """
        Создание дампа памяти данных в формате JSON
        """
        if end_addr is None:
            end_addr = min(len(self.data_memory), start_addr + 100)
            
        end_addr = min(end_addr, len(self.data_memory))
        
        memory_dump = {}
        for addr in range(start_addr, end_addr):
            memory_dump[str(addr)] = self.data_memory[addr]
            
        return {
            "memory_dump": memory_dump,
            "range": f"{start_addr}-{end_addr-1}",
            "total_memory_size": len(self.data_memory),
            "stack": self.stack,
            "instructions_executed": self.instructions_executed,
            "program_counter": self.pc
        }
        
    def save_memory_dump(self, output_file: str, start_addr: int = 0, end_addr: int = None):
        """
        Сохранение дампа памяти в файл JSON
        """
        dump_data = self.dump_memory(start_addr, end_addr)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dump_data, f, indent=2, ensure_ascii=False)
            
        print(f"Дамп памяти сохранен в {output_file} (адреса {dump_data['range']})")
        
    def initialize_memory_with_array(self, start_addr: int, data: List[int]):
        """
        Инициализация памяти данных массивом
        """
        for i, value in enumerate(data):
            if start_addr + i < len(self.data_memory):
                self.data_memory[start_addr + i] = value & 0xFF
                
        print(f"Память инициализирована массивом из {len(data)} элементов с адреса {start_addr}")
        
    def get_state(self):
        """
        Получение состояния виртуальной машины
        """
        return {
            'data_memory': self.data_memory[:100],
            'stack': self.stack,
            'pc': self.pc,
            'instructions_executed': self.instructions_executed
        }