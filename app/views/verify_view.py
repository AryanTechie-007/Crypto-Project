"""Verify Document View for CryptoGuard.

Allows users to verify arbitrary documents against detached Ed25519 signatures
and public keys with instant visual feedback and root-cause explanations.
"""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk

from app.controllers.app_controller import AppController
from app.theme import COLORS, FONTS
from app.widgets import CopyableText, FilePickerRow, StatusBanner

# Repository Root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class VerifyView(ctk.CTkFrame):
    """Document Signature Verification Tab."""

    def __init__(self, master, controller: AppController, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)

        # Header description
        self.desc_label = ctk.CTkLabel(
            self,
            text="Verify that a document's detached signature matches the author's Ed25519 public key\nand confirm the document is 100% authentic and unmodified.",
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

        default_doc = str(ROOT_DIR / "sample_data" / "sample_document.txt")
        default_sig = str(ROOT_DIR / "artifacts" / "sample_document.sig")
        default_pub = str(ROOT_DIR / "artifacts" / "signer_public_key.pem")

        self.doc_row = FilePickerRow(
            self.card,
            label_text="Original Document:",
            dialog_title="Select Document to Verify",
            file_types=[("Text / Data Documents", "*.txt;*.pdf;*.docx;*.*"), ("All Files", "*.*")],
            default_path=default_doc if Path(default_doc).exists() else "",
        )
        self.doc_row.grid(row=0, column=0, padx=16, pady=(14, 6), sticky="ew")

        self.sig_row = FilePickerRow(
            self.card,
            label_text="Detached Signature (.sig):",
            dialog_title="Select Detached Signature File",
            file_types=[("Signature Files", "*.sig"), ("All Files", "*.*")],
            default_path=default_sig if Path(default_sig).exists() else "",
        )
        self.sig_row.grid(row=1, column=0, padx=16, pady=6, sticky="ew")

        self.pub_row = FilePickerRow(
            self.card,
            label_text="Signer Public Key (.pem):",
            dialog_title="Select Signer's Public Key",
            file_types=[("PEM Public Keys", "*.pem;*.pub"), ("All Files", "*.*")],
            default_path=default_pub if Path(default_pub).exists() else "",
        )
        self.pub_row.grid(row=2, column=0, padx=16, pady=(6, 14), sticky="ew")

        # Action Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, padx=16, pady=(0, 14), sticky="ew")

        self.verify_btn = ctk.CTkButton(
            self.btn_frame,
            text="Check Signature & Integrity",
            font=FONTS["body_bold"],
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._on_verify,
        )
        self.verify_btn.pack(side="left", padx=(0, 10))

        self.reset_btn = ctk.CTkButton(
            self.btn_frame,
            text="Load Sample Artifacts",
            font=FONTS["body"],
            height=40,
            fg_color=COLORS["subtle_bg"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            command=self._load_sample_defaults,
        )
        self.reset_btn.pack(side="left")

        # Status Notification Banner
        self.status_banner = StatusBanner(self)
        self.status_banner.grid(row=3, column=0, padx=16, pady=(0, 10), sticky="ew")

        # Fingerprint Output Display (populated on successful verification)
        self.fp_display = CopyableText(self, label_text="Signer Fingerprint:")
        self.fp_display.grid(row=4, column=0, padx=16, pady=(0, 10), sticky="ew")
        self.fp_display.grid_remove()

    def _on_verify(self):
        doc = self.doc_row.get_path()
        sig = self.sig_row.get_path()
        pub = self.pub_row.get_path()

        res = self.controller.verify_document(doc, sig, pub)

        if res["is_valid"]:
            self.status_banner.show(
                state="success",
                title="AUTHENTIC & UNMODIFIED",
                details=f"{res['message']}\n{res['details'] or ''}".strip(),
            )
            if res.get("fingerprint"):
                self.fp_display.set_text(res["fingerprint"])
                self.fp_display.grid()
            else:
                self.fp_display.grid_remove()
        else:
            self.status_banner.show(
                state="error",
                title="NOT AUTHENTIC (VERIFICATION FAILED)",
                details=f"{res['message']}\n{res['details'] or ''}".strip(),
            )
            self.fp_display.grid_remove()

    def _load_sample_defaults(self):
        self.doc_row.set_path(str(ROOT_DIR / "sample_data" / "sample_document.txt"))
        self.sig_row.set_path(str(ROOT_DIR / "artifacts" / "sample_document.sig"))
        self.pub_row.set_path(str(ROOT_DIR / "artifacts" / "signer_public_key.pem"))
        self.status_banner.clear()
        self.fp_display.grid_remove()
