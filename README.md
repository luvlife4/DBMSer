# DBMSer

基于 LLM + RAG 的数据库课程智能学习助手。提供 Web 网页界面，支持知识检索分析、SQL 在线执行、学习画像、学习计划记录与回顾。

## 功能

- **Web 网页界面**：侧边栏 + 聊天区 + 弹窗，暗色主题，支持 Markdown 渲染
- **智能知识问答**：基于本地知识库的 RAG 检索增强问答，含 `rewrite_query` 查询改写，概念解释、易混点对比、小例讲解
- **SQL 在线执行**：内存 SQLite 环境，支持建表、插入、查询全流程，执行结果即时反馈，错误自动解释
- **学习画像**：基于 longterm_mem 生成结构化画像表（身份、目标、已掌握、薄弱点、偏好），弹窗展示
- **学习计划生成**：根据用户输入（学习目标、天数、薄弱点）由 LLM 生成分天学习计划，生成一次后持久缓存，侧边栏随时查看
- **双层记忆系统**：longterm_mem（学习画像表） + dynamic_mem（会话状态），后台异步更新
- **学习诊断与出题**：根据薄弱点生成针对性练习，判对错、分析错误原因

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

Web 启动：

```bash
python server.py
```

浏览器访问 `http://127.0.0.1:8000`，即可在网页中对话。

终端启动：

```bash
python main.py
```

输入问题即可对话，输入 `bye` 退出。

## 目录

```
DBMSer/
├── server.py                 # FastAPI Web 服务：路由、静态文件、Agent 管理
├── main.py                   # 终端入口，交互循环
├── output.py                 # Rich 格式化输出
├── static/
│   ├── index.html            # Web 页面
│   ├── style.css             # 样式
│   └── app.js                # 前端逻辑
├── agent/
│   ├── agent.py              # DBMSerAgent 类：对话循环、工具调度、后台记忆/计划更新
│   └── memory.py             # 双层记忆更新器
├── tools/
│   ├── tools.py              # 工具注册与 dispatch 分发
│   ├── analyze.py            # RAG 检索 + rewrite_query + LLM 分析
│   └── sqlite_exec.py        # SQLite 执行与 schema 查询
├── rag/
│   ├── RAGlibrary.py         # 向量库：文档加载、分块、嵌入、检索
│   └── search_library.py     # 检索工具封装
├── soul/
│   ├── soul.md               # 精简 system prompt
│   ├── real_soul.md          # 完整 system prompt（首次加载）
│   └── memory.md             # 长期记忆持久化文件
├── library/
│   ├── dbms.md               # MySQL 课程笔记
│   ├── 数据库原理与系统书稿-第1-12章.md
│   └── index.npz             # 向量索引缓存
└── requirements.txt
```

## 工具说明

| 工具 | 用途 |
|------|------|
| `analyze_tool` | RAG 检索知识库（含 rewrite_query 查询改写），返回课程资料与分析 |
| `sqlite_exec` | 在内存 SQLite 中执行 SQL 语句 |
| `sqlite_schema` | 查看当前数据库有哪些表、表结构如何 |

## API 接口

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | Web 页面 |
| `/chat` | POST | 对话 |
| `/new-chat` | POST | 新对话 |
| `/learning-portrait` | POST | 获取学习画像 |
| `/learning-schedule` | POST | 获取学习计划 |

## 初始化

首次运行自动扫描 `library/` 下的 `.md`/`.txt` 文件，构建向量索引并缓存为 `library/index.npz`。之后启动直接加载缓存。
