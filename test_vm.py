import unittest
import tempfile
import os
import json
from assembler import VMAssembler
from interpreter import VMInterpreter

class TestVMAssembler(unittest.TestCase):
    
    def test_load_const(self):
        """Тест загрузки константы"""
        assembler = VMAssembler()
        
        # Тест из спецификации: A=7, B=607
        program = {
            "instructions": [
                {"op": "LOAD_CONST", "value": 607}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(program, f)
            source_file = f.name
            
        try:
            output_file = "test_output.bin"
            bytes_result, internal_repr = assembler.assemble(source_file, output_file, test_mode=True)
            
            # Проверяем байты
            expected_bytes = [0xF8, 0x12, 0x80, 0x80, 0x80]  # 0xF8 = 0x7 << 5 | (607 >> 27)
            self.assertEqual(bytes_result, expected_bytes)
            
            # Проверяем внутреннее представление
            self.assertEqual(internal_repr[0]['A'], 7)
            self.assertEqual(internal_repr[0]['B'], 607)
            
        finally:
            os.unlink(source_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
                
    def test_read_mem(self):
        """Тест чтения из памяти"""
        assembler = VMAssembler()
        
        program = {
            "instructions": [
                {"op": "READ_MEM"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(program, f)
            source_file = f.name
            
        try:
            output_file = "test_output.bin"
            bytes_result, internal_repr = assembler.assemble(source_file, output_file, test_mode=True)
            
            self.assertEqual(bytes_result, [0x00])  # A=0 << 5
            self.assertEqual(internal_repr[0]['A'], 0)
            
        finally:
            os.unlink(source_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
                
    def test_write_mem(self):
        """Тест записи в память"""
        assembler = VMAssembler()
        
        # Тест из спецификации: A=5, B=777
        program = {
            "instructions": [
                {"op": "WRITE_MEM", "address": 777}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(program, f)
            source_file = f.name
            
        try:
            output_file = "test_output.bin"
            bytes_result, internal_repr = assembler.assemble(source_file, output_file, test_mode=True)
            
            # Проверяем байты
            expected_bytes = [0x40, 0x18, 0x80]  # 0x40 = 0x5 << 5 | (777 >> 16)
            self.assertEqual(bytes_result, expected_bytes)
            
            self.assertEqual(internal_repr[0]['A'], 5)
            self.assertEqual(internal_repr[0]['B'], 777)
            
        finally:
            os.unlink(source_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

class TestVMInterpreter(unittest.TestCase):
    
    def test_load_const_execution(self):
        """Тест выполнения загрузки константы"""
        vm = VMInterpreter()
        
        # Программа: LOAD_CONST 607
        program_bytes = bytes([0xF8, 0x12, 0x80, 0x80, 0x80])
        vm.load_program(program_bytes)
        vm.run()
        
        self.assertEqual(vm.stack, [607])
        
    def test_memory_operations(self):
        """Тест операций с памятью"""
        vm = VMInterpreter()
        
        # Программа: WRITE_MEM 777, затем READ_MEM
        program_bytes = bytes([0x40, 0x18, 0x80])  # WRITE_MEM 777
        vm.load_program(program_bytes)
        vm.stack.append(42)  # Значение для записи
        vm.run()
        
        self.assertEqual(vm.memory[777], 42)

if __name__ == '__main__':
    unittest.main()