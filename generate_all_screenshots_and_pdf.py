import os
import shutil
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

PROJECT_ROOT = Path(r"D:\SAURABH\Groww Discovery Engine")
OUTPUT_DIR = PROJECT_ROOT / "page_screenshots"
OUTPUT_DIR.mkdir(exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
LOCAL_URL = "http://127.0.0.1:8501"

print("--- Step 1: Capturing High-Resolution Screenshots of All Pages ---", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=CHROME_PATH,
        headless=True,
        args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
    )
    # Using 1920 width with device_scale_factor=2 for razor-sharp 4K text and visuals
    page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
    print(f"Connecting to {LOCAL_URL}...", flush=True)
    page.goto(LOCAL_URL, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_selector(".stApp", timeout=20000)
    page.wait_for_timeout(3500)

    def capture_full_current_page(filename: str):
        # Inject CSS to make container unconstrained vertically for full-page capture
        page.evaluate("""() => {
            let style = document.getElementById('full-page-screenshot-style');
            if (!style) {
                style = document.createElement('style');
                style.id = 'full-page-screenshot-style';
                document.head.appendChild(style);
            }
            style.innerHTML = `
                .stApp, [data-testid="stAppViewContainer"], section.main {
                    height: auto !important;
                    min-height: 100vh !important;
                    overflow: visible !important;
                }
            `;
        }""")
        page.wait_for_timeout(1000)

        # Calculate true document height
        full_h = page.evaluate("""() => {
            const block = document.querySelector('[data-testid="stMainBlockContainer"]');
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            const hBlock = block ? block.scrollHeight + 150 : 1080;
            const hSide = sidebar ? sidebar.scrollHeight + 150 : 1080;
            return Math.max(hBlock, hSide, 1080);
        }""")
        page.set_viewport_size({"width": 1920, "height": full_h})
        page.wait_for_timeout(1000)

        target_path = OUTPUT_DIR / filename
        page.screenshot(path=str(target_path), full_page=True)
        im = Image.open(target_path)
        print(f"Captured: {filename} -> Size: {im.size} ({im.size[0]}x{im.size[1]})", flush=True)

        # Reset viewport size for smooth navigation
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.wait_for_timeout(500)

    # 1. Overview
    print("Navigating to: Overview...", flush=True)
    page.locator('section[data-testid="stSidebar"] [role="radiogroup"] label').filter(has_text="Overview").click()
    page.wait_for_timeout(3000)
    capture_full_current_page("01_overview.png")

    # 2. Failure Themes
    print("Navigating to: Failure Themes...", flush=True)
    page.locator('section[data-testid="stSidebar"] [role="radiogroup"] label').filter(has_text="Failure Themes").click()
    page.wait_for_timeout(3000)
    capture_full_current_page("02_failure_themes.png")

    # 3. User Segments
    print("Navigating to: User Segments...", flush=True)
    page.locator('section[data-testid="stSidebar"] [role="radiogroup"] label').filter(has_text="User Segments").click()
    page.wait_for_timeout(3000)
    capture_full_current_page("03_user_segments.png")

    # 4. Opportunity Matrix - Bet 1 (Default active tab)
    print("Navigating to: Opportunity Matrix (Bet 1)...", flush=True)
    page.locator('section[data-testid="stSidebar"] [role="radiogroup"] label').filter(has_text="Opportunity Matrix").click()
    page.wait_for_timeout(3000)
    capture_full_current_page("04_opportunity_matrix_bet1.png")

    # 5. Opportunity Matrix - Bet 2
    print("Switching to: Opportunity Matrix (Bet 2)...", flush=True)
    role_tabs = page.locator('[role="tab"]')
    if role_tabs.count() >= 2:
        role_tabs.nth(1).click()
        page.wait_for_timeout(2000)
        capture_full_current_page("05_opportunity_matrix_bet2.png")

    # 6. Opportunity Matrix - Bet 3
    print("Switching to: Opportunity Matrix (Bet 3)...", flush=True)
    if role_tabs.count() >= 3:
        role_tabs.nth(2).click()
        page.wait_for_timeout(2000)
        capture_full_current_page("06_opportunity_matrix_bet3.png")

    # 7. RAG Assistant
    print("Navigating to: RAG Assistant...", flush=True)
    page.locator('section[data-testid="stSidebar"] [role="radiogroup"] label').filter(has_text="RAG Assistant").click()
    page.wait_for_timeout(3000)
    capture_full_current_page("07_rag_assistant.png")

    # 8. Engine Info
    print("Navigating to: Engine Info...", flush=True)
    page.locator('section[data-testid="stSidebar"] [role="radiogroup"] label').filter(has_text="Engine Info").click()
    page.wait_for_timeout(3000)
    capture_full_current_page("08_engine_info.png")

    browser.close()
    print("All browser screenshots captured!", flush=True)

# Copy Solution Slides to page_screenshots directory
solution_slides = [
    ("FINAL_SLIDE_1_Accumulation_Lens.png", "09_solution_1_accumulation_lens.png"),
    ("FINAL_SLIDE_2_Milestone_Horizon_Shield.png", "10_solution_2_milestone_shield.png"),
    ("FINAL_SLIDE_3_Market_Cycle_Time_Machine.png", "11_solution_3_cycle_time_machine.png"),
    ("FINAL_SLIDE_4_Smart_Volatility_Buffer.png", "12_solution_4_volatility_buffer.png"),
    ("FINAL_SLIDE_5_SIP_Confidence_Checkin.png", "13_solution_5_confidence_checkin.png"),
]

for src_name, dst_name in solution_slides:
    src_file = PROJECT_ROOT / src_name
    if src_file.exists():
        dst_file = OUTPUT_DIR / dst_name
        shutil.copy2(src_file, dst_file)
        print(f"Included Slide: {dst_name} from {src_name}", flush=True)

print("--- Step 2: Compiling High-Resolution PDF ---", flush=True)

image_files_ordered = [
    "01_overview.png",
    "02_failure_themes.png",
    "03_user_segments.png",
    "04_opportunity_matrix_bet1.png",
    "05_opportunity_matrix_bet2.png",
    "06_opportunity_matrix_bet3.png",
    "07_rag_assistant.png",
    "08_engine_info.png",
    "09_solution_1_accumulation_lens.png",
    "10_solution_2_milestone_shield.png",
    "11_solution_3_cycle_time_machine.png",
    "12_solution_4_volatility_buffer.png",
    "13_solution_5_confidence_checkin.png",
]

pil_images = []
for fname in image_files_ordered:
    fpath = OUTPUT_DIR / fname
    if fpath.exists():
        im = Image.open(fpath).convert("RGB")
        pil_images.append(im)
        print(f"Loaded for PDF: {fname} (dimensions: {im.size})", flush=True)
    else:
        print(f"Notice: {fname} not found, skipping.", flush=True)

pdf_output_path = PROJECT_ROOT / "ss of all page.pdf"
raw_name_path = PROJECT_ROOT / "ss of all page"

if pil_images:
    # Save as high-quality PDF with each page preserving exact dimensions
    pil_images[0].save(
        pdf_output_path,
        save_all=True,
        append_images=pil_images[1:],
        resolution=150.0,
        quality=95
    )
    print(f"Successfully generated: {pdf_output_path.resolve()}", flush=True)
    print(f"File size: {pdf_output_path.stat().st_size:,} bytes", flush=True)

    # Also copy to exact filename without extension requested by user
    shutil.copy2(pdf_output_path, raw_name_path)
    print(f"Created copy at: {raw_name_path.resolve()}", flush=True)
else:
    print("Error: No images were loaded for PDF generation!", flush=True)

print("--- COMPLETED SUCCESSFULLY ---", flush=True)

