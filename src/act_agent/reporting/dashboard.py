"""Generate a read-only, self-contained dashboard from canonical evidence."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def generate(root: Path) -> Path:
    ledger: dict[str, Any] = json.loads((root / "artifacts/run_state.json").read_text())
    baseline_path = root / "artifacts/e09_baseline_summary.json"
    baseline = json.loads(baseline_path.read_text()) if baseline_path.exists() else None
    verdict_path = root / "artifacts/final_verdict.json"
    verdict = json.loads(verdict_path.read_text()) if verdict_path.exists() else None
    access = json.loads((root / "artifacts/protected_access_ledger.json").read_text())
    states = [
        (
            name,
            str(item["state"]),
            str(item.get("name", name)),
            str(item["reason"]),
        )
        for name, item in ledger["stages"].items()
    ]
    stage_rows = "\n".join(
        "<tr data-state='{}'><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            *(html.escape(value, quote=True) for value in (state, name, state, title, reason))
        )
        for name, state, title, reason in states
    )
    if baseline:
        model_rows = "\n".join(
            "<tr><td>{}</td><td>{}/{}</td><td>{}/{}</td><td>{}/{}</td></tr>".format(
                html.escape(model),
                values["success"],
                values["n"],
                values["process_compliant"],
                values["n"],
                values["critical_violations"],
                values["n"],
            )
            for model, values in baseline["models"].items()
        )
        pilot = f"{baseline['paired_tasks']} paired synthetic development tasks"
    else:
        model_rows = "<tr><td colspan='4'>No complete paired baseline evidence</td></tr>"
        pilot = "No complete paired baseline evidence"
    decision = verdict["decision"] if verdict else "Pending final audit"
    output = root / "dashboards/index.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ACT-Agent evidence dashboard</title>
<style>
body{{font:16px system-ui,sans-serif;max-width:1200px;margin:2rem auto;padding:0 1rem;background:#f5f7fa;color:#172536}}
h1,h2{{line-height:1.2}}main{{display:grid;gap:1.2rem}}section{{background:white;border:1px solid #d5dce5;border-radius:10px;padding:1rem;overflow:auto}}
table{{border-collapse:collapse;width:100%}}th,td{{padding:.5rem;text-align:left;border-bottom:1px solid #dde3eb;vertical-align:top}}
th{{background:#ebf0f5}}button{{margin:.2rem;padding:.4rem .7rem;border:1px solid #8aa2bb;border-radius:5px;background:white;cursor:pointer}}
button[aria-pressed="true"]{{background:#173b63;color:white}}.notice{{border-left:4px solid #ab6911;padding-left:.8rem}}
</style></head><body><main>
<header><h1>ACT-Agent v1.0 evidence</h1><p>Protocol {html.escape(ledger["protocol"])} · Scientific decision: <strong>{html.escape(decision)}</strong></p></header>
<section><h2>Evidence boundary</h2><p class="notice">Mutable campaign effects and tasks are synthetic. Development model results are diagnostic while E07 is REVIEW. Empty protected or external results mean unexecuted, not zero.</p>
<p>Protected internal outcome access: {access["internal_outcome_access"]}; external benchmark outcome access: {access["external_benchmark_outcome_access"]}.</p></section>
<section><h2>B0–B2 development pilot</h2><p>{html.escape(pilot)}</p><table><thead><tr><th>Model</th><th>Completed</th><th>Process compliant</th><th>Critical attempted violations</th></tr></thead><tbody>{model_rows}</tbody></table>
<p><a href="../reports/baseline_development.md">Method and limitations</a> · <a href="../artifacts/e09_baseline_summary.json">Canonical summary</a></p></section>
<section><h2>Stage ledger</h2><div id="filters"><button type="button" data-filter="ALL" aria-pressed="true">All</button><button type="button" data-filter="PASS">PASS</button><button type="button" data-filter="REVIEW">REVIEW</button><button type="button" data-filter="PENDING">PENDING</button><button type="button" data-filter="CLOSED">CLOSED</button><button type="button" data-filter="BLOCKED_EXTERNAL">BLOCKED_EXTERNAL</button></div>
<table><thead><tr><th>Stage</th><th>State</th><th>Name</th><th>Reason</th></tr></thead><tbody id="stages">{stage_rows}</tbody></table></section>
<footer><a href="../reports/final_technical_report.md">Final technical report</a> · <a href="../artifacts/claim_ledger.json">Claim ledger</a></footer>
</main><script>
const buttons=[...document.querySelectorAll('[data-filter]')];
for(const button of buttons)button.addEventListener('click',()=>{{
  const selected=button.dataset.filter;
  for(const item of buttons)item.setAttribute('aria-pressed',String(item===button));
  for(const row of document.querySelectorAll('#stages tr'))row.hidden=selected!=='ALL'&&row.dataset.state!==selected;
}});
</script></body></html>
"""
    )
    return output


if __name__ == "__main__":
    print(generate(Path.cwd()))
