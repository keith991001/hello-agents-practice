"""测试记忆的真正持久化 —— 必须用两次独立的程序运行

用法：
  阶段 1：python test_memory_persist.py store
  阶段 2：python test_memory_persist.py recall

阶段之间程序完全退出。如果阶段 2 还能取回阶段 1 存的事实，
说明记忆真的写进了云端 Qdrant / Neo4j，而不是只活在内存。
"""
import sys
from dotenv import load_dotenv
from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools import MemoryTool

load_dotenv()

if len(sys.argv) < 2 or sys.argv[1] not in ("store", "recall"):
    print("用法: python test_memory_persist.py [store|recall]")
    sys.exit(1)

stage = sys.argv[1]

llm = HelloAgentsLLM()
memory_tool = MemoryTool(user_id="keith_persist_demo")  # 用专门的 user_id 避免污染前面的测试

registry = ToolRegistry()
registry.register_tool(memory_tool)

agent = SimpleAgent(
    name="持久化测试助手",
    llm=llm,
    system_prompt=(
        "你有 memory 工具可以存取信息。\n\n"
        "## 工具调用格式（严格遵守）\n"
        "存储事实（必须用 episodic 才能跨会话持久化）：\n"
        "  [TOOL_CALL:memory:action=add,content=事实文本,memory_type=episodic]\n\n"
        "检索记忆：\n"
        "  [TOOL_CALL:memory:action=search,query=你要查的关键词]\n\n"
        "## 行为规则\n"
        "1. 用户告诉你事实（姓名、偏好、属性）→ 必须用 action=add + memory_type=episodic 存\n"
        "2. 用户问起过去的事 → 必须用 action=search 取，基于结果回答\n"
        "3. 不要凭空编造或客套式承认已记住——必须真的调用工具"
    ),
    tool_registry=registry,
)

if stage == "store":
    print("📥 STORE 阶段：把事实写进云端记忆")
    print("=" * 60)
    answer = agent.run(
        "请记住：我最喜欢的颜色是青色，我养了一只叫 Mochi 的猫，我的生日是 5 月 19 日。"
    )
    print(f"\n回答: {answer}")
    print("\n✓ STORE 完成。现在退出程序，重新跑：")
    print("    python test_memory_persist.py recall")

elif stage == "recall":
    print("📤 RECALL 阶段：在全新程序里查问记忆")
    print("=" * 60)
    answer = agent.run(
        "你还记得我最喜欢的颜色吗？我养的猫叫什么？我生日哪天？"
    )
    print(f"\n回答: {answer}")
