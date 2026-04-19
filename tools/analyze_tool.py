from skills.analyze import analyze_skill

def analyze_tool(question: str,rag,client,longterm_mem,dynamic_mem):
    result = analyze_skill(
        user_input=question,
        client=client,
        rag=rag,
        longterm_mem=longterm_mem,
        dynamic_mem=dynamic_mem
    )
    return {"result": result}