# Three.js Game Skills — Review & Sharpening Plan

Review of all nine skills for clarity, correctness, enforceability, and de-duplication.
Findings are anchored to `file:line`. Priority: **P0** = actively wrong / bug / wastes money,
**P1** = weakens the skill's core promise, **P2** = sharpening / hygiene.

---

## Cross-cutting themes

These three patterns account for most of the findings. Fixing them at the root is higher-leverage
than fixing each instance.

### A. The enforcement layer is honor-system
The director's premise is "an audit script enforces the quality contract," but
`skills/threejs-game-director/scripts/audit_reference_report.py` is almost entirely **substring
matching against strings the SKILL.md tells the agent to paste**. An agent can copy the empty
ledger and blank scorecard templates into its report and pass the premium audit with zero real
work. Every "gate" and "ledger" downstream is self-attested prose that nothing verifies. This is
the highest-leverage fix in the repo.

### B. Duplication that is already drifting
The same policy lives in 2–3 files and the copies already disagree:
- Two scorecard files with different automatic-failure lists.
- `mobile-input.md` byte-identical in two skills.
- Two copies of `inspect-threejs-canvas.mjs` maintained separately.
- Asset-sourcing skip-rules and ledger templates restated (and diverging) across
  `SKILL.md`, `director-phase-os.md`, and `AGENTS.md`.

Every fix now costs double, and readers who hit two copies get contradictory rules.

### C. The scaffold doesn't fully practice what the docs preach
The starter agents copy (`threejs-vite-game`) has no restart/fail loop (violates its own
definition-of-done), leaks the whole scene on HMR (while a correct, unused `dispose.ts` helper
sits right there), and has a multi-key input bug.

---

## `threejs-game-director` — orchestration core

| # | Pri | Finding | Anchor |
|---|-----|---------|--------|
| D1 | **P0** | Audit gates are trivially satisfiable — every "premium" check is a bare substring search for a heading (`"average"`, `"art direction"`, etc.) that appears verbatim in the SKILL's own paste-in templates. Measures presence of headings, not results. | `scripts/audit_reference_report.py:29-55, 124-125` |
| D2 | **P0** | `--premium not-needed` check false-fails: it trips on the ledger template's own vocabulary (`not-needed`, `procedural`), punishing agents for using the required wording even on legitimately-skipped work. | `scripts/audit_reference_report.py:182` |
| D3 | **P0** | `probe_asset_credentials.sh` mis-detects keys for bash users: prefers `zsh` by binary presence (always present on macOS) and only sources zsh profiles. A key in `~/.bash_profile` reads `MISSING` — which the skill treats as a hard blocker authorizing skipped premium work. | `scripts/probe_asset_credentials.sh:4-11` |
| D4 | P1 | `EXTERNAL_OUTPUT_PATTERNS` (UUID + `*.glb`) passes on a fabricated task ID or a pre-existing stock model path — green-lights exactly the "prototype passed off as premium" failure the skill exists to prevent. | `scripts/audit_reference_report.py:64-67, 180` |
| D5 | P1 | `PREMIUM_AUDIO` / `--physics` markers are near-free: `"audio"` is a substring of `"audio generator"`; `PHYSICS_MARKERS` omits sensors/CCD/counts the prose gate requires. The stricter checks depend on the agent self-selecting the flag. | `audit_reference_report.py:23-27, 57-61` vs `director-phase-os.md:289` |
| D6 | P1 | SKILL.md is ~40% duplicated boilerplate (263 lines): asset-sourcing ledger appears twice (`72-87`, `162-172`), full Ledgers section duplicates `director-phase-os.md:85-130`. Load-bearing instructions are buried in fill-in-the-blank templates. | `SKILL.md:70-97, 148-195` |
| D7 | P2 | Front-matter `description` (~180 words) crams routing policy into the trigger field, diluting embedding match. Cut to what-it-is + keyword set; move "load these siblings" to the body (already there). | `SKILL.md:3` |
| D8 | P2 | Skip-rules + ledger templates diverge across three files (SKILL.md lists 5, phase-os lists a different 5, AGENTS.md a subset; phase-os has an `Audio/SFX/voice:` ledger line SKILL.md omits). Make `director-phase-os.md` canonical; others link. | `SKILL.md:89-97` / `director-phase-os.md:45-55` / `AGENTS.md:36-44` |

**Fix direction for D1/D2/D4/D5 (same root cause — labels vs. values):** require *numbers and paths*.
Regex 10 numeric category scores, verify `average ≥ 2.3` and no category `< 2`; require screenshot/
asset paths (`\.png|\.glb`) adjacent to claims; require the generation command + its output for
external-asset evidence rather than a lone UUID.

