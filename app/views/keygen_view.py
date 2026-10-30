"""Key Generation View for CryptoGuard.

Generates Ed25519 asymmetric key pairs with optional PKCS#8 passphrase encryption
and exports public keys in SPKI format.
"""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk

from app.controllers.app_controller import AppController
from app.theme import COLORS, FONTS
from app.widgets import CopyableText, FilePickerRow, PasswordEntry, StatusBanner

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class KeygenView(ctk.CTkFrame):
    """Ed25519 Key Pair Generation Tab."""

    def __init__(self, master, controller: AppController, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)

        # Header description
        self.desc_label = ctk.CTkLabel(
            self,
            text="Generate a cryptographically secure Ed25519 key pair using OS entropy.\nPublic keys are exported in SPKI PEM format; private keys in PKCS#8 with optional AES-256 encryption.",
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

        default_priv = str(ROOT_DIR / "private" / "my_private_key.pem")
        default_pub = str(ROOT_DIR / "keys" / "my_public_key.pem")

        self.priv_row = FilePickerRow(
            self.card,
            label_text="Save Private Key To:",
            dialog_title="Choose Private Key Destination",
            file_types=[("PEM Private Key", "*.pem;*.key"), ("All Files", "*.*")],
            default_path=default_priv,
            mode="save",
        )
        self.priv_row.grid(row=0, column=0, padx=16, pady=(14, 6), sticky="ew")

        self.pub_row = FilePickerRow(
            self.card,
            label_text="Save Public Key To:",
            dialog_title="Choose Public Key Destination",
            file_types=[("PEM Public Key", "*.pem;*.pub"), ("All Files", "*.*")],
            default_path=default_pub,
            mode="save",
        )
        self.pub_row.grid(row=1, column=0, padx=16, pady=6, sticky="ew")

        # Encryption Toggle
        self.encrypt_var = ctk.BooleanVar(value=True)
        self.encrypt_chk = ctk.CTkCheckBox(
            self.card,
            text="Encrypt private key with passphrase (Recommended)",
            variable=self.encrypt_var,
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
            command=self._on_toggle_encryption,
        )
        self.encrypt_chk.grid(row=2, column=0, padx=16, pady=(10, 6), sticky="w")

        # Passphrase Entries
        self.pass_entry = PasswordEntry(
            self.card,
            label_text="Passphrase:",
            placeholder="Enter a secure passphrase...",
        )
        self.pass_entry.grid(row=3, column=0, padx=16, pady=6, sticky="ew")

        self.confirm_entry = PasswordEntry(
            self.card,
            label_text="Confirm Passphrase:",
            placeholder="Confirm passphrase...",
        )
        self.confirm_entry.grid(row=4, column=0, padx=16, pady=(6, 10), sticky="ew")

        # Overwrite Guard Checkbox
        self.force_var = ctk.BooleanVar(value=False)
        self.force_chk = ctk.CTkCheckBox(
            self.card,
            text="Allow overwriting existing key files",
            variable=self.force_var,
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        )
        self.force_chk.grid(row=5, column=0, padx=16, pady=(0, 14), sticky="w")

        # Action Button
        self.gen_btn = ctk.CTkButton(
            self,
            text="Generate Ed25519 Key Pair",
            font=FONTS["body_bold"],
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._on_generate,
        )
        self.gen_btn.grid(row=2, column=0, padx=16, pady=(0, 14), sticky="w")

        # Status Banner
        self.status_banner = StatusBanner(self)
        self.status_banner.grid(row=3, column=0, padx=16, pady=(0, 10), sticky="ew")

        # Generated Public Key Fingerprint
        self.fp_display = CopyableText(self, label_text="Public Key Fingerprint:")
        self.fp_display.grid(row=4, column=0, padx=16, pady=(0, 10), sticky="ew")
        self.fp_display.grid_remove()

    def _on_toggle_encryption(self):
        if self.encrypt_var.get():
            self.pass_entry.grid()
            self.confirm_entry.grid()
        else:
            self.pass_entry.grid_remove()
            self.confirm_entry.grid_remove()

    def _on_generate(self):
        priv = self.priv_row.get_path()
        pub = self.pub_row.get_path()
        force = self.force_var.get()

        password = None
        if self.encrypt_var.get():
            p1 = self.pass_entry.get_password()
            p2 = self.confirm_entry.get_password()
            if not p1:
                self.status_banner.show(
                    state="error",
                    title="PASSPHRASE REQUIRED",
                    details="Encryption is enabled, but the passphrase field is empty. Enter a passphrase or uncheck encryption.",
                )
                return
            if p1 != p2:
                self.status_banner.show(
                    state="error",
                    title="PASSPHRASE MISMATCH",
                    details="The confirmation passphrase does not match. Please re-enter.",
                )
                return
            password = p1

        res = self.controller.generate_keys(
            priv_path=priv,
            pub_path=pub,
            password=password,
            force=force,
        )

        if res["success"]:
            enc_info = "[ENCRYPTED WITH AES-256]" if res["encrypted"] else "[UNENCRYPTED]"
            self.status_banner.show(
                state="success",
                title="KEY PAIR GENERATED SUCCESSFULLY",
                details=f"Private Key: {res['priv_path']} {enc_info}\nPublic Key:  {res['pub_path']}\n\nSecurity Notice (Req 8): Keep the private key confidential. Never commit it to git.",
            )
            self.fp_display.set_text(res["fingerprint"])
            self.fp_display.grid()
        else:
            self.status_banner.show(
                state="error",
                title="GENERATION FAILED",
                details=res["message"],
            )
            self.fp_display.grid_remove()
