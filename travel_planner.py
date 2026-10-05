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

Flow:
    load_settings()  ->  ask_user_for_city()  ->  create_travel_planner_agent()
    ->  create_top_places_task()  ->  run_travel_crew()  ->  print the result
"""

import os
import sys

from crewai import Agent, Crew, Task

# Model used when the MODEL environment variable is not set.
DEFAULT_MODEL = "openai/gpt-4o-mini"


def load_settings():
    """Load the API key and model name from the environment.

    Reads a local .env file first (if python-dotenv is installed), then
    makes sure OPENAI_API_KEY exists and MODEL has a value. Exits with a
    helpful message if the API key is missing.
    """
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
    os.environ.setdefault("MODEL", DEFAULT_MODEL)


def ask_user_for_city():
    """Prompt the user for a city name and return it as a clean string.

    Exits if the user enters nothing.
    """
    # lstrip removes a stray byte-order mark that some terminals add to piped input.
    city_name = input("Which city? ").strip().lstrip("﻿")
    if not city_name:
        sys.exit("Please enter a city name.")
    return city_name


def create_travel_planner_agent():
    """Build the single agent that recommends places to visit.

    The role, goal and backstory tell the LLM who it is and how to write:
    short, practical suggestions for first-time visitors. {city} is a
    placeholder that CrewAI fills in when the crew is started.
    """
    return Agent(
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
        verbose=True,  # print the agent's reasoning while it works
    )


def create_top_places_task(travel_planner_agent):
    """Build the task that asks the agent for exactly 3 places in {city}.

    expected_output pins down the exact format (3 numbered lines, nothing
    else) so the answer stays short and easy to read.
    """
    return Task(
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
        agent=travel_planner_agent,
    )


def run_travel_crew(city_name):
    """Assemble the agent and task into a crew, run it, and return the answer.

    kickoff() replaces every {city} placeholder with city_name before the
    agent starts working.
    """
    travel_planner_agent = create_travel_planner_agent()
    top_places_task = create_top_places_task(travel_planner_agent)

    travel_crew = Crew(
        agents=[travel_planner_agent],
        tasks=[top_places_task],
        verbose=True,
    )
    return travel_crew.kickoff(inputs={"city": city_name})


def main():
    """Entry point: check settings, ask for a city, and print 3 places to visit."""
    load_settings()
    city_name = ask_user_for_city()
    top_places = run_travel_crew(city_name)

    print(f"\nTop 3 places to visit in {city_name}:")
    print(top_places)


if __name__ == "__main__":
    main()
