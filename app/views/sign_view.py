"""Sign Document View for CryptoGuard.

Provides detached document signing using an Ed25519 private key with support
for optional passphrase-protected PKCS#8 keys.
"""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk

from app.controllers.app_controller import AppController
from app.theme import COLORS, FONTS
from app.widgets import FilePickerRow, PasswordEntry, StatusBanner


class SignView(ctk.CTkFrame):
    """Document Signing Tab."""

    def __init__(self, master, controller: AppController, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)

        # Header description
        self.desc_label = ctk.CTkLabel(
            self,
            text="Generate a 64-byte detached digital signature (.sig) for any document using an Ed25519 private key.\nThe original document remains unmodified.",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="left",
            anchor="w",
        )
        self.desc_label.grid(row=0, column=0, padx=16, pady=(12, 16), sticky="w")

        # Inputs Card
        self.card = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10, border_width=1, border_color=COLORS["border"])
        self.card.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="nsew")
        self.card.grid_columnconfigure(0, weight=1)

        self.doc_row = FilePickerRow(
            self.card,
            label_text="Document to Sign:",
            dialog_title="Select Document to Sign",
            file_types=[("All Files", "*.*")],
            on_change=self._on_doc_selected,
        )
        self.doc_row.grid(row=0, column=0, padx=16, pady=(14, 6), sticky="ew")

        self.priv_row = FilePickerRow(
            self.card,
            label_text="Private Key (.pem):",
            dialog_title="Select Ed25519 Private Key",
            file_types=[("PEM Private Keys", "*.pem;*.key;*.pkcs8"), ("All Files", "*.*")],
        )
        self.priv_row.grid(row=1, column=0, padx=16, pady=6, sticky="ew")

        self.out_sig_row = FilePickerRow(
            self.card,
            label_text="Save Signature As:",
            dialog_title="Specify Detached Signature Path",
            file_types=[("Signature Files", "*.sig"), ("All Files", "*.*")],
            mode="save",
        )
        self.out_sig_row.grid(row=2, column=0, padx=16, pady=6, sticky="ew")

        self.pass_entry = PasswordEntry(
            self.card,
            label_text="Key Passphrase:",
            placeholder="Leave empty if private key is unencrypted...",
        )
        self.pass_entry.grid(row=3, column=0, padx=16, pady=(6, 14), sticky="ew")

        # Action Button
        self.sign_btn = ctk.CTkButton(
            self,
            text="Sign Document (Detached)",
            font=FONTS["body_bold"],
            height=40,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self._on_sign,
        )
        self.sign_btn.grid(row=2, column=0, padx=16, pady=(0, 14), sticky="w")

        # Status Notification Banner
        self.status_banner = StatusBanner(self)
        self.status_banner.grid(row=3, column=0, padx=16, pady=(0, 10), sticky="ew")

    def _on_doc_selected(self, doc_path: str):
        """Auto-populate signature output path when a document is selected."""
        if doc_path and not self.out_sig_row.get_path():
            self.out_sig_row.set_path(doc_path + ".sig")

    def _on_sign(self):
        doc = self.doc_row.get_path()
        priv = self.priv_row.get_path()
        out_sig = self.out_sig_row.get_path()
        password = self.pass_entry.get_password()

        res = self.controller.sign_document(
            doc_path=doc,
            priv_path=priv,
            out_sig_path=out_sig,
            password=password,
        )

        if res["success"]:
            self.status_banner.show(
                state="success",
                title="DOCUMENT SIGNED SUCCESSFULLY",
                details=f"Detached signature written to:\n{res['signature_path']}\nSize: {res['size']} bytes (RFC 8032 Ed25519 standard)",
            )
        else:
            self.status_banner.show(
                state="error",
                title="SIGNING FAILED",
                details=res["message"],
            )
