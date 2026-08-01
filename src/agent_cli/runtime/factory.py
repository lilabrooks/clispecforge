from agent_cli.agents.base import Agent
from agent_cli.config.settings import Settings
from agent_cli.core.ports import LanguageModel
from agent_cli.providers.registry import create_provider


def build_model(settings: Settings) -> LanguageModel:
    return create_provider(
        settings.provider,
        model=settings.model,
        max_tokens=settings.max_tokens,
    )


def build_agent(settings: Settings) -> Agent:
    return Agent(
        name="clispecforge",
        system_prompt=settings.system_prompt,
        model=build_model(settings),
    )
