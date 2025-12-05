import os
from integrations.ollama_client import send_messages

def get_file_structure(root_dir: str) -> str:
    # Собираем дерево файлов
    file_list = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "build", "_build", "deps", "venv"]]

        for file in files:
            if file.startswith('.'): continue
            # Получаем относительный путь
            rel_path = os.path.relpath(os.path.join(root, file), root_dir)
            file_list.append(rel_path)

    return "\n".join(file_list)

def analyze_file_content(service_path: str, file_path: str, method: str, api_path: str) -> str:
    full_path = os.path.join(service_path, file_path)
    full_path = os.path.normpath(full_path)
    
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        return None
        
    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {full_path}: {e}")
        return None

    # Ограничиваем размер контекста
    if len(content.splitlines()) > 2000:
        content = "\n".join(content.splitlines()[:2000])
        content += "\n... (truncated) ..."

    system_prompt = """
    Ты — анализатор кода API. Твоя задача: извлечь метаданные эндпоинта и развернуть все ссылки.

    КРИТИЧНО: Финальная схема НЕ ДОЛЖНА содержать:
    - "$ref" 
    - "ref_type"
    - Ссылки на переменные/типы
    - Неразрешённые зависимости

    Все ссылки должны быть рекурсивно развёрнуты в инлайн-структуры.

    ФОРМАТ ВЫВОДА: Без пояснений, без разметки, без комментариев до или после.
    """

    user_prompt = f"""
    ФАЙЛ: {file_path}
    ЭНДПОИНТ: `{method.upper()} {api_path}`
    ```
    {content}
    ```

    ЗАДАЧИ:
    1. Определи язык/фреймворк
    2. Найди эндпоинт
    3. Извлеки метаданные (path, method, summary, parameters, request_body, responses, tags, operation_id)
    4. **Разверни ВСЕ ссылки рекурсивно**:
    - Ищи определения типов в файле
    - Подставляй их содержимое вместо ссылок
    - Повторяй до полного разрешения

    ФОРМАТ ОТВЕТА:

    Если эндпоинт найден — строго валидный JSON:
    {{
    "path": string,
    "method": string,
    "summary": string,
    "description": string | null,
    "parameters": array,
    "request_body": object | null,
    "responses": object,
    "tags": array,
    "operation_id": string | null
    }}

    Если НЕ НАЙДЕНО: верни только строку "NOT_FOUND" (без JSON).

    ВАЖНО: 
    - В `responses`, `request_body`, `parameters` не должно остаться ссылок
    - Все схемы должны быть развёрнуты в объекты с `type`, `properties`, `items` и т.д.
    - Если информации нет — используй `null` или `[]`, но не выдумывай данные
    """

    response = send_messages(
        messages=[{"role": "user", "content": user_prompt}],
        system_instruction=system_prompt
    )
    
    if not response:
        return None
        
    result = response[-1]["content"].strip()
    
    if "NOT_FOUND" in result:
        return None
        
    # Очищаем от markdown (```json ... ```)
    if result.startswith("```"):
        lines = result.splitlines()
        if len(lines) >= 3:
            result = "\n".join(lines[1:-1])
            
    return result

def find_implementation_file(service_path: str, method: str, path: str, max_attempts: int = 3) -> tuple[str, str]:
    structure = get_file_structure(service_path)
    checked_files = [] # Список проверенных файлов (blacklist)
    
    system_prompt = "Ты опытный разработчик. Твоя цель — найти файл с исходным кодом."

    for attempt in range(1, max_attempts + 1):
        print(f"Попытка поиска #{attempt}...")
        
        # Формируем список исключений, если были неудачные попытки
        exclusions = ""
        if checked_files:
            exclusions = f"\nВАЖНО: Я уже проверял файлы {checked_files}, в них РЕАЛИЗАЦИИ НЕТ. Не предлагай их снова!"

        user_prompt = f"""
        Вот структура файлов проекта:
        {structure}
        
        Мне нужно найти файл, в котором реализован API эндпоинт:
        {method.upper()} {path}
        
        Проанализируй названия файлов и структуру.
        Верни ТОЛЬКО путь к наиболее вероятному файлу (например: src/api/handlers.ml).
        Никаких объяснений, только путь.
        {exclusions}
        """

        # 1. Спрашиваем LLM о кандидате
        response = send_messages(
            messages=[{"role": "user", "content": user_prompt}],
            system_instruction=system_prompt
        )
        
        if not response:
            return None, None
            
        candidate_file = response[-1]["content"].strip()
        # Очистка возможных кавычек
        candidate_file = candidate_file.replace("'", "").replace('"', "").replace("`", "")

        print(f"Кандидат от LLM: {candidate_file}")

        # Если LLM начинает ходить по кругу и предлагает то же самое
        if candidate_file in checked_files:
            print("LLM предлагает тот же файл, прерываем поиск.")
            break

        # 2. Проверяем кандидата через analyze_file_content
        code_snippet = analyze_file_content(service_path, candidate_file, method, path)
        
        if code_snippet:
            return candidate_file, code_snippet
        
        # Если не нашли - добавляем в черный список и продолжаем
        print(f"В файле {candidate_file} реализация не найдена. Ищем дальше...")
        checked_files.append(candidate_file)

    print("Превышено количество попыток. Реализация не найдена.")
    return None, None