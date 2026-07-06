---
name: threejs-3d-generator
description: "Generate, texture, rig, retopologize, UV-unwrap, segment, convert, and download 3D assets for Three.js games. Use for text-to-3D, image-to-3D, multiview-to-3D, game-ready GLB/FBX/OBJ assets, characters, creatures, buildings, props, weapons, terrain pieces, auto-rigging, model texturing/restyling, low-poly/quad retopology, mesh segmentation, and browser asset pipelines. Default provider is Alpha3D, usable two ways: an MCP connector (no keys) or an ALPHA3D_API_KEY REST client; any other provider with the same submit-poll-download shape also works. Pair with threejs-image-generator for concepts, texture references, sky/background/terrain textures, logos, icons, and GUI art before image-to-3D generation."
---

# Three.js 3D Generator

## Purpose

Create production-oriented 3D assets, then prepare them for Three.js games. This is the Three.js game system's 3D-generation layer. The default provider is **Alpha3D**, which offers text-to-3D, image-to-3D, multiview-to-3D, texturing, auto-rigging, retopology, UV unwrap, segmentation, format conversion, and downloadable GLB/OBJ/FBX/STL outputs. The skill is provider-agnostic: any service that follows the same submit → poll → download shape can be substituted.

## Choosing An Integration Path

There are two supported ways to reach Alpha3D. Decide before generating and record the choice in the report.

**Path A — MCP connector (recommended, no API key in code).** If the Alpha3D MCP tools are available in this session (`generate_3d`, `get_job`, `rig_3d`, `texture_3d`, `retopologize`, `uv_unwrap`, `segment_3d`, `convert_format`, `remove_background`, `generate_image`, `list_generation_options`, `get_credit_balance`), call them directly. No script, no key handling — the connector authenticates over OAuth. Load `references/mcp-integration.md` for the tool map and the submit/poll pattern.

**Path B — API key (`ALPHA3D_API_KEY`).** Use the bundled REST client (`scripts/threejs_3d_asset.py`) against the Alpha3D `/v1` API. Requires an `ak_live_…` key from the Alpha3D dashboard. Load `references/api-notes.md` for endpoints and the job model.

**Any other provider.** If the user prefers a different 3D service, follow the same pattern: submit a job, poll status until terminal, download the model URL immediately (URLs expire). Document the substitution; the Three.js integration guidance still applies.

Decision rule for an agent:

1. If the Alpha3D MCP tools are present, use Path A.
2. Else if `ALPHA3D_API_KEY` is set (see credential probe below), use Path B.
3. Else report both setup options to the user, and fall back to procedural Three.js assets for now rather than blocking.

## Path A: MCP Connector Setup

If the tools are not yet present, the user adds Alpha3D as a custom MCP connector once:

- Create/sign in to an Alpha3D account.
- Claude Code / Claude: Settings → Connectors → Add custom connector → paste `https://api.alpha3d.io/mcp`, then complete the one-time sign-in.
- Codex / ChatGPT: Settings → Connectors (enable Developer Mode to run generation tools), add the same URL, sign in.

Auth is OAuth with PKCE (a scoped 30-day token tied to the account; no password is shared). Credits and the asset library stay in sync with the web app and REST API. Full usage in `references/mcp-integration.md`.

## Path B: API Key Setup

Never store API keys in skill files or client-side game code. The script reads the key from, in order:

1. `--api-key`
2. `ALPHA3D_API_KEY`

Create a key in the Alpha3D dashboard (API keys section). Keys are shown once (`ak_live_…`) and sent as `Authorization: Bearer <key>`.

Step 0 before declaring the key unavailable — run the director credential probe, which sources the user's shell profiles:

```bash
bash ~/.claude/skills/threejs-game-director/scripts/probe_asset_credentials.sh   # Codex: ~/.codex/...
```

Paste the literal `ALPHA3D_API_KEY=SET|MISSING` line in the report. Do not conclude the key is unavailable from a plain non-interactive shell until this probe has run. If the probe says SET but the script reports a missing key, the key is only in an interactive profile — wrap the call the same way the probe does (`zsh -lc '...'` / `bash -lc '...'`).

Use the API only from local/server-side tooling. Model download URLs are presigned and expire within minutes, so download outputs immediately after a job succeeds.

## Reference Gate

- Load `references/api-notes.md` before Path B API work: endpoints, job types, status polling, quality tiers, credits, idempotency.
- Load `references/mcp-integration.md` before Path A MCP work.
- Load `references/threejs-integration.md` before importing outputs into a browser game or advising GLB/FBX integration.
- Load `references/image-generator-workflows.md` before pairing `threejs-image-generator` with this skill for 2D concepts, texture references, UI art, logos, decals, or image-to-3D inputs.

Track required references in a reference ledger (yes/no, path, failure reason). Do not mark an asset pipeline complete while a required reference is skipped.

## Common Commands (Path B script)

```bash
python3 ~/.claude/skills/threejs-3d-generator/scripts/threejs_3d_asset.py --help
```

