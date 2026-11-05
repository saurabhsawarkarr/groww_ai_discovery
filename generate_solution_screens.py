"""Generator for the 5 Market Fluctuation Solution UI Screen Mockups.
Renders high-resolution, modern mobile app screens for Groww.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon
import numpy as np

OUTPUT_DIRS = [
    Path("deliverables/screens"),
    Path("C:/Users/KAUSTUBH/.gemini/antigravity/brain/708df285-86a7-405f-be3f-5a6d8dc3d597/screens")
]

# Color Palette
BG_CANVAS = "#F4F6F8"
CARD_BG = "#FFFFFF"
BORDER_COLOR = "#E2E8F0"
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#64748B"
TEXT_LIGHT = "#94A3B8"
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


def setup_phone_frame(title="Groww", subtitle=""):
    """Creates a 9:18.5 aspect ratio mobile screen canvas with status bar & navigation."""
    fig, ax = plt.subplots(figsize=(6, 12.3), dpi=150)
    fig.patch.set_facecolor(BG_CANVAS)
    ax.set_facecolor(BG_CANVAS)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 205)
    ax.axis("off")

    # Status Bar (Top)
    ax.text(8, 199, "9:41", fontsize=10, fontweight="bold", color=TEXT_DARK, va="center")
    # Wifi & Battery mock
    ax.add_patch(Rectangle((83, 197.5), 7, 3, facecolor="none", edgecolor=TEXT_DARK, lw=1))
    ax.add_patch(Rectangle((84, 198.5), 4, 1.5, facecolor=TEXT_DARK))
    ax.add_patch(Circle((78, 199), 1.2, facecolor=TEXT_DARK))

    # Top App Bar
    ax.text(8, 190, "←", fontsize=16, color=TEXT_DARK, va="center")
    ax.text(16, 190.5, title, fontsize=13, fontweight="bold", color=TEXT_DARK, va="center")
    if subtitle:
        ax.text(16, 186.5, subtitle, fontsize=9, color=TEXT_MUTED, va="center")

    # Profile / Help Icon
    ax.add_patch(Circle((90, 190), 3.5, facecolor="#E2E8F0"))
    ax.text(90, 190, "?", fontsize=10, fontweight="bold", color=TEXT_DARK, ha="center", va="center")

    return fig, ax


def save_screen(fig, filename):
    for d in OUTPUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        path = d / filename
        fig.savefig(path, bbox_inches="tight", dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Saved: {filename}")


# ==============================================================================
# SCREEN 1: ACCUMULATION LENS
# ==============================================================================
def create_screen_1():
    fig, ax = setup_phone_frame("Portfolio", "First-Year Accumulator View")

    # Mode Tag Banner
    ax.add_patch(FancyBboxPatch((8, 172), 84, 9, boxstyle="round,pad=1.5,rounding_size=3",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_GREEN, lw=1))
    ax.text(12, 176.5, "[Active] Year 1 Mode: Accumulation Lens", fontsize=9.5, fontweight="bold", color=GROWW_DARK_GREEN, va="center")
    ax.text(88, 176.5, "Info (i)", fontsize=8.5, color=GROWW_DARK_GREEN, ha="right", va="center")

    # Primary Hero Card: Units Bought at Discount
    ax.add_patch(FancyBboxPatch((8, 114), 84, 52, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1))
    
    ax.text(12, 160, "THIS MONTH'S INSTALMENT", fontsize=8.5, fontweight="bold", color=TEXT_MUTED)
    ax.text(12, 150, "42.8 Units Secured", fontsize=18, fontweight="bold", color=TEXT_DARK)
    
    # Bonus Tag Pill
    ax.add_patch(FancyBboxPatch((12, 137), 62, 7, boxstyle="round,pad=1,rounding_size=2",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_DARK_GREEN, lw=0.8))
    ax.text(15, 140.5, "+3.8 Bonus Units (Market Dip Advantage)", fontsize=8, fontweight="bold", color=GROWW_DARK_GREEN, va="center")

    # Metric Comparison
    ax.text(12, 128, "Purchase NAV:", fontsize=9, color=TEXT_MUTED)
    ax.text(40, 128, "Rs 23.36", fontsize=10, fontweight="bold", color=TEXT_DARK)
    ax.text(62, 128, "(Last month: Rs 25.12)", fontsize=8.5, color=TEXT_LIGHT)
    
    ax.text(12, 120, "Unit Discount:", fontsize=9, color=TEXT_MUTED)
    ax.text(40, 120, "7.0% Lower Cost", fontsize=10, fontweight="bold", color=GROWW_DARK_GREEN)

    # Explanation Insight Card
    ax.add_patch(FancyBboxPatch((8, 70), 84, 38, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1))
    ax.text(12, 102, "How Rupee-Cost Averaging Protects You", fontsize=10, fontweight="bold", color=TEXT_DARK)
    
    body_text = (
        "When market volatility pushes prices down, your fixed\n"
        "Rs 1,000 monthly SIP acts like a discount coupon -- accumulating\n"
        "more fund units. When markets recover, these bonus units\n"
        "compound significantly faster."
    )
    ax.text(12, 86, body_text, fontsize=8.5, color=TEXT_MUTED, va="center", linespacing=1.4)

    # Transparency Paper P&L Toggle Card
    ax.add_patch(FancyBboxPatch((8, 38), 84, 26, boxstyle="round,pad=2,rounding_size=4",
                                facecolor="#F8FAFC", edgecolor=BORDER_COLOR, lw=1))
    ax.text(12, 57, "TRANSPARENCY AUDIT", fontsize=8, fontweight="bold", color=TEXT_MUTED)
    ax.text(12, 48, "Paper Value Today: Rs 3,955", fontsize=11, fontweight="bold", color=TEXT_DARK)
    ax.text(12, 42, "Invested: Rs 4,000 | Short-term paper delta: -Rs 45 (-1.1%)", fontsize=8, color=RED_ACCENT)

    # Bottom Primary Button
    ax.add_patch(FancyBboxPatch((8, 14), 84, 15, boxstyle="round,pad=1.5,rounding_size=3",
                                facecolor=GROWW_GREEN, edgecolor="none"))
    ax.text(50, 21.5, "Continue SIP with Accumulation Shield", fontsize=10, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    # SEBI Compliance Note
    ax.text(50, 6, "SEBI: Mutual fund investments are subject to market risks.", fontsize=7, color=TEXT_LIGHT, ha="center")

    save_screen(fig, "solution_1_accumulation_lens.png")


# ==============================================================================
# SCREEN 2: MILESTONE HORIZON SHIELD
# ==============================================================================
def create_screen_2():
    fig, ax = setup_phone_frame("Goal Tracking", "Milestone Horizon Shield")

    # Milestone Header Card
    ax.add_patch(FancyBboxPatch((8, 160), 84, 22, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1))
    ax.text(12, 175, "[TARGET MILESTONE]", fontsize=8.5, fontweight="bold", color=PURPLE_ACCENT)
    ax.text(12, 166, "Higher Education Fund (2036)", fontsize=13, fontweight="bold", color=TEXT_DARK)
    ax.text(88, 166, "10-Yr Plan", fontsize=8.5, color=TEXT_MUTED, ha="right")

    # Trajectory Cone Visualization Card
    ax.add_patch(FancyBboxPatch((8, 86), 84, 68, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1))
    ax.text(12, 148, "Long-Term Trajectory vs Current Noise", fontsize=10, fontweight="bold", color=TEXT_DARK)
    
    # Draw Trajectory Cone Graph
    years = np.linspace(15, 85, 50)
    top_cone = 95 + (years - 15) * 0.55
    bottom_cone = 95 + (years - 15) * 0.25
    ax.fill_between(years, bottom_cone, top_cone, color="#F3E8FF", alpha=0.6, label="Expected Horizon Band")
    
    # Milestone Path
    mid_path = 95 + (years - 15) * 0.4
    ax.plot(years, mid_path, color=PURPLE_ACCENT, lw=2, linestyle="--")
    
    # Current Position (Small Dip inside the Cone)
    ax.plot([15, 18, 22], [95, 96.5, 96.0], color=TEXT_DARK, lw=2.5)
    ax.plot(22, 96.0, "o", color=RED_ACCENT, markersize=6)
    
    # Annotations
    ax.annotate("You are here (Month 4)\nShort-term dip is inside green band",
                xy=(22, 96.0), xytext=(28, 110),
                arrowprops=dict(arrowstyle="->", color=TEXT_DARK, lw=1),
                fontsize=7.5, fontweight="bold", color=TEXT_DARK)

    # Health Callout
    ax.add_patch(FancyBboxPatch((8, 48), 84, 32, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_DARK_GREEN, lw=1))
    ax.text(12, 73, "[Shield] Goal Health Status: 100% On Track", fontsize=10, fontweight="bold", color=GROWW_DARK_GREEN)
    reassurance = (
        "This week's 2.8% market dip affects less than 0.03% of your\n"
        "10-year goal target (Rs 15 Lakhs). Investors who stay invested\n"
        "through early cycles achieve their targets 94% of the time."
    )
    ax.text(12, 60, reassurance, fontsize=8.2, color=GROWW_DARK_GREEN, linespacing=1.4)

    # Bottom Action
    ax.add_patch(FancyBboxPatch((8, 16), 84, 15, boxstyle="round,pad=1.5,rounding_size=3",
                                facecolor=PURPLE_ACCENT, edgecolor="none"))
    ax.text(50, 23.5, "Lock In Goal Commitment (Auto-Protect)", fontsize=10, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    ax.text(50, 8, "Simulations based on historical category distributions. No guaranteed returns.", fontsize=7, color=TEXT_LIGHT, ha="center")

    save_screen(fig, "solution_2_milestone_horizon_shield.png")


# ==============================================================================
# SCREEN 3: MARKET CYCLE TIME MACHINE
# ==============================================================================
def create_screen_3():
    fig, ax = setup_phone_frame("Groww Insights", "Cycle Simulator")

    # Header Question
    ax.text(8, 178, "What happened to investors who\nstarted during past market crashes?",
            fontsize=12, fontweight="bold", color=TEXT_DARK, linespacing=1.3)

    # Crash Tabs
    ax.add_patch(FancyBboxPatch((8, 158), 40, 8, boxstyle="round,pad=1,rounding_size=2",
                                facecolor=TEXT_DARK, edgecolor="none"))
    ax.text(28, 162, "2020 COVID Crash", fontsize=8.5, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    ax.add_patch(FancyBboxPatch((52, 158), 40, 8, boxstyle="round,pad=1,rounding_size=2",
                                facecolor="#E2E8F0", edgecolor="none"))
    ax.text(72, 162, "2022 Rate Hikes", fontsize=8.5, color=TEXT_MUTED, ha="center", va="center")

    # Comparative Results Card
    ax.add_patch(FancyBboxPatch((8, 76), 84, 76, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1))
    ax.text(12, 144, "3-Year Outcome Comparison (Rs 1,000/mo SIP)", fontsize=9.5, fontweight="bold", color=TEXT_DARK)

    # Investor A (Stopped in Panic)
    ax.add_patch(FancyBboxPatch((12, 112), 76, 26, boxstyle="round,pad=1,rounding_size=3",
                                facecolor=RED_BG, edgecolor="#FCA5A5", lw=0.8))
    ax.text(16, 131, "[X] Investor A (Panicked & Stopped at Mo 3)", fontsize=8.5, fontweight="bold", color=RED_ACCENT)
    ax.text(16, 123, "- Total Invested: Rs 3,000 (Cut short)", fontsize=8, color=TEXT_DARK)
    ax.text(16, 116, "- Units Accumulated: 120 Units (Missed dip)", fontsize=8, color=TEXT_DARK)

    # Investor B (Stayed Disciplined)
    ax.add_patch(FancyBboxPatch((12, 80), 76, 28, boxstyle="round,pad=1,rounding_size=3",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_GREEN, lw=0.8))
    ax.text(16, 101, "[OK] Investor B (Maintained SIP Through Crash)", fontsize=8.5, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(16, 93, "- Total Invested: Rs 36,000 over 3 Years", fontsize=8, color=TEXT_DARK)
    ax.text(16, 85, "- Units Accumulated: 412 Units (+243% more!)", fontsize=8, fontweight="bold", color=GROWW_DARK_GREEN)

    # Bottom Reassurance Takeaway
    ax.add_patch(FancyBboxPatch((8, 40), 84, 30, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=AMBER_BG, edgecolor="#FCD34D", lw=1))
    ax.text(12, 63, "[Insight] The Historical Pattern", fontsize=9.5, fontweight="bold", color="#B45309")
    truth = (
        "Market pullbacks feel terrifying in real-time, but every single\n"
        "drawdown in Indian mutual fund history rewarded investors\n"
        "who kept their SIP active during the red months."
    )
    ax.text(12, 51, truth, fontsize=8.2, color="#92400E", linespacing=1.35)

    # Primary Action
    ax.add_patch(FancyBboxPatch((8, 14), 84, 15, boxstyle="round,pad=1.5,rounding_size=3",
                                facecolor=TEXT_DARK, edgecolor="none"))
    ax.text(50, 21.5, "Save Simulator & Stay On Course", fontsize=10, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    save_screen(fig, "solution_3_market_cycle_time_machine.png")


# ==============================================================================
# SCREEN 4: SMART VOLATILITY BUFFER & FLEXIBLE SIP PAUSE
# ==============================================================================
def create_screen_4():
    fig, ax = setup_phone_frame("Manage SIP", "Flexibility Controls")

    # Header Trigger
    ax.add_patch(FancyBboxPatch((8, 160), 84, 22, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=BLUE_BG, edgecolor=BLUE_ACCENT, lw=0.8))
    ax.text(12, 175, "Nervous About Volatility or Cash Flow?", fontsize=10.5, fontweight="bold", color=BLUE_ACCENT)
    ax.text(12, 166, "Don't cancel your compounding. Choose a smart pause.", fontsize=8.5, color=TEXT_MUTED)

    # Option 1: 30-Day Zero Penalty Pause
    ax.add_patch(FancyBboxPatch((8, 116), 84, 38, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=CARD_BG, edgecolor=GROWW_GREEN, lw=1.5))
    ax.text(12, 146, "[Active] OPTION 1: 30-Day Grace Pause", fontsize=10, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(12, 137, "- Skip next month's debit with 1-click", fontsize=8.5, color=TEXT_DARK)
    ax.text(12, 129, "- Zero bank bounce fees (Rs 0 NACH penalty)", fontsize=8.5, fontweight="bold", color=TEXT_DARK)
    ax.text(12, 121, "- Existing units continue compounding", fontsize=8.5, color=TEXT_MUTED)
    ax.text(88, 146, "[SELECTED]", fontsize=8, fontweight="bold", color=GROWW_DARK_GREEN, ha="right")

    # Option 2: Align with Salary Date
    ax.add_patch(FancyBboxPatch((8, 72), 84, 38, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1))
    ax.text(12, 102, "[Option 2] Shift Debit Date to Salary Day", fontsize=10, fontweight="bold", color=TEXT_DARK)
    ax.text(12, 93, "- Current deduction date: 2nd of month", fontsize=8.5, color=TEXT_MUTED)
    ax.text(12, 85, "- Recommended date: 7th (After salary hits)", fontsize=8.5, color=TEXT_DARK)
    ax.text(12, 77, "- Prevents month-end balance crunches", fontsize=8.5, color=TEXT_MUTED)

    # Option 3: Halve Instalment
    ax.add_patch(FancyBboxPatch((8, 36), 84, 30, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1))
    ax.text(12, 59, "[Option 3] Temporary Micro-SIP (Rs 500)", fontsize=10, fontweight="bold", color=TEXT_DARK)
    ax.text(12, 50, "Reduce instalment to Rs 500 for 2 months to ease cash pressure.", fontsize=8, color=TEXT_MUTED)

    # Bottom Button
    ax.add_patch(FancyBboxPatch((8, 12), 84, 15, boxstyle="round,pad=1.5,rounding_size=3",
                                facecolor=GROWW_GREEN, edgecolor="none"))
    ax.text(50, 19.5, "Confirm 30-Day Zero Penalty Pause", fontsize=10, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    save_screen(fig, "solution_4_smart_volatility_buffer_pause.png")


# ==============================================================================
# SCREEN 5: CONTEXTUAL MOVEMENT ATTRIBUTOR
# ==============================================================================
def create_screen_5():
    fig, ax = setup_phone_frame("Portfolio Context", "Plain-Language Attributor")

    # Today's Movement Card
    ax.add_patch(FancyBboxPatch((8, 158), 84, 24, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=RED_BG, edgecolor="#FCA5A5", lw=0.8))
    ax.text(12, 175, "TODAY'S PORTFOLIO MOVEMENT", fontsize=8.5, fontweight="bold", color=RED_ACCENT)
    ax.text(12, 165, "-1.8% (-Rs 72.00 on Rs 4,000)", fontsize=14, fontweight="bold", color=TEXT_DARK)
    ax.text(88, 165, "Oct 24", fontsize=8.5, color=TEXT_MUTED, ha="right")

    # Attribution Breakdown Card
    ax.add_patch(FancyBboxPatch((8, 72), 84, 80, boxstyle="round,pad=2,rounding_size=4",
                                facecolor=CARD_BG, edgecolor=BORDER_COLOR, lw=1))
    ax.text(12, 144, "What Drove Today's Movement?", fontsize=10.5, fontweight="bold", color=TEXT_DARK)

    # Attribution 1: Macro
    ax.add_patch(FancyBboxPatch((12, 120), 76, 18, boxstyle="round,pad=1,rounding_size=2",
                                facecolor="#F8FAFC", edgecolor=BORDER_COLOR, lw=0.8))
    ax.text(16, 131, "[Macro] Broader Market Sentiment (60% impact)", fontsize=8.5, fontweight="bold", color=TEXT_DARK)
    ax.text(16, 124, "Nifty 50 slipped 1.4% following US Fed interest rate commentary.", fontsize=7.8, color=TEXT_MUTED)

    # Attribution 2: Sector
    ax.add_patch(FancyBboxPatch((12, 97), 76, 18, boxstyle="round,pad=1,rounding_size=2",
                                facecolor="#F8FAFC", edgecolor=BORDER_COLOR, lw=0.8))
    ax.text(16, 108, "[Sector] Banking & IT Sector Correction (30% impact)", fontsize=8.5, fontweight="bold", color=TEXT_DARK)
    ax.text(16, 101, "Major private bank quarterly results triggered sector profit taking.", fontsize=7.8, color=TEXT_MUTED)

    # Attribution 3: Fund Manager Defense
    ax.add_patch(FancyBboxPatch((12, 74), 76, 18, boxstyle="round,pad=1,rounding_size=2",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_GREEN, lw=0.8))
    ax.text(16, 85, "[Defense] Fund Manager Cushion (+10% cushion)", fontsize=8.5, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(16, 78, "Your flexi-cap fund held 14% cash reserves, softening the overall dip.", fontsize=7.8, color=TEXT_MUTED)

    # Bottom Clarification Card
    ax.add_patch(FancyBboxPatch((8, 38), 84, 28, boxstyle="round,pad=2,rounding_size=4",
                                facecolor="#F0F9FF", edgecolor="#BAE6FD", lw=1))
    ax.text(12, 58, "[Fact] Normal Market Dynamics", fontsize=9, fontweight="bold", color="#0369A1")
    clarity = (
        "Short-term drops of 1-3% happen roughly 25-30 times every\n"
        "year. They do not alter long-term economic earnings power."
    )
    ax.text(12, 47, clarity, fontsize=8.2, color="#0C4A6E", linespacing=1.35)

    # Primary Action
    ax.add_patch(FancyBboxPatch((8, 12), 84, 15, boxstyle="round,pad=1.5,rounding_size=3",
                                facecolor=TEXT_DARK, edgecolor="none"))
    ax.text(50, 19.5, "I Understand - Keep My Plan Active", fontsize=10, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    save_screen(fig, "solution_5_contextual_movement_attributor.png")


if __name__ == "__main__":
    print("Generating 5 Mobile UI Solution Screens...")
    create_screen_1()
    create_screen_2()
    create_screen_3()
    create_screen_4()
    create_screen_5()
    print("All 5 screens generated successfully!")
