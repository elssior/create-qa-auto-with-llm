import yaml
import os
import subprocess

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../../config/services.yaml')
SERVICES_DIR = os.path.join(os.path.dirname(__file__), '../../services/')

#def clone_repository(url, path_to, service_name):
#    print(f"Cloning {service_name} from {url} to {path_to}")
#    subprocess.run(["git", "clone", url, path_to], check=True)

def get_services():
    
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE}")

    # Чтение YAML файла конфигурации
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    services = config.get('services', [])

    # Добавление абсолютных путей к сервисам
    for service in services:
        service["path"] = os.path.abspath(os.path.join(SERVICES_DIR, service['name']))
        service["swagger_path"] = os.path.abspath(os.path.join(SERVICES_DIR, service['name'], 'swagger.json'))

    ### В планах рeализовать автоматическое клонирование репозиториев и получение swagger
    #
    # for service in config.get('services', []):
    #     path_to = os.path.join(os.path.dirname(__file__), '../../services/', service['name'])
    #     # Клонирование репозитория если его еще нет
    #     if not os.path.exists(path_to):
    #         clone_repository(service['repo_url'], path_to, service['name'])
    ###
    

    return services