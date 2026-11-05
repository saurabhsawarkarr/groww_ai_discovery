"""Generator for Two-Screen Mobile UI User Flows for the 5 Market Fluctuation Solutions.
Renders side-by-side mobile screens (Screen 1: Trigger -> Screen 2: Resolution) in a single image.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Arrow, FancyArrowPatch
import numpy as np

OUTPUT_DIRS = [
    Path("deliverables/screens"),
    Path("C:/Users/KAUSTUBH/.gemini/antigravity/brain/708df285-86a7-405f-be3f-5a6d8dc3d597/screens")
]

# Color Palette
BG_CANVAS = "#0F172A"       # Dark slate canvas for high contrast presentation
FLOW_HEADER_BG = "#1E293B"
BORDER_CANVAS = "#334155"

PHONE_BG = "#F8FAFC"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E2E8F0"

TEXT_DARK = "#0F172A"
TEXT_MUTED = "#64748B"
TEXT_LIGHT = "#94A3B8"
TEXT_WHITE = "#FFFFFF"

GROWW_GREEN = "#00D09C"
GROWW_DARK_GREEN = "#008764"
GROWW_GREEN_BG = "#E6FBF5"

RED_ACCENT = "#EF4444"
RED_BG = "#FEF2F2"

BLUE_ACCENT = "#3B82F6"
BLUE_BG = "#EFF6FF"

PURPLE_ACCENT = "#8B5CF6"
PURPLE_BG = "#F5F3FF"

AMBER_ACCENT = "#F59E0B"
AMBER_BG = "#FFFBEB"


def setup_flow_canvas(title="Solution Flow", subtitle="Screen 1 (Trigger) -> Screen 2 (Resolution)"):
    """Creates a 16:10 wide canvas for side-by-side phone mockups and flow connectors."""
    fig, ax = plt.subplots(figsize=(16, 10), dpi=150)
    fig.patch.set_facecolor(BG_CANVAS)
    ax.set_facecolor(BG_CANVAS)
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Header Bar
    ax.add_patch(FancyBboxPatch((4, 88), 152, 9, boxstyle="round,pad=1,rounding_size=2",
                                facecolor=FLOW_HEADER_BG, edgecolor=BORDER_CANVAS, lw=1))
    ax.text(8, 93.5, title.upper(), fontsize=13, fontweight="bold", color=GROWW_GREEN, va="center")
    ax.text(8, 90, subtitle, fontsize=9.5, color="#94A3B8", va="center")
    ax.text(152, 92.5, "GROWW MUTUAL FUNDS • USER RETENTION FLOW", fontsize=8.5, fontweight="bold", color="#64748B", ha="right", va="center")

    # Flow Arrow in center
    arrow = FancyArrowPatch((74, 46), (86, 46),
                            arrowstyle='Simple,tail_width=2.5,head_width=9,head_length=9',
                            color=GROWW_GREEN, lw=1)
    ax.add_patch(arrow)

    return fig, ax


def draw_phone_bezel(ax, x_offset, y_offset, width=60, height=76, screen_title="Groww", step_badge="STEP 1"):
    """Draws a phone container on the canvas."""
    # Outer device chassis shadow / border
    ax.add_patch(FancyBboxPatch((x_offset, y_offset), width, height,
                                boxstyle="round,pad=1.2,rounding_size=3.5",
                                facecolor=PHONE_BG, edgecolor=BORDER_CANVAS, lw=1.5))

    # Top Status & Header
    top_y = y_offset + height
    # Notch / Camera pill
    ax.add_patch(FancyBboxPatch((x_offset + width/2 - 7, top_y - 2.8), 14, 2,
                                boxstyle="round,pad=0.2,rounding_size=1",
                                facecolor="#CBD5E1", edgecolor="none"))

    # Step Badge Above Phone
    ax.add_patch(FancyBboxPatch((x_offset, top_y + 1.2), 26, 3.8,
                                boxstyle="round,pad=0.5,rounding_size=1.5",
                                facecolor=GROWW_DARK_GREEN, edgecolor="none"))
    ax.text(x_offset + 13, top_y + 3.1, step_badge, fontsize=8, fontweight="bold", color=TEXT_WHITE, ha="center", va="center")

    # In-App App Bar
    ax.text(x_offset + 4, top_y - 6.5, "←", fontsize=11, color=TEXT_DARK, va="center")
    ax.text(x_offset + 10, top_y - 6.3, screen_title, fontsize=9.5, fontweight="bold", color=TEXT_DARK, va="center")
    # Avatar / help
    ax.add_patch(Circle((x_offset + width - 6, top_y - 6.5), 2.2, facecolor="#E2E8F0"))
    ax.text(x_offset + width - 6, top_y - 6.5, "?", fontsize=7.5, fontweight="bold", color=TEXT_DARK, ha="center", va="center")


def save_flow_screen(fig, filename):
    for d in OUTPUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        path = d / filename
        fig.savefig(path, bbox_inches="tight", dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Saved Flow: {filename}")

# ==============================================================================
# FLOW 1: ACCUMULATION LENS FLOW
# ==============================================================================
def create_flow_1():
    fig, ax = setup_flow_canvas(
        "Solution 1: The Accumulation Lens Flow",
        "Screen 1 (Drawdown Trigger & Anxiety)  ──▶  Screen 2 (Accumulation Reframing & Conviction)"
    )
    # Center transition caption
    ax.text(80, 52, "User taps banner\nduring -3.2% dip", fontsize=9, fontweight="bold", color="#38BDF8", ha="center")

    # SCREEN 1 (LEFT): Standard Portfolio with Market Dip & Entry Trigger
    draw_phone_bezel(ax, 10, 8, 60, 76, "Groww Portfolio", "SCREEN 1: THE TRIGGER")

    # Screen 1 Content
    # Red Market Movement Banner
    ax.add_patch(FancyBboxPatch((13, 67), 54, 8, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor=RED_BG, edgecolor="#FCA5A5", lw=0.8))
    ax.text(16, 71, "Nifty 50 is down -3.2% today", fontsize=8, fontweight="bold", color=RED_ACCENT)
    ax.text(16, 68.5, "Sensex fell 780 pts on global inflation cues", fontsize=6.8, color=TEXT_MUTED)

    # Standard Rupee Valuation (The Anxiety Source)
    ax.add_patch(FancyBboxPatch((13, 40), 54, 25, boxstyle="round,pad=1.2,rounding_size=3",
                                facecolor=CARD_BG, edgecolor=CARD_BORDER, lw=1))
    ax.text(16, 60, "TOTAL PORTFOLIO VALUE", fontsize=7, fontweight="bold", color=TEXT_MUTED)
    ax.text(16, 52.5, "Rs 3,870", fontsize=15, fontweight="bold", color=TEXT_DARK)
    ax.text(16, 46, "Invested: Rs 4,000  |  P&L: -Rs 130 (-3.2%)", fontsize=7.2, fontweight="bold", color=RED_ACCENT)
    ax.text(16, 42, "1-Yr XIRR: -28.4% (Distorted by small tenure)", fontsize=6.5, color=TEXT_LIGHT)

    # THE CONTEXTUAL ENTRY BANNER (Intervention Bridge)
    ax.add_patch(FancyBboxPatch((13, 20), 54, 18, boxstyle="round,pad=1,rounding_size=3",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_DARK_GREEN, lw=1.2))
    ax.text(16, 33, "Market Dip Advantage Active!", fontsize=8.5, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(16, 28, "Your Rs 1,000 monthly SIP just secured extra\nmutual fund units at discounted prices.", fontsize=7.2, color=TEXT_DARK, linespacing=1.3)
    ax.text(16, 22.5, "View Accumulation Impact  ->", fontsize=7.8, fontweight="bold", color=GROWW_DARK_GREEN)

    # Screen 1 Bottom Nav
    ax.add_patch(FancyBboxPatch((13, 10), 54, 7, boxstyle="round,pad=0.5,rounding_size=2",
                                facecolor="#F1F5F9", edgecolor="none"))
    ax.text(40, 13.5, "Stocks  |  Mutual Funds  |  Pay", fontsize=7.5, color=TEXT_MUTED, ha="center")

    # SCREEN 2 (RIGHT): The Accumulation Lens (Behavioral Reframing)
    draw_phone_bezel(ax, 90, 8, 60, 76, "Accumulation Lens", "SCREEN 2: RESOLUTION")

    # Screen 2 Content
    # Year 1 Mode Badge
    ax.add_patch(FancyBboxPatch((93, 68), 54, 6.5, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_GREEN, lw=0.8))
    ax.text(96, 71.2, "Year 1 Focus: Unit Wealth Engine", fontsize=8, fontweight="bold", color=GROWW_DARK_GREEN)

    # Hero Unit Acquisition Card
    ax.add_patch(FancyBboxPatch((93, 35), 54, 31, boxstyle="round,pad=1.2,rounding_size=3",
                                facecolor=CARD_BG, edgecolor=CARD_BORDER, lw=1))
    ax.text(96, 61, "THIS MONTH'S INSTALMENT", fontsize=7, fontweight="bold", color=TEXT_MUTED)
    ax.text(96, 53.5, "44.2 Units Secured", fontsize=15, fontweight="bold", color=TEXT_DARK)
    
    # Bonus Units Tag
    ax.add_patch(FancyBboxPatch((96, 45.5), 44, 5, boxstyle="round,pad=0.6,rounding_size=1.5",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_DARK_GREEN, lw=0.8))
    ax.text(98, 48, "+4.2 Bonus Units (7.8% Discount)", fontsize=7.2, fontweight="bold", color=GROWW_DARK_GREEN)

    ax.text(96, 40, "Purchase NAV: Rs 22.60 (Last Mo: Rs 25.10)", fontsize=7.2, color=TEXT_MUTED)
    ax.text(96, 36.5, "Total Units in Vault: 172.8 Units", fontsize=7.2, fontweight="bold", color=TEXT_DARK)

    # Educational Reassurance
    ax.add_patch(FancyBboxPatch((93, 20), 54, 13, boxstyle="round,pad=1,rounding_size=2",
                                facecolor="#F8FAFC", edgecolor=CARD_BORDER, lw=0.8))
    ax.text(96, 28.5, "Why This Matters for 12-Month Retention:", fontsize=7.2, fontweight="bold", color=TEXT_DARK)
    ax.text(96, 23.5, "You purchased more inventory on sale. In 10-year\nhorizons, units bought in dips drive 60% of total alpha.", fontsize=6.8, color=TEXT_MUTED, linespacing=1.25)

    # Action Button
    ax.add_patch(FancyBboxPatch((93, 10.5), 54, 7.5, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor=GROWW_GREEN, edgecolor="none"))
    ax.text(117, 14.2, "Keep Accumulating on Auto-Pilot", fontsize=8.2, fontweight="bold", color=TEXT_WHITE, ha="center")

    save_flow_screen(fig, "flow_solution_1_accumulation_lens.png")


# ==============================================================================
# FLOW 2: MILESTONE HORIZON SHIELD FLOW
# ==============================================================================
def create_flow_2():
    fig, ax = setup_flow_canvas(
        "Solution 2: Milestone Horizon Shield Flow",
        "Screen 1 (Fund Performance & Hesitation)  ──▶  Screen 2 (10-Year Horizon Trajectory Cone)"
    )
    ax.text(80, 52, "User taps 'Check\nGoal Health'", fontsize=9, fontweight="bold", color="#A855F7", ha="center")

    # SCREEN 1: Fund Details with Drawdown Anxiety
    draw_phone_bezel(ax, 10, 8, 60, 76, "Parag Parikh Flexi Cap", "SCREEN 1: THE HESITATION")

    # Fund Details Card
    ax.add_patch(FancyBboxPatch((13, 56), 54, 19, boxstyle="round,pad=1,rounding_size=2.5",
                                facecolor=CARD_BG, edgecolor=CARD_BORDER, lw=1))
    ax.text(16, 70, "MONTHLY SIP: RS 1,000", fontsize=7, fontweight="bold", color=TEXT_MUTED)
    ax.text(16, 64, "1-Month Return: -4.1%", fontsize=13, fontweight="bold", color=RED_ACCENT)
    ax.text(16, 58.5, "Short-term equity correction across large & midcaps", fontsize=6.8, color=TEXT_LIGHT)

    # Doubt / Anxiety Prompt
    ax.add_patch(FancyBboxPatch((13, 44), 54, 10, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor=RED_BG, edgecolor="#FCA5A5", lw=0.8))
    ax.text(16, 50.5, "Anxious about this month's negative return?", fontsize=7.2, fontweight="bold", color=RED_ACCENT)
    ax.text(16, 46.5, "Novice instinct: 'Should I pause or stop my SIP?'", fontsize=6.8, color=TEXT_MUTED)

    # LINKED GOAL CARD (The Anchor)
    ax.add_patch(FancyBboxPatch((13, 20), 54, 21, boxstyle="round,pad=1,rounding_size=2.5",
                                facecolor=PURPLE_BG, edgecolor=PURPLE_ACCENT, lw=1.2))
    ax.text(16, 36, "LINKED GOAL ANCHOR", fontsize=7.2, fontweight="bold", color=PURPLE_ACCENT)
    ax.text(16, 30.5, "Child Higher Education (2036)", fontsize=9.5, fontweight="bold", color=TEXT_DARK)
    ax.text(16, 25.5, "Target: Rs 15 Lakhs  |  Status: 100% ON TRACK", fontsize=7.2, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(16, 21.5, "Check 10-Year Horizon Trajectory  ->", fontsize=7.8, fontweight="bold", color=PURPLE_ACCENT)

    # SCREEN 2: The Horizon Trajectory Cone
    draw_phone_bezel(ax, 90, 8, 60, 76, "Horizon Shield", "SCREEN 2: TRAJECTORY CONE")

    # Milestone Header
    ax.add_patch(FancyBboxPatch((93, 67), 54, 8, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor=CARD_BG, edgecolor=CARD_BORDER, lw=1))
    ax.text(96, 71.5, "Goal: Child Education (Month 4 of 120)", fontsize=8.2, fontweight="bold", color=PURPLE_ACCENT)
    ax.text(96, 68.5, "10-Year Horizon (2026 - 2036)", fontsize=7, color=TEXT_MUTED)

    # Trajectory Cone Box
    ax.add_patch(FancyBboxPatch((93, 31), 54, 34, boxstyle="round,pad=1,rounding_size=2.5",
                                facecolor=CARD_BG, edgecolor=CARD_BORDER, lw=1))
    ax.text(96, 60.5, "10-Year Confidence Band vs Short-Term Dip", fontsize=7.2, fontweight="bold", color=TEXT_DARK)

    # Mini Cone Plot inside screen 2
    xs = np.linspace(96, 142, 30)
    top_y = 40 + (xs - 96) * 0.4
    bot_y = 40 + (xs - 96) * 0.15
    ax.fill_between(xs, bot_y, top_y, color="#F3E8FF", alpha=0.7)
    mid_y = 40 + (xs - 96) * 0.28
    ax.plot(xs, mid_y, color=PURPLE_ACCENT, lw=1.5, linestyle="--")
    # Current point
    ax.plot(100, 41.2, "o", color=RED_ACCENT, markersize=4)
    ax.text(102, 42.5, "You (Mo 4): Dip is <0.03% variance", fontsize=6.2, fontweight="bold", color=TEXT_DARK)

    # Reassurance Box
    ax.add_patch(FancyBboxPatch((93, 19), 54, 10.5, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_GREEN, lw=0.8))
    ax.text(96, 25.5, "Perspective: 94% of 10-Yr SIPs beat inflation", fontsize=7.2, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(96, 21.5, "Short-term noise has zero statistical impact on 2036.", fontsize=6.8, color=TEXT_MUTED)

    # Action CTA
    ax.add_patch(FancyBboxPatch((93, 10.5), 54, 7, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor=PURPLE_ACCENT, edgecolor="none"))
    ax.text(117, 14, "Reaffirm 10-Year Plan & Stay Active", fontsize=8.2, fontweight="bold", color=TEXT_WHITE, ha="center")

    save_flow_screen(fig, "flow_solution_2_milestone_horizon_shield.png")


# ==============================================================================
# FLOW 3: MARKET CYCLE TIME MACHINE FLOW
# ==============================================================================
def create_flow_3():
    fig, ax = setup_flow_canvas(
        "Solution 3: Market Cycle Time Machine Flow",
        "Screen 1 (Crisis In-App Discovery)  ──▶  Screen 2 (Historical Panic vs Discipline Simulation)"
    )
    ax.text(80, 52, "User selects '2020\nCrash Simulation'", fontsize=9, fontweight="bold", color="#F59E0B", ha="center")

    # SCREEN 1: Discovery Prompt during Market Crash
    draw_phone_bezel(ax, 10, 8, 60, 76, "Groww Insights", "SCREEN 1: THE SIMULATOR ENTRY")

    # Notification / Banner Prompt
    ax.add_patch(FancyBboxPatch((13, 62), 54, 13, boxstyle="round,pad=1,rounding_size=2.5",
                                facecolor=AMBER_BG, edgecolor="#FCD34D", lw=1))
    ax.text(16, 70.5, "Feeling Uneasy About Market Red Days?", fontsize=8, fontweight="bold", color="#B45309")
    ax.text(16, 65, "First-time investors often ask: 'Has this happened before?'\nSee real historical outcomes from past crashes.", fontsize=6.8, color="#92400E", linespacing=1.25)

    # Crisis Selector Cards
    ax.add_patch(FancyBboxPatch((13, 44), 54, 15, boxstyle="round,pad=1,rounding_size=2",
                                facecolor=CARD_BG, edgecolor=BORDER_CANVAS, lw=1))
    ax.text(16, 54, "Select an Indian Market Crisis:", fontsize=7.2, fontweight="bold", color=TEXT_MUTED)
    
    # 2020 Pill
    ax.add_patch(FancyBboxPatch((16, 46.5), 23, 5.5, boxstyle="round,pad=0.5,rounding_size=1.5",
                                facecolor=TEXT_DARK, edgecolor="none"))
    ax.text(27.5, 49.2, "2020 COVID (-38%)", fontsize=6.5, fontweight="bold", color=TEXT_WHITE, ha="center")

    # 2022 Pill
    ax.add_patch(FancyBboxPatch((41, 46.5), 23, 5.5, boxstyle="round,pad=0.5,rounding_size=1.5",
                                facecolor="#E2E8F0", edgecolor="none"))
    ax.text(52.5, 49.2, "2022 Rate Hikes", fontsize=6.5, color=TEXT_MUTED, ha="center")

    # Educational Teaser
    ax.add_patch(FancyBboxPatch((13, 20), 54, 21, boxstyle="round,pad=1,rounding_size=2",
                                facecolor=CARD_BG, edgecolor=CARD_BORDER, lw=0.8))
    ax.text(16, 36.5, "The Question We Answer:", fontsize=7.5, fontweight="bold", color=TEXT_DARK)
    ax.text(16, 31, "What happened to people who started a Rs 1,000 SIP\nright before the crash and stayed vs those who stopped?", fontsize=6.8, color=TEXT_MUTED, linespacing=1.3)
    ax.text(16, 23, "Run 3-Year Historical Simulation  ->", fontsize=7.5, fontweight="bold", color=BLUE_ACCENT)

    # SCREEN 2: Side-by-Side Outcome Simulation
    draw_phone_bezel(ax, 90, 8, 60, 76, "Cycle Simulation", "SCREEN 2: SIMULATION RESULTS")

    # Header Results
    ax.text(93, 72, "2020 Crash: 3-Year Outcome Comparison", fontsize=8.2, fontweight="bold", color=TEXT_DARK)

    # Investor A: Stopped SIP in Panic
    ax.add_patch(FancyBboxPatch((93, 49), 54, 20, boxstyle="round,pad=1,rounding_size=2",
                                facecolor=RED_BG, edgecolor="#FCA5A5", lw=0.8))
    ax.text(96, 64.5, "Investor A (Panicked & Stopped at Month 3)", fontsize=7.5, fontweight="bold", color=RED_ACCENT)
    ax.text(96, 59.5, "- Total Capital Invested: Rs 3,000", fontsize=7, color=TEXT_DARK)
    ax.text(96, 55, "- Units Accumulated: 120 Units", fontsize=7, color=TEXT_DARK)
    ax.text(96, 51, "- Result: Locked in paper loss, missed 110% bull run", fontsize=6.8, color=RED_ACCENT)

    # Investor B: Stayed Disciplined
    ax.add_patch(FancyBboxPatch((93, 26), 54, 21, boxstyle="round,pad=1,rounding_size=2",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_DARK_GREEN, lw=0.8))
    ax.text(96, 42.5, "Investor B (Maintained SIP Through Crash)", fontsize=7.5, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(96, 37.5, "- Total Capital Invested: Rs 36,000 over 3 Yrs", fontsize=7, color=TEXT_DARK)
    ax.text(96, 33, "- Units Accumulated: 412 Units (+243% more!)", fontsize=7, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(96, 28.5, "- Result: Rs 68,500 portfolio value (+22.4% CAGR)", fontsize=6.8, fontweight="bold", color=GROWW_DARK_GREEN)

    # CTA Button
    ax.add_patch(FancyBboxPatch((93, 10.5), 54, 7.5, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor=TEXT_DARK, edgecolor="none"))
    ax.text(117, 14.2, "I'll Stay Disciplined • Keep SIP Active", fontsize=8, fontweight="bold", color=TEXT_WHITE, ha="center")

    save_flow_screen(fig, "flow_solution_3_market_cycle_time_machine.png")


# ==============================================================================
# FLOW 4: SMART VOLATILITY BUFFER & FLEXIBLE PAUSE FLOW
# ==============================================================================
def create_flow_4():
    fig, ax = setup_flow_canvas(
        "Solution 4: Smart Volatility Buffer & Flexible Pause Flow",
        "Screen 1 (Churn Intent Interception)  ──▶  Screen 2 (3-Way Flexible Zero-Penalty Protection)"
    )
    ax.text(80, 52, "User selects\n'Flexible Options'", fontsize=9, fontweight="bold", color="#3B82F6", ha="center")

    # SCREEN 1: User tries to Cancel SIP (The Danger Zone)
    draw_phone_bezel(ax, 10, 8, 60, 76, "Manage SIP", "SCREEN 1: CHURN INTENT")

    # Fund Card
    ax.add_patch(FancyBboxPatch((13, 58), 54, 17, boxstyle="round,pad=1,rounding_size=2",
                                facecolor=CARD_BG, edgecolor=CARD_BORDER, lw=1))
    ax.text(16, 70.5, "Nippon India Small Cap Fund", fontsize=8.5, fontweight="bold", color=TEXT_DARK)
    ax.text(16, 65.5, "Monthly SIP: Rs 1,000  |  Debit Date: 2nd of month", fontsize=7, color=TEXT_MUTED)
    ax.text(16, 60.5, "Status: Active AutoPay Mandate", fontsize=7, color=GROWW_DARK_GREEN)

    # Cancel SIP Dialog Trigger
    ax.add_patch(FancyBboxPatch((13, 24), 54, 30, boxstyle="round,pad=1,rounding_size=2.5",
                                facecolor=BLUE_BG, edgecolor=BLUE_ACCENT, lw=1.2))
    ax.text(16, 49, "Thinking of Stopping Your SIP?", fontsize=8.5, fontweight="bold", color=BLUE_ACCENT)
    ax.text(16, 43, "If you are facing market uncertainty or a temporary\nsalary delay, cancelling breaks your compounding pace\nand requires re-doing your bank mandate later.", fontsize=6.8, color=TEXT_DARK, linespacing=1.3)
    
    # Action link
    ax.add_patch(FancyBboxPatch((16, 27), 48, 7, boxstyle="round,pad=0.6,rounding_size=1.5",
                                facecolor=BLUE_ACCENT, edgecolor="none"))
    ax.text(40, 30.5, "Explore Smart Pause & Date Options  ->", fontsize=7.2, fontweight="bold", color=TEXT_WHITE, ha="center")

    # SCREEN 2: 3-Way Flexible Controls (The Churn Shield)
    draw_phone_bezel(ax, 90, 8, 60, 76, "Flexibility Controls", "SCREEN 2: SMART PAUSE")

    ax.text(93, 72, "Select a Low-Stress Alternative:", fontsize=8, fontweight="bold", color=TEXT_DARK)

    # Option 1: 30-Day Zero Penalty Pause (Selected)
    ax.add_patch(FancyBboxPatch((93, 49), 54, 20, boxstyle="round,pad=1,rounding_size=2",
                                facecolor=CARD_BG, edgecolor=GROWW_GREEN, lw=1.5))
    ax.text(96, 64.5, "[SELECTED] Option 1: 30-Day Grace Skip", fontsize=7.5, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(96, 59.5, "- Skips next month's debit with 1-click", fontsize=7, color=TEXT_DARK)
    ax.text(96, 55, "- Rs 0 bank bounce fee (Protects against NACH penalty)", fontsize=6.8, fontweight="bold", color=TEXT_DARK)
    ax.text(96, 51, "- Existing units keep growing; resumes automatically", fontsize=6.8, color=TEXT_MUTED)

    # Option 2: Shift Date
    ax.add_patch(FancyBboxPatch((93, 33), 54, 14, boxstyle="round,pad=1,rounding_size=2",
                                facecolor=CARD_BG, edgecolor=CARD_BORDER, lw=0.8))
    ax.text(96, 42.5, "Option 2: Shift Debit to Salary Day (7th)", fontsize=7.2, fontweight="bold", color=TEXT_DARK)
    ax.text(96, 37.5, "Avoids month-end cash crunch by aligning with pay check.", fontsize=6.6, color=TEXT_MUTED)

    # Option 3: Micro SIP
    ax.add_patch(FancyBboxPatch((93, 20), 54, 11, boxstyle="round,pad=1,rounding_size=2",
                                facecolor=CARD_BG, edgecolor=CARD_BORDER, lw=0.8))
    ax.text(96, 27, "Option 3: Halve to Rs 500 for 2 Months", fontsize=7.2, fontweight="bold", color=TEXT_DARK)
    ax.text(96, 23, "Eases immediate wallet pressure without stopping.", fontsize=6.6, color=TEXT_MUTED)

    # Primary Action
    ax.add_patch(FancyBboxPatch((93, 10.5), 54, 7.5, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor=GROWW_GREEN, edgecolor="none"))
    ax.text(117, 14.2, "Confirm 30-Day Zero Penalty Pause", fontsize=8.2, fontweight="bold", color=TEXT_WHITE, ha="center")

    save_flow_screen(fig, "flow_solution_4_smart_volatility_buffer_pause.png")


# ==============================================================================
# FLOW 5: CONTEXTUAL MOVEMENT ATTRIBUTOR FLOW
# ==============================================================================
def create_flow_5():
    fig, ax = setup_flow_canvas(
        "Solution 5: Contextual Movement Attributor Flow",
        "Screen 1 (Daily Drop Notification / Card)  ──▶  Screen 2 (Plain-Language Factor Attribution)"
    )
    ax.text(80, 52, "User taps 'Why Did\nMy Fund Drop?'", fontsize=9, fontweight="bold", color="#0284C7", ha="center")

    # SCREEN 1: Daily Movement Alert on Portfolio
    draw_phone_bezel(ax, 10, 8, 60, 76, "Daily Portfolio", "SCREEN 1: THE SHOCK MOMENT")

    # Today's Movement Card
    ax.add_patch(FancyBboxPatch((13, 56), 54, 19, boxstyle="round,pad=1,rounding_size=2.5",
                                facecolor=RED_BG, edgecolor="#FCA5A5", lw=0.8))
    ax.text(16, 70.5, "TODAY'S PORTFOLIO DELTA", fontsize=7, fontweight="bold", color=RED_ACCENT)
    ax.text(16, 64, "-1.8% (-Rs 72 on Rs 4,000)", fontsize=13, fontweight="bold", color=TEXT_DARK)
    ax.text(16, 58.5, "Market Volatility Alert | Oct 24, 2026", fontsize=6.8, color=TEXT_MUTED)

    # Explanation Teaser Card
    ax.add_patch(FancyBboxPatch((13, 26), 54, 26, boxstyle="round,pad=1,rounding_size=2.5",
                                facecolor=CARD_BG, edgecolor=CARD_BORDER, lw=1))
    ax.text(16, 47, "Why did your funds drop today?", fontsize=8.5, fontweight="bold", color=TEXT_DARK)
    ax.text(16, 41, "Don't guess what happened. We broke down today's\nmovement into broader market, sector, and fund manager\nactions in plain English.", fontsize=6.8, color=TEXT_MUTED, linespacing=1.3)
    
    # Tap link
    ax.add_patch(FancyBboxPatch((16, 29), 48, 6.5, boxstyle="round,pad=0.5,rounding_size=1.5",
                                facecolor="#F0F9FF", edgecolor="#BAE6FD", lw=0.8))
    ax.text(40, 32.2, "See Plain-Language Attribution  ->", fontsize=7.2, fontweight="bold", color="#0284C7", ha="center")

    # SCREEN 2: Deconstructed Factor Attribution
    draw_phone_bezel(ax, 90, 8, 60, 76, "Movement Context", "SCREEN 2: PLAIN-LANGUAGE ATTRIBUTION")

    ax.text(93, 72, "What Drove Today's -1.8% Movement?", fontsize=8, fontweight="bold", color=TEXT_DARK)

    # Factor 1: Macro
    ax.add_patch(FancyBboxPatch((93, 57), 54, 12, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor="#F8FAFC", edgecolor=CARD_BORDER, lw=0.8))
    ax.text(96, 64.5, "[Macro] Broader Market Sentiment (60% impact)", fontsize=7, fontweight="bold", color=TEXT_DARK)
    ax.text(96, 60, "Nifty 50 slipped 1.4% following US Fed rate remarks.", fontsize=6.5, color=TEXT_MUTED)

    # Factor 2: Sector
    ax.add_patch(FancyBboxPatch((93, 42), 54, 12, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor="#F8FAFC", edgecolor=CARD_BORDER, lw=0.8))
    ax.text(96, 49.5, "[Sector] Banking & IT Correction (30% impact)", fontsize=7, fontweight="bold", color=TEXT_DARK)
    ax.text(96, 45, "Quarterly earnings prompted institutional profit-taking.", fontsize=6.5, color=TEXT_MUTED)

    # Factor 3: Fund Cushion
    ax.add_patch(FancyBboxPatch((93, 27), 54, 12, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_GREEN, lw=0.8))
    ax.text(96, 34.5, "[Defense] Fund Manager Cushion (+10% cushion)", fontsize=7, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(96, 30, "Your fund held 14% cash reserves, softening the drop.", fontsize=6.5, color=TEXT_MUTED)

    # Action CTA
    ax.add_patch(FancyBboxPatch((93, 10.5), 54, 7.5, boxstyle="round,pad=0.8,rounding_size=2",
                                facecolor=TEXT_DARK, edgecolor="none"))
    ax.text(117, 14.2, "I Understand • Keep My Plan Active", fontsize=8, fontweight="bold", color=TEXT_WHITE, ha="center")

    save_flow_screen(fig, "flow_solution_5_contextual_movement_attributor.png")


if __name__ == "__main__":
    print("Generating 5 Two-Screen User Flow Mockups...")
    create_flow_1()
    create_flow_2()
    create_flow_3()
    create_flow_4()
    create_flow_5()
    print("All 5 Flow Mockups generated successfully!")
