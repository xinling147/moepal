# Cat Sprite Pack

This directory contains the first cat desktop companion sprite concepts.

Required frame rules:

- Use transparent PNG files.
- Use `frame_000.png`, `frame_001.png`, ... naming.
- Keep all frames in one action directory at the same canvas size.
- Do not include blue backgrounds, rounded cards, drop shadows, checkerboards, UI icons, or screenshots.
- Runtime-ready frames should be 256x256 PNG; the app scales them to the configured pet size.

Current animated actions:

- `idle_lie/`: 8 subtle breathing frames.
- `sleep/`: 6 slower breathing frames.
- `peek/`: 8 side-peek frames.
- `nudge/`: 8 small attention-seeking frames.
- `tail_wag/`: 8 gentle movement frames.
- `happy_bounce/`: 8 small bounce frames.
- `look_around/`: 6 side-to-side frames.
- `sit_wait/`: 6 quiet waiting frames.

Frames are generated from the first project-local concept images with:

```powershell
.venv312\Scripts\python.exe tools\generate_cat_sprite_frames.py
```

The original built-in generated images remain under the Codex generated image cache. The files here are project-local processed copies for the app.
