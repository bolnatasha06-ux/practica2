import argparse
import sys
from assembler import VMAssembler
from interpreter import VMInterpreter

def main():
    parser = argparse.ArgumentParser(description='Ассемблер и интерпретатор УВМ')
    subparsers = parser.add_subparsers(dest='command', help='Команда')
    
    # Парсер для ассемблирования
    asm_parser = subparsers.add_parser('assemble', help='Ассемблирование программы')
    asm_parser.add_argument('source', help='Путь к исходному файлу')
    asm_parser.add_argument('output', help='Путь к выходному бинарному файлу')  
    asm_parser.add_argument('--test', action='store_true', help='Режим тестирования')
    
    # Парсер для интерпретации
    run_parser = subparsers.add_parser('run', help='Запуск программы')
    run_parser.add_argument('program', help='Путь к бинарному файлу программы')
    
    args = parser.parse_args()
    
    if args.command == 'assemble':
        assembler = VMAssembler()
        assembler.assemble(args.source, args.output, args.test)
        print(f"Программа успешно ассемблирована в {args.output}")
        
    elif args.command == 'run':
        with open(args.program, 'rb') as f:
            program_bytes = f.read()
            
        vm = VMInterpreter()
        vm.load_program(program_bytes)
        vm.run()
        
        state = vm.get_state()
        print("Состояние ВМ после выполнения:")
        print(f"Стек: {state['stack']}")
        print(f"Счетчик команд: {state['pc']}")
        print(f"Память (первые 20 ячеек): {state['memory'][:20]}")
        
    else:
        parser.print_help()

if __name__ == '__main__':
    main()