# exchange-changelog

## Installation

### Install SingleFile CLI

Follow the [SingleFile CLI Installation Guide](https://github.com/gildas-lormeau/single-file-cli#installation).

### Install uv

```sh
pip install uv
```

### Install Python Dependencies

Install the required Python dependencies using uv:

```sh
uv sync
```

### Environment Configuration

Create a `.env` file in the root directory of your project and add your API keys:

```env
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key_here
SINGLEFILE_PATH=single-file

# Optional
SLACK_TOKEN=your_slack_token_here
SLACK_CHANNEL=your_slack_channel_here
```

## Usage

Run the main script using uv:

```sh
uv run python main.py
```

Result: [gist](https://gist.github.com/narumiruna/707786b350fc17197a35ee9ae3d0456d)

## Prompt generation

To generate prompts, run the following script:

```sh
uv run chainlit run -w generate_prompt.py
```

For more details, refer to the [OpenAI Prompt Generation Guide](https://platform.openai.com/docs/guides/prompt-generation).
