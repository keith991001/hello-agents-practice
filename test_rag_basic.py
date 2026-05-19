"""8.3 节 RAG demo

阶段 1：把 knowledge_base/ 下每个 markdown 文件灌进 Qdrant
阶段 2：让 Agent 用 RAG 工具回答问题
"""
import os
from dotenv import load_dotenv
from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools import RAGTool

load_dotenv()

# 用独立的 namespace 避免污染别的实验
rag_tool = RAGTool(rag_namespace="ch8_demo")


# ============================================================
# 阶段 1：灌文档
# ============================================================
print("=" * 60)
print("阶段 1: 灌文档进 Qdrant")
print("=" * 60)
kb_dir = "./knowledge_base"
for fname in os.listdir(kb_dir):
    if fname.endswith(".md"):
        fpath = os.path.join(kb_dir, fname)
        print(f"\n→ 灌入 {fname}")
        result = rag_tool.run({
            "action": "add_document",
            "file_path": fpath,
        })
        print(f"  {result}")


# ============================================================
# 中场检查：stats
# ============================================================
print("\n" + "=" * 60)
print("阶段 2: 检查 RAG 索引状态")
print("=" * 60)
stats = rag_tool.run({"action": "stats"})
print(stats)


# ============================================================
# 阶段 3：Agent 用 RAG 工具回答问题
# ============================================================
print("\n" + "=" * 60)
print("阶段 3: Agent 用 RAG 检索回答问题")
print("=" * 60)

llm = HelloAgentsLLM()
registry = ToolRegistry()
registry.register_tool(rag_tool)

agent = SimpleAgent(
    name="文档问答助手",
    llm=llm,
    system_prompt=(
        "你是一个文档问答助手。回答任何问题前都必须先用 rag 工具检索知识库。\n\n"
        "工具调用格式（严格遵守）：\n"
        "  [TOOL_CALL:rag:action=search,query=关键词]\n\n"
        "规则：\n"
        "1. 必须先检索，再基于检索结果回答\n"
        "2. 如果检索没有相关内容，明确说\"知识库里没有这方面的信息\"\n"
        "3. 不要凭空编造或用你自己训练时的知识\n"
        "4. 回答时尽量引用文档原文片段"
    ),
    tool_registry=registry,
)

questions = [
    "Pepabo 的主要服务有哪些？",
    "Pepabo 16 期新人入职后会经过多久的研修？",
    "HTTP PUT 和 PATCH 有什么区别？",
    "Python 的列表推导式怎么写？",  # 故意问知识库里没有的，看 Agent 是否如实承认
]

for q in questions:
    print(f"\n❓ {q}")
    answer = agent.run(q)
    print(f"✅ {answer}")
