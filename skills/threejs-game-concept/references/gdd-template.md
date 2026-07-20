# Game Design Document Template

Copy this into the user's project at `docs/game-design.md` and fill it. Keep it concise and decision-dense — every line should inform the build. It is a living document; update it as decisions change.

```markdown
# [Game Title] — Game Design Document

## 1. High Concept
One sentence: a [genre] game where you [core verb] to [objective] while [pressure], set in [world].

- Player fantasy:
- Unique hook:
- Platform: desktop + mobile browser (Three.js)
- Scope target: prototype / polished / full — and rough time budget

## 2. Pillars
Three values every decision serves.
1.
2.
3.

## 3. Core Loop
One sentence with all six parts:
- Verb:
- Objective:
- Pressure:
- Reward:
- Fail state:
- Restart:

## 4. Mechanics
The 3–6 systems that create the loop. For each: what it does and which pillar it serves.
-

## 5. Controls
Every mechanic mapped to concrete inputs.
| Action | Desktop | Mobile / touch |
| --- | --- | --- |
|  |  |  |

## 6. Progression & Objectives
- Session goal / win condition:
- Difficulty ramp (speed / density / new types / upgrades / levels):
- How a session ends and how the player restarts:

## 7. World & Setting
Setting, tone, level/space structure, camera model (first/third/top-down/fixed).

## 8. Art Direction
Palette, mood, lighting feel, silhouette language, reference images. Keep it achievable and consistent.

## 9. Audio Direction
Music mood, key SFX ("juice" moments), ambience, UI sounds, voice. Mark which are essential.

## 10. UI / HUD
States the game needs: gameplay HUD, pause, settings, fail/retry, win/milestone, loading/error, touch controls. What each must show.

## 11. Asset Map
High-value assets and their source (procedural / image-generator / 3D-generator / audio-generator / hybrid). This pre-fills the director's external asset sourcing ledger.
| Surface | Needed | Source |
| --- | --- | --- |
| Hero / player |  |  |
| Enemies / vehicles / weapons |  |  |
| Signature props / pickups |  |  |
| World / sky / background |  |  |
| Materials / textures / decals |  |  |
| Logos / icons / GUI art |  |  |
| SFX / ambience / voice |  |  |

## 12. Scope Tiers
- MVP / vertical slice (build first): 
- Target build: 
- Stretch (must not block target): 
- Explicitly OUT of scope: 

## 13. Technical Notes (Three.js)
Performance budget (target fps desktop/mobile), physics approach (none / custom / Rapier / cannon-es), renderer/post-processing plans, WebGL fallback, and any heavy features that need a cheaper path.

## 14. Risks
Top 3 risks (design / technical / scope) and how the vertical slice de-risks each.

## 15. Milestones
- Vertical slice: 
- Target build: 
- Polish / release: 
```
