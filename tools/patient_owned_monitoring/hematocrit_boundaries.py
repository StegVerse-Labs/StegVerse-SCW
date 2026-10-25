#!/usr/bin/env python3
"""Propose packed-cell and plasma boundaries from a capillary image profile.

Input is a JSON object containing either a one-dimensional ``profile`` of RGB
triples sampled from the sealed end toward plasma, or an ``image`` plus a
rectangular region and axis. Proposed coordinates never replace reviewed
coordinates; both are retained in the output.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path


def _sha256(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _rgb(v):
    if not isinstance(v, (list, tuple)) or len(v) != 3:
        raise ValueError("RGB sample must contain three channels")
    out = tuple(float(x) for x in v)
    if any(not math.isfinite(x) for x in out):
        raise ValueError("RGB channels must be finite")
    return out


def _profile_from_image(image, region, axis):
    if axis not in {"x", "y"}:
        raise ValueError("axis must be x or y")
    x0, y0, x1, y1 = (int(region[k]) for k in ("x0", "y0", "x1", "y1"))
    if x1 <= x0 or y1 <= y0:
        raise ValueError("region must have positive area")
    height = len(image)
    width = len(image[0]) if height else 0
    if x0 < 0 or y0 < 0 or x1 > width or y1 > height:
        raise ValueError("region outside image")
    result = []
    count = x1 - x0 if axis == "x" else y1 - y0
    for i in range(count):
        pixels = []
        if axis == "x":
            x = x0 + i
            pixels = [_rgb(image[y][x]) for y in range(y0, y1)]
        else:
            y = y0 + i
            pixels = [_rgb(image[y][x]) for x in range(x0, x1)]
        result.append(tuple(sum(p[c] for p in pixels) / len(pixels) for c in range(3)))
    return result


def load_profile(payload):
    if "profile" in payload:
        profile = [_rgb(v) for v in payload["profile"]]
    elif "image" in payload and "region" in payload:
        profile = _profile_from_image(payload["image"], payload["region"], payload.get("axis", "x"))
    else:
        raise ValueError("input requires profile or image plus region")
    if len(profile) < 6:
        raise ValueError("profile requires at least six samples")
    return profile


def _smooth(values, radius=1):
    out = []
    for i in range(len(values)):
        lo, hi = max(0, i-radius), min(len(values), i+radius+1)
        out.append(sum(values[lo:hi]) / (hi-lo))
    return out


def propose(profile):
    # Packed red cells are typically darker and more red-dominant than plasma.
    # The score is transparent and deliberately produces a proposal only.
    score = _smooth([(r - (g+b)/2.0) - 0.35*(r+g+b)/3.0 for r, g, b in profile], 1)
    gradients = [score[i+1] - score[i] for i in range(len(score)-1)]
    transition = min(range(1, len(score)-1), key=lambda i: gradients[i-1])

    # Tube end is proposed from the first sustained non-background intensity.
    intensity = _smooth([sum(rgb)/3.0 for rgb in profile], 1)
    lo, hi = min(intensity), max(intensity)
    threshold = lo + 0.10*(hi-lo)
    tube_start = next((i for i, v in enumerate(intensity) if v > threshold), 0)

    total_length = len(profile) - tube_start
    packed_length = max(0, transition - tube_start)
    proposed_hct = packed_length / total_length if total_length > 0 else None
    contrast = abs(gradients[transition-1]) if gradients else 0.0
    spread = max(score) - min(score)
    confidence = min(1.0, contrast / spread) if spread > 0 else 0.0
    return {
        "tube_start_index": tube_start,
        "packed_cell_plasma_boundary_index": transition,
        "profile_end_index": len(profile)-1,
        "proposed_hematocrit_fraction": proposed_hct,
        "transition_contrast": contrast,
        "proposal_confidence": confidence,
    }


def analyze(payload, source_sha256=None):
    profile = load_profile(payload)
    proposal = propose(profile)
    reviewed = payload.get("reviewed_coordinates")
    return {
        "schema_version": "pom.hematocrit-boundary-proposal.v1",
        "output_label": "experimentally_inferred",
        "source_sha256": source_sha256,
        "profile_samples": len(profile),
        "proposal": proposal,
        "reviewed_coordinates": reviewed,
        "review_required": True,
        "effective_coordinates": reviewed,
        "algorithm": {
            "name": "red-dominance-gradient-boundary-proposal",
            "version": "0.1.0",
            "smoothing_radius_samples": 1,
        },
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input_json")
    p.add_argument("output_json", nargs="?")
    args = p.parse_args()
    payload = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    result = analyze(payload, _sha256(args.input_json))
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output_json:
        Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
