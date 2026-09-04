#!/usr/bin/env python3
"""Render a static local SME inspector for workstation incidents and correlation decisions."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

INCIDENT_SCHEMA = "stegverse.workstation-incident/v1"
DECISION_SCHEMA = "stegverse.workstation-incident-correlation-decision/v1"


def load_json_files(directory: Path, schema: str) -> list[dict]:
    rows: list[dict] = []
    if not directory.exists():
        return rows
    for path in sorted(directory.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("schema") == schema:
            rows.append(record)
    return rows


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def render_incident(record: dict) -> str:
    classification = record.get("classification", {})
    observation = record.get("observation", {})
    root_cause = record.get("root_cause", {})
    workaround = record.get("workaround", {})
    fix = record.get("fix", {})
    return f"""
    <article class="incident">
      <h2>{esc(record.get('incident_id'))}</h2>
      <p><strong>Status:</strong> {esc(record.get('status'))}</p>
      <p><strong>Product:</strong> {esc(classification.get('vendor'))} / {esc(classification.get('product'))}</p>
      <p><strong>Platform:</strong> {esc(classification.get('platform'))}</p>
      <p><strong>Surface:</strong> {esc(classification.get('surface'))}</p>
      <p><strong>Summary:</strong> {esc(observation.get('summary'))}</p>
      <p><strong>Observed:</strong> {esc(observation.get('observed_behavior'))}</p>
      <p><strong>Root cause:</strong> {esc(root_cause.get('state'))} — {esc(root_cause.get('statement'))}</p>
      <p><strong>Workaround:</strong> {esc(workaround.get('state'))} — {esc(workaround.get('procedure'))}</p>
      <p><strong>Fix:</strong> {esc(fix.get('state'))} — {esc(fix.get('statement'))}</p>
      <details><summary>Machine record</summary><pre>{esc(json.dumps(record, indent=2, sort_keys=True))}</pre></details>
    </article>
    """


def render_decision(record: dict) -> str:
    return f"""
    <tr>
      <td>{esc(record.get('decision_id'))}</td>
      <td>{esc(record.get('left_incident_id'))}</td>
      <td>{esc(record.get('right_incident_id'))}</td>
      <td>{esc(record.get('candidate_score'))}</td>
      <td>{esc(record.get('decision'))}</td>
      <td>{esc(record.get('relationship'))}</td>
      <td>{esc(record.get('reason'))}</td>
    </tr>
    """


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--incident-dir", default="data/workstation-incidents")
    parser.add_argument(
        "--decision-dir",
        default="data/workstation-incident-correlation-decisions",
    )
    parser.add_argument("--output", default="reports/workstation-incident-inspector.html")
    args = parser.parse_args()

    incidents = load_json_files(Path(args.incident_dir), INCIDENT_SCHEMA)
    decisions = load_json_files(Path(args.decision_dir), DECISION_SCHEMA)
    incident_html = "\n".join(render_incident(record) for record in incidents)
    decision_html = "\n".join(render_decision(record) for record in decisions)

    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>StegVerse Workstation Incident Inspector</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }}
.incident {{ border: 1px solid #aaa; border-radius: .5rem; padding: 1rem; margin: 1rem 0; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #aaa; padding: .5rem; vertical-align: top; }}
pre {{ overflow-x: auto; white-space: pre-wrap; }}
</style>
</head>
<body>
<h1>Workstation Incident Inspector</h1>
<p>Local evidence/provenance inspection only. This report grants no publication, remediation, vendor, activation, or authority effect.</p>
<section>
<h2>Incidents</h2>
{incident_html or '<p>No incidents found.</p>'}
</section>
<section>
<h2>Correlation decisions</h2>
<table>
<thead><tr><th>ID</th><th>Left</th><th>Right</th><th>Score</th><th>Decision</th><th>Relationship</th><th>Reason</th></tr></thead>
<tbody>{decision_html}</tbody>
</table>
</section>
</body>
</html>
"""
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