Text to 3D (game-ready hero asset):

```bash
python3 .../threejs_3d_asset.py text \
  --prompt "game-ready sci-fi hover bike, sleek armored panels, readable silhouette, PBR, front facing, centered pivot, no text" \
  --quality pbr --output textured \
  --wait --download --out-dir assets/models/hover-bike
```

Image to 3D from a local `threejs-image-generator` concept (auto-uploads the file):

```bash
python3 .../threejs_3d_asset.py image \
  --image assets/concepts/hover-bike-front.png \
  --quality pbr --output textured \
  --wait --download --out-dir assets/models/hover-bike
```

Multiview to 3D (front/back/left/right improve geometry):

```bash
python3 .../threejs_3d_asset.py multiview \
  --front assets/concepts/robot-front.png --back assets/concepts/robot-back.png \
  --left assets/concepts/robot-left.png \
  --wait --download --out-dir assets/models/robot
```

Status and download (URLs expire — re-fetch with `status` if a download link is stale):

```bash
python3 .../threejs_3d_asset.py status JOB_ID
python3 .../threejs_3d_asset.py download JOB_ID --out-dir assets/models --format glb
```

Edit jobs (all take `--job JOB_ID` from a succeeded generation, or `--model-url URL`):

```bash
# Retexture / restyle
python3 .../threejs_3d_asset.py texture --job JOB_ID \
  --prompt "brushed gunmetal, orange hazard decals, worn edges" \
  --wait --download --out-dir assets/models/retextured

# Auto-rig a T-pose humanoid mesh (armature + skin weights)
python3 .../threejs_3d_asset.py rig --job JOB_ID --wait --download --out-dir assets/models/rigged

# Retopology for a cleaner / lower mesh
python3 .../threejs_3d_asset.py retopology --job JOB_ID --detail medium --polygon-type quadrilateral \
  --wait --download --out-dir assets/models/retopo

# UV unwrap, segment into parts, or convert format
python3 .../threejs_3d_asset.py uv-unwrap --job JOB_ID --wait --download --out-dir assets/models/uv
python3 .../threejs_3d_asset.py segment  --job JOB_ID --wait --download --out-dir assets/models/parts
python3 .../threejs_3d_asset.py convert  --job JOB_ID --format FBX --wait --download --out-dir assets/models/fbx
```

Account:

```bash
python3 .../threejs_3d_asset.py usage      # credit balance + recent usage
python3 .../threejs_3d_asset.py list       # recent API jobs
```

## Quality Tiers And Outputs

- `--quality`: `standard` (untextured-lit), `pbr` (full PBR materials, default), `low_poly` (game-ready). `--face-count` (3000–1500000) overrides the tier when you need a specific budget.
- `--output`: `textured` (full PBR + paint, default) or `geometry` (shape-only, faster and cheaper).
- Formats: generation always returns GLB (recommended for Three.js) + OBJ + thumbnail; `convert` targets GLB/OBJ/FBX/STL.
- For mobile/browser budgets, prefer `low_poly` or a `retopology` pass, and keep `--output geometry` for background props that do not need textures.

## Rigging Reliability

Alpha3D auto-rigging produces an armature and skin weights on a humanoid mesh — it does not bake preset animation clips. Plan runtime animation in Three.js (`AnimationMixer` with your own or external clips) or via a DCC pipeline.

- Rig from a full-body **T-pose or A-pose**: arms away from the body, legs separated, symmetric, no props fused into the silhouette, whole body (including head) in frame. A `threejs-image-generator` T-pose reference before image-to-3D helps a lot.
- Verify the rendered preview is actually in T/A-pose before spending a rig job; regenerate the base mesh if the pose is wrong rather than rigging a bad pose.
- After download, inspect the skeleton and `gltf.animations` in the engine; validate the rig visually before wiring gameplay. See `references/threejs-integration.md`.

## Three.js Integration

Load `references/threejs-integration.md` before importing outputs. In short:

- Prefer GLB/PBR for Three.js; use `GLTFLoader` to load and `AnimationMixer` for animation.
- Keep generated model files out of client-side API flows; generation is a build-time tooling step.
- Inspect triangle count, texture/material count, file size, scale, pivot, bounds, and animation clips.
- Use generated 3D assets as hero/high-fidelity content, then build surrounding prop kits procedurally or with additional `threejs-3d-generator` / `threejs-image-generator` passes.

## Image Generator Pairing

Use `threejs-image-generator` before 3D generation when a strong 2D reference improves the result — character T-pose sheets, vehicle/building/prop concepts, style sheets, texture references, and logos/icons/decals. Load `references/image-generator-workflows.md` for prompt patterns and the handoff to `image` / `multiview`.

## Final Report

Report the chosen integration path (MCP or API key), credential probe output (Path B), reference ledger, job IDs, output paths, quality/output settings, any rig/texture/convert edits, Three.js import notes, renderer diagnostics, and any missing/failed steps.
