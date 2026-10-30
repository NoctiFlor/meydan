# MEYDAN asset source policy

MEYDAN uses original work and assets with a licence that explicitly permits use in
the game. Jadde files, music, character models, animations, textures, maps, UI
art, or extracted client content must never be imported.

## Preferred sources

| Source | Candidate | Licence shown by publisher | Intended use |
|---|---|---|---|
| Quaternius | [Universal Base Characters](https://quaternius.com/packs/universalbasecharacters.html) | CC0 on the pack page | Primary modular player/NPC base. Six base bodies, twenty hairstyles, humanoid rig, glTF/FBX/Blend, approximately 13k triangles per base character. |
| Quaternius | [Universal Animation Library](https://quaternius.com/packs/universalanimationlibrary.html) | CC0 on the pack page | Locomotion, sitting, emotes and social actions. Select only the clips used by the game. |
| Quaternius | [Universal Animation Library 2](https://quaternius.com/packs/universalanimationlibrary2.html) | CC0 on the pack page | Optional second animation source after the first library has been audited and integrated. |
| Quaternius | [Ultimate Modular Men](https://quaternius.com/packs/ultimatemodularcharacters.html) | CC0 on the pack page | Additional modular male NPC variety, subject to rig/texture optimisation. |
| Kenney | [Mini Characters](https://kenney.nl/assets/mini-characters) | CC0 | Low-detail distant NPCs or LOD references; not the preferred visual style for the main avatar. |
| Kenney | [Animated Characters Protagonists](https://kenney.nl/assets/animated-characters-protagonists) | CC0 | Prototyping and distant NPC roles when the style fits. |
| Kenney | [Building Kit](https://kenney.nl/assets/building-kit) | CC0 | Modular, mobile-friendly building pieces. Restyle materials to match MEYDAN. |
| Kenney | [Mini Market](https://kenney.nl/assets/mini-market) | CC0 | Lightweight shop and market props. |
| Hugging Face | [three-ws/avatars](https://huggingface.co/three-ws/avatars) | MIT shown on the repository card | Existing/reference GLB avatars only after checking the exact file history and included licence. `michelle.glb` is documented as about 28k triangles with a SambaDance clip. AI-generated avatars in the repository are not automatically approved. |

Publisher pages do not consistently publish archive or per-model file sizes. Do
not estimate or record invented sizes. Measure each downloaded file locally and
add the measured result to its asset manifest.

## Licence handling

- Store the licence file shipped in every downloaded archive under
  `licenses/<source>/<pack>/` before integrating an asset.
- Record the source URL, download date, author/publisher, exact pack name,
  licence identifier and original filename in an asset manifest.
- Prefer CC0 assets. Attribution is still welcome in project credits even when it
  is not required.
- Quaternius currently publishes a Quaternius Asset License as well as pack pages
  marked CC0. Preserve the licence that actually ships with the downloaded pack.
  The QAL permits use and modification in products but prohibits redistributing
  the raw assets as a standalone asset pack.
- Kenney states that assets on its asset pages are CC0 and may be used
  commercially without required attribution. Preserve the included licence.
- A repository-level licence does not prove that every uploaded AI-generated
  likeness, texture or input was cleared. Assets with unclear provenance, a
  recognisable person, trademark, or third-party character must be rejected.
- Do not imply that Quaternius, Kenney, Hugging Face, or any asset author endorses
  MEYDAN.

## Prohibited sources and uses

- No extracted Jadde or other game-client assets, even if a download link exists.
- No commercial music, copied beatmaps, logos, brand names, celebrity likenesses,
  or recognisable copyrighted characters.
- No asset whose licence is missing, ambiguous, non-commercial, or incompatible
  with distributing the complete offline APK/HTML package.
- No redistribution of a third-party pack as a downloadable source-asset bundle.
- No automatic bulk import directly into the release. Every selected asset must
  pass the checklist below.

## Mobile character and crowd budget

These are initial budgets, not claims about measured device performance:

- Main/near avatar target: about 13k triangles, with a documented upper bound of
  30k only when profiling proves it is safe.
- Near NPC target: at most about 13k triangles.
- Mid/far NPC LOD target: 2k–5k triangles or an equivalent simplified mesh.
- Visible crowd target: 8–12 NPCs on the initial quality profile.
- Simultaneously active animation mixers: 2–4; pause or update distant NPCs at a
  reduced rate.
- Prefer a shared humanoid skeleton, shared materials, texture atlases and cloned
  skinned meshes over unique rigs/materials for every NPC.
- Remove unused animation clips, hidden geometry and oversized textures.
- Use compressed, power-of-two textures sized for their on-screen importance;
  avoid large transparent layers.
- Add distance culling and LOD before increasing crowd density.

## Download and integration checklist

- [ ] Download from the publisher's official page or repository.
- [ ] Save the original archive checksum and download date.
- [ ] Inspect and preserve the licence included in the archive.
- [ ] Verify that the exact model/texture/animation is covered by that licence.
- [ ] Record measured archive, source and final GLB sizes; do not estimate them.
- [ ] Inspect file contents for unexpected scripts, executables or external URLs.
- [ ] Open the source in Blender or a trusted glTF viewer before conversion.
- [ ] Record triangle count, materials, textures, bones and animation clips.
- [ ] Check scale, orientation, root motion, skeleton names and animation retargeting.
- [ ] Remove unused clips, meshes, materials and texture channels.
- [ ] Create near and distant LODs where the asset will appear in a crowd.
- [ ] Convert/export to glTF/GLB without unsupported runtime extensions.
- [ ] Test the asset offline in standalone HTML and the Android package.
- [ ] Profile FPS, frame time, memory and load time on a physical Android phone.
- [ ] Confirm that player movement, second-pointer camera and dance input tests
      still pass.
- [ ] Add source/licence credit metadata to the project before release.

## Recommended first import

Start with one female and one male Universal Base Character plus only idle, walk,
run, sit, wave and dance-invite clips from the Universal Animation Library. Build
the shared rig, LOD and licence pipeline with those two assets before importing a
larger crowd. Existing MEYDAN models remain the fallback until the new assets pass
real-device profiling.
