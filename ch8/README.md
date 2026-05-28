# 第 8 章：记忆与检索（Memory & RAG）

> **如果你是 Claude Code 第一次进来这个目录**：
> - 读这份 README 了解全章结构
> - 检查 `.env` 是否配齐（见根目录 README）
> - 按下方"推荐学习路径"和用户一起跑代码

## 文件分类

| 类别 | 文件命名 | 目的 |
|---|---|---|
| 📘 **概念演示** | `06_*.py` / `08_*.py` / `10_*.py` / `11_*.py` | 与官方 `datawhalechina/hello-agents/code/chapter8/` 编号对齐，每个文件对应一个核心概念 |
| 🔧 **调试 / 验证** | `test_*.py` / `debug_*.py` / `smoke_test_*.py` / `diagnose_*.py` | 自己写的工具，确认底层 API / 云服务能用 |

## 推荐学习路径

### Phase 1: 基础设施验证（先确认能跑）

| 顺序 | 文件 | 干嘛 |
|---|---|---|
| 1 | `smoke_test_ch8.py` | 一次跑通 DeepSeek + DashScope + Qdrant + Neo4j 四个云服务 |
| 2 | `diagnose_neo4j.py` | （选）单独诊断 Neo4j 连接 |

### Phase 2: Memory 系统

| 顺序 | 文件 | 学什么 |
|---|---|---|
| 3 | `test_memory_direct.py` | 不走 LLM，直接调 `MemoryTool.run({"action": "add"/"search"})` |
| 4 | `test_memory_basic.py` | Agent 挂 MemoryTool，跨调用记得用户姓名 |
| 5 | `test_memory_persist.py store` 然后 `test_memory_persist.py recall` | 验证记忆**真的**写进了云端 Qdrant（两次独立进程运行）|
| 6 | **`06_memory_consolidation.py`** ⭐ | **概念**：短期记忆按 importance 自动固化到长期记忆 |

### Phase 3: RAG 系统

| 顺序 | 文件 | 学什么 |
|---|---|---|
| 7 | `test_rag_basic.py` | 灌 `knowledge_base/*.md` 到 Qdrant，Agent 用 RAG 工具问答（**也为后续 08 准备 `ch8_demo` namespace**）|
| 8 | `test_rag_ask.py` | 对比 `action=ask`（完整答案）vs `action=search`（chunk 列表）|
| 9 | `test_rag_rechunked.py` | chunk_size 调优实验（200~800 字符对召回的影响）|
| 10 | `debug_rag.py` | 检索质量定位（看 chunk 真的命中了什么）|

### Phase 4: 概念演示（跟官方对齐）

| 顺序 | 文件 | 学什么 | 前置 |
|---|---|---|---|
| 11 | **`08_agent_tool_integration.py`** ⭐ | 一个 Agent 同时挂 Memory + RAG，LLM 自己路由 | 第 7 步已灌好 `ch8_demo` |
| 12 | **`10_rag_pipeline_complete.py`** ⭐ | 完整 RAG 管道 + MQE / HyDE 高级检索 | `knowledge_base/` 有 `.md` 文件 |
| 13 | **`11_qa_assistant.py`** ⭐ | **终章作品**：`PDFLearningAssistant` 封装类 + CLI 交互 | 需要一份 PDF（或改成支持 .md，见下） |

## 11 号文件的特别说明

`11_qa_assistant.py` 默认 `load` 命令期待 PDF 路径，但本仓库的 `knowledge_base/` 只有 `.md` 文件。两种解决：

1. **临时找一份 PDF**：随便下载本入门书 PDF 放到目录里，`load /path/to/foo.pdf`
2. **改代码支持 .md**：把 `load_document()` 里的 `add_document` 直接传 `.md` 路径（hello_agents 的 RAGTool 用 MarkItDown 解析，理论上也吃 .md）

## 编号对照官方教程

| 你这里 | 官方文件 | 官方文档章节 |
|---|---|---|
| `06_memory_consolidation.py` | `06_Memory_Consolidation_Demo.py` | 8.4 记忆固化 |
| `08_agent_tool_integration.py` | `08_Agent_Tool_Integration.py` | 8.5 Agent 集成 |
| `10_rag_pipeline_complete.py` | `10_RAG_Pipeline_Complete.py` | 8.6 完整 RAG |
| `11_qa_assistant.py` | `11_Q&A_Assistant.py` | 8.7 应用案例 |

> **跳过的官方文件**（`01`-`05`、`07`、`09`）：内容已经在 `test_*.py` 里以"验证 + debug"的方式覆盖了，不重复实现演示。

## 已知 API 不确定点

我（写这些文件的 Claude）没有在本地跑过 `06/08/10/11`，以下三个 API 用法是基于官方 demo 推断的，可能需要根据实际报错调整：

1. `MemoryTool(memory_types=["working", "episodic", "semantic"])` — 该 kwarg 是否存在
2. `RAGTool.run({"action": "search", "enable_mqe": True, "enable_hyde": True})` — 这些 flag 是否被 0.2.x 版本支持
3. `MemoryTool.run({"action": "consolidate", "from_type": ..., "to_type": ..., "importance_threshold": 0.8})` — `consolidate` action 是否实现

跑出错时 grep 现有 `test_*.py` 看人家是怎么调的，或者去 `hello-agents` 源码翻 `MemoryTool` / `RAGTool` 类定义。
