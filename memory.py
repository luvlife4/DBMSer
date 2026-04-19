import json
def update_memory(user_input, reply,longterm_mem, dynamic_mem,client):

    prompt = f"""
你是一个学习助手系统里的“记忆更新器”。

你的任务是根据以下信息，更新两种记忆：

1. longterm_mem
- 只保留对未来长期有价值的信息，不许脑补，不许根据常识扩写
- 比如用户身份、长期目标、长期偏好、长期薄弱点
- 如果本轮没有新增长期信息，就尽量保持原内容，不要乱改

2. dynamic_mem
- 总结当前这几轮最重要的学习状态
- 包括当前主题、当前问题、当前目标、最近薄弱点
- 尽量用短条目列出事实，不要写成评价或推断。
- 要简洁，**适合作为下一轮 system prompt 的一部分**

补充规则：
- 只能记录用户明确表达的信息，或能从对话中直接确定的信息。
- 不要根据常识、角色设定、语气或推测补充事实。
- 不要脑补用户的阶段、水平、目标、课程进度、姓名等。
- 如果某项信息本轮无法确定，就不要写入 longterm_mem。
- dynamic_mem 可以总结当前对话重点，但也不能捏造用户未说过的事实。

已有记忆：
【longterm_mem】
{longterm_mem}

【dynamic_mem】
{dynamic_mem}

本轮对话：
【user】
{user_input}

【assistant】
{reply}

请你只输出 JSON，格式必须是：
{{
  "longterm_mem": "...",
  "dynamic_mem": "..."
}}
"""

    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "system", "content": "你是一个只负责更新记忆的模块，输出必须是合法 JSON。"},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content

    try:
        data = json.loads(content)
        longterm_mem = data.get("longterm_mem", longterm_mem)
        dynamic_mem = data.get("dynamic_mem", dynamic_mem)

        if isinstance(longterm_mem, list):
            longterm_mem = "\n".join(f"- {item}" for item in longterm_mem)

        if isinstance(dynamic_mem, list):
            dynamic_mem = "\n".join(f"- {item}" for item in dynamic_mem)
        print("longterm_mem 已更新：\n", longterm_mem)
        print("dynamic_mem 已更新：\n", dynamic_mem)
    except Exception as e:
        print("记忆更新失败：", e)
        print("模型原始输出：", content)
    return longterm_mem, dynamic_mem