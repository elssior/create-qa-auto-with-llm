from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import prance

@dataclass
class Endpoint:
    """Представление одного эндпоинта API."""
    path: str
    method: str
    summary: str
    description: Optional[str]
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Any]
    tags: List[str]
    operation_id: Optional[str]

def parse_swagger(swagger_path: str) -> List[Endpoint]:
    parser = prance.ResolvingParser(swagger_path)
    spec = parser.specification
    
    endpoints = []
    for path, methods in spec.get('paths', {}).items():
        for method, op in methods.items():
            if method.startswith('x-'):  # пропускаем расширения
                continue
            endpoints.append(Endpoint(
                path=path,
                method=method.upper(),
                summary=op.get('summary', ''),
                description=op.get('description', ''),
                parameters=op.get('parameters', []),
                request_body=op.get('requestBody'),
                responses=op.get('responses', {}),
                tags=op.get('tags', []),
                operation_id=op.get('operationId')
            ))
    return endpoints