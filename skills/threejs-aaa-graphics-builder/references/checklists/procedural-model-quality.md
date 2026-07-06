# Procedural Model Quality Checklist

Also apply the Every-Pass Baseline in `aaa-game-quality-gate.md` (diagnostics, desktop/mobile screenshots, instancing/shared resources).

- The model has a recognizable silhouette from the gameplay camera.
- Primary forms read clearly before material or post-processing detail.
- Secondary detail supports the asset role: panels, trims, ridges, tubes, fins, sockets, decals, or emissive accents.
- Tertiary detail is visible at intended camera distance and does not create noise.
- Materials have purposeful contrast in roughness, metalness, color, emissive, or texture.
- Bevels, curves, and segment counts improve silhouette or highlight behavior.
- Visual mesh and gameplay collision/proxy are intentionally separated when needed.
- The factory returns named groups/meshes and keeps ownership/disposal clear.
- The asset still reads as more than a primitive placeholder at mobile resolution.
