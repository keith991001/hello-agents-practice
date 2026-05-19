"""第八章冒烟测试 —— 验证三个云服务都能连通

每个服务发一个最简请求，把问题暴露在最早阶段。
都 ✓ 了再进 memory / RAG 实战。
"""
import os
from dotenv import load_dotenv

load_dotenv()


def banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ============================================================
# 1. DeepSeek（第七章已通，再确认一次）
# ============================================================
banner("1. DeepSeek LLM")
try:
    from hello_agents import HelloAgentsLLM
    llm = HelloAgentsLLM()
    print(f"  provider={llm.provider}, model={llm.model}")
    resp = llm.invoke([{"role": "user", "content": "用 5 个字回答：今天天气"}])
    print(f"  ✓ 响应: {resp}")
except Exception as e:
    print(f"  ❌ 失败: {e}")


# ============================================================
# 2. DashScope Embedding（国际版 OpenAI 兼容端点）
# ============================================================
banner("2. DashScope Embedding (OpenAI-compatible)")
try:
    from openai import OpenAI

    embed_client = OpenAI(
        api_key=os.getenv("EMBED_API_KEY"),
        base_url=os.getenv("EMBED_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    )
    result = embed_client.embeddings.create(
        model="text-embedding-v3",
        input="你好，世界",
    )
    embedding = result.data[0].embedding
    print(f"  ✓ 向量维度: {len(embedding)}（应为 1024）")
    print(f"  ✓ 前 5 维: {[round(x, 4) for x in embedding[:5]]}")
except Exception as e:
    print(f"  ❌ 失败: {e}")


# ============================================================
# 3. Qdrant 向量数据库 —— 试连接 + 列已有集合
# ============================================================
banner("3. Qdrant 向量数据库")
try:
    from qdrant_client import QdrantClient
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        timeout=30,
    )
    collections = client.get_collections().collections
    names = [c.name for c in collections]
    print(f"  ✓ 已连接，目前有 {len(names)} 个 collection: {names or '(空)'}")
except Exception as e:
    print(f"  ❌ 失败: {e}")


# ============================================================
# 4. Neo4j 图数据库 —— 试连接 + 跑一个最简 Cypher 查询
# ============================================================
banner("4. Neo4j 图数据库")
try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
    )
    with driver.session() as session:
        result = session.run("RETURN '你好 Neo4j' AS greeting").single()
        print(f"  ✓ 已连接，查询结果: {result['greeting']}")
    driver.close()
except Exception as e:
    print(f"  ❌ 失败: {e}")


print("\n" + "=" * 60)
print("  全部 ✓ 才能进入 8.2 节实战")
print("=" * 60)
