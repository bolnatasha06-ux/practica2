import argparse
import sys
import os
import json  # Добавлен импорт json
from assembler import VMAssembler
from interpreter import VMInterpreter

def main():
    parser = argparse.ArgumentParser(description='Ассемблер и интерпретатор УВМ')
    subparsers = parser.add_subparsers(dest='command', help='Команда')
    
    # Парсер для ассемблирования в бинарный формат
    asm_bin_parser = subparsers.add_parser('assemble-bin', help='Ассемблирование в бинарный формат')
    asm_bin_parser.add_argument('source', help='Путь к исходному файлу JSON')
    asm_bin_parser.add_argument('output', help='Путь к выходному бинарному файлу')  
    asm_bin_parser.add_argument('--test', action='store_true', help='Режим тестирования')
    
    # Парсер для ассемблирования в промежуточное представление
    asm_int_parser = subparsers.add_parser('assemble-int', help='Ассемблирование в промежуточное представление')
    asm_int_parser.add_argument('source', help='Путь к исходному файлу JSON')
    asm_int_parser.add_argument('output', help='Путь к выходному файлу промежуточного представления')
    
    # Парсер для запуска из бинарного формата
    run_bin_parser = subparsers.add_parser('run-bin', help='Запуск программы из бинарного формата')
    run_bin_parser.add_argument('program', help='Путь к бинарному файлу программы')
    run_bin_parser.add_argument('--dump', help='Путь для сохранения дампа памяти')
    run_bin_parser.add_argument('--start-addr', type=int, default=0, help='Начальный адрес для дампа')
    run_bin_parser.add_argument('--end-addr', type=int, help='Конечный адрес для дампа')
    
    # Парсер для запуска из промежуточного представления
    run_int_parser = subparsers.add_parser('run', help='Запуск программы из промежуточного представления')
    run_int_parser.add_argument('program', help='Путь к файлу промежуточного представления')
    run_int_parser.add_argument('--dump', required=True, help='Путь для сохранения дампа памяти')
    run_int_parser.add_argument('--start-addr', type=int, default=0, help='Начальный адрес для дампа')
    run_int_parser.add_argument('--end-addr', type=int, help='Конечный адрес для дампа')
    
    # Парсер для теста копирования массива
    test_parser = subparsers.add_parser('test-array-copy', help='Тест копирования массива')
    test_parser.add_argument('--dump', required=True, help='Путь для сохранения дампа памяти')
    
    args = parser.parse_args()
    
    if args.command == 'assemble-bin':
        assembler = VMAssembler()
        assembler.assemble_to_binary(args.source, args.output, args.test)
        print(f"Программа успешно ассемблирована в бинарный формат: {args.output}")
        
    elif args.command == 'assemble-int':
        assembler = VMAssembler()
        assembler.assemble_to_intermediate(args.source, args.output)
        print(f"Программа успешно ассемблирована в промежуточное представление: {args.output}")
        
    elif args.command == 'run-bin':
        with open(args.program, 'rb') as f:
            program_bytes = f.read()
            
        vm = VMInterpreter()
        vm.load_program_from_binary(program_bytes)
        vm.run_from_binary()
        
        if args.dump:
            vm.save_memory_dump(args.dump, args.start_addr, args.end_addr)
        
        state = vm.get_state()
        print("\nСостояние ВМ после выполнения:")
        print(f"Стек: {state['stack']}")
        print(f"Счетчик команд: {state['pc']}")
        print(f"Выполнено инструкций: {state['instructions_executed']}")
        print(f"Память данных (первые 20 ячеек): {state['data_memory'][:20]}")
        
    elif args.command == 'run':
        vm = VMInterpreter()
        vm.load_program_from_intermediate(args.program)
        vm.run_from_intermediate()
        
        if args.dump:
            vm.save_memory_dump(args.dump, args.start_addr, args.end_addr)
        
        state = vm.get_state()
        print("\nСостояние ВМ после выполнения:")
        print(f"Стек: {state['stack']}")
        print(f"Счетчик команд: {state['pc']}")
        print(f"Выполнено инструкций: {state['instructions_executed']}")
        print(f"Память данных (первые 20 ячеек): {state['data_memory'][:20]}")
        
    elif args.command == 'test-array-copy':
        # Тестовая программа: копирование массива
        run_array_copy_test(args.dump)
        
    else:
        parser.print_help()

def run_array_copy_test(dump_file: str):
    """
    Тестовая программа для копирования массива
    """
    print("=== ТЕСТ КОПИРОВАНИЯ МАССИВА ===")
    
    # Создаем тестовую программу
    test_program = {
        "instructions": [
            # Инициализация: загружаем исходный массив в память
            {"op": "LOAD_CONST", "value": 10},   # Значение для ячейки 100
            {"op": "WRITE_MEM", "address": 100},
            {"op": "LOAD_CONST", "value": 20},   # Значение для ячейки 101  
            {"op": "WRITE_MEM", "address": 101},
            {"op": "LOAD_CONST", "value": 30},   # Значение для ячейки 102
            {"op": "WRITE_MEM", "address": 102},
            {"op": "LOAD_CONST", "value": 40},   # Значение для ячейки 103
            {"op": "WRITE_MEM", "address": 103},
            
            # Копирование массива из адресов 100-103 в 200-203
            {"op": "LOAD_CONST", "value": 100},  # Начальный адрес источника
            {"op": "READ_MEM"},                  # Читаем значение
            {"op": "WRITE_MEM", "address": 200}, # Записываем в целевой адрес
            
            {"op": "LOAD_CONST", "value": 101},
            {"op": "READ_MEM"},
            {"op": "WRITE_MEM", "address": 201},
            
            {"op": "LOAD_CONST", "value": 102}, 
            {"op": "READ_MEM"},
            {"op": "WRITE_MEM", "address": 202},
            
            {"op": "LOAD_CONST", "value": 103},
            {"op": "READ_MEM"}, 
            {"op": "WRITE_MEM", "address": 203},
            
            # Проверяем результат - читаем из целевого массива
            {"op": "LOAD_CONST", "value": 200},
            {"op": "READ_MEM"},
            {"op": "LOAD_CONST", "value": 201},
            {"op": "READ_MEM"},
            {"op": "LOAD_CONST", "value": 202},
            {"op": "READ_MEM"},
            {"op": "LOAD_CONST", "value": 203},
            {"op": "READ_MEM"}
        ]
    }
    
    # Сохраняем тестовую программу
    with open('test_array_copy.json', 'w', encoding='utf-8') as f:
        json.dump(test_program, f, indent=2, ensure_ascii=False)
    
    # Ассемблируем и запускаем
    assembler = VMAssembler()
    intermediate_repr = assembler.assemble_to_intermediate('test_array_copy.json', 'test_array_copy_intermediate.json')
    
    vm = VMInterpreter()
    vm.load_program_from_intermediate('test_array_copy_intermediate.json')
    vm.run_from_intermediate()
    
    # Сохраняем дамп памяти
    vm.save_memory_dump(dump_file, 90, 210)
    
    # Проверяем результат
    state = vm.get_state()
    print("\nРезультат теста копирования массива:")
    print(f"Исходный массив (адреса 100-103): {state['data_memory'][100:104]}")
    print(f"Скопированный массив (адреса 200-203): {state['data_memory'][200:204]}")
    print(f"Стек (прочитанные значения): {state['stack']}")
    
    # Очистка временных файлов
    if os.path.exists('test_array_copy.json'):
        os.remove('test_array_copy.json')
    if os.path.exists('test_array_copy_intermediate.json'):
        os.remove('test_array_copy_intermediate.json')

if __name__ == '__main__':
    main()