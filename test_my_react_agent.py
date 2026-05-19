"""测试 MyReActAgent

跑两个题目，让你看到 ReAct 的多步推理过程：
- 题 1：单步计算
- 题 2：多步组合计算（需要连续调工具）
"""
from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM, ToolRegistry
from safe_calculator import SafeCalculatorTool
from my_react_agent import MyReActAgent

load_dotenv()

llm = HelloAgentsLLM()
registry = ToolRegistry()
registry.register_tool(SafeCalculatorTool())

agent = MyReActAgent(
    name="ReAct 推理助手",
    llm=llm,
    tool_registry=registry,
    max_steps=5,
)


# === 题 1：简单计算 ===
print("\n" + "=" * 60)
print("题 1：(15 * 8 + 32) / 4 = ?")
print("=" * 60)
answer1 = agent.run("请帮我计算 (15 * 8 + 32) / 4 是多少？")
print(f"\n👉 最终答案：{answer1}")


# === 题 2：组合计算 —— 需要多步 ===
print("\n" + "=" * 60)
print("题 2：一个长方形长 17.5、宽 8.3，求它的面积和周长")
print("=" * 60)
answer2 = agent.run("一个长方形长 17.5 米，宽 8.3 米。请分别算出它的面积和周长。")
print(f"\n👉 最终答案：{answer2}")
