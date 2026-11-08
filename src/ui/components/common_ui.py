"""Common UI components and constants matching the Discovery Engine reference design.

Provides:
- Standard Top Mission Philosophy Banner Pill
- Standard Left-Aligned Hero Metric KPI Cards
- Standard Section Card Wrappers
"""

MISSION_BANNER_HTML = ""


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
