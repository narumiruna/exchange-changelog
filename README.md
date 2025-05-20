# exchange-changelog

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Playwright](https://playwright.dev/docs/intro)

## Usage

```sh
export OPENAI_MODEL=gpt-4.1
export OPENAI_API_KEY=
# or
export AZURE_OPENAI_API_KEY=
export AZURE_OPENAI_ENDPOINT=
export OPENAI_API_VERSION=2025-03-01-preview

# Optional
export SLACK_TOKEN=
export SLACK_CHANNEL=

export LANGFUSE_SECRET_KEY=
export LANGFUSE_PUBLIC_KEY=
export LANGFUSE_HOST=

export LOGFIRE_ENVIRONMENT=dev

export REDIS_URL=

uv run exchange-changelog -c config/default.yaml -o changelog.md
```

Result: [gist](https://gist.github.com/narumiruna/707786b350fc17197a35ee9ae3d0456d)

## Prompt generation

To generate prompts, run the following script:

```sh
uv run chainlit run -w generate_prompt.py
```

For more details, refer to the [OpenAI Prompt Generation Guide](https://platform.openai.com/docs/guides/prompt-generation).
