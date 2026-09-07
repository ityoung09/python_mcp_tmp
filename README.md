# MCP TMP - MCP 学习与实践 + AI 服务

本项目基于 **FastMCP** 构建，一方面帮助初学者快速掌握 **MCP (Model Context Protocol)** 协议的核心原理与实际应用，另一方面集成了底层 AI 服务（当前提供商已重构为 **DeepSeek**）。

---

## 目录结构

```text
.
├── src/
│   ├── ai/                          # 底层 AI 服务
│   │   ├── __init__.py              # 导出 DeepSeekService
│   │   ├── deepseek_service.py      # DeepSeek AI 服务实现类（支持单轮/流式/多轮对话）
│   │   ├── grok_service.py          # （旧版参考）Grok 服务
│   │   └── openai_service.py        # （旧版参考）OpenAI 服务
│   └── mcp/                         # MCP 服务实现
│       ├── __init__.py
│       ├── mcp_tmp.py               # 基础系统信息与星座查询服务 (端口 8000)
│       ├── learning_mcp.py          # 核心教学服务: 全面演示 Tools、Resources 与 Prompts (端口 8001)
│       └── test_learning_mcp.py     # 自动化测试与客户端调用脚本
├── .env.example                     # 环境变量示例
├── main.py                          # 主入口示例
├── pyproject.toml                   # 项目配置与依赖
└── README.md
```

---

## 第一部分：AI 服务 (DeepSeek)

### 配置说明

1. 复制 `.env.example` 为 `.env`：
   ```bash
   cp .env.example .env
   ```
2. 在 `.env` 中填写您的 DeepSeek API Key：
   ```env
   DEEPSEEK_API_KEY=sk-your-key-here
   # 可选配置（若需修改基地址或模型）：
   # DEEPSEEK_BASE_URL=https://api.deepseek.com
   # DEEPSEEK_MODEL=deepseek-chat
   ```

### 使用方法

#### 1. 运行主程序
```bash
uv run python main.py
```

#### 2. 直接运行 DeepSeek 服务测试
```bash
uv run python src/ai/deepseek_service.py
```

#### 3. 代码中调用 DeepSeekService
```python
from src.ai import DeepSeekService

# 初始化（自动从 .env 或环境变量读取 DEEPSEEK_API_KEY）
ai = DeepSeekService()

# 基础对话
reply = ai.chat("你好！")
print(reply)

# 流式对话
for chunk in ai.chat_stream("请写一首小诗"):
    print(chunk, end="", flush=True)
```

---

## 第二部分：MCP 核心三要素 (The Three Primitives)

在 `src/mcp/learning_mcp.py` 中，完整演示了 MCP 协议的三大支柱：

### 1. Tools (工具)
- **概念**：大模型可以主动发起调用的外部函数（类似于 Function Calling）。模型根据你的输入、参数注解和 Docstring 决定何时调用。
- **示例工具**：
  - `calculate(expression)`: 使用 Python AST 语法树进行安全的数学算式求值。
  - `add_memo(title, content, category)`: 增加一条备忘录，结合 Pydantic 自动生成结构化 Schema。
  - `search_memos(keyword, category)`: 关键词与分类检索备忘录。
  - `delete_memo(memo_id)`: 删除指定的备忘录。
  - `get_programming_tip()`: 随机返回一条实用的架构设计与编程知识。

### 2. Resources (资源)
- **概念**：只读的数据上下文通道（类似 REST API 或虚拟文件系统）。客户端或 LLM 可以通过 URI 直接读取数据，作为会话的背景知识。
- **示例资源**：
  - 静态资源 `memo://all`: 读取所有备忘录的 Markdown 格式清单。
  - 静态资源 `memo://stats`: 读取知识库条数、分类分布的 JSON 统计。
  - 动态模板资源 `memo://category/{category_name}`: 动态拉取指定分类下的所有笔记。

### 3. Prompts (提示词模板)
- **概念**：由服务端统一管理的结构化提示词模板。客户端可以一键调用，将特定的业务逻辑或专家人设注入到大模型的对话中。
- **示例模板**：
  - `summarize_memos_prompt(focus_category)`: 知识梳理与行动计划复盘 Prompt。
  - `explain_concept_prompt(concept, target_audience)`: 针对不同受众的概念通俗化拆解 Prompt。

---

## MCP 快速上手与运行

### 1. 一键运行自动化测试 (推荐)
无需配置任何客户端，直接在终端里观察 MCP Client 与 Server 的完整交互：

```bash
uv run python src/mcp/test_learning_mcp.py
```

终端将依次输出 Tools 调用、Resources 读取和 Prompts 模板渲染的结果。

---

### 2. 作为 HTTP SSE 服务运行 (微服务模式)

在独立终端启动服务（默认监听端口 `8001`，避免与 `mcp_tmp.py` 的 `8000` 冲突）：

```bash
uv run python src/mcp/learning_mcp.py --transport sse --port 8001
```

启动后，可以通过 SSE 终端节点 `http://127.0.0.1:8001/sse` 访问。

---

### 3. 接入各大 AI 客户端 (Stdio 模式)

MCP 标准客户端（如 Claude Desktop、Cursor、Antigravity 等）通常通过标准输入输出 (Stdio) 启动子进程。

> 下方配置中的 `<项目绝对路径>` 请替换为你本机克隆本仓库后的绝对路径，例如 `D:/code/python_mcp_tmp`（Windows 下用正斜杠，或把反斜杠双写成 `\`）。

#### Claude Desktop 配置示例 (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "learning-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "<项目绝对路径>",
        "python",
        "src/mcp/learning_mcp.py",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

#### Cursor 配置示例 (`.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "learning-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "<项目绝对路径>",
        "python",
        "src/mcp/learning_mcp.py",
        "--transport",
        "stdio"
      ]
    }
  }
}
```
