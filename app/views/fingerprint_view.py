"""Public-Key Fingerprinting and Trust Verification View for CryptoGuard.

Computes canonical SHA-256 fingerprints of Ed25519 public keys and verifies
fingerprint matches against out-of-band reference values to detect substitution attacks.
"""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk

from app.controllers.app_controller import AppController
from app.theme import COLORS, FONTS
from app.widgets import CopyableText, FilePickerRow, StatusBanner

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class FingerprintView(ctk.CTkFrame):
    """Public Key Fingerprinting and Out-of-Band Trust Validation Tab."""

    def __init__(self, master, controller: AppController, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)

        # Header description
        self.desc_label = ctk.CTkLabel(
            self,
            text="Compute the canonical SHA-256 fingerprint of an Ed25519 public key (RFC 8410 SPKI DER format).\nCompare against a trusted out-of-band reference to defend against public-key substitution attacks (Req 7).",
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

        default_pub = str(ROOT_DIR / "artifacts" / "signer_public_key.pem")

        self.pub_row = FilePickerRow(
            self.card,
            label_text="Public Key (.pem):",
            dialog_title="Select Public Key to Inspect",
            file_types=[("PEM Public Keys", "*.pem;*.pub"), ("All Files", "*.*")],
            default_path=default_pub if Path(default_pub).exists() else "",
        )
        self.pub_row.grid(row=0, column=0, padx=16, pady=(14, 10), sticky="ew")

        # Action: Compute Fingerprint
        self.compute_btn = ctk.CTkButton(
            self.card,
            text="Compute Canonical Fingerprint",
            font=FONTS["body_bold"],
            height=36,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._on_compute,
        )
        self.compute_btn.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")

        # Result Fingerprint Display
        self.fp_display = CopyableText(self, label_text="SHA-256 Fingerprint:")
        self.fp_display.grid(row=2, column=0, padx=16, pady=(0, 14), sticky="ew")

        # Trust Validation Card
        self.trust_card = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10, border_width=1, border_color=COLORS["border"])
        self.trust_card.grid(row=3, column=0, padx=16, pady=(0, 14), sticky="nsew")
        self.trust_card.grid_columnconfigure(1, weight=1)

        self.trust_header = ctk.CTkLabel(
            self.trust_card,
            text="Out-of-Band Trust Comparison (Requirement 7 & Experiment 5)",
            font=FONTS["subheading"],
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        self.trust_header.grid(row=0, column=0, columnspan=2, padx=16, pady=(12, 6), sticky="w")

        self.exp_label = ctk.CTkLabel(
            self.trust_card,
            text="Trusted Reference:",
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
            width=140,
            anchor="w",
        )
        self.exp_label.grid(row=1, column=0, padx=(16, 10), pady=6, sticky="w")

        self.exp_entry = ctk.CTkEntry(
            self.trust_card,
            font=FONTS["code_small"],
            height=34,
            placeholder_text="e.g. SHA256:56:fe:17:fc:1f:68:09:4e:93:34:a6...",
        )
        self.exp_entry.grid(row=1, column=1, padx=(0, 16), pady=6, sticky="ew")

        self.verify_trust_btn = ctk.CTkButton(
            self.trust_card,
            text="Verify Fingerprint Match",
            font=FONTS["body_bold"],
            height=36,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self._on_verify_trust,
        )
        self.verify_trust_btn.grid(row=2, column=0, columnspan=2, padx=16, pady=(6, 14), sticky="w")

        # Status Notification Banner
        self.status_banner = StatusBanner(self)
        self.status_banner.grid(row=4, column=0, padx=16, pady=(0, 10), sticky="ew")

        # Auto-compute for default path if present
        if default_pub and Path(default_pub).exists():
            self._on_compute()

    def _on_compute(self):
        pub = self.pub_row.get_path()
        res = self.controller.compute_fingerprint(pub)

        if res["success"]:
            self.fp_display.set_text(res["fingerprint"])
            self.status_banner.show(
                state="info",
                title="FINGERPRINT COMPUTED (CANONICAL SPKI DER)",
                details="Format: OpenSSH/OpenSSL standard colon-separated hex digest over SubjectPublicKeyInfo DER.",
            )
        else:
            self.fp_display.set_text("")
            self.status_banner.show(
                state="error",
                title="FINGERPRINT COMPUTATION FAILED",
                details=res["message"],
            )

    def _on_verify_trust(self):
        pub = self.pub_row.get_path()
        expected = self.exp_entry.get().strip()

        if not expected:
            self.status_banner.show(
                state="warning",
                title="NO REFERENCE SUPPLIED",
                details="Please enter or paste an expected fingerprint obtained through a trusted channel (e.g. university registrar, authenticated email).",
            )
            return

        res = self.controller.compute_fingerprint(pub, expected=expected)

        if not res["success"]:
            self.status_banner.show(state="error", title="ERROR", details=res["message"])
            return

        if res["matches"]:
            self.status_banner.show(
                state="success",
                title="TRUSTED — FINGERPRINT MATCHES",
                details="The public key matches the authenticated reference value. Public key substitution is ruled out.",
            )
        else:
            self.status_banner.show(
                state="error",
                title="UNTRUSTED — FINGERPRINT MISMATCH",
                details=f"WARNING: The public key's fingerprint does NOT match the expected reference!\nCalculated: {res['fingerprint']}\nExpected:   {expected}\nThis public key may have been substituted by an attacker (Experiment 5).",
            )
