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

# 用 invoke（非流式）拿一次完整字符串，避免框架内部自己 print 造成重复
response = llm.invoke(messages)
print(f"DeepSeek 响应：{response}")
print("\n✓ 调用成功！")
