"""测试 MySimpleAgent：无工具 → 加工具 → 多轮调用 → 历史记录"""
from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM, ToolRegistry
from safe_calculator import SafeCalculatorTool
from my_simple_agent import MySimpleAgent

load_dotenv()
llm = HelloAgentsLLM()


# === 测试 1：不带工具的纯对话 ===
print("=" * 50)
print("测试 1：纯对话（无工具）")
print("=" * 50)
plain = MySimpleAgent(
    name="纯对话助手",
    llm=llm,
    system_prompt="你是一个友好的 AI 助手，请用简洁明了的方式回答。",
)
print("回答:", plain.run("用一句话告诉我什么是 Python？"))


# === 测试 2：带计算器工具 ===
print("\n" + "=" * 50)
print("测试 2：带工具调用")
print("=" * 50)

registry = ToolRegistry()
registry.register_tool(SafeCalculatorTool())

calc_agent = MySimpleAgent(
    name="计算助手",
    llm=llm,
    system_prompt="你是一个智能助手，遇到数学计算优先用 calculator 工具，得到结果后用自然语言回答用户。",
    tool_registry=registry,
)

print("回答:", calc_agent.run("请帮我计算 (15 * 8 + 32) / 4 是多少？"))


# === 测试 3：连续对话 + 历史记录 ===
print("\n" + "=" * 50)
print("测试 3：多轮对话 + 查看历史")
print("=" * 50)

print("第一轮回答:", calc_agent.run("再帮我算一下 7 的 4 次方"))
print(f"\n累计历史条数: {len(calc_agent.get_history())}")
print("历史明细:")
for i, m in enumerate(calc_agent.get_history()):
    preview = m.content[:50].replace("\n", " ")
    print(f"  [{i}] {m.role}: {preview}{'...' if len(m.content) > 50 else ''}")
