# hello-agents-tutorial

从零跟着 datawhalechina/hello-agents 教材构建的 Agent 学习项目。涵盖 **第 7 章（构建 Agent 框架）** 和 **第 8 章（记忆与 RAG）**。

## 第 7 章成果

- **LLM 客户端扩展** (`my_llm.py`) — 继承 `HelloAgentsLLM` 添加干净流式输出和 token 追踪
- **SimpleAgent + 工具调用** (`my_simple_agent.py`) — Prompt 模板嵌入式工具调用
- **ReActAgent** (`my_react_agent.py`) — Reasoning + Acting 多步推理，带 markdown 兼容 parser
- **Python 3.14 兼容计算器** (`safe_calculator.py`) — 修复框架自带 calculator 的 `ast.Num` bug
- **Wikipedia 搜索工具** (`wikipedia_tool.py`) — 调用维基开放 REST API
- **多工具协同 demo** (`test_multi_tool_agent.py`) — ReAct + 计算器 + 维基百科组合

## 第 8 章成果

- **冒烟测试** (`smoke_test_ch8.py`) — 一次性验证 DeepSeek / DashScope / Qdrant / Neo4j 四个云服务连通
- **记忆系统 demo** (`test_memory_basic.py` / `test_memory_persist.py`) — 跨进程的对话记忆，使用 Qdrant 向量库做语义检索
- **直接调用工具诊断** (`test_memory_direct.py`) — 绕过 LLM 验证 MemoryTool 底层是否工作
- **RAG 系统** (`test_rag_basic.py` / `test_rag_ask.py` / `test_rag_rechunked.py`) — 文档问答，含 chunk_size 调优实验
- **知识库** (`knowledge_base/`) — Markdown 格式的小规模测试语料
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

# 3. 跑示例
# --- 第 7 章 ---
python quick_test.py                  # 验证 LLM 调用
python test_my_simple_agent.py        # SimpleAgent + 工具调用
python test_my_react_agent.py         # ReAct
python test_advanced_agents.py        # Reflection / Plan-Solve / Function Calling
python test_multi_tool_agent.py       # 多工具协同

# --- 第 8 章 ---
python smoke_test_ch8.py              # 云基础设施冒烟测试
python test_memory_direct.py          # 直接验证 memory 工具
python test_memory_persist.py store   # 跨进程持久化 - 写
python test_memory_persist.py recall  # 跨进程持久化 - 读
python test_rag_ask.py                # RAG 问答
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
- [ ] 8.4 综合问答助手（跳过 —— Memory + RAG 单独都已会用，组合无新概念）

## License

仅供学习使用。基于 [datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents) 教材。
