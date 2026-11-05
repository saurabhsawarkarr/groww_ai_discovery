"""HTML/CSS Slide Renderer using Headless Chrome.
Generates pixel-perfect, crisp, beautifully aligned 16:9 presentation slides matching Figma design.
"""

from pathlib import Path
import subprocess

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_DIR = Path("deliverables/screens")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BRAIN_DIR = Path(r"C:\Users\KAUSTUBH\.gemini\antigravity\brain\708df285-86a7-405f-be3f-5a6d8dc3d597\screens")
BRAIN_DIR.mkdir(parents=True, exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1920px;
    height: 1080px;
    background: #F8FAFC;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #0F172A;
    padding: 36px 48px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }

  /* Header Section */
  .header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    height: 110px;
  }
  .header-left {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .brand-row {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .groww-logo {
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
  }
  .groww-text {
    font-size: 26px;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.5px;
  }
  .solution-badge {
    background: #EEF2FF;
    border: 1px solid #C7D2FE;
    color: #4F46E5;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.3px;
  }
  .slide-title {
    font-size: 30px;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.8px;
    margin-top: 4px;
  }
  .slide-subtitle {
    font-size: 14.5px;
    color: #475569;
    max-width: 880px;
    line-height: 1.4;
  }
  .focus-box {
    background: #EDE9FE;
    border: 1px solid #DDD6FE;
    border-radius: 16px;
    padding: 18px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    max-width: 580px;
  }
  .focus-icon {
    width: 44px;
    height: 44px;
    background: #DDD6FE;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: #5B21B6;
    flex-shrink: 0;
  }
  .focus-text {
    font-size: 14px;
    font-weight: 700;
    color: #1E1B4B;
    line-height: 1.45;
  }

  /* 5 Phones Flow Section */
  .flow-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    margin-top: 10px;
  }
  .phone-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 310px;
  }

  /* Phone Mockup Frame */
  .phone-frame {
    width: 304px;
    height: 520px;
    background: #FFFFFF;
    border: 3.5px solid #0F172A;
    border-radius: 36px;
    box-shadow: 0 16px 36px -10px rgba(15, 23, 42, 0.15), 0 0 0 1px rgba(15, 23, 42, 0.05);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    position: relative;
  }
  .notch {
    position: absolute;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    width: 76px;
    height: 14px;
    background: #0F172A;
    border-radius: 10px;
    z-index: 10;
  }
  .status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 22px 6px;
    font-size: 11px;
    font-weight: 700;
    color: #0F172A;
  }
  .app-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 18px 12px;
    border-bottom: 1px solid #F1F5F9;
  }
  .app-header-title {
    font-size: 13.5px;
    font-weight: 700;
    color: #0F172A;
  }
  .screen-content {
    flex: 1;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    overflow: hidden;
    background: #FFFFFF;
  }

  .chevron {
    font-size: 26px;
    font-weight: 800;
    color: #A5B4FC;
    margin-top: -80px;
  }

  /* Step Descriptions under phones */
  .step-info {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-top: 16px;
    width: 290px;
  }
  .step-number {
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
  }
  .step-title {
    font-size: 14px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 3px;
  }
  .step-desc {
    font-size: 11.5px;
    color: #64748B;
    line-height: 1.35;
  }

  /* Common UI Elements inside phones */
  .pill-tag {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
  }
  .pill-green { background: #E6FBF5; color: #008764; }
  .pill-red { background: #FEF2F2; color: #DC2626; }
  .pill-purple { background: #EEF2FF; color: #4F46E5; }

  .card-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 10px 12px;
  }

  .primary-btn {
    background: #6366F1;
    color: white;
    text-align: center;
    padding: 11px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 12.5px;
    margin-top: auto;
  }
  .primary-btn-green {
    background: #00D09C;
    color: #044332;
    text-align: center;
    padding: 11px;
    border-radius: 10px;
    font-weight: 800;
    font-size: 12.5px;
    margin-top: auto;
  }

  /* Bottom Outcome Bar */
  .outcome-bar {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    padding: 16px 28px;
    display: flex;
    align-items: center;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
  }
  .outcome-pill {
    background: #00D09C;
    color: white;
    font-weight: 800;
    font-size: 15px;
    padding: 7px 18px;
    border-radius: 20px;
    margin-right: 32px;
  }
  .outcome-grid {
    display: flex;
    align-items: center;
    flex: 1;
    justify-content: space-between;
  }
  .outcome-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-right: 28px;
    border-right: 1px solid #E2E8F0;
  }
  .outcome-item:last-child {
    border-right: none;
    padding-right: 0;
  }
  .outcome-icon {
    width: 34px;
    height: 34px;
    background: #E6FBF5;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    color: #008764;
    font-weight: 800;
  }
  .outcome-text {
    font-size: 13.5px;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.25;
  }
</style>
</head>
<body>

  <!-- HEADER -->
  <div class="header">
    <div class="header-left">
      <div class="brand-row">
        <div class="groww-logo">G</div>
        <span class="groww-text">Groww</span>
        <span class="solution-badge">{solution_badge}</span>
      </div>
      <div class="slide-title">{title}</div>
      <div class="slide-subtitle">{subtitle}</div>
    </div>
    <div class="focus-box">
      <div class="focus-icon">🎯</div>
      <div class="focus-text">Focus: {focus_text}</div>
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

def generate_chrome_slide(html_content, output_png_name):
    temp_html = Path(r"C:\temp\slide_temp.html")
    temp_html.write_text(html_content, encoding="utf-8")
    
    out_path_1 = OUTPUT_DIR / output_png_name
    out_path_2 = BRAIN_DIR / output_png_name
    
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1920,1080",
        f"--screenshot={out_path_1.resolve()}",
        f"file:///{temp_html.resolve()}".replace("\\", "/")
    ]
    subprocess.run(cmd, check=True)
    
    # Also copy to brain dir
    import shutil
    shutil.copy2(out_path_1, out_path_2)
    print(f"Generated pixel-perfect slide: {output_png_name}")

