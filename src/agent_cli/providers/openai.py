from typing import TYPE_CHECKING

from agent_cli.core.models import CompletionRequest, CompletionResponse, ResponseTruncatedError

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MAX_TOKENS = 4096


class OpenAILanguageModel:
    """Provider adapter backed by the OpenAI Chat Completions API.

    Requires the `openai` package (`pip install ".[openai]"`). The import is
    deferred to `complete()` so the rest of the CLI keeps working without it
    installed.
    """

    def __init__(self, model: str | None = None, max_tokens: int | None = None) -> None:
        self._model = model if model is not None else DEFAULT_MODEL
        self._max_tokens = max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        import openai  # noqa: PLC0415 (kept optional; see module docstring)

        client = openai.OpenAI()
        # Built with per-role branches so each dict matches its member of the
        # ChatCompletion*MessageParam union (a shared dict[str, str] does not).
        messages: list[ChatCompletionMessageParam] = []
        for message in request.messages:
            if message.role == "system":
                messages.append({"role": "system", "content": message.content})
            elif message.role == "user":
                messages.append({"role": "user", "content": message.content})
            elif message.role == "assistant":
                messages.append({"role": "assistant", "content": message.content})

        response = client.chat.completions.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=messages,
        )
        if response.choices[0].finish_reason == "length":
            raise ResponseTruncatedError("OpenAI", self._max_tokens)
        text = response.choices[0].message.content or ""
        usage = {}
        if response.usage is not None:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }
        return CompletionResponse(text=text, model=response.model, usage=usage)
