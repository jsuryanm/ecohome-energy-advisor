# EcoHome Energy Advisor

An agentic AI assistant that helps homeowners understand and optimize their home
energy use. It answers questions about historical energy consumption, solar
generation, electricity pricing, and weather, and gives grounded energy-saving
advice by retrieving from a small knowledge base of best practices.

The agent is a **LangChain tool-calling (ReAct) agent**: given a natural-language
question, it decides which tool(s) to call, runs them, and synthesizes a grounded
answer. Its retrieval-and-answer quality and its tool-selection behaviour are both
evaluated with **Ragas**.

## What it does

- **Query energy usage** from a SQLite database (by date range, optionally per device type).
- **Query solar generation** history (production, weather, irradiance).
- **Summarize recent energy** use and generation across devices.
- **Look up weather forecasts** and **time-of-use electricity prices** (mocked data sources).
- **Search energy-saving tips** via RAG over best-practice documents.
- **Estimate savings** (kWh, $, %) from a proposed optimization.

## Tech stack

| Layer | Choice |
| --- | --- |
| Orchestration | LangGraph (`create_react_agent`) |
| LLM | Groq (if `GROQ_API_KEY` set) with OpenAI `gpt-4o-mini` fallback |
| Tools / framework | LangChain (`@tool`) |
| Vector store | Chroma (`langchain-chroma`) |
| Embeddings | OpenAI `text-embedding-3-small` |
| Database / ORM | SQLite via SQLAlchemy |
| Evaluation | Ragas 0.4.3 (`ragas.metrics.collections`) |
| Runtime | Python 3.12 |

## Project structure

```
.
├── 01_db_setup.ipynb          # Create SQLite schema + seed sample energy/solar data
├── 02_rag_setup.ipynb         # Build & persist the Chroma vector store from tip docs
├── 03_run_and_evaluate.ipynb  # Run the agent + evaluate with Ragas (RAG + trajectory)
├── agent.py                   # EcoHomeAgent: LangGraph ReAct agent over the tool kit
├── tools.py                   # The 7 agent tools (DB queries, weather, pricing, RAG, savings)
├── models/
│   └── energy.py              # SQLAlchemy models + DatabaseManager
├── data/
│   ├── documents/             # Source knowledge-base text files
│   ├── energy_data.db          # (generated) SQLite database
│   └── vectorstore/            # (generated) persisted Chroma store
├── requirements.txt
├── pyproject.toml
└── .env                        # API keys (not committed)
```

## How the pieces fit together

1. `01_db_setup.ipynb` populates `data/energy_data.db` with ~30 days of synthetic
   hourly energy-usage and solar-generation records.
2. `02_rag_setup.ipynb` loads the two tip documents, chunks them, embeds the chunks,
   and persists them to `data/vectorstore` (Chroma). The agent's `search_energy_tips`
   tool reads this store back at runtime.
3. `agent.py` builds a LangGraph ReAct agent over the seven tools in `tools.py` with
   a system prompt that tells it to ground every answer in tool output.
4. `03_run_and_evaluate.ipynb` runs the agent and evaluates it (see below).

## Evaluation

Evaluation lives in `03_run_and_evaluate.ipynb` and uses the modern Ragas 0.4.x
**collections API** (`from ragas.metrics.collections import ...`, async
`await metric.ascore(...)`, with `llm_factory` / `embedding_factory` over an
`AsyncOpenAI` client).

**Part A - RAG quality.** A small retrieve-then-answer pipeline over the energy-tips
knowledge base is scored on:

- **Faithfulness** - is the answer grounded in the retrieved context?
- **Answer Relevancy** - does the answer actually address the question?
- **Context Precision** - is the retrieved context relevant (vs. a reference answer)?
- **Factual Correctness** - F1 of the answer's claims against a reference answer.

**Part B - Agent trajectory.** Whether the agent routes each query to the correct
tool, scored two ways:

- **Trajectory match** - deterministic check that the expected tool appears in the
  agent's tool-call sequence (robust to argument differences).
- **Ragas `ToolCallAccuracy`** - converts the LangGraph message trace via
  `convert_to_ragas_messages` and compares against reference `ToolCall`s. This is
  stricter: it scores tool *name* and *arguments*, so dynamic args (e.g. dates) can
  legitimately lower the score.

Results are collected into pandas DataFrames with per-question rows and mean scores.

## Setup & run

### 1. Environment

Requires Python 3.12. Using [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv sync
```

Or with pip:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

> Ragas 0.4.3 is required for the collections API used in the evaluation notebook
> (`pip install "ragas>=0.4.3"` if your lockfile pins an older version).

### 2. API keys

Copy `.env.example` to `.env` and fill in:

```
OPENAI_API_KEY=sk-...          # required (embeddings + Ragas evaluator; default LLM)
# GROQ_API_KEY=...             # optional; if set, the agent uses Groq instead of OpenAI
# OPEN_WEATHER_MAP_API_KEY=... # optional; weather/pricing tools currently use mock data
```

### 3. Run the notebooks in order

```
01_db_setup.ipynb   ->   02_rag_setup.ipynb   ->   03_run_and_evaluate.ipynb
```

You can also smoke-test the agent directly:

```bash
python agent.py
```

## Notes

- The weather and electricity-pricing tools return realistic **mock** data; swap in a
  real API (e.g. OpenWeatherMap) without changing the agent.
- `search_energy_tips` lazily builds the vector store on first use if `02_rag_setup`
  hasn't been run, but running the notebook first is recommended for a clean build.
- The embedding model is pinned (`text-embedding-3-small`) in both `tools.py` and
  `02_rag_setup.ipynb` so the store is written and read in the same embedding space.