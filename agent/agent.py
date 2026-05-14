from openai import OpenAI
from tools.tools import tools,dispatch_tool
import json
import threading
from rag.RAGlibrary import load_or_build_rag_library
from agent.memory import update_memory
import os
from dotenv import load_dotenv
#环境变量
load_dotenv()
class DBMSerAgent :
    def __init__(self) -> None:
        with open("./soul/real_soul.md", "r", encoding="utf-8") as f:
            self.real_soul = f.read()
        with open("./soul/soul.md", "r", encoding="utf-8") as f:
            self.soul = f.read()
        self.dynamic_mem = ""
        self.longterm_mem = ""
        self.client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("BASE_URL")
        )
        self.rag = load_or_build_rag_library(
            client=self.client,
            docs_dir="library",
            index_path="library/index.npz",
        )
        self.state = ""
        self.history = []
        self.recent_history = []
        self.isFirstTime = True
        self.input = ""
        self.schedule = ""
    def build_state(self):
        dynamic_text = self.dynamic_mem
        if isinstance(self.dynamic_mem, list):
            dynamic_text = "\n".join(f"- {item}" for item in self.dynamic_mem)

        return self.soul + "\n" + self.longterm_mem + "\n" + dynamic_text
    
    def collect_mem(self):
        return str(self.longterm_mem)+str(self.dynamic_mem)

    def collect_schedule(self):
        if not self.history:
            return "暂无对话历史，请先进行一些对话。"
        collect_prompt = (
            "这是用户最近的输入，根据用户的学习目标，剩余天数，薄弱点制定计划。"
            "如果用户没有明确的与学习计划相关的信息，就在计划中尽量全面的覆盖知识点。"
            "最后输出这部分计划，不要有多余的输出。"
        )
        messages = [
            {"role":"system","content":self.soul+collect_prompt},
            {"role":"user","content": self.input}
        ]
        if self.schedule == "":
            response = self.client.chat.completions.create(
                model = "qwen-plus",
                messages = messages
                )
            self.schedule = response.choices[0].message.content
        return self.schedule or "未能提取到学习计划。"
    def agent_loop(self,user_input):

        self.input +=str(user_input)
        self.recent_history = self.history[-4:]
        self.state = self.build_state()
        # 第一次循环才读真正的长文档，后面都读小的
        if  self.isFirstTime :
            messages = [
                {"role": "system", "content": self.real_soul+self.state},
                *self.recent_history,#这里用的是最近几轮的
                {"role": "user", "content": user_input}
            ]
            self.isFirstTime = False
        else:
            messages = [
                {"role": "system", "content": self.state},
                *self.recent_history,#这里用的是最近几轮的
                {"role": "user", "content": user_input}
            ]
        # 更新历史
        self.recent_history = self.history[-4:]
        # 更新状态
        self.state = self.build_state()
        while True:
            response = self.client.chat.completions.create(
                model="qwen-plus",
                tools=tools,
                messages=messages
            )
            choice = response.choices[0]
            reply = choice.message.content

            if choice.finish_reason == "stop":
                #根据对话更新动态记忆，这样可以实现智能总结对话，
                #提取关键信息，提取出最重要的：学生学习情况
                def background_memory_task():
                    self.longterm_mem, self.dynamic_mem = update_memory(
                    user_input=user_input,
                    reply=reply,
                    longterm_mem=self.longterm_mem,
                    dynamic_mem=self.dynamic_mem,
                    client=self.client
                )
                threading.Thread(
                    target=background_memory_task,
                    daemon=True
                ).start()
                threading.Thread(
                    target=self.collect_schedule,
                    daemon=True
                ).start()
                #后台更新计划
                self.history.append({"role": "user", "content": user_input})
                self.history.append({"role": "assistant", "content": reply})
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
                        rag=self.rag,
                        client=self.client,
                        longterm_mem=self.longterm_mem,
                        dynamic_mem=self.dynamic_mem,
                    )            
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result, ensure_ascii=False)
                    })