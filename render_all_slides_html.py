"""Pixel-Perfect HTML/CSS 16:9 Presentation Slide Generator for Groww.
Renders all 5 solution flows using headless Chrome with authentic typography,
CSS flexbox layouts, SVG icons, box shadows, and zero distortion.
"""

from pathlib import Path
import subprocess
import shutil

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_DIR = Path("deliverables/screens")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BRAIN_DIR = Path(r"C:\Users\KAUSTUBH\.gemini\antigravity\brain\708df285-86a7-405f-be3f-5a6d8dc3d597\screens")
BRAIN_DIR.mkdir(parents=True, exist_ok=True)


def build_slide_html(badge, title, subtitle, focus, phones, outcomes):
    """Assembles the complete 1920x1080 HTML page for a solution slide."""
    
    phones_html = ""
    for i, p in enumerate(phones):
        phones_html += f"""
        <div class="phone-column">
          <div class="phone-frame">
            <div class="notch"></div>
            <div class="status-bar">
              <span>9:41</span>
              <div style="display: flex; gap: 4px; align-items: center;">
                <svg width="12" height="10" viewBox="0 0 12 10" fill="#0F172A"><path d="M1 8h2v2H1V8zm3-3h2v5H4V5zm3-3h2v8H7V2zm3-2h2v10h-2V0z"/></svg>
                <div style="width: 18px; height: 9px; border: 1.5px solid #0F172A; border-radius: 2.5px; padding: 1px; display: flex;">
                  <div style="width: 80%; height: 100%; background: #0F172A; border-radius: 1px;"></div>
                </div>
              </div>
            </div>
            
            <div class="app-header">
              {p.get('back_btn', '<span style="font-size: 14px; font-weight: 800;">←</span>')}
              <span class="app-header-title">{p['screen_title']}</span>
            </div>
            
            <div class="screen-content">
              {p['content_html']}
            </div>
          </div>

          <div class="step-info">
            <div class="step-number">{i + 1}</div>
            <div>
              <div class="step-title">{p['step_title']}</div>
              <div class="step-desc">{p['step_desc']}</div>
            </div>
          </div>
        </div>
        """
        if i < 4:
            phones_html += '<div class="chevron">›</div>'

    outcomes_html = ""
    for icon_svg, desc in outcomes:
        outcomes_html += f"""
        <div class="outcome-item">
          <div class="outcome-icon">{icon_svg}</div>
          <div class="outcome-text">{desc}</div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1920px;
    height: 1080px;
    background: #F8FAFC;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #0F172A;
    padding: 34px 44px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }}

  .header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }}
  .brand-row {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .groww-logo {{
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #00D09C 0%, #0284C7 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 800;
    font-size: 16px;
  }}
  .groww-text {{
    font-size: 24px;
    font-weight: 800;
    color: #0F172A;
  }}
  .solution-badge {{
    background: #EEF2FF;
    border: 1px solid #C7D2FE;
    color: #4F46E5;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
  }}
  .slide-title {{
    font-size: 28px;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.5px;
    margin-top: 6px;
  }}
  .slide-subtitle {{
    font-size: 14.5px;
    color: #475569;
    max-width: 920px;
    line-height: 1.4;
    margin-top: 3px;
  }}
  .focus-box {{
    background: #EDE9FE;
    border: 1px solid #DDD6FE;
    border-radius: 16px;
    padding: 16px 22px;
    display: flex;
    align-items: center;
    gap: 16px;
    max-width: 600px;
  }}
  .focus-icon {{
    width: 44px;
    height: 44px;
    background: #DDD6FE;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    color: #5B21B6;
    flex-shrink: 0;
  }}
  .focus-text {{
    font-size: 14px;
    font-weight: 700;
    color: #1E1B4B;
    line-height: 1.45;
  }}

  .flow-container {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    margin-top: 8px;
  }}
  .phone-column {{
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 312px;
  }}

  .phone-frame {{
    width: 308px;
    height: 524px;
    background: #FFFFFF;
    border: 3.5px solid #0F172A;
    border-radius: 38px;
    box-shadow: 0 16px 36px -12px rgba(15, 23, 42, 0.18), 0 0 0 1px rgba(15, 23, 42, 0.05);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    position: relative;
  }}
  .notch {{
    position: absolute;
    top: 9px;
    left: 50%;
    transform: translateX(-50%);
    width: 78px;
    height: 14px;
    background: #0F172A;
    border-radius: 10px;
    z-index: 10;
  }}
  .status-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 24px 6px;
    font-size: 11px;
    font-weight: 700;
    color: #0F172A;
  }}
  .app-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 18px 10px;
    border-bottom: 1px solid #F1F5F9;
  }}
  .app-header-title {{
    font-size: 13.5px;
    font-weight: 700;
    color: #0F172A;
  }}
  .screen-content {{
    flex: 1;
    padding: 12px 16px 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    overflow: hidden;
    background: #FFFFFF;
  }}

  .chevron {{
    font-size: 32px;
    font-weight: 800;
    color: #A5B4FC;
    margin-top: -65px;
  }}

  .step-info {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-top: 14px;
    width: 295px;
  }}
  .step-number {{
    width: 26px;
    height: 26px;
    background: #6366F1;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 13px;
    flex-shrink: 0;
  }}
  .step-title {{
    font-size: 13.5px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 2px;
  }}
  .step-desc {{
    font-size: 11px;
    color: #64748B;
    line-height: 1.35;
  }}

  .card-box {{
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 10px 12px;
  }}
  .primary-btn {{
    background: #6366F1;
    color: white;
    text-align: center;
    padding: 11px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 12px;
    margin-top: auto;
  }}

  .outcome-bar {{
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    padding: 14px 28px;
    display: flex;
    align-items: center;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
  }}
  .outcome-pill {{
    background: #00D09C;
    color: white;
    font-weight: 800;
    font-size: 14.5px;
    padding: 7px 18px;
    border-radius: 20px;
    margin-right: 32px;
  }}
  .outcome-grid {{
    display: flex;
    align-items: center;
    flex: 1;
    justify-content: space-between;
  }}
  .outcome-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding-right: 28px;
    border-right: 1px solid #E2E8F0;
  }}
  .outcome-item:last-child {{
    border-right: none;
    padding-right: 0;
  }}
  .outcome-icon {{
    width: 32px;
    height: 32px;
    background: #E6FBF5;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    color: #008764;
    font-weight: 800;
  }}
  .outcome-text {{
    font-size: 12.5px;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.25;
  }}
</style>
</head>
<body>

  <!-- HEADER -->
  <div class="header">
    <div class="header-left">
      <div class="brand-row">
        <div class="groww-logo">G</div>
        <span class="groww-text">Groww</span>
        <span class="solution-badge">{badge}</span>
      </div>
      <div class="slide-title">{title}</div>
      <div class="slide-subtitle">{subtitle}</div>
    </div>
    <div class="focus-box">
      <div class="focus-icon">🎯</div>
      <div class="focus-text">Focus: {focus}</div>
    </div>
  </div>

  <!-- FLOW CONTAINER (5 PHONES) -->
  <div class="flow-container">
    {phones_html}
  </div>

  <!-- BOTTOM OUTCOME BAR -->
  <div class="outcome-bar">
    <div class="outcome-pill">Outcome</div>
    <div class="outcome-grid">
      {outcomes_html}
    </div>
  </div>

</body>
</html>
"""
    return html


