import sys
import types

import pytest

from agent_cli.core.messages import Message
from agent_cli.core.models import CompletionRequest, ResponseTruncatedError
from agent_cli.providers.anthropic import AnthropicLanguageModel


class _FakeContentBlock:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _FakeUsage:
    def __init__(self, input_tokens: int, output_tokens: int) -> None:
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class _FakeMessage:
    def __init__(self, text: str, model: str, stop_reason: str = "end_turn") -> None:
        self.content = [_FakeContentBlock(text)]
        self.usage = _FakeUsage(input_tokens=10, output_tokens=5)
        self.model = model
        self.stop_reason = stop_reason


class _FakeMessages:
    def __init__(self, stop_reason: str = "end_turn") -> None:
        self.calls: list[dict[str, object]] = []
        self.stop_reason = stop_reason

    def create(self, **kwargs: object) -> _FakeMessage:
        self.calls.append(kwargs)
        return _FakeMessage(
            text="hello from claude",
            model=str(kwargs["model"]),
            stop_reason=self.stop_reason,
        )


class _FakeClient:
    def __init__(self, stop_reason: str = "end_turn") -> None:
        self.messages = _FakeMessages(stop_reason)


def _install_fake_anthropic(
    monkeypatch: pytest.MonkeyPatch,
    stop_reason: str = "end_turn",
) -> _FakeClient:
    client = _FakeClient(stop_reason)
    fake_module = types.SimpleNamespace(Anthropic=lambda: client)
    monkeypatch.setitem(sys.modules, "anthropic", fake_module)
    return client


def test_complete_splits_system_prompt_from_messages(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _install_fake_anthropic(monkeypatch)
    model = AnthropicLanguageModel(max_tokens=8192)
    request = CompletionRequest(
        messages=(
            Message(role="system", content="You are terse."),
            Message(role="user", content="hello"),
            Message(role="assistant", content="prior reply"),
        )
    )

    response = model.complete(request)

    call = client.messages.calls[0]
    assert call["system"] == "You are terse."
    assert call["messages"] == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "prior reply"},
    ]
    assert call["max_tokens"] == 8192
    assert response.text == "hello from claude"
    assert response.usage == {"input_tokens": 10, "output_tokens": 5}


def test_complete_omits_system_kwarg_when_no_system_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _install_fake_anthropic(monkeypatch)
    model = AnthropicLanguageModel()
    request = CompletionRequest(messages=(Message(role="user", content="hello"),))

    model.complete(request)

    assert "system" not in client.messages.calls[0]


def test_complete_rejects_truncated_response(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_anthropic(monkeypatch, stop_reason="max_tokens")
    model = AnthropicLanguageModel(max_tokens=2048)
    request = CompletionRequest(messages=(Message(role="user", content="hello"),))

    with pytest.raises(ResponseTruncatedError, match="configured 2048-token output limit"):
        model.complete(request)
