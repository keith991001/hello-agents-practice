"""Python 3.14 兼容的安全计算器工具

不依赖已被移除的 ast.Num，只用 ast.Constant（Python 3.8+ 都有）。
通过 AST 白名单确保安全 —— 只允许数字常量、四则运算、幂运算、负号。
"""
import ast
import operator
from typing import Dict, Any, List
from hello_agents.tools.base import Tool, ToolParameter


# 把 AST 节点映射到实际运算函数
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class SafeCalculatorTool(Tool):
    """安全计算器：AST 白名单 + Python 3.14 兼容"""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="数学计算工具，支持 +、-、*、/、**、//、% 和括号。输入数学表达式字符串。",
        )

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="input",
                type="string",
                description="要计算的数学表达式，例如 '(15 * 8 + 32) / 4'",
                required=True,
            )
        ]

    def run(self, parameters: Dict[str, Any]) -> str:
        expression = parameters.get("input", "").strip()
        if not expression:
            return "❌ 请提供数学表达式。"

        print(f"🧮 SafeCalculator 正在计算: {expression}")
        try:
            tree = ast.parse(expression, mode="eval")
            result = self._eval(tree.body)
            return f"{expression} = {result}"
        except Exception as e:
            return f"❌ 计算失败: {e}"

    # ------------------------------------------------------------
    # AST 递归求值（白名单：只接受我们允许的节点类型）
    # ------------------------------------------------------------
    def _eval(self, node):
        # 数字常量 —— Python 3.8+ 用 ast.Constant 取代 ast.Num
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"不支持的常量类型: {type(node.value).__name__}")

        # 二元运算：left OP right
        if isinstance(node, ast.BinOp):
            op_fn = _OPS.get(type(node.op))
            if op_fn is None:
                raise ValueError(f"不支持的二元运算: {type(node.op).__name__}")
            return op_fn(self._eval(node.left), self._eval(node.right))

        # 一元运算：-x  或  +x
        if isinstance(node, ast.UnaryOp):
            op_fn = _OPS.get(type(node.op))
            if op_fn is None:
                raise ValueError(f"不支持的一元运算: {type(node.op).__name__}")
            return op_fn(self._eval(node.operand))

        # 其他全部拒绝（函数调用、变量名、属性访问……都被挡在外面）
        raise ValueError(f"不安全或不支持的语法: {type(node).__name__}")
