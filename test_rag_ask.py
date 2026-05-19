"""用 RAGTool.ask 做问答 —— 框架内部一次性完成"检索 + 生成"，比 SimpleAgent 走 search 更接地气"""
from dotenv import load_dotenv
from hello_agents.tools import RAGTool

load_dotenv()

rag_tool = RAGTool(rag_namespace="ch8_demo")

questions = [
    "Pepabo 的主要服务有哪些？请按文档列举。",
    "Pepabo 16 期新人入职后会经过多久的研修？研修内容大概包括什么？",
    "HTTP PUT 和 PATCH 有什么区别？",
    "Python 的列表推导式怎么写？",
]

for q in questions:
    print("\n" + "=" * 60)
    print(f"❓ {q}")
    print("=" * 60)
    result = rag_tool.run({
        "action": "ask",
        "question": q,
        "top_k": 3,
    })
    print(result)
