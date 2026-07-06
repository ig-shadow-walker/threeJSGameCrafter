# Alpha3D MCP Integration (Path A — no API key)

This is the recommended path when the user runs an assistant that supports MCP connectors (Claude Code / Claude, Codex / ChatGPT, or any MCP client). The connector authenticates over OAuth, so there is no API key to store and no script to run — the agent calls tools directly.

## One-Time Setup

The user adds Alpha3D as a custom connector once:

1. Create or sign in to an Alpha3D account.
2. Add the connector URL `https://api.alpha3d.io/mcp`:
   - Claude Code / Claude: Settings → Connectors → Add custom connector → paste the URL → complete the one-time sign-in.
   - Codex / ChatGPT: Settings → Connectors (enable Developer Mode to run the generation tools) → add the URL → sign in.
3. Sign in when the assistant opens the one-time link (OAuth + PKCE; a scoped 30-day token tied to the account — no password is shared).

Credits, generations, and the asset library stay in sync across the web app, the REST API, and the MCP assistant.

## Detecting Availability

Before assuming the connector is missing, check whether the Alpha3D MCP tools are present in the session (e.g. `generate_3d`, `get_job`). If present, use them. If absent, tell the user the one-time setup above, and either wait or fall back to Path B (API key) or procedural assets.

## Tool Map

| Tool | Purpose |
| --- | --- |
| `list_generation_options` | List every operation with its credit cost and required params. Call before spending credits so you can tell the user what a job costs. |
| `get_credit_balance` | Current credit balance. |
| `generate_3d` | Text, image (`image_url`), or multiview (`multi_view_images`, 1–3 of `{view, image_url}`) → 3D. `quality`: `standard`/`pbr`/`low_poly`. `face_count` optional. Returns a `job_id`. |
| `generate_image` | FLUX text/image/style → image (free, rate-limited). Returns the image inline. |
| `remove_background` | Cutout → transparent PNG (free, rate-limited). |
| `rig_3d` | Auto-rig a T-pose humanoid mesh (`post_id` of a generation, or `model_url`). Returns a `job_id`. |
| `texture_3d` | Retexture/restyle a mesh. |
| `retopologize` | Cleaner / lower mesh. |
| `uv_unwrap` | Auto UV layout. |
| `segment_3d` | Split into semantic parts. |
| `convert_format` | GLB/OBJ/FBX/STL conversion. |
| `get_job` | Poll a `job_id`: `queued`/`processing`/`completed`/`error`. When completed, returns fresh download links. Poll every 15–30s. |
| `list_library` / `search` / `fetch` | Browse or fetch existing assets in the account library. |

## Submit → Poll → Download Pattern

1. Optionally call `list_generation_options` and `get_credit_balance`, and report the cost to the user before spending credits.
2. Call a generation/edit tool (`generate_3d`, `rig_3d`, etc.). It returns a `job_id` immediately.
3. Poll `get_job(job_id)` every 15–30s until `completed` or `error`. Treat anything that is not a terminal state as still running.
4. On `completed`, download the returned links **immediately** — they are presigned and expire within minutes. Save under the project's `assets/models/…`.
5. For rigging, remember Alpha3D returns an armature + skin weights, not baked animation clips — plan runtime animation in Three.js (see `threejs-integration.md`).

## Credit Awareness

Generation and edit jobs spend credits (see `list_generation_options` for current costs, e.g. `standard`/`pbr`/`low_poly` tiers). Image tools (`generate_image`, `remove_background`) are free but rate-limited. If a job fails for lack of credits, surface it to the user as a top-up blocker rather than retrying.

## Reporting

Report the path (MCP), the tools/jobs run, job IDs, credit cost where known, downloaded asset paths, and Three.js import notes — the same evidence the API-key path reports, minus the credential probe.
