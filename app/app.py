"""CryptoGuard Main Application Window.

Assembles the tabbed navigation, appearance mode controls, and view components
into a standalone desktop application.
"""

from __future__ import annotations

import customtkinter as ctk

from app.controllers.app_controller import AppController
from app.theme import COLORS, FONTS
from app.views.fingerprint_view import FingerprintView
from app.views.keygen_view import KeygenView
from app.views.sign_view import SignView
from app.views.verify_view import VerifyView


class CryptoGuardApp(ctk.CTk):
    """Main desktop application window for CryptoGuard."""

    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("CryptoGuard — Ed25519 Document Verification System")
        self.geometry("860x680")
        self.minsize(780, 580)

        # Set default appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize shared controller
        self.controller = AppController()

        # Grid configuration
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Build UI Sections
        self._build_header()
        self._build_tabs()
        self._build_footer()

    def _build_header(self):
        """Top navigation and branding bar."""
        self.header_frame = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=0, height=64)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Brand Title & Subtitle
        title_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=10)

        self.app_title = ctk.CTkLabel(
            title_box,
            text="CryptoGuard",
            font=FONTS["title"],
            text_color=COLORS["text_primary"],
        )
        self.app_title.pack(anchor="w")

        self.app_sub = ctk.CTkLabel(
            title_box,
            text="Ed25519 Digital Signature & Public-Key Verification Suite (RFC 8032)",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        )
        self.app_sub.pack(anchor="w")

        # Theme Switcher (Dark / Light)
        theme_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        theme_box.pack(side="right", padx=20, pady=10)

        self.theme_label = ctk.CTkLabel(
            theme_box,
            text="Dark Mode:",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        )
        self.theme_label.pack(side="left", padx=(0, 8))

        self.theme_switch = ctk.CTkSwitch(
            theme_box,
            text="",
            width=42,
            command=self._on_theme_toggle,
        )
        self.theme_switch.select()  # Start in dark mode
        self.theme_switch.pack(side="left")

    def _build_tabs(self):
        """Tabbed view hosting the 4 operational workflows."""
        self.tabview = ctk.CTkTabview(
            self,
            fg_color="transparent",
            segmented_button_fg_color=COLORS["subtle_bg"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_hover"],
            segmented_button_unselected_color=COLORS["subtle_bg"],
            segmented_button_unselected_hover_color=COLORS["border"],
            text_color=COLORS["text_primary"],
        )
        self.tabview.grid(row=1, column=0, padx=20, pady=(6, 10), sticky="nsew")

        # Tab 1: Verify Document
        tab_verify = self.tabview.add("Verify Document")
        tab_verify.grid_columnconfigure(0, weight=1)
        self.verify_view = VerifyView(tab_verify, controller=self.controller)
        self.verify_view.grid(row=0, column=0, sticky="nsew")

        # Tab 2: Sign Document
        tab_sign = self.tabview.add("Sign Document")
        tab_sign.grid_columnconfigure(0, weight=1)
        self.sign_view = SignView(tab_sign, controller=self.controller)
        self.sign_view.grid(row=0, column=0, sticky="nsew")

        # Tab 3: Key Generation
        tab_keygen = self.tabview.add("Generate Keys")
        tab_keygen.grid_columnconfigure(0, weight=1)
        self.keygen_view = KeygenView(tab_keygen, controller=self.controller)
        self.keygen_view.grid(row=0, column=0, sticky="nsew")

        # Tab 4: Public Key Fingerprint
        tab_fp = self.tabview.add("Public Key Fingerprint")
        tab_fp.grid_columnconfigure(0, weight=1)
        self.fp_view = FingerprintView(tab_fp, controller=self.controller)
        self.fp_view.grid(row=0, column=0, sticky="nsew")

        # Set default tab
        self.tabview.set("Verify Document")

    def _build_footer(self):
        """Bottom status information bar."""
        self.footer_frame = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=0, height=28)
        self.footer_frame.grid(row=2, column=0, sticky="ew")

        left_lbl = ctk.CTkLabel(
            self.footer_frame,
            text="University Cryptography Assessment • Project 4: Digital Signatures",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        )
        left_lbl.pack(side="left", padx=20, pady=4)

        right_lbl = ctk.CTkLabel(
            self.footer_frame,
            text="Algorithm: RFC 8032 Ed25519 (SHA-512 / Curve25519) | Status: Active",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
        )
        right_lbl.pack(side="right", padx=20, pady=4)

    def _on_theme_toggle(self):
        """Toggle between Dark and Light mode."""
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")


def run():
    """Launch the CryptoGuard desktop application."""
    app = CryptoGuardApp()
    app.mainloop()


if __name__ == "__main__":
    run()
