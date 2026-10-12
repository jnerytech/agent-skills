# Appendix A: Trying out LangChain

## Core Idea
A hands-on setup guide for running your first LangChain code in a Jupyter Notebook: configuring an OpenAI API key, invoking a chat model directly, then building prompts with `PromptTemplate` and chaining them with LCEL.

## Key Concepts
- **OpenAI API key**: A secret key created in the OpenAI platform (profile icon > Your profile > User API Key), used to authenticate calls to OpenAI models; should be saved safely since it can't be retrieved again, and a spending limit should be set to control costs.
- **Virtual environment**: An isolated Python environment (`python -m venv`) created per chapter/project so package versions (`notebook`, `langchain`, `openai`) don't conflict across examples.
- **ChatOpenAI**: The LangChain class that wraps an OpenAI chat model (e.g., `gpt-5-nano`) into a `Runnable` object you can `.invoke()` directly with a string prompt.
- **PromptTemplate**: A LangChain class that builds prompts from a template string with `{placeholder}` parameters, letting you reuse the same prompt structure with different inputs.
- **Runnable interface**: The common interface implemented by both `PromptTemplate` and `ChatOpenAI` objects, which is what allows them to be linked with the `|` operator.
- **LCEL (LangChain Expression Language)**: A declarative syntax using `|` to compose components (e.g., prompt, LLM, parsers) into a chain/pipeline, replacing more verbose imperative wiring.

## Code Examples
```python
# Set up API key and invoke a chat model directly
from langchain_openai import ChatOpenAI
import getpass

OPENAI_API_KEY = getpass.getpass('Enter your OPENAI_API_KEY')

llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name="gpt-5-nano")
llm.invoke("It's a hot day, I would like to go to the…")

# Build and run a reusable prompt with PromptTemplate
from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate.from_template(
    """You are an experienced copywriter. Write a {num_words} words summary
    of the following text, using a {tone} tone: {text}"""
)
prompt_input = prompt_template.format(
    text=segovia_aqueduct_text, num_words=20, tone="knowledgeable and engaging"
)
response = llm.invoke(prompt_input)
print(response.content)

# Same task expressed as an LCEL chain
chain = prompt_template | llm
response = chain.invoke({
    "text": segovia_aqueduct_text,
    "num_words": 20,
    "tone": "knowledgeable and engaging"
})
print(response.content)
```
- **What it demonstrates**: How raw `llm.invoke()` calls, templated prompts, and LCEL's `|` chaining all accomplish the same summarization task with progressively less imperative code.

## Key Takeaways
1. Create the OpenAI key, set a spending limit, and store it safely before writing any LangChain code — it can't be retrieved later.
2. Use a dedicated virtual environment and `pip install -r requirements.txt` (or `notebook`/`langchain`/`openai`) to keep chapter environments reproducible.
3. `getpass.getpass()` is the book's preferred way to supply the API key interactively in a notebook, though an `OPENAI_API_KEY` environment variable read via `os.getenv` works too.
4. `PromptTemplate | llm` works because both implement the `Runnable` interface — this is the mechanical basis for every LCEL chain in the book.
5. GPT-5-nano is used throughout for low-cost experimentation; swap to GPT-5-mini or GPT-5 for higher accuracy.

## Connects To
- **Ch 1**: This appendix is the practical companion to getting started with LangChain — it operationalizes the concepts introduced in Ch 1 (models, prompts, chains) as runnable notebook code, and its prompt-template/LCEL examples are extended in Ch 2 and Ch 5.
