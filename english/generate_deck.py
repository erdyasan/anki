"""
English Vocabulary Anki Deck Generator

Generates .apkg files with custom Note Type:
- Fields: Word, WordType, WordTranslation, Example1-3, Example1-3 Translation
- Cards: Word→TR, TR→Word, Example1→TR, Example2→TR, Example3→TR
"""

import genanki
import yaml
import sys
from pathlib import Path

# Stable IDs (generated once, never change — Anki uses these to identify note/model types)
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

# Card 1: Word → Translation
CARD1_FRONT = """
<div class="label">What does this word mean?</div>
<div class="word">{{Word}}</div>
<div class="word-type">{{WordType}}</div>
"""

CARD1_BACK = """
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
"""

# Card 2: Translation → Word
CARD2_FRONT = """
<div class="label">Bu kelimenin İngilizcesi nedir?</div>
<div class="translation">{{WordTranslation}}</div>
"""

CARD2_BACK = """
{{FrontSide}}
<div class="divider"></div>
<div class="word">{{Word}}</div>
<div class="word-type">{{WordType}}</div>
<div class="divider"></div>
<div class="example">{{Example1}}</div>
<div class="example">{{Example2}}</div>
<div class="example">{{Example3}}</div>
"""

# Card 3: Example1 → Translation
CARD3_FRONT = """
<div class="label">Translate this sentence</div>
<div class="example">{{Example1}}</div>
"""

CARD3_BACK = """
{{FrontSide}}
<div class="divider"></div>
<div class="example-translation">{{Example1Translation}}</div>
<div class="divider"></div>
<div class="word">{{Word}}</div>
<div class="word-type">{{WordType}}</div>
"""

# Card 4: Example2 → Translation
CARD4_FRONT = """
<div class="label">Translate this sentence</div>
<div class="example">{{Example2}}</div>
"""

CARD4_BACK = """
{{FrontSide}}
<div class="divider"></div>
<div class="example-translation">{{Example2Translation}}</div>
<div class="divider"></div>
<div class="word">{{Word}}</div>
<div class="word-type">{{WordType}}</div>
"""

# Card 5: Example3 → Translation
CARD5_FRONT = """
<div class="label">Translate this sentence</div>
<div class="example">{{Example3}}</div>
"""

CARD5_BACK = """
{{FrontSide}}
<div class="divider"></div>
<div class="example-translation">{{Example3Translation}}</div>
<div class="divider"></div>
<div class="word">{{Word}}</div>
<div class="word-type">{{WordType}}</div>
"""


def create_model() -> genanki.Model:
    """Create the English Vocabulary note type with 5 card templates."""
    return genanki.Model(
        MODEL_ID,
        "English Vocabulary",
        fields=[
            {"name": "Word"},
            {"name": "WordType"},
            {"name": "WordTranslation"},
            {"name": "Example1"},
            {"name": "Example1Translation"},
            {"name": "Example2"},
            {"name": "Example2Translation"},
            {"name": "Example3"},
            {"name": "Example3Translation"},
        ],
        templates=[
            {
                "name": "Word → Translation",
                "qfmt": CARD1_FRONT,
                "afmt": CARD1_BACK,
            },
            {
                "name": "Translation → Word",
                "qfmt": CARD2_FRONT,
                "afmt": CARD2_BACK,
            },
            {
                "name": "Example 1 → Translation",
                "qfmt": CARD3_FRONT,
                "afmt": CARD3_BACK,
            },
            {
                "name": "Example 2 → Translation",
                "qfmt": CARD4_FRONT,
                "afmt": CARD4_BACK,
            },
            {
                "name": "Example 3 → Translation",
                "qfmt": CARD5_FRONT,
                "afmt": CARD5_BACK,
            },
        ],
        css=CARD_CSS,
    )


def load_words(yaml_path: str) -> list[dict]:
    """Load word list from a YAML file."""
    path = Path(yaml_path)
    if not path.exists():
        print(f"Error: File not found: {yaml_path}")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "words" not in data:
        print("Error: YAML must have a top-level 'words' key")
        sys.exit(1)

    return data["words"]


def create_note(model: genanki.Model, word_data: dict) -> genanki.Note:
    """Create a single note from word data."""
    required_fields = [
        "word", "type", "translation",
        "example1", "example1_tr",
        "example2", "example2_tr",
        "example3", "example3_tr",
    ]

    for field in required_fields:
        if field not in word_data:
            raise ValueError(f"Missing required field '{field}' for word: {word_data.get('word', '?')}")

    return genanki.Note(
        model=model,
        fields=[
            word_data["word"],
            word_data["type"],
            word_data["translation"],
            word_data["example1"],
            word_data["example1_tr"],
            word_data["example2"],
            word_data["example2_tr"],
            word_data["example3"],
            word_data["example3_tr"],
        ],
    )


def generate_deck(yaml_path: str, output_path: str | None = None) -> str:
    """Generate an .apkg deck from a YAML word list."""
    words = load_words(yaml_path)
    model = create_model()

    deck = genanki.Deck(DECK_ID, "English Vocabulary")

    note_count = 0
    for word_data in words:
        try:
            note = create_note(model, word_data)
            deck.add_note(note)
            note_count += 1
        except ValueError as e:
            print(f"Warning: Skipping word — {e}")

    if output_path is None:
        output_path = str(Path(yaml_path).with_suffix(".apkg"))

    package = genanki.Package(deck)
    package.write_to_file(output_path)

    print(f"Generated {output_path}")
    print(f"  Notes: {note_count}")
    print(f"  Cards: {note_count * 5}")

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_deck.py <words.yaml> [output.apkg]")
        print("Example: python generate_deck.py words.yaml english_vocab.apkg")
        sys.exit(1)

    yaml_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    generate_deck(yaml_file, output_file)
