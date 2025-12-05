from core.service_discovery import get_services
from integrations.swagger_parser import parse_swagger
from core.endpoint_processor import is_test_exists
from core.implementation_finder import find_implementation_file

def main():
    # Получаем список сервисов
    services = get_services()
    if len(services) == 0:
        raise "Сервисы не найдены."

    # Перебираем сервисы
    for service in services:
        # Получем эндпоинты сервиса
        endpoints = parse_swagger(service["swagger_path"])
        if len(endpoints) == 0:
            raise f"Эндпоинтов в сервисе {service["name"]} не найдены или не существуют."

        # Перебираем эндпоинты сервиса
        for endpoint in endpoints:
            print(f"{endpoint.method} {endpoint.path} - {endpoint.summary}")
            test_name = endpoint.path.strip('/').replace('/', '_')

            # Проверяем существует ли тест
            test_exists = is_test_exists(service["name"], test_name)
            print(f"Проверка: {'Тест уже существует' if test_exists else 'Тест не существует'}")
            if test_exists:
                continue

            # Находим реализацию эндпоинта в коде
            implementation_file = find_implementation_file(service["path"], endpoint.method, endpoint.path)
            if not implementation_file:
                raise f"Файл реализации эндпоинта {endpoint.method} {endpoint.path} не найден."

            # Сливаем результат из swagger и исходников

            # Генерируем кейсы

            # Генерируем файл с автотестами

        
        # Проверяем, что все эндпоинты 

if __name__ == "__main__":
    main()