"""8.x 节：记忆固化 —— 把短期记忆"沉淀"成长期记忆

人脑睡觉时会把"工作记忆"里重要的部分搬到长期记忆，不重要的丢掉。
MemoryTool.consolidate() 模仿这个过程：按 importance 阈值，
从 from_type 搬到 to_type。

典型路径：
  working → episodic   （事件型经历："今天开了会"）
  working → semantic   （概念型知识："注意力机制的原理"）
  episodic → semantic  （从多次经历中提炼出通用知识）
"""
from dotenv import load_dotenv
from hello_agents.tools import MemoryTool

load_dotenv()

memory_tool = MemoryTool(
    user_id="keith_consolidation",
    memory_types=["working", "episodic", "semantic"],
)

# === Step 1: 灌一批 importance 从 0.2 到 0.9 的工作记忆 ===
print("=" * 60)
print("Step 1: 添加工作记忆（importance 0.2 ~ 0.9）")
print("=" * 60)

memories = [
    ("学习了 Transformer 的多头注意力机制",          0.90, "deep_learning"),
    ("修好了 hello_agents 的 ast.Num 兼容性 bug",    0.85, "engineering"),
    ("解决了 Qdrant 检索结果总为空的问题",            0.90, "engineering"),
    ("今天下午开了项目进展会",                         0.70, "teamwork"),
    ("看了一眼天气预报",                               0.30, "daily"),
    ("喝了一杯咖啡",                                   0.20, "daily"),
]

for content, importance, topic in memories:
    memory_tool.run({
        "action": "add",
        "content": content,
        "memory_type": "working",
        "importance": importance,
        "topic": topic,
    })
    print(f"  + [imp={importance:.2f}] {content}")

print(f"\n📊 固化前统计:\n{memory_tool.run({'action': 'stats'})}")

# === Step 2: 第一次固化 working → episodic, 阈值 0.8 ===
# 只有 imp >= 0.8 的记忆会被搬走；它们在 episodic 里多了"consolidated"标记
print("\n" + "=" * 60)
print("Step 2: 固化 working → episodic (threshold=0.8)")
print("=" * 60)

result = memory_tool.run({
    "action": "consolidate",
    "from_type": "working",
    "to_type": "episodic",
    "importance_threshold": 0.8,
})
print(f"固化结果: {result}")
print(f"\n📊 固化后统计:\n{memory_tool.run({'action': 'stats'})}")

# === Step 3: 看 episodic 里到底搬进了什么 ===
print("\n" + "=" * 60)
print("Step 3: 查看 episodic 内容")
print("=" * 60)
print(memory_tool.run({
    "action": "search",
    "query": "",          # 空 query = 列出所有
    "memory_type": "episodic",
    "limit": 10,
}))

# === Step 4: 另一条路径 — 工程类高分记忆同时升格成 semantic 知识 ===
# 实际系统里可以按 topic / metadata 分流，比如：
#   - topic in {"deep_learning", "engineering"} → semantic（沉淀为知识）
#   - 其他高分 → episodic（保留为经历）
# 这里只演示 API，简单按 threshold 切。
print("\n" + "=" * 60)
print("Step 4: 固化 working → semantic (threshold=0.85)")
print("=" * 60)
result = memory_tool.run({
    "action": "consolidate",
    "from_type": "working",
    "to_type": "semantic",
    "importance_threshold": 0.85,
})
print(f"固化结果: {result}")
print(f"\n📊 最终统计:\n{memory_tool.run({'action': 'stats'})}")

# === Step 5: 验证 — 跨类型语义检索 ===
# 固化后，同一个 query 能从 episodic + semantic 都召回。
# 不指定 memory_type 就是全类型搜索。
print("\n" + "=" * 60)
print("Step 5: 跨类型检索 'Transformer 注意力'")
print("=" * 60)
print(memory_tool.run({
    "action": "search",
    "query": "Transformer 注意力",
    "limit": 5,
}))
