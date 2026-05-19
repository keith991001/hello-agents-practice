"""绕开 LLM 直接看 RAG 搜什么 —— 排查到底是 RAG 没搜到对的，还是 LLM 看到对的但幻觉"""
from dotenv import load_dotenv
from hello_agents.tools import RAGTool

load_dotenv()

rag_tool = RAGTool(rag_namespace="ch8_demo")

queries = [
    "Pepabo 主要服务",
    "Pepabo 16 期 研修 时长",
    "HTTP PUT PATCH 区别",
]

for q in queries:
    print("\n" + "=" * 60)
    print(f"查询: {q}")
    print("=" * 60)
    result = rag_tool.run({"action": "search", "query": q, "top_k": 3})
    print(result)
