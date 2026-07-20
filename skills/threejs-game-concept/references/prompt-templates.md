# Prompt Templates

Reusable prompts for the concept/ideation phase. Load only when the user wants a reusable template.

## Brainstorm distinct directions

```text
I want to make a browser game about [theme/feeling/reference]. Propose 3 distinct concept
directions (different genre or feel), each as: a one-line high concept, the player fantasy,
the core verb, and why it is fun. Keep all three achievable in real-time Three.js on desktop
and mobile. Then recommend one and say why.
```

## Turn an idea into a core loop

```text
Here is my idea: [idea]. Write the one-sentence core loop with all six parts — verb, objective,
pressure, reward, fail state, restart. If the idea is too broad to state in one sentence, tell me
what to cut to focus it.
```

## Produce the full GDD

```text
Use threejs-game-concept to write a full Game Design Document for [concept] into
docs/game-design.md: high concept, 3 pillars, core loop, mechanics, desktop + mobile controls,
progression and fail/win, world, art direction, audio direction, UI/HUD states, an asset map
tagged by generator, scope tiers with a vertical slice to build first, Three.js technical notes,
risks, and milestones.
```

## Scope check an existing idea

```text
Review this game idea for browser feasibility and scope: [idea]. Flag anything that fights a
real-time WebGL budget on mid mobile, propose the cheaper path for each, and define the smallest
vertical slice that proves the loop is fun.
```

## Hand off to the build

```text
The GDD is in docs/game-design.md. Use threejs-game-director to build the vertical slice first,
then iterate to the target build with the gameplay, graphics, UI, asset, audio, debug, and QA
skills.
```
