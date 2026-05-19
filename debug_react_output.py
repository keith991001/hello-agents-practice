"""调试 DeepSeek 对 ReAct prompt 的真实输出格式"""
from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM, ToolRegistry
from safe_calculator import SafeCalculatorTool
from my_react_agent import MY_REACT_PROMPT

load_dotenv()
llm = HelloAgentsLLM()
registry = ToolRegistry()
registry.register_tool(SafeCalculatorTool())

prompt = MY_REACT_PROMPT.format(
    tools=registry.get_tools_description(),
    question="请帮我计算 (15 * 8 + 32) / 4 是多少？",
    history="",
)

response = llm.invoke([{"role": "user", "content": prompt}])

print("=" * 60)
print("DeepSeek 原始响应（注意观察 Thought / Action 的真实格式）：")
print("=" * 60)
print(response)
print("=" * 60)
print("响应长度:", len(response), "字符")
print("response.startswith('Thought'):", response.startswith("Thought"))
print("'Action:' in response:", "Action:" in response)
print("'**Action:**' in response:", "**Action:**" in response)
