# Performance-Safe Visual Detail Checklist

Also apply the Every-Pass Baseline in `aaa-game-quality-gate.md` (diagnostics, desktop/mobile screenshots, instancing/shared resources).

- Draw calls, triangles, geometries, materials, textures, and frame time are reviewed after changes.
- High segment counts are limited to silhouette-critical forms.
- Shadows are scoped by light count, shadow map size, casters/receivers, and camera distance.
- Post-processing is justified by gameplay readability or strong art direction.
- DPR is capped to the canonical value in `render-recipes.md` (Renderer Setup), or adaptive quality is used for mobile.
- Generated resources have a disposal/reuse strategy.
- The worst-case gameplay scene, not only idle view, is inspected.
- Visual detail remains readable at mobile resolution without excessive GPU cost.
