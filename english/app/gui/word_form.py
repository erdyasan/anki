"""
Word add/edit form dialog.
Opens as a top-level window for creating or editing a vocabulary word.
"""

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from ..database import Word

WORD_TYPES = ["noun", "verb", "adjective", "adverb", "preposition", "conjunction", "pronoun", "interjection", "phrase"]


class WordFormDialog(ctk.CTkToplevel):
    """Modal dialog for adding or editing a word."""

    def __init__(
        self,
        parent: ctk.CTk,
        on_save: Callable[[Word, bool], Any],
        word: Word | None = None,
    ) -> None:
        super().__init__(parent)

        self._on_save = on_save
        self._editing_word = word
        self._is_edit_mode = word is not None
        self._error_label: ctk.CTkLabel | None = None

        self.title("Edit Word" if self._is_edit_mode else "Add New Word")
        self.geometry("600x700")
        self.resizable(False, True)

        # Delay UI build — CTkToplevel has a known rendering bug
        # where widgets don't appear if built before the window is mapped.
        self.after(100, lambda: self._init_form(parent, word))

    def _init_form(self, parent: ctk.CTk, word: Word | None) -> None:
        """Initialize form after window is mapped (avoids CTkToplevel render bug)."""
        self.transient(parent)
        self.grab_set()
        self._build_form()
        if self._is_edit_mode and word is not None:
            self._populate_form(word)

    def _build_form(self) -> None:
        """Build all form fields."""
        self._main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Word
        self._word_entry = self._add_entry("Word")

        # Word Type
        self._add_label("Word Type")
        self._type_var = ctk.StringVar(value=WORD_TYPES[0])
        self._type_menu = ctk.CTkOptionMenu(
            self._main_frame,
            variable=self._type_var,
            values=WORD_TYPES,
            width=250,
        )
        self._type_menu.pack(anchor="w", pady=(0, 12))

        # Translation
        self._translation_entry = self._add_entry("Translation (TR)")

        # Separator
        self._add_separator("Example 1")
        self._example1_entry = self._add_entry("English Sentence")
        self._example1_tr_entry = self._add_entry("Turkish Translation")

        self._add_separator("Example 2")
        self._example2_entry = self._add_entry("English Sentence")
        self._example2_tr_entry = self._add_entry("Turkish Translation")

        self._add_separator("Example 3")
        self._example3_entry = self._add_entry("English Sentence")
        self._example3_tr_entry = self._add_entry("Turkish Translation")

        # Hint
        hint = ctk.CTkLabel(
            self._main_frame,
            text="Tip: Use <b>word</b> to bold the target word in examples",
            text_color="gray",
            font=ctk.CTkFont(size=12),
        )
        hint.pack(anchor="w", pady=(8, 4))

        # Buttons
        btn_frame = ctk.CTkFrame(self._main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(16, 0))

        save_text = "Update" if self._is_edit_mode else "Add Word"
        ctk.CTkButton(
            btn_frame,
            text=save_text,
            command=self._handle_save,
            fg_color="#1a73e8",
            hover_color="#1557b0",
            width=140,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="gray",
            hover_color="#555",
            width=100,
        ).pack(side="right")

    def _add_label(self, text: str) -> ctk.CTkLabel:
        label = ctk.CTkLabel(
            self._main_frame,
            text=text,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        label.pack(anchor="w", pady=(4, 2))
        return label

    def _add_entry(self, placeholder: str) -> ctk.CTkEntry:
        self._add_label(placeholder)
        entry = ctk.CTkEntry(
            self._main_frame,
            placeholder_text=placeholder,
            width=540,
            height=36,
        )
        entry.pack(anchor="w", pady=(0, 8))
        return entry

    def _add_separator(self, title: str) -> None:
        sep_frame = ctk.CTkFrame(self._main_frame, fg_color="transparent")
        sep_frame.pack(fill="x", pady=(12, 4))
        ctk.CTkLabel(
            sep_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1a73e8",
        ).pack(anchor="w")

    def _populate_form(self, word: Word) -> None:
        """Fill form fields with existing word data for editing."""
        self._word_entry.insert(0, word.word)
        self._type_var.set(word.word_type)
        self._translation_entry.insert(0, word.translation)
        self._example1_entry.insert(0, word.example1)
        self._example1_tr_entry.insert(0, word.example1_tr)
        self._example2_entry.insert(0, word.example2)
        self._example2_tr_entry.insert(0, word.example2_tr)
        self._example3_entry.insert(0, word.example3)
        self._example3_tr_entry.insert(0, word.example3_tr)

    def _validate(self) -> str | None:
        """Validate form fields. Returns error message or None if valid."""
        if not self._word_entry.get().strip():
            return "Word is required"
        if not self._translation_entry.get().strip():
            return "Translation is required"
        if not self._example1_entry.get().strip():
            return "At least Example 1 is required"
        return None

    def _collect_word(self) -> Word:
        """Collect form data into a Word object."""
        word_id = self._editing_word.id if self._is_edit_mode and self._editing_word is not None else None
        return Word(
            id=word_id,
            word=self._word_entry.get().strip(),
            word_type=self._type_var.get(),
            translation=self._translation_entry.get().strip(),
            example1=self._example1_entry.get().strip(),
            example1_tr=self._example1_tr_entry.get().strip(),
            example2=self._example2_entry.get().strip(),
            example2_tr=self._example2_tr_entry.get().strip(),
            example3=self._example3_entry.get().strip(),
            example3_tr=self._example3_tr_entry.get().strip(),
        )

    def _handle_save(self) -> None:
        """Validate and save the word."""
        error = self._validate()
        if error:
            self._show_error(error)
            return

        word = self._collect_word()
        self._on_save(word, self._is_edit_mode)
        self.destroy()

    def _show_error(self, message: str) -> None:
        """Show a simple error label (replaces any existing one)."""
        if self._error_label is not None:
            self._error_label.destroy()

        self._error_label = ctk.CTkLabel(
            self._main_frame,
            text=message,
            text_color="#d32f2f",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._error_label.pack(anchor="w", pady=(4, 0))