---

## `threejs-gameplay-systems` — guidance + scaffold

| # | Pri | Finding | Anchor |
|---|-----|---------|--------|
| G1 | **P0** | Scaffold has no restart/fail loop — on completion it sets `complete = true` and freezes. Directly contradicts `new-game-definition-of-done.md:6,16` and `gameplay-workflows.md:32`. The reference agents copy teaches the anti-pattern. | `assets/threejs-vite-game/src/game/Game.ts:103-105` |
| G2 | **P0** | HMR scene leak — `dispose()` frees only pickups/player; floor geometry+`CanvasTexture`, rails, ring marker, and lights leak on every HMR edit. The correct `disposeObject3D()` helper is imported nowhere. | `Game.ts:74-83`; `src/utils/dispose.ts` (0 refs) |
| G3 | **P0** | Dash input bug — Space OR Shift set/clear one shared `dashDown` bool; releasing one while the other is held drops the dash. Exactly the "controls stick or drop" class the skill warns about. | `src/core/InputController.ts:25-37` |
| G4 | P1 | Fixed-timestep contradiction — refs mandate fixed-step for physics, scaffold ships variable-step (`Loop.ts` clamps delta only) with no accumulator to copy except a markdown block. State the intent explicitly or build a `fixedUpdate` into `Loop`. | `src/core/Loop.ts:23-30`; `physics-engine-selection.md:74-88` |
| G5 | P2 | Per-frame `Vector3` allocations contradict "keep hot paths allocation-light" (`SKILL.md:35`). Hoist offsets to fields. | `src/systems/CameraRig.ts:15,23` |
| G6 | P2 | `Pickup.update` mutates `group.children[0]` by index — brittle when an agent adds a glow child (very likely per the premium checklist). Hold a `core` mesh ref. | `src/entities/Pickup.ts:39` |
| G7 | P2 | `create_threejs_game.py --force` merges via `copytree(dirs_exist_ok=True)` — stale files from a prior game survive. SKILL says "overwritten"; it merges. Add `--clean` or fix wording. | `scripts/create_threejs_game.py:62-66`; `SKILL.md:46` |
| G8 | P2 | Non-ASCII dir names silently fall back to `threejs-vite-game` package name with no warning. Print the normalized name in the success output. | `create_threejs_game.py:34-36` |
| G9 | P2 | Endless-runner tasks route to a demanding checklist but the only scaffold is a top-down collector. Add a one-line note that the scaffold is a collector, not a runner starter. | `SKILL.md:24` |

**Note:** dependency pins are current (Vite 8 / TS 6 era) — not a finding. Guidance quality and
`physics-engine-selection.md` (a real decision ladder, not waffle) are strong and should be kept.

---

## `threejs-aaa-graphics-builder`

| # | Pri | Finding | Anchor |
|---|-----|---------|--------|
| A1 | **P0** | No physically-correct light-unit guidance. r155+ uses PBR light units by default; agents porting old intensity values get black or blown-out scenes. Most likely cause of a visibly broken result. | `references/render-recipes.md:24-33` |
| A2 | P1 | No `OutputPass` guidance. With `EffectComposer`, tone-mapping/sRGB leaves the main render path; bloom applies after tone mapping and colors go wrong. Recipe adds bloom but never says where tone mapping happens. | `render-recipes.md:7`; `implementation-blueprint.md:144` |
| A3 | P1 | Two scorecard files drifting — `checklists/aaa-visual-scorecard.md:16` lists 6 automatic failures; canonical `visual-scorecard.md:82-94` lists 10 (omits "UI overlaps play path / fails safe areas" and "not playable through real input"). An agent using the checklist can pass a game the real rubric fails. Collapse checklist to a pointer. | both files |
| A4 | P1 | Scorecard is gameable — report format asks for free-text `evidence:`; an agent self-assigns 2/3 with a sentence. Require pasted `renderer.info` + screenshot paths, not adjectives. | `visual-scorecard.md:59-63, 100-111` |
| A5 | P2 | Workflow threshold contradicts the scorecard's own gate — `SKILL.md:48` says "every category ≥ 2" but drops the `average ≥ 2.3` requirement, so an all-2s (avg 2.0) game claims premium. | `SKILL.md:48` vs `visual-scorecard.md:69-70` |
| A6 | P2 | ~40% overlap across `material-lighting-quality`, `performance-safe-visual-detail`, `procedural-model-quality` (diagnostics + mobile + instancing repeated in all three). Extract a shared "every-pass baseline" block. | three checklist files |
| A7 | P2 | Emissive/`MeshPhysicalMaterial` advice never cross-references the "glow hides missing geometry" anti-pattern at the point of temptation. | `implementation-blueprint.md:86`; `model-recipes.md:130-134` |
| A8 | P2 | Inconsistent DPR cap across three files (`1.5 or 2` / unspecified / "considered"). State one concrete value and reference it. Also: LOD listed uncritically — for fixed arcade cameras it's pure overhead. | `render-recipes.md:10`; `implementation-blueprint.md:147,178`; `model-recipes.md:124` |