def render_html_to_png(html_str, filename):
    temp_html = Path(r"C:\temp\render_temp.html")
    temp_html.write_text(html_str, encoding="utf-8")
    
    out_1 = OUTPUT_DIR / filename
    out_2 = BRAIN_DIR / filename
    
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1920,1080",
        f"--screenshot={out_1.resolve()}",
        f"file:///{temp_html.resolve()}".replace("\\", "/")
    ]
    subprocess.run(cmd, check=True)
    shutil.copy2(out_1, out_2)
    print(f"Generated: {filename} ({out_1.stat().st_size} bytes)")

# ==============================================================================
# SLIDE 1: THE ACCUMULATION LENS
# ==============================================================================
def generate_slide_1():
    phones = [
        # Phone 1
        {
            "screen_title": "Portfolio",
            "back_btn": '<span style="font-size: 14px; font-weight: 800;">🔍</span>',
            "step_title": "Get a timely nudge",
            "step_desc": "See a simple check-in prompt on your portfolio.",
            "content_html": """
              <div style="display: flex; gap: 14px; font-size: 11.5px; font-weight: 700; color: #6366F1; border-bottom: 2px solid #F1F5F9; padding-bottom: 6px;">
                <span style="border-bottom: 2px solid #6366F1; padding-bottom: 6px;">Overview</span>
                <span style="color: #64748B;">Mutual Funds</span>
                <span style="color: #64748B;">Stocks</span>
              </div>
              <div>
                <div style="font-size: 11px; color: #64748B; font-weight: 600;">Total Portfolio Value</div>
                <div style="font-size: 22px; font-weight: 800; color: #0F172A; margin: 2px 0;">₹2,84,500</div>
                <div style="font-size: 11px; font-weight: 700; color: #EF4444;">▼ -3.8% (-₹11,300) <span style="font-weight: 500; color: #64748B;">1M</span></div>
              </div>
              <svg width="276" height="38" viewBox="0 0 276 38" fill="none">
                <path d="M0 8 C 50 12, 100 24, 150 18 C 200 12, 240 32, 276 35" stroke="#EF4444" stroke-width="2" fill="none"/>
              </svg>
              <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 12px; padding: 12px; display: flex; align-items: center; justify-content: space-between;">
                <div>
                  <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">📅 Your SIP Check-in is due</div>
                  <div style="font-size: 10px; color: #64748B; margin-top: 2px;">Take 30 seconds to see how this dip helped your SIP units.</div>
                </div>
                <span style="font-size: 14px; font-weight: 800; color: #64748B;">›</span>
              </div>
              <div style="font-size: 11.5px; font-weight: 700; color: #0F172A; margin-top: 4px;">Your Investments (3)</div>
              <div class="card-box" style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                  <div style="font-size: 11px; font-weight: 700; color: #0F172A;">HDFC Flexi Cap Fund</div>
                  <div style="font-size: 10px; color: #64748B;">₹1,24,000 <span style="color: #EF4444; font-weight: 700;">-4.1%</span></div>
                </div>
                <span style="color: #94A3B8;">›</span>
              </div>
            """
        },
        # Phone 2
        {
            "screen_title": "SIP Confidence Check-in",
            "step_title": "Share your confidence",
            "step_desc": "Answer a quick, single question about how you feel.",
            "content_html": """
              <div style="text-align: center; margin: 8px 0;">
                <div style="font-size: 28px;">📋</div>
                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin-top: 4px;">How do you feel about<br/>your investment right now?</div>
                <div style="font-size: 10px; color: #64748B; margin-top: 3px;">This helps us tailor your unit report.</div>
              </div>
              <div style="display: flex; flex-direction: column; gap: 8px;">
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">😊 Confident, I'm on track</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">😐 Slightly uncertain</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: #EEF2FF; border-color: #6366F1;">
                  <span style="font-size: 11px; font-weight: 700; color: #1E1B4B;">😟 Concerned about returns</span>
                  <div style="width: 14px; height: 14px; border: 4px solid #6366F1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">❓ Need help understanding</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
              </div>
              <div class="primary-btn">Continue</div>
            """
        },
        # Phone 3
        {
            "screen_title": "Here's what's happening",
            "step_title": "See your unit advantage",
            "step_desc": "Understand how rupee-cost averaging bought extra units.",
            "content_html": """
              <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 12px; padding: 10px 12px;">
                <div style="font-size: 11px; font-weight: 700; color: #EF4444;">📉 Your portfolio is down 3.8% this month.</div>
                <div style="font-size: 9.5px; color: #64748B; margin-top: 2px;">Let's see how your SIP took advantage:</div>
              </div>
              <div style="background: #E6FBF5; border: 1.5px solid #00D09C; border-radius: 12px; padding: 12px;">
                <div style="font-size: 10px; font-weight: 700; color: #008764;">DISCOUNT ACCUMULATION ACTIVE</div>
                <div style="font-size: 18px; font-weight: 800; color: #044332; margin: 2px 0;">44.2 Units Secured</div>
                <div style="font-size: 10.5px; font-weight: 700; color: #008764;">🎁 +4.2 Bonus Units (7.8% NAV Discount)</div>
                <div style="font-size: 9.5px; color: #475569; margin-top: 3px;">Purchase NAV: ₹22.60 vs ₹25.10 last month</div>
              </div>
              <div style="display: flex; flex-direction: column; gap: 8px;">
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-size: 10.5px; font-weight: 600;">📊 What's driving the change?</span>
                  <span style="color: #94A3B8;">›</span>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-size: 10.5px; font-weight: 600;">⏱️ How does it look long term?</span>
                  <span style="color: #94A3B8;">›</span>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-size: 10.5px; font-weight: 600;">📖 Key takeaways for you</span>
                  <span style="color: #94A3B8;">›</span>
                </div>
              </div>
            """
        },
        # Phone 4
        {
            "screen_title": "Key Takeaways for You",
            "step_title": "Learn and take action",
            "step_desc": "See clear takeaways and next steps based on your response.",
            "content_html": """
              <div style="display: flex; gap: 10px; align-items: flex-start;">
                <div style="width: 22px; height: 22px; background: #E6FBF5; border-radius: 50%; color: #008764; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">✓</div>
                <div>
                  <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">This is a normal market movement</div>
                  <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 2px;">The broader market is down 2.6% this month, and sectors were affected.</div>
                </div>
              </div>
              <div style="display: flex; gap: 10px; align-items: flex-start;">
                <div style="width: 22px; height: 22px; background: #E6FBF5; border-radius: 50%; color: #008764; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">✓</div>
                <div>
                  <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">Your long-term plan is intact</div>
                  <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 2px;">You're investing through SIP, which averages out market ups and downs.</div>
                </div>
              </div>
              <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 12px; padding: 12px;">
                <div style="font-size: 11.5px; font-weight: 700; color: #92400E;">💡 What you can do</div>
                <div style="font-size: 10px; color: #78350F; line-height: 1.4; margin-top: 4px;">
                  • Stay invested if your goal is intact.<br/>
                  • Review your goal or fund details if unsure.
                </div>
              </div>
              <div class="primary-btn">Got it</div>
            """
        },
        # Phone 5
        {
            "screen_title": "Check-in Complete",
            "step_title": "Stay supported",
            "step_desc": "Check-in complete, with a reminder for the next one.",
            "content_html": """
              <div style="text-align: center; margin: 16px 0;">
                <div style="width: 58px; height: 58px; background: #00D09C; color: white; border-radius: 50%; font-size: 26px; font-weight: 800; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px;">✓</div>
                <div style="font-size: 15px; font-weight: 800; color: #0F172A;">Thanks for your input!</div>
                <div style="font-size: 10.5px; color: #64748B; line-height: 1.4; margin-top: 4px;">We'll use this to bring more relevant insights and support for you.</div>
              </div>
              <div class="card-box" style="margin-top: 10px;">
                <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">📅 Next check-in</div>
                <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 3px;">In 30 days, we'll check in again to see how you're feeling.</div>
              </div>
              <div style="text-align: center; font-size: 10.5px; font-weight: 700; color: #6366F1; margin-top: auto; padding-bottom: 8px;">Update anytime in Settings ›</div>
            """
        }
    ]

    outcomes = [
        ("🔍", "Identify investor<br/>uncertainty early"),
        ("📖", "Provide relevant<br/>education & context"),
        ("📈", "Build confidence<br/>during market dips"),
        ("👥", "Improve chances of SIP<br/>continuation for 12 months")
    ]

    html = build_slide_html(
        badge="Solution 1",
        title="The Accumulation Lens 🏷️",
        subtitle="A simple, periodic check-in that reframes portfolio drawdowns into unit accumulation advantages, keeping investors disciplined through Year 1.",
        focus="Identify investor uncertainty early and give relevant support to keep them invested for 12 months.",
        phones=phones,
        outcomes=outcomes
    )
    render_html_to_png(html, "slide_solution_1_accumulation_lens.png")


