# Anki Deck Builder

A desktop application for creating Anki flashcard decks with a GUI. Wraps the complexity of Anki's Note Type / Card Template system into a simple interface powered by SQLite and [genanki](https://github.com/kerrickstaley/genanki).

## Features

- **CRUD operations** — Add, edit, delete vocabulary words through a GUI
- **Search** — Instant search by word or translation
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

```bash
source .venv/bin/activate
python -m english.app.main
```

1. Click **+ Add Word** to add a vocabulary word with examples
2. Double-click a row or select + **Edit** to modify
3. Select + **Delete** to remove a word
4. Click **Generate Anki Deck** to create `output/english_vocab.apkg`
5. Import the `.apkg` file in Anki via `File > Import`

## Project Structure

```
anki/
├── english/
│   ├── app/
│   │   ├── main.py              # Entry point
│   │   ├── database.py          # SQLite repository
│   │   ├── deck_generator.py    # Anki .apkg generator (genanki)
│   │   └── gui/
│   │       ├── main_window.py   # Main window + word list
│   │       └── word_form.py     # Add/edit word form
│   ├── data/                    # SQLite database (auto-created)
│   └── output/                  # Generated .apkg files
├── csharp/                      # (planned)
├── requirements.txt
└── .gitignore
```

## License

MIT
