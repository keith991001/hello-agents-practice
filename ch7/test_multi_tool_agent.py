"""综合演示：ReActAgent 同时使用 Calculator + Wikipedia 两个工具

任务：求"光速 × 1 秒等于多少千米"
预期推理路径：
  Step 1: 想要光速 → wikipedia 搜"光速"
  Step 2: 从搜索结果里提取数字 → calculator 计算
  Step 3: Finish 给最终答案
"""
from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM, ToolRegistry
from safe_calculator import SafeCalculatorTool
from wikipedia_tool import WikipediaSearchTool
from my_react_agent import MyReActAgent

load_dotenv()

llm = HelloAgentsLLM()

# 同时注册两个工具
registry = ToolRegistry()
registry.register_tool(SafeCalculatorTool())
registry.register_tool(WikipediaSearchTool(language="zh"))

print("\n📋 注册的工具列表：")
print(registry.get_tools_description())

agent = MyReActAgent(
    name="多工具研究员",
    llm=llm,
    tool_registry=registry,
    max_steps=6,  # 多工具任务给多点空间
)

# 一个需要"先搜索 + 再计算"的题
answer = agent.run(
    "光速大约是多少米每秒？请先查证一下，然后告诉我光在 1 微秒（10^-6 秒）内走多少米。"
)

print(f"\n{'=' * 60}")
print(f"最终答案：{answer}")
