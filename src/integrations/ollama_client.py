from qwen_agent.agents.assistant import Assistant
import os
import yaml

ollama_cfg_path = os.path.join(os.path.dirname(__file__), "../../config/ollama.yaml")

def send_messages(messages: list, system_instruction: str = None, tools: list = None):
    # Чтение конфигурации
    if not os.path.exists(ollama_cfg_path):
        raise FileNotFoundError(f"Configuration file not found: {ollama_cfg_path}")
    
    with open(ollama_cfg_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    llm_cfg = config["llm"]

    # Инициализация LLM
    llm = {
         "model": llm_cfg["model"],
         "model_server": llm_cfg["model_server"],
         "api_key": llm_cfg["api_key"],
         "stream": llm_cfg["stream"],
         "generate_cfg": {
            "top_p": 0.8,
            "temperature": 0.0,
            "max_tokens": 4096,
            "stop": ["```中文", "中文回答"],  # Стоп-токены для китайского
        }
    }

    # Инициализация агента
    agent = Assistant(
        llm=llm,
        system_message=system_instruction,
        function_list=tools,
        )
    
    # Отправка сообщений
    response = []
    for responces in agent.run(messages):
        response = responces

    # Вывод ответа
    for response_view in response:
        print(f"Модель ответила: {response_view['content']}")

    # Возвращение ответа
    return response