def validate_llm_response(response: object):
    #valida a estrutura de uma resposta recebida do modelo

    if not isinstance(response, dict):
        raise ValueError("A resposta deve ser um dicionário.")

    response_type = response.get("type")    

    if response_type == "text":
        if not isinstance(response.get("content"), str):
            raise ValueError("O conteúdo da resposta deve ser uma string.")

        return
    
    if response_type == "tool_call":
        tool_name = response.get("tool_name")
        arguments = response.get("arguments")

        if not isinstance(tool_name, str) or not tool_name.strip():
            raise ValueError("O nome da ferramenta é inválido.")

        if not isinstance(arguments, dict):
            raise ValueError("Os argumentos devem ser um dicionário.")

        return

    raise ValueError("Tipo de resposta inválido.")