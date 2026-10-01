"""
CrewAI Travel Planner Agent
---------------------------
Asks the user for a city, then a single Travel Planner agent suggests
exactly 3 places to visit there.

Setup:
    OPENAI_API_KEY  - your OpenAI API key (required, read from the environment)
    MODEL           - model name, e.g. "openai/gpt-4o-mini" (optional)

Run:
    python travel_planner.py
"""

import os
import sys

from crewai import Agent, Crew, Task

# Optional: load variables from a local .env file if python-dotenv is installed.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# The API key is always read from the environment - never hard-coded.
if not os.getenv("OPENAI_API_KEY"):
    sys.exit(
        "Error: OPENAI_API_KEY is not set.\n"
        "Set it first, e.g.\n"
        '  PowerShell:   $env:OPENAI_API_KEY="your-key"\n'
        '  macOS/Linux:  export OPENAI_API_KEY="your-key"\n'
        "or put it in a .env file (see .env.example)."
    )

# CrewAI reads MODEL from the environment; fall back to a sensible default.
os.environ.setdefault("MODEL", "openai/gpt-4o-mini")

# lstrip removes a stray byte-order mark that some terminals add to piped input.
city = input("Which city? ").strip().lstrip("﻿")
if not city:
    sys.exit("Please enter a city name.")

planner = Agent(
    role="Local Travel Planner",
    goal=(
        "Recommend the three most worthwhile places to visit in {city}, "
        "each with a short, practical tip a first-time visitor can act on."
    ),
    backstory=(
        "You are a seasoned travel planner who has spent years guiding "
        "first-time visitors on short city breaks. Your readers have only a "
        "day or two and no patience for long guidebook prose, so you pick "
        "only the places that truly define a city and describe each one in "
        "a single crisp line. You always add one useful tip, such as the "
        "best time to go, and you never pad your answer with introductions "
        "or closing remarks."
    ),
    verbose=True,
)

task = Task(
    description=(
        "The traveller is visiting {city}. Suggest exactly 3 places to visit "
        "in {city}. Choose well-known, genuinely distinct spots that are "
        "actually located in {city}. For each place, give its name and one "
        "short line describing what makes it special, plus a quick tip."
    ),
    expected_output=(
        "Exactly 3 lines and nothing else - no title, introduction or "
        "conclusion. Each line follows this format:\n"
        "<number>. <Place name> - <one short description with a quick tip>\n"
        "Example:\n"
        "1. Amber Fort - hilltop fort with mirrored halls, go early\n"
        "2. Hawa Mahal - the pink facade, best in morning light\n"
        "3. City Palace - royal courtyards and a textile museum"
    ),
    agent=planner,
)

crew = Crew(agents=[planner], tasks=[task], verbose=True)

result = crew.kickoff(inputs={"city": city})

print(f"\nTop 3 places to visit in {city}:")
print(result)
