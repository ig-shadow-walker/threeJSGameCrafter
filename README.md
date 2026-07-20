# Three.js Game Skills

Self-contained Codex and Claude Code skills for building playable, polished Three.js browser games. Install the skills, then ask your agent to use `threejs-game-director`; the director routes concept/design, gameplay, graphics, UI, asset generation, audio, debugging, and release verification without requiring users to choose every specialist skill manually.

The package includes the runtime materials agents need: `SKILL.md` files, references, checklists, prompt templates, helper scripts, and a Vite + TypeScript + Three.js scaffold bundled inside the relevant skill folders.

3D and image asset generation are powered by [Alpha3D](https://alpha3d.io), usable either through an MCP connector (no API key) or an API key — see [Asset Generation](#asset-generation).

Maintained by Aryan Behzadi — [Alpha3D](https://alpha3d.io) team ([GitHub](https://github.com/ig-shadow-walker)).

## Demos

Demo games and videos are coming soon.

| Game | Video | Play |
| --- | --- | --- |
| _Coming soon_ | — | — |

## Install

Install all skills for Codex:

```bash
npx skills add ig-shadow-walker/threejs-game-skills --skill '*' -a codex -g -y
```

Install all skills for Claude Code:

```bash
npx skills add ig-shadow-walker/threejs-game-skills --skill '*' -a claude-code -g -y
```

If your installed `skills` CLI does not support the Claude Code target, install from a cloned checkout with `./install.sh --claude`.

For local development from a cloned checkout:

```bash
./install.sh --codex
./install.sh --claude
./install.sh --all
```

The local installer copies `skills/` into the selected agent skills directory. It skips same-named skills unless you pass `--force`, and it never removes unrelated user skills unless `--prune-managed` is explicitly requested.

```bash
./install.sh --codex --force
```

## Use The Skills

After installing, open Codex or Claude Code in an empty project folder, or in an existing Three.js game you want to improve. Then prompt the agent with the outcome you want and name the director skill:

```text
Use threejs-game-director to build a premium futuristic tower defense game from scratch.
Automatically use the relevant gameplay, graphics, UI, asset generation, audio, debug,
and QA skills. Build a playable loop first, then iterate until it passes browser,
mobile, visual, UI, performance, and release checks.
```

The agent should:

- Load `threejs-game-director` first for broad game work.
- Load sibling skills for gameplay systems, AAA graphics, UI, debug/profile, QA/release, 3D generation, image generation, and audio generation when the request calls for them.
- Use the bundled scaffold internally when starting from an empty folder.
- Create or update the game code in your project.
- Run builds, browser checks, screenshots, canvas-pixel checks, mobile viewport checks, and QA gates before claiming completion.
- Report the skill-loading ledger, reference ledger, asset/audio sourcing decisions, visual scorecard, and remaining risks for premium work.

Users generally should not need to run the scaffold or QA helper scripts directly. Those scripts are packaged so the skills can use them as part of the workflow.

## Asset Generation

The core Three.js skills work without any paid asset generation. When generation is unavailable, the director reports the credential probe output, skips external generation, and falls back to procedural/local assets.

3D and image generation default to **Alpha3D**, which you can reach two ways:

### Option 1 — MCP connector (recommended, no API key)

Add Alpha3D as a custom MCP connector once, and the agent calls its tools directly with no key stored anywhere:

1. Create or sign in to an account at [alpha3d.io](https://alpha3d.io).
2. Add the connector URL `https://api.alpha3d.io/mcp`:
   - Claude Code / Claude: Settings → Connectors → Add custom connector → paste the URL → complete the one-time sign-in.
   - Codex / ChatGPT: Settings → Connectors (enable Developer Mode to run generation tools) → add the URL → sign in.
3. Sign in when the assistant opens the one-time link (OAuth; no password is shared).

The connector exposes text/image/multiview → 3D, rigging, texturing, retopology, UV unwrap, segmentation, format conversion, background removal, FLUX image generation, job polling, and credit balance. Credits and your asset library stay in sync with the web app and the REST API.

### Option 2 — API key

Create an API key in the Alpha3D dashboard and export it. The bundled scripts use it from local/server-side tooling only.

```bash
export ALPHA3D_API_KEY="ak_live_..."   # 3D + image generation via the /v1 REST API
```

Never commit API keys or put them in browser-side game code. These skills use provider APIs from local agent tooling, then save generated assets into your game project. Generated download URLs are presigned and expire quickly, so the skills download outputs immediately after a job succeeds.

### Providers and keys

| Capability | Skill | How to enable | Use cases |
| --- | --- | --- | --- |
| 3D generation | `threejs-3d-generator` | Alpha3D MCP connector, **or** `ALPHA3D_API_KEY` | Text/image/multiview → 3D, game-ready GLB/FBX/OBJ hero models, vehicles, props, buildings, weapons, rigging, texturing, retopology, UV unwrap, segmentation, format conversion. |
| Image generation | `threejs-image-generator` | Alpha3D MCP connector or `ALPHA3D_API_KEY` (alternate: `GEMINI_API_KEY`) | Concept art, image-to-3D source images, texture references, decals, skies, backgrounds, icons, logos, GUI art, title/menu art. |
| Audio generation | `threejs-audio-generator` | `ELEVENLABS_API_KEY` | SFX, ambience loops, UI sounds, announcer lines, dialogue TTS, voice conversion, audio cleanup, game audio manifests. |

Set keys in your shell profile, then restart your terminal.

macOS/Linux with `zsh` or `bash`:

```bash
export ALPHA3D_API_KEY="..."
export GEMINI_API_KEY="..."       # optional image alternate
export ELEVENLABS_API_KEY="..."
```

For `zsh`, put those lines in `~/.zshrc` or `~/.zprofile`. For `bash`, put them in `~/.bashrc` or `~/.bash_profile`.

Windows PowerShell, persistent for your user account:

```powershell
[Environment]::SetEnvironmentVariable("ALPHA3D_API_KEY", "...", "User")
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "...", "User")
[Environment]::SetEnvironmentVariable("ELEVENLABS_API_KEY", "...", "User")
```

After setting persistent Windows variables, restart your terminal, Codex, or Claude Code so the agent process can see the new environment.

The director skill includes a credential probe that sources common shell profiles before deciding a key is missing:

```bash
bash ~/.agents/skills/threejs-game-director/scripts/probe_asset_credentials.sh
```

Expected output:

```text
ALPHA3D_API_KEY=SET|MISSING
GEMINI_API_KEY=SET|MISSING
ELEVENLABS_API_KEY=SET|MISSING
```

Notes:

- The Alpha3D MCP connector authenticates over OAuth and needs no environment variable, so a `MISSING` `ALPHA3D_API_KEY` does not block the MCP path.
- Alpha3D 3D generation is optional but useful for high-value surfaces procedural code alone rarely makes premium: hero vehicles, bosses, weapons, buildings, creatures, props, and textured GLB/FBX assets.
- Alpha3D image generation (FLUX) is free (rate-limited) and useful before image-to-3D and for high-quality texture, sky, icon, logo, decal, and GUI sources; Gemini remains an alternate via `GEMINI_API_KEY`.
- ElevenLabs is optional but useful for making games feel finished through interaction SFX, ambience, UI feedback, voice, and cleanup.

## Best Entry Points

- Use `threejs-game-director` for complete games, major upgrades, premium polish, release-ready work, or anything broad.
- Use `threejs-game-concept` to ideate and scope a new game and write its Game Design Document — start here for a new idea, a vague request, or "help me plan the game I want to build".
- Use `threejs-gameplay-systems` for mechanics, architecture, input, camera, physics, scoring, objectives, and game feel.
- Use `threejs-aaa-graphics-builder` when screenshots look basic or the game needs stronger models, materials, lighting, VFX, world detail, or render polish.
- Use `threejs-game-ui-designer` for HUDs, menus, overlays, responsive layout, safe areas, icons, touch controls, and text fit.
- Use `threejs-debug-profiler` for black screens, runtime errors, loading issues, resize/mobile bugs, performance, draw calls, triangles, textures, and memory.
- Use `threejs-qa-release` for production builds, browser verification, screenshots, canvas pixels, mobile checks, release risk reports, and static-hosting readiness.
- Use `threejs-3d-generator` for Alpha3D text/image-to-3D models, texturing, rigging, retopology, UV unwrap, segmentation, conversion, and GLB/FBX game assets.
- Use `threejs-image-generator` for Alpha3D (or Gemini) concepts, image-to-3D inputs, textures, decals, skies, backgrounds, icons, logos, GUI art, and title/menu art.
- Use `threejs-audio-generator` for ElevenLabs SFX, ambience, UI sounds, voice/TTS, voice conversion, cleanup, and Three.js audio integration.

For most user-facing game requests, start with `threejs-game-director` and let it pull in the specialists.

## What Good Usage Looks Like

For a new game:

```text
Use threejs-game-director to create a AAA-inspired hover racing game from scratch.
Make it playable, add premium track visuals, vehicle feel, HUD, SFX hooks, desktop and
mobile controls, and run the full verification pass before reporting done.
```

For visual upgrades:

```text
Use threejs-game-director to upgrade this Three.js game from prototype visuals to
premium browser-game quality. Use the AAA graphics, UI, image, 3D, audio, debug,
and QA skills as needed. Include the visual scorecard and evidence from active-play
screenshots.
```

For an existing broken game:

```text
Use threejs-game-director to debug and finish this Three.js game. First get it running,
then improve gameplay feel, UI, graphics, performance, and release verification until
the remaining risks are explicit.
```

For asset-heavy games:

```text
Use threejs-game-director to build a premium space dogfight game. Use threejs-image-generator
for concepts, skies, decals, icons, and GUI art; use threejs-3d-generator for hero ships
and weapons via the Alpha3D connector or API key; use threejs-audio-generator for SFX and
ambience. If generation is blocked, report the credential probe output and fallback plan.
```

## Expected Evidence

For meaningful Three.js work, the skills should gather evidence before claiming success:

- `npm run build`
- local browser run
- browser console and page error check
- Playwright screenshot
- canvas nonblank pixel check
- desktop and mobile viewport pass
- interaction check for the main control path
- performance snapshot when graphics, assets, shaders, or post-processing changed
- UI text-fit, overlap, safe-area, and touch-target checks when UI changed
- visual scorecard for premium, AAA, showcase, or less-basic claims
- external asset/audio sourcing ledger when generated assets or audio are in scope

Premium/AAA claims should not rely on a static scene, placeholder cubes, generic stat-card HUDs, or unverified screenshots. The game should have an active playable loop and a filled visual scorecard.

## Skill System

- `threejs-game-director`: main entrypoint for complete game builds and orchestration.
- `threejs-game-concept`: ideation, concept, pillars, core loop, scope tiers, asset map, and the Game Design Document (`docs/game-design.md`) — the pre-production phase.
- `threejs-gameplay-systems`: playable loop, architecture, mechanics, entities, controls, camera, physics, and feel.
- `threejs-aaa-graphics-builder`: visual scorecard, asset architecture, models, materials, VFX, render polish.
- `threejs-game-ui-designer`: HUDs, menus, overlays, responsive UI, icons, safe areas, UI states.
- `threejs-debug-profiler`: scene/runtime/render bugs, mobile bugs, performance profiling, renderer metrics.
- `threejs-qa-release`: browser QA, screenshots, canvas pixels, responsive checks, production build, release risk report.
- `threejs-3d-generator`: Alpha3D text/image-to-3D, texturing, rigging, retopology, UV unwrap, segmentation, conversion, download, and Three.js import guidance (MCP connector or API key).
- `threejs-image-generator`: Alpha3D (or Gemini) image generation for concepts, textures, decals, skies, icons, GUI art, and image-to-3D inputs.
- `threejs-audio-generator`: ElevenLabs-backed SFX, ambience, UI sounds, voice/TTS, voice conversion, cleanup, and Three.js audio integration.

## Packaged Resources

Installed skills are self-contained. They do not depend on root docs, root scaffolds, root prompts, or root checklists.

- `skills/`: the full public package. Each skill owns its required `SKILL.md`, `references/`, `scripts/`, and `assets/`.
- `skills/threejs-gameplay-systems/assets/threejs-vite-game/`: packaged game scaffold used by the skills when starting from an empty project.
- `skills/threejs-qa-release/scripts/inspect-threejs-canvas.mjs`: packaged browser/canvas inspection helper used by QA workflows.
- `scripts/`: local validation helpers for maintainers.
- `install.sh`: local installer for working on this checkout.

## Maintainer Checks

Validate this workflow repository:

```bash
npm install
npm run check:scripts
npm run validate:skills
```

Maintainers can run packaged helpers directly when testing the skill package, but normal users should interact through agent prompts:

```bash
python3 skills/threejs-gameplay-systems/scripts/create_threejs_game.py ../my-threejs-game
node skills/threejs-qa-release/scripts/inspect-threejs-canvas.mjs --url http://127.0.0.1:5188 --mobile
```

## Acknowledgements

This project is built on top of the original Three.js game skills created by [Majid Manzarpour](https://x.com/majidmanzarpour). His work laid the foundation for the skill system, the game scaffold, and the phase-based orchestration approach used here. Full credit and thanks to him for the original project.

> Based on the Three.js game skills by Majid Manzarpour — https://x.com/majidmanzarpour

## License

MIT. See [LICENSE](LICENSE).
