import yaml
import os
import subprocess

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../../config/services.yaml')

def clone_repository():

    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE}")

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    for service in config.get('services', []):
        path_to = os.path.join(os.path.dirname(__file__), '../../services/', service['name'])
        if os.path.exists(path_to):
            print(f"Service {service['name']} already cloned.")
            continue
        
        print(f"Cloning {service['name']} from {service['url']} to {path_to}")
        subprocess.run(["git", "clone", service['url'], path_to], check=True)
