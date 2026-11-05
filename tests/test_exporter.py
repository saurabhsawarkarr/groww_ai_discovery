"""Unit and integration tests for Deliverables Synthesis & Export Center (Phase 8)."""

import json
from pathlib import Path
import pytest

from src.database.connection import get_db_path
from src.exporter.evidence_log import EvidenceLogGenerator
from src.exporter.export_all import export_all_deliverables, package_deliverable_1
from src.exporter.findings_report import FindingsReportGenerator
from src.exporter.slide_generator import SlideDiagramGenerator


@pytest.fixture
def test_db_path():
    """Return the active SQLite database path."""
    return get_db_path()


def test_findings_report_generation(test_db_path, tmp_path):
    """Test Deliverable 2 generator outputs comprehensive findings report."""
    generator = FindingsReportGenerator(db_path=test_db_path)
    out_file = tmp_path / "test_findings.md"
    content = generator.generate_report(output_path=out_file)

    assert out_file.exists()
    assert len(content) > 5000
    assert "# Deliverable 2: Discovery Findings Report" in content
    assert "Emergent Behavioral Clusters" in content
    assert "5-Pillar Opportunity Prioritization" in content
    assert "Targeted Primary Research Interview Protocol" in content
    assert "Segment Comparisons & Disclosed Data Gaps" in content


def test_evidence_log_generation(test_db_path, tmp_path):
    """Test Deliverable 3 generator outputs complete audit log with 7 dimensions & failure cases."""
    generator = EvidenceLogGenerator(db_path=test_db_path)
    out_file = tmp_path / "test_evidence_log.md"
    content = generator.generate_log(output_path=out_file)

    assert out_file.exists()
    assert len(content) > 4000
    assert "# Deliverable 3: AI Evidence Log & Evaluation Benchmark" in content
    assert "Curated Golden Set (20 Items) Side-by-Side Audit Table" in content
    assert "The 7 Mandated Agreement Dimensions" in content or "7 Agreement Dimensions" in content
    assert "Documented AI Failure Modes & Engineering Remediations" in content
    assert "Human-in-the-Loop Review Governance" in content


def test_slide_diagram_generation(test_db_path, tmp_path):
    """Test Deliverable 4 slide generator outputs PDF, SVG, and PNG files."""
    generator = SlideDiagramGenerator(db_path=test_db_path)
    pdf_path = tmp_path / "slide.pdf"
    svg_path = tmp_path / "slide.svg"
    png_path = tmp_path / "slide.png"

    paths = generator.generate_slide(
        output_pdf_path=pdf_path,
        output_svg_path=svg_path,
        output_png_path=png_path,
    )

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 10000

    assert svg_path.exists()
    assert svg_path.stat().st_size > 10000

    assert png_path.exists()
    assert png_path.stat().st_size > 10000


def test_deliverable_1_packaging(tmp_path):
    """Test Deliverable 1 packaging creates clean runnable directory with README and manifest."""
    project_root = Path(__file__).resolve().parent.parent
    target_dir = tmp_path / "Deliverable_1_Discovery_Engine_Codebase"

    manifest = package_deliverable_1(project_root, target_dir)

    assert target_dir.exists()
    assert (target_dir / "README.md").exists()
    assert (target_dir / "MANIFEST.json").exists()
    assert (target_dir / "run_pipeline.py").exists()
    assert (target_dir / "requirements.txt").exists()
    assert (target_dir / "src").is_dir()

    readme_text = (target_dir / "README.md").read_text(encoding="utf-8")
    assert "# Deliverable 1: Groww AI-Powered Discovery Engine" in readme_text
    assert "python run_pipeline.py" in readme_text
