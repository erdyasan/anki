# Anki Deck Builder

A desktop application and MCP server for creating Anki flashcard decks. Wraps the complexity of Anki's Note Type / Card Template system into a simple interface powered by SQLite and [genanki](https://github.com/kerrickstaley/genanki).

## Features

- **GUI Application** — Add, edit, delete, search vocabulary words through a desktop interface
- **MCP Server** — AI agents (OpenCode, Claude Code, etc.) can add words and generate decks via MCP tools
- **Duplicate Detection** — Same word + same type is rejected; different types allowed (e.g., `run` as verb vs noun)
- **SQLite storage** — All words stored locally in a SQLite database
- **Anki deck generation** — One-click `.apkg` export ready to import into Anki
- **Custom Note Type** — English Vocabulary with 5 card templates per word

## English Vocabulary Note Type

Each word generates **5 cards**:

| Card | Front | Back |
|------|-------|------|
| 1 | Word *(type)* | Turkish translation + all examples |
| 2 | Turkish translation | Word *(type)* + examples |
| 3 | Example sentence 1 | Turkish translation of sentence |
| 4 | Example sentence 2 | Turkish translation of sentence |
| 5 | Example sentence 3 | Turkish translation of sentence |

## Prerequisites

- Python 3.12+
- [pyenv](https://github.com/pyenv/pyenv) (recommended)
- Tkinter system package (`sudo apt install python3-tk` on Ubuntu/Debian)

## Setup

```bash
# Clone the repository
git clone https://github.com/erdyasan/anki.git
cd anki

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate        # bash/zsh
# source .venv/bin/activate.fish # fish

pip install -r requirements.txt
```

## Usage

### GUI Application

```bash
source .venv/bin/activate
python -m english.app.main
```

1. Click **+ Add Word** to add a vocabulary word with examples
2. Double-click a row or select + **Edit** to modify
3. Select + **Delete** to remove a word
4. Click **Generate Anki Deck** to create `output/english_vocab.apkg`
5. Import the `.apkg` file in Anki via `File > Import`

### MCP Server (AI Integration)

The MCP server allows AI agents to manage vocabulary words directly.

#### OpenCode

Add to your project's `opencode.json` (already included in this repo):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "anki-english": {
      "type": "local",
      "command": [
        "/path/to/anki/.venv/bin/python",
        "-m",
        "english.mcp_server"
      ],
      "enabled": true
    }
  }
}
```

#### Available MCP Tools

| Tool | Description |
|------|-------------|
| `add_word` | Add a word with type, translation, and 3 example sentences |
| `search_words` | Search by word or translation |
| `list_words` | List all words |
| `get_word` | Get full details of a word by ID |
| `delete_word` | Delete a word by ID |
| `generate_anki_deck` | Generate `.apkg` from all words |
| `get_word_count` | Get total word count |

#### Example AI Prompt

> "Add the word 'abandon' as a verb, meaning 'terk etmek, birakmak', with 3 example sentences and their Turkish translations"

The AI will call `add_word` with all the fields filled in, including `<b>` tags for bolding the target word in examples.

## Project Structure

```
anki/
├── english/
│   ├── mcp_server.py            # MCP server for AI agents
│   ├── app/
│   │   ├── main.py              # GUI entry point
│   │   ├── database.py          # SQLite repository
│   │   ├── deck_generator.py    # Anki .apkg generator (genanki)
│   │   └── gui/
│   │       ├── main_window.py   # Main window + word list
│   │       └── word_form.py     # Add/edit word form
│   ├── data/                    # SQLite database (auto-created)
│   └── output/                  # Generated .apkg files
├── csharp/                      # (planned)
├── opencode.json                # OpenCode MCP config
├── requirements.txt
└── .gitignore
```

## License

MIT
