import httpx

try:
    from app.config import settings
except ModuleNotFoundError as exc:
    if exc.name != "app":
        raise
    from config import settings


class OpenRouterError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def chat_completion(
    system: str, messages: list[dict[str, str]], max_tokens: int = 400
) -> str:
    """Send a chat-completion request through OpenRouter."""
    if not settings.openrouter_api_key or settings.openrouter_api_key == "your-openrouter-api-key":
        raise OpenRouterError(
            "OPENROUTER_API_KEY is missing or still uses the placeholder value."
        )

    payload = {
        "model": settings.chat_model,
        "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}, *messages],
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Bella Tavola",
    }

    try:
        response = httpx.post(
            f"{settings.openrouter_base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=20.0,
        )
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as exc:
        raise OpenRouterError(
            f"OpenRouter request failed with status {exc.response.status_code}.",
            exc.response.status_code,
        ) from exc
    except httpx.HTTPError as exc:
        raise OpenRouterError("OpenRouter request could not be completed.") from exc
    except ValueError as exc:
        raise OpenRouterError("OpenRouter returned invalid JSON.") from exc

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise OpenRouterError(
            "OpenRouter response did not contain message content."
        ) from exc

    if not isinstance(content, str) or not content.strip():
        raise OpenRouterError("OpenRouter returned an empty response.")
    return content.strip()


def ask_llm(user_message: str) -> str:
    return chat_completion(
        "You are a friendly Italian waiter. Reply in two sentences.",
        [{"role": "user", "content": user_message}],
        max_tokens=200,
    )


if __name__ == "__main__":
    print(ask_llm("What goes into carbonara?"))
