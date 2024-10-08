from __future__ import annotations

import os

from google.generativeai import GenerationConfig
from google.generativeai import GenerativeModel
from google.generativeai import configure
from google.generativeai.types import ContentsType
from google.generativeai.types import GenerateContentResponse
from google.generativeai.types import HarmBlockThreshold
from google.generativeai.types import HarmCategory
from typing_extensions import TypedDict


class ChangeLog(TypedDict):
    date: str
    text: str


class Gemini:
    def __init__(
        self,
        model: str = "gemini-1.5-pro",
        temperature: float = 0,
    ) -> None:
        self.model = model
        self.temperature = temperature

        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=list[ChangeLog],
        )

        configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.client = GenerativeModel(
            model_name=model,
            generation_config=generation_config,
        )

        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

    def __call__(self, contents: ContentsType) -> GenerateContentResponse:
        return self.client.generate_content(
            contents=contents,
            # safety_settings=self.safety_settings,
        )
