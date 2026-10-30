"""CryptoGuard Theme and Design System.

Defines color palettes, font configurations, and component styling for both
light and dark appearance modes in CustomTkinter.
"""

from __future__ import annotations

# Color Palettes (Light, Dark tuples for CustomTkinter native theme switching)
COLORS = {
    # Brand
    "primary": ("#2B6CB0", "#3182CE"),
    "primary_hover": ("#2C5282", "#2B6CB0"),
    "accent": ("#319795", "#38B2AC"),
    "accent_hover": ("#285E61", "#319795"),

    # Backgrounds & Cards
    "card_bg": ("#FFFFFF", "#1A202C"),
    "subtle_bg": ("#EDF2F7", "#2D3748"),
    "border": ("#E2E8F0", "#4A5568"),

    # Text
    "text_primary": ("#1A202C", "#F7FAFC"),
    "text_secondary": ("#718096", "#A0AEC0"),
    "text_muted": ("#A0AEC0", "#718096"),

    # Status Banners
    "success_bg": ("#C6F6D5", "#1C4532"),
    "success_fg": ("#22543D", "#9AE6B4"),
    "success_border": ("#9AE6B4", "#276749"),

    "error_bg": ("#FED7D7", "#742A2A"),
    "error_fg": ("#9B2C2C", "#FEB2B2"),
    "error_border": ("#FEB2B2", "#9B2C2C"),

    "warning_bg": ("#FEFCBF", "#744210"),
    "warning_fg": ("#744210", "#FAF089"),
    "warning_border": ("#FAF089", "#975A16"),

    "info_bg": ("#BEE3F8", "#2A4365"),
    "info_fg": ("#2B6CB0", "#90CDF4"),
    "info_border": ("#90CDF4", "#2B6CB0"),
}

# Typography
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"

FONTS = {
    "title": (FONT_FAMILY, 20, "bold"),
    "subtitle": (FONT_FAMILY, 12),
    "heading": (FONT_FAMILY, 15, "bold"),
    "subheading": (FONT_FAMILY, 13, "bold"),
    "body": (FONT_FAMILY, 12),
    "body_bold": (FONT_FAMILY, 12, "bold"),
    "small": (FONT_FAMILY, 10),
    "code": (FONT_MONO, 11),
    "code_small": (FONT_MONO, 10),
}
