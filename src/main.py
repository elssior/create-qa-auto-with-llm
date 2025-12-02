from core.service_discovery import get_services
from integrations.swagger_parser import parse_swagger
def main():
    services = get_services()

    for service in services:
        endpoints = parse_swagger(service["swagger_path"])
        
        for endpoint in endpoints:
            print(f"{endpoint.method} {endpoint.path} - {endpoint.summary}")

if __name__ == "__main__":
    main()