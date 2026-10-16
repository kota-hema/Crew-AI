# Campus Cafe Launch Brief

A CrewAI team researches a proposed university cafe, calculates a transparent monthly break-even point, drafts a Dean-ready brief, and subjects it to sustainability and skeptical review. LangChain provides a no-key web-search tool and a calculator tool.

## Dataset

The Kaggle CSV is included at `data/raw/student_spending.csv`; its original download is `data/raw/student-spending-dataset.zip`. The dataset creator explicitly describes all 1,000 rows as fictional. It is included for data-ingestion practice only and must not be used as evidence of real student behavior. See [data/raw/README.md](data/raw/README.md).

## Run

Use Python 3.10 through 3.13. Create and activate a virtual environment, then install the project:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Start the Streamlit interface with:

```bash
streamlit run app.py
```

Enter an OpenAI API key in the sidebar for a live run. It is used for that run and is not saved to project files. Choose sequential or hierarchical orchestration. The committed example brief is shown before running agents.

The command-line runner is also available. Set `OPENAI_API_KEY` in the environment, then run:

```bash
campus-cafe-brief --process sequential
```

The supported process choices are `sequential` (default) and `hierarchical`. Both write the Skeptical Reviewer's output to `final_brief.md`. The hierarchical mode also needs an LLM model supported by CrewAI for its manager; configure it with `CAMPUS_CAFE_MODEL` (default `openai/gpt-4o-mini`). Web search requires an internet connection. Tool errors are returned to the agents as errors, not as research findings.

Install test dependencies and run the local calculator tests:

```bash
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
```

The committed [final_brief.md](final_brief.md) is a conservative example. Running the crew replaces it with a newly researched and reviewed version. The collaboration reflection is in [reflection.md](reflection.md).