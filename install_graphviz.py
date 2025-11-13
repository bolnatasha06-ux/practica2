#!/usr/bin/env python3
"""
Утилита для помощи в установке Graphviz
"""

import platform
import subprocess
import sys

def install_graphviz():
    """Помогает установить Graphviz"""
    system = platform.system().lower()
    
    print("Установка Graphviz...")
    
    if system == "windows":
        print("Для Windows:")
        print("1. Скачайте установщик с https://graphviz.org/download/")
        print("2. Установите Graphviz")
        print("3. Добавьте путь к bin в PATH (обычно C:\\Program Files\\Graphviz\\bin)")
        
    elif system == "darwin":  # macOS
        try:
            subprocess.run(['brew', '--version'], capture_output=True, check=True)
            print("Устанавливаем через Homebrew...")
            subprocess.run(['brew', 'install', 'graphviz'], check=True)
        except:
            print("Установите через Homebrew: brew install graphviz")
            print("Или скачайте с https://graphviz.org/download/")
            
    elif system == "linux":
        print("Устанавливаем через пакетный менеджер...")
        try:
            # Попробуем apt (Ubuntu/Debian)
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'graphviz'], check=True)
        except:
            try:
                # Попробуем yum (CentOS/RHEL)
                subprocess.run(['sudo', 'yum', 'install', '-y', 'graphviz'], check=True)
            except:
                print("Установите graphviz через ваш пакетный менеджер")
                print("Ubuntu/Debian: sudo apt install graphviz")
                print("CentOS/RHEL: sudo yum install graphviz")

if __name__ == "__main__":
    install_graphviz()