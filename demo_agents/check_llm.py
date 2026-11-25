"""One-off check for step 0.3: one LLM call, configured only by env vars."""

import os

from anthropic import Anthropic


def main() -> None:
    client = Anthropic(
        base_url=os.environ.get("LLM_BASE_URL") or None,
        api_key=os.environ["LLM_API_KEY"],
    )
    message = client.messages.create(
        model=os.environ["AGENT_MODEL"],
        max_tokens=50,
        messages=[{"role": "user", "content": "Reply with the single word: ready"}],
    )
    print(message.model, message.stop_reason, message.usage.input_tokens)  # noqa: T201
    print(message.content)  # noqa: T201


if __name__ == "__main__":
    main()
