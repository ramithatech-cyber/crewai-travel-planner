# CrewAI Travel Planner Agent

My first CrewAI agent (Social Eagle, Week 4 · Day 3). You type in a city and a **Travel Planner** agent suggests **3 places to visit** there.

## How it works

Everything is in one file, `travel_planner.py`:

| Piece | What it does |
|-------|--------------|
| **Agent** | A *Local Travel Planner* with a role, goal and backstory. It writes for first-time visitors on a short trip, so its answers stay short and practical. `verbose=True` shows its reasoning. |
| **Task** | Asks for exactly 3 places in `{city}`. The `expected_output` asks for exactly 3 numbered lines (`<n>. <Place> - <short description + tip>`) with nothing else, so you get three clean suggestions instead of an essay. |
| **Crew** | Puts the agent and task together. `kickoff(inputs={"city": city_name})` fills in the `{city}` placeholder and runs the task. |

The code is split into small, documented functions that run in this order:

| Function | What it does |
|----------|--------------|
| `load_settings()` | Loads `.env` (if present), checks and trims `OPENAI_API_KEY`, and defaults `MODEL` to `openai/gpt-4o-mini`. |
| `ask_user_for_city()` | Asks "Which city?", checks the answer, and returns the cleaned-up name. |
| `build_travel_crew()` | Builds the *Local Travel Planner* agent, its "suggest exactly 3 places" task, and the crew that runs them. |
| `find_top_places(city_name)` | Runs the crew and turns any failure into a clear message. |
| `main()` | Calls the steps above and prints the result. |
| `exit_with_error(message)` | Small helper that prints an error neatly and exits. |

### Error handling

Instead of a long traceback, the script stops with a short message that says what went wrong and how to fix it:

| Problem | Message |
|---------|---------|
| `crewai` not installed | Tells you to run `pip install -r requirements.txt` |
| `OPENAI_API_KEY` missing | Shows how to set it in PowerShell, macOS/Linux or `.env` |
| Key doesn't start with `sk-` | Warning only, the script still runs |
| Empty, cancelled or non-city input (e.g. `123`) | Asks for a real city name |
| Unsupported or unknown `MODEL` | Suggests `openai/gpt-4o-mini` |
| Wrong API key | Links to the OpenAI API keys page |
| Rate limit / no credit left | Says to wait, or links to billing |
| No internet | Asks you to check your connection |
| Empty answer from the agent | Asks you to try again |

The OpenAI API key is **read from an environment variable**. It is never hard-coded in the script.

## Setup

Requires Python 3.10 – 3.13.

```bash
git clone https://github.com/ramithatech-cyber/crewai-travel-planner.git
cd crewai-travel-planner
python -m venv venv
```

**Windows (PowerShell)**
```powershell
venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OPENAI_API_KEY="your-key"
$env:MODEL="openai/gpt-4o-mini"
```

**macOS / Linux**
```bash
source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
export MODEL="openai/gpt-4o-mini"
```

You can also copy `.env.example` to `.env` and fill it in instead. `.env` is git-ignored. If `MODEL` is not set, the script uses `openai/gpt-4o-mini`.

## Run

```bash
python travel_planner.py
```

Example output (shown after the verbose agent log):

```
Which city? Jaipur
1. Amber Fort - hilltop fort with mirrored halls, go early
2. Hawa Mahal - the pink facade, best in morning light
3. City Palace - royal courtyards and a textile museum
```

## Project structure

```
crewai-travel-planner/
├── travel_planner.py   # agent, task and crew (the whole app)
├── requirements.txt    # crewai, python-dotenv
├── .env.example        # template for your API key / model
├── .gitignore          # keeps .env and venv out of git
├── LICENSE
└── README.md
```

## License

[MIT](LICENSE)
