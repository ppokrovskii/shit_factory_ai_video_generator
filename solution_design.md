### Goal
Generate short transition videos between ordered images.

### CLI
- --src: image dir; --out: out dir (default ./.out)
- --duration: seconds (float)
- --provider: veo (default), switchable; --dry-run; --verbose {0,1,2}
- --prompts: path to JSON prompts (optional)
- --img-gen: enable image generation from prompts (bool)
- --img-provider: openai (default) | google
- --img-out: dir for images (default ./.src)
- --pair-source: prompts-only | existing | all (default: prompts-only when img-gen enabled)
- --force-regen: regenerate images even if they already exist (default: false, skips existing)
  (Prompts JSON supports field: `target_filename`)
  Env overrides: `OPENAI_IMAGE_MODEL` (default: `gpt-image-1-mini`; options: `dall-e-2`, `dall-e-3`, `gpt-image-1`)
                 `OPENAI_IMAGE_SIZE` (default: `1024x1024`; supported: `1024x1024`, `1024x1536`, `1536x1024`, `auto`)

### Flow
0) If `--img-gen` and `--prompts` provided: read JSON; for each clip generate an image using `--img-provider`:
   - Prompts are self-contained with detailed descriptions including any continuity (e.g., "continuation of previous scene...")
   - OpenAI & Google: use text-to-image Generations API with comprehensive prompts
   - No dependencies between images - suitable for parallel generation in future
   Save using `target_filename` when provided; write to `--img-out`. Default pairing source is prompts order (or `--pair-source=all` to merge with existing images)
1) Scan `.src`, support PNG/JPG/JPEG/WEBP, natural sort
2) Pair (i, i+1)
3) If dry-run, print plan and exit 0
4) For each pair: call provider respecting start/end, save `<idx>__<start>__to__<end>.mp4`
5) Write `manifest.json`; non-zero exit if any pair failed; bounded retries

### Architecture
- io.scan (sync), core.pairs (pure), provider.{base, veo} (sync wrappers), engine.generate (sync), manifest.write (sync), cli.app
- image_gen.{base, openai, google} (sync API per call)
  - image_gen providers honor `target_filename` for output naming
  - OpenAI provider: uses Generations API for all images with self-contained prompts
  - No inter-image dependencies; suitable for parallel generation in future

### NFR
Cross-platform; env creds; structured logging; no secrets; deterministic names.

### Tooling
Use uv: `uv init`, `uv add PKG`, `uv run python -m app`, `uv lock`, `uv venv`.


### Project Structure
```
shit_factory_ai_video_generator/
  .cursorrules
  requirements.md
  solution_design.md
  .env.example
  .src/                       # input images
  .out/                       # generated videos (default)
  app/
    __init__.py
    cli.py                    # entry point (argparse/typer)
    io_scan.py                # discover & sort images
    core_pairs.py             # pair generation
    engine.py                 # orchestration (sync)
    orchestrator.py           # optional bounded concurrency wrapper around engine
    manifest.py               # manifest writer
    logging_conf.py
    providers/
      __init__.py
      base.py
      veo.py
    image_gen/
      __init__.py
      base.py
      openai.py
      google.py
  pyproject.toml              # managed by uv
```

### Examples
- Dry run:
  - `uv run python -m app.cli --src ./.src --duration 3 --dry-run --verbose 1`
- Generate with defaults (veo, out=./.out):
  - `uv run python -m app.cli --src ./.src --duration 3`
  
- Image generation then video:
  - `uv run python -m app.cli --img-gen --prompts ./.src/video_prompts.json --img-provider openai --img-out ./.src --duration 3`
- Image generation merging with existing images:
  - `uv run python -m app.cli --img-gen --prompts ./.src/video_prompts.json --pair-source all --duration 3`
- CI test:
  - `uv run pytest -q`


