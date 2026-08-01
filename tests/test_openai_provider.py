import sys
import types

import pytest

from agent_cli.core.messages import Message
from agent_cli.core.models import CompletionRequest, ResponseTruncatedError
from agent_cli.providers.openai import OpenAILanguageModel


class _FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str, finish_reason: str = "stop") -> None:
        self.message = _FakeMessage(content)
        self.finish_reason = finish_reason


class _FakeUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class _FakeCompletion:
    def __init__(self, text: str, model: str, finish_reason: str = "stop") -> None:
        self.choices = [_FakeChoice(text, finish_reason)]
        self.usage = _FakeUsage(prompt_tokens=8, completion_tokens=4)
        self.model = model


class _FakeCompletions:
    def __init__(self, finish_reason: str = "stop") -> None:
        self.calls: list[dict[str, object]] = []
        self.finish_reason = finish_reason

    def create(self, **kwargs: object) -> _FakeCompletion:
        self.calls.append(kwargs)
        return _FakeCompletion(
            text="hello from gpt",
            model=str(kwargs["model"]),
            finish_reason=self.finish_reason,
        )


class _FakeChat:
    def __init__(self, finish_reason: str = "stop") -> None:
        self.completions = _FakeCompletions(finish_reason)


class _FakeClient:
    def __init__(self, finish_reason: str = "stop") -> None:
        self.chat = _FakeChat(finish_reason)


def _install_fake_openai(
    monkeypatch: pytest.MonkeyPatch,
    finish_reason: str = "stop",
) -> _FakeClient:
    client = _FakeClient(finish_reason)
    fake_module = types.SimpleNamespace(OpenAI=lambda: client)
    monkeypatch.setitem(sys.modules, "openai", fake_module)
    return client


def test_complete_sends_system_and_user_messages(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _install_fake_openai(monkeypatch)
    model = OpenAILanguageModel(max_tokens=8192)
    request = CompletionRequest(
        messages=(
            Message(role="system", content="You are terse."),
            Message(role="user", content="hello"),
        )
    )

    response = model.complete(request)

    call = client.chat.completions.calls[0]
    assert call["messages"] == [
        {"role": "system", "content": "You are terse."},
        {"role": "user", "content": "hello"},
    ]
    assert call["max_tokens"] == 8192
    assert response.text == "hello from gpt"
    assert response.usage == {"input_tokens": 8, "output_tokens": 4}


def test_complete_rejects_truncated_response(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_openai(monkeypatch, finish_reason="length")
    model = OpenAILanguageModel(max_tokens=2048)
    request = CompletionRequest(messages=(Message(role="user", content="hello"),))

    with pytest.raises(ResponseTruncatedError, match="configured 2048-token output limit"):
        model.complete(request)
