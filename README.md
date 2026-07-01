{\rtf1\ansi\ansicpg1252\cocoartf2870
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\froman\fcharset0 Times-Bold;\f1\froman\fcharset0 Times-Roman;}
{\colortbl;\red255\green255\blue255;\red32\green36\blue45;\red167\green0\blue20;\red16\green19\blue24;
\red108\green0\blue181;\red0\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c16863\c18824\c23137;\cssrgb\c72157\c3922\c9412;\cssrgb\c7843\c9412\c12157;
\cssrgb\c50588\c0\c76078;\cssrgb\c0\c0\c0;}
\paperw11900\paperh16840\margl1440\margr1440\vieww40420\viewh25260\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\b\fs24 \cf2 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 #\cf3 \strokec3  Retail Analytics Agent
\f1\b0 \cf4 \strokec4 \
\
A from-scratch implementation of an MCP (Model Context Protocol) server combining \
\pard\pardeftab720\partightenfactor0
\cf2 \strokec2 **\cf4 \strokec4 SQL query tools\cf2 \strokec2 **\cf4 \strokec4  and \cf2 \strokec2 **\cf4 \strokec4 RAG (Retrieval-Augmented Generation)\cf2 \strokec2 **\cf4 \strokec4  into a single ReAct \
agent. Built without LangChain, LlamaIndex, or any agentic framework \'97 just Python, \
Flask, FAISS, and the OpenAI API.\
\
\cf2 \strokec2 ---\cf4 \strokec4 \
\
\pard\pardeftab720\partightenfactor0

\f0\b \cf2 \strokec2 ##\cf3 \strokec3  What This Is
\f1\b0 \cf4 \strokec4 \
\
Most agentic AI tutorials either wrap everything in LangChain and hide what's actually \
happening, or demo a single tool (SQL \cf2 \strokec2 *\cf4 \strokec4 or\cf2 \strokec2 *\cf4 \strokec4  RAG) in isolation.\
\
This project does neither. It shows how to build a \cf2 \strokec2 **\cf4 \strokec4 multi-tool MCP server\cf2 \strokec2 **\cf4 \strokec4  where a \
reasoning agent decides \'97 in real time \'97 whether a question requires structured data \
retrieval (SQL), unstructured knowledge lookup (RAG), or both in sequence.\
\
\pard\pardeftab720\partightenfactor0
\cf2 \strokec2 **\cf4 \strokec4 Example:\cf2 \strokec2 **\cf4 \strokec4 \
\
\cf2 \strokec2 >\cf4 \strokec4  \cf2 \strokec2 *\cf4 \strokec4 "What is the return rate for each customer segment? Use the correct metric definition."\cf2 \strokec2 *\cf4 \strokec4 \
\
The agent:\
\cf2 \strokec2 1.\cf4 \strokec4  Calls \cf5 \strokec5 `search_metrics`\cf4 \strokec4  \uc0\u8594  retrieves the Return Rate definition, learns cancelled \
   orders must be excluded from both numerator and denominator\
\cf2 \strokec2 2.\cf4 \strokec4  Calls \cf5 \strokec5 `get_schema`\cf4 \strokec4  \uc0\u8594  discovers actual table and column names\
\cf2 \strokec2 3.\cf4 \strokec4  Calls \cf5 \strokec5 `run_sql`\cf4 \strokec4  with wrong case \uc0\u8594  gets zeros, self-corrects by checking distinct \
   status values\
\cf2 \strokec2 4.\cf4 \strokec4  Calls \cf5 \strokec5 `run_sql`\cf4 \strokec4  again with correct values \uc0\u8594  returns accurate rates per segment\
\
No framework orchestrated that. The agent reasoned through it.\
\
\cf2 \strokec2 ---\cf4 \strokec4 \
\
\pard\pardeftab720\partightenfactor0

