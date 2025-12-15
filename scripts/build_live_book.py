# -*- coding: utf-8 -*-
"""
Records_AI – Auto Live Book Builder (UPAP-focused)

This script:
- Runs UPAP pipeline validation
- Normalizes the report structure
- Produces a simple text Live Book under ./live_book/
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime

from backend.services.upap.engine.upap_validation import build_pipeline_report


# =======================================================
# 1) Normalize report shape (dict / list karışıklığını düzelt)
# =======================================================
def normalize_report(raw_report):
    """
    Ensure we always work with a dict of:
      {
        "contract_reports": {stage_name: {...} or str},
        "runtime_reports": {stage_name: {...} or str},
        "overall_score": int
      }
    """
    report = raw_report

    # Eğer liste geldiyse (tek elemanlı bile olsa) ilkini al
    if isinstance(report, list):
        if not report:
            raise ValueError("UPAP report list is empty.")
        report = report[0]

    if not isinstance(report, dict):
        raise ValueError(f"UPAP report is not dict: {type(report)!r}")

    # contract_reports düzelt
    contract = report.get("contract_reports", {})
    contract = _normalize_stage_block(contract, prefix="stage")
    report["contract_reports"] = contract

    # runtime_reports düzelt
    runtime = report.get("runtime_reports", {})
    runtime = _normalize_stage_block(runtime, prefix="stage")
    report["runtime_reports"] = runtime

    # overall_score yoksa 0 yap
    if "overall_score" not in report:
        report["overall_score"] = 0

    return report


def _normalize_stage_block(block, prefix: str) -> dict:
    """
    Stage block, dict veya list olabilir.
    Çıktı her zaman dict olsun: {name: info}
    info dict değilse, "raw" alanına sar.
    """
    normalized = {}

    if isinstance(block, dict):
        for k, v in block.items():
            if isinstance(v, dict):
                normalized[str(k)] = v
            else:
                normalized[str(k)] = {"raw": str(v), "score": 0}
        return normalized

    if isinstance(block, list):
        for idx, item in enumerate(block, start=1):
            name = f"{prefix}_{idx}"
            if isinstance(item, dict):
                # stage/name alanı varsa onunla isimlendir
                stage_name = (
                    item.get("stage")
                    or item.get("name")
                    or item.get("stage_name")
                    or name
                )
                normalized[str(stage_name)] = item
            else:
                normalized[name] = {"raw": str(item), "score": 0}
        return normalized

    # Tanınmayan tip → boş dict
    return {}


# =======================================================
# 2) Human-readable text formatter
# =======================================================
def format_upap_report(report: dict) -> str:
    """
    Convert normalized UPAP validation report into readable plain text.
    Bu fonksiyon, contract/runtime bloklarındaki değerlerin hem dict hem string
    olabilmesini tolere eder.
    """
    lines: list[str] = []
    lines.append("=== UPAP VALIDATION REPORT ===")
    lines.append("")

    contract = report.get("contract_reports", {})
    runtime = report.get("runtime_reports", {})
    overall = report.get("overall_score", 0)

    # ---- Contract section ----
    lines.append(">> CONTRACT VALIDATION")
    if isinstance(contract, dict) and contract:
        for stage, info in contract.items():
            score = 0
            extra = ""
            if isinstance(info, dict):
                score = info.get("score", 0)
                if "notes" in info:
                    extra = f" | notes: {info['notes']}"
            else:
                # info string ise
                extra = f" | raw: {info!r}"
            lines.append(f"  - {stage}: {score}/100{extra}")
    else:
        lines.append("  (no contract data)")
    lines.append("")

    # ---- Runtime section ----
    lines.append(">> RUNTIME VALIDATION")
    if isinstance(runtime, dict) and runtime:
        for stage, info in runtime.items():
            score = 0
            extra = ""
            if isinstance(info, dict):
                score = info.get("score", 0)
                err = info.get("error")
                if err:
                    extra = f" | error: {err}"
            else:
                extra = f" | raw: {info!r}"
            lines.append(f"  - {stage}: {score}/100{extra}")
    else:
        lines.append("  (no runtime data)")
    lines.append("")

    lines.append(f">> OVERALL SCORE: {overall}/100")
    lines.append("")

    return "\n".join(lines)


# =======================================================
# 3) Main builder
# =======================================================
def main() -> None:
    print("=== Records_AI V2 – Building LIVE BOOK ===")
    print("[1/3] Running UPAP validation...")

    raw_report = build_pipeline_report()
    report = normalize_report(raw_report)
    upap_text = format_upap_report(report)

    print("[OK] UPAP validation processed.")
    print("[2/3] Writing Live Book file...")

    output_dir = Path("live_book")
    output_dir.mkdir(exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = output_dir / f"records_ai_live_book_{ts}.txt"

    with out_path.open("w", encoding="utf-8") as f:
        f.write(upap_text)

    print("[3/3] DONE.")
    print(f"Live Book created at: {out_path}")


if __name__ == "__main__":
    main()


def render_operational_readiness(upap_report: dict) -> str:
    """
    Render Operational Readiness section for Live Book.

    This section is auto-generated and reflects the CURRENT
    deploy eligibility state of the system.
    """

    score = upap_report.get("overall_score", 0)

    deploy_gate = "OPEN" if score >= 95 else "CLOSED"
    status = "HEALTHY" if score >= 95 else "DEGRADED"

    lines = []
    lines.append("=== OPERATIONAL READINESS ===")
    lines.append(f"Golden Level Target : 8")
    lines.append(f"UPAP Overall Score  : {score} / 100")
    lines.append(f"Deploy Gate         : {deploy_gate}")
    lines.append(f"UPAP Status         : {status}")
    lines.append(
        f"Generated At        : {datetime.utcnow().isoformat()}Z"
    )
    lines.append(
        "Reference           : Main Book / Section 8"
    )
    lines.append("")

    return "\n".join(lines)
