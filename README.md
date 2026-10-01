# CrewAI Travel Planner Agent

My first CrewAI agent (Social Eagle, Week 4 · Day 3). You type in a city and a **Travel Planner** agent suggests **3 places to visit** there.

## How it works

Everything is in one file, `travel_planner.py`:

| Piece | What it does |
|-------|--------------|
| **Agent** | A *Local Travel Planner* with a role, goal and backstory. It writes for first-time visitors on a short trip, so its answers stay short and practical. `verbose=True` shows its reasoning. |
| **Task** | Asks for exactly 3 places in `{city}`. The `expected_output` asks for exactly 3 numbered lines (`<n>. <Place> - <short description + tip>`) with nothing else, so you get three clean suggestions instead of an essay. |
| **Crew** | Puts the agent and task together. `crew.kickoff(inputs={"city": city})` fills in the `{city}` placeholder and runs the task. |

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
