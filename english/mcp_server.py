"""
MCP Server for Anki English Vocabulary Builder.

Exposes tools for AI agents (Claude Code, etc.) to manage vocabulary words
and generate Anki decks via the Model Context Protocol.

Run: python -m english.mcp_server
"""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .app.database import Word, WordRepository
from .app.deck_generator import generate_deck

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = str(BASE_DIR / "data" / "words.db")
OUTPUT_DIR = str(BASE_DIR / "output")

repo = WordRepository(DB_PATH)

mcp = FastMCP(
    "anki-english-vocabulary",
    instructions=(
        "Anki English Vocabulary Builder. "
        "Use these tools to add, search, list, and delete English vocabulary words, "
        "and to generate Anki .apkg decks. "
        "When adding words, provide the word, its type (noun/verb/adjective/etc.), "
        "Turkish translation, and 3 example sentences with translations. "
        "Use <b>word</b> HTML tags to bold the target word in example sentences. "
        "Always check for duplicates before adding — same word + same word_type is not allowed."
    ),
)


@mcp.tool()
def add_word(
    word: str,
    word_type: str,
    translation: str,
    example1: str,
    example1_tr: str,
    example2: str,
    example2_tr: str,
    example3: str,
    example3_tr: str,
) -> str:
    """Add a new English vocabulary word with Turkish translation and 3 example sentences.

    Duplicate check: If the same word + word_type already exists, the word is rejected.
    The same word with a different type is allowed (e.g., 'run' as verb and 'run' as noun).

    Use <b>word</b> HTML tags to bold the target word in example sentences.

    Args:
        word: The English word (e.g., "abandon")
        word_type: Part of speech — one of: noun, verb, adjective, adverb, preposition, conjunction, pronoun, interjection, phrase
        translation: Turkish translation (e.g., "terk etmek, bırakmak")
        example1: First example sentence in English with the word bolded using <b> tags
        example1_tr: Turkish translation of the first example sentence
        example2: Second example sentence in English with the word bolded using <b> tags
        example2_tr: Turkish translation of the second example sentence
        example3: Third example sentence in English with the word bolded using <b> tags
        example3_tr: Turkish translation of the third example sentence
    """
    existing = repo.find_duplicate(word, word_type)
    if existing is not None:
        return json.dumps({
            "status": "duplicate",
            "message": f"'{word}' ({word_type}) already exists with translation: '{existing.translation}'",
            "existing_id": existing.id,
        })

    new_word = Word(
        id=None,
        word=word.strip(),
        word_type=word_type.strip().lower(),
        translation=translation.strip(),
        example1=example1.strip(),
        example1_tr=example1_tr.strip(),
        example2=example2.strip(),
        example2_tr=example2_tr.strip(),
        example3=example3.strip(),
        example3_tr=example3_tr.strip(),
    )

    word_id = repo.create(new_word)
    return json.dumps({
        "status": "created",
        "message": f"'{word}' ({word_type}) added successfully",
        "id": word_id,
    })


@mcp.tool()
def search_words(query: str) -> str:
    """Search vocabulary words by word or Turkish translation (case-insensitive partial match).

    Args:
        query: Search term to match against word or translation fields
    """
    words = repo.search(query)
    if not words:
        return json.dumps({"status": "empty", "message": f"No words found matching '{query}'"})

    results = [
        {
            "id": w.id,
            "word": w.word,
            "word_type": w.word_type,
            "translation": w.translation,
        }
        for w in words
    ]
    return json.dumps({"status": "ok", "count": len(results), "words": results})


@mcp.tool()
def list_words() -> str:
    """List all vocabulary words in the database, ordered alphabetically."""
    words = repo.get_all()
    if not words:
        return json.dumps({"status": "empty", "message": "No words in the database"})

    results = [
        {
            "id": w.id,
            "word": w.word,
            "word_type": w.word_type,
            "translation": w.translation,
        }
        for w in words
    ]
    return json.dumps({"status": "ok", "count": len(results), "words": results})


@mcp.tool()
def get_word(word_id: int) -> str:
    """Get full details of a word by its ID, including all example sentences.

    Args:
        word_id: The database ID of the word
    """
    word = repo.get_by_id(word_id)
    if word is None:
        return json.dumps({"status": "not_found", "message": f"No word found with ID {word_id}"})

    return json.dumps({
        "status": "ok",
        "word": {
            "id": word.id,
            "word": word.word,
            "word_type": word.word_type,
            "translation": word.translation,
            "example1": word.example1,
            "example1_tr": word.example1_tr,
            "example2": word.example2,
            "example2_tr": word.example2_tr,
            "example3": word.example3,
            "example3_tr": word.example3_tr,
        },
    })


@mcp.tool()
def delete_word(word_id: int) -> str:
    """Delete a vocabulary word by its ID.

    Args:
        word_id: The database ID of the word to delete
    """
    word = repo.get_by_id(word_id)
    if word is None:
        return json.dumps({"status": "not_found", "message": f"No word found with ID {word_id}"})

    repo.delete(word_id)
    return json.dumps({
        "status": "deleted",
        "message": f"'{word.word}' ({word.word_type}) deleted successfully",
    })


@mcp.tool()
def generate_anki_deck() -> str:
    """Generate an Anki .apkg deck file from all words in the database.

    The deck is saved to the output directory and can be imported into Anki via File > Import.
    Each word produces 5 cards: Word→TR, TR→Word, Example1→TR, Example2→TR, Example3→TR.
    """
    words = repo.get_all()
    if not words:
        return json.dumps({"status": "empty", "message": "No words to generate deck from"})

    output_path = str(Path(OUTPUT_DIR) / "english_vocab.apkg")

    try:
        note_count, card_count = generate_deck(words, output_path)
        return json.dumps({
            "status": "generated",
            "message": f"Deck generated successfully",
            "notes": note_count,
            "cards": card_count,
            "output_path": output_path,
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
def get_word_count() -> str:
    """Get the total number of vocabulary words in the database."""
    count = repo.count()
    return json.dumps({"status": "ok", "count": count})


if __name__ == "__main__":
    mcp.run(transport="stdio")
