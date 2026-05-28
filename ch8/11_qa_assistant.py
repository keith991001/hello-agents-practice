"""8.7 节 终章作品：智能文档问答助手

前面 10 个例子都是"演示 API"，这一个是"组装产品"。
把 RAG（外部知识）+ Memory（用户上下文）+ Agent（LLM 决策）封装成一个类，
对外暴露 ask/recall/note/stats 等真实方法 —— 这就是一个能交付的 Agent App。

架构：
              ┌─────────────────────────────────────┐
              │  PDFLearningAssistant               │
              │  (会话级状态: session_id, stats)    │
              ├──────────────┬──────────────────────┤
              │  RAGTool     │  MemoryTool          │
              │  (知识)       │  (个人化历史)         │
              └──────────────┴──────────────────────┘
                       │                │
                  Qdrant Cloud    Qdrant + Neo4j

CLI 版（官方版用 Gradio Web UI；UI 不是第 8 章核心，我们保留架构本体）。

## 前置条件
- .env 已配 LLM / DashScope / Qdrant
- 一份文档来加载（默认期待 PDF，但 hello-agents 的 RAGTool 用 MarkItDown 解析,
  理论上也能吃 .md / .docx / .html / .txt —— 试试 `load knowledge_base/web_basics.md`）

## 跑完会产生什么
- Qdrant 里多一个 `rag_namespace="pdf_keith"` 和 `user_id="keith"` 的 collection
- 进入交互模式后, 每个 ask/note/recall 都会落到云端
- 输入 `report` 会在当前目录生成 `report_session_*.json`（已加进 .gitignore）

## CLI 命令
  load <path>     灌一份文档到这个用户的私有 RAG 知识库
  ask <q>         问问题（用 MQE+HyDE 高级检索）
  recall <q>      回忆 — 在自己的记忆里搜
  note <txt>      记笔记（落 semantic memory）
  stats           查会话统计
  report          生成 JSON 报告
  quit            退出

## 试用脚本
  >>> load knowledge_base/web_basics.md
  >>> ask HTTP PUT 和 PATCH 有什么区别?
  >>> note PUT 整体替换, PATCH 局部修改
  >>> recall PUT
  >>> stats
  >>> quit

## 下一步
这就是第 8 章的终点了。可以继续学 hello-agents 的 ch9+（出到 ch16），
或者把这个 PDFLearningAssistant 套个 Gradio UI 变成 Web 应用（参考官方 11 号文件）。
"""
import os
import json
from datetime import datetime
from typing import Any
from dotenv import load_dotenv
from hello_agents.tools import MemoryTool, RAGTool

load_dotenv()


class PDFLearningAssistant:
    """文档问答 + 学习历程记录助手。一个用户一份实例（user_id 隔离）。"""

    def __init__(self, user_id: str = "keith"):
        self.user_id = user_id
        self.session_id = f"session_{datetime.now():%Y%m%d_%H%M%S}"
        self.memory_tool = MemoryTool(user_id=user_id)
        self.rag_tool = RAGTool(rag_namespace=f"pdf_{user_id}")
        self.session_start = datetime.now()
        self.stats = {"documents": 0, "questions": 0, "notes": 0}
        self.current_doc: str | None = None

    def load_document(self, file_path: str) -> str:
        """灌一份 PDF/MD 到这个用户的私有知识库。"""
        if not os.path.exists(file_path):
            return f"❌ 文件不存在: {file_path}"

        result = self.rag_tool.run({
            "action": "add_document",
            "file_path": file_path,
            "chunk_size": 1000,
            "chunk_overlap": 200,
        })
        self.current_doc = os.path.basename(file_path)
        self.stats["documents"] += 1

        # 学习历程也要记一笔 (走 episodic, 长期保留)
        self.memory_tool.run({
            "action": "add",
            "content": f"加载了文档《{self.current_doc}》",
            "memory_type": "episodic",
            "importance": 0.85,
            "event_type": "doc_loaded",
            "session_id": self.session_id,
        })
        return f"✓ 加载: {self.current_doc} — {result}"

    def ask(self, question: str, advanced: bool = True) -> str:
        """问问题。同时记录到 working memory 作为短期上下文。"""
        # 短期记忆：这次会话的提问轨迹
        self.memory_tool.run({
            "action": "add",
            "content": f"提问: {question}",
            "memory_type": "working",
            "importance": 0.5,
            "session_id": self.session_id,
        })

        answer = self.rag_tool.run({
            "action": "ask",
            "question": question,
            "top_k": 5,
            "enable_advanced_search": advanced,
            "enable_mqe": advanced,
            "enable_hyde": advanced,
        })

        # 情景记忆：保留"今天问了什么"作为长期可回溯的事件
        self.memory_tool.run({
            "action": "add",
            "content": f"问了一个关于'{question}'的问题",
            "memory_type": "episodic",
            "importance": 0.7,
            "event_type": "qa",
            "session_id": self.session_id,
        })

        self.stats["questions"] += 1
        return answer

    def note(self, content: str, concept: str = "general") -> str:
        """记笔记。落到 semantic memory，因为笔记代表"概念性知识"。"""
        self.memory_tool.run({
            "action": "add",
            "content": content,
            "memory_type": "semantic",
            "importance": 0.8,
            "concept": concept,
            "session_id": self.session_id,
        })
        self.stats["notes"] += 1
        return f"✓ 笔记已存 ({concept}): {content[:50]}..."

    def recall(self, query: str, limit: int = 5) -> str:
        """回忆 — 从全部记忆类型里检索（episodic + semantic + working）。"""
        return self.memory_tool.run({
            "action": "search",
            "query": query,
            "limit": limit,
        })

    def get_stats(self) -> dict[str, Any]:
        duration_sec = (datetime.now() - self.session_start).total_seconds()
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "duration_sec": int(duration_sec),
            "current_doc": self.current_doc or "(none)",
            **self.stats,
        }

    def report(self, save: bool = True) -> dict[str, Any]:
        """生成会话报告（导出给 review/复盘用）。"""
        report = {
            "session": self.get_stats(),
            "memory_summary": self.memory_tool.run({"action": "summary", "limit": 10}),
            "rag_status": self.rag_tool.run({"action": "stats"}),
        }
        if save:
            fname = f"report_{self.session_id}.json"
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            report["saved_to"] = fname
        return report


# ====================================================================
# CLI 主循环 —— 真正能用的助手长啥样
# ====================================================================
def main():
    print("=" * 60)
    print("📚 智能文档问答助手 (CLI)")
    print("=" * 60)
    print("命令: load <path> | ask <q> | recall <q> | note <txt> | stats | report | quit")
    print()

    assistant = PDFLearningAssistant(user_id="keith")

    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 退出")
            break

        if not line:
            continue
        if line in {"quit", "exit", "q"}:
            print("\n📊 最后统计:", assistant.get_stats())
            break

        parts = line.split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "load":
            print(assistant.load_document(arg))
        elif cmd == "ask":
            print(assistant.ask(arg) if arg else "用法: ask <问题>")
        elif cmd == "recall":
            print(assistant.recall(arg) if arg else "用法: recall <关键词>")
        elif cmd == "note":
            print(assistant.note(arg) if arg else "用法: note <内容>")
        elif cmd == "stats":
            print(assistant.get_stats())
        elif cmd == "report":
            r = assistant.report()
            print(f"✓ 报告已生成 → {r.get('saved_to', '(未保存)')}")
        else:
            print(f"❓ 未知命令: {cmd}")


if __name__ == "__main__":
    main()
