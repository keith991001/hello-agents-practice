"""验证 hello-agents 能成功调用 DeepSeek API"""
from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM

load_dotenv()

llm = HelloAgentsLLM()
print(f"✓ 检测到的 provider: {llm.provider}")
print(f"✓ 使用的模型: {llm.model}")
print(f"✓ Base URL: {llm.base_url}\n")

messages = [
    {"role": "user", "content": "用一句话介绍你自己。"}
]

print("DeepSeek 响应：", end="", flush=True)
for chunk in llm.think(messages):
    print(chunk, end="", flush=True)
print("\n\n✓ 调用成功！")
