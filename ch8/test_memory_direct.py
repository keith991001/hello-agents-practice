"""绕开 LLM 直接调用 MemoryTool —— 排查是 LLM 没调工具，还是工具本身有问题

逻辑：
  1. 手动调 memory.add 存 3 条事实
  2. 列出存了哪些
  3. 手动调 memory.search 看能否取回
"""
from dotenv import load_dotenv
from hello_agents.tools import MemoryTool

load_dotenv()

tool = MemoryTool(user_id="keith_direct_test")

print("=" * 60)
print("1. 直接 add：把 3 条事实写入")
print("=" * 60)
for content in [
    "我最喜欢的颜色是青色",
    "我养了一只叫 Mochi 的猫",
    "我的生日是 5 月 19 日",
]:
    result = tool.run({"action": "add", "content": content, "memory_type": "episodic"})
    print(f"  → {result}")

print("\n" + "=" * 60)
print("2. stats：看一下 episodic memory 里有多少条")
print("=" * 60)
result = tool.run({"action": "stats"})
print(result)

print("\n" + "=" * 60)
print("3. search：用语义检索把刚才的事实找出来")
print("=" * 60)
for query in ["我喜欢什么颜色", "我的宠物", "我的生日"]:
    print(f"\n  查询: {query}")
    result = tool.run({"action": "search", "query": query})
    print(f"  ← {result}")