---

## `threejs-game-ui-designer` / `threejs-debug-profiler` / `threejs-qa-release`

| # | Pri | Finding | Anchor |
|---|-----|---------|--------|
| U1 | **P0** | `mobile-input.md` is byte-identical in two skills and misfiled — 7/10 lines are input/DPR mechanics (belong in debug-profiler); the design half is already in `responsive-ui-fit.md` + `ui-patterns.md`. Delete the ui-designer copy. | `threejs-debug-profiler/.../mobile-input.md` == `threejs-game-ui-designer/.../mobile-input.md` |
| U2 | **P0** | Inspector alpha check is dead code — Playwright screenshots are always opaque (alpha=255), so `alphaPixels > 256` is always true and the `a>>6` term is constant. The "transparency signal" tests nothing. | `threejs-qa-release/scripts/inspect-threejs-canvas.mjs:55,70` |
| U3 | **P0** | `--mobile` sets `userAgent: undefined`, overriding the iPhone UA with desktop Chromium — games that branch on `navigator.userAgent` render the desktop path, so mobile emulation silently tests the wrong branch. | `inspect-threejs-canvas.mjs:89` |
| U4 | P1 | Inspector crashes on the exact case SKILL.md recommends it for — qa-release ships no `package.json`, so `@playwright/test`/`pngjs` aren't installed in a standalone target (`ERR_MODULE_NOT_FOUND`). Add an install note or remove the dep. | `threejs-qa-release/scripts/` (no package.json); `SKILL.md:32` |
| U5 | P1 | `waitUntil: 'networkidle'` is flaky for games with continuous rAF/streaming — hangs to timeout or races. Use `'load'` + existing selector/warmup wait. | `inspect-threejs-canvas.mjs:100` |
| U6 | P1 | Failures before `sampleCanvas` (no canvas, nav timeout — the most common real failures) write no structured report; caller gets no machine-parseable reason. Wrap in try/catch and always emit a report with `reason`. | `inspect-threejs-canvas.mjs:100-101,127-130` |
| U7 | P1 | Two divergent copies of the inspector (qa-release + scaffold) maintained separately, currently identical but no equality guard. Every bug above must be fixed twice. Make one canonical + CI diff check. | both `inspect-threejs-canvas.mjs` |
| U8 | P2 | `--wait` with a bad/missing value → `Number()` NaN → `waitForTimeout(NaN)` resolves immediately, skipping warmup. Validate finite ≥ 0. | `inspect-threejs-canvas.mjs:20,102` |
| U9 | P2 | `fullPage: true` on a viewport-fixed WebGL canvas can trigger a resize mid-capture and misrepresent framing. Use `fullPage: false`. | `inspect-threejs-canvas.mjs:106` |
| U10 | P2 | Performance-check boundary between debug-profiler (diagnose/optimize) and qa-release (record/gate) is correct but never stated — add a one-line handoff to each. | `qa-release-checklists.md:72-82` vs `debug-profile-checklists.md:97-139` |
| U11 | P2 | A few checklist items are subjective/un-checkable (contrast "legible", FPS "after warmup", "generic dashboard styling"). Attach concrete thresholds (WCAG ≥ 4.5:1; ≥ 55 fps desktop / ≥ 30 mobile over 3s after 2s warmup; ~44 CSS px touch targets — already in `ui-patterns.md:69`). | multiple checklists |
| U12 | P2 | SKILL descriptions overlap on "mobile/screenshots/console" — front-load distinguishing verbs (design / diagnose / verify-and-gate). | three `SKILL.md:3` |

---

## `threejs-3d-generator` / `threejs-image-generator` / `threejs-audio-generator`

Credit-spending scripts — bugs here cost real money.

