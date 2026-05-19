# hello-agents-tutorial

从零跟着 [datawhalechina/hello-agents 第七章](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md) 一步步构建的 Agent 学习项目。

## 包含什么

- **LLM 客户端扩展** (`my_llm.py`) — 继承 `HelloAgentsLLM` 添加干净流式输出和 token 追踪
- **SimpleAgent + 工具调用** (`my_simple_agent.py`) — Prompt 模板嵌入式工具调用
- **ReActAgent** (`my_react_agent.py`) — Reasoning + Acting，多步推理，带 markdown 兼容 parser
- **Python 3.14 兼容计算器** (`safe_calculator.py`) — 修复了框架内置 calculator 在新 Python 上的 `ast.Num` bug
- **Wikipedia 搜索工具** (`wikipedia_tool.py`) — 调用维基开放 REST API，无需 key
- **多工具协同 demo** (`test_multi_tool_agent.py`) — ReAct + 计算器 + 维基百科组合

## 环境要求

- Python ≥ 3.10
- DeepSeek API key（或其他 OpenAI 兼容的 LLM provider）

## 复现步骤

```bash
# 1. clone 后建虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. 配置 API key
cp .env.example .env       # 然后编辑 .env 填入你的 sk-...

# 3. 跑示例
python quick_test.py                  # 验证 LLM 调用
python test_my_simple_agent.py        # SimpleAgent + 工具调用
python test_my_react_agent.py         # ReAct
python test_advanced_agents.py        # Reflection / Plan-Solve / Function Calling
python test_multi_tool_agent.py       # 多工具协同
```

## 踩过的坑（学习记录）

| 问题 | 修复 |
|---|---|
| TextEdit 富文本模式给 .py 加前导空格 → `IndentationError` | 用 `cat > file << 'EOF'` heredoc 或 VS Code |
| `.gitignore` 缩进失效 → API key 没被忽略 | `git check-ignore -v .env` 验证 |
| `provider="auto"` 是非空字符串，绕过了父类的 `or` fallback | 默认值改成 `None` |
| 框架内置 calculator 在 Python 3.14 用 `ast.Num` 报错 | 写 `SafeCalculatorTool` 绕开 |
| `think` / `stream_invoke` 自己内部 print → 重复输出 | 用非流式 `invoke`，或 `clean_stream` 直接调底层 client |
| ReAct parser 正则不认 markdown 粗体 `**Thought:**` | override `_parse_output` 让正则容忍 `\*{0,2}` |

## 学习目标完成情况

- [x] 7.2 扩展 HelloAgentsLLM（继承 + super + override）
- [x] 7.3 理解 Message / Config / Agent 基类（抽象基类 + DTO 模式）
- [x] 7.4.1 SimpleAgent + 工具调用
- [x] 7.4.2 ReActAgent
- [x] 7.4.3-5 Reflection / Plan-Solve / Function Calling 范式
- [x] 7.5 工具系统 + 自定义工具

## License

仅供学习使用。基于 [datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents) 教材。
