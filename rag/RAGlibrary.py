from openai import OpenAI
import numpy as np
from pathlib import Path
from dataclasses import dataclass  

@dataclass
class Chunk:
    content: str    # 文本片段内容
    source: str     # 来源文件名
    index: int      # 片段序号

class RAGlibrary:
    def __init__(        
        self,
        client:OpenAI,
        embedding_model: str,
        chunk_size = 500,
        chunk_overlap = 50,

    ) -> None:
        if chunk_size <=0 or chunk_overlap < 0:
            raise ValueError("chunk parameter error.cannot process.")
        
        self.client = client
        self.embedding_model = embedding_model
        self.chunk_overlap = chunk_overlap
        self.chunk_size = chunk_size

        self.chunks = []
        self.embeddings: np.ndarray | None = None
    
    #分词
    def _split_text(self,text:str) -> list[str]:
        text = text.strip()
        if not text:
            return []
        
        start = 0
        result = []
        while start < len(text):
            end = start+self.chunk_size
            result.append(text[start:end])
            start+=self.chunk_size-self.chunk_overlap
        return result

    #加载文档
    def load_documents(self,dir_path: str | Path)->None:
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise NotADirectoryError("not a dir: {dir_path} !")
        self.chunks = []
        self.embeddings = None
        for path in dir_path.rglob("*"):
            if path.suffix.lower() not in {".txt",".md"}:
                continue
            content = path.read_text(encoding="utf-8")
            for text in self._split_text(content):
                self.chunks.append(
                    Chunk(
                        content=text,
                        source = path.name,
                        index = len(self.chunks)
                    )
                )

    #创建向量库
    def create_embeddings(self)->None:
        if not self.chunks:
            raise ValueError("No chunks found.")
        
        vectors = []
        batch_size = 10
        chunk_batch = []
        for chunk in self.chunks:
            chunk_batch.append(chunk.content)
            if len(chunk_batch) == batch_size:
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=chunk_batch
                )
                chunk_batch = []
                vectors.extend(item.embedding for item in response.data)

        if chunk_batch:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=chunk_batch
            )
        vectors.extend(item.embedding for item in response.data)
        
        self.embeddings = np.array(vectors,dtype=np.float32)
    
    #保存向量索引
    def save_index(self,filepath:str | Path)->None:
        if self.embeddings is None:
            raise ValueError("No embeddings to save")
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True,exist_ok=True)

        np.savez(
            filepath,
            embeddings = self.embeddings,
            chunks_content = np.array([chunk.content for chunk in self.chunks]),
            chunks_source = np.array([chunk.source for chunk in self.chunks]),
            chunks_index = np.array([chunk.index for chunk in self.chunks])
        )
    
    #加载向量
    def load_index(self,filepath:str|Path)->None:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True,exist_ok=True)   
        if not filepath.exists():
            raise ValueError("Cannot Load.No local embeddings found.")
        data = np.load(filepath)
        self.embeddings = data["embeddings"]
        self.chunks = [
            Chunk(
                content=str(content),
                source=str(source),
                index=int(idx),
            )
            for content, source, idx in zip(
                data["chunks_content"],
                data["chunks_source"],
                data["chunks_index"],
            )
        ]

    #检索向量库
    def search(self,query:np.ndarray,top_k:int=5)->list[tuple[Chunk,float]]:

        if self.embeddings is None:
            raise ValueError("cannot search similarity,cause theres no embeddings")
        chunk_similarities = []

        for chunk, embedding in zip(self.chunks, self.embeddings):
            sim = _cosine_similarity(query, embedding)
            chunk_similarities.append((chunk, sim))
        chunk_similarities.sort(key=lambda x: x[1], reverse=True)
        return chunk_similarities[:top_k]
        

#==========辅助函数=============#
def _cosine_similarity(query:np.ndarray,documents:np.ndarray):
    similarity = np.dot(query,documents)/(np.linalg.norm(query)*np.linalg.norm(documents))
    return similarity
def load_or_build_rag_library(
        client:OpenAI,
        embedding_model:str = "text-embedding-v4",
        docs_dir :str|Path="library",
        index_path:str|Path = "library/index.npz",
        verbose: bool = True,
    )->RAGlibrary:
    docs_dir = Path(docs_dir)
    index_path = Path(index_path)

    rag = RAGlibrary(client=client,embedding_model=embedding_model)

    if index_path.exists():
        if verbose:
            print("加载本地向量索引...")
        rag.load_index(index_path)
    else:
        if verbose:
            print("找不到本地索引，创建索引中...")
        rag.load_documents(docs_dir)
        rag.create_embeddings()
        rag.save_index(index_path)
        if verbose:
            print("创建索引成功！")

    return rag   

