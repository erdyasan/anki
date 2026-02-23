"""
Main application window.
Displays the word list with search, CRUD operations, and deck generation.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

import customtkinter as ctk

from ..database import Word, WordRepository
from ..deck_generator import generate_deck
from .word_form import WordFormDialog


class MainWindow(ctk.CTk):
    """Main application window with word list and controls."""

    def __init__(self, repo: WordRepository, output_dir: str) -> None:
        super().__init__()

        self._repo = repo
        self._output_dir = output_dir

        self.title("Anki English Vocabulary Builder")
        self.geometry("900x650")
        self.minsize(750, 500)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._build_ui()
        self._refresh_word_list()

    def _build_ui(self) -> None:
        """Build the main UI layout."""
        # Top bar: search + action buttons
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=16, pady=(16, 8))

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._on_search())
        search_entry = ctk.CTkEntry(
            top_frame,
            placeholder_text="Search words...",
            textvariable=self._search_var,
            width=300,
            height=36,
        )
        search_entry.pack(side="left")

        # Status label
        self._status_label = ctk.CTkLabel(
            top_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self._status_label.pack(side="left", padx=(16, 0))

        # Generate button
        ctk.CTkButton(
            top_frame,
            text="Generate Anki Deck",
            command=self._handle_generate,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            width=180,
            height=36,
        ).pack(side="right", padx=(8, 0))

        # Delete button
        ctk.CTkButton(
            top_frame,
            text="Delete",
            command=self._handle_delete,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            width=80,
            height=36,
        ).pack(side="right", padx=(8, 0))

        # Edit button
        ctk.CTkButton(
            top_frame,
            text="Edit",
            command=self._handle_edit,
            fg_color="#f57c00",
            hover_color="#e65100",
            width=80,
            height=36,
        ).pack(side="right", padx=(8, 0))

        # Add button
        ctk.CTkButton(
            top_frame,
            text="+ Add Word",
            command=self._handle_add,
            fg_color="#1a73e8",
            hover_color="#1557b0",
            width=120,
            height=36,
        ).pack(side="right")

        # Word list (Treeview)
        list_frame = ctk.CTkFrame(self, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Treeview with scrollbar
        columns = ("id", "word", "type", "translation", "example1")
        self._tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        self._tree.heading("id", text="ID")
        self._tree.heading("word", text="Word")
        self._tree.heading("type", text="Type")
        self._tree.heading("translation", text="Translation")
        self._tree.heading("example1", text="Example 1")

        self._tree.column("id", width=40, minwidth=40, stretch=False)
        self._tree.column("word", width=140, minwidth=100)
        self._tree.column("type", width=90, minwidth=70, stretch=False)
        self._tree.column("translation", width=200, minwidth=120)
        self._tree.column("example1", width=350, minwidth=150)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Double-click to edit
        self._tree.bind("<Double-1>", lambda _: self._handle_edit())

        # Style the treeview for dark mode
        self._style_treeview()

    def _style_treeview(self) -> None:
        """Apply dark theme styling to the Treeview widget."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="#e0e0e0",
            fieldbackground="#2b2b2b",
            rowheight=32,
            font=("Segoe UI", 12),
        )
        style.configure(
            "Treeview.Heading",
            background="#3c3c3c",
            foreground="#ffffff",
            font=("Segoe UI", 12, "bold"),
        )
        style.map(
            "Treeview",
            background=[("selected", "#1a73e8")],
            foreground=[("selected", "#ffffff")],
        )

    def _refresh_word_list(self, words: list[Word] | None = None) -> None:
        """Reload the word list from the database."""
        self._tree.delete(*self._tree.get_children())

        if words is None:
            words = self._repo.get_all()

        for word in words:
            self._tree.insert(
                "",
                "end",
                iid=str(word.id),
                values=(word.id, word.word, word.word_type, word.translation, word.example1),
            )

        count = len(words)
        total = self._repo.count()
        if count == total:
            self._status_label.configure(text=f"{total} words")
        else:
            self._status_label.configure(text=f"{count} / {total} words")

    def _get_selected_word_id(self) -> int | None:
        """Get the ID of the currently selected word in the treeview."""
        selection = self._tree.selection()
        if not selection:
            return None
        return int(selection[0])

    def _on_search(self) -> None:
        """Filter word list based on search query."""
        query = self._search_var.get().strip()
        if query:
            words = self._repo.search(query)
        else:
            words = self._repo.get_all()
        self._refresh_word_list(words)

    def _handle_add(self) -> None:
        """Open the add word form."""
        WordFormDialog(self, on_save=self._save_word)

    def _handle_edit(self) -> None:
        """Open the edit form for the selected word."""
        word_id = self._get_selected_word_id()
        if word_id is None:
            messagebox.showwarning("No Selection", "Please select a word to edit.")
            return

        word = self._repo.get_by_id(word_id)
        if word is None:
            messagebox.showerror("Error", "Word not found in database.")
            return

        WordFormDialog(self, on_save=self._save_word, word=word)

    def _handle_delete(self) -> None:
        """Delete the selected word after confirmation."""
        word_id = self._get_selected_word_id()
        if word_id is None:
            messagebox.showwarning("No Selection", "Please select a word to delete.")
            return

        word = self._repo.get_by_id(word_id)
        if word is None:
            messagebox.showerror("Error", "Word not found in database.")
            return

        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{word.word}'?",
        )
        if confirmed:
            self._repo.delete(word_id)
            self._refresh_word_list()

    def _save_word(self, word: Word, is_edit: bool) -> None:
        """Save a word (create or update) and refresh the list."""
        if is_edit:
            self._repo.update(word)
        else:
            self._repo.create(word)
        self._refresh_word_list()

    def _handle_generate(self) -> None:
        """Generate the Anki .apkg deck from all words in the database."""
        words = self._repo.get_all()
        if not words:
            messagebox.showwarning("No Words", "Add some words before generating a deck.")
            return

        output_path = str(Path(self._output_dir) / "english_vocab.apkg")

        try:
            note_count, card_count = generate_deck(words, output_path)
            messagebox.showinfo(
                "Deck Generated",
                f"Successfully generated Anki deck!\n\n"
                f"Notes: {note_count}\n"
                f"Cards: {card_count}\n"
                f"File: {output_path}",
            )
        except Exception as e:
            messagebox.showerror("Generation Failed", f"Failed to generate deck:\n{e}")
