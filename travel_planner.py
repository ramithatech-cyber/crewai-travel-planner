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
    load_settings()  ->  ask_user_for_city()  ->  build_travel_crew()
    ->  crew.kickoff()  ->  print the result
"""

import os
import sys

# CrewAI is the only required third-party package; explain how to fix a
# missing install instead of showing a raw traceback.
try:
    from crewai import Agent, Crew, Task
except ImportError:
    sys.exit(
        "Error: the 'crewai' package is not installed.\n"
        "Activate your virtual environment and run:\n"
        "  pip install -r requirements.txt"
    )

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

    Exits if the user enters nothing or cancels the prompt.
    """
    try:
        # lstrip removes a stray byte-order mark that some terminals add to piped input.
        city_name = input("Which city? ").strip().lstrip("﻿")
    except (EOFError, KeyboardInterrupt):
        # EOFError: input stream closed; KeyboardInterrupt: user pressed Ctrl+C.
        sys.exit("\nNo city entered - exiting.")

    if not city_name:
        sys.exit("Please enter a city name.")
    return city_name


def build_travel_crew():
    """Build the Travel Planner agent, its task, and the crew that runs them.

    {city} is a placeholder that CrewAI fills in when kickoff() is called.
    The agent's role, goal and backstory set its voice (short, practical,
    for first-time visitors); the task's expected_output pins the answer
    to exactly 3 numbered lines.
    """
    travel_planner_agent = Agent(
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

    top_places_task = Task(
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

    return Crew(
        agents=[travel_planner_agent],
        tasks=[top_places_task],
        verbose=True,
    )


def main():
    """Entry point: check settings, ask for a city, and print 3 places to visit."""
    load_settings()
    city_name = ask_user_for_city()

    # kickoff() calls the OpenAI API, so it can fail on a bad key, no
    # internet, rate limits, etc. Show a short message instead of a traceback.
    try:
        top_places = build_travel_crew().kickoff(inputs={"city": city_name})
    except KeyboardInterrupt:
        sys.exit("\nCancelled by user.")
    except Exception as error:
        sys.exit(
            f"Error: could not get suggestions for {city_name}.\n"
            f"Reason: {error}\n"
            "Check your OPENAI_API_KEY, MODEL and internet connection."
        )

    print(f"\nTop 3 places to visit in {city_name}:")
    print(top_places)


if __name__ == "__main__":
    main()
