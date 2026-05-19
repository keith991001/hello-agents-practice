"""清掉旧索引，用小 chunk_size 重新灌入，再问"""
import os
from dotenv import load_dotenv
from hello_agents.tools import RAGTool

load_dotenv()

rag_tool = RAGTool(rag_namespace="ch8_demo")


# ============================================================
# 阶段 1：清空旧索引
# ============================================================
print("=" * 60)
print("阶段 1: 清空当前 namespace 的所有索引")
print("=" * 60)
result = rag_tool.run({"action": "clear"})
print(result)


# ============================================================
# 阶段 2：用 chunk_size=250 重新灌
# ============================================================
print("\n" + "=" * 60)
print("阶段 2: 重新灌入文档，chunk_size=250（小切片）")
print("=" * 60)
kb_dir = "./knowledge_base"
for fname in os.listdir(kb_dir):
    if fname.endswith(".md"):
        fpath = os.path.join(kb_dir, fname)
        print(f"\n→ 灌入 {fname}")
        result = rag_tool.run({
            "action": "add_document",
            "file_path": fpath,
            "chunk_size": 250,
            "chunk_overlap": 50,
        })
        print(result)


# ============================================================
# 阶段 3：用 ask 重新问
# ============================================================
print("\n" + "=" * 60)
print("阶段 3: 重新问答")
print("=" * 60)

questions = [
    "Pepabo 的主要服务有哪些？请逐一列举。",
    "Pepabo 16 期新人入职后会经过多久的研修？研修内容是什么？",
    "HTTP PUT 和 PATCH 有什么区别？",
]

for q in questions:
    print("\n" + "─" * 60)
    print(f"❓ {q}")
    print("─" * 60)
    result = rag_tool.run({"action": "ask", "question": q, "top_k": 5})
    print(result)
