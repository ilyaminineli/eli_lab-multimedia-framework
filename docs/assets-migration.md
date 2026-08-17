# Asset subsystem migration

The asset subsystem is the next framework layer after project management.

## Architecture

```text
Legacy GUI
   ↓
root-level adapter
   ↓
src/eli_lab/assets/
   ├── textures.py
   └── optimization.py
```

The GUI is responsible for Tkinter state, dialogs and presentation only. Asset services own filesystem operations, Pillow processing and pngquant execution.

## Texture conversion

`eli_lab.assets.convert_textures()` converts supported image formats to PNG and preserves originals by default. Replacing the source requires an explicit `replace_original=True` argument.

## Texture optimization

`eli_lab.assets.optimize_textures()` uses `pngquant` when it is available on `PATH`. The service returns a result for every file instead of showing GUI dialogs itself.

The GUI adapter uses `root.after()` to marshal progress and completion back to Tkinter's main thread.

## Next steps

- add Blender template management under `eli_lab.assets.blender`
- move custom file renaming into `eli_lab.automation`
- add richer asset validation
- add CLI commands for conversion and optimization
- add tests for pngquant behavior and collision handling
