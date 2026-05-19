"""8.2 节 30 秒体验：让 Agent 拥有记忆

跑两次"会话"，第二次能想起第一次的事 —— 跨调用的记忆能力。
"""
from dotenv import load_dotenv
from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools import MemoryTool

load_dotenv()

llm = HelloAgentsLLM()

# 创建记忆工具 —— user_id 用于区分不同用户的记忆
memory_tool = MemoryTool(user_id="keith_001")

# 注册到工具表
registry = ToolRegistry()
registry.register_tool(memory_tool)

# 创建 Agent，挂上 memory 工具
agent = SimpleAgent(
    name="有记忆的助手",
    llm=llm,
    system_prompt=(
        "你是一个有记忆能力的 AI 助手。"
        "遇到用户告诉你的个人信息（姓名、偏好、专业方向等），"
        "要主动用 memory 工具存起来。"
        "用户问起过往的事时，主动用 memory 工具检索。"
    ),
    tool_registry=registry,
)

print("\n" + "=" * 60)
print("第一轮对话：告诉 Agent 一些事实")
print("=" * 60)
r1 = agent.run("你好，我叫 Keith，是 Pepabo 16 期新人，在学 Python 和 Web 开发。")
print(f"\n回答: {r1}")

print("\n" + "=" * 60)
print("第二轮对话：问起之前的事")
print("=" * 60)
r2 = agent.run("你还记得我叫什么名字、在做什么吗？")
print(f"\n回答: {r2}")
