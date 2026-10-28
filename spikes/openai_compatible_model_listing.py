"""List models exposed by a configured OpenAI-compatible provider."""

from urllib.parse import urlparse

from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from llm_config import load_llm_config


console = Console()


def get_provider_name(base_url: str | None) -> str:
    if not base_url:
        return "OpenAI"

    hostname = urlparse(base_url).hostname or ""
    known_providers = {
        "api.openai.com": "OpenAI",
        "api.groq.com": "Groq",
        "api.x.ai": "xAI/Grok",
        "api.mistral.ai": "Mistral",
    }
    return known_providers.get(hostname, "Custom OpenAI-compatible provider")


def validate_base_url(base_url: str | None) -> None:
    if not base_url:
        return

    parsed_url = urlparse(base_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise RuntimeError("LLM_BASE_URL must be a valid HTTP or HTTPS URL.")


def build_client(config):
    client_kwargs = {"api_key": config.api_key}
    if config.base_url:
        client_kwargs["base_url"] = config.base_url
    return OpenAI(**client_kwargs)


def model_value(model, field: str, default: str = "Not provided") -> str:
    value = getattr(model, field, None)
    if value is None:
        return default
    if field == "active":
        return "Yes" if value else "No"
    return str(value)


def main() -> None:
    config = load_llm_config()
    validate_base_url(config.base_url)
    provider_name = get_provider_name(config.base_url)

    client = build_client(config)
    models = client.models.list()

    console.print(
        Panel.fit(
            f"[bold]Provider:[/bold] {provider_name}\n"
            f"[bold]Base URL:[/bold] {config.base_url or 'https://api.openai.com/v1'}",
            title="OpenAI-Compatible Model Listing",
        )
    )

    table = Table(title="Models Returned by the Provider")
    table.add_column("Model ID", style="cyan")
    table.add_column("Owner")
    table.add_column("Active")
    table.add_column("Context Window")
    table.add_column("Created")

    for model in models.data:
        table.add_row(
            model_value(model, "id"),
            model_value(model, "owned_by"),
            model_value(model, "active"),
            model_value(model, "context_window"),
            model_value(model, "created"),
        )

    console.print(table)
    console.print(
        "[dim]Rate limits, pricing, capabilities, and full model-card details are "
        "shown only when exposed by the provider's API response."
        "[/dim]"
    )


if __name__ == "__main__":
    main()
