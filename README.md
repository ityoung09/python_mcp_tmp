# MCP TMP - AI 服务与 FastMCP

本项目集成了 FastMCP 工具服务与底层 AI 服务。当前底层 AI 服务提供商已重构为 **DeepSeek**。

## 目录结构

```text
├── src/
│   ├── ai/
│   │   ├── __init__.py          # 导出 DeepSeekService
│   │   ├── deepseek_service.py  # DeepSeek AI 服务实现类（支持单轮/流式/多轮对话）
│   │   ├── grok_service.py      # （旧版参考）Grok 服务
│   │   └── openai_service.py    # （旧版参考）OpenAI 服务
│   └── mcp/
│       └── mcp_tmp.py           # FastMCP 工具服务
├── .env.example                 # 环境变量示例
├── main.py                      # 主入口示例
└── pyproject.toml               # 项目配置与依赖
```

## 配置说明

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

## 使用方法

### 1. 运行主程序
```bash
uv run python main.py
```

### 2. 直接运行 DeepSeek 服务测试
```bash
uv run python src/ai/deepseek_service.py
```

### 3. 代码中调用 DeepSeekService
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
