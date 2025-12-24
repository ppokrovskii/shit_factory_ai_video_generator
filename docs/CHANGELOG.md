# Changelog

Completed changes. Newest at top.

---

## [2024-12-24] [testing] Optimize test suite - remove slow integration tests

- Reduced test execution time from 74s to 0.66s (112x faster)
- Removed 18 redundant slow integration tests using subprocess
- Kept all 24 fast unit tests with mocked APIs (no real API calls)
- Kept 3 essential integration tests for smoke testing
- Result: 41 tests in <1 second, zero API costs

## [2024-12-24] [video-cli] Add video quality presets: fast/regular/ultra

- Added `--video-preset fast` - Quick testing (mock provider, 3s)
- Added `--video-preset regular` - Standard quality (veo, 5s) [default]
- Added `--video-preset ultra` - High quality (veo, 8s)
- Environment variable overrides: `VIDEO_PRESET_{FAST|REGULAR|ULTRA}_{PROVIDER|DURATION}`
- Backward compatibility: `--provider` flag still works
- `--duration` flag overrides preset duration

## [2024-12-24] [image-cli] Add Gemini 3 Pro provider: `--provider gemini-pro` for 4K images

- Created new `GeminiProImageProvider` for professional quality generation
- Supports 1K, 2K, 4K resolution options (size shortcuts)
- Professional quality with Gemini's "thinking" mode
- Used by ultra preset by default
- Environment variable: `GEMINI_PRO_IMAGE_MODEL`

## [2024-12-24] [image-cli] Implement preset-based config: `generate fast|regular|ultra "prompt"`

- Added preset system with environment variable support
- `image-cli generate fast "prompt"` - Cheapest/fastest (~$0.01, <5s, OpenAI)
- `image-cli generate "prompt"` - Best value default (~$0.04, ~10s, Gemini)
- `image-cli generate ultra "prompt"` - Highest quality (~$0.10, ~30s, Gemini Pro)
- Environment variables: `IMAGE_PRESET_{FAST|REGULAR|ULTRA}_{PROVIDER|MODEL|SIZE}`
- Added `--img-preset` flag to video-cli
- Backward compatibility: `--provider` flag overrides preset
- Created env.example with all preset configuration options
- Updated README with preset-first approach

## [2024-12-24] [docs] Removed Defapi and third-party provider references

## [2024-12-24] [docs] Created BACKLOG.md and CHANGELOG.md tracking system
