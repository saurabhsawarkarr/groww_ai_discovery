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
    value_color: str = "#0F172A",
    sub_color: str = "#008764",
) -> str:
    """Generate HTML for left-aligned crisp KPI card exactly matching the inspiration screenshot."""
    return f"""<div class="executive-kpi-card">
<div class="kpi-title">{title}</div>
<div class="kpi-value" style="color: {value_color};">{value}</div>
<div class="kpi-subtitle" style="color: {sub_color};">{subtitle}</div>
</div>"""

