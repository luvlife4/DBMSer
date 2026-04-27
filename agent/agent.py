from openai import OpenAI
from tools.tools import tools,dispatch_tool
import json
from rag.RAGlibrary import load_or_build_rag_library
from agent.memory import update_memory
import os
from dotenv import load_dotenv
#环境变量
load_dotenv()
#state 存储学生的各类学习状态
soul = ""
with open("./soul/soul.md", "r", encoding="utf-8") as f:
    soul = f.read()
with open("./soul/memory.md","r",encoding="utf-8") as f:
    longterm_mem = f.read()
dynamic_mem = ""
#这一轮对话的历史
history = []

#创建client
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL")
    )
#加载向量库
rag = load_or_build_rag_library(
    client=client,
    docs_dir="library",
    index_path="library/index.npz",
)
#更新状态
def build_state():
    dynamic_text = dynamic_mem
    if isinstance(dynamic_mem, list):
        dynamic_text = "\n".join(f"- {item}" for item in dynamic_mem)

    return soul + "\n" + longterm_mem + "\n" + dynamic_text

#主循环
def agent_loop(user_input):

    global longterm_mem, dynamic_mem, history
    recent_history = history[-4:]
    state = build_state()
    messages = [
        {"role": "system", "content": state},
        *recent_history,#这里用的是最近几轮的
        {"role": "user", "content": user_input}
    ]
    while True:
        #更新历史
        recent_history = history[-4:]
        #更新状态
        state = build_state()

        response = client.chat.completions.create(
            model="qwen-plus",
            tools=tools,
            messages=messages
        )
        choice = response.choices[0]
        reply = choice.message.content

        if choice.finish_reason == "stop":
            #根据对话更新动态记忆，这样可以实现智能总结对话，
            #提取关键信息，提取出最重要的：学生学习情况
            longterm_mem,dynamic_mem = update_memory(user_input=user_input,reply=reply,longterm_mem=longterm_mem
                          ,dynamic_mem=dynamic_mem,client=client)
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": reply})
            return choice.message.content

        if choice.finish_reason == "tool_calls":
            #把要调用工具这条信息加进messages里
            messages.append(choice.message)
            
            for tool_call in choice.message.tool_calls:
                print("调用工具，名称：",tool_call.function.name)
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)   
                tool_result = dispatch_tool(
                    tool_name,
                    tool_args,
                    rag=rag,
                    client=client,
                    longterm_mem=longterm_mem,
                    dynamic_mem=dynamic_mem,
                )            
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            continue
