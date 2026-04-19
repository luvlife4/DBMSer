# DBMSer

DBMSer 是一个基于 OpenAI 和本地知识库的数据库学习助手。它使用向量检索（RAG）和工具调用机制，为用户提供数据库课程资料检索、问题分析与总结能力。

## 功能

- 基于 `library/` 中文档构建本地向量索引
- 使用 OpenAI 模型处理对话、生成回答与更新记忆
- 动态维护聊天历史、长期记忆和当前学习状态
- 支持工具调用：RAG检索知识库，分析用户问题

## 依赖

- Python 3.11+
- `openai`
- `numpy`
- `rich`
- `python-dotenv`

## 安装

1. 创建 Conda 环境并激活：

```bash
conda create -n dbmser python=3.11 -y
conda activate dbmser
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 在项目根目录创建 `.env` 文件，添加环境变量：

```env
API_KEY=your_openai_api_key
BASE_URL=https://api.openai.com/v1
```

> 如果你使用兼容的自定义服务或私有部署，请将 `BASE_URL` 修改为相应地址。

## 使用方法

```bash
python main.py
```

然后在交互提示符中输入问题，输入 `exit` 退出。

## 目录说明

- `main.py`：启动交互式聊天入口
- `agent.py`：主代理逻辑，负责构建对话、调用 OpenAI、更新记忆
- `memory.py`：负责长期记忆与动态记忆的更新
- `tools/tools.py`：工具注册与分发实现
- `tools/analyze_tool.py`：分析工具封装
- `skills/analyze.py`：实际分析逻辑与 RAG 检索调用
- `rag/RAGlibrary.py`：本地向量库构建与检索实现
- `rag/search_library.py`：检索知识库工具实现
- `library/`：保存用于构建向量索引的知识文档
- `soul/`：系统上下文与状态描述文件

## 初始化说明

首次运行时，系统会尝试加载 `library/index.npz`。如果不存在，则会自动扫描 `library/` 下的 `.txt` / `.md` 文件并构建向量索引。

## 注意事项

- 请确保 `library/` 目录下有有效的课程资料文件
- 保持 `.env` 中的 `API_KEY` 和 `BASE_URL` 配置正确
- 推荐在支持中文的模型或服务上运行
