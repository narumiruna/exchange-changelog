# exchange-changelog

## Installation

### Install Singlefile CLI

Follow the [Singlefile CLI Installation Guide](https://github.com/gildas-lormeau/single-file-cli?tab=readme-ov-file#installation).

### Install Poetry

To install Poetry, first install `pipx` and then use `pipx` to install Poetry:

```sh
pip install pipx
pipx install poetry
```

### Install Python Dependencies

Install the required Python dependencies using Poetry:

```sh
poetry install
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

Run the main script using Poetry:

```sh
poetry run python main.py
```

Result: [gist](https://gist.github.com/narumiruna/707786b350fc17197a35ee9ae3d0456d)

## Prompt generation

To generate prompts, run the following script:

```sh
poetry run python meta_prompt.py
```

For more details, refer to the [OpenAI Prompt Generation Guide](https://platform.openai.com/docs/guides/prompt-generation).