# ==============================================================================
# SLIDE 2: MILESTONE HORIZON SHIELD
# ==============================================================================
def generate_slide_2():
    phones = [
        # Phone 1
        {
            "screen_title": "Fund Details",
            "back_btn": '<span style="font-size: 14px; font-weight: 800;">←</span>',
            "step_title": "See goal status",
            "step_desc": "Spot your linked milestone directly alongside short-term negative returns.",
            "content_html": """
              <div>
                <div style="font-size: 13px; font-weight: 800; color: #0F172A;">Parag Parikh Flexi Cap</div>
                <div style="font-size: 10.5px; color: #64748B;">Monthly SIP: ₹1,000</div>
                <div style="font-size: 15px; font-weight: 800; color: #EF4444; margin-top: 4px;">▼ -4.1% <span style="font-size: 10px; font-weight: 500; color: #64748B;">1-Month Return</span></div>
              </div>
              <div style="background: #F5F3FF; border: 1.5px solid #DDD6FE; border-radius: 12px; padding: 12px; margin-top: 8px;">
                <div style="font-size: 10px; font-weight: 800; color: #6366F1;">🎯 LINKED GOAL ANCHOR</div>
                <div style="font-size: 12px; font-weight: 800; color: #1E1B4B; margin-top: 3px;">Child Higher Education (2036)</div>
                <div style="font-size: 10px; color: #008764; font-weight: 700; margin-top: 2px;">Target: ₹15 Lakhs • Status: 100% On Track</div>
                <div style="font-size: 10px; font-weight: 700; color: #6366F1; margin-top: 6px;">Check 10-Year Horizon Trajectory ›</div>
              </div>
              <div class="card-box" style="margin-top: 8px;">
                <div style="font-size: 11px; font-weight: 700;">Fund Asset Allocation</div>
                <div style="font-size: 10px; color: #64748B; margin-top: 2px;">Equity: 84% | Cash: 16%</div>
              </div>
            """
        },
        # Phone 2
        {
            "screen_title": "Confirm Horizon",
            "step_title": "Confirm your horizon",
            "step_desc": "Reaffirm your 10-year timeline to unlock perspective.",
            "content_html": """
              <div style="text-align: center; margin: 8px 0;">
                <div style="font-size: 28px;">🧭</div>
                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin-top: 4px;">When do you plan to use<br/>this investment?</div>
                <div style="font-size: 10px; color: #64748B; margin-top: 3px;">Your time horizon determines if dips matter.</div>
              </div>
              <div style="display: flex; flex-direction: column; gap: 8px;">
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">In 1–2 years (Short term)</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">In 3–5 years (Medium term)</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: #EEF2FF; border-color: #6366F1;">
                  <span style="font-size: 11px; font-weight: 700; color: #1E1B4B;">In 10+ years (Milestone)</span>
                  <div style="width: 14px; height: 14px; border: 4px solid #6366F1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">Not sure yet</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
              </div>
              <div class="primary-btn">Inspect Trajectory</div>
            """
        },
        # Phone 3
        {
            "screen_title": "10-Year Horizon Cone",
            "step_title": "Inspect trajectory cone",
            "step_desc": "See how short-term drops sit safely inside expected bands.",
            "content_html": """
              <div>
                <div style="font-size: 12px; font-weight: 800; color: #6366F1;">Child Education Fund (2036)</div>
                <div style="font-size: 10px; color: #64748B;">10-Year Statistical Projection Band</div>
              </div>
              <div style="background: #F5F3FF; border: 1px solid #DDD6FE; border-radius: 12px; padding: 12px; text-align: center;">
                <svg width="250" height="90" viewBox="0 0 250 90">
                  <polygon points="10,65 240,15 240,80 10,65" fill="#DDD6FE" opacity="0.6"/>
                  <line x1="10" y1="65" x2="240" y2="45" stroke="#6366F1" stroke-width="2" stroke-dasharray="4"/>
                  <circle cx="45" cy="62" r="5" fill="#EF4444"/>
                </svg>
                <div style="font-size: 10px; font-weight: 700; color: #0F172A;">You are here (Month 4): Dip is &lt;0.03% variance</div>
              </div>
              <div style="background: #E6FBF5; border: 1px solid #00D09C; border-radius: 12px; padding: 10px;">
                <div style="font-size: 11px; font-weight: 800; color: #008764;">🛡️ Goal Health: 100% On Track</div>
                <div style="font-size: 9.5px; color: #475569; margin-top: 2px;">Short-term market dips have zero mathematical impact on your 2036 milestone.</div>
              </div>
            """
        },
        # Phone 4
        {
            "screen_title": "Key Takeaways for You",
            "step_title": "Learn the long view",
            "step_desc": "Review empirical data proving early drops don't hurt 2036.",
            "content_html": """
              <div style="display: flex; gap: 10px; align-items: flex-start;">
                <div style="width: 22px; height: 22px; background: #E6FBF5; border-radius: 50%; color: #008764; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">✓</div>
                <div>
                  <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">94% of 10-Yr SIPs Beat Inflation</div>
                  <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 2px;">Every historical Indian investor holding a 10-year equity SIP generated positive wealth.</div>
                </div>
              </div>
              <div style="display: flex; gap: 10px; align-items: flex-start;">
                <div style="width: 22px; height: 22px; background: #E6FBF5; border-radius: 50%; color: #008764; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">✓</div>
                <div>
                  <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">Noise today, wealth tomorrow</div>
                  <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 2px;">Month 4 drawdown is completely irrelevant to your 2036 milestone.</div>
                </div>
              </div>
              <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 12px; padding: 12px;">
                <div style="font-size: 11.5px; font-weight: 700; color: #92400E;">🎯 Recommended Action</div>
                <div style="font-size: 10px; color: #78350F; line-height: 1.4; margin-top: 4px;">
                  • Keep auto-debit active.<br/>
                  • Switch app reviews to quarterly milestone checks.
                </div>
              </div>
              <div class="primary-btn">Protect My Goal</div>
            """
        },
        # Phone 5
        {
            "screen_title": "Shield Activated",
            "step_title": "Stay goal-anchored",
            "step_desc": "Milestone shield locked in, switching app to quarterly reviews.",
            "content_html": """
              <div style="text-align: center; margin: 16px 0;">
                <div style="width: 58px; height: 58px; background: #6366F1; color: white; border-radius: 50%; font-size: 26px; font-weight: 800; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px;">🛡️</div>
                <div style="font-size: 15px; font-weight: 800; color: #0F172A;">Milestone Shield Active!</div>
                <div style="font-size: 10.5px; color: #64748B; line-height: 1.4; margin-top: 4px;">Your SIP is anchored to Child Education 2036. Daily market noise muted.</div>
              </div>
              <div class="card-box" style="margin-top: 10px;">
                <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">📅 Next Goal Review</div>
                <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 3px;">Scheduled in 90 days. We'll update your trajectory progression.</div>
              </div>
              <div style="text-align: center; font-size: 10.5px; font-weight: 700; color: #6366F1; margin-top: auto; padding-bottom: 8px;">View Full Milestone Plan ›</div>
            """
        }
    ]

    outcomes = [
        ("🎯", "Anchor SIP to<br/>emotional milestones"),
        ("📊", "Visualize 10-year<br/>trajectory cone"),
        ("🛡️", "Dampen short-term<br/>noise sensitivity"),
        ("👥", "Benchmark retention<br/>against 10-yr investors")
    ]

    html = build_slide_html(
        badge="Solution 2",
        title="Milestone Horizon Shield 🎯",
        subtitle="Connects short-term mutual fund market volatility directly to 10-year goal milestones, proving early dips have negligible impact on life goals.",
        focus="Anchor investors to long-term goals (Child Education, Home) so daily noise doesn't trigger impulsive cancellations.",
        phones=phones,
        outcomes=outcomes
    )
    render_html_to_png(html, "slide_solution_2_milestone_horizon_shield.png")


