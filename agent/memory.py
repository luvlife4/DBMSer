import json
from pathlib import Path
import os
def save_longterm_mem(longterm_mem):
    with open("./soul/memory.md","w",encoding="utf-8") as f:
        f.write(longterm_mem)
def update_memory(user_input, reply,longterm_mem, dynamic_mem,client):

    prompt = f"""
你是一个学习助手系统里的“记忆更新器”。

你的任务是根据以下信息更新两种记忆。

## longterm_mem（学习画像）

longterm_mem 是一张固定格式的学习画像表。你必须严格按照以下字段输出，未知项填"未知"：


|------|------|
| 身份 | 用户身份（如大二计算机学生） |（此处你可以猜测）
| 长期目标 | 学习数据库的长期目标（如通过期末考试、考研） |
| 已掌握知识点 | 用户明确已经学会的知识点 |
| 薄弱点 | 用户经常出错或不理解的知识点 |
| 学习偏好 | 用户偏好的学习方式（如先讲概念再做题、直接刷题等） |

规则：
- 只能记录用户明确表达的信息，不许脑补，不许根据常识扩写
- 如果本轮没有新增信息，各个字段保持原内容不变
- 某个字段本轮无法确定且之前也没有记录，填"未知"

## dynamic_mem

- 总结当前这几轮最重要的学习状态
- 包括当前主题、当前问题、最近薄弱点
- 用短条目列出事实，不要写成评价或推断
- 要简洁，适合作为下一轮 system prompt 的一部分
- 不能捏造用户未说过的事实

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
  "longterm_mem": "| 字段 | 内容 |\\n|------|------|\\n| 身份 | ... |\\n| 长期目标 | ... |\\n| 已掌握知识点 | ... |\\n| 薄弱点 | ... |\\n| 学习偏好 | ... |",
  "dynamic_mem": "..."
}}
"""

    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "system", "content": "你是一个只负责更新记忆的模块，输出必须是合法 JSON。"},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"} 
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
        #print("longterm_mem 已更新：\n", longterm_mem)
        save_longterm_mem(longterm_mem=longterm_mem)
        #print("dynamic_mem 已更新：\n", dynamic_mem)
    except Exception as e:
        print("记忆更新失败：", e)
        print("模型原始输出：", content)
    return longterm_mem, dynamic_mem