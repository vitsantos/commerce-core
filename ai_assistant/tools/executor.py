from ai_assistant.tools.registry import TOOL_REGISTRY

def execute_tool(tool_name: str, arguments: dict):
    if not isinstance(arguments, dict):
        raise ValueError("Os argumentos devem ser um dicionário.")
    
    tool = TOOL_REGISTRY.get(tool_name)

    if tool is None:
        raise ValueError(f"Ferramenta não resgistrada: {tool_name}")

    if tool_name == "search_products":
        query = arguments.get("query")

        if not isinstance(query, str) or not query.strip():
            raise ValueError("O argumento 'query' é obrigatório.")

    return tool(**arguments)