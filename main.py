import os
import sys
from src.ai import DeepSeekService

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    print("=== DeepSeek AI 服务测试 ===")
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("提示: 未检测到 DEEPSEEK_API_KEY。请在 .env 中设置 DEEPSEEK_API_KEY=sk-...")
        print("也可以在调用 DeepSeekService 时通过参数传入 api_key。")
        return

    ai_service = DeepSeekService()
    print(f"底层 AI 提供商: DeepSeek (模型: {ai_service.model})")
    prompt = "请简要介绍一下你自己，以及你支持哪些功能？"
    print(f"用户问题: {prompt}\n")
    response = ai_service.chat(prompt)
    print(f"AI 回复:\n{response}")


if __name__ == "__main__":
    main()
