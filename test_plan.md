## AI Video Generator — Functional Test Plan (Lean)

### Scope
- Functional behavior only for CLI app per `requirements.md` and `solution_design.md`.
- In-scope use cases: UC-00 … UC-12. Non-functional (performance, UX polish, security pen-test) out of scope.

### Assumptions
- Executed via `uv run python -m app.cli`.
- Inputs under `.src/`; outputs default to `./.out/` unless `--out` provided.
- Video provider `veo` default; other providers pluggable via `--provider`.
- Image generation pre-step is optional, enabled via `--img-gen` with `--prompts` JSON. `.md` prompts are not accepted at runtime.

### Test Cases (Functional)
0) TC-UC00-Prompts-JSON-Only
   - Steps: Run with `--img-gen --prompts ./.src/video_prompts.md`.
   - Expected: Rejects `.md`; requires JSON; validation error; non-zero exit.

0.1) TC-UC00-Prompts-JSON-Schema
   - Steps: Provide malformed JSON or missing required fields.
   - Expected: Schema validation error; non-zero exit; no images written.

0.2) TC-UC00-Image-Gen-Default-Provider
   - Steps: `--img-gen --prompts ./.src/video_prompts.json` without `--img-provider`.
   - Expected: Uses `google_vertex_imagen_2` by default; generates one image per prompt to `./.src`.

0.3) TC-UC00-Image-Gen-Provider-Switch
   - Steps: Use `--img-provider openai`.
   - Expected: Succeeds with identical UX; images saved to target dir.

0.4) TC-UC00-Image-Gen-Params
   - Steps: Set `--img-size 1024x1024 --img-out ./.src`.
   - Expected: Params applied; `imgOutDir` honored; sequential generation within each group.

0.4a) TC-UC00-Target-Filename
   - Steps: Use prompts with `target_filename` set (e.g., `S01_girl_01A.png`).
   - Expected: Generated image file name matches `target_filename` exactly in `--img-out`.

0.4b) TC-UC00-Attachment-As-Init
   - Steps: Provide `attachment` referencing an existing file; run image-gen.
   - Expected: Provider called with that file as init/reference; image generated; no crash if attachment missing → validation error.

0.4c) TC-UC00-Sequential-Within-Group
   - Steps: Use prompts where multiple clips share the same `group` (e.g., `girl_01`). Enable image-gen.
   - Expected: Generation for that group runs strictly in order; each clip can use prior image as attachment.

0.4d) TC-UC00-Concurrent-Across-Groups
   - Steps: Use prompts with at least 3 distinct groups and set `--concurrency 2`.
   - Expected: At most 2 groups generate concurrently; within each group, clips are sequential.

0.5) TC-UC00-Pair-Source-Prompts-Only
   - Steps: Enable image-gen; omit `--pair-source`.
   - Expected: Pairing uses prompts order by default.

0.6) TC-UC00-Pair-Source-All
   - Steps: `--img-gen --pair-source all` with existing images in `.src/`.
   - Expected: Generated images merged with existing; pairing source is combined set.

0.7) TC-UC00-Seed-Determinism
   - Steps: Run twice with same `--img-gen --prompts` and `--seed 123`.
   - Expected: Identical images (within provider determinism contract) and same filenames.
1) TC-UC01-Discover-Supported
   - Steps: Place PNG/JPG/JPEG/WEBP in `.src/`; run with `--dry-run`.
   - Expected: Only supported files discovered; count matches; no scan errors.

2) TC-UC01-Natural-Sort
   - Steps: Files `img1.jpg,img2.jpg,img10.jpg`; run `--dry-run`.
   - Expected: Order is `img1,img2,img10` (natural sort).

3) TC-UC02-Pairing
   - Steps: 4 images; run `--dry-run`.
   - Expected: Pairs are `(1,2),(2,3),(3,4)`; exactly N-1 pairs.

4) TC-UC03-Duration-Required
   - Steps: Omit `--duration`.
   - Expected: Input validation error; exit code non-zero; no outputs.

5) TC-UC03-Duration-Float
   - Steps: Use `--duration 2.5`.
   - Expected: Accepted; subsequent behavior uses given duration.

6) TC-UC04-Dry-Run-Behavior
   - Steps: Use `--dry-run` with valid inputs.
   - Expected: Prints sorted list, pairs, planned counts; exits 0; no files written.

7) TC-UC05-Generate-Default
   - Steps: Run without `--dry-run` and with `--duration`.
   - Expected: One video per pair created in `./.out/`.

8) TC-UC05-Start-End-Respect
   - Steps: Use images with distinct start/end frames; generate.
   - Expected: Output transitions respect start→end ordering per pair.

9) TC-UC06-Provider-Default-And-Switch
   - Steps: Run once with default (no `--provider`), then with `--provider veo`.
   - Expected: Both succeed with identical UX; provider abstraction intact.

10) TC-UC07-Output-Naming
    - Steps: Generate outputs.
    - Expected: Filenames follow `<idx>__<start>__to__<end>.mp4`; deterministic and collision-free.

11) TC-UC08-Error-Handling-Retry-Continue
    - Steps: Induce one provider call failure (transient); run full job.
    - Expected: Bounded retries attempted; processing continues for other pairs; final exit non-zero if any pair permanently failed.

12) TC-UC09-Logging-Verbosity
    - Steps: Run with `--verbose 0`, `1`, `2`.
    - Expected: Start banner, per-pair progress, final summary; volume matches level; no secrets in logs.

13) TC-UC10-Manifest-Contents
    - Steps: Generate successfully.
    - Expected: `manifest.json` written with inputs, pairs, outputs, provider, params, timestamps; schema consistent; paths valid.

14) TC-UC11-Group-Concurrency-Cap
   - Steps: Run with image-gen enabled and `--concurrency 2` on a JSON containing multiple groups.
   - Expected: No more than 2 groups active concurrently; per-group sequence preserved; logs show grouped scheduling.

15) TC-UC12-Cross-Platform-Paths
    - Steps: Run on Windows path semantics (backslashes) and POSIX paths.
    - Expected: Works on both; no path-related failures.

16) TC-Exit-Code-All-Succeed
    - Steps: Happy path with all pairs generated.
    - Expected: Exit code 0.

17) TC-Exit-Code-Any-Fail
    - Steps: Force one pair to fail definitively.
    - Expected: Exit code non-zero; manifest reflects failure; other pairs processed.

18) TC-CLI-Args-Defaults-And-Overrides
    - Steps: Vary `--src`, `--out`, `--duration`, `--provider`, `--dry-run`, `--verbose`.
    - Expected: Flags parsed; defaults applied when omitted; overrides honored.

### Minimal Test Data
- Sorting set: `img1.jpg, img2.jpg, img10.jpg`.
- Mixed formats: include one unsupported (e.g., `.bmp`) to verify filtering.
- Small valid images for quick transitions.

### Entry / Exit
- Entry: `.src/` populated; CLI reachable via uv; env cred(s) set when required.
- Exit: Outputs and `manifest.json` validated or intentional errors observed; exit code asserted.


