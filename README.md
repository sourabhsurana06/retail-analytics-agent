# Retail Analytics Agent

A from-scratch MCP (Model Context Protocol) server combining SQL query tools and RAG (Retrieval-Augmented Generation) into a single ReAct agent. Built without LangChain, LlamaIndex, or any agentic framework — just Python, Flask, FAISS, and the OpenAI API.

## What This Is

Most agentic AI tutorials either wrap everything in LangChain and hide what's actually happening, or demo a single tool (SQL or RAG) in isolation.

This project does neither. It builds a multi-tool MCP server where a reasoning agent decides in real time whether a question requires structured data retrieval (SQL), unstructured knowledge lookup (RAG), or both in sequence.

**Example:**

> "What is the return rate for each customer segment? Use the correct metric definition."

The agent:
1. Calls search_metrics — retrieves the Return Rate definition, learns cancelled orders must be excluded from both numerator and denominator
2. Calls get_schema — discovers actual table and column names
3. Calls run_sql with wrong case — gets zeros, self-corrects by checking distinct status values
4. Calls run_sql again with correct values — returns accurate rates per segment

No framework orchestrated that. The agent reasoned through it.

## Tools

| Tool | Type | Description |
|------|------|-------------|
| get_schema | SQL | Returns all table names, column names, and data types |
| run_sql | SQL | Executes a SELECT query, returns rows as JSON |
| list_metrics | RAG | Returns all metric names and one-line descriptions |
| search_metrics | RAG | Semantic search over the metrics glossary PDF |

## The Metrics Glossary

The RAG knowledge base is a PDF containing precise business metric definitions with inclusion/exclusion rules. These are the distinctions a naive agent would get wrong without it:

- Return Rate: cancelled orders excluded from both numerator and denominator
- LTV Gross: returned orders included — this is a demand-side metric
- LTV Net: returned orders netted to zero — this is the revenue-side metric
- Category Affinity: returned items excluded — a return signals category rejection
- Recent Purchase Activity: returned orders included — engagement, not revenue

## Dataset

Synthetic Indian retail database:

- 15 customers across 6 cities, segmented into Premium / Standard / Budget
- 15 products across 8 categories with rupee-denominated pricing
- 90 orders across 2024 with statuses: Completed / Returned / Pending
- 222 line items with quantity and discount percentage

Seeded deterministically (random.seed(42)) — results are reproducible.

## Quickstart

### 1. Clone and install

git clone https://github.com/sourabhsurana06/retail-analytics-agent
cd retail-analytics-agent
pip install -r requirements.txt

### 2. Set up environment

cp .env.example .env
# Add your OPENAI_API_KEY

### 3. Build the database and vector index

python3 core/CreateDB.py
python3 build_index.py

### 4. Start the MCP server

python3 server.py

### 5. Run the agent (second terminal)

python3 agent.py

## Project Structure

retail-analytics-agent/
├── core/
│   ├── __init__.py
│   ├── database.py
│   ├── CreateDB.py
│   ├── sql_tools.py
│   ├── rag_tools.py
│   └── retail_analytics_metric_list.pdf
├── data/                  (gitignored — generated files)
├── agent.py
├── server.py
├── build_index.py
├── requirements.txt
├── .env.example
└── .gitignore

## What This Is Not

- Not production-ready (SQLite, no auth, single-threaded Flask dev server)
- Not a framework demo — no LangChain, no LlamaIndex, no AutoGen
- Not complete (no streaming, no async, no retry logic)

It is a learning system that shows exactly what is happening at each step.

## License

MIT
