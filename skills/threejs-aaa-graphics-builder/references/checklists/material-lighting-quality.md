# Material and Lighting Quality Checklist

Also apply the Every-Pass Baseline in `aaa-game-quality-gate.md` (diagnostics, desktop/mobile screenshots, instancing/shared resources).

- Renderer color space, tone mapping, exposure, and shadow settings are intentional.
- Key, fill, rim, ambient, and environment lighting clarify depth and gameplay roles.
- Materials avoid flat default looks through roughness/metalness/emissive/vertex-color variation.
- Important objects have readable silhouettes against background, fog, and effects.
- Shadows help ground assets without obscuring navigation or collision boundaries.
- Fog, bloom, particles, and post-processing support readability instead of hiding it.
- Procedural textures or decals are scaled, stable, and not visually noisy during movement.
- Materials are disposed when obsolete.
