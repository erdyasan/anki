"""
Anki deck generator service.
Creates .apkg files from vocabulary words stored in the database.

Note Type: English Vocabulary
Cards per word: 5
  1. Word → Translation
  2. Translation → Word
  3. Example1 → Translation
  4. Example2 → Translation
  5. Example3 → Translation
"""

import genanki
from pathlib import Path

from .database import Word

# Stable IDs — Anki uses these to identify note/model types across imports
MODEL_ID = 1607392319
DECK_ID = 2059400110

CARD_CSS = """
.card {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 20px;
    text-align: center;
    color: #333;
    background-color: #fafafa;
    padding: 20px;
    line-height: 1.6;
}

.word {
    font-size: 32px;
    font-weight: bold;
    color: #1a73e8;
    margin-bottom: 8px;
}

.word-type {
    font-size: 14px;
    color: #888;
    font-style: italic;
    margin-bottom: 12px;
}

.translation {
    font-size: 24px;
    color: #2e7d32;
    font-weight: 600;
}

.example {
    font-size: 18px;
    color: #444;
    margin: 12px 0;
    padding: 12px 16px;
    background: #f0f4ff;
    border-left: 4px solid #1a73e8;
    border-radius: 4px;
    text-align: left;
}

.example-translation {
    font-size: 16px;
    color: #666;
    margin: 8px 0;
    padding: 8px 16px;
    background: #f0fff0;
    border-left: 4px solid #2e7d32;
    border-radius: 4px;
    text-align: left;
}

.label {
    font-size: 12px;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}

.divider {
    border-top: 1px solid #e0e0e0;
    margin: 16px 0;
}
"""

TEMPLATES = [
    {
        "name": "Word → Translation",
        "qfmt": """
            <div class="label">What does this word mean?</div>
            <div class="word">{{Word}}</div>
            <div class="word-type">{{WordType}}</div>
        """,
        "afmt": """
            {{FrontSide}}
            <div class="divider"></div>
            <div class="translation">{{WordTranslation}}</div>
            <div class="divider"></div>
            <div class="example">{{Example1}}</div>
            <div class="example-translation">{{Example1Translation}}</div>
            <div class="example">{{Example2}}</div>
            <div class="example-translation">{{Example2Translation}}</div>
            <div class="example">{{Example3}}</div>
            <div class="example-translation">{{Example3Translation}}</div>
        """,
    },
    {
        "name": "Translation → Word",
        "qfmt": """
            <div class="label">Bu kelimenin İngilizcesi nedir?</div>
            <div class="translation">{{WordTranslation}}</div>
        """,
        "afmt": """
            {{FrontSide}}
            <div class="divider"></div>
            <div class="word">{{Word}}</div>
            <div class="word-type">{{WordType}}</div>
            <div class="divider"></div>
            <div class="example">{{Example1}}</div>
            <div class="example">{{Example2}}</div>
            <div class="example">{{Example3}}</div>
        """,
    },
    {
        "name": "Example 1 → Translation",
        "qfmt": """
            <div class="label">Translate this sentence</div>
            <div class="example">{{Example1}}</div>
        """,
        "afmt": """
            {{FrontSide}}
            <div class="divider"></div>
            <div class="example-translation">{{Example1Translation}}</div>
            <div class="divider"></div>
            <div class="word">{{Word}}</div>
            <div class="word-type">{{WordType}}</div>
        """,
    },
    {
        "name": "Example 2 → Translation",
        "qfmt": """
            <div class="label">Translate this sentence</div>
            <div class="example">{{Example2}}</div>
        """,
        "afmt": """
            {{FrontSide}}
            <div class="divider"></div>
            <div class="example-translation">{{Example2Translation}}</div>
            <div class="divider"></div>
            <div class="word">{{Word}}</div>
            <div class="word-type">{{WordType}}</div>
        """,
    },
    {
        "name": "Example 3 → Translation",
        "qfmt": """
            <div class="label">Translate this sentence</div>
            <div class="example">{{Example3}}</div>
        """,
        "afmt": """
            {{FrontSide}}
            <div class="divider"></div>
            <div class="example-translation">{{Example3Translation}}</div>
            <div class="divider"></div>
            <div class="word">{{Word}}</div>
            <div class="word-type">{{WordType}}</div>
        """,
    },
]

FIELDS = [
    {"name": "Word"},
    {"name": "WordType"},
    {"name": "WordTranslation"},
    {"name": "Example1"},
    {"name": "Example1Translation"},
    {"name": "Example2"},
    {"name": "Example2Translation"},
    {"name": "Example3"},
    {"name": "Example3Translation"},
]


def _create_model() -> genanki.Model:
    """Create the English Vocabulary note type with 5 card templates."""
    return genanki.Model(
        MODEL_ID,
        "English Vocabulary",
        fields=FIELDS,
        templates=TEMPLATES,
        css=CARD_CSS,
    )


def _word_to_note(model: genanki.Model, word: Word) -> genanki.Note:
    """Convert a Word dataclass to a genanki Note."""
    return genanki.Note(
        model=model,
        fields=[
            word.word,
            word.word_type,
            word.translation,
            word.example1,
            word.example1_tr,
            word.example2,
            word.example2_tr,
            word.example3,
            word.example3_tr,
        ],
    )


def generate_deck(words: list[Word], output_path: str) -> tuple[int, int]:
    """
    Generate an .apkg deck from a list of Word objects.

    Returns:
        Tuple of (note_count, card_count)
    """
    if not words:
        raise ValueError("No words to generate deck from")

    model = _create_model()
    deck = genanki.Deck(DECK_ID, "English Vocabulary")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    note_count = 0
    for word in words:
        note = _word_to_note(model, word)
        deck.add_note(note)
        note_count += 1

    package = genanki.Package(deck)
    package.write_to_file(output_path)

    return note_count, note_count * 5
