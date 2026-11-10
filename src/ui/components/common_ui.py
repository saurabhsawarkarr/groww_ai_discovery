"""Common UI components and constants matching the Discovery Engine reference design.

Provides:
- Standard Top Mission Philosophy Banner Pill
- Standard Left-Aligned Hero Metric KPI Cards
- Standard Section Card Wrappers
"""

import html
import re

MISSION_BANNER_HTML = ""

_SYNTHETIC_URL_RE = re.compile(
    r"(?:/comments/(?:\d{3}_|exp_|g\d+_)|watch\?v=(?:vid\d+|tax_sip|sip_xirr|groww_sip)|reviewId=gp_|apps\.apple\.com/in/app/groww-stocks-mutual-fund/id)",
    re.IGNORECASE,
)


def format_source_link_html(
    source_url: str,
    label: str = "[Source Link ↗]",
    color: str = "#00D09C",
    font_size: str = "11px",
    text_decoration: str = "none",
    extra_style: str = "",
) -> str:
    """Render a safe, clickable external source anchor tag for verified http(s) URLs."""
    url = (source_url or "").strip()
    if not url.startswith(("http://", "https://")):
        return ""
    if _SYNTHETIC_URL_RE.search(url):
        return ""
    safe_href = html.escape(url, quote=True)
    safe_label = html.escape(label)
    style = f"color: {color}; font-weight: 600; text-decoration: {text_decoration}; font-size: {font_size}; {extra_style}".strip()
    return f'<a href="{safe_href}" target="_blank" rel="noopener noreferrer" style="{style}">{safe_label}</a>'


def get_kpi_card_html(
    title: str,
    value: str,
    subtitle: str,
    value_color: str = "#F1F5F9",
    sub_color: str = "#00D09C",
) -> str:
    """Generate HTML for left-aligned crisp KPI card styled for dark Groww theme."""
    return f"""<div class="executive-kpi-card">
<div class="kpi-title">{title}</div>
<div class="kpi-value" style="color: {value_color};">{value}</div>
<div class="kpi-subtitle" style="color: {sub_color};">{subtitle}</div>
</div>"""
