"""
Post-tool-use hook — scans web-fetched content for prompt injection
before it re-enters the agent's context.

Wired in .claude/settings.json under hooks.PostToolUse.
Only activates when the tool is a web-fetch variant.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents', 'hanuman'))

WEB_TOOLS = {
    "WebFetch", "mcp__firecrawl__scrape", "mcp__agent_reach__read",
    "mcp__playwright__navigate", "mcp__agent_browser__snapshot"
}

def main():
    try:
        tool_result = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = tool_result.get("tool_name", "")

    if tool_name in WEB_TOOLS:
        try:
            from sanitizer import sanitize_web_content
            output = str(tool_result.get("output", ""))
            url = tool_result.get("tool_input", {}).get("url", "unknown")
            cleaned, findings = sanitize_web_content(output, url)

            if findings:
                tool_result["output"] = cleaned
                tool_result["_sanitizer_findings"] = findings

        except ImportError:
            pass  # sanitizer not available, pass through unchanged

    print(json.dumps(tool_result))

if __name__ == "__main__":
    main()
