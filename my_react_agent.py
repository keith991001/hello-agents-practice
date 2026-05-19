"""自定义的 ReActAgent

继承框架的 ReActAgent，主要演示 ReAct 范式 = Reasoning + Acting：
1. 每一步 LLM 必须先输出 Thought（思考），再输出 Action（行动）
2. Action 要么是工具调用，要么是 Finish 收尾
3. 工具结果作为 Observation 回灌进下一轮 prompt

另外修复了一个框架 bug：默认 parser 的正则不识别 markdown 粗体（**Thought:**）。
"""
import re
from typing import Optional, Tuple
from hello_agents import ReActAgent, HelloAgentsLLM, Config, ToolRegistry


# 自定义提示词模板 —— 比框架默认版多了"明确禁止心算"的约束
MY_REACT_PROMPT = """你是一个具备推理和行动能力的 AI 助手。请严格按 ReAct 范式作答：每一轮思考一步、行动一步。

## 可用工具
{tools}

## 工作流程（严格遵守！每一轮回应只能包含一个 Thought 和一个 Action）

**Thought:** 分析当前问题，思考下一步该做什么。
**Action:** 选择一个行动，格式必须是下面之一：
- `工具名[参数]` —— 调用指定工具，例如 `calculator[15 * 8 + 32]`
- `Finish[最终答案]` —— 当你已经从工具获得足够信息时，用它收尾

## 重要纪律
1. 涉及数学计算时，**必须使用 calculator 工具**，禁止心算或推导
2. 工具结果会作为 Observation 出现在下一轮的"执行历史"里，你要基于它继续推理
3. 一次 Action 解决不了的话，可以连续调用工具多次
4. 别一次输出多个 Action，每轮一次

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动："""


class MyReActAgent(ReActAgent):
    """重写的 ReActAgent，用更严格的提示词"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        tool_registry: ToolRegistry,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        max_steps: int = 5,
        custom_prompt: Optional[str] = None,
    ):
        # 如果调用方没传 custom_prompt，就用我们写的 MY_REACT_PROMPT
        prompt = custom_prompt if custom_prompt else MY_REACT_PROMPT
        super().__init__(
            name=name,
            llm=llm,
            tool_registry=tool_registry,
            system_prompt=system_prompt,
            config=config,
            max_steps=max_steps,
            custom_prompt=prompt,
        )
        print(f"✅ {name} 初始化完成，最大步数: {max_steps}")

    # ============================================================
    # 修复框架 bug：默认 parser 不认 markdown 粗体（**Thought:**）
    # ============================================================
    def _parse_output(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """容忍 markdown 粗体的 ReAct 输出解析器

        匹配模式（可选 ** 包围）：
          **Thought:** xxxx   /  Thought: xxxx   /  **Thought**: xxxx
          **Action:**  yyyy   /  Action:  yyyy   /  **Action**:  yyyy
        """
        thought_pat = r"\*{0,2}Thought\*{0,2}\s*:\s*\*{0,2}\s*(.+?)(?=\n|$)"
        action_pat = r"\*{0,2}Action\*{0,2}\s*:\s*\*{0,2}\s*(.+?)(?=\n|$)"

        thought_match = re.search(thought_pat, text)
        action_match = re.search(action_pat, text)

        thought = thought_match.group(1).strip().rstrip("*").strip() if thought_match else None
        action = action_match.group(1).strip().rstrip("*").strip() if action_match else None

        # Action 内容可能被包在反引号里：`calculator[...]` —— 也兼容一下
        if action and action.startswith("`") and action.endswith("`"):
            action = action[1:-1].strip()

        return thought, action
