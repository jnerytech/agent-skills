# Appendix B: Setting up a Jupyter Notebook environment

## Core Idea
Sets up an isolated Python environment and a running Jupyter Notebook so the book's LangChain code examples can be executed and iterated on interactively.

## Key Concepts
- **Jupyter Notebook**: an interactive space for typing and running code cells, seeing results immediately, and tweaking code in place.
- **venv**: Python's built-in tool for creating a self-contained virtual environment per project, avoiding package version conflicts across projects.
- **requirements.txt**: the book repo's pinned list of Jupyter and LangChain packages, installed in one step into the activated virtual environment.

## Code Examples
```bash
# Create a project folder and a virtual environment inside it
python -m venv env_ch01

# Activate the virtual environment (Windows)
.\env_ch01\Scripts\activate

# Upgrade pip before installing packages
python -m pip install --upgrade pip

# Install Jupyter + LangChain packages from the book's requirements.txt
pip install -r requirements.txt

# Optional: confirm installed packages
pip list

# Launch Jupyter Notebook
jupyter notebook
```
- **What it demonstrates**: the full path from a bare Python install to a running notebook server, ready for a new `langchain_examples.ipynb` notebook (File > New > Notebook, then File > Rename).

## Key Takeaways
1. Use Python 3.11+ and a dedicated `venv` per chapter/project folder to keep dependencies isolated and reproducible.
2. Always upgrade `pip` before installing from `requirements.txt` to avoid installation issues.
3. Install packages from the book's own `requirements.txt` (GitHub repo or code zip) rather than installing LangChain/Jupyter ad hoc, to match the versions the examples were written against.
4. In Jupyter, use Ctrl+Enter to execute a cell in place.

## Connects To
- **Chapter code examples**: this environment is the prerequisite runtime for executing every LangChain/LangGraph/MCP code snippet in the book's notebooks.
