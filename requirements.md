## AI Video Generator — Lean Business Requirements (Indexed Use Cases)

UC-01 Discover images: scan `.src`, supported formats (PNG/JPG/JPEG/WEBP), natural sort.
UC-02 Pairing: for N images, create N-1 pairs `(i, i+1)` in order.
UC-03 Duration: required at run; applies per video (seconds, int/float).
UC-04 Preview: dry-run prints sorted images, pairs, and planned count.
UC-05 Generate: per pair, call provider; start/end frames respected; save video.
UC-06 Provider abstraction: default `veo`; switchable via flag/env without UX change.
UC-07 Output: write to `outDir` (default `./out`); name `<idx>__<start>__to__<end>.mp4`.
UC-08 Errors: validate inputs; bounded retries; continue on failure; non-zero exit if any fail.
UC-09 Logging: start banner, per-pair progress, final summary; verbosity levels.
UC-10 Manifest: `manifest.json` with inputs, pairs, outputs, provider, params, timestamps.
UC-11 Concurrency: cap parallel jobs; respect provider rate limits.
UC-12 Cross-platform & security: Win/macOS/Linux; env-based creds; no secrets in logs.

Definition of Done: Given 4 sorted images, produce 3 videos (1→2, 2→3, 3→4) of ~D seconds, saved in `outDir` with deterministic names and a manifest; exit code 0 if all succeed.


