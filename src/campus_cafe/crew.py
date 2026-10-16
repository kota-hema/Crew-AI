"""CrewAI agents and explicitly connected tasks for the launch brief."""

import os

from crewai import Agent, Crew, Process, Task

from campus_cafe.tools import calculator_tool, web_search_tool


def build_crew(process_name: str = "sequential") -> Crew:
    model = os.getenv("CAMPUS_CAFE_MODEL", "openai/gpt-4o-mini")
    researcher = Agent(
        role="Market Researcher",
        goal="Find recent, relevant, verifiable evidence on student spending, cafe prices, and food-service trends.",
        backstory="You are a careful research librarian. You distinguish actual survey data from synthetic data and cite each factual claim with a source URL and date.",
        tools=[web_search_tool],
        llm=model,
        allow_delegation=False,
        verbose=True,
    )
    analyst = Agent(
        role="Financial Analyst",
        goal="Calculate a transparent monthly cafe break-even estimate and show every assumption and operation.",
        backstory="You are a conservative campus-operations analyst. You never present a planning assumption as observed data and verify every arithmetic result with your calculator.",
        tools=[calculator_tool],
        llm=model,
        allow_delegation=False,
        verbose=True,
    )
    writer = Agent(
        role="Marketing Writer",
        goal="Write a concise, persuasive, evidence-led launch brief for the Dean of Student Affairs.",
        backstory="You turn research and budgets into clear decisions for busy non-technical university leaders. You preserve citations and label assumptions plainly.",
        tools=[web_search_tool],
        llm=model,
        allow_delegation=False,
        verbose=True,
    )
    sustainability = Agent(
        role="Sustainability Officer",
        goal="Verify environmental and plant-based claims, identify tradeoffs, and prevent unsupported green claims.",
        backstory="You are an evidence-focused sustainability reviewer who distinguishes practical menu choices from measured environmental outcomes.",
        tools=[web_search_tool],
        llm=model,
        allow_delegation=False,
        verbose=True,
    )
    reviewer = Agent(
        role="Skeptical Reviewer",
        goal="Challenge the draft's claims, calculations, omissions, and risks, then deliver the corrected final brief.",
        backstory="You are an independent decision-quality reviewer. You remove weak claims, repair unsupported numbers, retain useful citations, and make uncertainty visible.",
        tools=[web_search_tool, calculator_tool],
        llm=model,
        allow_delegation=False,
        verbose=True,
    )

    research_task = Task(
        description=(
            "Research current, sourced evidence relevant to launching a cafe at a US university with 8,000 students. "
            "Use web search for student food/spending behavior, published cafe/menu pricing, and current sustainability or plant-forward food-service trends. "
            "Prefer primary or reputable sources; report publication dates, exact supported facts, and direct URLs. "
            "Separate national context from evidence about this campus, and state when evidence is unavailable. "
            "The included Kaggle dataset has 1,000 explicitly fictional rows: do not use it as evidence of real student spending. "
            "Do not invent sources or exact numbers. Return a short evidence ledger with claim, source, date, and limitation."
        ),
        expected_output="A concise evidence ledger with source URLs and caveats; clearly identify facts that cannot be established.",
        agent=researcher,
    )
    finance_task = Task(
        description=(
            "Build a monthly break-even estimate. Treat these as planning assumptions, not sourced observations: 8,000 enrolled students; "
            "$24,000 fixed monthly costs ($17,500 staffing including payroll load, $4,500 facilities/utilities, $2,000 maintenance and administration); "
            "$8.00 average transaction; variable food/packaging cost equal to 35% of sales; card processing equal to 3% of sales; and 22 open days per month. "
            "Use the calculator tool for every calculation, including rounding up with ceil(expression). Show contribution per transaction, monthly transactions to break even, and transactions per open day. "
            "Explain exclusions such as startup capital and local demand uncertainty."
        ),
        expected_output="A brief calculation worksheet with all assumptions, calculator expressions/results, and exclusions.",
        agent=analyst,
        context=[research_task],
    )
    draft_task = Task(
        description=(
            "Draft a one-page launch brief for the Dean from the research and financial outputs. "
            "Use plain, persuasive language, cite sourced facts inline with URLs, show the break-even arithmetic, and label every financial input as an assumption. "
            "Do not use the fictional Kaggle rows as evidence. Include a measured recommendation, key risks, and a small pilot/measurement proposal. "
            "No number may appear without an inline source or an explicit assumption label."
        ),
        expected_output="A polished Markdown draft of a one-page decision brief.",
        agent=writer,
        context=[research_task, finance_task],
    )
    sustainability_task = Task(
        description=(
            "Audit the draft's sustainability and plant-based statements against current, credible sources. "
            "Use search and return only verified claims with URLs, or say that a claim could not be verified. "
            "Note practical tradeoffs (availability, cost, waste measurement) without inventing numbers."
        ),
        expected_output="A brief sustainability fact-check with source links, proposed corrections, and any unresolved claim.",
        agent=sustainability,
        context=[research_task, draft_task],
    )
    review_task = Task(
        description=(
            "Critically review the draft, evidence ledger, financial worksheet, and sustainability audit. "
            "Identify and fix weak or unsupported claims, unsupported numbers, arithmetic errors, missing risks, and overconfident conclusions. "
            "Use the calculator tool to independently verify the break-even figures. Do not invent citations; remove claims that cannot be sourced. "
            "Return only the final one-page Markdown brief, suitable for the Dean, with sources and explicit assumptions."
        ),
        expected_output="The final corrected, cited, one-page Markdown launch brief.",
        agent=reviewer,
        context=[research_task, finance_task, draft_task, sustainability_task],
    )

    process = Process.hierarchical if process_name == "hierarchical" else Process.sequential
    options = {"manager_llm": model} if process is Process.hierarchical else {}
    return Crew(
        agents=[researcher, analyst, writer, sustainability, reviewer],
        tasks=[research_task, finance_task, draft_task, sustainability_task, review_task],
        process=process,
        verbose=True,
        **options,
    )