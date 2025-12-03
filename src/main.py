from core.service_discovery import get_services
from integrations.swagger_parser import parse_swagger
from core.endpoint_processor import is_test_exists

def main():
    services = get_services()

    for service in services:
        endpoints = parse_swagger(service["swagger_path"])
        
        for endpoint in endpoints:
            print(f"{endpoint.method} {endpoint.path} - {endpoint.summary}")
            test_name = endpoint.path.strip('/').replace('/', '_')
            test_exists = is_test_exists(service["name"], test_name)
            print(f"  Test exists: {'Yes' if test_exists else 'No'}")
            
if __name__ == "__main__":
    main()