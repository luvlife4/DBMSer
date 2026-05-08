from tools.analyze import analyze_skill
from tools.sqlite_exec import exec_sql, show_schema

def analyze_tool(question: str,rag,client,longterm_mem,dynamic_mem):
    return analyze_skill(
        user_input=question,
        client=client,
        rag=rag,
        longterm_mem=longterm_mem,
        dynamic_mem=dynamic_mem
    )

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
    },
    {
        "type": "function",
        "function": {
            "name": "sqlite_exec",
            "description": (
                "在内存SQLite数据库中执行一条SQL语句。"
                "数据库持久存在于整个会话中，建表后可以一直查询。"
                "支持CREATE TABLE、INSERT、SELECT、UPDATE、DELETE等所有SQL语句。"
                "执行SELECT会返回列名和所有行数据。"
                "执行非查询语句会返回影响行数。"
                "执行前如果需要了解当前有哪些表、表结构如何，请先调用sqlite_schema工具。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "要执行的SQL语句"
                    }
                },
                "required": ["sql"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sqlite_schema",
            "description": (
                "查看当前内存数据库中所有表和表结构。"
                "在写SQL之前应该先调用此工具了解数据库中有哪些表、每个表有哪些列。"
                "返回每个表的名称和各列（列名+类型）。"
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
]

def dispatch_tool(tool_name, tool_args,*, rag, client, longterm_mem, dynamic_mem):
    try:
        if tool_name == "analyze_tool":
            result = analyze_tool(
                question=tool_args["question"],
                rag=rag,
                client=client,
                longterm_mem=longterm_mem,
                dynamic_mem=dynamic_mem,
            )
            return {"ok": True, "result": result}
        elif tool_name == "sqlite_exec":
            return exec_sql(tool_args["sql"])
        elif tool_name == "sqlite_schema":
            return show_schema()
        print("tool call unsuccessful")
        return {"ok": False, "error": f"unknown tool: {tool_name}"}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
