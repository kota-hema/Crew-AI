"""Run the cafe launch brief crew and save the reviewed result."""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from campus_cafe.crew import build_crew


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Research and write a campus cafe launch brief.")
    parser.add_argument("--process", choices=("sequential", "hierarchical"), default="sequential")
    arguments = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        parser.error("Set OPENAI_API_KEY before running the crew.")

    result = build_crew(arguments.process).kickoff(inputs={"student_count": 8000})
    brief = str(result).strip()
    if not brief:
        raise RuntimeError("The reviewer returned an empty brief.")
    if "http://" not in brief and "https://" not in brief:
        raise RuntimeError("The final brief contains no source URLs; refusing to overwrite final_brief.md.")

    output_path = Path.cwd() / "final_brief.md"
    output_path.write_text(f"{brief}\n", encoding="utf-8")
    print(f"Saved reviewed brief to {output_path}")