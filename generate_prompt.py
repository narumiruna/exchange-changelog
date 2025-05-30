from functools import cache

import chainlit as cl
from agents import Agent
from agents import ModelSettings
from agents import Runner
from agents import TResponseInputItem
from dotenv import find_dotenv
from dotenv import load_dotenv
from pydantic import BaseModel

from exchange_changelog.lazy import get_openai_model


class Example(BaseModel):
    input: str
    output: str


class Prompt(BaseModel):
    description: str
    guidelines: list[str]
    steps: list[str]
    output_format: str
    examples: list[Example]
    notes: list[str]

    def __str__(self) -> str:
        return "\n".join(
            [
                self.description,
                "# Guidelines",
                "\n".join([f"- {g}" for g in self.guidelines]),
                "# Steps",
                "\n".join([f"- {s}" for s in self.steps]),
                "# Output Format",
                self.output_format,
                "# Examples",
                "\n".join([f"- {e.input} -> {e.output}" for e in self.examples]),
                "# Notes",
                "\n".join([f"- {n}" for n in self.notes]),
            ]
        )


META_PROMPT = """
Given a task description or existing prompt, produce a detailed system prompt to guide a language model in completing the task effectively.

# Guidelines

- Understand the Task: Grasp the main objective, goals, requirements, constraints, and expected output.
- Minimal Changes: If an existing prompt is provided, improve it only if it's simple. For complex prompts, enhance clarity and add missing elements without altering the original structure.
- Reasoning Before Conclusions**: Encourage reasoning steps before any conclusions are reached. ATTENTION! If the user provides examples where the reasoning happens afterward, REVERSE the order! NEVER START EXAMPLES WITH CONCLUSIONS!
    - Reasoning Order: Call out reasoning portions of the prompt and conclusion parts (specific fields by name). For each, determine the ORDER in which this is done, and whether it needs to be reversed.
    - Conclusion, classifications, or results should ALWAYS appear last.
- Examples: Include high-quality examples if helpful, using placeholders [in brackets] for complex elements.
   - What kinds of examples may need to be included, how many, and whether they are complex enough to benefit from placeholders.
- Clarity and Conciseness: Use clear, specific language. Avoid unnecessary instructions or bland statements.
- Formatting: Use markdown features for readability. DO NOT USE ``` CODE BLOCKS UNLESS SPECIFICALLY REQUESTED.
- Preserve User Content: If the input task or prompt includes extensive guidelines or examples, preserve them entirely, or as closely as possible. If they are vague, consider breaking down into sub-steps. Keep any details, guidelines, examples, variables, or placeholders provided by the user.
- Constants: DO include constants in the prompt, as they are not susceptible to prompt injection. Such as guides, rubrics, and examples.
- Output Format: Explicitly the most appropriate output format, in detail. This should include length and syntax (e.g. short sentence, paragraph, JSON, etc.)
    - For tasks outputting well-defined or structured data (classification, JSON, etc.) bias toward outputting a JSON.
    - JSON should never be wrapped in code blocks (```) unless explicitly requested.

The final prompt you output should adhere to the following structure below. Do not include any additional commentary, only output the completed system prompt. SPECIFICALLY, do not include any additional messages at the start or end of the prompt. (e.g. no "---")

[Concise instruction describing the task - this should be the first line in the prompt, no section header]

[Additional details as needed.]

[Optional sections with headings or bullet points for detailed steps.]

# Steps [optional]

[optional: a detailed breakdown of the steps necessary to accomplish the task]

# Output Format

[Specifically call out how the output should be formatted, be it response length, structure e.g. JSON, markdown, etc]

# Examples [optional]

[Optional: 1-3 well-defined examples with placeholders if necessary. Clearly mark where examples start and end, and what the input and output are. User placeholders as necessary.]
[If the examples are shorter than what a realistic example is expected to be, make a reference with () explaining how real examples should be longer / shorter / different. AND USE PLACEHOLDERS! ]

# Notes [optional]

[optional: edge cases, details, and an area to call or repeat out specific important considerations]
""".strip()  # noqa


class Bot:
    def __init__(self) -> None:
        self.agent = Agent(
            name="prompt-agent",
            instructions=META_PROMPT,
            model=get_openai_model(),
            model_settings=ModelSettings(temperature=0.0),
            output_type=Prompt,
        )
        self.input_items: list[TResponseInputItem] = []

    async def run(self, content: str) -> str:
        self.input_items.append(
            {
                "role": "user",
                "content": content,
            }
        )

        result = await Runner.run(self.agent, input=self.input_items)
        self.input_items = result.to_input_list()

        return str(result.final_output)


@cache
def get_bot() -> Bot:
    load_dotenv(find_dotenv())
    return Bot()


@cl.on_message
async def chat(message: cl.Message) -> None:
    response = await get_bot().run(message.content)
    await cl.Message(content=response).send()
