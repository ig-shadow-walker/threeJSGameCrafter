# Ideation Workflows

Turn a rough idea into a focused, buildable browser-game concept. Use these tools in order; stop asking and start proposing once the loop is clear.

## Discovery Questions

Ask only what changes the design (4 to 7 max), then propose. Good prompts:

- What should the player *feel* — speed, mastery, tension, calm, power, discovery, chaos?
- What is the player's fantasy — who are they and what do they do?
- Any reference games or moments ("like the boost in X", "the vibe of Y")?
- Platform: desktop, mobile, or both? (Default: both, browser.)
- How big is this — a weekend prototype, a polished showcase, or a full game? How much time?
- Art direction: stylized, realistic, low-poly, neon, hand-drawn, minimalist?
- Any hard constraints — no violence, must be one-handed mobile, must run on weak devices, a theme/brief?

If the user is unsure, offer 2 to 3 distinct directions (different genre/feel), each with a one-line pitch, and let them choose or remix.

## High-Concept Formula

One sentence that sells the game:

> A [genre] game where you [core verb] to [objective] while [pressure], set in [world].

Example: "A low-poly hover-racing game where you drift through neon canyons to beat rivals while your boost overheats, set on a derelict orbital ring."

Also capture:

- **Player fantasy:** the one-line role/power the player lives out.
- **Unique hook:** the one thing that makes this not a clone — a mechanic twist, a constraint, a combination.

## Design Pillars

Pick 3 pillars — the values every design decision must serve. Examples: "Always in motion", "Readable at a glance", "One more run". When a feature does not serve a pillar, cut it. Pillars are the tie-breaker for scope fights.

## Core Loop (the director's contract)

State the loop in ONE sentence with all six parts. If you cannot, the concept is not focused enough:

- **Verb:** the primary action (drive, build, dodge, stack, shoot, sing, sort).
- **Objective:** what the player is trying to achieve moment to moment.
- **Pressure:** what pushes back — timer, enemies, resource drain, rising difficulty.
- **Reward:** what the player gains — score, upgrades, territory, story, juice.
- **Fail state:** how a run ends badly.
- **Restart:** how the player re-enters quickly (arcade loops live or die on this).

## Genre Menu (browser-friendly)

Fast starting points that run well in Three.js: endless runner, arcade racer/flyer, wave survival/shooter, tower defense, physics puzzle (mini-golf, marble, stacking), collectathon/platformer, top-down arena, rhythm/reactive, sandbox/builder (bounded), roguelike run. Note the genre so the director can load the right checklist (e.g. the endless-runner checklist).

## Mechanics, Controls, Progression

- **Mechanics:** list the 3 to 6 verbs/systems that create the loop. Cut anything that is not in service of a pillar.
- **Controls:** every mechanic must map to a concrete input on BOTH desktop (keys/mouse) and mobile (touch/tilt/on-screen). If a mechanic has no clean touch mapping, redesign or cut it.
- **Progression:** how difficulty/interest ramps — speed, density, new enemy types, upgrades, levels, score thresholds. Define win/end conditions and how a session ends.

## Art And Audio Direction

- **Art:** palette, mood, lighting feel, silhouette language, reference images. Keep it achievable — a strong, consistent stylized look beats an inconsistent realistic one.
- **Audio:** music mood, key SFX (the "juice" moments), ambience, UI sounds, any voice. Note which are essential to the feel.

## Scope Tiers

Define three tiers and what is explicitly OUT:

- **MVP / vertical slice:** the smallest build that proves the loop is fun — one level/area, core verb, one fail state, restart, placeholder-but-readable visuals. Build this first.
- **Target:** the shippable version — full loop, real art/audio, HUD/menu states, mobile, polish.
- **Stretch:** nice-to-haves that must not block the target.

Always recommend building the vertical slice first and playtesting the loop before investing in assets.

## Asset Map (pre-fills the director's sourcing ledger)

List high-value assets and tag each source so the director/generators can act:

- Hero/player, enemies/vehicles/weapons, signature props/pickups, world/sky/background, materials/textures/decals, logos/icons/GUI art, SFX/ambience/voice.
- Tag each: procedural / `threejs-image-generator` / `threejs-3d-generator` / `threejs-audio-generator` / hybrid.

## Three.js Feasibility

- 60 fps desktop, 30+ fps mid mobile; keep a WebGL/WebGL2 fallback in mind.
- One hero asset + instanced/procedural set dressing beats many unique heavy meshes.
- Bound world size, draw calls, and unique materials; cull/stream rather than render everything.
- Heavy rigid-body physics, large crowds, and stacked post-processing are scope risks to justify — not defaults.
- If a concept needs an open world, thousands of agents, or film-grade rendering, scope it down to the browser-real-time version and say so.

## Risks

List the top 3 risks (design, technical, or scope) and how the vertical slice de-risks each. "Is the loop actually fun?" is almost always risk #1 — the slice answers it before art spend.
