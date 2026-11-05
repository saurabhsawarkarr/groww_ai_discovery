"""Synchronizes all slide images, busts browser cache with clean FINAL filenames,
and creates an interactive, standalone HTML presentation gallery viewer.
"""

from pathlib import Path
import shutil
import subprocess

PROJECT_ROOT = Path(r"D:\SAURABH\Groww Discovery Engine")
DELIVERABLES_SCREENS = PROJECT_ROOT / "deliverables" / "screens"
BRAIN_SCREENS = Path(r"C:\Users\KAUSTUBH\.gemini\antigravity\brain\708df285-86a7-405f-be3f-5a6d8dc3d597\screens")

SLIDE_MAPPING = [
    ("slide_solution_1_accumulation_lens.png", "FINAL_SLIDE_1_Accumulation_Lens.png", "solution_1_accumulation_lens.png", "flow_solution_1_accumulation_lens.png"),
    ("slide_solution_2_milestone_horizon_shield.png", "FINAL_SLIDE_2_Milestone_Horizon_Shield.png", "solution_2_milestone_horizon_shield.png", "flow_solution_2_milestone_horizon_shield.png"),
    ("slide_solution_3_market_cycle_time_machine.png", "FINAL_SLIDE_3_Market_Cycle_Time_Machine.png", "solution_3_market_cycle_time_machine.png", "flow_solution_3_market_cycle_time_machine.png"),
    ("slide_solution_4_smart_volatility_buffer_pause.png", "FINAL_SLIDE_4_Smart_Volatility_Buffer.png", "solution_4_smart_volatility_buffer_pause.png", "flow_solution_4_smart_volatility_buffer_pause.png"),
    ("slide_solution_5_sip_confidence_checkin.png", "FINAL_SLIDE_5_SIP_Confidence_Checkin.png", "solution_5_contextual_movement_attributor.png", "flow_solution_5_contextual_movement_attributor.png"),
]

print("Syncing slide images across all target filenames...")
for src_name, final_name, legacy_sol, legacy_flow in SLIDE_MAPPING:
    src_file = DELIVERABLES_SCREENS / src_name
    if not src_file.exists():
        print(f"Warning: {src_name} not found!")
        continue
    
    # 1. Create clean FINAL_SLIDE file in deliverables/screens
    final_file = DELIVERABLES_SCREENS / final_name
    shutil.copy2(src_file, final_file)
    
    # 2. Overwrite legacy files so older links now show the clean slide
    shutil.copy2(src_file, DELIVERABLES_SCREENS / legacy_sol)
    shutil.copy2(src_file, DELIVERABLES_SCREENS / legacy_flow)
    
    # 3. Copy to Brain Screens dir as well
    shutil.copy2(src_file, BRAIN_SCREENS / src_name)
    shutil.copy2(src_file, BRAIN_SCREENS / final_name)
    shutil.copy2(src_file, BRAIN_SCREENS / legacy_sol)
    shutil.copy2(src_file, BRAIN_SCREENS / legacy_flow)
    
    # 4. Copy directly to project root for instant access
    shutil.copy2(src_file, PROJECT_ROOT / final_name)
    print(f"Synced: {final_name} (Size: {final_file.stat().st_size} bytes)")