\f0\b \cf2 \strokec2 ##\cf3 \strokec3  Architecture
\f1\b0 \cf4 \strokec4 \
\pard\pardeftab720\sa240\partightenfactor0
\cf0 \strokec6 \uc0\u9484 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9488 \u8232 \u9474  agent.py \u9474 \u8232 \u9474  ReAct Loop (Thought\u8594 Action\u8594 Observation) \u9474 \u8232 \u9492 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9516 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9496 \u8232 \u9474  HTTP POST /execute\u8232 \u9660 \u8232 \u9484 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9488 \u8232 \u9474  server.py \u9474 \u8232 \u9474  Flask MCP Server (:8000) \u9474 \u8232 \u9474  \u9474 \u8232 \u9474  GET /health GET /tools POST /execute \u9474 \u8232 \u9492 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9516 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9516 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9496 \u8232 \u9474  \u9474 \u8232 \u9660  \u9660 \u8232 \u9484 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9488  \u9484 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9488 \u8232 \u9474  core/sql_tools \u9474  \u9474  core/rag_tools \u9474 \u8232 \u9474  \u9474  \u9474  \u9474 \u8232 \u9474  get_schema() \u9474  \u9474  list_metrics() \u9474 \u8232 \u9474  run_sql() \u9474  \u9474  search_metrics() \u9474 \u8232 \u9492 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9516 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9496  \u9492 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9516 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9496 \u8232 \u9474  \u9474 \u8232 \u9660  \u9660 \u8232 \u9484 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9488  \u9484 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9488 \u8232 \u9474  data/retail.db \u9474  \u9474  data/index.faiss \u9474 \u8232 \u9474  (SQLite) \u9474  \u9474  data/metrics_glossary.pdf \u9474 \u8232 \u9474  \u9474  \u9474  (FAISS + MiniLM-L6-v2) \u9474 \u8232 \u9492 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9496  \u9492 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9496 \
\pard\pardeftab720\partightenfactor0
\cf4 \strokec4 \
**Key design principle:** The agent has zero knowledge of SQLite, FAISS, or any \
implementation detail. It only knows there is an MCP server with tools it can call \
over HTTP. Swap the database or vector store \'97 the agent doesn't change.\
\
---\
\
## Tools\
\
| Tool | Type | Description |\
|------|------|-------------|\
| `get_schema` | SQL | Returns all table names, column names, and data types |\
| `run_sql` | SQL | Executes a SELECT query, returns rows as JSON |\
| `list_metrics` | RAG | Returns all metric names and one-line descriptions |\
| `search_metrics` | RAG | Semantic search over the metrics glossary PDF |\
\
---\
\
## The Metrics Glossary\
\
The RAG knowledge base is a PDF containing precise business metric definitions with \
inclusion/exclusion rules. These are the distinctions a naive agent would get wrong \
without it:\
\
- **Return Rate**: cancelled orders excluded from *both* numerator and denominator\
- **LTV Gross**: returned orders *included* \'97 this is a demand-side metric\
- **LTV Net**: returned orders netted to zero \'97 this is the revenue-side metric  \
- **Category Affinity**: returned items *excluded* \'97 a return signals category rejection\
- **Recent Purchase Activity**: returned orders *included* \'97 engagement, not revenue\
\
These distinctions live in the glossary. The agent retrieves the right definition \
before writing SQL, producing answers that are definitionally correct, not just \
computationally correct.\
\
---\
\
## Dataset\
\
Synthetic Indian retail database:\
\
- **15 customers** across 6 cities, segmented into Premium / Standard / Budget\
- **15 products** across 8 categories with \uc0\u8377 -denominated pricing\
- **90 orders** across 2024 \'97 Completed / Returned / Pending\
- **222 line items** with quantity and discount percentage\
\
Seeded deterministically (`random.seed(42)`) \'97 results are reproducible.\
\
---\
\
## Quickstart\
\
### 1. Clone and install\
\
```bash\
git clone https://github.com/sourabhsurana06/retail-analytics-agent\
cd retail-analytics-agent\
pip install -r requirements.txt\
```\
\
### 2. Set up environment\
\
```bash\
cp .env.example .env\
# Add your OPENAI_API_KEY\
```\
\
### 3. Build the database and vector index\
\
```bash\
python3 core/CreateDB.py       # creates data/retail.db\
python3 build_index.py         # creates data/index.faiss and data/chunks.json\
```\
\
### 4. Start the MCP server\
\
```bash\
python3 server.py\
# \uc0\u8594  http://localhost:8000\
```\
\
### 5. Run the agent (second terminal)\
\
```bash\
python3 agent.py\
```\
\
---\
\
## Example Agent Runs\
\
**Pure RAG:**\
\pard\pardeftab720\sa240\partightenfactor0
\cf0 \strokec6 Q: How is Return Rate defined and what orders should be excluded?\
\uc0\u8594  search_metrics("return rate definition")\u8232 \u8592  Definition retrieved: order-level metric, cancelled orders excluded from\u8232 both numerator and denominator\u8232 Final Answer: Return Rate = returned orders / completed orders. Cancelled\u8232 orders excluded from both sides.\
\pard\pardeftab720\partightenfactor0
\cf4 \strokec4 \
**Hybrid SQL + RAG:**\
\pard\pardeftab720\sa240\partightenfactor0
\cf0 \strokec6 Q: What is the return rate for each segment? Use the correct definition.\
\uc0\u8594  search_metrics("how is return rate calculated")\u8232 \u8594  get_schema()\u8232 \u8594  run_sql() [wrong case \u8594  zeros]\u8232 \u8594  run_sql("SELECT DISTINCT status FROM orders") [self-correction]\u8232 \u8594  run_sql() [correct case \u8594  accurate results]\u8232 Final Answer: Budget 11.76% | Premium 35% | Standard 72.73%\
\pard\pardeftab720\partightenfactor0
\cf4 \strokec4 \
---\
\
## Project Structure\
\pard\pardeftab720\sa240\partightenfactor0
\cf0 \strokec6 retail-analytics-agent/\uc0\u8232 \u9500 \u9472 \u9472  core/\u8232 \u9474  \u9500 \u9472 \u9472  
\f0\b init
\f1\b0 .py\uc0\u8232 \u9474  \u9500 \u9472 \u9472  database.py \u8592  DB path + connection helper\u8232 \u9474  \u9500 \u9472 \u9472  CreateDB.py \u8592  schema creation + seed data\u8232 \u9474  \u9500 \u9472 \u9472  sql_tools.py \u8592  get_schema(), run_sql()\u8232 \u9474  \u9500 \u9472 \u9472  rag_tools.py \u8592  list_metrics(), search_metrics()\u8232 \u9474  \u9492 \u9472 \u9472  retail_analytics_metric_list.pdf \u8592  metrics glossary (RAG source)\u8232 \u9474 \u8232 \u9500 \u9472 \u9472  data/ \u8592  generated files (gitignored)\u8232 \u9474  \u9500 \u9472 \u9472  retail.db\u8232 \u9474  \u9500 \u9472 \u9472  index.faiss\u8232 \u9474  \u9492 \u9472 \u9472  chunks.json\u8232 \u9474 \u8232 \u9500 \u9472 \u9472  agent.py \u8592  ReAct agent (OpenAI GPT-4o)\u8232 \u9500 \u9472 \u9472  server.py \u8592  Flask MCP server (4 tools, 3 endpoints)\u8232 \u9500 \u9472 \u9472  build_index.py \u8592  one-time FAISS index builder\u8232 \u9500 \u9472 \u9472  requirements.txt\u8232 \u9500 \u9472 \u9472  .env.example\u8232 \u9492 \u9472 \u9472  .gitignore\
\pard\pardeftab720\partightenfactor0
\cf4 \strokec4 \
---\
\
## Extending This\
\
**Add a new SQL tool:** write a function in `core/sql_tools.py`, register it in \
`server.py`, and the agent discovers it automatically on next startup.\
\
**Add a new document to RAG:** drop a PDF into `data/`, update `build_index.py` \
to include it, rerun `python3 build_index.py`.\
\
**Swap the LLM:** change the client in `agent.py`. The MCP server is model-agnostic.\
\
---\
\
## What This Is Not\
\
- Not production-ready (SQLite, no auth, single-threaded Flask dev server)\
- Not a framework demo \'97 no LangChain, no LlamaIndex, no AutoGen\
- Not complete (no streaming, no async, no retry logic)\
\
It is a **learning system** that shows exactly what's happening at each step.\
\
---\
\
## License\
\
MIT\
}