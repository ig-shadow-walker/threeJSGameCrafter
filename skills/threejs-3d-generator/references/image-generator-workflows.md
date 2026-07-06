# Three.js Image Generator Pairing

Use `threejs-image-generator` when a strong 2D input improves `threejs-3d-generator` output or when the final asset is 2D rather than 3D. The default image provider is Alpha3D (FLUX), available via the same MCP connector or `ALPHA3D_API_KEY`; Gemini or another provider can be substituted.

## 2D To 3D Reference Images

Generate clean reference images before image-to-3D for:

- Characters: full-body T-pose or A-pose, neutral expression, visible hands/feet, no cropped limbs.
- Creatures: side/front silhouettes, clear limb count, readable anatomy.
- Vehicles: front/side/three-quarter concepts, clear wheels/thrusters/wings, material zones.
- Buildings: front elevation, roof silhouette, doors/windows, scale cues.
- Weapons/tools: side view, readable handle/blade/barrel proportions, material callouts.
- Props/pickups: centered object, plain background, strong silhouette, no text baked in unless wanted.
- Terrain/world modules: tileable rocks, cliffs, rails, gates, arena pieces, modular set dressing.

Prompt pattern:

```text
Create a clean 3D-generation reference image of [asset]. Centered single object, plain light background, full object visible, readable silhouette, [style], [materials], no motion blur, no cropped parts.
```

For riggable characters:

```text
Create a full-body T-pose character reference for 3D rigging: [character details]. Arms out, legs visible, symmetrical stance, plain background, front-facing, readable costume layers.
```

## Texture And Material References

Use `threejs-image-generator` for:

- Terrain albedo references: rock, sand, mud, snow, moss, cracked asphalt.
- Sci-fi trim sheets, panel lines, decals, hazard stripes, window bands.
- Metal, leather, fabric, glass, ceramic, wood, painted plastic, worn armor.
- Sky, clouds, nebula, city haze, horizon plates, menu backgrounds.
- Faction marks, logos, numbers, signs, pickup icons, hazard labels.

Prompt pattern:

```text
Create a seamless game texture reference for [surface], top-down/orthographic, no perspective, no strong shadows, PBR-friendly color, [style/material details].
```

## UI And Logo Use Cases

Use `threejs-image-generator` directly, not 3D generation, for:

- Logos and faction marks.
- HUD icons, item icons, ability icons, pickup symbols.
- Menu backgrounds and loading illustrations.
- Button/icon textures, decals, title art, achievement badges.
- 2D sky/backdrop cards when a 3D model is unnecessary.

## 3D Generator Handoff

After generating a 2D reference:

1. Save the image in the working project, usually `assets/concepts/`.
2. Path B: run the `threejs-3d-generator` `image` command with `--image <path>` (it presigns + uploads the local file, then submits `image_to_3d`). For several angles of one object, use `multiview` with `--front/--back/--left/--right`.
3. Path A: pass the image URL to the MCP `generate_3d` tool (`image_url` or `multi_view_images`).
4. Keep `--quality pbr --output textured` when visual fidelity matters; drop to `low_poly`/`--output geometry` for background props.
5. Download generated 3D outputs immediately after success — URLs expire.

## Avoid

- Crowded scene images for single-object 3D generation.
- Cropped limbs, hidden backs, extreme perspective, motion blur, or heavy depth of field.
- Tiny UI/logo text in 3D model textures unless text fidelity is noncritical.
- Using 3D generation for pure 2D UI assets.
