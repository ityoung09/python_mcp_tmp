import os
import sys
from typing import Generator, Optional
from dotenv import load_dotenv
from openai import OpenAI

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()


class DeepSeekService:
    """DeepSeek AI 服务封装类"""

    DEFAULT_BASE_URL = "https://api.deepseek.com"
    DEFAULT_MODEL = "deepseek-chat"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = (
            base_url or os.getenv("DEEPSEEK_BASE_URL") or self.DEFAULT_BASE_URL
        )
        self.model = model or os.getenv("DEEPSEEK_MODEL") or self.DEFAULT_MODEL

        if not self.api_key:
            raise ValueError(
                "未找到 DEEPSEEK_API_KEY，请在环境变量或 .env 文件中配置 DEEPSEEK_API_KEY，或在实例化时传入 api_key。"
            )

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def chat(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 1.0,
        **kwargs,
    ) -> str:
        """发送单轮对话请求并获取完整回复

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 采样温度 (0.0 ~ 2.0)
            **kwargs: 透传给 openai 客户端的其他参数

        Returns:
            模型生成的回复文本
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    def chat_stream(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 1.0,
        **kwargs,
    ) -> Generator[str, None, None]:
        """以流式输出方式发送对话请求

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 采样温度
            **kwargs: 透传给 openai 客户端的其他参数

        Yields:
            逐块生成的文本片段
        """
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            stream=True,
            **kwargs,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def create_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 1.0,
        **kwargs,
    ):
        """支持自定义 messages 列表的多轮对话或高级请求

        Args:
            messages: 符合 OpenAI 格式的消息列表
            temperature: 采样温度
            **kwargs: 透传给 openai 客户端的其他参数

        Returns:
            ChatCompletion 响应对象
        """
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            **kwargs,
        )


if __name__ == "__main__":
    try:
        service = DeepSeekService()
        print(f"正在使用模型: {service.model} 连接 {service.base_url} ...")
        question = "可以给我讲一个中文笑话吗?"
        print(f"提问: {question}\n")
        answer = service.chat(question)
        print(f"DeepSeek 回复:\n{answer}")
    except ValueError as err:
        print(f"配置提示: {err}")
        print("示例用法: 设置环境变量 DEEPSEEK_API_KEY='sk-...' 或创建 .env 文件。")