# ==============================================================================
# SLIDE 3: MARKET CYCLE TIME MACHINE
# ==============================================================================
def generate_slide_3():
    phones = [
        # Phone 1
        {
            "screen_title": "Groww Insights",
            "back_btn": '<span style="font-size: 14px; font-weight: 800;">←</span>',
            "step_title": "Spot the simulator",
            "step_desc": "See an interactive prompt during market crash days.",
            "content_html": """
              <div>
                <div style="font-size: 14px; font-weight: 800; color: #EF4444;">Sensex slips 850 pts</div>
                <div style="font-size: 10px; color: #64748B;">Market Volatility Alert</div>
              </div>
              <div style="background: #FFFBEB; border: 1.5px solid #FCD34D; border-radius: 12px; padding: 12px; margin-top: 8px;">
                <div style="font-size: 10px; font-weight: 800; color: #B45309;">⏳ CYCLE TIME MACHINE</div>
                <div style="font-size: 12px; font-weight: 800; color: #0F172A; margin-top: 3px;">Has this happened before?</div>
                <div style="font-size: 10px; color: #78350F; line-height: 1.35; margin-top: 3px;">See what happened to investors who started SIPs right before past market crashes.</div>
                <div style="font-size: 10px; font-weight: 700; color: #6366F1; margin-top: 6px;">Launch Historical Simulator ›</div>
              </div>
              <div class="card-box" style="margin-top: 8px;">
                <div style="font-size: 11px; font-weight: 700;">Historical Drawdown Facts</div>
                <div style="font-size: 10px; color: #64748B; margin-top: 2px;">Average recovery time: 7 months</div>
              </div>
            """
        },
        # Phone 2
        {
            "screen_title": "Select Crisis",
            "step_title": "Select historical crisis",
            "step_desc": "Choose 2020 COVID or 2022 to run empirical backtest.",
            "content_html": """
              <div style="text-align: center; margin: 8px 0;">
                <div style="font-size: 28px;">⏳</div>
                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin-top: 4px;">Select an Indian<br/>Market Crisis</div>
                <div style="font-size: 10px; color: #64748B; margin-top: 3px;">Test your fund against real market history.</div>
              </div>
              <div style="display: flex; flex-direction: column; gap: 8px;">
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: #EEF2FF; border-color: #6366F1;">
                  <span style="font-size: 11px; font-weight: 700; color: #1E1B4B;">2020 COVID Crash (-38%)</span>
                  <div style="width: 14px; height: 14px; border: 4px solid #6366F1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">2022 Global Rate Hikes (-15%)</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">2018 Mid-Cap Dip (-22%)</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">2008 Financial Crisis (-55%)</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
              </div>
              <div class="primary-btn">Run 3-Yr Simulation</div>
            """
        },
        # Phone 3
        {
            "screen_title": "2020 Crash Outcome",
            "step_title": "See dual-cohort outcome",
            "step_desc": "Compare investor who stopped vs disciplined compounder.",
            "content_html": """
              <div>
                <div style="font-size: 12px; font-weight: 800; color: #0F172A;">3-Year Outcome Comparison</div>
                <div style="font-size: 10px; color: #64748B;">Starting SIP: ₹1,000 / month</div>
              </div>
              <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 10px; padding: 10px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #EF4444;">❌ Investor A (Panicked & Stopped at Mo 3)</div>
                <div style="font-size: 9.5px; color: #0F172A; margin-top: 3px;">• Invested: ₹3,000 | Stopped in fear</div>
                <div style="font-size: 9.5px; color: #0F172A;">• Units Accumulated: 120 Units</div>
                <div style="font-size: 9.5px; font-weight: 700; color: #EF4444;">• Missed 110% recovery bull run</div>
              </div>
              <div style="background: #E6FBF5; border: 1px solid #00D09C; border-radius: 10px; padding: 10px;">
                <div style="font-size: 10.5px; font-weight: 800; color: #008764;">✅ Investor B (Stayed Disciplined)</div>
                <div style="font-size: 9.5px; color: #0F172A; margin-top: 3px;">• Invested: ₹36,000 over 3 Years</div>
                <div style="font-size: 9.5px; font-weight: 700; color: #008764;">• Units Accumulated: 412 Units (+243%!)</div>
                <div style="font-size: 9.5px; font-weight: 800; color: #008764;">• Portfolio Value: ₹68,500 (+22.4% CAGR)</div>
              </div>
            """
        },
        # Phone 4
        {
            "screen_title": "Key Takeaways for You",
            "step_title": "Learn the crash lesson",
            "step_desc": "Discover why every Indian crash rewarded SIP accumulators.",
            "content_html": """
              <div style="display: flex; gap: 10px; align-items: flex-start;">
                <div style="width: 22px; height: 22px; background: #E6FBF5; border-radius: 50%; color: #008764; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">✓</div>
                <div>
                  <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">Crashes create bonus units</div>
                  <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 2px;">Investor B accumulated 243% more units by buying through the red months.</div>
                </div>
              </div>
              <div style="display: flex; gap: 10px; align-items: flex-start;">
                <div style="width: 22px; height: 22px; background: #E6FBF5; border-radius: 50%; color: #008764; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">✓</div>
                <div>
                  <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">Timing the market fails beginners</div>
                  <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 2px;">Stopping locked in losses; auto-pilot delivered 22.4% compound growth.</div>
                </div>
              </div>
              <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 12px; padding: 12px;">
                <div style="font-size: 11.5px; font-weight: 700; color: #92400E;">💡 The Rule of Compounding</div>
                <div style="font-size: 10px; color: #78350F; line-height: 1.4; margin-top: 4px;">
                  • Treat market pullbacks as discount sales.<br/>
                  • Maintain monthly SIP contributions.
                </div>
              </div>
              <div class="primary-btn">Stay Disciplined</div>
            """
        },
        # Phone 5
        {
            "screen_title": "Simulator Saved",
            "step_title": "Stay supported",
            "step_desc": "Simulation saved to insights with automated instalment countdown.",
            "content_html": """
              <div style="text-align: center; margin: 16px 0;">
                <div style="width: 58px; height: 58px; background: #00D09C; color: white; border-radius: 50%; font-size: 26px; font-weight: 800; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px;">✓</div>
                <div style="font-size: 15px; font-weight: 800; color: #0F172A;">Conviction Reaffirmed!</div>
                <div style="font-size: 10.5px; color: #64748B; line-height: 1.4; margin-top: 4px;">Your 2020 Crash Simulation has been saved to your Insights tab for reference.</div>
              </div>
              <div class="card-box" style="margin-top: 10px;">
                <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">⏱️ Next Instalment Scheduled</div>
                <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 3px;">Nov 5th auto-debit active. Securing your next batch of discounted units.</div>
              </div>
              <div style="text-align: center; font-size: 10.5px; font-weight: 700; color: #6366F1; margin-top: auto; padding-bottom: 8px;">Return to Portfolio ›</div>
            """
        }
    ]

    outcomes = [
        ("⏳", "Demystify past market<br/>crashes with data"),
        ("⚖️", "Compare stopping vs<br/>continuing empirically"),
        ("📈", "Reframe drawdowns as<br/>high-alpha accumulation"),
        ("👥", "Boost 12-month retention<br/>through market cycles")
    ]

    html = build_slide_html(
        badge="Solution 3",
        title="Market Cycle Time Machine ⏳",
        subtitle="An interactive simulator that demonstrates how investors who started right before past crashes (2020 COVID, 2022) performed if they stayed vs stopped.",
        focus="Replace fear of the unknown with empirical proof that historical crashes rewarded disciplined SIP accumulators.",
        phones=phones,
        outcomes=outcomes
    )
    render_html_to_png(html, "slide_solution_3_market_cycle_time_machine.png")