# Create an Interactive Standalone HTML Presentation Viewer in Project Root
gallery_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Groww - 5 Solution Presentation Slides</title>
<style>
  body {
    margin: 0;
    padding: 24px;
    background: #0F172A;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #F8FAFC;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .nav-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    background: #1E293B;
    padding: 8px 14px;
    border-radius: 14px;
    border: 1px solid #334155;
    position: sticky;
    top: 16px;
    z-index: 100;
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);
  }
  .nav-btn {
    background: #334155;
    color: #94A3B8;
    border: none;
    padding: 10px 18px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
  }
  .nav-btn:hover { background: #475569; color: white; }
  .nav-btn.active { background: #00D09C; color: #044332; }

  .slide-container {
    width: 100%;
    max-width: 1440px;
    background: #1E293B;
    border-radius: 20px;
    border: 1px solid #334155;
    padding: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    margin-bottom: 40px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .slide-header {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    padding: 0 8px;
  }
  .slide-title { font-size: 20px; font-weight: 800; color: #00D09C; }
  .slide-sub { font-size: 13.5px; color: #94A3B8; }
  .slide-img {
    width: 100%;
    height: auto;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  }
</style>
</head>
<body>

  <h1 style="margin: 0 0 6px; font-size: 26px; font-weight: 800; color: #FFFFFF;">
    Groww Mutual Funds • 5 Market Fluctuation Solution Flows
  </h1>
  <p style="margin: 0 0 20px; color: #94A3B8; font-size: 14.5px;">
    Pixel-perfect 16:9 presentation slides matching the sample layout with 5-phone user flows.
  </p>

  <div class="nav-bar">
    <button class="nav-btn active" onclick="showSlide(1)">1. Accumulation Lens</button>
    <button class="nav-btn" onclick="showSlide(2)">2. Horizon Shield</button>
    <button class="nav-btn" onclick="showSlide(3)">3. Cycle Time Machine</button>
    <button class="nav-btn" onclick="showSlide(4)">4. Volatility Buffer</button>
    <button class="nav-btn" onclick="showSlide(5)">5. SIP Confidence Check-in</button>
  </div>

  <!-- SLIDE 1 -->
  <div class="slide-container" id="slide-1">
    <div class="slide-header">
      <div class="slide-title">Solution 1: The Accumulation Lens (Year-1 Discount Unit Mode)</div>
      <div class="slide-sub">Reframes drawdowns into bonus unit accumulation</div>
    </div>
    <img class="slide-img" src="deliverables/screens/FINAL_SLIDE_1_Accumulation_Lens.png" alt="Solution 1" />
  </div>

  <!-- SLIDE 2 -->
  <div class="slide-container" id="slide-2" style="display: none;">
    <div class="slide-header">
      <div class="slide-title">Solution 2: Milestone Horizon Shield (Goal-Anchored Pacing)</div>
      <div class="slide-sub">Visualizes 10-year trajectory cone to neutralize short-term noise</div>
    </div>
    <img class="slide-img" src="deliverables/screens/FINAL_SLIDE_2_Milestone_Horizon_Shield.png" alt="Solution 2" />
  </div>

  <!-- SLIDE 3 -->
  <div class="slide-container" id="slide-3" style="display: none;">
    <div class="slide-header">
      <div class="slide-title">Solution 3: Market Cycle Time Machine (Historical Simulator)</div>
      <div class="slide-sub">Empirical comparison of stopping vs maintaining SIP through past crashes</div>
    </div>
    <img class="slide-img" src="deliverables/screens/FINAL_SLIDE_3_Market_Cycle_Time_Machine.png" alt="Solution 3" />
  </div>

  <!-- SLIDE 4 -->
  <div class="slide-container" id="slide-4" style="display: none;">
    <div class="slide-header">
      <div class="slide-title">Solution 4: Smart Volatility Buffer & Flexible SIP Pause</div>
      <div class="slide-sub">1-click 30-day grace skip (₹0 bank bounce fees) to eliminate churn</div>
    </div>
    <img class="slide-img" src="deliverables/screens/FINAL_SLIDE_4_Smart_Volatility_Buffer.png" alt="Solution 4" />
  </div>

  <!-- SLIDE 5 -->
  <div class="slide-container" id="slide-5" style="display: none;">
    <div class="slide-header">
      <div class="slide-title">Solution 5: SIP Confidence Check-in & Contextual Attributor</div>
      <div class="slide-sub">Proactive pulse check explaining macro, sector & fund movements</div>
    </div>
    <img class="slide-img" src="deliverables/screens/FINAL_SLIDE_5_SIP_Confidence_Checkin.png" alt="Solution 5" />
  </div>

  <script>
    function showSlide(num) {
      for (let i = 1; i <= 5; i++) {
        document.getElementById('slide-' + i).style.display = (i === num) ? 'flex' : 'none';
      }
      const btns = document.querySelectorAll('.nav-btn');
      btns.forEach((b, idx) => {
        b.classList.toggle('active', (idx + 1) === num);
      });
      window.scrollTo({ top: 120, behavior: 'smooth' });
    }
  </script>
</body>
</html>
"""

viewer_path = PROJECT_ROOT / "view_solution_slides.html"
viewer_path.write_text(gallery_html, encoding="utf-8")
print(f"Created Gallery Viewer at: {viewer_path.resolve()}")

