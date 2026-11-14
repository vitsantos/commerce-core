from ai_assistant.tools.executor import execute_tool

def process_tool_call(tool_call: dict):
    #recebe uma solicitação da ferramenta e coordena sua execução

    if not isinstance(tool_call, dict):
        raise ValueError("A solicitação deve ser um dicionário!")

    tool_name = tool_call.get("tool_name")
    arguments = tool_call.get("arguments")

    if not tool_name:
        raise ValueError("O nome da ferramenta é obrigatório.")

    if arguments is None:
        raise ValueError("Os argumentos são obrigatórios.")

    return execute_tool(tool_name, arguments)