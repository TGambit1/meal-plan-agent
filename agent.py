"""
agent.py — single agentic loop for meal planning.

Follows the OpenClaw/Tradclaw workspace architecture: loads bootstrap files
(AGENTS.md, SOUL.md, IDENTITY.md, USER.md, MEMORY.md) to build the system
prompt, then runs a single tool-use loop. CLI tools in tools/ read from
markdown resources in resources/. State written to output/<timestamp>/.
"""

from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, date

import anthropic

_ROOT      = Path(__file__).parent
_TOOLS_DIR = _ROOT / "tools"
_SKILLS_DIR = _ROOT / "skills"

# ── Bootstrap file loader ─────────────────────────────────────────────────────

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def _load_skill(skill_name: str) -> str:
    skill_file = _SKILLS_DIR / skill_name / "SKILL.md"
    if skill_file.exists():
        return f"\n\n---\n# Active Skill: {skill_name}\n\n{_read(skill_file)}"
    return ""


def build_system_prompt(skill: str = "meal-planner") -> str:
    """Load workspace bootstrap files in read order, then append the active skill."""
    sections = []

    for filename in ("SOUL.md", "IDENTITY.md", "USER.md"):
        content = _read(_ROOT / filename)
        if content:
            sections.append(content)

    memory = _read(_ROOT / "MEMORY.md")
    if memory:
        sections.append(f"# Long-term Memory\n\n{memory}")

    today     = date.today().isoformat()
    yesterday = date.fromordinal(date.today().toordinal() - 1).isoformat()
    for day in (yesterday, today):
        daily = _read(_ROOT / "memory" / f"{day}.md")
        if daily:
            sections.append(f"# Daily Memory ({day})\n\n{daily}")

    agents = _read(_ROOT / "AGENTS.md")
    if agents:
        sections.append(agents)

    sections.append(_load_skill(skill))

    return "\n\n---\n\n".join(sections)


# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "run_tool",
        "description": (
            "Run a CLI tool from the tools/ directory. "
            "Available tools: context, pantry, recipe <name>, save-recipe-video <url> [name-hint]. "
            "These read from markdown resource files — use them for all data lookups."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tool": {
                    "type": "string",
                    "description": "Tool name: context | pantry | recipe | save-recipe-video",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "CLI arguments passed to the tool",
                },
            },
            "required": ["tool"],
        },
    },
    {
        "name": "read_resource",
        "description": (
            "Read a workspace resource file. "
            "Paths are relative to the workspace root. "
            "Examples: resources/meal-plans/favorite-meals.md, resources/meal-plans/this-week.md, "
            "skills/meal-planner/SKILL.md"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path from workspace root"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": (
            "Write a file to the run directory. "
            "Use for PLAN.md, TODO.md, grocery-list.md, and other run outputs."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Filename within the run directory"},
                "content":  {"type": "string", "description": "Full file content"},
            },
            "required": ["filename", "content"],
        },
    },
    {
        "name": "read_file",
        "description": "Read a file from the current run directory (e.g. TODO.md to update checkboxes).",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
            },
            "required": ["filename"],
        },
    },
    {
        "name": "update_resource",
        "description": (
            "Write or overwrite a workspace resource file. "
            "Use to update resources/meal-plans/this-week.md or resources/shopping/groceries.md "
            "after a planning run so the household has a persistent current plan."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path":    {"type": "string", "description": "Relative path from workspace root"},
                "content": {"type": "string", "description": "Full file content"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "write_memory",
        "description": (
            "Write today's memory log to memory/YYYY-MM-DD.md. "
            "Call this at the end of a run to record what was planned, any notable constraints, "
            "and anything worth remembering for next time."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Memory log content in markdown"},
            },
            "required": ["content"],
        },
    },
]


# ── Tool execution ────────────────────────────────────────────────────────────

def execute_tool(name: str, inputs: dict, run_dir: Path) -> str:
    if name == "run_tool":
        tool   = inputs["tool"]
        args   = inputs.get("args", [])
        script = _TOOLS_DIR / tool
        if not script.exists():
            return f"Error: tool '{tool}' not found in tools/"
        try:
            result = subprocess.run(
                [sys.executable, str(script)] + [str(a) for a in args],
                capture_output=True, text=True, timeout=60,
            )
            return result.stdout or result.stderr or "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: tool timed out"

    if name == "read_resource":
        path = _ROOT / inputs["path"]
        if not path.exists():
            return f"Error: {inputs['path']} not found"
        return path.read_text(encoding="utf-8")

    if name == "write_file":
        path = run_dir / inputs["filename"]
        path.write_text(inputs["content"], encoding="utf-8")
        return f"Written: {inputs['filename']}"

    if name == "read_file":
        path = run_dir / inputs["filename"]
        if not path.exists():
            return f"Error: {inputs['filename']} not found"
        return path.read_text(encoding="utf-8")

    if name == "update_resource":
        path = _ROOT / inputs["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(inputs["content"], encoding="utf-8")
        return f"Updated: {inputs['path']}"

    if name == "write_memory":
        today  = date.today().isoformat()
        path   = _ROOT / "memory" / f"{today}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(inputs["content"], encoding="utf-8")
        return f"Memory saved: memory/{today}.md"

    return f"Error: unknown tool '{name}'"


# ── Agent loop ────────────────────────────────────────────────────────────────

def run(request: str, model: str = "claude-opus-4-6", skill: str = "meal-planner") -> Path:
    """Run the agent and return the run directory."""
    run_id  = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = _ROOT / "output" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    system   = build_system_prompt(skill=skill)
    client   = anthropic.Anthropic()
    messages = [{"role": "user", "content": request}]

    print(f"[agent] run={run_id}  skill={skill}  model={model}")

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system,
            tools=TOOLS,
            messages=messages,
        )

        tool_calls = []
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"[agent] {block.text.strip()[:120]}")
            elif block.type == "tool_use":
                tool_calls.append(block)

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            break

        if tool_calls:
            results = []
            for tc in tool_calls:
                print(f"[tool]  {tc.name}({json.dumps(tc.input)[:80]})")
                output = execute_tool(tc.name, tc.input, run_dir)
                results.append({
                    "type":        "tool_result",
                    "tool_use_id": tc.id,
                    "content":     output,
                })
            messages.append({"role": "user", "content": results})

    print(f"[agent] done → {run_dir}")
    return run_dir
