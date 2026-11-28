# ProofDelta sharing assets

The requested GitHub source package, demo video and two social-post drafts are prepared from the existing ProofDelta source. No social posts were published.

- `GITHUB-README.md`: README for the source export, without private hosting metadata.
- `render_demo.py`: reproducible silent, captioned, 42-second illustrated walkthrough, not a screen recording.
- `linkedin.md`, `x.md`: ready-to-edit drafts. Attach the MP4. Do not claim a public site or link a private preview as public.
- Generated video, cover, timeline and a diagnostic contact sheet: `tmp/launch/`.

GitHub destination: https://github.com/kallurayaankit/proofdelta. The owner created this public repository for the prepared source. Publication is performed through the connected GitHub tools.

The code export contains tracked project files, the launch assets and a public-facing README. It excludes `.git`, `.openai`, private verification notes, runtime folders and dependencies. It preserves upstream licensing files. The existing private Site has not been redeployed or made public.

## Raya narrated edition

`media/ProofDelta-Raya-Voice.mp4` adds the existing Raya — My Voice narration at natural speed. Runtime is approximately 35 seconds; graphics follow the returned speech alignment. `narration.txt` contains the spoken script. The original silent edition is retained. Full stream decode, exact alignment text, seven scene layouts and audio levels were checked; full listening/playback review was unavailable. No social post was published.

## Mandarin edition

`media/ProofDelta-Mandarin-Raya.mp4` uses the existing Raya voice with language `zh`, natural speed, and Simplified Chinese graphic labels. The fictional source PDF images retain their original English text. Run `python launch/render_narrated.py --mandarin` with local narration inputs under `tmp/launch/mandarin/`. `mandarin_art.py` contains the translations; `narration-zh.txt` is the spoken script. Timing, seven layouts, full decode and audio levels were checked. Full listening and accent review were unavailable. English editions remain available.
