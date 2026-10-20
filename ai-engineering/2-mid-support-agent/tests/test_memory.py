from support_agent.memory import ConversationMemory


def test_keeps_all_messages_under_the_limit():
    memory = ConversationMemory(max_messages=5)
    memory.add("user", "hi")
    memory.add("assistant", "hello")
    assert [m["content"] for m in memory.messages()] == ["hi", "hello"]
