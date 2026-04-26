#!/usr/bin/env python3
"""
run.py — entry point.

Usage:
    python3 run.py 'Plan meals for the week'
    python3 run.py 'Taco night, lasagna, something with salmon' --model claude-sonnet-4-6
    python3 run.py save-recipe https://www.instagram.com/reel/...
    python3 run.py save-recipe https://www.tiktok.com/... "Grandma's Tacos"
"""

import argparse
import subprocess
import sys
from pathlib import Path

from agent import run

_TOOLS = Path(__file__).parent / "tools"


def main() -> None:
    parser = argparse.ArgumentParser(description="Household meal planning agent (Sous)")
    sub = parser.add_subparsers(dest="command")

    # ── run ────────────────────────────────────────────────────────────────
    run_p = sub.add_parser("run", help="Generate a meal plan and grocery list")
    run_p.add_argument("request", help="Natural-language meal planning request")
    run_p.add_argument("--model", default="claude-opus-4-6", help="Claude model ID")
    run_p.add_argument("--skill", default="meal-planner", help="Skill to activate")

    # ── save-recipe ────────────────────────────────────────────────────────
    save_p = sub.add_parser("save-recipe", help="Extract and save a recipe from a video URL")
    save_p.add_argument("url", help="Instagram, TikTok, or YouTube URL")
    save_p.add_argument("name", nargs="?", default="", help="Optional recipe name hint")

    # Bare invocation: python3 run.py 'request' → treated as run
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "save-recipe", "-h", "--help"):
        sys.argv.insert(1, "run")

    args = parser.parse_args()

    if args.command == "save-recipe":
        cmd = [sys.executable, str(_TOOLS / "save-recipe-video"), args.url]
        if args.name:
            cmd.append(args.name)
        subprocess.run(cmd)
        return

    run_dir = run(request=args.request, model=args.model, skill=args.skill)

    grocery_list = run_dir / "grocery-list.md"
    if grocery_list.exists():
        print("\n" + "=" * 60)
        print(grocery_list.read_text())
        print("=" * 60)
    else:
        print(f"\nOutput written to {run_dir}")


if __name__ == "__main__":
    main()
