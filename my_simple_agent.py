"""带工具调用能力的 SimpleAgent

继承框架的 SimpleAgent，加入：
1. system_prompt 末尾自动拼接工具说明
2. 解析 LLM 输出的 [TOOL_CALL:name:params] 标记并执行
3. 多轮工具调用循环 —— 工具结果回灌后让 LLM 继续推理
"""
import re
from typing import Optional
from hello_agents import SimpleAgent, HelloAgentsLLM, Config, Message


class MySimpleAgent(SimpleAgent):
    """加强版 SimpleAgent，支持工具调用"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        tool_registry: Optional["ToolRegistry"] = None,
        enable_tool_calling: bool = True
    ):
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        # 只有同时传入了 registry 且 enable_tool_calling=True 才真启用
        self.enable_tool_calling = enable_tool_calling and tool_registry is not None
        status = "启用" if self.enable_tool_calling else "禁用"
        print(f"✅ {name} 初始化完成，工具调用: {status}")

    # ============================================================
    # 公开入口
    # ============================================================
    def run(self, input_text: str, max_tool_iterations: int = 3, **kwargs) -> str:
        """对外入口 —— 跟父类签名兼容，但加了 max_tool_iterations 防死循环"""
        print(f"\n🤖 {self.name} 收到: {input_text}")

        # 拼接系统提示词（可能带工具说明）+ 历史 + 当前问题
        messages = [{"role": "system", "content": self._build_system_prompt()}]
        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": input_text})

        # 没启用工具 → 走简单分支
        if not self.enable_tool_calling:
            response = self.llm.invoke(messages, **kwargs)
            self.add_message(Message(input_text, "user"))
            self.add_message(Message(response, "assistant"))
            return response

        # 启用工具 → 进入多轮循环
        return self._run_with_tools(messages, input_text, max_tool_iterations, **kwargs)

    # ============================================================
    # 内部方法
    # ============================================================
    def _build_system_prompt(self) -> str:
        """如果有工具注册表，把工具说明拼到 system_prompt 末尾"""
        base = self.system_prompt or "你是一个有用的 AI 助手。"

        if not self.enable_tool_calling:
            return base

        tools_desc = self.tool_registry.get_tools_description()
        if not tools_desc or tools_desc == "暂无可用工具":
            return base

        return (
            f"{base}\n\n"
            f"## 可用工具\n你可以使用以下工具来帮助回答问题：\n{tools_desc}\n\n"
            f"## 工具调用格式\n"
            f"当需要使用工具时，请用如下标记：`[TOOL_CALL:工具名:参数]`\n"
            f"例如：`[TOOL_CALL:calculator:2 + 3 * 4]`\n"
            f"调用工具后，工具结果会被注入对话，然后你可以继续回答。\n"
            f"如果不需要工具，直接回答即可。"
        )

    def _run_with_tools(self, messages: list, input_text: str,
                        max_iter: int, **kwargs) -> str:
        """多轮工具调用循环"""
        final = ""
        for step in range(max_iter):
            response = self.llm.invoke(messages, **kwargs)
            calls = self._parse_tool_calls(response)

            if not calls:
                # 没有工具调用 → 这就是最终回答
                final = response
                break

            print(f"🔧 第 {step+1} 轮发现 {len(calls)} 个工具调用")
            # 把 LLM 这一轮的回应（含调用标记）放进对话
            messages.append({"role": "assistant", "content": response})

            # 执行所有工具调用
            results = []
            for c in calls:
                r = self._exec_tool(c["tool_name"], c["parameters"])
                results.append(r)

            # 把工具结果作为 user 消息塞回去，提示 LLM 继续
            messages.append({
                "role": "user",
                "content": "工具结果：\n" + "\n".join(results) + "\n\n请基于结果继续回答。"
            })
        else:
            # for-else: 没 break 出来说明用完了 max_iter
            final = "（已达最大工具调用次数，未能完成）"

        # 写历史 —— 注意：历史里只保留 user 提问和最终回答
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final, "assistant"))
        return final

    @staticmethod
    def _parse_tool_calls(text: str) -> list:
        """从 LLM 输出抽取 [TOOL_CALL:name:params] 标记"""
        pattern = r"\[TOOL_CALL:([^:\]]+):([^\]]+)\]"
        return [
            {"tool_name": m.group(1).strip(), "parameters": m.group(2).strip()}
            for m in re.finditer(pattern, text)
        ]

    def _exec_tool(self, tool_name: str, parameters: str) -> str:
        """执行单个工具调用，捕获异常"""
        try:
            result = self.tool_registry.execute_tool(tool_name, parameters)
            return f"🔧 {tool_name} → {result}"
        except Exception as e:
            return f"❌ {tool_name} 调用失败: {e}"
