"""维基百科搜索工具

调用维基百科开放 REST API，无需 API key。
返回查询词的页面摘要（前几句话）。
"""
import requests
from typing import Dict, Any, List
from hello_agents.tools.base import Tool, ToolParameter


class WikipediaSearchTool(Tool):
    """从维基百科搜索一个主题并返回摘要"""

    def __init__(self, language: str = "zh"):
        super().__init__(
            name="wikipedia",
            description="维基百科搜索工具。输入一个主题名称（人名、地名、概念等），返回该主题的简短介绍。",
        )
        self.language = language
        self.base = f"https://{language}.wikipedia.org/api/rest_v1"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="input",
                type="string",
                description="要搜索的主题名称，例如 '光速'、'阿尔伯特·爱因斯坦'",
                required=True,
            )
        ]

    def run(self, parameters: Dict[str, Any]) -> str:
        query = parameters.get("input", "").strip()
        if not query:
            return "❌ 请提供搜索关键词。"

        print(f"📚 Wikipedia 正在查询: {query}")

        try:
            # REST API：page/summary/{title}
            url = f"{self.base}/page/summary/{query}"
            resp = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "hello-agents-tutorial/0.1 (learning)"},
            )

            if resp.status_code == 404:
                return f"未找到与 '{query}' 完全匹配的页面。可以换个关键词。"

            resp.raise_for_status()
            data = resp.json()

            title = data.get("title", query)
            extract = data.get("extract", "（无摘要）")

            # 截短一下，避免给 LLM 灌太多无关上下文
            if len(extract) > 600:
                extract = extract[:600] + "……"

            return f"【{title}】\n{extract}"

        except requests.exceptions.RequestException as e:
            return f"❌ Wikipedia 网络请求失败: {e}"
        except Exception as e:
            return f"❌ Wikipedia 查询出错: {e}"
