# EcoHome Energy Advisor

EcoHome Energy Advisor is a small AI project that helps answer home energy
questions. You can ask things like when to charge an electric vehicle, when to
run an appliance, or how to reduce electricity costs.

The project works by combining an OpenAI chat model with a set of local tools.
Those tools can read sample home energy data, check sample solar generation,
look up mock weather and electricity prices, search energy-saving documents, and
estimate savings.

This is a demonstration project. Weather and electricity prices are mocked, so
the answers are useful for learning how the solution works, not for making real
utility decisions.

## What This Project Does

- Answers home energy optimization questions in plain language.
- Uses tool calls to gather data before writing a recommendation.
- Stores sample energy and solar data in a local SQLite database.
- Stores energy-saving documents in a Chroma vector database for retrieval.
- Runs a set of test questions and creates an evaluation report.

Example questions:

- "When should I charge my electric car tomorrow?"
- "When should I run my dishwasher to save money?"
- "How can I make better use of my solar panels?"
- "What is the single most impactful way to lower my energy bill?"

## How The Solution Works

The project is split into three notebooks and a few Python files.

1. `01_db_setup.ipynb` creates `data/energy_data.db` and fills it with sample
   home energy usage and solar generation records.
2. `02_rag_setup.ipynb` loads the text files in `data/documents/`, splits them
   into chunks, creates embeddings, and saves them in a local Chroma vector
   store.
3. `03_run_and_evaluate.ipynb` creates the energy advisor agent, asks it several
   test questions, and evaluates the responses.
4. `agent.py` builds the LangChain agent that talks to the OpenAI model and uses
   the tools.
5. `tools.py` defines the seven tools the agent can call.
6. `models/energy.py` defines the SQLite tables and database helper methods.

At runtime, the flow looks like this:

```text
User question
    -> Agent decides which tool to use
    -> Tool reads database, vector store, mock weather, or mock price data
    -> Agent combines the tool results
    -> Final energy-saving answer is returned
```

## Project Files

```text
.
|-- 01_db_setup.ipynb          Create and populate the SQLite database
|-- 02_rag_setup.ipynb         Build the Chroma vector store from text documents
|-- 03_run_and_evaluate.ipynb  Run the agent and evaluate the results
|-- agent.py                   Creates the OpenAI-powered LangChain agent
|-- tools.py                   Contains the agent tools
|-- main.py                    Small starter file
|-- template.py                Creates the project file structure
|-- models/
|   |-- __init__.py
|   `-- energy.py              SQLAlchemy database models and manager
|-- data/
|   |-- energy_data.db         Local SQLite database
|   `-- documents/             Energy-saving text documents
|-- requirements.txt           pip dependency list
|-- pyproject.toml             uv/project dependency configuration
|-- .env.example               Example environment variable file
`-- README.md                  Project guide
```

## Tech Stack

| Technology | What it is used for |
| --- | --- |
| Python 3.12 | Main programming language |
| Jupyter Notebook | Step-by-step setup, running, and evaluation |
| LangChain / LangGraph | Agent workflow and tool calling |
| OpenAI / `langchain-openai` | Chat model and embeddings |
| SQLite | Local database for energy and solar data |
| SQLAlchemy | Python interface for the SQLite database |
| ChromaDB | Local vector store for energy-saving documents |
| Pandas / NumPy | Data handling and evaluation summaries |
| python-dotenv | Loading API keys from `.env` |

## Setup Instructions

These steps are written for Windows PowerShell.

### 1. Open the project folder

```powershell
cd "C:\Users\rsurs\OneDrive\Documents\Root\ecohome_solution"
```

### 2. Check Python

The project expects Python 3.12 or newer.

```powershell
python --version
```

### 3. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this command once in the same terminal:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

If you use `uv`, run:

```powershell
uv sync
```

If you use `pip`, run:

```powershell
pip install -r requirements.txt
```

### 5. Create the `.env` file

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and add your OpenAI API key:

```text
OPENAI_API_KEY=your_api_key_here
```

The OpenAI key is needed for the chat model and embeddings.

## How To Run The Project

Run the notebooks in this order:

```text
01_db_setup.ipynb
02_rag_setup.ipynb
03_run_and_evaluate.ipynb
```

The order matters:

1. The first notebook creates the database.
2. The second notebook creates the vector store.
3. The third notebook uses both of those resources to run the agent.

To open Jupyter Notebook from PowerShell:

```powershell
jupyter notebook
```

Then open each notebook in the browser and run the cells from top to bottom.

You can also open the project in VS Code and run the notebooks there. Make sure
the selected notebook kernel uses the `.venv` environment.

## How Evaluation Works

`03_run_and_evaluate.ipynb` includes a list of test questions for the energy
advisor. For each test case, the notebook:

1. Sends the question to the agent.
2. Saves the agent response and message trace.
3. Checks whether the answer is relevant and useful.
4. Checks whether the expected tools were used.
5. Builds a final report with scores and feedback.

The current evaluation uses simple Python heuristics. It checks things like
whether important words from the question and expected answer appear in the final
response, and whether expected tools are present in the tool trace.

This keeps the evaluation easy to understand for a beginner project. It is not a
perfect measurement of answer quality, but it gives a useful quick check.

## Troubleshooting

### `OPENAI_API_KEY` is missing

Make sure `.env` exists and contains:

```text
OPENAI_API_KEY=your_api_key_here
```

Also make sure the notebook was restarted after editing `.env`.

### The agent cannot find database records

Run `01_db_setup.ipynb` again from top to bottom. This recreates and fills the
local SQLite database.

### Search or document retrieval does not work

Run `02_rag_setup.ipynb` again from top to bottom. This rebuilds the local Chroma
vector store.

### `03_run_and_evaluate.ipynb` gives empty or poor results

Check that the first two notebooks were completed successfully. The evaluation
notebook depends on both the database and the vector store.

### PowerShell cannot activate `.venv`

Run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Notes

- Weather and electricity prices are mocked in `tools.py`.
- The sample database is local and safe to recreate.
- The vector store is built from the text files in `data/documents/`.
- This project is designed for learning agent tools, RAG, notebooks, and
  evaluation.
- For real-world use, replace the mock weather and price tools with real APIs.
