import functools

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSerializable

from .llm import get_llm_from_env


@functools.cache
def get_chain(template: str) -> RunnableSerializable:
    llm = get_llm_from_env()
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    return chain
