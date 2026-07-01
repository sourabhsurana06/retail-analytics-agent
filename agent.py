import json
import re
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = "http://localhost:8000"
MAX_ITERATIONS = 10
MODEL          = "gpt-4o"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def check_server_health():
    try:
        r = requests.get(f"{MCP_SERVER_URL}/health", timeout=3)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def fetch_tools_manifest():
    r = requests.get(f"{MCP_SERVER_URL}/tools", timeout=5)
    r.raise_for_status()
    return r.json()["tools"]

def call_tool(tool_name, inputs):
    r = requests.post(f"{MCP_SERVER_URL}/execute", json={"tool": tool_name, "inputs": inputs}, timeout=15)
    r.raise_for_status()
    return r.json()

def build_system_prompt(tools):
    tools_description = ""
    for tool in tools:
        tools_description += f"\nTool: {tool['name']}\n"
        tools_description += f"Description: {tool['description']}\n"
        if tool["inputs"]:
            for name, spec in tool["inputs"].items():
                tools_description += f"  - {name} ({spec['type']}): {spec['description']}\n"
        else:
            tools_description += "  Inputs: none required\n"

    return f"""You are a retail analytics agent with access to two knowledge sources:
1. A structured SQLite retail database (customers, orders, products, order_items)
2. A metrics glossary defining how business metrics should be calculated

Use the ReAct pattern — Thought / Action / Observation — until you have a Final Answer.

Available tools:
{tools_description}

DECISION RULES:
- Question about metric DEFINITION or CALCULATION RULES → search_metrics
- Question about ACTUAL DATA → get_schema then run_sql
- Question needing BOTH → search_metrics first for rules, then get_schema + run_sql

SQL RULES:
- Always call get_schema before writing SQL
- SELECT only — no writes
- Fix SQL errors using the error message in the next iteration

Action format — one line, valid JSON:
Action: {{"tool": "get_schema", "inputs": {{}}}}
Action: {{"tool": "run_sql", "inputs": {{"query": "SELECT ..."}}}}
Action: {{"tool": "list_metrics", "inputs": {{}}}}
Action: {{"tool": "search_metrics", "inputs": {{"query": "your question about the metric"}}}}

End with: Final Answer: <your answer>
"""

def parse_action(text):
    match = re.search(r"Action:\s*(\{.*\})", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None

def run_agent(question):
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}\n")

    tools         = fetch_tools_manifest()
    system_prompt = build_system_prompt(tools)
    messages      = [{"role": "user", "content": question}]

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"--- Iteration {iteration} ---")
        response       = client.responses.create(model=MODEL, instructions=system_prompt, input=messages)
        assistant_text = response.output_text
        print(f"Agent:\n{assistant_text}\n")
        messages.append({"role": "assistant", "content": assistant_text})

        if "Final Answer:" in assistant_text:
            final = assistant_text.split("Final Answer:")[-1].strip()
            print(f"\n{'='*60}")
            print(f"FINAL ANSWER: {final}")
            print(f"{'='*60}\n")
            return final

        action = parse_action(assistant_text)
        if not action:
            observation = "No valid Action found. Include a correctly formatted Action line."
        else:
            tool_name = action.get("tool")
            inputs    = action.get("inputs", {})
            print(f"→ Calling tool: {tool_name} | inputs: {inputs}")
            try:
                result      = call_tool(tool_name, inputs)
                observation = json.dumps(result, indent=2)
            except Exception as e:
                observation = f"ERROR: {str(e)}"
            preview = observation[:400] + ("..." if len(observation) > 400 else "")
            print(f"← Observation: {preview}\n")

        messages.append({"role": "user", "content": f"Observation: {observation}"})

    return "Max iterations reached without a final answer."

if __name__ == "__main__":
    if not check_server_health():
        print("ERROR: MCP server not running. Start with: python3 server.py")
        exit(1)

    print("Server healthy. Running agent.\n")

    questions = [
        "How is Return Rate defined and what orders should be excluded?",
        "Which city has the highest number of customers?",
        "What is the return rate for each customer segment? Use the correct metric definition.",
        "Who are the top 5 customers by LTV Gross? Use the correct metric definition.",
    ]

    for q in questions:
        run_agent(q)