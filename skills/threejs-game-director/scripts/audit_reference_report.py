#!/usr/bin/env python3
"""Audit a Three.js game director final report for required skill evidence."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


BASE_REQUIRED = [
    "skill-loading ledger",
    "reference ledger",
    "phase ledger",
    "gameplay systems",
    "aaa graphics",
    "ui",
    "debug/profile",
    "qa/release",
]

PHYSICS_MARKERS = [
    "physics engine",
    "timestep",
    "collider",
    "sensor",
    "ccd",
]

# Ten scorecard categories that must carry a numeric score (0-3) in the report,
# not merely appear as headings. Matched as "<category> ... <digit>".
SCORECARD_CATEGORIES = [
    "art direction",
    "hero/player",
    "obstacles/enemies",
    "rewards/interactables",
    "world/environment",
    "materials/textures",
    "lighting/render",
    "vfx/motion",
    "ui/hud",
    "performance evidence",
]

PREMIUM_SCORECARD = [
    "art direction",
    "hero/player",
    "obstacles/enemies",
    "rewards/interactables",
    "world/environment",
    "materials/textures",
    "lighting/render",
    "vfx/motion",
    "ui/hud",
    "performance evidence",
    "average",
    "automatic failures",
]

PREMIUM_ASSET_SOURCING = [
    "external asset sourcing",
    "credential probe output",
    "alpha3d_api_key=",
    "3d generator",
    "image generator",
    "chosen sources",
    "hero/player",
    "world/sky/background",
    "materials/textures/decals",
]

# "audio" alone is a substring of "audio generator" (free). Require the ledger line
# plus real evidence (checked separately via has_audio_output_evidence / blocker).
PREMIUM_AUDIO = [
    "audio generator",
]

EXTERNAL_OUTPUT_PATTERNS = [
    # A concrete downloaded asset path under the project.
    re.compile(r"\b[\w./-]*assets/(models|concepts|textures|ui|images|audio)/[\w./-]+\.(glb|gltf|fbx|png|jpg|jpeg|webp|mp3|wav|ogg|m4a)\b"),
    # An Alpha3D integer job id (as printed by the client / MCP: "job 123").
    re.compile(r"\bjob[_ ]?id?\b[:=\s#]*\d+"),
    re.compile(r"\bjob\s+\d+\b"),
    # Other providers' UUID-style task ids.
    re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"),
]

AUDIO_OUTPUT_PATTERNS = [
    re.compile(r"\b[\w./-]*assets/audio/[\w./-]+\.(mp3|wav|ogg|m4a)\b"),
]

NON_CREDENTIAL_BLOCKER_MARKERS = [
    "api error",
    "network error",
    "quota",
    "offline-only",
    "offline only",
    "user requested no external",
    "no external ai",
    "no external assets",
]

VERIFICATION_MARKERS = [
    "build",
    "console",
    "page error",
    "desktop",
    "mobile",
    "screenshot",
    "canvas",
    "pixel",
]


def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("skill loading ledger", "skill-loading ledger")
    text = text.replace("skill loaded ledger", "skill-loading ledger")
    text = text.replace("reference loading ledger", "reference ledger")
    text = text.replace("asset sourcing ledger", "external asset sourcing")
    text = text.replace("external asset ledger", "external asset sourcing")
    text = text.replace("threejs-3d-generator", "3d generator")
    text = text.replace("threejs-image-generator", "image generator")
    text = text.replace("threejs-audio-generator", "audio generator")
    text = text.replace("alpha3d 3d assets", "3d generator")
    text = text.replace("alpha3d 3d generation", "3d generator")
    text = text.replace("phase-execution ledger", "phase ledger")
    text = text.replace("phase execution ledger", "phase ledger")
    text = text.replace("debug and profile", "debug/profile")
    text = text.replace("debug profile", "debug/profile")
    text = text.replace("qa and release", "qa/release")
    text = text.replace("qa release", "qa/release")
    text = text.replace("page errors", "page error")
    return re.sub(r"\s+", " ", text)


def missing_markers(text: str, markers: list[str]) -> list[str]:
    return [marker for marker in markers if marker not in text]


def has_external_output_evidence(text: str) -> bool:
    return any(pattern.search(text) for pattern in EXTERNAL_OUTPUT_PATTERNS)


def has_audio_output_evidence(text: str) -> bool:
    return any(pattern.search(text) for pattern in AUDIO_OUTPUT_PATTERNS)


def has_external_blocker(text: str) -> bool:
    both_credentials_missing = "alpha3d_api_key=missing" in text and "gemini_api_key=missing" in text
    non_credential_blocker = any(marker in text for marker in NON_CREDENTIAL_BLOCKER_MARKERS)
    return both_credentials_missing or non_credential_blocker


def scorecard_problems(text: str) -> list[str]:
    """Require numeric scores (values, not headings): >=8 of 10 categories scored,
    an explicit average >= 2.3, and no category below 2."""
    problems: list[str] = []
    scores: list[int] = []
    for category in SCORECARD_CATEGORIES:
        # "<category> ... N" or "<category> ... N/3" with limited filler in between.
        match = re.search(re.escape(category) + r"[^0-9\n]{0,16}([0-3])(?:\s*/\s*3)?", text)
        if match:
            scores.append(int(match.group(1)))
    if len(scores) < 8:
        problems.append("numeric scorecard scores for at least 8 of 10 categories "
                        f"(found {len(scores)})")
        return problems
    if any(score < 2 for score in scores):
        problems.append("a scorecard category scored below 2 (premium gate requires every category >= 2)")
    avg_match = re.search(r"average[^0-9\n]{0,16}([0-9](?:\.[0-9]+)?)", text)
    if not avg_match:
        problems.append("an explicit numeric scorecard average")
    elif float(avg_match.group(1)) < 2.3:
        problems.append(f"scorecard average >= 2.3 (found {avg_match.group(1)})")
    return problems


def has_audio_blocker(text: str) -> bool:
    return "elevenlabs_api_key=missing" in text or any(marker in text for marker in NON_CREDENTIAL_BLOCKER_MARKERS)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that a Three.js director final report includes required ledgers, scorecard, and verification evidence."
    )
    parser.add_argument("report", help="Path to the markdown/text final report draft.")
    parser.add_argument(
        "--premium",
        action="store_true",
        help="Require the premium/AAA visual scorecard and full verification evidence.",
    )
    parser.add_argument(
        "--physics",
        action="store_true",
        help="Require physics engine choice and diagnostics evidence.",
    )
    parser.add_argument(
        "--audio",
        action="store_true",
        help="Require generated/integrated audio evidence or a real blocker.",
    )
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Missing report file: {report_path}", file=sys.stderr)
        return 1

    text = normalize(report_path.read_text(encoding="utf-8"))
    missing = missing_markers(text, BASE_REQUIRED)

    if args.premium:
        missing.extend(missing_markers(text, PREMIUM_SCORECARD))
        # Values, not just headings: the scorecard must carry numeric scores,
        # an average >= 2.3, and no category below 2.
        missing.extend(scorecard_problems(text))
        missing.extend(missing_markers(text, PREMIUM_ASSET_SOURCING))
        missing.extend(missing_markers(text, VERIFICATION_MARKERS))
        # A screenshot claim must cite an actual image path, not just the word.
        if "screenshot" in text and not re.search(r"\.(png|jpg|jpeg|webp)\b", text):
            missing.append("a screenshot file path (e.g. .png), not just the word 'screenshot'")
        if not has_external_output_evidence(text) and not has_external_blocker(text):
            missing.append("real external asset evidence (asset path or job id) or a stated blocker")

    if args.physics:
        missing.extend(missing_markers(text, PHYSICS_MARKERS))

    if args.audio:
        missing.extend(missing_markers(text, PREMIUM_AUDIO))
        if not has_audio_output_evidence(text) and not has_audio_blocker(text):
            missing.append("real audio asset evidence or blocker")

    if missing:
        print("Director report audit failed. Missing required markers:")
        for marker in missing:
            print(f"- {marker}")
        return 1

    print("Director report audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