# ==============================================================================
# SLIDE 4: SMART VOLATILITY BUFFER & FLEXIBLE SIP PAUSE
# ==============================================================================
def generate_slide_4():
    phones = [
        # Phone 1
        {
            "screen_title": "Manage SIP",
            "back_btn": '<span style="font-size: 14px; font-weight: 800;">←</span>',
            "step_title": "Intercept churn intent",
            "step_desc": "Trigger supportive options when user taps 'Cancel SIP'.",
            "content_html": """
              <div>
                <div style="font-size: 13px; font-weight: 800; color: #0F172A;">Nippon India Small Cap</div>
                <div style="font-size: 10.5px; color: #64748B;">Monthly SIP: ₹1,000 | Debit: 2nd</div>
              </div>
              <div style="background: #EFF6FF; border: 1.5px solid #BFDBFE; border-radius: 12px; padding: 12px; margin-top: 8px;">
                <div style="font-size: 10px; font-weight: 800; color: #1D4ED8;">🛡️ CHURN INTERCEPTION</div>
                <div style="font-size: 12px; font-weight: 800; color: #1E1B4B; margin-top: 3px;">Thinking of stopping?</div>
                <div style="font-size: 10px; color: #475569; line-height: 1.35; margin-top: 3px;">Cancelling breaks your compounding pace and requires re-doing bank mandates.</div>
                <div style="font-size: 10px; font-weight: 700; color: #1D4ED8; margin-top: 6px;">Explore Smart Pause Options ›</div>
              </div>
              <div class="card-box" style="margin-top: 8px;">
                <div style="font-size: 11px; font-weight: 700;">Mandate Health</div>
                <div style="font-size: 10px; color: #008764; font-weight: 600;">Active AutoPay • 0 Missed Debits</div>
              </div>
            """
        },
        # Phone 2
        {
            "screen_title": "Pause Diagnostic",
            "step_title": "Diagnose the friction",
            "step_desc": "Identify whether friction is cash shortage or market anxiety.",
            "content_html": """
              <div style="text-align: center; margin: 8px 0;">
                <div style="font-size: 28px;">❓</div>
                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin-top: 4px;">What's prompting<br/>your pause?</div>
                <div style="font-size: 10px; color: #64748B; margin-top: 3px;">We'll tailor the right flexibility support.</div>
              </div>
              <div style="display: flex; flex-direction: column; gap: 8px;">
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">Nervous about market drop</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: #EEF2FF; border-color: #6366F1;">
                  <span style="font-size: 11px; font-weight: 700; color: #1E1B4B;">Temporary cash crunch</span>
                  <div style="width: 14px; height: 14px; border: 4px solid #6366F1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">SIP date clashes with bills</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">Other personal reason</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
              </div>
              <div class="primary-btn">See Flexible Controls</div>
            """
        },
        # Phone 3
        {
            "screen_title": "Flexibility Controls",
            "step_title": "Select flexible relief",
            "step_desc": "Choose 30-day skip, date shift, or temporary micro-SIP.",
            "content_html": """
              <div>
                <div style="font-size: 12px; font-weight: 800; color: #0F172A;">Choose Your Relief Option:</div>
                <div style="font-size: 10px; color: #64748B;">Protect your 12-month compounding pace</div>
              </div>
              <div style="background: #E6FBF5; border: 1.5px solid #00D09C; border-radius: 10px; padding: 10px;">
                <div style="font-size: 10.5px; font-weight: 800; color: #008764;">[SELECTED] Option 1: 30-Day Grace Skip</div>
                <div style="font-size: 9.5px; font-weight: 700; color: #044332; margin-top: 2px;">• Skips next debit (₹0 NACH bounce fee)</div>
                <div style="font-size: 9px; color: #475569;">• Units continue growing; auto-resumes Dec</div>
              </div>
              <div class="card-box">
                <div style="font-size: 10.5px; font-weight: 700;">Option 2: Shift Date to Salary Day (7th)</div>
                <div style="font-size: 9px; color: #64748B;">Move deduction after paycheck clears.</div>
              </div>
              <div class="card-box">
                <div style="font-size: 10.5px; font-weight: 700;">Option 3: Halve to ₹500 for 2 Months</div>
                <div style="font-size: 9px; color: #64748B;">Reduce monthly commitment temporarily.</div>
              </div>
            """
        },
        # Phone 4
        {
            "screen_title": "Key Takeaways for You",
            "step_title": "Learn pause benefits",
            "step_desc": "See how smart pause saves your 12-month compounding.",
            "content_html": """
              <div style="display: flex; gap: 10px; align-items: flex-start;">
                <div style="width: 22px; height: 22px; background: #E6FBF5; border-radius: 50%; color: #008764; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">✓</div>
                <div>
                  <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">Zero Bank Penalty Guaranteed</div>
                  <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 2px;">Groww pauses the NACH mandate with your bank. No ₹450 bounce fee.</div>
                </div>
              </div>
              <div style="display: flex; gap: 10px; align-items: flex-start;">
                <div style="width: 22px; height: 22px; background: #E6FBF5; border-radius: 50%; color: #008764; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">✓</div>
                <div>
                  <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">Compounding stays active</div>
                  <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 2px;">Existing units stay invested and earn market returns uninterrupted.</div>
                </div>
              </div>
              <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 12px; padding: 12px;">
                <div style="font-size: 11.5px; font-weight: 700; color: #92400E;">🛡️ Stress-Free Relief</div>
                <div style="font-size: 10px; color: #78350F; line-height: 1.4; margin-top: 4px;">
                  • Take a 30-day breather stress-free.<br/>
                  • AutoPay restarts automatically in Dec.
                </div>
              </div>
              <div class="primary-btn" style="background: #00D09C; color: #044332; font-weight: 800;">Confirm 30-Day Pause</div>
            """
        },
        # Phone 5
        {
            "screen_title": "Pause Confirmed",
            "step_title": "Stay supported",
            "step_desc": "Pause active with auto-resume date; zero mandate deletion churn.",
            "content_html": """
              <div style="text-align: center; margin: 16px 0;">
                <div style="width: 58px; height: 58px; background: #00D09C; color: white; border-radius: 50%; font-size: 26px; font-weight: 800; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px;">🛡️</div>
                <div style="font-size: 15px; font-weight: 800; color: #0F172A;">SIP Safely Paused!</div>
                <div style="font-size: 10.5px; color: #64748B; line-height: 1.4; margin-top: 4px;">Your November debit is skipped with ₹0 fees. Existing units remain invested.</div>
              </div>
              <div class="card-box" style="margin-top: 10px;">
                <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">⏱️ Auto-Resume Scheduled</div>
                <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 3px;">Instalment auto-resumes on Dec 5th. No manual banking action needed.</div>
              </div>
              <div style="text-align: center; font-size: 10.5px; font-weight: 700; color: #6366F1; margin-top: auto; padding-bottom: 8px;">Manage SIP Settings ›</div>
            """
        }
    ]

    outcomes = [
        ("🛡️", "Eliminate bank NACH<br/>bounce penalty fears"),
        ("📅", "Align debits with<br/>salary credit cycles"),
        ("⚙️", "Prevent destructive<br/>binary cancellations"),
        ("👥", "Protect 12-month active<br/>retention through crunches")
    ]

    html = build_slide_html(
        badge="Solution 4",
        title="Smart Volatility Buffer 🛡️",
        subtitle="Replaces destructive SIP cancellations with a 1-click zero-penalty 30-day grace pause and automated salary-date alignment.",
        focus="Eliminate involuntary and panic churn caused by fear of ₹450 bank bounce penalties and salary delays.",
        phones=phones,
        outcomes=outcomes
    )
    render_html_to_png(html, "slide_solution_4_smart_volatility_buffer_pause.png")


