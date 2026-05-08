from openai import OpenAI
from rag.RAGlibrary import RAGlibrary
from rag.search_library import search_library

def rewrite_query(user_input,client):
    prompt = f"""
        你是数据库知识库检索的 query rewrite 模块。

        任务：
        把用户原始输入改写成更适合检索知识库的查询语句，用于在数据库课程资料中搜索相关知识点。

        要求：
        1. 保留用户真正想问的核心问题
        2. 补全明显相关的数据库术语
        3. 去掉寒暄、口语废话、无关表述
        4. 不要改变原问题意思
        5. 输出尽量短，适合检索
        6. 只输出改写后的 query，不要解释

        【用户输入】
        {user_input}
        """

    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role":"system","content":"你是一个只负责改写检索 query 的模块，只输出 query 本身。"},
            {"role":"user","content":prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def analyze_skill(user_input,client: OpenAI, rag,longterm_mem="", dynamic_mem=""):
    # 1. 先重写,然后搜索
    search = rewrite_query(user_input=user_input,client=client)
    rag_results = search_library(search,3,client=client,rag=rag)
    print("rewrite后的query:", repr(search))
    # print("rag text result",rag_results)

    # 2. 把检索结果拼成文本
    if isinstance(rag_results, list):
        rag_text = "\n".join(f"{i+1}. {item}" for i, item in enumerate(rag_results))
    else:
        rag_text = str(rag_results)

    # 3. 让模型做分析和总结
    prompt = f"""
你是数据库学习助手里的“检索分析模块”。

你的任务：
1. 根据用户问题，判断他当前在问什么知识点
2. 结合检索到的资料，给出资料中的相关知识
3. 给出一个简短、自然的总结
4. 不要编造资料里没有的信息
5. 输出给上层程序看的简洁结果，不要啰嗦

【用户输入】
{user_input}

【longterm_mem】
{longterm_mem}

【dynamic_mem】
{dynamic_mem}

【RAG检索结果】
{rag_text}

请按下面格式输出：

主题：
资料相关内容：
总结：
"""

    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "system", "content": "你是数据库学习助手中的学情分析模块，只能基于用户输入、记忆和检索结果进行分析，不要编造。"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

