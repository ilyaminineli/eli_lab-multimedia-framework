# eli_lab Production Pipeline

eli_lab treats a project as a living production workspace rather than a fixed folder template.

## Workflow

1. Scan an existing project.
2. Recognize its hierarchy and classify it as canonical, legacy, mixed, or unknown.
3. Discover Projects, Characters, Locations, Assets, Scenes, Scripts, and Test Scenes.
4. Generate factual metadata from the files already present.
5. Review a safe normalization plan before moving anything.
6. Normalize only high-confidence structure and never overwrite an existing destination.
7. Generate entity records and preset Markdown documentation.
8. Continue using the existing asset, validation, automation, analysis, and task services.

## Preset documentation

- `project` — human-friendly project README and inventory
- `catalogue` — entity catalogue
- `pipeline` — structure and pipeline report
- `compact` — concise overview

## Legacy projects

Legacy layouts are inputs, not failures. The normalizer recognizes loose Blender files, loose textures, UUID-style asset folders, and scene-local asset directories. Ambiguous material or texture relationships are reported for review rather than moved automatically.