| # | Pri | Finding | Anchor |
|---|-----|---------|--------|
| X1 | **P0** | Tripo polling treats missing/unknown `status` as terminal (`"unknown"` is in `FINAL_STATUSES`) → spurious hard failure that also wastes already-spent credits. Drive the loop off an explicit `ONGOING = {queued, running}` set; keep polling on unknown until timeout. | `threejs-3d-generator/scripts/threejs_3d_asset.py:17,184` |
| X2 | **P0** | Gemini uses fragile `response.parts` shortcut → opaque `AttributeError` on safety-block/empty instead of a reason. Read `candidates[0].content.parts`; surface `finish_reason`/`block_reason`. | `threejs-image-generator/scripts/generate_image.py:127` |
| X3 | P1 | No retry/backoff on 429/5xx/transient network in any script — a single blip aborts a multi-minute paid pipeline. Add bounded exponential backoff for `URLError` + 429/5xx; leave 4xx non-retried. | all three scripts (`threejs_3d_asset.py:110`, `threejs_audio_asset.py:60`, `generate_image.py:113`) |
| X4 | P1 | `download_url` reads whole body, writes directly to the final path, clobbers silently — a crash mid-write leaves a truncated GLB that later loads fail on confusingly. Stream to `.part` + `os.replace()`. | `threejs_3d_asset.py:221-230` |
| X5 | P1 | `character-pipeline` can reference an unbound `candidate_id` on total rig-submit failure (`NameError` / stale ID fed to retarget). Init `candidate_id = None` and guard. | `threejs_3d_asset.py:694-703` |
| X6 | P1 | `animate_retarget` sets `out_format` twice; the second (`if args.out_format`) can override the forced `fbx`, defeating the documented corruption guard. Compute `out_format` once. | `threejs_3d_asset.py:489-525`; `SKILL.md:191` |
| X7 | P1 | `wait_for_task` timeout strands an in-flight paid task with no resume hint. Include `status/download TASK_ID` in the error; consider `--timeout 0` for detailed+rig+retarget runs (900s may be short). | `threejs_3d_asset.py:189-190` |
| X8 | P2 | Gemini `gemini-3-pro-image-preview` + `image_config.image_size` are version-fragile with only a `>=1.0.0` SDK pin and no fallback; also no request timeout (can hang the pipeline). Pin a floor version; retry without `image_config` on unknown-field; set an `http_options` timeout. | `generate_image.py:5,114-122` |
| X9 | P2 | Audio `voice-change`/`isolate` don't validate input size/type before upload (Tripo image path does). Mirror the guard. | `threejs_audio_asset.py:97-107` |
| X10 | P2 | Unguarded `json.loads` on 200 responses — an HTML 502/proxy page throws a raw traceback instead of the domain error. Wrap parses. | `threejs_3d_asset.py:118,158,264`; `threejs_audio_asset.py:155` |
| X11 | P2 | Defensive key-scrub: no script leaks the key today, but add `str(exc).replace(key, "***")` in each `main()` handler as cheap insurance for secret-handling scripts. | `threejs_3d_asset.py` / `threejs_audio_asset.py` main handlers |
| X12 | P2 | Output paths (`--out`/`--filename`/`--out-dir`) accept absolute/`..` with no confinement — assets can land outside the project. Warn/refuse on escape; note paths are CWD-relative. | audio `write_file:133`; image `generate_image.py:78`; Tripo out-dir |
| X13 | P2 | Three SKILLs each hand-roll slightly different `zsh -c 'source ...'` credential wrappers that `probe_asset_credentials.sh` already solves; scripts still read only `os.environ`. Document one canonical wrapper (or have the probe emit it). | 3d `SKILL.md:33-37`, image `SKILL.md:45-49`, audio `SKILL.md:46-50` |

**Note:** endpoints, auth headers (`Bearer` Tripo / `xi-api-key` ElevenLabs), payload shapes, exit
codes, and `--help` all check out. No key is written into browser-side game code anywhere.

---

## Suggested order of work

1. **Audit hardening** (D1, D2, D4, D5) — one root cause (labels→values); makes the whole enforcement layer real.
2. **Scaffold bugs** (G1, G2, G3; then G4–G6) — the code agents copy most.
3. **Inspector** (U2, U3, U5, U6, U8, U9) + de-dupe the two copies (U7).
4. **Credit-wasting generator bugs** (X1, X2) + resilience (X3, X4).
5. **Dedup/drift** (A3, U1, D6, D8, A6) — collapse the diverging copies.
6. **Graphics currency + verifiability** (A1, A2, A4, A5) and remaining P2 polish.

Nothing here changes the package's architecture — these are sharpening edits. The strongest parts
(art-direction discipline, physics decision ladder, the scaffold's materials/lighting/testing
foundation) stay as-is.
