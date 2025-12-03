import os

SERVICES_DIR = os.path.join(os.path.dirname(__file__), '../../tests')

def is_test_exists(service_name, endpoint):
    return os.path.exists(f"{SERVICES_DIR}/{service_name}/{endpoint}.py")