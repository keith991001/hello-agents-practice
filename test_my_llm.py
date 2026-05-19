"""测试 MyLLM 的三大功能：
1. 继承父类的 invoke()，行为完全一致
2. 自己实现的 clean_stream()，没有重复打印
3. 累计 token 使用统计
"""
from dotenv import load_dotenv
from my_llm import MyLLM

load_dotenv()

llm = MyLLM()
print(f"✓ Provider: {llm.provider}, Model: {llm.model}\n")

# === 测试 1: 继承自父类的 invoke() ===
print("=== 测试 1: invoke (非流式) ===")
response = llm.invoke([
    {"role": "user", "content": "用 8 个字介绍你自己。"}
])
print(f"响应: {response}\n")

# === 测试 2: 我们自己的 clean_stream() ===
print("=== 测试 2: clean_stream (干净的流式) ===")
print("响应: ", end="", flush=True)
for chunk in llm.clean_stream([
    {"role": "user", "content": "写一句关于学习的格言，不超过 20 字。"}
]):
    print(chunk, end="", flush=True)
print("\n")

# === 测试 3: token 使用情况 ===
print("=== 测试 3: token 累计统计 ===")
print(llm.get_usage_summary())
