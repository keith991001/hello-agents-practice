"""自定义的 LLM 客户端

通过继承 HelloAgentsLLM 演示三件事：
1. 添加一个真正干净的 stream 方法（修复框架内部 print 重复输出的问题）
2. 自动追踪每次调用消耗的 token 数量
3. 演示 super().__init__() 模式 —— 把不熟悉的 provider 交给父类处理
"""
import os
from typing import Optional, Iterator
from openai import OpenAI
from hello_agents import HelloAgentsLLM


class MyLLM(HelloAgentsLLM):
    """加强版 LLM 客户端"""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        provider: Optional[str] = None,  # 不传 None 会跳过父类的自动检测
        **kwargs
    ):
        # 先调用父类的 __init__ 把 client/model/provider 等基础属性建好
        super().__init__(
            model=model,
            api_key=api_key,
            base_url=base_url,
            provider=provider,
            **kwargs
        )
        # 我们自己增加的状态：token 使用量统计
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_calls = 0
        print(f"📊 MyLLM 已初始化，token 追踪已开启")

    def clean_stream(self, messages: list[dict], **kwargs) -> Iterator[str]:
        """真正干净的流式调用 —— 只 yield 不 print

        这是框架原生 think / stream_invoke 的修复版。框架的 think 内部
        会用 print() 把 chunk 打到 stdout，导致用户代码再 print 一次时
        每个字会出现两遍。这里我们直接调用 OpenAI SDK，绕开框架的 print。
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get('temperature', self.temperature),
            max_tokens=kwargs.get('max_tokens', self.max_tokens),
            stream=True,
            stream_options={"include_usage": True},  # 让 DeepSeek 在末尾返回 token 统计
        )

        self.total_calls += 1
        for chunk in response:
            # 末尾会有一个 chunk 只携带 usage 信息（choices 为空）
            if chunk.usage:
                self.total_prompt_tokens += chunk.usage.prompt_tokens
                self.total_completion_tokens += chunk.usage.completion_tokens
                continue
            # 内容 chunk
            if chunk.choices:
                content = chunk.choices[0].delta.content or ""
                if content:
                    yield content

    def get_usage_summary(self) -> str:
        """打印累计 token 使用情况"""
        return (
            f"📊 累计调用 {self.total_calls} 次 | "
            f"输入 {self.total_prompt_tokens} tokens | "
            f"输出 {self.total_completion_tokens} tokens"
        )
