# Taskthon2

> A lightweight task-management assistant project with an AI agent, a small database layer, and both CLI and GUI frontends.

## Features

- AI agent for task automation and helpers (`ai_agent/agent.py`)
- Simple database manager (`database/db_manager.py`) with tests (`test_db.py`)
- MCP server for integrations and automation (`mcp_server/server.py`)
- Command-line and graphical frontends (`ui/cli.py`, `ui/gui.py`)

## Repository structure

- `ai_agent/` — AI agent implementation and orchestration
- `database/` — database utilities and manager
- `mcp_server/` — lightweight server for automation/integration
- `ui/` — user interfaces: CLI and GUI
- `test_db.py` — simple database tests / example usage
- `requirements.txt` — Python dependencies

## Requirements

- Python 3.9+
- See `requirements.txt` for Python packages. Create and activate a virtual environment before installing.

## Installation

1. Create & activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

- Run the database test (quick sanity check):

```bash
python test_db.py
```

- Start the MCP server (if used for integrations):

```bash
python -m mcp_server.server
```

- Run the AI agent (experimentally):

```bash
python -m ai_agent.agent
```

- Launch the CLI:

```bash
python -m ui.cli
```

- Launch the GUI (if implemented):

```bash
python -m ui.gui
```

Notes:
- The concrete entrypoints above assume the modules expose runnable `if __name__ == '__main__'` blocks. If not, run the appropriate helper scripts or import and call the exposed functions.

## Development

- Run tests and iterate. Use the virtual environment from above.
- Add features or fix bugs by editing the relevant package and creating small, focused commits.

## Contributing

Contributions are welcome. Please open issues or pull requests on the repository.

## License

This project is provided as-is. Add a license file or replace this section with the chosen license (e.g., MIT).

