from ai_assistant.tools.executor import execute_tool
from ai_assistant.services.response_validator import validate_llm_response

def process_tool_call(tool_call: dict):
    #recebe uma solicitação da ferramenta e coordena sua execução

    if not isinstance(tool_call, dict):
        raise ValueError("A solicitação deve ser um dicionário!")

    tool_name = tool_call.get("tool_name")
    arguments = tool_call.get("arguments")

    if not isinstance(tool_name, str) or not tool_name.strip():
        raise ValueError("O nome da ferramenta é obrigatório.")

    if arguments is None:
        raise ValueError("Os argumentos são obrigatórios.")

    return execute_tool(tool_name, arguments)

def process_llm_response(response: dict):
    #valida e direciona a resposta recebida do modelo

    validate_llm_response(response)

    if response["type"] == "text":
        return response

    return process_tool_call({
        "tool_name": response["tool_name"],
        "arguments": response["arguments"],
    })