# hello-agents-tutorial

从零跟着 datawhalechina/hello-agents 教材构建的 Agent 学习项目。涵盖 **第 7 章（构建 Agent 框架）** 和 **第 8 章（记忆与 RAG）**。

## 如何用这个 repo 学习

这个 repo 设计成 **"未来的我 + Claude Code 协作"** 模式 —— 任何时候 clone 下来，配好 .env 后让 CC 读项目，就能自动找到学习路径。

- **第 7 章**：已学完，代码全部跑通 → 直接读 `ch7/` 复习即可
- **第 8 章**：
  - **`ch8/test_*.py / debug_*.py / smoke_test_*.py`** —— 自己写的诊断脚本（学第 8 章时一边踩坑一边写的）
  - **`ch8/06_*.py / 08_*.py / 10_*.py / 11_*.py`** —— 跟官方教程对齐的 **概念演示**（编号匹配 `datawhalechina/hello-agents/code/chapter8/` 里的编号）
  - 完整学习路径见 [ch8/README.md](ch8/README.md)

## 项目结构

```
hello-agents-tutorial/
├── ch7/                   # 第 7 章：Agent 框架核心
├── ch8/                   # 第 8 章：记忆与 RAG
├── knowledge_base/        # ch8 用的测试语料（Markdown）
├── memory_data/           # ch8 自动生成的 SQLite 缓存（.gitignored）
├── .env                   # API key（.gitignored）
├── .env.example
├── requirements.txt
└── README.md
```

## 第 7 章成果（ch7/）

- **LLM 客户端扩展** (`my_llm.py`) — 继承 `HelloAgentsLLM` 添加干净流式输出和 token 追踪
- **SimpleAgent + 工具调用** (`my_simple_agent.py`) — Prompt 模板嵌入式工具调用
- **ReActAgent** (`my_react_agent.py`) — Reasoning + Acting 多步推理，带 markdown 兼容 parser
- **Python 3.14 兼容计算器** (`safe_calculator.py`) — 修复框架自带 calculator 的 `ast.Num` bug
- **Wikipedia 搜索工具** (`wikipedia_tool.py`) — 调用维基开放 REST API
- **多工具协同 demo** (`test_multi_tool_agent.py`) — ReAct + 计算器 + 维基百科组合

## 第 8 章成果（ch8/）

### 📘 概念演示（跟官方教程章节对齐）

按编号顺序读 / 跑，每个文件对应一个教程概念：

- **`06_memory_consolidation.py`** — 记忆固化（working → episodic/semantic 智能迁移）
- **`08_agent_tool_integration.py`** — 一个 Agent 同时挂载 Memory + RAG 两个工具，LLM 自主路由
- **`10_rag_pipeline_complete.py`** — 完整 RAG 流水线 + MQE/HyDE 高级检索对比
- **`11_qa_assistant.py`** — **终章作品**：`PDFLearningAssistant` 类（Memory + RAG + Agent 封装）+ CLI 交互

### 🔧 自己写的诊断与验证脚本

学第 8 章时一边写一边踩坑的，帮你理解底层在做什么：

- **冒烟测试** (`smoke_test_ch8.py`) — 一次性验证 DeepSeek / DashScope / Qdrant / Neo4j 四个云服务连通
- **记忆系统 demo** (`test_memory_basic.py` / `test_memory_persist.py`) — 跨进程的对话记忆，使用 Qdrant 向量库做语义检索
- **直接调用工具诊断** (`test_memory_direct.py`) — 绕过 LLM 验证 MemoryTool 底层是否工作
- **RAG 系统** (`test_rag_basic.py` / `test_rag_ask.py` / `test_rag_rechunked.py`) — 文档问答，含 chunk_size 调优实验
- **诊断脚本** (`diagnose_neo4j.py` / `debug_rag.py`) — 定位云服务和检索质量问题

## 环境要求

- Python ≥ 3.10
- DeepSeek API key（LLM 推理）
- 第 8 章额外：DashScope（embedding）、Qdrant Cloud（向量库）、Neo4j Aura（图谱）

## 复现步骤

