"""综合演示：Reflection、Plan-and-Solve、Function Calling 三种范式

每段演示都包含：
1. 概念解释
2. 实际跑一次
3. 输出观察点
"""
from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM
from hello_agents.agents.reflection_agent import ReflectionAgent
from hello_agents.agents.plan_solve_agent import PlanAndSolveAgent

load_dotenv()
llm = HelloAgentsLLM()


# ============================================================
# 范式 1: Reflection ——"生成→反思→修正"循环
# ============================================================
print("\n" + "█" * 70)
print("范式 1: ReflectionAgent —— 让 LLM 当自己的批改老师")
print("█" * 70)
print("""
任务：写一句关于"学习"的格言。
观察点：
  - 初始尝试 → 反思（LLM 自我评价）→ 修正 → 再反思 ...
  - 通常 1-2 轮就会显著改善，3 轮后边际效益递减
  - 代价：每轮 3-5 倍的 token 消耗
""")

reflector = ReflectionAgent(
    name="格言写作家",
    llm=llm,
    max_iterations=2,  # 反思 2 轮就够看效果了
)
final_essay = reflector.run("用一句话写一条关于'终身学习'的格言，要求富有诗意且能引人深思。")
print(f"\n>>> 最终输出:\n{final_essay}")


# ============================================================
# 范式 2: Plan-and-Solve —— 先拆任务，再依次执行
# ============================================================
print("\n\n" + "█" * 70)
print("范式 2: PlanAndSolveAgent —— 先规划，后执行")
print("█" * 70)
print("""
任务：一个需要多步推理的应用题。
观察点：
  - 第一步：Planner 把任务拆成 N 步
  - 后续步骤：Executor 逐步推进
  - 跟 ReAct 的区别：ReAct 边走边想，Plan-Solve 想完再走（更有"全局视角"）
""")

planner = PlanAndSolveAgent(
    name="规划求解师",
    llm=llm,
)
result = planner.run(
    "小明有 100 元。先用 30% 买书，剩下的钱买零食花了 25 元，最后又赚了 15 元。问最后剩多少？"
)
print(f"\n>>> 最终结果:\n{result}")


# ============================================================
# 范式 3: Function Calling —— LLM 原生的"标准化工具调用"
# ============================================================
print("\n\n" + "█" * 70)
print("范式 3: DeepSeek 原生 Function Calling —— 不靠 prompt 解析")
print("█" * 70)
print("""
观察点：
  - 我们不再写"工具调用格式"prompt 模板了
  - 而是把工具的 JSON Schema 通过 API 的 tools 参数告诉模型
  - 模型直接返回结构化的 tool_calls 对象，框架无需 regex 解析
  - 这是生产环境的首选方案
""")

# 工具 schema —— OpenAI 协议规定的格式
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行数学计算。输入一个表达式字符串，返回计算结果。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如 '(15 * 8 + 32) / 4'",
                    },
                },
                "required": ["expression"],
            },
        },
    }
]

from safe_calculator import SafeCalculatorTool
calc = SafeCalculatorTool()

# 直接用底层 OpenAI client 发请求（绕开 hello-agents 的 prompt 模板）
messages = [
    {"role": "user", "content": "请帮我算 (15 * 8 + 32) / 4 是多少？"}
]
resp = llm._client.chat.completions.create(
    model=llm.model,
    messages=messages,
    tools=tools_schema,
)
msg = resp.choices[0].message
print(f"\nLLM 第一次响应（应该返回 tool_calls 而不是普通文字）:")
print(f"  content: {msg.content}")
print(f"  tool_calls: {msg.tool_calls}")

# 如果 LLM 决定调工具，我们执行并把结果回灌
if msg.tool_calls:
    messages.append(msg.model_dump())  # 把 assistant 的 tool_calls 消息追加
    for call in msg.tool_calls:
        import json
        args = json.loads(call.function.arguments)
        result = calc.run({"input": args["expression"]})
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": result,
        })

    # 第二次调用：让 LLM 基于工具结果给出最终答案
    resp2 = llm._client.chat.completions.create(
        model=llm.model,
        messages=messages,
    )
    print(f"\nLLM 第二次响应（基于工具结果的最终回答）:")
    print(resp2.choices[0].message.content)
