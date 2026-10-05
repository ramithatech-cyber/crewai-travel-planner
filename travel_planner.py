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
    ->  find_top_places()  ->  print the result
"""

import os
import sys

# CrewAI is the only required third-party package (it installs the openai
# client too). Explain how to fix a missing install instead of showing a
# raw traceback.
try:
    import openai
    from crewai import Agent, Crew, Task
    from crewai.events import crewai_event_bus
except ImportError:
    sys.exit(
        "Error: the 'crewai' package is not installed.\n"
        "Activate your virtual environment and run:\n"
        "  pip install -r requirements.txt"
    )

# Model used when the MODEL environment variable is not set.
DEFAULT_MODEL = "openai/gpt-4o-mini"


def exit_with_error(message):
    """Print a friendly error message and stop the program with exit code 1."""
    # CrewAI prints its log boxes from a background thread. Wait for them to
    # finish (at most 5 seconds) and flush stdout, so our message appears
    # after the log instead of in the middle of a box.
    crewai_event_bus.flush(timeout=5)
    sys.stdout.flush()
    sys.exit(f"\nError: {message}")


def load_settings():
    """Load the API key and model name from the environment.

    Reads a local .env file first (if python-dotenv is installed), then
    makes sure OPENAI_API_KEY exists and MODEL has a value. Exits with a
    helpful message if the API key is missing.
    """
    # Step 1: load a local .env file, if there is one.
    # python-dotenv is optional - without it, variables must be set in the
    # shell. Existing shell variables always win over values in .env.
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    # Step 2: read and check the API key.
    # The key is always read from the environment - never hard-coded - so it
    # cannot be committed to git by accident.
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        exit_with_error(
            "OPENAI_API_KEY is not set.\n"
            "Set it first, e.g.\n"
            '  PowerShell:   $env:OPENAI_API_KEY="your-key"\n'
            '  macOS/Linux:  export OPENAI_API_KEY="your-key"\n'
            "or put it in a .env file (see .env.example)."
        )

    # Write the trimmed key back: a space or newline copied along with the
    # key would otherwise make OpenAI reject it as invalid.
    os.environ["OPENAI_API_KEY"] = api_key

    # OpenAI keys start with "sk-". Only warn (don't stop), in case the
    # format changes or a compatible provider is being used.
    if not api_key.startswith("sk-"):
        print("Warning: OPENAI_API_KEY does not start with 'sk-' - check it is correct.")

    # Step 3: choose the model.
    # CrewAI reads MODEL from the environment. Use the default when it is
    # missing or blank (e.g. MODEL= in .env with no value).
    if not os.getenv("MODEL", "").strip():
        os.environ["MODEL"] = DEFAULT_MODEL


def ask_user_for_city():
    """Prompt the user for a city name and return it as a clean string.

    Exits if the user enters nothing, enters something that is clearly not
    a city name, or cancels the prompt.
    """
    try:
        # lstrip removes a stray byte-order mark that some terminals add to piped input.
        city_name = input("Which city? ").strip().lstrip("﻿")
    except (EOFError, KeyboardInterrupt):
        # EOFError: input stream closed; KeyboardInterrupt: user pressed Ctrl+C.
        exit_with_error("no city entered - exiting.")

    if not city_name:
        exit_with_error("please enter a city name.")

    # Every city name has at least one letter; this catches inputs like
    # "123" or "!!" before spending an API call on them.
    if not any(char.isalpha() for char in city_name):
        exit_with_error(f"'{city_name}' doesn't look like a city name.")

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


def find_top_places(city_name):
    """Run the crew for city_name and return the agent's answer as text.

    Every step that can fail is turned into a short, specific message
    explaining what went wrong and how to fix it.
    """
    model = os.environ["MODEL"]

    # Building the crew validates MODEL: CrewAI raises ImportError/ValueError
    # when it doesn't recognise the model name.
    try:
        travel_crew = build_travel_crew()
    except (ImportError, ValueError) as error:
        exit_with_error(
            f"MODEL '{model}' is not supported.\n"
            f"Use an OpenAI model such as '{DEFAULT_MODEL}'.\n"
            # CrewAI's message is long; its first line says what went wrong.
            f"Details: {str(error).splitlines()[0]}"
        )

    # kickoff() calls the OpenAI API. Each except block below matches one
    # kind of failure; the order matters because the last ones are broader.
    # CrewAI re-raises some OpenAI errors as built-in Python errors
    # (ConnectionError, ValueError), so those are matched here too.
    try:
        result = travel_crew.kickoff(inputs={"city": city_name})
    except KeyboardInterrupt:
        exit_with_error("cancelled by user.")
    except openai.AuthenticationError:
        exit_with_error(
            "OpenAI rejected your API key.\n"
            "Check OPENAI_API_KEY, or create a new key at "
            "https://platform.openai.com/api-keys"
        )
    except openai.RateLimitError as error:
        # The same error type covers "too many requests" and "no credit left".
        if "insufficient_quota" in str(error):
            exit_with_error(
                "your OpenAI account has no credit left.\n"
                "Add billing at https://platform.openai.com/settings/organization/billing"
            )
        exit_with_error("too many requests to OpenAI. Wait a minute and try again.")
    except (openai.NotFoundError, ValueError) as error:
        # A ValueError here is usually CrewAI's wrapper around OpenAI's
        # "model not found" (404); any other ValueError gets a general message.
        if isinstance(error, ValueError) and "not found" not in str(error):
            exit_with_error(f"could not get suggestions for {city_name}.\nReason: {error}")
        exit_with_error(
            f"model '{model}' was not found or your key has no access to it.\n"
            f"Try MODEL={DEFAULT_MODEL}"
        )
    except openai.PermissionDeniedError:
        exit_with_error(
            "your API key is not allowed to use this model or project.\n"
            "Check the key's permissions on the OpenAI dashboard."
        )
    except (openai.APIConnectionError, openai.APITimeoutError, ConnectionError):
        exit_with_error(
            "could not reach OpenAI. Check your internet connection and try again."
        )
    except openai.OpenAIError as error:
        # Any other error reported by the OpenAI API.
        exit_with_error(f"OpenAI returned an error: {error}")
    except Exception as error:
        # Safety net for anything unexpected inside CrewAI itself.
        exit_with_error(
            f"could not get suggestions for {city_name}.\n"
            f"Reason: {type(error).__name__}: {error}"
        )

    # The call can succeed but still return nothing useful.
    answer = str(result).strip()
    if not answer:
        exit_with_error(f"the agent returned an empty answer for {city_name}. Please try again.")
    return answer


def main():
    """Entry point: check settings, ask for a city, and print 3 places to visit."""
    load_settings()
    city_name = ask_user_for_city()
    top_places = find_top_places(city_name)

    print(f"\nTop 3 places to visit in {city_name}:")
    print(top_places)


if __name__ == "__main__":
    main()
