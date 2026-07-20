---
name: threejs-game-concept
description: "Ideate and scope a Three.js browser game and write its Game Design Document before building. Use for new game ideas, brainstorming a concept, 'what game should I make', defining the core loop, pillars, player fantasy, mechanics, controls, progression and fail states, world and art direction, audio direction, UI needs, scope tiers from MVP to premium, and an asset list. Start here for from-scratch or vague requests, then hand the GDD to threejs-game-director for the playable build. Keeps concepts achievable in a real-time browser: WebGL budget, desktop and mobile, vertical slice first."
---

# Three.js Game Concept

## Purpose

Turn a rough idea (or a blank page) into a clear, buildable game concept and a written Game Design Document (GDD). This is the pre-production layer of the Three.js game system. Its output is the input the rest of the pipeline needs: `threejs-game-director` reads the GDD's core loop for its playable contract, and the GDD's asset list drives the external asset sourcing decisions for `threejs-3d-generator`, `threejs-image-generator`, and `threejs-audio-generator`.

Design for what a browser can actually run in real time. A concept that cannot hit frame rate on a mid mobile device is not done — it is a wish.

## When To Use

- New game from scratch, or a vague request ("make me a cool game", "what should I build").
- The user has an idea but no defined loop, scope, or plan.
- A game needs a design reset — unclear objective, no fail state, scope creep.

Skip or keep it light for: fixing a bug, a single visual/UI pass, or an existing game whose direction is already clear. In those cases go straight to the relevant specialist or `threejs-game-director`.

## Output

Write the GDD into the user's project at `docs/game-design.md` (create the folder if needed) using the structure in `references/gdd-template.md`. It is a living document — update it as decisions change. Keep it concise and decision-dense, not a novel.

## Reference Gate

- Load `references/ideation-workflows.md` before ideation: discovery questions, the high-concept formula, pillars, core-loop framing, genre menu, art/audio direction, scope tiers, and Three.js feasibility limits.
- Load `references/gdd-template.md` before writing the document.
- Load `references/checklists/concept-definition-of-done.md` before declaring the concept ready to build.

Record these in the reference ledger (yes/no, path). Do not hand a concept to the director while a required reference was skipped.

## Workflow

1. **Discover.** Ask only the questions that change the design: player fantasy and target feeling, genre/reference games, platform (assume desktop + mobile browser unless told otherwise), scope and time budget, art direction, and any hard constraints. Do not interrogate — 4 to 7 sharp questions, then propose. If the user is unsure, offer 2 to 3 distinct concept directions and let them pick.
2. **Concept.** Write a one-line high concept, the player fantasy, the unique hook, and 3 design pillars (the values every decision serves).
3. **Core loop.** Define the one-sentence loop the director needs: player verb, objective, pressure, reward, fail state, restart. If you cannot state it in one sentence, the concept is not focused enough yet.
4. **Systems and content.** Mechanics, controls (desktop AND mobile/touch), progression/objectives/difficulty, world/setting, art direction, audio direction, and the UI/HUD states the game needs.
5. **Scope tiers.** Define an MVP (vertical slice — the smallest thing that proves the loop is fun), a target build, and stretch goals. Name what is explicitly out of scope. Recommend building the vertical slice first.
6. **Asset map.** List the high-value assets and tag each as procedural / image-generator / 3D-generator / audio-generator / hybrid. This becomes the director's external asset sourcing ledger — you are pre-filling it.
7. **Feasibility and risks.** Flag anything that fights a browser real-time budget (huge worlds, heavy physics, many unique high-poly meshes, expensive post) and propose the cheaper path. List the top risks and how the vertical slice de-risks them.
8. **Write and hand off.** Save the GDD, summarize the loop and scope, and hand off: "use `threejs-game-director` to build the vertical slice from `docs/game-design.md`."

## Three.js Feasibility Rules

- Target 60 fps desktop, 30+ fps mid mobile; keep a WebGL/WebGL2 fallback in mind.
- Prefer one strong hero asset plus instanced/procedural set dressing over many unique heavy models.
- Bound world size and draw calls; stream or cull rather than render everything.
- Treat heavy rigid-body physics, large crowds, and unchecked post-processing as scope risks to justify, not defaults.
- Every mechanic must map to a concrete input on both desktop and touch, or it is cut or redesigned.

## Handoff And Report

Report: the reference ledger, the one-line high concept, the one-sentence core loop, the 3 pillars, the scope tiers with the recommended vertical slice, the asset map (with generator tags), the top risks, and the path to the saved GDD (`docs/game-design.md`). End by naming the next step: build the vertical slice via `threejs-game-director`.
