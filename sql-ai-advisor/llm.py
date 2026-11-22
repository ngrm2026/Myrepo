"""One small wrapper so the rest of the app does not care which LLM is used."""
import config


def ask(system: str, user: str) -> str:
    provider = config.LLM_PROVIDER

    if provider in ("azure", "openai"):
        from openai import AzureOpenAI, OpenAI

        if provider == "azure":
            if not (config.AZURE_OPENAI_ENDPOINT and config.AZURE_OPENAI_API_KEY and config.LLM_MODEL):
                raise RuntimeError("Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY and LLM_MODEL (deployment name) in .env")
            client = AzureOpenAI(
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
                api_key=config.AZURE_OPENAI_API_KEY,
                api_version=config.AZURE_OPENAI_API_VERSION,
            )
        else:
            if not config.OPENAI_API_KEY:
                raise RuntimeError("Set OPENAI_API_KEY in .env")
            client = OpenAI(api_key=config.OPENAI_API_KEY)

        resp = client.chat.completions.create(
            model=config.LLM_MODEL or "gpt-4o-mini",
            max_tokens=config.LLM_MAX_TOKENS,
            temperature=0.2,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        return resp.choices[0].message.content

    if provider == "anthropic":
        import anthropic

        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError("Set ANTHROPIC_API_KEY in .env")
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model=config.LLM_MODEL or "claude-sonnet-5-5",
            max_tokens=config.LLM_MAX_TOKENS,
            temperature=0.2,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")

    raise RuntimeError(f"Unknown LLM_PROVIDER '{provider}'. Use azure, openai or anthropic.")
