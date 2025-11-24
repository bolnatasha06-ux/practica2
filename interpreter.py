from typing import Tuple, List

class VMInterpreter:
    """
    Интерпретатор для учебной виртуальной машины
    """
    
    def __init__(self, memory_size=1024):
        self.memory = [0] * memory_size
        self.stack = []
        self.pc = 0  # Program counter
        self.halted = False
        
    def load_program(self, program_bytes: bytes):
        """
        Загрузка программы в память
        """
        for i, byte in enumerate(program_bytes):
            if i < len(self.memory):
                self.memory[i] = byte
                
    def read_instruction(self) -> Tuple[int, int]:
        """
        Чтение инструкции из памяти
        Возвращает (A, B)
        """
        if self.pc >= len(self.memory):
            return None, None
            
        first_byte = self.memory[self.pc]
        a_field = (first_byte >> 5) & 0x7  # Биты 0-2
        
        if a_field == 7:  # LOAD_CONST - 5 байт
            if self.pc + 4 >= len(self.memory):
                return None, None
                
            b_field = ((first_byte & 0x1F) << 27) | \
                     (self.memory[self.pc + 1] << 22) | \
                     (self.memory[self.pc + 2] << 17) | \
                     (self.memory[self.pc + 3] << 12) | \
                     (self.memory[self.pc + 4] << 7)
            self.pc += 5
            
        elif a_field == 0:  # READ_MEM - 1 байт
            b_field = 0
            self.pc += 1
            
        elif a_field in [3, 5]:  # BINARY_OP, WRITE_MEM - 3 байта
            if self.pc + 2 >= len(self.memory):
                return None, None
                
            b_field = ((first_byte & 0x1F) << 16) | \
                     (self.memory[self.pc + 1] << 11) | \
                     (self.memory[self.pc + 2] << 6)
            self.pc += 3
            
        else:
            # Неизвестная инструкция
            self.pc += 1
            return None, None
            
        return a_field, b_field
        
    def execute_instruction(self, a: int, b: int):
        """
        Выполнение одной инструкции
        """
        if a == 7:  # LOAD_CONST
            self.stack.append(b)
            
        elif a == 0:  # READ_MEM
            if self.stack:
                addr = self.stack.pop()
                if 0 <= addr < len(self.memory):
                    self.stack.append(self.memory[addr])
                else:
                    self.stack.append(0)  # Обработка ошибки
                    
        elif a == 5:  # WRITE_MEM
            if self.stack:
                value = self.stack.pop()
                if 0 <= b < len(self.memory):
                    self.memory[b] = value & 0xFF
                    
        elif a == 3:  # BINARY_OP
            # Простая реализация - сложение
            if len(self.stack) >= 2:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                result = op1 + op2
                self.stack.append(result)
                
    def run(self, max_steps=1000):
        """
        Запуск интерпретатора
        """
        steps = 0
        while not self.halted and steps < max_steps:
            a, b = self.read_instruction()
            if a is None:
                break
            self.execute_instruction(a, b)
            steps += 1
            
    def get_state(self):
        """
        Получение состояния виртуальной машины
        """
        return {
            'memory': self.memory[:100],  # Первые 100 ячеек
            'stack': self.stack,
            'pc': self.pc
        }