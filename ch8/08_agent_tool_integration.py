"""8.x 节：Agent + Memory + RAG 集成 —— 把两个工具挂在同一个 Agent 上

前面 test_memory_basic 演示了 Agent + Memory，test_rag_basic 演示了 Agent + RAG。
本节关键：**两个工具同时挂到一个 Agent**，让 LLM 自己决定什么时候用哪个。

工具注册的设计哲学：
  - ToolRegistry 是一个工具的"总线"，Agent 拿到 registry 就能用上面所有工具
  - 每个工具都暴露同样的 .run({"action": ..., ...}) 接口（统一协议）
  - LLM 通过 system_prompt 知道工具的能力，用 [TOOL_CALL:name:action=...,...] 调用

典型协同场景：
  - 用户告诉 Agent 一条事实  →  MemoryTool 存
  - 用户问文档里的内容       →  RAGTool 查
  - 用户问"我刚才学了什么"   →  MemoryTool 查
"""
from dotenv import load_dotenv
from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools import MemoryTool, RAGTool

load_dotenv()

# === Setup：两个工具 + 一个 Agent ===
memory_tool = MemoryTool(user_id="keith_integration")
rag_tool = RAGTool(rag_namespace="ch8_demo")   # 复用 test_rag_basic 已经灌好的知识库

registry = ToolRegistry()
registry.register_tool(memory_tool)
registry.register_tool(rag_tool)

# === 工具注册机制小探 ===
print("=" * 60)
print("工具注册总线状态")
print("=" * 60)
print(f"已注册工具: {list(registry._tools.keys())}")
for name, tool in registry._tools.items():
    print(f"  - {name}: {type(tool).__name__}")

# === 创建一个能同时用两个工具的 Agent ===
llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="集成助手",
    llm=llm,
    system_prompt=(
        "你是一个有记忆 + 能查知识库的助手。你有两个工具：\n\n"
        "## memory（个人事实/经历）\n"
        "  存：[TOOL_CALL:memory:action=add,content=事实,memory_type=episodic]\n"
        "  查：[TOOL_CALL:memory:action=search,query=关键词]\n\n"
        "## rag（外部知识库）\n"
        "  查：[TOOL_CALL:rag:action=search,query=关键词]\n\n"
        "## 决策规则\n"
        "1. 用户告诉你关于他自己的事 → memory.add\n"
        "2. 用户问关于他自己之前说过的事 → memory.search\n"
        "3. 用户问通用知识/文档内容 → rag.search\n"
        "4. 不确定时优先 rag.search，再用 memory.search 补充上下文"
    ),
    tool_registry=registry,
)

# === Scenario 1：教 Agent 一个个人事实 → 走 memory ===
print("\n" + "=" * 60)
print("Scenario 1: 教 Agent 个人信息（应走 memory.add）")
print("=" * 60)
r1 = agent.run("我叫 Keith，最近在学 hello_agents 框架，特别关心 Memory 模块的实现。")
print(f"\n回答: {r1}")

# === Scenario 2：问知识库内容 → 走 rag ===
print("\n" + "=" * 60)
print("Scenario 2: 问知识库（应走 rag.search）")
print("=" * 60)
r2 = agent.run("Pepabo 的主要服务有哪些？")
print(f"\n回答: {r2}")

# === Scenario 3：组合问题 → 两个工具都要用 ===
# 这是 08 的高潮：让 Agent 自己决定先查 memory（我是谁？我关心什么？）
# 再查 rag（基于我的关心，文档里有什么相关？）
print("\n" + "=" * 60)
print("Scenario 3: 复合问题（应同时调 memory + rag）")
print("=" * 60)
r3 = agent.run("你还记得我在学什么吗？知识库里有没有相关内容可以推荐？")
print(f"\n回答: {r3}")

# === 收尾：两个系统各自的状态 ===
print("\n" + "=" * 60)
print("两个工具的最终状态")
print("=" * 60)
print(f"\n[Memory stats]\n{memory_tool.run({'action': 'stats'})}")
print(f"\n[RAG stats]\n{rag_tool.run({'action': 'stats'})}")
