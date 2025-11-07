import requests
import json
import sys

def get_crate_info(crate_name, version=None):
    """
    Получает информацию о пакете из crates.io API
    """
    try:
        if version:
            url = f"https://crates.io/api/v1/crates/{crate_name}/{version}"
        else:
            url = f"https://crates.io/api/v1/crates/{crate_name}"
        
        response = requests.get(url)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении данных: {e}")
        return None

def get_direct_dependencies(crate_name, version):
    """
    Извлекает прямые зависимости для указанной версии пакета
    """
    crate_info = get_crate_info(crate_name, version)
    
    if not crate_info:
        return None
    
    # Получаем информацию о зависимостях
    dependencies_url = f"https://crates.io/api/v1/crates/{crate_name}/{version}/dependencies"
    
    try:
        response = requests.get(dependencies_url)
        response.raise_for_status()
        dependencies_data = response.json()
        
        direct_dependencies = []
        
        for dep in dependencies_data.get('dependencies', []):
            dep_info = {
                'name': dep['crate_id'],
                'version': dep['req'],
                'kind': dep.get('kind', 'normal'),
                'optional': dep.get('optional', False),
                'platform': dep.get('target')
            }
            direct_dependencies.append(dep_info)
        
        return direct_dependencies
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении зависимостей: {e}")
        return None

def main():
    """
    Основная функция - получает и выводит зависимости для заданных пакетов
    """
    # Задаем пакеты и версии для анализа (пользователь не вводит данные)
    packages_to_analyze = [
        {"name": "serde", "version": "1.0.200"},
        {"name": "tokio", "version": "1.0.0"},
        {"name": "reqwest", "version": "0.11.0"}
    ]
    
    print("АНАЛИЗ ПРЯМЫХ ЗАВИСИМОСТЕЙ RUST(Cargo) ПАКЕТОВ")
    
    for package in packages_to_analyze:
        crate_name = package["name"]
        version = package["version"]
        
        print(f"\nПакет: {crate_name} версия {version}")
        print("-" * 40)
        
        dependencies = get_direct_dependencies(crate_name, version)
        
        if dependencies:
            if dependencies:
                print(f"Найдено {len(dependencies)} прямых зависимостей:")
                print()
                
                for i, dep in enumerate(dependencies, 1):
                    kind = "dev" if dep['kind'] == 'dev' else "normal"
                    optional = " (optional)" if dep['optional'] else ""
                    platform = f" [platform: {dep['platform']}]" if dep['platform'] else ""
                    
                    print(f"{i}. {dep['name']} {dep['version']} ({kind}){optional}{platform}")
            else:
                print("Прямые зависимости не найдены")
        else:
            print("Не удалось получить информацию о зависимостях")
        
        print()

if __name__ == "__main__":
    main()