# Video Generation Guide for Veo 3.1

Based on [Google Cloud's Ultimate Prompting Guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)

## Quick Commands

**Generate everything (images + videos):**
```bash
uv run python -m app.cli
# or
python -m app.cli
```

**Test with first 3 videos:**
```bash
uv run python -m app.cli --limit 3
```

**See detailed logs:**
```bash
uv run python -m app.cli --verbose
```

**Only images:**
```bash
uv run python -m app.cli --images-only
```

**Only videos from existing images:**
```bash
uv run python -m app.cli --prompts ""
```

## Core Rules

### 1. Smooth Flows Only
**ALL video transitions must be smooth within the same scene.**
- ✅ Same character, different action/pose
- ✅ Same location, camera movement
- ✅ Same scene, energy intensifying
- ❌ NO scene jumps (girl → city, forest → river)
- ❌ NO location changes (ground → aerial different place)
- ❌ NO subject changes (solitary → group)

**Flow breaks = editing cuts, NOT generated videos**

### 2. Character Movement Required - NATURAL HUMAN MOTION
**Every image MUST show character progression with REALISTIC, ORGANIC movement.**

❌ **BAD:** Same pose, just closer camera (statue-like)  
❌ **BAD:** Robotic/doll-like movement without weight or momentum  
✅ **GOOD:** Natural, fluid human motion with weight transfer and breathing

**Required in every transition:**
- **Natural weight transfer**: shifting balance, hip movement, foot positioning
- **Breathing**: chest rising/falling, shoulders moving naturally
- **Facial micro-movements**: eyes blinking/fluttering, mouth relaxing, expression evolving
- **Body momentum**: smooth acceleration/deceleration, natural follow-through
- **Hair movement**: responding naturally to motion and wind (not stiff)
- **Organic posture changes**: muscles tensing/relaxing, natural body curves

**Key phrases to include in video prompts:**
- "Natural, fluid human movement"
- "Realistic weight and momentum"
- "Organic motion"
- "Smooth, lifelike"
- "Takes a slow breath"
- "Weight shifts naturally"

### 3. Progressive Action & Environmental Life

**Every frame needs visible differences:**
- Character: different pose/expression/action
- Environment: moving elements (birds, clouds, mist, energy, hair)
- Energy effects: spreading/building/changing patterns

**Example - 5 frame awakening:**
```
S01: Arms down, head bowed, eyes CLOSED, mist swirling gently
S02: Eyes OPENING, head LIFTING, fingers SPREADING, mist flowing faster
S03: Eyes WIDE, mouth OPENS, hair WHIPPING, energy gathering
S04: Arms RAISING to shoulders, energy GLOWING, hair flowing UP
S05: Arms THRUST up, back ARCHED, energy BURSTING skyward
```

**Example - 5 frame city with environment:**
```
S06: Low altitude, tiny people on streets, vehicles streaking, clouds drifting
S07: Higher, bird flocks flying across, clouds moving faster, shadows shifting
S08: Peak view, multiple bird flocks crisscrossing, clouds large, vehicles like fireflies
S09: Descending, clouds below camera, birds swooping down, light casting shadows
S10: Rapid descent, birds peeling away, clouds far above, ground sharp focus
```

**Key:** Each image = clear new physical action + environmental changes, not just closer/farther view.

### 4. Prompts Structure (Five-Part Formula)

**Use this formula for all detailed prompts:**

**[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]**

#### A images (flow starters) - Full Formula
Use all five parts with specific details:

1. **Cinematography:** Camera work and shot composition
   - Shot types: Wide shot, medium shot, close-up, extreme close-up, two-shot
   - Camera movement: Dolly shot, tracking shot, crane shot, aerial view, slow pan, POV shot
   - Lens & focus: Shallow depth of field, wide-angle lens, soft focus, macro lens, deep focus

2. **Subject:** Main character/focal point with specific starting pose
   - **Specify exact pose:** arms position, head angle, eyes open/closed, hand gestures
   - **Natural, relaxed posture** - avoid stiff/robotic descriptions

3. **Action:** What the subject is actively doing (present tense, ongoing)
   - Describe as natural human behavior, not mechanical actions

4. **Context:** Environment and background elements with atmospheric details

5. **Style & Ambiance:** Overall aesthetic, mood, lighting, color tones
   - **For natural human movement:** Use "Photorealistic", "cinematic", "natural lighting"
   - Include: Slavic Steampunk environmental elements (ruins, brass, steam)
   - ⚠️ **AVOID for characters:** "animation blend", "cel-shaded", "comic book", "bold outlines" (these cause robotic movement)
   - ✅ **Use instead:** "Photorealistic with cinematic lighting", "film grain", "natural"

**Example A-image prompt (GOOD - Natural Movement):**
"Wide shot with deep focus, a young woman with long dark hair, standing with arms relaxed at sides, head slightly bowed, eyes closed, wearing flowing linen dress with embroidered details, leather straps, barefoot, in frozen brass-plated field at dawn, surrounded by weathered temple ruins with brass fixtures and copper details, morning mist swirling. Photorealistic with cinematic lighting, cold blue dawn light with warm amber accents, volumetric fog, film grain, 4k. Contemplative, mystical atmosphere."

**Example A-image prompt (BAD - Causes Robotic Movement):**
"Medium shot, tech-mystic woman with brass goggles, standing with arms down, in ceremonial pose, in front of brass clockwork ruins. Cel-shaded animation style with bold dynamic outlines, halftone patterns, comic book aesthetics."

#### B/C/D images (continuations) - Concise Changes Only
- **MUST start with:** "Same [subject] from reference image."
  - **For characters:** "Same girl from reference image.", "Same woman from reference image.", "Same dancers from reference image."
  - **For locations:** "Same city from reference image.", "Same landscape from reference image.", "Same rune circle from reference image."
  - **For objects:** "Same hands from reference image.", "Same fire ring from reference image.", "Same clockwork web from reference image."
- **Then describe ONLY changes:** [Cinematography change]. [Action change]. [Environmental change].
- **Pattern:** "Same [subject] from reference image. [Camera]. [Physical action]. [Environment]."

⚠️ **CRITICAL:** Without "Same [subject] from reference image" at the start, Gemini will generate completely different scenes!

**Good B/C/D examples:**
- ✅ "Same girl from reference image. Camera push-in to medium close-up. Eyes opening, head lifting, fingers spreading. Hair flowing with wind, mist swirling faster."
- ✅ "Same city from reference image. Crane shot ascending higher. Mechanical birds fly across frame in formation. Clouds moving faster, steam from pipes more visible."
- ✅ "Same hands from reference image. Extreme close-up with macro lens. Fingers pressed hard against rune circle, knuckles white. Energy sparks intensify around contact points."

**Bad examples:**
- ❌ "Medium close-up of tech-mystic woman..." (no reference mentioned → generates new character)
- ❌ "Same character, outfit, and art style as reference image. [full description]" (too verbose)
- ❌ "Same city, character, outfit from reference..." (doesn't match subject type)

#### Video Transition Prompts (First & Last Frame)
Describe the transformation between frames, combining:
- **Camera movement:** The cinematography change (dolly in, crane up, pan, orbit, etc.)
- **Character action:** Physical progression with NATURAL HUMAN MOTION
- **Visual effects:** Energy, particles, environmental changes

**Formula:** "[Camera movement]. [Natural character action with breathing/weight]. [Visual effects/environment]. Natural, fluid human movement."

**Examples for CHARACTER movements:**
- ✅ "Smooth dolly shot pushing in from wide to medium close-up. Woman takes a slow, deep breath - chest rises naturally, weight shifts organically onto one foot. Head lifts smoothly with natural neck movement as eyes flutter open. Shoulders relax and drop slightly. Hair moves gently with wind. Mist swirls softly. Natural, fluid human movement with realistic weight and momentum."
- ✅ "Dolly shot pulling back slightly. Arms begin raising gracefully with natural shoulder rotation and elbow bend. Body sways slightly with the upward motion. Weight shifts to both feet evenly. Breathing deepens - chest and abdomen expand. Energy glow builds gradually. Ground patterns emerge. Organic, lifelike movement with smooth acceleration."
- ✅ "Close-up dolly in. Eyes widen naturally - eyelids lift smoothly, pupils dilate gradually. Eyebrows raise slightly. Mouth parts gently as she takes a breath. Facial muscles respond naturally to emotion. Hair flows with supernatural wind but moves realistically. Natural human facial expressions with subtle micro-movements."

**Examples for NON-CHARACTER scenes:**
- ✅ "Orbital tracking shot rotating 180-degrees around subject with smooth arc. Symbols multiply exponentially and densify weaving together in braiding patterns. Vertical light threads intensify brightening connections."
- ✅ "Extreme crane shot rapidly ascending vertically with explosive speed. Ring shrinks rapidly far below as camera climbs hundreds of meters into sky. Fire energy transforms supernaturally morphing into massive clockwork mechanism web."

**Key additions for natural movement:**
- Always end with: "Natural, fluid human movement" or "Organic, lifelike motion"
- Include: breathing, weight shifts, momentum
- Avoid: stiff, robotic, mechanical descriptions for humans

### 5. Advanced Techniques

#### Negative Prompts (What to Exclude)
Describe what you want to **exclude** positively, not as negations:
- ❌ BAD: "no buildings" or "no people"
- ✅ GOOD: "desolate landscape with only natural rock formations" or "solitary figure with empty streets"

**Common exclusions for our style:**
- "Clean modern architecture with pristine surfaces" (when we want weathered ruins)
- "Bright daylight with harsh shadows" (when we want moody dusk/dawn)
- "Static pose with no hair movement" (when we want dynamic energy)

#### Audio Direction (Not Applicable for Music Videos)
**Note:** Veo 3.1 supports audio generation (dialogue, SFX, ambient), but **we are not using this feature** because this is a music video. The audio track is the song itself, not generated by Veo.

- ❌ Do NOT include audio descriptions in video prompts
- ❌ Do NOT add dialogue, SFX, or ambient sound instructions
- ✅ Focus only on visual elements and camera movements
- ✅ The music will be added in post-production editing

#### Timestamp Prompting (Multi-Shot Sequences)
For complex scenes with multiple distinct shots in one generation:

```
[00:00-00:02] Medium shot from behind the woman as she pushes aside hanging brass chains to reveal a hidden chamber.
[00:02-00:04] Reverse shot of her face, expression filled with awe. SFX: Chains swinging, echoing.
[00:04-00:06] Tracking shot following her as she steps forward, running her hand over glowing rune carvings.
[00:06-00:08] Wide crane shot revealing the vast chamber, half-swallowed by overgrowth. SFX: Orchestral swell.
```

**Note:** We use this for single-flow continuous sequences, not cross-flow transitions.

### 6. Safety Filters & Forbidden References

**❌ NEVER Reference Existing Media:**
- NO movie/show titles (Spider-Verse, Matrix, Blade Runner, etc.)
- NO character names (Spider-Man, Neo, etc.)
- NO franchise names (Marvel, DC, Star Wars, etc.)
- NO "X-inspired" or "X-style" referencing media

**❌ Safety Filter Triggers:**
- glowing tattoo, ritual tattoo, god sigils, deity names, cyber shaman, ritual pose, blood, wound

**✅ Use Instead:**
- Style: hybrid 2D/3D, cel-shaded, comic book aesthetics, bold outlines, halftone patterns
- Character: tech-mystic, Slavic geometric patterns, ceremonial pose, energy patterns
- Setting: Slavic Steampunk, brass mechanisms, steam-powered, Victorian-era with folk motifs

### 7. JSON Structure (Lean)

```json
{
  "schema_version": "3.0",
  "images": [
    {
      "code": "S01",
      "filename": "S01_scene_A.png",
      "prompt": "Full detailed prompt with EXACT STARTING POSE...",
      "reference": null
    },
    {
      "code": "S02",
      "filename": "S02_scene_B.png",
      "prompt": "Action change: eyes opening, head lifting...",
      "reference": "S01_scene_A.png"
    }
  ],
  "videos": [
    {
      "from": "S01_scene_A.png",
      "to": "S02_scene_B.png",
      "prompt": "Camera and character action together..."
    }
  ]
}
```

### 8. Flow Organization for 2:20 Music Video

**Structure:** 7 flows × 4 videos × 5s = 140s (2:20)

Each flow = 5 images → 4 smooth transitions → 20 seconds

**Example flows:**
1. AWAKENING (girl energy gathering)
2. CITY ASCENT (vertical camera journey)
3. GROUND RITUAL (hands channeling energy)
4. DANCERS (group movement)
5. RIVER & SYMBOLS (water → geometric patterns)
6. FIRE & NEURAL (fire → cosmic network)
7. TRANSCENDENCE (dissolution → closure)

**Between flows = hard cuts in editing software** (NOT in generation)

## Checklist Before Generating

For each image pair, verify:
- ✅ What changes physically? (pose, gesture, position)
- ✅ What changes facially? (eyes, mouth, expression)
- ✅ What's moving? (hair, clothing, energy)
- ✅ Same scene/location? (no jumps)

If you can't describe the physical change, images are too similar → video will be static/boring.

## Style Keywords (Slavic Steampunk + Hybrid Animation)

**Visual Style (include in A-images):**
- **Animation:** hybrid 2D/3D, cel-shaded, bold dynamic outlines, varying line weights, painterly brush strokes
- **Visual Effects:** halftone patterns, Ben-Day dots, chromatic aberration, motion blur trails, speed lines, film grain
- **Aesthetic:** imperfect hand-drawn edges, pop art influences, intentional imperfections, comic book aesthetics
- **Post-processing:** varied frame timing, high contrast vibrant colors

**Slavic Steampunk Elements:**
- **Materials:** brass, copper, bronze, worn leather, aged wood, tarnished metal, weathered surfaces
- **Technology:** clockwork mechanisms, steam-powered, gear-driven, pneumatic systems, analog dials, coal ember glow
- **Architecture:** Orthodox onion domes with brass plating, steam-pipe spires, mechanical bell towers
- **Cultural:** Traditional Slavic patterns, folk motifs, Cyrillic aesthetics, geometric embroidery
- **Atmosphere:** Steam clouds, pressure valves releasing, mechanical sparks, mist, nature reclaiming technology

## Key Takeaways from Veo 3.1 Guide

**Most Important for Us:**
1. ✅ **Five-part prompt formula** - Structure ensures consistency and control
2. ✅ **Cinematography vocabulary** - Precise camera terms (dolly, crane, tracking) give better results
3. ⚠️ **Audio generation** - Available in Veo 3.1 but NOT USED (we have a music track)
4. ✅ **Negative prompts** - Describe exclusions positively (not "no X" but "desolate landscape")
5. ✅ **First & Last Frame** - Our current approach is officially recommended by Google
6. ✅ **Ingredients to Video** - Using reference images for consistency is a core feature
7. ✅ **Timestamp prompting** - Can create multi-shot sequences in single generation

**What We're Doing Right (Applied):**
- ✅ Using reference images for character/scene consistency
- ✅ First & Last Frame transitions between images
- ✅ Precise cinematography terms (dolly, crane, tracking, orbital shots)
- ✅ Five-part formula for all A-images (flow starters)
- ✅ Breaking video into manageable flows
- ✅ Character movement and environmental dynamism in every frame

**What We're NOT Using:**
- ❌ Audio generation (we have a separate music track for the video)

