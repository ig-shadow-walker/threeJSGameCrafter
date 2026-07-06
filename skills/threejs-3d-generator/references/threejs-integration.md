# Three.js Integration

Use this after `threejs-3d-generator` generates or edits a model (via the MCP connector or the API-key script).

## Preferred Outputs

- Three.js runtime: GLB/PBR model first.
- Animation/game-engine interchange: FBX when a tool needs it, then convert/import carefully.
- Static web asset exchange: GLTF/GLB.
- 3D print only: STL, not for textured game runtime.
- Apple AR: USDZ.

## Import Pattern

Use `GLTFLoader`:

```ts
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const loader = new GLTFLoader();
const gltf = await loader.loadAsync('/assets/models/asset/model.glb');
scene.add(gltf.scene);
```

For rigged/animated meshes, drive an `AnimationMixer`:

```ts
const mixer = new THREE.AnimationMixer(gltf.scene);
const action = mixer.clipAction(gltf.animations[0]);
action.play();

// in loop
mixer.update(deltaSeconds);
```

Animation intake notes:

- Alpha3D auto-rigging produces an armature and skin weights but does **not** bake preset animation clips. A freshly rigged GLB usually has an empty or minimal `gltf.animations`. Supply motion yourself: your own authored clips, an external library (e.g. via `SkeletonUtils.retargetClip`), or procedural bone motion.
- Log the skeleton and clips after load: `gltf.animations.map(c => `${c.name} ${c.tracks.length} tracks`)`, and walk the bone hierarchy once to confirm symmetric limb chains. A rig with a missing or single-bone limb warps every clip you retarget onto it — regenerate the mesh from a cleaner T-pose rather than fighting it at runtime.
- If you convert to FBX for an external animation tool, `FBXLoader` lives at `three/addons/loaders/FBXLoader.js` and imports `fflate` (bundlers resolve it from npm; import-map/CDN pages must map `fflate`). FBXLoader produces Phong materials (darker than GLB PBR) — for final art parity, animate on the GLB or convert back offline (Blender / FBX2glTF).
- If a clip carries baked root motion and you want in-place locomotion, zero only the horizontal (X/Z) components of the root bone's position track and keep Y (vertical motion is the jump/gait bob), then drive locomotion from gameplay code:

```ts
for (const clip of clips) {
  for (const tr of clip.tracks) {
    if (!tr.name.endsWith('.position')) continue;
    // only the top root bone; skip if your rig names it differently
    const v = tr.values, x0 = v[0], z0 = v[2];
    for (let i = 0; i < v.length; i += 3) { v[i] = x0; v[i + 2] = z0; }
  }
}
```

## Asset Intake Checklist

Inspect before shipping:

- File size.
- Triangle count.
- Mesh count.
- Material count.
- Texture count and texture dimensions.
- PBR material behavior under the game lighting rig.
- Scale in meters and normalization assumptions.
- Pivot/origin and bounds.
- Collision proxy separate from the detailed mesh.
- Animation clip names, durations, and root-motion behavior.
- Mobile memory/performance impact.

## Game Asset Strategy

- Use `threejs-3d-generator` for hero assets, characters, creatures, bosses, buildings, weapons, signature props, and complex pickups.
- Use procedural Three.js kits for high-volume repeated detail such as bolts, windows, track plates, rails, debris, markers, and background silhouettes.
- Use `threejs-image-generator` for concept art, texture references, decals, logos, UI icons, and backdrop images.
- Combine: image-generator concept → 3D-generator model → Three.js import → procedural set dressing → visual scorecard.

## Performance Discipline

- Use `low_poly`, `face_count`, `convert`, or a `retopology` pass for browser/mobile budgets.
- Prefer one high-fidelity hero asset plus instanced/procedural supporting detail over many unique heavy models.
- Keep textures compressed or reasonably sized.
- Clone carefully; share geometry/materials when possible.
- Dispose loaded assets when leaving scenes.
- Run renderer diagnostics after importing: calls, triangles, geometries, textures, materials, file sizes.

## Common Fixes

- Model too large/small: normalize bounds in an asset wrapper group.
- Wrong orientation: set a wrapper rotation on import.
- Materials too dark/bright: check output color space, tone mapping, environment, and light exposure (see the graphics skill's render recipes for physically-based light units).
- Collision too complex: build primitive proxies in Three.js and keep the generated mesh visual-only.
- Rig looks broken: validate the skeleton (symmetric limb chains, head, feet) before wiring gameplay; regenerate from a cleaner T-pose if a limb chain is missing.

## Final Evidence

Report:

- Integration path (MCP or API key) and job IDs.
- Downloaded asset paths.
- Generation options (quality, output, face count) and any edit jobs (texture, rig, retopology, convert).
- Three.js import files changed.
- Renderer diagnostics before/after import.
- Screenshot evidence in active gameplay.