# ==============================================================================
# SLIDE 5: SIP CONFIDENCE CHECK-IN
# ==============================================================================
def generate_slide_5():
    phones = [
        # Phone 1
        {
            "screen_title": "Portfolio",
            "back_btn": '<span style="font-size: 14px; font-weight: 800;">🔍</span>',
            "step_title": "Get a timely nudge",
            "step_desc": "See a simple check-in prompt on your portfolio.",
            "content_html": """
              <div style="display: flex; gap: 14px; font-size: 11.5px; font-weight: 700; color: #6366F1; border-bottom: 2px solid #F1F5F9; padding-bottom: 6px;">
                <span style="border-bottom: 2px solid #6366F1; padding-bottom: 6px;">Overview</span>
                <span style="color: #64748B;">Mutual Funds</span>
                <span style="color: #64748B;">Stocks</span>
              </div>
              <div>
                <div style="font-size: 11px; color: #64748B; font-weight: 600;">Total Portfolio Value</div>
                <div style="font-size: 22px; font-weight: 800; color: #0F172A; margin: 2px 0;">₹2,84,500</div>
                <div style="font-size: 11px; font-weight: 700; color: #EF4444;">▼ -3.8% (-₹11,300) <span style="font-weight: 500; color: #64748B;">1M</span></div>
              </div>
              <svg width="276" height="38" viewBox="0 0 276 38" fill="none">
                <path d="M0 8 C 50 12, 100 24, 150 18 C 200 12, 240 32, 276 35" stroke="#EF4444" stroke-width="2" fill="none"/>
              </svg>
              <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 12px; padding: 12px; display: flex; align-items: center; justify-content: space-between;">
                <div>
                  <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">📅 Your SIP Check-in is due</div>
                  <div style="font-size: 10px; color: #64748B; margin-top: 2px;">Take 30 seconds to tell us how you feel about your investments.</div>
                </div>
                <span style="font-size: 14px; font-weight: 800; color: #64748B;">›</span>
              </div>
              <div style="font-size: 11.5px; font-weight: 700; color: #0F172A; margin-top: 4px;">Your Investments (3)</div>
              <div class="card-box" style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                  <div style="font-size: 11px; font-weight: 700; color: #0F172A;">HDFC Flexi Cap Fund</div>
                  <div style="font-size: 10px; color: #64748B;">₹1,24,000 <span style="color: #EF4444; font-weight: 700;">-4.1%</span></div>
                </div>
                <span style="color: #94A3B8;">›</span>
              </div>
            """
        },
        # Phone 2
        {
            "screen_title": "SIP Confidence Check-in",
            "step_title": "Share your confidence",
            "step_desc": "Answer a quick, single question about how you feel.",
            "content_html": """
              <div style="text-align: center; margin: 8px 0;">
                <div style="font-size: 28px;">📋</div>
                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin-top: 4px;">How do you feel about<br/>your investment right now?</div>
                <div style="font-size: 10px; color: #64748B; margin-top: 3px;">This helps us understand your confidence and show you the right information.</div>
              </div>
              <div style="display: flex; flex-direction: column; gap: 8px;">
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">😊 Confident, I'm on track</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">😐 Slightly uncertain</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: #EEF2FF; border-color: #6366F1;">
                  <span style="font-size: 11px; font-weight: 700; color: #1E1B4B;">😟 Concerned about returns</span>
                  <div style="width: 14px; height: 14px; border: 4px solid #6366F1; border-radius: 50%;"></div>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 600;">❓ Need help understanding</span>
                  <div style="width: 14px; height: 14px; border: 1.5px solid #CBD5E1; border-radius: 50%;"></div>
                </div>
              </div>
              <div class="primary-btn">Continue</div>
            """
        },
        # Phone 3
        {
            "screen_title": "Here's what's happening",
            "step_title": "Get relevant insights",
            "step_desc": "Understand why your portfolio changed and what's driving it.",
            "content_html": """
              <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 12px; padding: 10px 12px;">
                <div style="font-size: 11px; font-weight: 700; color: #EF4444;">📉 Your portfolio is down 3.8% this month.</div>
                <div style="font-size: 9.5px; color: #64748B; margin-top: 2px;">Let's understand it better:</div>
              </div>
              <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 4px;">
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center;">
                  <div>
                    <div style="font-size: 11px; font-weight: 700;">📊 What's driving the change?</div>
                    <div style="font-size: 9.5px; color: #64748B;">Market, sector and fund impact</div>
                  </div>
                  <span style="color: #94A3B8;">›</span>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center;">
                  <div>
                    <div style="font-size: 11px; font-weight: 700;">⏱️ How does it look long term?</div>
                    <div style="font-size: 9.5px; color: #64748B;">Your performance over time</div>
                  </div>
                  <span style="color: #94A3B8;">›</span>
                </div>
                <div class="card-box" style="display: flex; justify-content: space-between; align-items: center;">
                  <div>
                    <div style="font-size: 11px; font-weight: 700;">📖 Key takeaways for you</div>
                    <div style="font-size: 9.5px; color: #64748B;">Simple, relevant insights</div>
                  </div>
                  <span style="color: #94A3B8;">›</span>
                </div>
              </div>
            """
        },
        # Phone 4
        {
            "screen_title": "Key Takeaways for You",
            "step_title": "Learn and take action",
            "step_desc": "See clear takeaways and next steps based on your response.",
            "content_html": """
              <div style="display: flex; gap: 10px; align-items: flex-start;">
                <div style="width: 22px; height: 22px; background: #E6FBF5; border-radius: 50%; color: #008764; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">✓</div>
                <div>
                  <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">This is a normal market movement</div>
                  <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 2px;">The broader market is down 2.6% this month, and some of the sectors in your funds were also affected.</div>
                </div>
              </div>
              <div style="display: flex; gap: 10px; align-items: flex-start;">
                <div style="width: 22px; height: 22px; background: #E6FBF5; border-radius: 50%; color: #008764; font-weight: 800; font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">✓</div>
                <div>
                  <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">Your long-term plan is intact</div>
                  <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 2px;">You're investing through SIP, which helps average out market ups and downs over time.</div>
                </div>
              </div>
              <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 12px; padding: 12px;">
                <div style="font-size: 11.5px; font-weight: 700; color: #92400E;">💡 What you can do</div>
                <div style="font-size: 10px; color: #78350F; line-height: 1.4; margin-top: 4px;">
                  • Stay invested if your financial goal and time horizon are intact.<br/>
                  • Review your goal or fund details if you're still unsure.
                </div>
              </div>
              <div class="primary-btn">Got it</div>
            """
        },
        # Phone 5
        {
            "screen_title": "Check-in Complete",
            "step_title": "Stay supported",
            "step_desc": "Check-in complete, with a reminder for the next one.",
            "content_html": """
              <div style="text-align: center; margin: 16px 0;">
                <div style="width: 58px; height: 58px; background: #00D09C; color: white; border-radius: 50%; font-size: 26px; font-weight: 800; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px;">✓</div>
                <div style="font-size: 15px; font-weight: 800; color: #0F172A;">Thanks for your input!</div>
                <div style="font-size: 10.5px; color: #64748B; line-height: 1.4; margin-top: 4px;">We'll use this to bring more relevant insights and support for you.</div>
              </div>
              <div class="card-box" style="margin-top: 10px;">
                <div style="font-size: 11.5px; font-weight: 700; color: #0F172A;">📅 Next check-in</div>
                <div style="font-size: 10px; color: #64748B; line-height: 1.35; margin-top: 3px;">In 30 days, we'll check in again to see how you're feeling.</div>
              </div>
              <div style="text-align: center; font-size: 10.5px; font-weight: 700; color: #6366F1; margin-top: auto; padding-bottom: 8px;">Update anytime in Settings ›</div>
            """
        }
    ]

    outcomes = [
        ("🔍", "Identify investor<br/>uncertainty early"),
        ("📖", "Provide relevant<br/>education & context"),
        ("📈", "Build confidence<br/>during market ups & downs"),
        ("👥", "Improve chances of SIP<br/>continuation for 12 months")
    ]

    html = build_slide_html(
        badge="Solution 5",
        title="SIP Confidence Check-in 💬",
        subtitle="A simple, periodic check-in to understand how investors feel about their investments and provide the right support before uncertainty turns into a SIP stop.",
        focus="Identify investor uncertainty early and give relevant support to keep them invested for 12 months.",
        phones=phones,
        outcomes=outcomes
    )
    render_html_to_png(html, "slide_solution_5_sip_confidence_checkin.png")


if __name__ == "__main__":
    print("Generating all 5 Pixel-Perfect HTML/CSS Presentation Slides...")
    generate_slide_1()
    generate_slide_2()
    generate_slide_3()
    generate_slide_4()
    generate_slide_5()
    print("All 5 Slides successfully generated with zero distortion!")