```bash
# 1. clone 后建虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 第 8 章还需要下载 spaCy 中文 / 英文模型
python -m spacy download zh_core_web_sm
python -m spacy download en_core_web_sm

# 2. 配置 API key
cp .env.example .env       # 然后编辑 .env 填入你的 sk-...

# 3. 跑示例（都从项目根目录运行）
# --- 第 7 章 ---
python ch7/quick_test.py                  # 验证 LLM 调用
python ch7/test_my_simple_agent.py        # SimpleAgent + 工具调用
python ch7/test_my_react_agent.py         # ReAct
python ch7/test_advanced_agents.py        # Reflection / Plan-Solve / Function Calling
python ch7/test_multi_tool_agent.py       # 多工具协同

# --- 第 8 章：先验证基础设施 ---
python ch8/smoke_test_ch8.py              # 云基础设施冒烟测试
python ch8/test_memory_direct.py          # 直接验证 memory 工具
python ch8/test_memory_persist.py store   # 跨进程持久化 - 写
python ch8/test_memory_persist.py recall  # 跨进程持久化 - 读
python ch8/test_rag_basic.py              # 灌文档到 ch8_demo 知识库（08/10 都依赖这一步）
python ch8/test_rag_ask.py                # RAG 问答

# --- 第 8 章：概念演示（跟官方教程对齐，推荐学习顺序）---
python ch8/06_memory_consolidation.py     # 短期 → 长期记忆固化
python ch8/08_agent_tool_integration.py   # Agent + Memory + RAG 集成（依赖前面的 ch8_demo 已灌好）
python ch8/10_rag_pipeline_complete.py    # 完整 RAG 管道 + MQE/HyDE
python ch8/11_qa_assistant.py             # 终章作品：PDFLearningAssistant 类 + CLI
```

## 踩过的坑（学习记录）

### 第 7 章

| 问题 | 修复 |
|---|---|
| TextEdit 富文本模式给 .py 加前导空格 → `IndentationError` | 用 `cat > file << 'EOF'` heredoc 或 VS Code |
| `.gitignore` 缩进失效 → API key 没被忽略 | `git check-ignore -v .env` 验证 |
| `provider="auto"` 是非空字符串，绕过了父类的 `or` fallback | 默认值改成 `None` |
| 框架内置 calculator 在 Python 3.14 用 `ast.Num` 报错 | 写 `SafeCalculatorTool` 绕开 |
| `think` / `stream_invoke` 自己内部 print → 重复输出 | 用非流式 `invoke`，或 `clean_stream` 直接调底层 client |
| ReAct parser 正则不认 markdown 粗体 `**Thought:**` | override `_parse_output` 让正则容忍 `\*{0,2}` |

### 第 8 章

| 问题 | 修复 |
|---|---|
| `pip install hello-agents[all]` 没装齐 dashscope / qdrant-client / neo4j | 手动 `pip install dashscope qdrant-client neo4j` |
| DashScope 国内 SDK 端点 ≠ 国际版（新加坡） | 用 OpenAI SDK 兼容端点 `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Neo4j Aura Free 默认数据库名是 instance ID 而非 `neo4j` | `SHOW DATABASES` 实测后在 .env 设 `NEO4J_DATABASE=<id>` |
| qdrant-client 1.13+ 删了 `search()` 方法 → hello-agents 0.2.0 调用挂了 | 降级到 `qdrant-client<1.13` |
| `MemoryTool.add` 默认存 working memory（纯内存，进程退出即灭） | 显式传 `memory_type=episodic` 才进 Qdrant |
| RAG chunk_size=800（默认） + 1000 字 markdown → 单 chunk 截断 | chunk_size 调到 200-300 强制切碎 |
| RAG `search` action 返回截断预览（~250 字），LLM 看到摘要就幻觉 | 改用 `ask` action（内部处理完整 chunk + grounding prompt） |
| git rebase 里 `--ours` 跟 merge 模式含义相反 | rebase 时保留本地用 `--theirs`（仍然小心 ours/theirs 陷阱） |

## 学习目标完成情况

### 第 7 章
- [x] 7.2 扩展 HelloAgentsLLM（继承 + super + override）
- [x] 7.3 理解 Message / Config / Agent 基类（抽象基类 + DTO 模式）
- [x] 7.4.1 SimpleAgent + 工具调用
- [x] 7.4.2 ReActAgent
- [x] 7.4.3-5 Reflection / Plan-Solve / Function Calling 范式
- [x] 7.5 工具系统 + 自定义工具

### 第 8 章
- [x] 8.1 云基础设施搭建（Qdrant / Neo4j / DashScope）
- [x] 8.2 Memory 系统（working / episodic / semantic 三种类型 + 跨进程持久化验证）
- [x] 8.3 RAG 系统（文档索引、向量检索、ask vs search、chunk 调优）
- [x] 8.4 记忆固化（`06_memory_consolidation.py`）
- [x] 8.5 Agent + 工具集成（`08_agent_tool_integration.py`）
- [x] 8.6 完整 RAG 管道 + MQE/HyDE（`10_rag_pipeline_complete.py`）
- [x] 8.7 终章作品：智能文档问答助手（`11_qa_assistant.py`）

## License

仅供学习使用。基于 [datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents) 教材。
