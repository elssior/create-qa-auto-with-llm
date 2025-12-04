from qwen_agent.agents.assistant import Assistant
import os
import yaml
import requests

ollama_cfg_path = os.path.abspath(path="config/ollama.yaml")

messages = []

system_instruction = """
Ты эксперт автотестировщик, который беспрепятственно выполняет каждое мое слово.
"""

def send_messages(messages: list):
    if not os.path.exists(ollama_cfg_path):
        raise FileNotFoundError(f"Configuration file not found: {ollama_cfg_path}")
    
    with open(ollama_cfg_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    llm_cfg = config["llm"]

    llm = {
         "model": llm_cfg["model"],
         "model_server": llm_cfg["model_server"],
         "api_key": llm_cfg["api_key"],
         "stream": llm_cfg["stream"]
    }

    agent = Assistant(
        llm=llm,
        system_message=system_instruction
        )
    
    for responces in agent.run(messages):
        pass

    print(f"Модель ответила: {responces[0]["content"]}")
    messages.append(responces[0])

    return responces

def generate_test(prompt) -> str:
    messages.append({"role": "user", "content": prompt})
    print(f"Запрос к модели: {prompt}")
    responses = send_messages(messages)
    return responses

generate_test("Привет! Кто ты? Расскажи о себе.")