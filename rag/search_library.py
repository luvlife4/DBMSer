import numpy as np
from openai import OpenAI
from rag.RAGlibrary import RAGlibrary

 
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_library",
            "description": (
                "从课程知识库中检索与查询相关的参考资料。"
                "当用户提问涉及课程知识、学习内容时，调用此工具获取相关资料。"
                "当用户闲聊与课程无关的问题时，不要调用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用于检索的查询语句。应该是一个清晰的问题或关键词组合。"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回最相关的文档数量，默认 3",
                        "default": 3,
                    },
                },
                "required": ["query"],
            },
        },
    }
]
 
def search_library(
        query:str,
        top_k:int=3,
        *,
        client: OpenAI,
        rag: RAGlibrary,
        embedding_model: str = "text-embedding-v4",)->str:
    response = client.embeddings.create(
        input=query,
        model=embedding_model,
    )
    query_vector = np.array(response.data[0].embedding,dtype=np.float32)
    results = rag.search(query=query_vector,top_k=top_k)
    if not results:
        return "知识库中未找到相关内容。"
 
    # 3. 格式化输出（LLM 会看到这段文本）
    parts = []
    for i, (chunk, score) in enumerate(results, 1):
        parts.append(
            f"[资料 {i}] (来源: {chunk.source}, 相关度: {score:.3f})\n"
            f"{chunk.content}"
        )
 
    return "\n\n---\n\n".join(parts)
 