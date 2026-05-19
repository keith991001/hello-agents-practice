"""探索 hello-agents 的三大核心类：Message / Config / Agent

不实际调用 LLM，纯粹把对象造出来、打印出来，理解它们的内部结构。
"""
from dotenv import load_dotenv
from hello_agents import Message, Config
from hello_agents.core.agent import Agent
from datetime import datetime

load_dotenv()


# === 1. Message 类 ===
print("=" * 50)
print("1. Message 类 —— 一条对话消息")
print("=" * 50)

msg_user = Message(content="你好，请介绍自己", role="user")
msg_assistant = Message(
    content="我是 DeepSeek 助手",
    role="assistant",
    metadata={"tokens": 8, "latency_ms": 320}
)

print(f"用户消息: {msg_user}")
print(f"助手消息: {msg_assistant}")
print(f"\n助手消息的内部字段:")
print(f"  - content: {msg_assistant.content}")
print(f"  - role: {msg_assistant.role}")
print(f"  - timestamp: {msg_assistant.timestamp}")
print(f"  - metadata: {msg_assistant.metadata}")
print(f"\nto_dict() 转成 OpenAI API 格式:")
print(f"  {msg_assistant.to_dict()}")


# === 2. Config 类 ===
print("\n" + "=" * 50)
print("2. Config 类 —— 框架级配置")
print("=" * 50)

cfg_default = Config()
print(f"默认配置:")
print(f"  - default_model: {cfg_default.default_model}")
print(f"  - temperature: {cfg_default.temperature}")
print(f"  - debug: {cfg_default.debug}")
print(f"  - max_history_length: {cfg_default.max_history_length}")

cfg_from_env = Config.from_env()
print(f"\n从环境变量读出来的配置:")
print(f"  - temperature: {cfg_from_env.temperature}")
print(f"  - debug: {cfg_from_env.debug}")


# === 3. Agent 抽象基类 ===
print("\n" + "=" * 50)
print("3. Agent 抽象基类 —— 不能直接实例化")
print("=" * 50)

try:
    from hello_agents import HelloAgentsLLM
    llm = HelloAgentsLLM()
    a = Agent(name="试图直接实例化", llm=llm)
except TypeError as e:
    print(f"❌ 预期的失败: {e}")
    print("\n   原因：Agent 用 @abstractmethod 装饰了 run() 方法，")
    print("   没有具体子类实现 run() 就不能 new 出实例。")
    print("   这就是 Python 强制 '抽象类不能直接用' 的机制。")

# 但是 SimpleAgent 是 Agent 的具体子类，它实现了 run()，所以可以实例化
print("\n下面这个就行，因为 SimpleAgent 实现了 run():")
from hello_agents import SimpleAgent
agent = SimpleAgent(
    name="测试助手",
    llm=HelloAgentsLLM(),
    system_prompt="你是个测试助手"
)
print(f"  ✓ {agent}")
print(f"  历史消息条数（应为 0）: {len(agent.get_history())}")

# 手动塞两条消息进历史
agent.add_message(Message("你好", "user"))
agent.add_message(Message("您好！", "assistant"))
print(f"  添加两条后: {len(agent.get_history())} 条")
for m in agent.get_history():
    print(f"    - {m}")
