# changelog-helper

## Installation

### Install Singlefile CLI

Follow the [Singlefile CLI Installation Guide](https://github.com/gildas-lormeau/single-file-cli?tab=readme-ov-file#installation).

### Install Poetry

```sh
pip install pipx
pipx install poetry
```

### Install Python Dependencies

```sh
poetry install
```

### API Key Configuration

Create a `.env` file in the root directory of your project and add your API keys:

```env
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key_here
```

### Run the Code

```sh
poetry run python main.py
```
