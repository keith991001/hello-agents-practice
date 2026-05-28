"""8.6 节：完整 RAG 流水线 —— 摄取、分块、检索、问答全链路

test_rag_basic 已经跑通最简流程（add_document → ask）。
本节展开"完整管道"的关键参数和高级检索：

  阶段 1: 摄取（ingest） — 文档 → MarkItDown 解析 → 分块
  阶段 2: 索引（index）  — chunk → embedding → 落 Qdrant
  阶段 3: 检索（retrieval）— query → 向量相似度搜索 → top-k chunks
  阶段 4: 生成（generation）— chunks + query → LLM → 答案

高级检索技巧（这是 08 章独有的）：
  - MQE  (Multi-Query Expansion): 把 1 个问题改写成 N 个语义相近的问题, 召回更全
  - HyDE (Hypothetical Document Embeddings): 让 LLM 先"假装"写答案, 再用这个假答案去检索

## 前置条件
- .env 已配 LLM / DashScope / Qdrant
- `knowledge_base/` 目录有至少 1 个 .md 文件（默认仓库里有 `pepabo_intro.md` / `web_basics.md`）
- 不依赖 `ch8_demo` collection —— 本文件用独立的 `ch8_pipeline` namespace

## 跑完会产生什么
- Qdrant 里多一个 `rag_namespace="ch8_pipeline"` 的 collection
- stdout 输出 3 档检索对比（基础 / MQE / HyDE）+ 最终端到端答案
- 注意: 开 MQE/HyDE 后 LLM 调用次数 ×3~5, 耗时显著增加（你会等几十秒）

## 下一步
推荐接着跑 `11_qa_assistant.py` —— 终章作品，把 Memory + RAG + Agent 全封装成一个类。

## 已知 API 不确定点
`enable_mqe` / `enable_hyde` flag 是从官方 11 号文件抄的，
如果你的 hello-agents 版本不识别这些参数，可以删掉，回退到基础检索。
"""
import os
from dotenv import load_dotenv
from hello_agents.tools import RAGTool

load_dotenv()

# 用独立 namespace 避免污染 ch8_demo 那个 collection
rag_tool = RAGTool(rag_namespace="ch8_pipeline")

# === Phase 1: 摄取 — 演示不同 chunk_size 的影响 ===
# chunk_size 太大: 一个 chunk 信息密度低, 检索时召回的内容包含太多噪声
# chunk_size 太小: 切碎了语义, 单个 chunk 不足以回答完整问题
# 实际经验: 500~1200 字符 + 100~200 overlap 是大多数中文文档的甜蜜区
print("=" * 60)
print("Phase 1: 摄取文档（chunk_size=800, overlap=150）")
print("=" * 60)

kb_dir = "./knowledge_base"
if not os.path.isdir(kb_dir):
    print(f"⚠️  {kb_dir} 不存在，请先确认知识库目录")
else:
    for fname in os.listdir(kb_dir):
        if fname.endswith(".md"):
            result = rag_tool.run({
                "action": "add_document",
                "file_path": os.path.join(kb_dir, fname),
                "chunk_size": 800,
                "chunk_overlap": 150,
            })
            print(f"  ✓ {fname} → {result}")

# === Phase 2: 索引状态检查 ===
print("\n" + "=" * 60)
print("Phase 2: 索引状态")
print("=" * 60)
print(rag_tool.run({"action": "stats"}))

# === Phase 3: 三档检索对比 — 基础 vs MQE vs HyDE ===
# 用同一个问题，三种检索模式各跑一次，对比召回的 chunk 质量。
# 实际工程里 MQE / HyDE 会显著增加 LLM 调用次数 & 延迟，要权衡。
print("\n" + "=" * 60)
print("Phase 3: 三档检索对比")
print("=" * 60)

question = "Pepabo 16 期新人研修的内容大概是什么？"

print(f"\n问题: {question}")

# 3a. 基础检索 — 直接拿原问题去向量搜
print("\n--- [a] 基础检索（直接向量搜索）---")
print(rag_tool.run({
    "action": "search",
    "query": question,
    "limit": 3,
}))

# 3b. MQE 检索 — LLM 先把问题改写成 3~5 个相关问题, 各自检索后合并
print("\n--- [b] MQE 检索（多查询扩展）---")
print(rag_tool.run({
    "action": "search",
    "query": question,
    "limit": 3,
    "enable_mqe": True,
}))

# 3c. HyDE 检索 — LLM 先"假装"写一段答案, 用这个假答案的 embedding 去检索
# 思路: 问题和答案的 embedding 不在同一片空间, 假答案更接近真答案的位置
print("\n--- [c] HyDE 检索（假设答案 embedding）---")
print(rag_tool.run({
    "action": "search",
    "query": question,
    "limit": 3,
    "enable_hyde": True,
}))

# === Phase 4: 端到端问答 — 把高级检索打开, 一次性出答案 ===
print("\n" + "=" * 60)
print("Phase 4: 端到端问答（MQE + HyDE 全开）")
print("=" * 60)
answer = rag_tool.run({
    "action": "ask",
    "question": question,
    "top_k": 5,
    "enable_advanced_search": True,
    "enable_mqe": True,
    "enable_hyde": True,
})
print(f"\n📝 答案:\n{answer}")
