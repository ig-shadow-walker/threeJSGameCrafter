#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pillow>=10.0.0",
#     "google-genai>=1.38.0",
# ]
# ///
"""Generate 2D image assets for Three.js games.

Default provider is Alpha3D (FLUX) via the /v1 REST API using ALPHA3D_API_KEY.
Pass --provider gemini to use Google's Gemini image API (GEMINI_API_KEY) instead.
If the Alpha3D MCP connector is available in your assistant, prefer calling the
MCP generate_image tool directly (no key needed) — this script is the API-key path.

Usage:
    uv run generate_image.py --prompt "..." --filename assets/concepts/out.png
    uv run generate_image.py --provider gemini --prompt "..." --filename out.png --resolution 2K
    uv run generate_image.py --input-image in.png --prompt "restyle to red livery" --filename out.png
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from io import BytesIO
from pathlib import Path
from urllib import error, request

ALPHA3D_DEFAULT_BASE = "https://api.alpha3d.io"
RETRYABLE_HTTP = {429, 500, 502, 503, 504}
MAX_RETRIES = 3


class ImageGenError(Exception):
    """Domain error for image generation failures."""


def _scrub(text: str, key: str | None) -> str:
    return text.replace(key, "***") if (key and text) else text


def _confined_output(filename: str) -> Path:
    path = Path(filename)
    resolved = path.resolve()
    try:
        resolved.relative_to(Path.cwd().resolve())
    except ValueError:
        print(f"WARNING: output path {resolved} is outside the current project; "
              f"writing there anyway.", file=sys.stderr)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _save_bytes(data: bytes, output_path: Path) -> None:
    """Save image bytes, converting to the extension the user asked for."""
    try:
        from PIL import Image as PILImage
    except ImportError:
        output_path.write_bytes(data)
        return
    image = PILImage.open(BytesIO(data))
    ext = output_path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        image.convert("RGB").save(output_path, "JPEG", quality=95)
    else:
        # PNG (default): preserve alpha if present.
        image.save(output_path, "PNG")


# --------------------------------------------------------------------------- #
# Alpha3D provider (default)
# --------------------------------------------------------------------------- #


def _alpha3d_request(url: str, key: str, body: dict, timeout: int = 120) -> dict:
    raw = json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        req = request.Request(url, data=raw, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=timeout) as resp:
                payload = resp.read()
            try:
                return json.loads(payload.decode("utf-8"))
            except (ValueError, UnicodeDecodeError) as exc:
                snippet = payload[:300].decode("utf-8", "replace")
                raise ImageGenError(f"Non-JSON response from {url}: {snippet}") from exc
        except error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read()[:400].decode("utf-8", "replace")
            except Exception:  # noqa: BLE001
                detail = ""
            if exc.code in RETRYABLE_HTTP and attempt < MAX_RETRIES - 1:
                last_exc = exc
                import time
                time.sleep(1.5 * (2 ** attempt))
                continue
            raise ImageGenError(f"HTTP {exc.code} from {url}: {detail}") from exc
        except (error.URLError, TimeoutError) as exc:
            if attempt < MAX_RETRIES - 1:
                last_exc = exc
                import time
                time.sleep(1.5 * (2 ** attempt))
                continue
            raise ImageGenError(f"Network error for {url}: {exc}") from exc
    raise ImageGenError(f"Request failed for {url}: {last_exc}")


def _alpha3d_resolution(resolution: str) -> str:
    # Alpha3D supports 1K and 1080p; map larger requests to 1080p.
    return "1K" if resolution == "1K" else "1080p"


def run_alpha3d(args, output_path: Path) -> None:
    key = args.api_key or os.environ.get("ALPHA3D_API_KEY")
    if not key:
        raise ImageGenError(
            "No Alpha3D API key. Pass --api-key or set ALPHA3D_API_KEY (run the "
            "credential probe first), or use --provider gemini, or call the Alpha3D "
            "MCP generate_image tool directly (no key needed).")
    base = (args.base_url or os.environ.get("ALPHA3D_API_BASE")
            or ALPHA3D_DEFAULT_BASE).rstrip("/")

    if args.input_image:
        src = Path(args.input_image)
        if not src.is_file():
            raise ImageGenError(f"Input image not found: {args.input_image}")
        body = {
            "prompt": args.prompt,
            "image_base64": base64.b64encode(src.read_bytes()).decode("ascii"),
        }
        if args.seed is not None:
            body["seed"] = args.seed
        data = _alpha3d_request(f"{base}/v1/images/transform", key, body)
    else:
        body = {"prompt": args.prompt, "ratio": args.ratio,
                "resolution": _alpha3d_resolution(args.resolution)}
        if args.seed is not None:
            body["seed"] = args.seed
        if args.static_enhancement:
            body["static_enhancement"] = True
        data = _alpha3d_request(f"{base}/v1/images/generate", key, body)

    b64 = data.get("image_base64")
    if not b64:
        raise ImageGenError(f"No image in Alpha3D response: {list(data)}")
    _save_bytes(base64.b64decode(b64), output_path)
    print(f"Image saved: {output_path.resolve()} (provider alpha3d)")


# --------------------------------------------------------------------------- #
# Gemini provider (alternate)
# --------------------------------------------------------------------------- #


def run_gemini(args, output_path: Path) -> None:
    key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ImageGenError("No Gemini API key. Pass --api-key or set GEMINI_API_KEY.")
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise ImageGenError(
            "google-genai is not installed; run via `uv run` or "
            "`pip install google-genai`.") from exc

    client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=120_000))
    contents = args.prompt
    if args.input_image:
        from PIL import Image as PILImage
        contents = [PILImage.open(args.input_image), args.prompt]

    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(image_size=args.resolution),
    )
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview", contents=contents, config=config)
    except Exception as exc:  # noqa: BLE001 - SDK may reject newer config fields
        # Retry once without image_config if the field/model is unsupported.
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview", contents=contents,
            config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]))
        print(f"Note: retried without image_config ({exc}).", file=sys.stderr)

    # X2: read candidates defensively and surface block/finish reasons.
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        reason = getattr(getattr(response, "prompt_feedback", None), "block_reason", None)
        raise ImageGenError(f"Gemini returned no candidates (block_reason={reason}).")
    parts = getattr(getattr(candidates[0], "content", None), "parts", None) or []
    for part in parts:
        inline = getattr(part, "inline_data", None)
        if inline is not None and inline.data:
            data = inline.data
            if isinstance(data, str):
                data = base64.b64decode(data)
            _save_bytes(data, output_path)
            print(f"Image saved: {output_path.resolve()} (provider gemini)")
            return
        if getattr(part, "text", None):
            print(f"Model response: {part.text}")
    finish = getattr(candidates[0], "finish_reason", None)
    raise ImageGenError(f"Gemini returned no image (finish_reason={finish}).")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate 2D image assets for Three.js games (Alpha3D FLUX by "
                    "default, Gemini alternate).")
    parser.add_argument("--prompt", "-p", required=True, help="image description")
    parser.add_argument("--filename", "-f", required=True, help="output path")
    parser.add_argument("--input-image", "-i", help="edit/transform this image")
    parser.add_argument("--provider", choices=["alpha3d", "gemini"], default="alpha3d")
    parser.add_argument("--resolution", "-r", choices=["1K", "2K", "4K"], default="1K",
                        help="Alpha3D maps 2K/4K to 1080p; Gemini uses the value as-is")
    parser.add_argument("--ratio", choices=["square", "portrait", "landscape"],
                        default="square", help="Alpha3D only")
    parser.add_argument("--seed", type=int, help="reproducibility seed")
    parser.add_argument("--static-enhancement", action="store_true",
                        help="Alpha3D: frame the image for the image-to-3D pipeline")
    parser.add_argument("--api-key", "-k", help="override the provider env key")
    parser.add_argument("--base-url", help="Alpha3D API base (else ALPHA3D_API_BASE)")
    args = parser.parse_args(argv)

    output_path = _confined_output(args.filename)
    key_for_scrub = (args.api_key or os.environ.get("ALPHA3D_API_KEY")
                     or os.environ.get("GEMINI_API_KEY"))
    try:
        if args.provider == "gemini":
            run_gemini(args, output_path)
        else:
            run_alpha3d(args, output_path)
        return 0
    except ImageGenError as exc:
        print(f"Error: {_scrub(str(exc), key_for_scrub)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
