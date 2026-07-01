from flask import Flask, request, jsonify
from core.sql_tools import get_schema, run_sql
from core.rag_tools import list_metrics, search_metrics

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

TOOLS_MANIFEST = {
    "tools": [
        {
            "name": "get_schema",
            "description": "Returns the full retail database schema: all table names, column names, and data types. Always call this before writing any SQL query.",
            "inputs": {}
        },
        {
            "name": "run_sql",
            "description": "Executes a SELECT SQL query against the retail database. Returns rows as a list of dicts. Only SELECT statements allowed. Results capped at 50 rows.",
            "inputs": {
                "query": {
                    "type": "string",
                    "required": True,
                    "description": "A valid SQLite SELECT statement."
                }
            }
        },
        {
            "name": "list_metrics",
            "description": "Returns all metric names and one-line descriptions from the metrics glossary. Call this first to check whether a metric definition exists.",
            "inputs": {}
        },
        {
            "name": "search_metrics",
            "description": "Semantic search over the metrics glossary. Use this to look up how a metric is defined, calculated, or what inclusion/exclusion rules apply.",
            "inputs": {
                "query": {
                    "type": "string",
                    "required": True,
                    "description": "Natural language query about a metric. Example: 'how is return rate calculated'"
                }
            }
        }
    ]
}

@app.route("/tools", methods=["GET"])
def tools():
    return jsonify(TOOLS_MANIFEST)

@app.route("/execute", methods=["POST"])
def execute():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"success": False, "error": "Request body must be valid JSON."}), 400
    tool_name = body.get("tool")
    if not tool_name:
        return jsonify({"success": False, "error": "Missing field: 'tool'."}), 400
    inputs = body.get("inputs", {})

    if tool_name == "get_schema":
        return jsonify(get_schema())
    elif tool_name == "run_sql":
        query = inputs.get("query")
        if not query:
            return jsonify({"success": False, "error": "Missing input: 'query'."}), 400
        return jsonify(run_sql(query))
    elif tool_name == "list_metrics":
        return jsonify(list_metrics())
    elif tool_name == "search_metrics":
        query = inputs.get("query")
        if not query:
            return jsonify({"success": False, "error": "Missing input: 'query'."}), 400
        return jsonify(search_metrics(query))
    else:
        return jsonify({"success": False, "error": f"Unknown tool: '{tool_name}'."}), 404

if __name__ == "__main__":
    print("Starting Retail Analytics MCP Server on http://localhost:8000")
    print("Tools: get_schema | run_sql | list_metrics | search_metrics")
    app.run(host="0.0.0.0", port=8000, debug=True)