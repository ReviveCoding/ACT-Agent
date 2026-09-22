from act_agent.training.preprocess import tokenize_trace


class DummyTokenizer:
    def apply_chat_template(self, messages, tokenize=True, add_generation_prompt=False):
        return [len(m["content"]) for m in messages]


def test_only_assistant_message_is_labeled() -> None:
    ids, labels = tokenize_trace(
        DummyTokenizer(),
        [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "ok"},
            {"role": "tool", "content": "result"},
        ],
        10,
    )
    assert ids == [5, 2, 6]
    assert labels == [-100, 2, -100]
