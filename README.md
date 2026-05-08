# DBMSer

基于 LLM + RAG 的数据库课程智能学习助手。支持知识检索分析、SQL 在线执行、双层记忆追踪。

## 功能

- **智能知识问答**：基于本地知识库（MySQL教程 + 数据库理论教材）的 RAG 检索增强问答，概念解释、易混点对比、小例讲解
- **SQL 在线执行**：内存 SQLite 环境，支持建表、插入、查询全流程，SQL 执行结果即时反馈，错误自动解释
- **双层记忆系统**：longterm_mem（持久化长期画像） + dynamic_mem（会话动态状态），后台异步更新，不阻塞对话
- **学习诊断与出题**：根据薄弱点生成针对性练习，判对错、分析错误原因
- **学习计划制定**：结合学生基础、目标、可用时间，按天生成具体学习计划

## 安装

```bash
pip install -r requirements.txt
```

项目根目录创建 `.env` 文件：

```env
API_KEY=your_api_key
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

## 使用

```bash
python3 main.py
```

输入问题即可对话，输入 `bye` 退出。

## 目录

```
DBMSer/
├── main.py                  # 入口，交互循环
├── output.py                # Rich 格式化输出
├── agent/
│   ├── agent.py             # 核心对话循环、工具调度、记忆更新
│   └── memory.py            # 双层记忆更新器
├── tools/
│   ├── tools.py             # 工具注册与 dispatch 分发
│   ├── analyze_tool.py      # RAG 分析工具封装
│   └── analyze.py           # RAG 检索 + LLM 分析逻辑
│   └── sqlite_exec.py       # SQLite 执行与 schema 查询
├── rag/
│   ├── RAGlibrary.py        # 向量库：文档加载、分块、嵌入、检索
│   └── search_library.py    # 检索工具封装
├── soul/
│   ├── soul.md              # 精简 system prompt
│   ├── real_soul.md         # 完整 system prompt（首次加载）
│   └── memory.md            # 长期记忆持久化文件
├── library/
│   ├── dbms.md              # MySQL 课程笔记
│   ├── 数据库原理与系统书稿-第1-12章.md
│   └── index.npz            # 向量索引缓存
└── requirements.txt
```

## 工具说明

| 工具 | 用途 |
|------|------|
| `analyze_tool` | RAG 检索知识库，返回相关课程资料与分析 |
| `sqlite_exec` | 在内存 SQLite 中执行 SQL 语句 |
| `sqlite_schema` | 查看当前数据库有哪些表、表结构如何 |

## 初始化

首次运行自动扫描 `library/` 下的 `.md`/`.txt` 文件，构建向量索引并缓存为 `library/index.npz`。之后启动直接加载缓存。
