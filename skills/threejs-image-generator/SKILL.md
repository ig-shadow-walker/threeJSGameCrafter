---
name: threejs-image-generator
description: "Generate and edit 2D image assets for Three.js games. Use for concept sheets, image-to-3D inputs, texture references, sky/background plates, decals, logos, icons, GUI art, title/menu art, thumbnails, marketing stills, and source images that feed threejs-3d-generator. Default provider is Alpha3D (FLUX), usable via an MCP connector (no keys) or an ALPHA3D_API_KEY REST client; Gemini or another provider can be substituted. Also use for direct image editing when the user provides an image path."
---

# Three.js Image Generator

## Purpose

Create game-useful 2D assets and references for Three.js projects. This skill is the image-generation layer for the Three.js game system: it produces concepts, textures, decals, UI art, and 2D inputs that can be handed to `threejs-3d-generator` for image-to-3D model creation.

Default provider: **Alpha3D (FLUX)**, image generation is free (rate-limited). The same two integration paths as the 3D generator apply.

## Choosing An Integration Path

**Path A — MCP connector (recommended, no key).** If the Alpha3D MCP tools are available (`generate_image`, `remove_background`), call them directly. `generate_image` supports text, image (transform), and style modes; returns the image inline. See the 3D generator's `references/mcp-integration.md` for connector setup — it is the same connector.

**Path B — API key (`ALPHA3D_API_KEY`).** Use the bundled script against `/v1/images/*` (generate/transform). Free but rate-limited.

**Alternate provider — Gemini.** Pass `--provider gemini` (`GEMINI_API_KEY`) to use Google's Gemini image API instead, or adapt for another provider.

Decision rule: prefer the MCP tool if present; else the Alpha3D API key; else Gemini/other if that key is set; else report the options and fall back to procedural art.

## When To Use

Use this skill before procedural-only fallback when a Three.js game needs:

- 2D-to-3D reference images for `threejs-3d-generator`: characters, creatures, buildings, ships, cars, weapons, props, pickups, terrain modules.
- Texture and material references: terrain, road, rock, sand, metal, sci-fi panels, trim sheets, decals, hazard labels, signs.
- Environment images: skies, backdrops, city horizons, nebula plates, menu backgrounds, parallax layers.
- UI art: logos, faction marks, icons, item cards, ability badges, cockpit decals, GUI panels, title art.
- Existing-image edits, style variants, cleanup, palette alignment, or concept sheet refinements.

For premium/AAA/showcase graphics work, generate at least one relevant image for high-value 2D surfaces or image-to-3D inputs unless the credential probe or a real generation attempt shows a blocker.

## API Key (Path B / Gemini)

Never store API keys in skill files or browser/game code. The script reads, in order: `--api-key`, then the provider env var (`ALPHA3D_API_KEY` for Alpha3D, `GEMINI_API_KEY` for Gemini).

Before declaring a key unavailable in a `threejs-game-director` or `threejs-aaa-graphics-builder` workflow, run the director credential probe and paste its literal SET/MISSING output:

```bash
bash ~/.claude/skills/threejs-game-director/scripts/probe_asset_credentials.sh   # Codex: ~/.codex/...
```

If the probe says `ALPHA3D_API_KEY=SET` but the script sees no key, run through a login shell that sources the user's profile (`zsh -lc '...'` / `bash -lc '...'`), the same way the probe does.

## Tool Script (Path B)

Run from the project directory so output lands in the game project:

```bash
# Alpha3D (default)
uv run ~/.claude/skills/threejs-image-generator/scripts/generate_image.py \
  --prompt "your image description" --filename assets/concepts/output.png --ratio square

# Image-to-3D framing helps the 3D pipeline
uv run .../generate_image.py --prompt "single sci-fi hover bike, plain background" \
  --filename assets/concepts/bike.png --static-enhancement

# Edit / restyle an existing image
uv run .../generate_image.py --input-image assets/concepts/ship.png \
  --prompt "battle-worn red racing livery, clearer material zones" \
  --filename assets/concepts/ship-red.png

# Gemini alternate
uv run .../generate_image.py --provider gemini --prompt "..." \
  --filename assets/concepts/out.png --resolution 2K
```

Resolution: Alpha3D supports `1K` and `1080p` (the script maps `--resolution 2K/4K` to `1080p`); Gemini uses `1K`/`2K`/`4K` as given. Use `--ratio square|portrait|landscape` for Alpha3D framing.

## Prompt Patterns

Image-to-3D reference:

```text
Create a clean 3D-generation reference image of [asset]. Centered single object, full object visible, plain light background, readable silhouette, clear material zones, game-ready [genre/style], no motion blur, no cropped parts, no text.
```

Riggable character/creature reference:

```text
Create a full-body [T-pose/A-pose/side-view creature] reference for 3D rigging: [details]. Symmetric stance, visible hands/feet/limbs, plain background, readable costume/anatomy layers, no weapon fused to hands.
```

Texture/material reference:

```text
Create a seamless game texture reference for [surface]. Orthographic/top-down, PBR-friendly albedo, clear material variation, no perspective, no baked strong shadows, [style/material details].
```

Logo/icon/UI art:

```text
Create a crisp game UI [logo/icon/badge/panel] for [faction/item/ability]. Transparent-friendly silhouette, high contrast at small size, [genre styling], no tiny unreadable text.
```

Sky/background:

```text
Create a wide game background plate of [environment]. Layered depth, readable horizon, [time/weather/style], suitable behind a real-time Three.js scene, no foreground subject.
```

## Three.js Integration Rules

- Save concepts and image-to-3D sources under `assets/concepts/`.
- Save textures, decals, icons, and GUI source images under `assets/textures/`, `assets/decals/`, or `assets/ui/`.
- For image-to-3D, hand the saved image path to `threejs-3d-generator` (`image` / `multiview` commands, or the MCP `generate_3d` tool) and record the chain in the external asset ledger.
- Do not call the image API from client-side game code.
- Convert generated images into runtime formats deliberately: PNG for alpha/UI, JPG/WebP/KTX2 for larger opaque textures where the project pipeline supports it.
- Verify how the image appears in game, not only that the file exists.

## Required Report

Report:

- Integration path (MCP / Alpha3D API key / Gemini) and credential probe output or blocker.
- Prompt and purpose.
- Output path and resolution/ratio.
- Whether the image was used directly, edited further, or handed to `threejs-3d-generator`.
- Any remaining integration work such as compression, UV assignment, alpha cleanup, or atlas packing.

Do not mark a premium graphics phase complete if the needed image outputs are missing and the only justification is "procedural is enough" for high-value UI, texture, sky, decal, logo, or image-to-3D surfaces.
