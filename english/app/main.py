"""
Entry point for the English Vocabulary Anki Builder application.
"""

from pathlib import Path

from .database import WordRepository
from .gui.main_window import MainWindow

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(BASE_DIR / "data" / "words.db")
OUTPUT_DIR = str(BASE_DIR / "output")


def main() -> None:
    repo = WordRepository(DB_PATH)
    app = MainWindow(repo=repo, output_dir=OUTPUT_DIR)
    app.mainloop()


if __name__ == "__main__":
    main()
