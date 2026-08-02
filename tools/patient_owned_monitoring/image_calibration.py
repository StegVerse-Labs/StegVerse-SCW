#!/usr/bin/env python3
"""Calibrate fixed-light RGB images and sample corrected rectangular regions.

The portable input format is JSON so the module has no external image-library
requirement. Pixel data is a row-major array of [r, g, b] triplets. Calibration
patches identify rectangular image regions and their reference RGB values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable, Sequence

RGB = tuple[float, float, float]


def _sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _validate_pixels(pixels: Sequence[Sequence[Sequence[float]]]) -> tuple[int, int]:
    if not pixels or not pixels[0]:
        raise ValueError("pixel matrix must be non-empty")
    width = len(pixels[0])
    for row in pixels:
        if len(row) != width:
            raise ValueError("pixel rows must have equal width")
        for pixel in row:
            if len(pixel) != 3:
                raise ValueError("every pixel must contain exactly three channels")
            if any(float(channel) < 0 or float(channel) > 255 for channel in pixel):
                raise ValueError("pixel channels must be between 0 and 255")
    return width, len(pixels)


def mean_region(pixels: Sequence[Sequence[Sequence[float]]], region: Sequence[int]) -> RGB:
    width, height = _validate_pixels(pixels)
    if len(region) != 4:
        raise ValueError("region must be [x0, y0, x1, y1]")
    x0, y0, x1, y1 = (int(value) for value in region)
    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
        raise ValueError("region lies outside image bounds or is empty")
    values = [pixels[y][x] for y in range(y0, y1) for x in range(x0, x1)]
    count = len(values)
    return tuple(sum(float(pixel[channel]) for pixel in values) / count for channel in range(3))  # type: ignore[return-value]


def _fit_affine(observed: Iterable[float], reference: Iterable[float]) -> tuple[float, float, float]:
    xs = [float(value) for value in observed]
    ys = [float(value) for value in reference]
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("at least two calibration observations are required")
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denominator = sum((value - x_mean) ** 2 for value in xs)
    if denominator == 0:
        raise ValueError("calibration observations have no channel variation")
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator
    intercept = y_mean - slope * x_mean
    rmse = (sum((slope * x + intercept - y) ** 2 for x, y in zip(xs, ys)) / len(xs)) ** 0.5
    return slope, intercept, rmse


def fit_calibration(pixels, patches: Sequence[dict]) -> dict:
    if len(patches) < 2:
        raise ValueError("at least two calibration patches are required")
    observed: list[RGB] = []
    references: list[RGB] = []
    patch_results = []
    for patch in patches:
        measured = mean_region(pixels, patch["region"])
        reference = tuple(float(value) for value in patch["reference_rgb"])
        if len(reference) != 3:
            raise ValueError("reference_rgb must contain three channels")
        observed.append(measured)
        references.append(reference)  # type: ignore[arg-type]
        patch_results.append({"patch_id": patch.get("patch_id"), "observed_rgb": measured, "reference_rgb": reference})

    channels = []
    names = ("r", "g", "b")
    for index, name in enumerate(names):
        slope, intercept, rmse = _fit_affine((rgb[index] for rgb in observed), (rgb[index] for rgb in references))
        channels.append({"channel": name, "slope": slope, "intercept": intercept, "fit_rmse": rmse})
    return {"model": "per-channel-affine", "version": "1.0.0", "channels": channels, "patches": patch_results}


def correct_rgb(rgb: Sequence[float], calibration: dict) -> RGB:
    corrected = []
    for value, channel in zip(rgb, calibration["channels"]):
        result = channel["slope"] * float(value) + channel["intercept"]
        corrected.append(min(255.0, max(0.0, result)))
    return tuple(corrected)  # type: ignore[return-value]


def calibrate_document(document: dict) -> dict:
    pixels = document["pixels"]
    _validate_pixels(pixels)
    calibration = fit_calibration(pixels, document["calibration_patches"])
    samples = []
    for sample in document.get("sample_regions", []):
        observed = mean_region(pixels, sample["region"])
        samples.append({
            "sample_id": sample["sample_id"],
            "region": sample["region"],
            "observed_rgb": observed,
            "corrected_rgb": correct_rgb(observed, calibration),
            "output_label": "calculated",
        })
    return {
        "schema_version": "pom.image-calibration.v1",
        "calibration": calibration,
        "samples": samples,
        "quality": {
            "patch_count": len(document["calibration_patches"]),
            "maximum_channel_fit_rmse": max(channel["fit_rmse"] for channel in calibration["channels"]),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json")
    parser.add_argument("output_json")
    args = parser.parse_args()
    with open(args.input_json, encoding="utf-8") as handle:
        document = json.load(handle)
    result = calibrate_document(document)
    result["source_sha256"] = _sha256(args.input_json)
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"status": "COMPLETE", "output": args.output_json, "samples": len(result["samples"])}, separators=(",", ":")))


if __name__ == "__main__":
    main()
