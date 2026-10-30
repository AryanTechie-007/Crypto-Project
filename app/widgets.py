"""Reusable UI Widgets for CryptoGuard Desktop Application.

Provides styled components for file selection, masked password inputs,
status notification banners, and copyable text fields.
"""

from __future__ import annotations

import tkinter.filedialog as fd
from pathlib import Path
from typing import List, Optional, Tuple

import customtkinter as ctk

from app.theme import COLORS, FONTS


class FilePickerRow(ctk.CTkFrame):
    """Row widget combining a title label, file path entry, and Browse button."""

    def __init__(
        self,
        master,
        label_text: str,
        dialog_title: str = "Select File",
        file_types: Optional[List[Tuple[str, str]]] = None,
        default_path: str = "",
        mode: str = "open",  # "open" or "save"
        on_change=None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.dialog_title = dialog_title
        self.file_types = file_types or [("All Files", "*.*")]
        self.mode = mode
        self.on_change = on_change

        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
            width=160,
            anchor="w",
        )
        self.label.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="w")

        self.entry = ctk.CTkEntry(
            self,
            font=FONTS["body"],
            height=34,
            placeholder_text="No file selected...",
        )
        self.entry.grid(row=0, column=1, padx=(0, 8), pady=4, sticky="ew")

        if default_path:
            self.set_path(default_path)

        self.browse_btn = ctk.CTkButton(
            self,
            text="Browse...",
            width=90,
            height=34,
            font=FONTS["body"],
            fg_color=COLORS["subtle_bg"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            command=self._on_browse,
        )
        self.browse_btn.grid(row=0, column=2, pady=4, sticky="e")

    def _on_browse(self):
        curr = self.get_path()
        initial_dir = str(Path(curr).parent) if curr and Path(curr).parent.exists() else None

        if self.mode == "save":
            path = fd.asksaveasfilename(
                title=self.dialog_title,
                filetypes=self.file_types,
                initialdir=initial_dir,
            )
        else:
            path = fd.askopenfilename(
                title=self.dialog_title,
                filetypes=self.file_types,
                initialdir=initial_dir,
            )

        if path:
            self.set_path(path)
            if self.on_change:
                self.on_change(path)

    def get_path(self) -> str:
        return self.entry.get().strip()

    def set_path(self, path: str):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(path))


class PasswordEntry(ctk.CTkFrame):
    """Masked passphrase field with a show/hide toggle button."""

    def __init__(self, master, label_text: str = "Passphrase:", placeholder: str = "", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(1, weight=1)
        self._is_masked = True

        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
            width=160,
            anchor="w",
        )
        self.label.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="w")

        self.entry = ctk.CTkEntry(
            self,
            show="*",
            font=FONTS["body"],
            height=34,
            placeholder_text=placeholder,
        )
        self.entry.grid(row=0, column=1, padx=(0, 8), pady=4, sticky="ew")

        self.toggle_btn = ctk.CTkButton(
            self,
            text="Show",
            width=65,
            height=34,
            font=FONTS["small"],
            fg_color=COLORS["subtle_bg"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            command=self._toggle_mask,
        )
        self.toggle_btn.grid(row=0, column=2, pady=4, sticky="e")

    def _toggle_mask(self):
        self._is_masked = not self._is_masked
        self.entry.configure(show="" if not self._is_masked else "*")
        self.toggle_btn.configure(text="Hide" if not self._is_masked else "Show")

    def get_password(self) -> str:
        return self.entry.get()

    def clear(self):
        self.entry.delete(0, "end")


class StatusBanner(ctk.CTkFrame):
    """Full-width result banner with dynamic color themes (success, error, info)."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            corner_radius=8,
            border_width=1,
            fg_color=COLORS["subtle_bg"],
            border_color=COLORS["border"],
            **kwargs,
        )

        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text="",
            font=FONTS["subheading"],
            anchor="w",
            justify="left",
        )
        self.title_label.grid(row=0, column=0, padx=14, pady=(10, 2), sticky="w")

        self.details_label = ctk.CTkLabel(
            self,
            text="",
            font=FONTS["body"],
            anchor="w",
            justify="left",
            wraplength=600,
        )
        self.details_label.grid(row=1, column=0, padx=14, pady=(0, 10), sticky="w")

        self.grid_remove()  # Hidden by default

    def show(self, state: str, title: str, details: str = ""):
        """Display the banner with state theme ('success', 'error', 'info', 'warning')."""
        fg_key = f"{state}_bg"
        text_key = f"{state}_fg"
        border_key = f"{state}_border"

        bg_color = COLORS.get(fg_key, COLORS["subtle_bg"])
        text_color = COLORS.get(text_key, COLORS["text_primary"])
        border_color = COLORS.get(border_key, COLORS["border"])

        self.configure(fg_color=bg_color, border_color=border_color)
        self.title_label.configure(text=title, text_color=text_color)

        if details:
            self.details_label.configure(text=details, text_color=text_color)
            self.details_label.grid()
        else:
            self.details_label.grid_remove()

        self.grid()

    def clear(self):
        self.grid_remove()


class CopyableText(ctk.CTkFrame):
    """Monospaced text display with a one-click Copy button."""

    def __init__(self, master, label_text: str = "", text: str = "", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(1, weight=1)

        if label_text:
            self.label = ctk.CTkLabel(
                self,
                text=label_text,
                font=FONTS["body_bold"],
                text_color=COLORS["text_primary"],
                anchor="w",
            )
            self.label.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="w")

        self.entry = ctk.CTkEntry(
            self,
            font=FONTS["code_small"],
            height=32,
            fg_color=COLORS["subtle_bg"],
        )
        self.entry.grid(row=0, column=1, padx=(0, 8), pady=4, sticky="ew")
        if text:
            self.set_text(text)

        self.copy_btn = ctk.CTkButton(
            self,
            text="Copy",
            width=70,
            height=32,
            font=FONTS["small"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._on_copy,
        )
        self.copy_btn.grid(row=0, column=2, pady=4, sticky="e")

    def _on_copy(self):
        val = self.get_text()
        if val:
            self.clipboard_clear()
            self.clipboard_append(val)
            self.copy_btn.configure(text="Copied!")
            self.after(1500, lambda: self.copy_btn.configure(text="Copy"))

    def get_text(self) -> str:
        return self.entry.get().strip()

    def set_text(self, text: str):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(text))
