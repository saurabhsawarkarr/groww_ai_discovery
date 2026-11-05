"""Comprehensive Exporter CLI generating Deliverables 1 through 4.

Orchestrates the synthesis and export of all 4 mandatory assignment deliverables:
1. Deliverable 1: Runnable Engine Codebase package with clean README & manifest.
2. Deliverable 2: Discovery Findings Report (Deliverable_2_Discovery_Findings.md).
3. Deliverable 3: AI Evidence Log & Benchmark (Deliverable_3_AI_Evidence_Log.md).
4. Deliverable 4: Executive One-Slide Workflow Diagram (Deliverable_4_One_Slide_Workflow.pdf/svg/png).
"""

import argparse
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import shutil
import sys
from typing import Any, Dict, Optional, Union

from src.database.connection import get_db_path
from src.exporter.evidence_log import EvidenceLogGenerator
from src.exporter.findings_report import FindingsReportGenerator
from src.exporter.slide_generator import SlideDiagramGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("groww_discovery.exporter.export_all")


def package_deliverable_1(
    project_root: Path,
    target_dir: Path,
) -> Dict[str, Any]:
    """Package the runnable discovery engine codebase with clean instructions."""
    target_dir.mkdir(parents=True, exist_ok=True)

    # Folders and files to include in Deliverable 1
    include_dirs = ["src", "configs", "tests", "data/golden_set"]
    include_files = [
        "pyproject.toml",
        "requirements.txt",
        ".env.example",
        "run_pipeline.py",
    ]

    copied_items = []

    for d in include_dirs:
        src_path = project_root / d
        dst_path = target_dir / d
        if src_path.exists():
            if dst_path.exists():
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
            copied_items.append(d)

    for f in include_files:
        src_path = project_root / f
        dst_path = target_dir / f
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            copied_items.append(f)

    # Generate polished README for Deliverable 1
    readme_content = f"""# Deliverable 1: Groww AI-Powered Discovery Engine

> **Project:** Senior PM Discovery Assignment — Mutual Fund SIP 12-Month Retention  
> **Strategic Metric:** 12-Month First-Time Mutual Fund SIP Continuation Rate  
> **Architecture Standard:** 7-Stage Pipeline with Verbatim Quote Extraction & TDD Benchmark Gate  
> **Package Date:** {datetime.now().strftime('%B %d, %Y')}

---

## 1. Executive Summary & Engine Overview

The **Groww AI-Powered Discovery Engine** is an enterprise-grade qualitative research platform that systematically harvests, sanitizes, extracts, clusters, and prioritizes user friction and behavioral patterns from public discourse (Play Store, App Store, Reddit, YouTube) without anchoring on preconceived biases.

Built to address the strategic challenge of improving **12-month mutual fund SIP continuation**, the engine operates under strict epistemic guardrails:
1. **100% Verbatim Quote Exactness:** Rejects any hallucinated or paraphrased text. Every evidence quote is verified as an exact contiguous substring of the raw post.
2. **Epistemic Humility (§9.4):** Explicitly marks unstated demographics as `unknown`. Never fabricates investor segments.
3. **Contradictory Counter-Evidence:** Uncovers resilient investors who continued their SIP despite experiencing the same friction.
4. **Transparent 5-Pillar Prioritization:** Qualitatively evaluates candidate opportunities across Prevalence, User Impact, 12M SIP Relevance, Evidence Quality, and Product Addressability.

---

## 2. Quickstart & Single CLI Execution

### 2.1 Prerequisites & Installation
Ensure Python 3.10+ is installed:

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\\.venv\\Scripts\\activate

# 2. Install dependencies
pip install -r requirements.txt
```

### 2.2 End-to-End Pipeline Execution (Single Command)
Execute the complete 7-stage workflow — from ingestion and sanitization through clustering, hypothesis synthesis, and deliverables export:

```bash
python run_pipeline.py
```

Optional CLI flags:
```bash
python run_pipeline.py --help
# Options:
#   --skip-ingestion   Use existing SQLite dataset without re-harvesting
#   --db-path PATH     Custom SQLite database location
#   --output-dir DIR   Output folder for generated deliverables (default: deliverables/)
#   --verbose          Enable verbose debug logging
```

### 2.3 Interactive Streamlit Research Dashboard
Launch the Growth PM research workspace for quote inspection and human-in-the-loop review:

```bash
streamlit run src/ui/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser:
- **Tab 1 (Evidence Explorer):** Search and filter 155+ qualified records by platform and journey stage with 1-click quote traceability to raw URLs.
- **Tab 2 (Thematic Clusters):** Interactive radar and prevalence distribution across 8 emergent behavioral themes with counter-evidence quotes.
- **Tab 3 (Opportunity Matrix):** 5-pillar qualitative evaluation matrix and semi-structured 1:1 user interview protocol generators.
- **Tab 4 (Golden Set & Audit):** 7-dimension agreement benchmark, live Golden Set inspection, and diagnostic AI failure logs.

---

## 3. Test Suite Verification

Run the automated test suite covering all 8 pipeline modules:

```bash
pytest -v
```
All tests enforce strict data contracts, Pydantic validation schemas, exact substring guardrails, and deterministic scoring.

---

## 4. Repository Structure & Module Architecture

```text
Deliverable_1_Discovery_Engine_Codebase/
├── run_pipeline.py                 # Single root CLI entry point
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project packaging specifications
├── configs/
│   ├── config.yaml                 # Pipeline hyperparameters & weights
│   └── pii_patterns.json           # Regex patterns for PII scrubbing
├── data/
│   └── golden_set/                 # 20-item human ground-truth benchmark
├── src/
│   ├── connectors/                 # Play Store, App Store, Reddit, YouTube, CSV
│   ├── preprocessing/              # PII masking, SHA-256 deduplication, qualification
│   ├── extraction/                 # 21-field Pydantic schema & substring guardrail
│   ├── evaluation/                 # 7 agreement metrics & diagnostic failure logger
│   ├── clustering/                 # Embeddings, UMAP projection & HDBSCAN themes
│   ├── hypotheses/                 # Competing hypotheses (A/B) & 5-pillar ranker
│   ├── ui/                         # Streamlit Growth PM dashboard
│   ├── database/                   # SQLite connection & 8-table relational schema
│   └── exporter/                   # Deliverables synthesis & export center
└── tests/                          # 65+ unit & integration test suite
```

---

## 5. Artifact Manifest & Verification

| Deliverable | File Path | Format | Description |
|---|---|:---:|---|
| **Deliverable 1** | `Deliverable_1_Discovery_Engine_Codebase/` | Package | Fully runnable discovery engine with root CLI |
| **Deliverable 2** | `Deliverable_2_Discovery_Findings.md` | Markdown | Comprehensive findings, 8 themes, hypotheses |
| **Deliverable 3** | `Deliverable_3_AI_Evidence_Log.md` | Markdown | Golden Set audit, 7 agreement metrics, failure logs |
| **Deliverable 4** | `Deliverable_4_One_Slide_Workflow.pdf` | PDF / SVG | 16:9 executive workflow slide for final presentation |

---
*Developed for Groww Growth Engineering & Product Teams.*
"""

    with open(target_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Manifest file
    manifest = {
        "deliverable": "Deliverable 1: Working AI Discovery Engine Codebase",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "entry_point": "run_pipeline.py",
        "included_modules": copied_items,
        "database_backend": "SQLite3",
        "dashboard_entry": "streamlit run src/ui/app.py",
    }
    with open(target_dir / "MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.info("Packaged Deliverable 1 to %s", str(target_dir))
    return manifest


def export_all_deliverables(
    project_root: Optional[Union[str, Path]] = None,
    output_dir: Optional[Union[str, Path]] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, str]:
    """Execute end-to-end export of Deliverables 1, 2, 3, and 4."""
    root = Path(project_root) if project_root else Path(__file__).resolve().parent.parent.parent
    out_dir = Path(output_dir) if output_dir else root / "deliverables"
    out_dir.mkdir(parents=True, exist_ok=True)
    database_path = get_db_path(db_path)

    logger.info("Starting synthesis of all Part 1 Mandated Deliverables...")
    logger.info("Target Output Directory: %s", str(out_dir))
    logger.info("Source SQLite Database: %s", str(database_path))

    results = {}

    # 1. Deliverable 1: Packaged Codebase
    d1_dir = out_dir / "Deliverable_1_Discovery_Engine_Codebase"
    logger.info("[1/4] Packaging Deliverable 1 (Engine Codebase & CLI)...")
    package_deliverable_1(root, d1_dir)
    results["Deliverable 1 (Codebase)"] = str(d1_dir)

    # 2. Deliverable 2: Discovery Findings Report
    d2_file = out_dir / "Deliverable_2_Discovery_Findings.md"
    logger.info("[2/4] Generating Deliverable 2 (Discovery Findings Report)...")
    findings_gen = FindingsReportGenerator(db_path=database_path)
    findings_gen.generate_report(output_path=d2_file)
    results["Deliverable 2 (Findings Report)"] = str(d2_file)

    # 3. Deliverable 3: AI Evidence Log & Evaluation Benchmark
    d3_file = out_dir / "Deliverable_3_AI_Evidence_Log.md"
    logger.info("[3/4] Generating Deliverable 3 (AI Evidence Log & Benchmark)...")
    evidence_gen = EvidenceLogGenerator(db_path=database_path)
    evidence_gen.generate_log(output_path=d3_file)
    results["Deliverable 3 (AI Evidence Log)"] = str(d3_file)

    # 4. Deliverable 4: Executive One-Slide Workflow Diagram
    d4_pdf = out_dir / "Deliverable_4_One_Slide_Workflow.pdf"
    d4_svg = out_dir / "Deliverable_4_One_Slide_Workflow.svg"
    d4_png = out_dir / "Deliverable_4_One_Slide_Workflow.png"
    logger.info("[4/4] Generating Deliverable 4 (Executive 16:9 One-Slide Workflow)...")
    slide_gen = SlideDiagramGenerator(db_path=database_path)
    slide_gen.generate_slide(
        output_pdf_path=d4_pdf,
        output_svg_path=d4_svg,
        output_png_path=d4_png,
    )
    results["Deliverable 4 (Workflow Slide PDF)"] = str(d4_pdf)
    results["Deliverable 4 (Workflow Slide SVG)"] = str(d4_svg)
    results["Deliverable 4 (Workflow Slide PNG)"] = str(d4_png)

    # Print Summary Table
    print("\n" + "=" * 80)
    print("  GROWW AI DISCOVERY ENGINE -- DELIVERABLES SYNTHESIS COMPLETE")
    print("=" * 80)
    for title, path_str in results.items():
        p = Path(path_str)
        if p.is_dir():
            size_str = f"{len(list(p.rglob('*')))} files"
        elif p.exists():
            size_kb = p.stat().st_size / 1024
            size_str = f"{size_kb:.1f} KB"
        else:
            size_str = "N/A"
        print(f"  [OK] {title:<36} -> {p.name:<34} ({size_str})")
    print("=" * 80 + "\n")

    return results


def main():
    """CLI entry point for exporting all deliverables."""
    parser = argparse.ArgumentParser(
        description="Generate all 4 mandated assignment deliverables for Groww Discovery Engine."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save generated deliverables (default: deliverables/)",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="Custom SQLite database path",
    )
    args = parser.parse_args()
    export_all_deliverables(output_dir=args.output_dir, db_path=args.db_path)


if __name__ == "__main__":
    main()
