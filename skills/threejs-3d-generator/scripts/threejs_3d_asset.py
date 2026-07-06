#!/usr/bin/env python3
"""Alpha3D /v1 client for generating Three.js game assets (Path B — API key).

Submit → poll → download against the Alpha3D public API. For the MCP connector
path (no API key), call the Alpha3D MCP tools directly instead; see
references/mcp-integration.md. Any other provider with the same job shape can be
adapted from this client.

Auth:  Authorization: Bearer <ALPHA3D_API_KEY>   (key looks like ak_live_...)
Base:  https://api.alpha3d.io   (override with ALPHA3D_API_BASE); routes under /v1

Design notes (hardening):
- Polling is driven off an explicit ONGOING set; unknown statuses keep polling
  until timeout, never terminate early.
- HTTP helpers retry with backoff on transient network / 429 / 5xx only.
- Downloads are atomic (.part -> os.replace) so a crash never leaves a truncated
  model file.
- The API key is scrubbed from any error surfaced to stdout/stderr.
- Output paths are resolved and a warning is printed if they escape the CWD tree.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path
from urllib import error, request

DEFAULT_BASE = "https://api.alpha3d.io"
API_PREFIX = "/v1"

ONGOING_STATUSES = {"queued", "processing", "pending", "running", "starting"}
SUCCESS_STATUSES = {"succeeded", "success", "completed", "complete"}
FAILURE_STATUSES = {"failed", "error", "banned", "cancelled", "canceled", "expired"}

RETRYABLE_HTTP = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.5

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MODEL_EXTS = {".glb", ".gltf", ".obj", ".fbx", ".usdz", ".stl"}
MAX_UPLOAD_BYTES = 60 * 1024 * 1024  # 60MB ceiling for local uploads

DEFAULT_TIMEOUT = 900
DEFAULT_POLL_INTERVAL = 20


class Alpha3DError(Exception):
    """Domain error raised for all client-side and API failures."""


# --------------------------------------------------------------------------- #
# HTTP layer
# --------------------------------------------------------------------------- #


def _scrub(text: str, key: str | None) -> str:
    if not text:
        return text
    if key:
        text = text.replace(key, "***")
    return text


def _sleep_backoff(attempt: int) -> None:
    time.sleep(RETRY_BASE_DELAY * (2 ** attempt))


def _parse_json(raw: bytes, context: str) -> dict:
    try:
        return json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        snippet = raw[:300].decode("utf-8", "replace")
        raise Alpha3DError(f"{context}: non-JSON response ({exc}): {snippet}") from exc


def _request(
    method: str,
    url: str,
    key: str | None,
    *,
    body: dict | None = None,
    raw_body: bytes | None = None,
    content_type: str | None = None,
    extra_headers: dict | None = None,
    timeout: int = 120,
    expect_json: bool = True,
):
    """Perform an HTTP request with bounded retry on transient failures."""
    headers = {"Accept": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    if body is not None:
        raw_body = json.dumps(body).encode("utf-8")
        content_type = "application/json"
    if content_type:
        headers["Content-Type"] = content_type
    if extra_headers:
        headers.update(extra_headers)

    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        req = request.Request(url, data=raw_body, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=timeout) as resp:
                payload = resp.read()
            if expect_json:
                return _parse_json(payload, f"{method} {url}")
            return payload
        except error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read()[:500].decode("utf-8", "replace")
            except Exception:  # noqa: BLE001 - best-effort detail
                detail = ""
            if exc.code in RETRYABLE_HTTP and attempt < MAX_RETRIES - 1:
                last_exc = exc
                _sleep_backoff(attempt)
                continue
            raise Alpha3DError(f"HTTP {exc.code} for {method} {url}: {detail}") from exc
        except (error.URLError, TimeoutError) as exc:
            if attempt < MAX_RETRIES - 1:
                last_exc = exc
                _sleep_backoff(attempt)
                continue
            raise Alpha3DError(f"Network error for {method} {url}: {exc}") from exc
    raise Alpha3DError(f"Request failed for {method} {url}: {last_exc}")


# --------------------------------------------------------------------------- #
# API client
# --------------------------------------------------------------------------- #


class Client:
    def __init__(self, key: str, base: str):
        self.key = key
        self.base = base.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self.base}{API_PREFIX}{path}"

    def submit_job(self, body: dict) -> dict:
        headers = {"Idempotency-Key": uuid.uuid4().hex}
        data = _request("POST", self._url("/jobs"), self.key, body=body,
                        extra_headers=headers)
        return _job_view(data)

    def get_job(self, job_id) -> dict:
        data = _request("GET", self._url(f"/jobs/{job_id}"), self.key)
        return _job_view(data)

    def list_jobs(self, limit: int = 20) -> dict:
        return _request("GET", self._url(f"/jobs?limit={limit}"), self.key)

    def usage(self) -> dict:
        return _request("GET", self._url("/usage"), self.key)

    def presign(self, file_name: str, kind: str, content_type: str | None) -> dict:
        body = {"file_name": file_name, "kind": kind}
        if content_type:
            body["content_type"] = content_type
        return _request("POST", self._url("/uploads/presign"), self.key, body=body)

    def upload_local(self, local_path: str, kind: str) -> str:
        """Presign, PUT the bytes, and return the file_url to reference in a job."""
        path = Path(local_path)
        if not path.is_file():
            raise Alpha3DError(f"File not found: {local_path}")
        ext = path.suffix.lower()
        allowed = IMAGE_EXTS if kind == "image" else MODEL_EXTS
        if ext not in allowed:
            raise Alpha3DError(
                f"Unsupported {kind} extension {ext!r}; allowed: {sorted(allowed)}")
        size = path.stat().st_size
        if size > MAX_UPLOAD_BYTES:
            raise Alpha3DError(
                f"{local_path} is {size} bytes; exceeds {MAX_UPLOAD_BYTES}-byte upload ceiling")
        ct = _content_type_for(ext)
        signed = self.presign(path.name, kind, ct)
        upload_url = signed.get("upload_url")
        file_url = signed.get("file_url")
        if not upload_url or not file_url:
            raise Alpha3DError(f"Presign response missing upload_url/file_url: {signed}")
        _request("PUT", upload_url, key=None, raw_body=path.read_bytes(),
                 content_type=ct, expect_json=False, timeout=300)
        return file_url

    def resolve_source(self, local_or_url: str, kind: str) -> str:
        """Return a usable URL: upload local files, pass through https URLs."""
        if local_or_url.startswith("http://") or local_or_url.startswith("https://"):
            return local_or_url
        return self.upload_local(local_or_url, kind)

    def wait(self, job_id, timeout: int, interval: int) -> dict:
        deadline = time.monotonic() + timeout
        job = self.get_job(job_id)
        while True:
            status = str(job.get("status", "")).lower()
            if status in SUCCESS_STATUSES:
                return job
            if status in FAILURE_STATUSES:
                raise Alpha3DError(
                    f"Job {job_id} ended as {status!r}: {job.get('error') or 'no detail'}")
            # ONGOING or unrecognized -> keep polling until timeout.
            if time.monotonic() >= deadline:
                raise Alpha3DError(
                    f"Timed out waiting for job {job_id} after {timeout}s (last status "
                    f"{status!r}). The job keeps running server-side; resume with: "
                    f"status {job_id}  /  download {job_id}")
            stage = job.get("stage")
            print(f"  job {job_id}: {status}{f' ({stage})' if stage else ''}...",
                  file=sys.stderr)
            time.sleep(interval)
            job = self.get_job(job_id)


def _job_view(data: dict) -> dict:
    """Accept either a bare job object or a {job: ...} / {data: {post: ...}} wrapper."""
    if not isinstance(data, dict):
        raise Alpha3DError(f"Unexpected job response: {data!r}")
    for key in ("job", "post"):
        if key in data and isinstance(data[key], dict):
            return data[key]
    if "data" in data and isinstance(data["data"], dict):
        return _job_view(data["data"])
    return data


def _content_type_for(ext: str) -> str:
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".webp": "image/webp", ".glb": "model/gltf-binary", ".gltf": "model/gltf+json",
        ".obj": "application/octet-stream", ".fbx": "application/octet-stream",
        ".usdz": "model/vnd.usdz+zip", ".stl": "model/stl",
    }.get(ext, "application/octet-stream")


# --------------------------------------------------------------------------- #
# Downloads
# --------------------------------------------------------------------------- #


def _safe_out_dir(out_dir: str) -> Path:
    path = Path(out_dir).resolve()
    cwd = Path.cwd().resolve()
    try:
        path.relative_to(cwd)
    except ValueError:
        print(f"WARNING: output path {path} is outside the current project "
              f"({cwd}); writing there anyway.", file=sys.stderr)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _download(url: str, dest: Path) -> None:
    tmp = dest.with_suffix(dest.suffix + ".part")
    payload = _request("GET", url, key=None, expect_json=False, timeout=300)
    tmp.write_bytes(payload)
    os.replace(tmp, dest)


def download_outputs(job: dict, out_dir: str, fmt: str | None) -> list[str]:
    outputs = job.get("outputs") or {}
    if not outputs:
        raise Alpha3DError(f"Job {job.get('id')} has no outputs; status "
                           f"{job.get('status')!r}")
    target = _safe_out_dir(out_dir)
    job_id = job.get("id", "asset")
    written: list[str] = []

    if fmt:
        key = fmt.lower()
        url = outputs.get(key)
        if not url:
            raise Alpha3DError(f"No {fmt!r} output on job {job_id}; available: "
                               f"{sorted(outputs)}")
        keys = [key]
    else:
        # Prefer a loadable mesh; always grab a thumbnail if present.
        preferred = ["glb", "textured_mesh", "mesh", "obj", "fbx"]
        keys = [k for k in preferred if k in outputs][:1]
        keys += [k for k in outputs if k.startswith("part_")]
        if "thumbnail" in outputs:
            keys.append("thumbnail")
        if not keys:
            keys = list(outputs)

    for key in keys:
        url = outputs[key]
        ext = _ext_for_output(key, url)
        dest = target / f"{job_id}_{key}{ext}"
        _download(url, dest)
        written.append(str(dest))
        print(f"  downloaded {key} -> {dest}")
    return written


def _ext_for_output(key: str, url: str) -> str:
    if key == "thumbnail":
        return ".png"
    if key == "obj":
        return ".obj"
    if key == "fbx":
        return ".fbx"
    # part_* and mesh/glb default to .glb
    base = url.split("?", 1)[0]
    for known in (".glb", ".gltf", ".obj", ".fbx", ".stl", ".png", ".jpg"):
        if base.lower().endswith(known):
            return known
    return ".glb"


# --------------------------------------------------------------------------- #
# Command handlers
# --------------------------------------------------------------------------- #


def _finish(client: Client, job: dict, args) -> int:
    print(f"Submitted job {job.get('id')} (type {job.get('type')}, "
          f"status {job.get('status')}).")
    if not args.wait and not args.download:
        print("Not waiting. Poll with: status " + str(job.get("id")))
        return 0
    job = client.wait(job["id"], args.timeout, args.poll_interval)
    print(f"Job {job['id']} succeeded.")
    if args.download:
        written = download_outputs(job, args.out_dir, getattr(args, "format", None))
        print("Files:\n  " + "\n  ".join(written))
    else:
        print("Outputs:", json.dumps(job.get("outputs", {}), indent=2))
    return 0


def _shared_job_fields(args) -> dict:
    body: dict = {}
    if getattr(args, "quality", None):
        body["quality"] = args.quality
    if getattr(args, "output", None):
        body["output"] = args.output
    if getattr(args, "face_count", None):
        body["face_count"] = args.face_count
    if getattr(args, "title", None):
        body["title"] = args.title
    return body


def cmd_text(client: Client, args) -> int:
    body = {"type": "text_to_3d", "prompt": args.prompt, **_shared_job_fields(args)}
    if args.no_advance_control:
        body["advance_control"] = False
    if args.image:
        body["image_url"] = client.resolve_source(args.image, "image")
    return _finish(client, client.submit_job(body), args)


def cmd_image(client: Client, args) -> int:
    body = {
        "type": "image_to_3d",
        "image_url": client.resolve_source(args.image, "image"),
        **_shared_job_fields(args),
    }
    return _finish(client, client.submit_job(body), args)


def cmd_multiview(client: Client, args) -> int:
    views = []
    for view in ("front", "back", "left", "right"):
        src = getattr(args, view)
        if src:
            views.append({"view": view, "image_url": client.resolve_source(src, "image")})
    if not views:
        raise Alpha3DError("multiview needs at least one of --front/--back/--left/--right")
    body = {"type": "multiview_to_3d", "multi_view_images": views,
            **_shared_job_fields(args)}
    return _finish(client, client.submit_job(body), args)


def _edit_source(client: Client, args) -> dict:
    if args.job:
        return {"post_id": int(args.job)}
    if args.model_url:
        return {"model_url": client.resolve_source(args.model_url, "model")}
    raise Alpha3DError("edit jobs need --job JOB_ID or --model-url URL/path")


def cmd_texture(client: Client, args) -> int:
    if bool(args.prompt) == bool(args.image):
        raise Alpha3DError("texture needs exactly one of --prompt or --image")
    body = {"type": "texture_edit", **_edit_source(client, args), **_shared_job_fields(args)}
    if args.prompt:
        body["prompt"] = args.prompt
    else:
        body["image_url"] = client.resolve_source(args.image, "image")
    return _finish(client, client.submit_job(body), args)


def cmd_rig(client: Client, args) -> int:
    body = {"type": "rigging", **_edit_source(client, args), **_shared_job_fields(args)}
    return _finish(client, client.submit_job(body), args)


def cmd_retopology(client: Client, args) -> int:
    body = {"type": "retopology", **_edit_source(client, args), **_shared_job_fields(args)}
    if args.detail:
        body["detail"] = args.detail
    if args.polygon_type:
        body["polygon_type"] = args.polygon_type
    return _finish(client, client.submit_job(body), args)


def cmd_uv_unwrap(client: Client, args) -> int:
    body = {"type": "uv_unwrap", **_edit_source(client, args), **_shared_job_fields(args)}
    return _finish(client, client.submit_job(body), args)


def cmd_segment(client: Client, args) -> int:
    body = {"type": "segment", **_edit_source(client, args), **_shared_job_fields(args)}
    return _finish(client, client.submit_job(body), args)


def cmd_convert(client: Client, args) -> int:
    body = {"type": "convert", "target_format": args.format,
            **_edit_source(client, args)}
    return _finish(client, client.submit_job(body), args)


def cmd_status(client: Client, args) -> int:
    job = client.get_job(args.job_id)
    print(json.dumps(job, indent=2))
    return 0


def cmd_download(client: Client, args) -> int:
    job = client.get_job(args.job_id)
    status = str(job.get("status", "")).lower()
    if status not in SUCCESS_STATUSES:
        raise Alpha3DError(f"Job {args.job_id} is {status!r}, not ready to download")
    written = download_outputs(job, args.out_dir, args.format)
    print("Files:\n  " + "\n  ".join(written))
    return 0


def cmd_usage(client: Client, args) -> int:
    print(json.dumps(client.usage(), indent=2))
    return 0


def cmd_list(client: Client, args) -> int:
    print(json.dumps(client.list_jobs(args.limit), indent=2))
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _add_wait_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--wait", action="store_true", help="poll until the job finishes")
    p.add_argument("--download", action="store_true", help="download outputs when done")
    p.add_argument("--out-dir", default="assets/models", help="download directory")
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                   help="max seconds to wait (default 900)")
    p.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL,
                   help="seconds between polls (default 20)")


def _add_gen_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--quality", choices=["standard", "pbr", "low_poly"])
    p.add_argument("--output", choices=["textured", "geometry"])
    p.add_argument("--face-count", type=int)
    p.add_argument("--title")
    _add_wait_flags(p)


def _add_edit_source_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--job", help="post_id of a succeeded generation to refine")
    p.add_argument("--model-url", help="https URL or local model file to use as source")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Alpha3D /v1 client for Three.js game assets (Path B — API key). "
                    "For the MCP connector path, call the Alpha3D MCP tools directly.")
    parser.add_argument("--api-key", help="Alpha3D API key (else ALPHA3D_API_KEY)")
    parser.add_argument("--base-url", help="API base (else ALPHA3D_API_BASE or default)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("text", help="text_to_3d")
    p.add_argument("--prompt", required=True)
    p.add_argument("--image", help="optional reference image (local path or https URL)")
    p.add_argument("--no-advance-control", action="store_true",
                   help="auto-generate the reference image (FLUX + rembg) instead of "
                        "supplying one")
    _add_gen_flags(p)
    p.set_defaults(func=cmd_text)

    p = sub.add_parser("image", help="image_to_3d")
    p.add_argument("--image", required=True, help="local path or https URL")
    _add_gen_flags(p)
    p.set_defaults(func=cmd_image)

    p = sub.add_parser("multiview", help="multiview_to_3d")
    for view in ("front", "back", "left", "right"):
        p.add_argument(f"--{view}", help=f"{view} view (local path or https URL)")
    _add_gen_flags(p)
    p.set_defaults(func=cmd_multiview)

    p = sub.add_parser("texture", help="texture_edit (retexture/restyle)")
    _add_edit_source_flags(p)
    p.add_argument("--prompt", help="describe the new look (XOR --image)")
    p.add_argument("--image", help="reference image (XOR --prompt)")
    _add_gen_flags(p)
    p.set_defaults(func=cmd_texture)

    p = sub.add_parser("rig", help="rigging (armature + skin weights)")
    _add_edit_source_flags(p)
    _add_gen_flags(p)
    p.set_defaults(func=cmd_rig)

    p = sub.add_parser("retopology", help="retopology")
    _add_edit_source_flags(p)
    p.add_argument("--detail", choices=["high", "medium", "low"])
    p.add_argument("--polygon-type", choices=["triangle", "quadrilateral"])
    _add_gen_flags(p)
    p.set_defaults(func=cmd_retopology)

    p = sub.add_parser("uv-unwrap", help="uv_unwrap")
    _add_edit_source_flags(p)
    _add_gen_flags(p)
    p.set_defaults(func=cmd_uv_unwrap)

    p = sub.add_parser("segment", help="segment into parts")
    _add_edit_source_flags(p)
    _add_gen_flags(p)
    p.set_defaults(func=cmd_segment)

    p = sub.add_parser("convert", help="convert format")
    _add_edit_source_flags(p)
    p.add_argument("--format", required=True, choices=["GLB", "OBJ", "FBX", "STL"])
    _add_wait_flags(p)
    p.set_defaults(func=cmd_convert)

    p = sub.add_parser("status", help="poll a job")
    p.add_argument("job_id")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("download", help="download a finished job's outputs")
    p.add_argument("job_id")
    p.add_argument("--out-dir", default="assets/models")
    p.add_argument("--format", choices=["glb", "obj", "fbx", "stl", "thumbnail"])
    p.set_defaults(func=cmd_download)

    p = sub.add_parser("usage", help="credit balance + usage")
    p.set_defaults(func=cmd_usage)

    p = sub.add_parser("list", help="list recent API jobs")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    key = args.api_key or os.environ.get("ALPHA3D_API_KEY")
    if not key:
        print("ERROR: no API key. Pass --api-key or set ALPHA3D_API_KEY. "
              "Run the director credential probe first if unsure. Alternatively use "
              "the Alpha3D MCP connector (no key needed).", file=sys.stderr)
        return 2
    base = args.base_url or os.environ.get("ALPHA3D_API_BASE") or DEFAULT_BASE
    client = Client(key, base)

    try:
        return args.func(client, args)
    except Alpha3DError as exc:
        print(f"ERROR: {_scrub(str(exc), key)}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
