# Alpha3D API Notes (Path B — API key)

These notes summarize the Alpha3D public `/v1` API used by `scripts/threejs_3d_asset.py`. For the MCP connector path, see `mcp-integration.md` instead. Any other provider can be substituted by mapping the same submit → poll → download shape.

## Base API

- Base URL: `https://api.alpha3d.io` (override with `ALPHA3D_API_BASE`). All routes below are under `/v1`.
- Auth: `Authorization: Bearer <ALPHA3D_API_KEY>` where the key looks like `ak_live_…`.
- Content type: `application/json`.
- Rate limits: ~120 requests/min per user across `/v1`; image tools (`/v1/images/*`) allow ~20/sec.
- Idempotency: send an `Idempotency-Key` header on `POST /v1/jobs` for safe retries. The script generates one per submission.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/v1/jobs` | Submit a generation or edit job. Returns a job (status `queued`). |
| GET | `/v1/jobs/:id` | Poll a job (live refresh) with fresh presigned output URLs. |
| GET | `/v1/jobs` | List your API-created jobs (paginated). |
| POST | `/v1/images/generate` | FLUX text→image (0 credits, rate-limited). |
| POST | `/v1/images/transform` | FLUX image→image restyle (0 credits). |
| POST | `/v1/images/remove-background` | Background removal → transparent PNG (0 credits). |
| POST | `/v1/uploads/presign` | Presigned PUT URL for uploading a local image/model; returns `file_url` to pass as `image_url`/`model_url`. |
| GET | `/v1/usage` | Usage totals + credit balance. |

## Job Status

Ongoing (keep polling): `queued`, `processing` (a `stage` field names the phase). Terminal: `succeeded`, `failed` (credits auto-refunded on failure). Treat any unrecognized status as ongoing and keep polling until the timeout — never as terminal.

Poll every 15–30s. On timeout, the job keeps running server-side; resume with `status JOB_ID` / `download JOB_ID` later.

## Job Types (`type` in the POST body)

Generation:

- `text_to_3d`: `prompt` (required); optional `image_url` reference. `advance_control` defaults true (you supply a reviewed reference image); set false to auto-generate the reference via FLUX + background removal.
- `image_to_3d`: `image_url` (required) — a single image.
- `multiview_to_3d`: `multi_view_images` (1–4 of `{ view: front|back|left|right, image_url }`).

Edit (source mesh via `post_id` of a succeeded job, or `model_url`; `model_format` inferred if omitted):

- `retopology`: `detail` (`high`|`medium`|`low`, default high), `polygon_type` (`triangle`|`quadrilateral`).
- `uv_unwrap`
- `texture_edit`: `prompt` XOR `image_url` (the new look).
- `rigging`: auto skeleton + skin weights (no baked animation clips).
- `convert`: `target_format` (`GLB`|`OBJ`|`FBX`|`STL`, required).
- `segment` / `segment_preview`: split into semantic parts.

Shared optional fields: `output` (`textured` default | `geometry`), `quality` (`standard` | `pbr` default | `low_poly`), `face_count` (3000–1500000), `title`, `webhook_url`.

## Response Shape

`GET /v1/jobs/:id` returns:

```json
{
  "id": 123,
  "type": "text_to_3d",
  "output": "textured",
  "status": "succeeded",
  "stage": "texturing",
  "title": "hover bike",
  "outputs": {
    "glb": "https://…",
    "obj": "https://…",
    "fbx": "https://…",
    "textured_mesh": "https://…",
    "mesh": "https://…",
    "thumbnail": "https://…",
    "part_0": "https://…"
  },
  "error": null,
  "view_url": "https://alpha3d.io/…",
  "created_at": "…",
  "updated_at": "…"
}
```

Output URLs are presigned and expire (~5 min); re-read the job to get fresh ones. Prefer `outputs.glb` for Three.js.

## Uploads (local files)

To use a local image or model as input, presign then PUT the bytes:

1. `POST /v1/uploads/presign` with `{ file_name, kind: "image"|"model", content_type? }` → `{ upload_url, file_url, expires_in: 300 }`.
2. HTTP `PUT` the file bytes to `upload_url` (valid 5 min).
3. Submit the job with `image_url`/`model_url` = `file_url`.

Allowed: images jpg/jpeg/png/webp; models glb/gltf/obj/fbx/usdz/stl. The `image` and `multiview` script commands do this automatically for local paths.

## Credits

- Generation/edit jobs deduct credits by tier; image tools (`/v1/images/*`) are 0 credits but rate-limited.
- `GET /v1/usage` returns `balance` (`monthly_credits_remaining`, `bonus_credits`, `purchased_credits`, `total_usable`) and per-tool/per-key usage.
- An out-of-credit condition returns an HTTP 402/403; surface it as a top-up blocker and do not retry.

## Webhooks (optional)

Configure an account webhook in the dashboard, or pass `webhook_url` per job. Events: `job.submitted`, `job.updated`, `job.completed`, `job.failed`. Verification headers include `X-Alpha3D-Event` and `X-Alpha3D-Token`. Polling with `status JOB_ID` is sufficient for the script workflow; webhooks are for server integrations.

## Game Defaults

- Prefer `quality=pbr` + `output=textured` for hero assets; `standard`/`geometry` for background props.
- Prefer GLB/PBR for Three.js runtime imports.
- Use `low_poly`, `face_count`, `convert`, or a `retopology` pass for browser/mobile budgets.
- Rig only clean full-body T/A-pose humanoid meshes; verify the pose in the preview before spending a rig job.
- Download output URLs immediately after a job succeeds — they expire.
