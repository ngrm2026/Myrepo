"""One small wrapper so the rest of the app does not care which LLM is used."""
import config


def _placeholder(value: str) -> bool:
    return (not value) or "<" in value or ">" in value


def ask(system: str, user: str) -> str:
    provider = config.LLM_PROVIDER

    if provider in ("azure", "openai", "ollama"):
        from openai import AzureOpenAI, OpenAI

        if provider == "azure":
            if _placeholder(config.AZURE_OPENAI_ENDPOINT) or _placeholder(config.AZURE_OPENAI_API_KEY) \
                    or _placeholder(config.LLM_MODEL):
                raise RuntimeError(
                    "Azure OpenAI is not configured: set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY and "
                    "LLM_MODEL (deployment name) in .env — or use LLM_PROVIDER=ollama for a free local model.")
            client = AzureOpenAI(
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
                api_key=config.AZURE_OPENAI_API_KEY,
                api_version=config.AZURE_OPENAI_API_VERSION,
            )
            model = config.LLM_MODEL
        elif provider == "openai":
            if _placeholder(config.OPENAI_API_KEY):
                raise RuntimeError("Set OPENAI_API_KEY in .env")
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            model = config.LLM_MODEL if not _placeholder(config.LLM_MODEL) else "gpt-4o-mini"
        else:  # ollama: local model, OpenAI-compatible API, nothing leaves the machine
            client = OpenAI(base_url=config.OLLAMA_BASE_URL, api_key="ollama")
            model = config.LLM_MODEL if not _placeholder(config.LLM_MODEL) else "qwen2.5-coder:7b"

        try:
            resp = client.chat.completions.create(
                model=model,
                max_tokens=config.LLM_MAX_TOKENS,
                temperature=0.2,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
        except Exception as exc:
            if provider == "ollama":
                raise RuntimeError(
                    f"Could not reach Ollama at {config.OLLAMA_BASE_URL}. Is Ollama running and is the model "
                    f"pulled? Run: ollama pull {model}   ({exc})") from exc
            raise
        return resp.choices[0].message.content

    if provider == "anthropic":
        import anthropic

        if _placeholder(config.ANTHROPIC_API_KEY):
            raise RuntimeError("Set ANTHROPIC_API_KEY in .env")
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model=config.LLM_MODEL if not _placeholder(config.LLM_MODEL) else "claude-sonnet-5-5",
            max_tokens=config.LLM_MAX_TOKENS,
            temperature=0.2,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")

    raise RuntimeError(f"Unknown LLM_PROVIDER '{provider}'. Use azure, openai, anthropic or ollama.")
