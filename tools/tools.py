from tools.analyze_tool import analyze_tool
tools = [
        {
            "type": "function",
            "function": {
                "name": "analyze_tool",
                "description": "分析用户询问的知识点，结合RAG查询结果给出资料和总结",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "用户当前的问题"
                        }
                    },
                    "required": ["question"]
                }
            }
        }
    ]

#tool分发
def dispatch_tool(tool_name, tool_args,*, rag, client, longterm_mem, dynamic_mem):
    if tool_name == "analyze_tool":
        return analyze_tool(
            question=tool_args["question"],
            rag=rag,
            client=client,
            longterm_mem=longterm_mem,
            dynamic_mem=dynamic_mem,
        )
    return {"error": f"unknown tool: {tool_name}"}