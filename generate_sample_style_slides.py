"""Generates full presentation slide images matching the user's uploaded sample layout.
Creates 1920x1080 landscape slides with 5-phone user flows, header cards, step labels, and outcome bar.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon, Arc
import numpy as np

OUTPUT_DIRS = [
    Path("deliverables/screens"),
    Path("C:/Users/KAUSTUBH/.gemini/antigravity/brain/708df285-86a7-405f-be3f-5a6d8dc3d597/screens")
]

# Color Palette matching the sample image exactly
BG_SLIDE = "#F8FAFC"
HEADER_TEXT = "#0F172A"
SUBTITLE_TEXT = "#475569"
MUTED_TEXT = "#64748B"

PURPLE_BRAND = "#6366F1"       # Primary indigo/purple
PURPLE_LIGHT = "#EEF2FF"       # Soft purple container
PURPLE_BORDER = "#C7D2FE"
PURPLE_DARK = "#4338CA"

GROWW_GREEN = "#00D09C"        # Groww trademark green
GROWW_DARK_GREEN = "#008764"
GROWW_GREEN_BG = "#E6FBF5"

PHONE_CHASSIS = "#0F172A"      # Dark iPhone frame
PHONE_SCREEN = "#FFFFFF"       # Phone screen white
PHONE_CARD_BG = "#F8FAFC"
PHONE_BORDER = "#E2E8F0"

RED_ALERT = "#EF4444"
RED_BG = "#FEF2F2"
AMBER_ALERT = "#F59E0B"
AMBER_BG = "#FFFBEB"


def setup_slide_canvas():
    """Initializes 1920x1080 (16:9) slide canvas."""
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(BG_SLIDE)
    ax.set_facecolor(BG_SLIDE)
    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    ax.axis("off")
    return fig, ax


def draw_header(ax, solution_badge="Solution 1", title="Solution Title", subtitle="", focus_text=""):
    """Draws top header: Groww Logo | Badge | Title | Subtitle | Right Focus Card."""
    # Groww Logo circle
    ax.add_patch(Circle((70, 1010), 22, facecolor=GROWW_GREEN))
    # Inner white curve to resemble Groww logo
    ax.add_patch(Circle((70, 1010), 14, facecolor="#0284C7"))
    ax.add_patch(Circle((74, 1013), 9, facecolor=GROWW_GREEN))

    ax.text(105, 1010, "Groww", fontsize=22, fontweight="bold", color=HEADER_TEXT, va="center")

    # Solution Badge Pill
    ax.add_patch(FancyBboxPatch((215, 995), 130, 30, boxstyle="round,pad=1,rounding_size=8",
                                facecolor=PURPLE_LIGHT, edgecolor=PURPLE_BORDER, lw=1.2))
    ax.text(280, 1010, solution_badge, fontsize=13, fontweight="bold", color=PURPLE_DARK, ha="center", va="center")

    # Main Title
    ax.text(50, 955, title, fontsize=28, fontweight="bold", color=HEADER_TEXT, va="center")

    # Subtitle
    ax.text(50, 915, subtitle, fontsize=13.5, color=SUBTITLE_TEXT, va="center", linespacing=1.35)

    # Focus Box (Top Right)
    ax.add_patch(FancyBboxPatch((1200, 895), 670, 95, boxstyle="round,pad=2,rounding_size=12",
                                facecolor=PURPLE_LIGHT, edgecolor=PURPLE_BORDER, lw=1))
    # Target Icon circle
    ax.add_patch(Circle((1245, 942), 22, facecolor="#DDD6FE"))
    ax.text(1245, 942, "[Target]", fontsize=9, fontweight="bold", color=PURPLE_DARK, ha="center", va="center")
    
    # Focus Text
    ax.text(1285, 942, focus_text, fontsize=13, fontweight="bold", color=HEADER_TEXT, va="center", linespacing=1.35)


def draw_phone_frame(ax, x, y, width=320, height=520, screen_title="Groww"):
    """Draws a sleek realistic phone frame."""
    # Outer dark chassis
    ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=2,rounding_size=28",
                                facecolor=PHONE_CHASSIS, edgecolor="#334155", lw=2))
    # Inner screen
    screen_x = x + 7
    screen_y = y + 7
    screen_w = width - 14
    screen_h = height - 14
    ax.add_patch(FancyBboxPatch((screen_x, screen_y), screen_w, screen_h, boxstyle="round,pad=1,rounding_size=24",
                                facecolor=PHONE_SCREEN, edgecolor="none"))

    # Dynamic Island / Notch
    ax.add_patch(FancyBboxPatch((x + width/2 - 35, y + height - 24), 70, 12, boxstyle="round,pad=1,rounding_size=6",
                                facecolor=PHONE_CHASSIS, edgecolor="none"))

    # Status Bar: 9:41
    ax.text(screen_x + 22, screen_y + screen_h - 22, "9:41", fontsize=9.5, fontweight="bold", color=HEADER_TEXT, va="center")
    # Battery icon
    ax.add_patch(Rectangle((screen_x + screen_w - 42, screen_y + screen_h - 26), 20, 9, facecolor="none", edgecolor=HEADER_TEXT, lw=1))
    ax.add_patch(Rectangle((screen_x + screen_w - 40, screen_y + screen_h - 24), 14, 5, facecolor=HEADER_TEXT))

    # In-App App Bar
    ax.text(screen_x + 18, screen_y + screen_h - 52, "<-", fontsize=13, fontweight="bold", color=HEADER_TEXT, va="center")
    ax.text(screen_x + 48, screen_y + screen_h - 52, screen_title, fontsize=12, fontweight="bold", color=HEADER_TEXT, va="center")

    return screen_x, screen_y, screen_w, screen_h


def draw_chevron(ax, x, y):
    """Draws purple transition chevron '>' between phone frames."""
    ax.text(x, y, ">", fontsize=24, fontweight="bold", color="#A5B4FC", ha="center", va="center")


def draw_step_label(ax, x_center, y, step_num=1, step_title="Step Title", step_desc="Step description"):
    """Draws numbered purple circle and two-line description under each phone."""
    # Purple circle
    ax.add_patch(Circle((x_center - 100, y), 14, facecolor=PURPLE_BRAND))
    ax.text(x_center - 100, y, str(step_num), fontsize=12, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    # Step Title
    ax.text(x_center - 75, y + 4, step_title, fontsize=12.5, fontweight="bold", color=HEADER_TEXT, va="center")
    # Step Description
    ax.text(x_center - 75, y - 18, step_desc, fontsize=10, color=MUTED_TEXT, va="center", linespacing=1.25)


def draw_bottom_outcomes(ax, outcomes):
    """Draws the bottom green Outcome pill and 4 metric blocks."""
    bar_y = 65
    # Card container
    ax.add_patch(FancyBboxPatch((50, 25), 1820, 68, boxstyle="round,pad=2,rounding_size=12",
                                facecolor="#FFFFFF", edgecolor="#E2E8F0", lw=1))

    # Green Outcome Pill
    ax.add_patch(FancyBboxPatch((70, 40), 115, 38, boxstyle="round,pad=1,rounding_size=18",
                                facecolor=GROWW_GREEN, edgecolor="none"))
    ax.text(127, 59, "Outcome", fontsize=14, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    # 4 Outcome items
    x_positions = [240, 620, 1020, 1420]
    for i, (icon_label, desc) in enumerate(outcomes):
        xp = x_positions[i]
        # Icon tag
        ax.add_patch(Circle((xp + 20, bar_y - 6), 16, facecolor=GROWW_GREEN_BG))
        ax.text(xp + 20, bar_y - 6, icon_label, fontsize=10, fontweight="bold", color=GROWW_DARK_GREEN, ha="center", va="center")

        # Outcome text
        ax.text(xp + 48, bar_y - 6, desc, fontsize=11.5, fontweight="bold", color=HEADER_TEXT, va="center", linespacing=1.2)

        # Divider line except last
        if i < 3:
            ax.plot([xp + 350, xp + 350], [38, 80], color="#CBD5E1", lw=1)


def save_slide(fig, filename):
    for d in OUTPUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        path = d / filename
        fig.savefig(path, bbox_inches="tight", dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Generated Slide: {filename}")

# ==============================================================================
# SLIDE 1: THE ACCUMULATION LENS
# ==============================================================================
def create_slide_1():
    fig, ax = setup_slide_canvas()
    
    draw_header(
        ax,
        solution_badge="Solution 1",
        title="The Accumulation Lens",
        subtitle="A Year-1 portfolio mode that flips the default visual focus from paper losses to units\naccumulated at a discount during market pullbacks.",
        focus_text="Focus: Transform early loss aversion into accumulation conviction\nto keep first-time investors active through their first 12 months."
    )

    y_phone = 280
    y_step = 215

    # ------------------ PHONE 1 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 70, y_phone, 320, 520, "Portfolio")
    # Subtabs
    ax.text(sx + 15, sy + sh - 80, "Overview   Mutual Funds   Stocks", fontsize=9, fontweight="bold", color=PURPLE_BRAND)
    # Total Portfolio Card
    ax.text(sx + 15, sy + sh - 110, "Total Portfolio Value", fontsize=9, color=MUTED_TEXT)
    ax.text(sx + 15, sy + sh - 138, "Rs 2,84,500", fontsize=20, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 15, sy + sh - 160, "v -3.8% (-Rs 11,300) 1M", fontsize=9, fontweight="bold", color=RED_ALERT)
    
    # Mini chart
    cx = np.linspace(sx + 15, sx + sw - 20, 25)
    cy = sy + sh - 180 - np.sin(np.linspace(0, 3, 25)) * 8 - np.linspace(0, 12, 25)
    ax.plot(cx, cy, color="#FCA5A5", lw=1.8)

    # Nudge Card
    ax.add_patch(FancyBboxPatch((sx + 12, sy + sh - 275), sw - 24, 75, boxstyle="round,pad=1,rounding_size=10",
                                facecolor="#FEF2F2", edgecolor="#FECACA", lw=1))
    ax.text(sx + 25, sy + sh - 225, "[Calendar] Your SIP Check-in is due", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 25, sy + sh - 248, "Take 30 seconds to see how this\nmarket dip helped your SIP units.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)
    ax.text(sx + sw - 28, sy + sh - 238, ">", fontsize=13, fontweight="bold", color=MUTED_TEXT)

    # Investments list
    ax.text(sx + 15, sy + sh - 300, "Your Investments (3)", fontsize=10, fontweight="bold", color=HEADER_TEXT)
    ax.add_patch(FancyBboxPatch((sx + 12, sy + sh - 365), sw - 24, 55, boxstyle="round,pad=1,rounding_size=8",
                                facecolor=PHONE_CARD_BG, edgecolor=PHONE_BORDER, lw=0.8))
    ax.text(sx + 45, sy + sh - 330, "HDFC Flexi Cap Fund", fontsize=9, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 45, sy + sh - 348, "Rs 1,24,000   -4.1%", fontsize=8.5, color=RED_ALERT)

    draw_step_label(ax, 70 + 160, y_step, 1, "Get a timely nudge", "See a simple check-in prompt\non your portfolio during a dip.")
    draw_chevron(ax, 412, y_phone + 260)

    # ------------------ PHONE 2 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 435, y_phone, 320, 520, "SIP Confidence Check-in")
    ax.text(sx + sw/2, sy + sh - 100, "[ClipBoard]", fontsize=14, color=PURPLE_BRAND, ha="center")
    ax.text(sx + sw/2, sy + sh - 130, "How do you feel about\nyour investment right now?", fontsize=12, fontweight="bold", color=HEADER_TEXT, ha="center", linespacing=1.2)
    ax.text(sx + sw/2, sy + sh - 165, "This helps us understand your\nconfidence and show you the right math.", fontsize=8.5, color=MUTED_TEXT, ha="center", linespacing=1.2)

    # Radio Options
    opts = [
        ("Confident, I'm on track", False),
        ("Slightly uncertain", False),
        ("Concerned about recent returns", True),
        ("Need help understanding my portfolio", False)
    ]
    opt_y = sy + sh - 215
    for text, sel in opts:
        bg = "#F5F3FF" if sel else PHONE_CARD_BG
        bdr = PURPLE_BRAND if sel else PHONE_BORDER
        ax.add_patch(FancyBboxPatch((sx + 15, opt_y), sw - 30, 36, boxstyle="round,pad=1,rounding_size=8",
                                    facecolor=bg, edgecolor=bdr, lw=1.2 if sel else 0.8))
        ax.text(sx + 30, opt_y + 18, text, fontsize=8.5, fontweight="bold" if sel else "normal", color=HEADER_TEXT, va="center")
        ax.add_patch(Circle((sx + sw - 32, opt_y + 18), 7, facecolor=PURPLE_BRAND if sel else "none", edgecolor=PURPLE_BRAND, lw=1))
        opt_y -= 46

    # Continue Button
    ax.add_patch(FancyBboxPatch((sx + 15, sy + 25), sw - 30, 42, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PURPLE_BRAND, edgecolor="none"))
    ax.text(sx + sw/2, sy + 46, "Continue", fontsize=11, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    draw_step_label(ax, 435 + 160, y_step, 2, "Share your confidence", "Answer a quick, single question\nabout how you feel.")
    draw_chevron(ax, 777, y_phone + 260)

    # ------------------ PHONE 3 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 800, y_phone, 320, 520, "Here's what's happening")
    # Red drop callout
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 130), sw - 30, 55, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=RED_BG, edgecolor="#FECACA", lw=1))
    ax.text(sx + 30, sy + sh - 98, "[Trend Down] Your portfolio is down 3.8%", fontsize=9.5, fontweight="bold", color=RED_ALERT)
    ax.text(sx + 30, sy + sh - 116, "this month due to broader market noise.", fontsize=8.5, color=MUTED_TEXT)

    ax.text(sx + 15, sy + sh - 155, "Let's see how your SIP took advantage:", fontsize=9, fontweight="bold", color=HEADER_TEXT)

    # Hero Unit Card
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 280), sw - 30, 110, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_DARK_GREEN, lw=1.2))
    ax.text(sx + 25, sy + sh - 185, "THIS MONTH'S ACCUMULATION", fontsize=8, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(sx + 25, sy + sh - 215, "44.2 Units Secured", fontsize=16, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 25, sy + sh - 240, "+4.2 Bonus Units (Market Dip Discount)", fontsize=8.5, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(sx + 25, sy + sh - 262, "NAV: Rs 22.60  |  7.8% lower than last month", fontsize=8, color=MUTED_TEXT)

    # Navigation cards
    cards = ["What's driving the change?", "How does it look long term?", "Key takeaways for you"]
    cy = sy + sh - 335
    for c in cards:
        ax.add_patch(FancyBboxPatch((sx + 15, cy), sw - 30, 36, boxstyle="round,pad=1,rounding_size=8",
                                    facecolor=PHONE_CARD_BG, edgecolor=PHONE_BORDER, lw=0.8))
        ax.text(sx + 30, cy + 18, c, fontsize=9, color=HEADER_TEXT, va="center")
        ax.text(sx + sw - 32, cy + 18, ">", fontsize=11, color=MUTED_TEXT, va="center")
        cy -= 46

    draw_step_label(ax, 800 + 160, y_step, 3, "See your unit advantage", "Understand how rupee-cost\naveraging bought extra units.")
    draw_chevron(ax, 1142, y_phone + 260)

    # ------------------ PHONE 4 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 1165, y_phone, 320, 520, "Key Takeaways for You")
    
    # Point 1
    ax.add_patch(Circle((sx + 28, sy + sh - 95), 10, facecolor=GROWW_GREEN_BG))
    ax.text(sx + 28, sy + sh - 95, "[OK]", fontsize=7, color=GROWW_DARK_GREEN, ha="center", va="center")
    ax.text(sx + 46, sy + sh - 90, "This is a normal market movement", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 46, sy + sh - 118, "The broader market is down 2.6% this\nmonth, and sectors were affected.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    # Point 2
    ax.add_patch(Circle((sx + 28, sy + sh - 175), 10, facecolor=GROWW_GREEN_BG))
    ax.text(sx + 28, sy + sh - 175, "[OK]", fontsize=7, color=GROWW_DARK_GREEN, ha="center", va="center")
    ax.text(sx + 46, sy + sh - 170, "Your long-term plan is intact", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 46, sy + sh - 198, "You're investing through SIP, which\naverages out market ups and downs.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    # Yellow Takeaway Card
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 320), sw - 30, 95, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=AMBER_BG, edgecolor="#FDE68A", lw=1))
    ax.text(sx + 30, sy + sh - 250, "[Idea] What you can do", fontsize=9.5, fontweight="bold", color="#92400E")
    ax.text(sx + 30, sy + sh - 275, "* Stay invested if your goal is intact.", fontsize=8.5, color="#78350F")
    ax.text(sx + 30, sy + sh - 298, "* Review goal details if still unsure.", fontsize=8.5, color="#78350F")

    # Got It Button
    ax.add_patch(FancyBboxPatch((sx + 15, sy + 25), sw - 30, 42, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PURPLE_BRAND, edgecolor="none"))
    ax.text(sx + sw/2, sy + 46, "Got it", fontsize=11, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    draw_step_label(ax, 1165 + 160, y_step, 4, "Learn and take action", "See clear takeaways and next\nsteps based on your response.")
    draw_chevron(ax, 1507, y_phone + 260)

    # ------------------ PHONE 5 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 1530, y_phone, 320, 520, "Check-in Complete")
    # Large green circle
    ax.add_patch(Circle((sx + sw/2, sy + sh - 120), 32, facecolor=GROWW_GREEN_BG))
    ax.text(sx + sw/2, sy + sh - 120, "[Check]", fontsize=18, fontweight="bold", color=GROWW_DARK_GREEN, ha="center", va="center")

    ax.text(sx + sw/2, sy + sh - 180, "Thanks for your input!", fontsize=14, fontweight="bold", color=HEADER_TEXT, ha="center")
    ax.text(sx + sw/2, sy + sh - 215, "We'll use this to bring more relevant\ninsights and support for your journey.", fontsize=8.5, color=MUTED_TEXT, ha="center", linespacing=1.3)

    # Next Check-in Card
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 320), sw - 30, 75, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PHONE_CARD_BG, edgecolor=PHONE_BORDER, lw=0.8))
    ax.text(sx + 30, sy + sh - 270, "[Calendar] Next check-in", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 30, sy + sh - 295, "In 30 days, we'll check in again to\nsee how you're feeling.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    ax.text(sx + sw/2, sy + 60, "Update anytime in Settings >", fontsize=8.5, color=PURPLE_BRAND, ha="center")

    draw_step_label(ax, 1530 + 160, y_step, 5, "Stay supported", "Check-in complete, with a\nreminder for the next one.")

    # ------------------ OUTCOMES ------------------
    outcomes = [
        ("[Search]", "Identify investor\nuncertainty early"),
        ("[Book]", "Provide relevant\neducation and context"),
        ("[Trend]", "Build confidence\nduring market ups & downs"),
        ("[Users]", "Improve chances of SIP\ncontinuation for 12 months")
    ]
    draw_bottom_outcomes(ax, outcomes)

    save_slide(fig, "slide_solution_1_accumulation_lens.png")


# ==============================================================================
# SLIDE 2: MILESTONE HORIZON SHIELD
# ==============================================================================
def create_slide_2():
    fig, ax = setup_slide_canvas()
    
    draw_header(
        ax,
        solution_badge="Solution 2",
        title="Milestone Horizon Shield",
        subtitle="Connects short-term mutual fund market volatility directly to 10-year goal milestones,\nproving early dips have negligible impact on life goals.",
        focus_text="Focus: Anchor investors to long-term goals (Child Education, Home)\nso daily noise doesn't trigger impulsive cancellations."
    )

    y_phone = 280
    y_step = 215

    # ------------------ PHONE 1 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 70, y_phone, 320, 520, "Fund Details")
    ax.text(sx + 15, sy + sh - 80, "Parag Parikh Flexi Cap", fontsize=11, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 15, sy + sh - 105, "Monthly SIP: Rs 1,000", fontsize=9, color=MUTED_TEXT)
    ax.text(sx + 15, sy + sh - 130, "1-Month Return: -4.1%", fontsize=14, fontweight="bold", color=RED_ALERT)

    # Goal Anchor Card
    ax.add_patch(FancyBboxPatch((sx + 12, sy + sh - 250), sw - 24, 90, boxstyle="round,pad=1,rounding_size=10",
                                facecolor="#F5F3FF", edgecolor="#DDD6FE", lw=1.2))
    ax.text(sx + 25, sy + sh - 180, "[Goal] LINKED GOAL ANCHOR", fontsize=8.5, fontweight="bold", color=PURPLE_DARK)
    ax.text(sx + 25, sy + sh - 205, "Child Higher Education (2036)", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 25, sy + sh - 225, "Target: Rs 15 Lakhs | Status: 100% On Track", fontsize=8, color=GROWW_DARK_GREEN)
    ax.text(sx + 25, sy + sh - 240, "Check 10-Year Horizon Trajectory >", fontsize=8, fontweight="bold", color=PURPLE_BRAND)

    draw_step_label(ax, 70 + 160, y_step, 1, "See goal health", "View your linked milestone\nright beside the monthly dip.")
    draw_chevron(ax, 412, y_phone + 260)

    # ------------------ PHONE 2 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 435, y_phone, 320, 520, "Milestone Horizon")
    ax.text(sx + sw/2, sy + sh - 100, "[Compass]", fontsize=14, color=PURPLE_BRAND, ha="center")
    ax.text(sx + sw/2, sy + sh - 130, "When do you plan to use\nthis investment?", fontsize=12, fontweight="bold", color=HEADER_TEXT, ha="center", linespacing=1.2)
    ax.text(sx + sw/2, sy + sh - 165, "Your time horizon determines whether\nshort-term dips matter.", fontsize=8.5, color=MUTED_TEXT, ha="center", linespacing=1.2)

    opts = [
        ("In 1-2 years (Short-term)", False),
        ("In 3-5 years (Medium-term)", False),
        ("In 10+ years for my milestone", True),
        ("Not sure yet", False)
    ]
    opt_y = sy + sh - 215
    for text, sel in opts:
        bg = "#F5F3FF" if sel else PHONE_CARD_BG
        bdr = PURPLE_BRAND if sel else PHONE_BORDER
        ax.add_patch(FancyBboxPatch((sx + 15, opt_y), sw - 30, 36, boxstyle="round,pad=1,rounding_size=8",
                                    facecolor=bg, edgecolor=bdr, lw=1.2 if sel else 0.8))
        ax.text(sx + 30, opt_y + 18, text, fontsize=8.5, fontweight="bold" if sel else "normal", color=HEADER_TEXT, va="center")
        ax.add_patch(Circle((sx + sw - 32, opt_y + 18), 7, facecolor=PURPLE_BRAND if sel else "none", edgecolor=PURPLE_BRAND, lw=1))
        opt_y -= 46

    ax.add_patch(FancyBboxPatch((sx + 15, sy + 25), sw - 30, 42, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PURPLE_BRAND, edgecolor="none"))
    ax.text(sx + sw/2, sy + 46, "Check Trajectory", fontsize=11, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    draw_step_label(ax, 435 + 160, y_step, 2, "Confirm your horizon", "Reaffirm your 10-year timeline\nto unlock perspective.")
    draw_chevron(ax, 777, y_phone + 260)

    # ------------------ PHONE 3 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 800, y_phone, 320, 520, "10-Year Horizon Cone")
    ax.text(sx + 15, sy + sh - 80, "Child Education (2036)", fontsize=10, fontweight="bold", color=PURPLE_DARK)
    ax.text(sx + 15, sy + sh - 100, "10-Year Expected Trajectory Band", fontsize=8.5, color=MUTED_TEXT)

    # Trajectory Cone inside phone
    t_xs = np.linspace(sx + 20, sx + sw - 25, 30)
    cone_top = sy + sh - 250 + (t_xs - sx - 20) * 0.5
    cone_bot = sy + sh - 250 + (t_xs - sx - 20) * 0.15
    ax.fill_between(t_xs, cone_bot, cone_top, color="#EDE9FE", alpha=0.8)
    cone_mid = sy + sh - 250 + (t_xs - sx - 20) * 0.32
    ax.plot(t_xs, cone_mid, color=PURPLE_BRAND, lw=1.5, linestyle="--")
    # Current point
    ax.plot(sx + 35, sy + sh - 245, "o", color=RED_ALERT, markersize=5)
    ax.text(sx + 45, sy + sh - 240, "You (Mo 4): Dip is <0.03% variance", fontsize=7, fontweight="bold", color=HEADER_TEXT)

    # Reassurance Card
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 370), sw - 30, 85, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_DARK_GREEN, lw=1))
    ax.text(sx + 25, sy + sh - 310, "[Shield] Status: 100% On Track", fontsize=9.5, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(sx + 25, sy + sh - 335, "This month's dip affects less than\n0.03% of your 10-year goal target.", fontsize=8, color=MUTED_TEXT, linespacing=1.2)

    draw_step_label(ax, 800 + 160, y_step, 3, "Inspect trajectory cone", "See how short-term drops sit\nsafely inside expected bands.")
    draw_chevron(ax, 1142, y_phone + 260)

    # ------------------ PHONE 4 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 1165, y_phone, 320, 520, "Key Takeaways for You")
    
    # Point 1
    ax.add_patch(Circle((sx + 28, sy + sh - 95), 10, facecolor=GROWW_GREEN_BG))
    ax.text(sx + 28, sy + sh - 95, "[OK]", fontsize=7, color=GROWW_DARK_GREEN, ha="center", va="center")
    ax.text(sx + 46, sy + sh - 90, "94% of 10-Year SIPs Beat Inflation", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 46, sy + sh - 118, "Historically, every investor who held a\n10-year SIP generated positive wealth.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    # Point 2
    ax.add_patch(Circle((sx + 28, sy + sh - 175), 10, facecolor=GROWW_GREEN_BG))
    ax.text(sx + 28, sy + sh - 175, "[OK]", fontsize=7, color=GROWW_DARK_GREEN, ha="center", va="center")
    ax.text(sx + 46, sy + sh - 170, "Drawdowns are noise for 2036", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 46, sy + sh - 198, "Year 1 drawdowns do not alter your\nchild education milestone delivery.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    # Yellow Takeaway Card
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 320), sw - 30, 95, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=AMBER_BG, edgecolor="#FDE68A", lw=1))
    ax.text(sx + 30, sy + sh - 250, "[Idea] What you can do", fontsize=9.5, fontweight="bold", color="#92400E")
    ax.text(sx + 30, sy + sh - 275, "* Keep auto-debit active for 2036.", fontsize=8.5, color="#78350F")
    ax.text(sx + 30, sy + sh - 298, "* Review milestone trajectory quarterly.", fontsize=8.5, color="#78350F")

    ax.add_patch(FancyBboxPatch((sx + 15, sy + 25), sw - 30, 42, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PURPLE_BRAND, edgecolor="none"))
    ax.text(sx + sw/2, sy + 46, "Protect My Goal", fontsize=11, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    draw_step_label(ax, 1165 + 160, y_step, 4, "Learn the long view", "Review empirical data proving\nearly drops don't hurt 2036.")
    draw_chevron(ax, 1507, y_phone + 260)

    # ------------------ PHONE 5 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 1530, y_phone, 320, 520, "Shield Activated")
    ax.add_patch(Circle((sx + sw/2, sy + sh - 120), 32, facecolor=PURPLE_LIGHT))
    ax.text(sx + sw/2, sy + sh - 120, "[Shield]", fontsize=18, fontweight="bold", color=PURPLE_BRAND, ha="center", va="center")

    ax.text(sx + sw/2, sy + sh - 180, "Milestone Shield Active!", fontsize=14, fontweight="bold", color=HEADER_TEXT, ha="center")
    ax.text(sx + sw/2, sy + sh - 215, "Your SIP is now shielded by your 10-year\ngoal anchor. Daily noise muted.", fontsize=8.5, color=MUTED_TEXT, ha="center", linespacing=1.3)

    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 320), sw - 30, 75, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PHONE_CARD_BG, edgecolor=PHONE_BORDER, lw=0.8))
    ax.text(sx + 30, sy + sh - 270, "[Calendar] Next Goal Review", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 30, sy + sh - 295, "Scheduled in 90 days. We'll track\nyour trajectory progression.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    ax.text(sx + sw/2, sy + 60, "View Full Milestone Plan >", fontsize=8.5, color=PURPLE_BRAND, ha="center")

    draw_step_label(ax, 1530 + 160, y_step, 5, "Stay goal-anchored", "Milestone shield locked in,\nswitching app to quarterly reviews.")

    outcomes = [
        ("[Target]", "Anchor SIP to\nemotional milestones"),
        ("[Chart]", "Visualize 10-year\ntrajectory cone"),
        ("[Shield]", "Dampen short-term\nnoise sensitivity"),
        ("[Users]", "Benchmark retention\nagainst 10-yr investors")
    ]
    draw_bottom_outcomes(ax, outcomes)

    save_slide(fig, "slide_solution_2_milestone_horizon_shield.png")


# ==============================================================================
# SLIDE 3: MARKET CYCLE TIME MACHINE
# ==============================================================================
def create_slide_3():
    fig, ax = setup_slide_canvas()
    
    draw_header(
        ax,
        solution_badge="Solution 3",
        title="Market Cycle Time Machine",
        subtitle="An interactive simulator that demonstrates how investors who started right before past crashes\n(2020 COVID, 2022) performed if they stayed vs stopped.",
        focus_text="Focus: Replace fear of the unknown with empirical proof that\nhistorical crashes rewarded disciplined SIP accumulators."
    )

    y_phone = 280
    y_step = 215

    # ------------------ PHONE 1 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 70, y_phone, 320, 520, "Groww Insights")
    ax.text(sx + 15, sy + sh - 80, "Sensex slips 850 pts", fontsize=11, fontweight="bold", color=RED_ALERT)
    ax.text(sx + 15, sy + sh - 105, "Market Volatility Alert", fontsize=9, color=MUTED_TEXT)

    ax.add_patch(FancyBboxPatch((sx + 12, sy + sh - 250), sw - 24, 110, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=AMBER_BG, edgecolor="#FCD34D", lw=1.2))
    ax.text(sx + 25, sy + sh - 170, "[Clock] CYCLE TIME MACHINE", fontsize=8.5, fontweight="bold", color="#B45309")
    ax.text(sx + 25, sy + sh - 195, "Has this happened before?", fontsize=11, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 25, sy + sh - 225, "See what happened to investors who\nstarted SIPs right before past crashes.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)
    ax.text(sx + 25, sy + sh - 242, "Launch Historical Simulator >", fontsize=8.5, fontweight="bold", color=PURPLE_BRAND)

    draw_step_label(ax, 70 + 160, y_step, 1, "Spot the simulator", "See an interactive prompt\nduring market crash days.")
    draw_chevron(ax, 412, y_phone + 260)

    # ------------------ PHONE 2 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 435, y_phone, 320, 520, "Select Crisis")
    ax.text(sx + sw/2, sy + sh - 95, "[History]", fontsize=14, color=PURPLE_BRAND, ha="center")
    ax.text(sx + sw/2, sy + sh - 125, "Select an Indian Market Crisis", fontsize=11.5, fontweight="bold", color=HEADER_TEXT, ha="center")
    ax.text(sx + sw/2, sy + sh - 150, "Test your fund against real market history.", fontsize=8.5, color=MUTED_TEXT, ha="center")

    opts = [
        ("2020 COVID Crash (-38% drop)", True),
        ("2022 Global Rate Hikes (-15% dip)", False),
        ("2018 Mid-Cap Correction (-22%)", False),
        ("2008 Global Financial Crisis (-55%)", False)
    ]
    opt_y = sy + sh - 200
    for text, sel in opts:
        bg = "#F5F3FF" if sel else PHONE_CARD_BG
        bdr = PURPLE_BRAND if sel else PHONE_BORDER
        ax.add_patch(FancyBboxPatch((sx + 15, opt_y), sw - 30, 36, boxstyle="round,pad=1,rounding_size=8",
                                    facecolor=bg, edgecolor=bdr, lw=1.2 if sel else 0.8))
        ax.text(sx + 30, opt_y + 18, text, fontsize=8, fontweight="bold" if sel else "normal", color=HEADER_TEXT, va="center")
        ax.add_patch(Circle((sx + sw - 32, opt_y + 18), 7, facecolor=PURPLE_BRAND if sel else "none", edgecolor=PURPLE_BRAND, lw=1))
        opt_y -= 46

    ax.add_patch(FancyBboxPatch((sx + 15, sy + 25), sw - 30, 42, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PURPLE_BRAND, edgecolor="none"))
    ax.text(sx + sw/2, sy + 46, "Run 3-Yr Simulation", fontsize=11, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    draw_step_label(ax, 435 + 160, y_step, 2, "Select historical crisis", "Choose 2020 COVID or 2022\nto run empirical backtest.")
    draw_chevron(ax, 777, y_phone + 260)

    # ------------------ PHONE 3 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 800, y_phone, 320, 520, "2020 Crash Outcome")
    ax.text(sx + 15, sy + sh - 80, "3-Year Outcome Comparison", fontsize=10.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 15, sy + sh - 100, "Starting SIP: Rs 1,000 / month", fontsize=8.5, color=MUTED_TEXT)

    # Investor A
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 210), sw - 30, 95, boxstyle="round,pad=1,rounding_size=8",
                                facecolor=RED_BG, edgecolor="#FCA5A5", lw=0.8))
    ax.text(sx + 25, sy + sh - 135, "[X] Investor A (Panicked at Mo 3)", fontsize=8.5, fontweight="bold", color=RED_ALERT)
    ax.text(sx + 25, sy + sh - 158, "Invested: Rs 3,000 | Stopped in fear", fontsize=8, color=HEADER_TEXT)
    ax.text(sx + 25, sy + sh - 178, "Units Accumulated: 120 Units", fontsize=8, color=HEADER_TEXT)
    ax.text(sx + 25, sy + sh - 198, "Missed 110% recovery bull run", fontsize=8, fontweight="bold", color=RED_ALERT)

    # Investor B
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 330), sw - 30, 105, boxstyle="round,pad=1,rounding_size=8",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_DARK_GREEN, lw=0.8))
    ax.text(sx + 25, sy + sh - 245, "[OK] Investor B (Kept SIP Active)", fontsize=8.5, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(sx + 25, sy + sh - 268, "Invested: Rs 36,000 over 3 Years", fontsize=8, color=HEADER_TEXT)
    ax.text(sx + 25, sy + sh - 288, "Units Accumulated: 412 Units (+243%!)", fontsize=8, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(sx + 25, sy + sh - 312, "Portfolio Value: Rs 68,500 (+22.4% CAGR)", fontsize=8, fontweight="bold", color=GROWW_DARK_GREEN)

    draw_step_label(ax, 800 + 160, y_step, 3, "See dual-cohort outcome", "Compare investor who stopped\nvs disciplined compounder.")
    draw_chevron(ax, 1142, y_phone + 260)

    # ------------------ PHONE 4 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 1165, y_phone, 320, 520, "Key Takeaways for You")
    
    # Point 1
    ax.add_patch(Circle((sx + 28, sy + sh - 95), 10, facecolor=GROWW_GREEN_BG))
    ax.text(sx + 28, sy + sh - 95, "[OK]", fontsize=7, color=GROWW_DARK_GREEN, ha="center", va="center")
    ax.text(sx + 46, sy + sh - 90, "Crashes create bonus unit inventory", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 46, sy + sh - 118, "Investor B accumulated 243% more units\nby buying through the red months.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    # Point 2
    ax.add_patch(Circle((sx + 28, sy + sh - 175), 10, facecolor=GROWW_GREEN_BG))
    ax.text(sx + 28, sy + sh - 175, "[OK]", fontsize=7, color=GROWW_DARK_GREEN, ha="center", va="center")
    ax.text(sx + 46, sy + sh - 170, "Timing the market fails beginners", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 46, sy + sh - 198, "Stopping locked in losses; staying on\nauto-pilot delivered 22.4% CAGR.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    # Yellow Takeaway Card
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 320), sw - 30, 95, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=AMBER_BG, edgecolor="#FDE68A", lw=1))
    ax.text(sx + 30, sy + sh - 250, "[Idea] What you can do", fontsize=9.5, fontweight="bold", color="#92400E")
    ax.text(sx + 30, sy + sh - 275, "* Treat pullbacks as discount shopping.", fontsize=8.5, color="#78350F")
    ax.text(sx + 30, sy + sh - 298, "* Maintain monthly instalment discipline.", fontsize=8.5, color="#78350F")

    ax.add_patch(FancyBboxPatch((sx + 15, sy + 25), sw - 30, 42, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PURPLE_BRAND, edgecolor="none"))
    ax.text(sx + sw/2, sy + 46, "Stay Disciplined", fontsize=11, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    draw_step_label(ax, 1165 + 160, y_step, 4, "Learn the crash lesson", "Discover why every Indian crash\nrewarded SIP accumulators.")
    draw_chevron(ax, 1507, y_phone + 260)

    # ------------------ PHONE 5 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 1530, y_phone, 320, 520, "Simulator Saved")
    ax.add_patch(Circle((sx + sw/2, sy + sh - 120), 32, facecolor=GROWW_GREEN_BG))
    ax.text(sx + sw/2, sy + sh - 120, "[Check]", fontsize=18, fontweight="bold", color=GROWW_DARK_GREEN, ha="center", va="center")

    ax.text(sx + sw/2, sy + sh - 180, "Conviction Reaffirmed!", fontsize=14, fontweight="bold", color=HEADER_TEXT, ha="center")
    ax.text(sx + sw/2, sy + sh - 215, "Your 2020 Crash Simulation has been\nsaved to your Insights tab for reference.", fontsize=8.5, color=MUTED_TEXT, ha="center", linespacing=1.3)

    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 320), sw - 30, 75, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PHONE_CARD_BG, edgecolor=PHONE_BORDER, lw=0.8))
    ax.text(sx + 30, sy + sh - 270, "[Clock] Next Instalment Scheduled", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 30, sy + sh - 295, "Nov 5th auto-debit active. Securing\nyour next batch of discounted units.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    ax.text(sx + sw/2, sy + 60, "Return to Portfolio >", fontsize=8.5, color=PURPLE_BRAND, ha="center")

    draw_step_label(ax, 1530 + 160, y_step, 5, "Stay supported", "Simulation saved to insights with\nautomated instalment countdown.")

    outcomes = [
        ("[History]", "Demystify past market\ncrashes with data"),
        ("[Scale]", "Compare stopping vs\ncontinuing empirically"),
        ("[Trend]", "Reframe drawdowns as\nhigh-alpha accumulation"),
        ("[Users]", "Boost 12-month retention\nthrough market cycles")
    ]
    draw_bottom_outcomes(ax, outcomes)

    save_slide(fig, "slide_solution_3_market_cycle_time_machine.png")


# ==============================================================================
# SLIDE 4: SMART VOLATILITY BUFFER & FLEXIBLE SIP PAUSE
# ==============================================================================
def create_slide_4():
    fig, ax = setup_slide_canvas()
    
    draw_header(
        ax,
        solution_badge="Solution 4",
        title="Smart Volatility Buffer",
        subtitle="Replaces destructive SIP cancellations with a 1-click zero-penalty 30-day grace pause\nand automated salary-date alignment.",
        focus_text="Focus: Eliminate involuntary and panic churn caused by fear of\nRs 450 bank bounce penalties and salary delays."
    )

    y_phone = 280
    y_step = 215

    # ------------------ PHONE 1 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 70, y_phone, 320, 520, "Manage SIP")
    ax.text(sx + 15, sy + sh - 80, "Nippon India Small Cap", fontsize=10.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 15, sy + sh - 105, "Monthly SIP: Rs 1,000 | Debit Date: 2nd", fontsize=8.5, color=MUTED_TEXT)
    
    # Churn Interception Dialog
    ax.add_patch(FancyBboxPatch((sx + 12, sy + sh - 250), sw - 24, 120, boxstyle="round,pad=1,rounding_size=10",
                                facecolor="#EFF6FF", edgecolor="#BFDBFE", lw=1.2))
    ax.text(sx + 25, sy + sh - 160, "[Shield] CHURN INTERCEPTION", fontsize=8.5, fontweight="bold", color="#1D4ED8")
    ax.text(sx + 25, sy + sh - 185, "Thinking of stopping?", fontsize=11, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 25, sy + sh - 215, "Cancelling breaks your compounding pace\nand requires re-doing bank mandates.\nChoose a flexible alternative.", fontsize=8, color=MUTED_TEXT, linespacing=1.2)
    ax.text(sx + 25, sy + sh - 240, "Explore Smart Pause Options >", fontsize=8.5, fontweight="bold", color=PURPLE_BRAND)

    draw_step_label(ax, 70 + 160, y_step, 1, "Intercept churn intent", "Trigger supportive options when\nuser taps 'Cancel SIP'.")
    draw_chevron(ax, 412, y_phone + 260)

    # ------------------ PHONE 2 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 435, y_phone, 320, 520, "Pause Diagnostic")
    ax.text(sx + sw/2, sy + sh - 95, "[Question]", fontsize=14, color=PURPLE_BRAND, ha="center")
    ax.text(sx + sw/2, sy + sh - 125, "What's prompting your pause?", fontsize=11.5, fontweight="bold", color=HEADER_TEXT, ha="center")
    ax.text(sx + sw/2, sy + sh - 150, "We'll tailor the right flexibility support.", fontsize=8.5, color=MUTED_TEXT, ha="center")

    opts = [
        ("Nervous about recent market drop", False),
        ("Temporary cash crunch / delay", True),
        ("SIP date clashes with other bills", False),
        ("Other personal reason", False)
    ]
    opt_y = sy + sh - 200
    for text, sel in opts:
        bg = "#F5F3FF" if sel else PHONE_CARD_BG
        bdr = PURPLE_BRAND if sel else PHONE_BORDER
        ax.add_patch(FancyBboxPatch((sx + 15, opt_y), sw - 30, 36, boxstyle="round,pad=1,rounding_size=8",
                                    facecolor=bg, edgecolor=bdr, lw=1.2 if sel else 0.8))
        ax.text(sx + 30, opt_y + 18, text, fontsize=8, fontweight="bold" if sel else "normal", color=HEADER_TEXT, va="center")
        ax.add_patch(Circle((sx + sw - 32, opt_y + 18), 7, facecolor=PURPLE_BRAND if sel else "none", edgecolor=PURPLE_BRAND, lw=1))
        opt_y -= 46

    ax.add_patch(FancyBboxPatch((sx + 15, sy + 25), sw - 30, 42, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PURPLE_BRAND, edgecolor="none"))
    ax.text(sx + sw/2, sy + 46, "See Flexible Controls", fontsize=11, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    draw_step_label(ax, 435 + 160, y_step, 2, "Diagnose the friction", "Identify whether friction is cash\nshortage or market anxiety.")
    draw_chevron(ax, 777, y_phone + 260)

    # ------------------ PHONE 3 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 800, y_phone, 320, 520, "Flexibility Controls")
    ax.text(sx + 15, sy + sh - 80, "Choose Your Relief Option:", fontsize=10.5, fontweight="bold", color=HEADER_TEXT)

    # Option 1: 30-Day Skip (Selected)
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 185), sw - 30, 85, boxstyle="round,pad=1,rounding_size=8",
                                facecolor=GROWW_GREEN_BG, edgecolor=GROWW_DARK_GREEN, lw=1.2))
    ax.text(sx + 25, sy + sh - 120, "[SELECTED] Option 1: 30-Day Grace Skip", fontsize=8.5, fontweight="bold", color=GROWW_DARK_GREEN)
    ax.text(sx + 25, sy + sh - 142, "* Skips next debit (Rs 0 NACH bounce fee)", fontsize=8, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 25, sy + sh - 162, "* Units continue growing; auto-resumes Dec", fontsize=8, color=MUTED_TEXT)

    # Option 2: Shift Date
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 265), sw - 30, 65, boxstyle="round,pad=1,rounding_size=8",
                                facecolor=PHONE_CARD_BG, edgecolor=PHONE_BORDER, lw=0.8))
    ax.text(sx + 25, sy + sh - 215, "Option 2: Shift Date to Salary Day (7th)", fontsize=8.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 25, sy + sh - 238, "Move deduction after paycheck clears.", fontsize=8, color=MUTED_TEXT)

    # Option 3: Halve Amount
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 345), sw - 30, 65, boxstyle="round,pad=1,rounding_size=8",
                                facecolor=PHONE_CARD_BG, edgecolor=PHONE_BORDER, lw=0.8))
    ax.text(sx + 25, sy + sh - 295, "Option 3: Halve to Rs 500 for 2 Months", fontsize=8.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 25, sy + sh - 318, "Reduce monthly commitment temporarily.", fontsize=8, color=MUTED_TEXT)

    draw_step_label(ax, 800 + 160, y_step, 3, "Select flexible relief", "Choose 30-day skip, date shift,\nor temporary micro-SIP.")
    draw_chevron(ax, 1142, y_phone + 260)

    # ------------------ PHONE 4 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 1165, y_phone, 320, 520, "Key Takeaways for You")
    
    # Point 1
    ax.add_patch(Circle((sx + 28, sy + sh - 95), 10, facecolor=GROWW_GREEN_BG))
    ax.text(sx + 28, sy + sh - 95, "[OK]", fontsize=7, color=GROWW_DARK_GREEN, ha="center", va="center")
    ax.text(sx + 46, sy + sh - 90, "Zero Bank Penalty Guaranteed", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 46, sy + sh - 118, "Groww pauses the NACH mandate\nwith your bank. No Rs 450 bounce fee.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    # Point 2
    ax.add_patch(Circle((sx + 28, sy + sh - 175), 10, facecolor=GROWW_GREEN_BG))
    ax.text(sx + 28, sy + sh - 175, "[OK]", fontsize=7, color=GROWW_DARK_GREEN, ha="center", va="center")
    ax.text(sx + 46, sy + sh - 170, "Compounding remains active", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 46, sy + sh - 198, "Your existing units stay invested and\nearn market returns uninterrupted.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    # Yellow Takeaway Card
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 320), sw - 30, 95, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=AMBER_BG, edgecolor="#FDE68A", lw=1))
    ax.text(sx + 30, sy + sh - 250, "[Idea] What you can do", fontsize=9.5, fontweight="bold", color="#92400E")
    ax.text(sx + 30, sy + sh - 275, "* Take a 30-day breather stress-free.", fontsize=8.5, color="#78350F")
    ax.text(sx + 30, sy + sh - 298, "* AutoPay restarts automatically in Dec.", fontsize=8.5, color="#78350F")

    ax.add_patch(FancyBboxPatch((sx + 15, sy + 25), sw - 30, 42, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=GROWW_GREEN, edgecolor="none"))
    ax.text(sx + sw/2, sy + 46, "Confirm 30-Day Pause", fontsize=11, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    draw_step_label(ax, 1165 + 160, y_step, 4, "Learn pause benefits", "See how smart pause saves\nyour 12-month compounding.")
    draw_chevron(ax, 1507, y_phone + 260)

    # ------------------ PHONE 5 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 1530, y_phone, 320, 520, "Pause Confirmed")
    ax.add_patch(Circle((sx + sw/2, sy + sh - 120), 32, facecolor=GROWW_GREEN_BG))
    ax.text(sx + sw/2, sy + sh - 120, "[Shield]", fontsize=18, fontweight="bold", color=GROWW_DARK_GREEN, ha="center", va="center")

    ax.text(sx + sw/2, sy + sh - 180, "SIP Safely Paused!", fontsize=14, fontweight="bold", color=HEADER_TEXT, ha="center")
    ax.text(sx + sw/2, sy + sh - 215, "Your November debit is skipped with Rs 0 fees.\nExisting units remain invested.", fontsize=8.5, color=MUTED_TEXT, ha="center", linespacing=1.3)

    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 320), sw - 30, 75, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PHONE_CARD_BG, edgecolor=PHONE_BORDER, lw=0.8))
    ax.text(sx + 30, sy + sh - 270, "[Clock] Auto-Resume Scheduled", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 30, sy + sh - 295, "Instalment auto-resumes on Dec 5th.\nNo manual banking action needed.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    ax.text(sx + sw/2, sy + 60, "Manage SIP Settings >", fontsize=8.5, color=PURPLE_BRAND, ha="center")

    draw_step_label(ax, 1530 + 160, y_step, 5, "Stay supported", "Pause active with auto-resume date;\nzero mandate deletion churn.")

    outcomes = [
        ("[Shield]", "Eliminate bank NACH\nbounce penalty fears"),
        ("[Calendar]", "Align debits with\nsalary credit cycles"),
        ("[Settings]", "Prevent destructive\nbinary cancellations"),
        ("[Users]", "Protect 12-month active\nretention through crunches")
    ]
    draw_bottom_outcomes(ax, outcomes)

    save_slide(fig, "slide_solution_4_smart_volatility_buffer_pause.png")


# ==============================================================================
# SLIDE 5: SIP CONFIDENCE CHECK-IN & CONTEXTUAL ATTRIBUTOR
# ==============================================================================
def create_slide_5():
    fig, ax = setup_slide_canvas()
    
    draw_header(
        ax,
        solution_badge="Solution 5",
        title="SIP Confidence Check-in",
        subtitle="A proactive monthly check-in that identifies investor uncertainty early and explains\nportfolio movements in plain language before doubt turns into churn.",
        focus_text="Focus: Identify investor uncertainty early and give relevant support\nto keep them invested for 12 months."
    )

    y_phone = 280
    y_step = 215

    # ------------------ PHONE 1 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 70, y_phone, 320, 520, "Portfolio")
    ax.text(sx + 15, sy + sh - 80, "Overview   Mutual Funds   Stocks", fontsize=9, fontweight="bold", color=PURPLE_BRAND)
    ax.text(sx + 15, sy + sh - 110, "Total Portfolio Value", fontsize=9, color=MUTED_TEXT)
    ax.text(sx + 15, sy + sh - 138, "Rs 2,84,500", fontsize=20, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 15, sy + sh - 160, "v -3.8% (-Rs 11,300) 1M", fontsize=9, fontweight="bold", color=RED_ALERT)

    cx = np.linspace(sx + 15, sx + sw - 20, 25)
    cy = sy + sh - 180 - np.sin(np.linspace(0, 3, 25)) * 8 - np.linspace(0, 12, 25)
    ax.plot(cx, cy, color="#FCA5A5", lw=1.8)

    ax.add_patch(FancyBboxPatch((sx + 12, sy + sh - 275), sw - 24, 75, boxstyle="round,pad=1,rounding_size=10",
                                facecolor="#FEF2F2", edgecolor="#FECACA", lw=1))
    ax.text(sx + 25, sy + sh - 225, "[Calendar] Your SIP Check-in is due", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 25, sy + sh - 248, "Take 30 seconds to tell us how\nyou feel about your investments.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)
    ax.text(sx + sw - 28, sy + sh - 238, ">", fontsize=13, fontweight="bold", color=MUTED_TEXT)

    ax.text(sx + 15, sy + sh - 300, "Your Investments (3)", fontsize=10, fontweight="bold", color=HEADER_TEXT)
    ax.add_patch(FancyBboxPatch((sx + 12, sy + sh - 365), sw - 24, 55, boxstyle="round,pad=1,rounding_size=8",
                                facecolor=PHONE_CARD_BG, edgecolor=PHONE_BORDER, lw=0.8))
    ax.text(sx + 45, sy + sh - 330, "HDFC Flexi Cap Fund", fontsize=9, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 45, sy + sh - 348, "Rs 1,24,000   -4.1%", fontsize=8.5, color=RED_ALERT)

    draw_step_label(ax, 70 + 160, y_step, 1, "Get a timely nudge", "See a simple check-in prompt\non your portfolio.")
    draw_chevron(ax, 412, y_phone + 260)

    # ------------------ PHONE 2 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 435, y_phone, 320, 520, "SIP Confidence Check-in")
    ax.text(sx + sw/2, sy + sh - 100, "[ClipBoard]", fontsize=14, color=PURPLE_BRAND, ha="center")
    ax.text(sx + sw/2, sy + sh - 130, "How do you feel about\nyour investment right now?", fontsize=12, fontweight="bold", color=HEADER_TEXT, ha="center", linespacing=1.2)
    ax.text(sx + sw/2, sy + sh - 165, "This helps us understand your\nconfidence and show you the right math.", fontsize=8.5, color=MUTED_TEXT, ha="center", linespacing=1.2)

    opts = [
        ("Confident, I'm on track", False),
        ("Slightly uncertain", False),
        ("Concerned about recent returns", True),
        ("Need help understanding my portfolio", False)
    ]
    opt_y = sy + sh - 215
    for text, sel in opts:
        bg = "#F5F3FF" if sel else PHONE_CARD_BG
        bdr = PURPLE_BRAND if sel else PHONE_BORDER
        ax.add_patch(FancyBboxPatch((sx + 15, opt_y), sw - 30, 36, boxstyle="round,pad=1,rounding_size=8",
                                    facecolor=bg, edgecolor=bdr, lw=1.2 if sel else 0.8))
        ax.text(sx + 30, opt_y + 18, text, fontsize=8.5, fontweight="bold" if sel else "normal", color=HEADER_TEXT, va="center")
        ax.add_patch(Circle((sx + sw - 32, opt_y + 18), 7, facecolor=PURPLE_BRAND if sel else "none", edgecolor=PURPLE_BRAND, lw=1))
        opt_y -= 46

    ax.add_patch(FancyBboxPatch((sx + 15, sy + 25), sw - 30, 42, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PURPLE_BRAND, edgecolor="none"))
    ax.text(sx + sw/2, sy + 46, "Continue", fontsize=11, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    draw_step_label(ax, 435 + 160, y_step, 2, "Share your confidence", "Answer a quick, single question\nabout how you feel.")
    draw_chevron(ax, 777, y_phone + 260)

    # ------------------ PHONE 3 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 800, y_phone, 320, 520, "Here's what's happening")
    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 130), sw - 30, 55, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=RED_BG, edgecolor="#FECACA", lw=1))
    ax.text(sx + 30, sy + sh - 98, "[Trend Down] Your portfolio is down 3.8%", fontsize=9.5, fontweight="bold", color=RED_ALERT)
    ax.text(sx + 30, sy + sh - 116, "this month. Let's understand it better.", fontsize=8.5, color=MUTED_TEXT)

    ax.text(sx + 15, sy + sh - 155, "Let's understand it better:", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)

    cards = [
        ("[BarChart] What's driving the change?\nMarket, sector and fund impact", 75),
        ("[Clock] How does it look long term?\nYour performance over time", 75),
        ("[Book] Key takeaways for you\nSimple, relevant insights", 75)
    ]
    cy = sy + sh - 250
    for title, h in cards:
        ax.add_patch(FancyBboxPatch((sx + 15, cy), sw - 30, 55, boxstyle="round,pad=1,rounding_size=8",
                                    facecolor=PHONE_CARD_BG, edgecolor=PHONE_BORDER, lw=0.8))
        ax.text(sx + 30, cy + 28, title, fontsize=8.5, color=HEADER_TEXT, va="center", linespacing=1.2)
        ax.text(sx + sw - 32, cy + 28, ">", fontsize=11, color=MUTED_TEXT, va="center")
        cy -= 65

    draw_step_label(ax, 800 + 160, y_step, 3, "Get relevant insights", "Understand why your portfolio\nchanged and what's driving it.")
    draw_chevron(ax, 1142, y_phone + 260)

    # ------------------ PHONE 4 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 1165, y_phone, 320, 520, "Key Takeaways for You")
    
    ax.add_patch(Circle((sx + 28, sy + sh - 95), 10, facecolor=GROWW_GREEN_BG))
    ax.text(sx + 28, sy + sh - 95, "[OK]", fontsize=7, color=GROWW_DARK_GREEN, ha="center", va="center")
    ax.text(sx + 46, sy + sh - 90, "This is a normal market movement", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 46, sy + sh - 118, "The broader market is down 2.6% this\nmonth, and some sectors were affected.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    ax.add_patch(Circle((sx + 28, sy + sh - 175), 10, facecolor=GROWW_GREEN_BG))
    ax.text(sx + 28, sy + sh - 175, "[OK]", fontsize=7, color=GROWW_DARK_GREEN, ha="center", va="center")
    ax.text(sx + 46, sy + sh - 170, "Your long-term plan is intact", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 46, sy + sh - 198, "You're investing through SIP, which helps\naverage out market ups and downs.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 320), sw - 30, 95, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=AMBER_BG, edgecolor="#FDE68A", lw=1))
    ax.text(sx + 30, sy + sh - 250, "[Idea] What you can do", fontsize=9.5, fontweight="bold", color="#92400E")
    ax.text(sx + 30, sy + sh - 275, "* Stay invested if your goal is intact.", fontsize=8.5, color="#78350F")
    ax.text(sx + 30, sy + sh - 298, "* Review your goal or fund details.", fontsize=8.5, color="#78350F")

    ax.add_patch(FancyBboxPatch((sx + 15, sy + 25), sw - 30, 42, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PURPLE_BRAND, edgecolor="none"))
    ax.text(sx + sw/2, sy + 46, "Got it", fontsize=11, fontweight="bold", color="#FFFFFF", ha="center", va="center")

    draw_step_label(ax, 1165 + 160, y_step, 4, "Learn and take action", "See clear takeaways and next\nsteps based on your response.")
    draw_chevron(ax, 1507, y_phone + 260)

    # ------------------ PHONE 5 ------------------
    sx, sy, sw, sh = draw_phone_frame(ax, 1530, y_phone, 320, 520, "Check-in Complete")
    ax.add_patch(Circle((sx + sw/2, sy + sh - 120), 32, facecolor=GROWW_GREEN_BG))
    ax.text(sx + sw/2, sy + sh - 120, "[Check]", fontsize=18, fontweight="bold", color=GROWW_DARK_GREEN, ha="center", va="center")

    ax.text(sx + sw/2, sy + sh - 180, "Thanks for your input!", fontsize=14, fontweight="bold", color=HEADER_TEXT, ha="center")
    ax.text(sx + sw/2, sy + sh - 215, "We'll use this to bring more relevant\ninsights and support for you.", fontsize=8.5, color=MUTED_TEXT, ha="center", linespacing=1.3)

    ax.add_patch(FancyBboxPatch((sx + 15, sy + sh - 320), sw - 30, 75, boxstyle="round,pad=1,rounding_size=10",
                                facecolor=PHONE_CARD_BG, edgecolor=PHONE_BORDER, lw=0.8))
    ax.text(sx + 30, sy + sh - 270, "[Calendar] Next check-in", fontsize=9.5, fontweight="bold", color=HEADER_TEXT)
    ax.text(sx + 30, sy + sh - 295, "In 30 days, we'll check in again to\nsee how you're feeling.", fontsize=8.5, color=MUTED_TEXT, linespacing=1.2)

    ax.text(sx + sw/2, sy + 60, "Update anytime in Settings >", fontsize=8.5, color=PURPLE_BRAND, ha="center")

    draw_step_label(ax, 1530 + 160, y_step, 5, "Stay supported", "Check-in complete, with a\nreminder for the next one.")

    outcomes = [
        ("[Search]", "Identify investor\nuncertainty early"),
        ("[Book]", "Provide relevant\neducation and context"),
        ("[Trend]", "Build confidence\nduring market ups & downs"),
        ("[Users]", "Improve chances of SIP\ncontinuation for 12 months")
    ]
    draw_bottom_outcomes(ax, outcomes)

    save_slide(fig, "slide_solution_5_sip_confidence_checkin.png")


if __name__ == "__main__":
    print("Generating all 5 Figma-Style Slide Presentation Images...")
    create_slide_1()
    create_slide_2()
    create_slide_3()
    create_slide_4()
    create_slide_5()
    print("All 5 Slides successfully generated!")
