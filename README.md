# MIT 2.009 — All Tests and Selects

## Vercel and the focused headshot generator

The canonical repository is now `mit2009/MIT-2009-Videos-2026`. Import this
repository into the **mit-2009** Vercel team. Its `vercel.json` installs the pinned
dependencies, runs `npm run build:vercel`, and serves `vercel-site/`.

The live Vercel address is https://26-mit-2009-videos.vercel.app/. It provides:

- `/tests/`: all sixty-one videos, numbered 1–61, including the lecture poster loops 60–61.
- `/posters/`: the two silent three-minute lecture loops, with playback and downloads.
- `/selects/` (and `/`): the existing ten Selects, with original MP4 downloads.
- `/generator/`: a focused headshot generator, using the single-reel effects
  from tests 38–41 and the original 18-second Disco D soundtrack.

In the generator, load JPG/PNG/WebP headshots, choose the student who should
land in the middle, choose the light color, and adjust three effect recipes.
Preview together, make three 1080 × 1920 / 60 fps MP4s, and download them.
Batch export creates a new timestamped folder and saves three videos plus a
settings file per student. Batch folder export requires browser support for
`showDirectoryPicker`; ordinary MP4 export requires H.264 WebCodecs encoding.
Runtime capability checks explain unsupported browsers before rendering.

Images are fitted in full, without cropping. The original reel timing,
temporal motion blur and lighting designs are reused. With multiple input photos, each reel
uses up to 53 other portraits (repeating when needed) followed by its selected
student. A single input photo repeats itself during the roll. Light color is
an explicit setting, not an inferred student team. Generated files are drafts;
the generator does not change catalog membership or Selects.

Photos and new videos are processed in the browser, with no uploads, backend,
database or generation service. The 18-second AAC music packets are copied
unchanged from the existing selected Disco D track into every export. Photos
and on-page downloads are held in memory; download finished videos before
closing the page. Batch outputs already saved to disk survive cancellation.
This focused generator is separate from the broader local Social Studio.

`npm test` checks both catalog builds, all original MP4 hashes, selection and
link preservation, every possible headshot landing, and exact audio packet
and timing preservation across three muxed outputs. Browser UI and hardware
MP4 export still require a live browser check before a full production run.

The Cloudflare addresses and instructions below are retained as migration history.

- [All Tests](https://mit-2009-videos-2026.pages.dev/tests/): all forty videos, newest first.
- [Selects](https://mit-2009-videos-2026.pages.dev/): items 1, 3, 6, 9, 20, 25, 38, 39, 40, and 41, newest first. This is the link to share with people who may post the videos.

Selects shows only the chosen videos and has no navigation back to All Tests.
The original root URL now shows only Selects, so people who received it earlier
see the chosen videos. The earlier `/selects/` link shows the same collection.
All experiments are at `/tests/`; an old root anchor for an unselected video stays
on Selects and does not redirect to a test. Both pages use the same original MP4s,
posters, and catalog numbers. Video download URLs remain unchanged. To change the picks, edit `assets/SELECTS.json`,
rebuild, and upload the site again.

Sixty-one videos with browser previews and original-quality MP4 downloads. The page
has a light background, simple controls, and links to the separate looping
slideshows where available. The seventeen slideshow videos are silent H.264 MP4s at 30 frames per second.
The two original portrait reel tests are 60 fps with original ticks and a landing chime.
Fourteen newer mixed-team reel tests are 18 seconds at 60 fps and silent.

| Original catalog number | Video | Duration |
| --- | --- | --- |
| 01 | Six teams — Balloon Bloom | 45 seconds |
| 02 | Rubber Reality — Wavvy Men | 30 seconds |
| 03 | Student headshots | 129.6 seconds |
| 04 | 2025 Finals — complete slideshow | 157.5 seconds |
| 05 | 2025 Finals — landscape, 0.8 sec/photo | 50.4 seconds |
| 06 | 2025 Finals | 63 seconds |
| 07 | 2025 Finals — landscape, 1.4 sec/photo | 88.2 seconds |
| 08 | 2025 Finals — vertical phone turn | 94.2 seconds |
| 09 | Theme Reveal & Balloon Challenge | 64.4 seconds |
| 10 | Theme Reveal & Balloon Challenge — 1.8 sec/photo | 82.8 seconds |
| 11 | Theme Reveal & Balloon Challenge — phone turn, 1.4 sec/photo | 76.4 seconds |
| 12 | Theme Reveal & Balloon Challenge — phone turn, 1.8 sec/photo | 94.8 seconds |
| 13 | MechE Communications — no rotation | 28 seconds |
| 14 | MechE Communications — clockwise | 40 seconds |
| 15 | MechE Communications — counterclockwise | 40 seconds |
| 16 | MechE Communications — gentle vertical motion | 28 seconds |
| 17 | MechE Communications — dynamic vertical pans | 28 seconds |
| 18 | Yellow Team — Slot reel A (quick spin) | 8 seconds |
| 19 | Yellow Team — Slot reel B (slow landing) | 11 seconds |
| 20 | All teams — Paper confetti | 18 seconds |
| 21 | All teams — Color bloom | 18 seconds |
| 22 | All teams — Paper confetti · Neighbors visible | 18 seconds |
| 23 | All teams — Color bloom · Neighbors visible | 18 seconds |
| 24 | Blue Team — Confetti shower | 18 seconds |
| 25 | Blue Team — Confetti shower · Neighbors visible | 18 seconds |
| 26 | Blue Team — Analog party poppers | 18 seconds |
| 27 | Blue Team — Analog paper drift | 18 seconds |
| 28 | Blue Team — Six pieces · Gentle sway | 18 seconds |
| 29 | Blue Team — Six pieces · Slow turns | 18 seconds |
| 30 | Blue Team — Digital · Neon Circuit | 18 seconds |
| 31 | Blue Team — Digital · Prism Jackpot | 18 seconds |
| 32 | Blue Team — Digital · Orbit | 18 seconds |
| 33 | Blue Team — Digital · Pixel Party | 18 seconds |
| 34 | Disco A — Mirrorball | 18 seconds |
| 35 | Disco B — Neon Boogie | 18 seconds |
| 36 | Disco C — Pocket Funk | 18 seconds |
| 37 | Disco D — Space Disco | 18 seconds |
| 38 | Blue Team — Neon Circuit · Disco D | 18 seconds |
| 39 | Blue Team — Prism Jackpot · Disco D | 18 seconds |
| 40 | Blue Team — Orbit · Disco D | 18 seconds |
| 41 | Blue Team — Pixel Party · Disco D | 18 seconds |
| 42 | Six teams — Together · Disco D | 18 seconds |
| 43 | Six teams — Color Cascade · Disco D | 18 seconds |
| 44 | Six teams — Center Out · Disco D | 18 seconds |
| 45 | One machine — Slow Bloom · Disco D | 15 seconds |
| 46 | One machine — Color Sweep · Disco D | 15 seconds |
| 47 | One machine — Color Rush · Disco D | 15 seconds |
| 48 | Vertical — Six-window machine · Disco D | 15 seconds |
| 49 | Vertical — One reel builds six · Disco D | 15 seconds |
| 50 | Vertical — Two reels, three rounds · Disco D | 15 seconds |
| 51 | Vertical — Neon Arcade · Disco D | 15 seconds |
| 52 | Vertical — Color Ribbons · Disco D | 15 seconds |
| 53 | Vertical — Pixel Jackpot · Disco D | 15 seconds |
| 54 | Pixel + Prism — 15-second test | 15 seconds |
| 55 | Pixel + Prism — 13-second test | 13 seconds |
| 56 | Pixel + Prism — 11-second test | 11 seconds |
| 57 | Finals invitation — 13 seconds | 13 seconds |
| 58 | Finals invitation — 15 seconds | 15 seconds |
| 59 | Finals invitation — 17 seconds | 17 seconds |
| 60 | 36 posters — Flat ribbon | 180 seconds |
| 61 | 36 posters — Curved carousel | 180 seconds |

On October 4, the 13 earlier videos (2, 4, 5, 7, 8, and 10–17) were restored
from the original September 24 library at Danny's request. Number 18 was
already present. Their numbers and original MP4/poster bytes are preserved;
the existing catalog entries and Selects did not change. Restoration notes
and complete decode/hash verification are in
`assets/production-notes/catalog-restoration-2026-10-04/`.

Items 54–56 are Danny's requested duration comparison: Pixel Party's colored
perimeter squares with Prism Jackpot's outward rays. The same 54-photo sequence
lands on Blue portrait 88 at 12, 10, or 8 seconds, followed by a three-second
celebration. The motion is retimed proportionally; photos and neighboring
portraits are preserved. Disco D keeps its original tempo, pitch, and gain:
the edits start at source seconds 0, 2, and 4 and all end at source second 15,
with short edge fades. The three-second winning phrase is identical in all
three. These are All Tests drafts; Selects and the generator remain unchanged
while Danny chooses the pacing. Production notes record the verification.

Items 57–59 add Danny's Finals livestream invitation, with total running times
of 13, 15, and 17 seconds. Portrait landings move to 5, 7, and 9 seconds. Each
gets three seconds of celebration, a one-second rush through the rays, and
four full seconds of a still title card: “MIT 2.009 FINALS · WATCH LIVE DEC 7.”
Danny approved this copy for testing while the stream URL and time are pending.
The same eight-second Disco D finish runs through the celebration, transition,
and card. A whole two-second bar extends the winning groove before the original
musical resolution; pitch, tempo, and gain remain unchanged. All Tests only.

Items 60–61 are the silent lecture poster loops requested on October 5. Each
contains all 36 completed opportunity posters, edge to edge, moving left to
right. A new poster crosses the center every five seconds in the exact order
Green → Purple → Red → Blue → Yellow → Pink, repeated six times. One is a flat
ribbon, the other a cylindrical carousel. Both are 180 seconds at 1920 × 1080,
60 fps, and loop seamlessly. The consolidated six-page Pink export supplies
both Pink subteams; duplicated, unfinished, and template pages are omitted.
Source selection and verification are recorded in the production notes.

Balloon Bloom uses a 7-second transition and a 0.5-second hold. Student
headshots use 1.2 seconds per photo. 2025 Finals uses 1 second per photo;
Theme Reveal uses 1.4 seconds. Items 01 and 03 loop in the preview player.
The original two reel tests use one column of Yellow Team portraits, bounce at the stop,
and settle on photo 15. The mixed-team tests sample 54 portraits (nine per team). Items 20–21 land on Yellow Team photo 15; items 22–23 land on Blue Team photo 88 and retain partial neighboring portraits above and below. Items 20–23 compare paper confetti with a six-color bloom. Items 24–25 both feature photo 88, settle two seconds sooner, and use six times as many paper particles in a foreground shower; item 24 isolates the winner, while item 25 retains neighboring portraits. Items 26–27 build on item 25 with varied paper shapes and folds, simulated air currents, unequal rebounds, and fixed pools of warm interior lighting from concealed bulbs. Item 26 uses uneven party-popper bursts; item 27 uses a looser drifting shower. Both retain neighboring portraits. Items 28–29 use exactly six large paper pieces, one per team color, released at uneven intervals within 0.31 seconds and falling from top to bottom. They retain photo 88, neighboring portraits, and warm interior lighting. Items 30–33 explore modern digital slot screens: Neon Circuit, Prism Jackpot, Orbit, and Pixel Party. They use the same 54 portraits, land on photo 88 at 12 seconds, retain neighboring portraits, and celebrate with six seconds of LED chases, color pulses, rings, or pixel lights. These appear only in All Tests. Items 34–37 are four original 120 BPM disco sketches, all paired with the unchanged Neon Circuit video for comparison. Each accents the 12-second landing, includes MP3 and WAV downloads, and has matched loudness. These audio auditions are only in All Tests. Items 38–41 are the selected updates to those four digital graphics: blue background glow, slowly changing accents that settle on blue at 12 seconds, plus identical Disco D audio. The copied AAC stream has matching hashes and starts at zero in all four. These four are in Selects; prior silent looks and music auditions remain in All Tests. None of the reel tests loop. Only one preview plays at a time. The original catalog numbering is intentional. The page shows the newest additions first; append future videos to assets/CATALOG.json.

## What is included

- `assets/videos/`: the original short MP4s, with the Finals filename updated.
- `assets/video-parts/`: ordered lossless parts of the two long lecture originals; the build assembles and verifies exact MP4 bytes.
- `assets/previews/`: the sixty-one poster images.
- `assets/CATALOG.json`: titles, descriptions, timings, links, and file hashes.
- `assets/audio/`: standalone MP3 and 24-bit WAV disco-beat exports.
- `assets/SELECTS.json`: catalog numbers to show on the share page.
- `build.py`: creates the website and Cloudflare upload ZIP.
- `video-handler.mjs`: serves MP4 playback, seeking, and downloads.
- `preview.mjs` and `local-assets.mjs`: local preview server.
- `tests/`: video delivery and file-integrity checks.

Everything needed to rebuild this collection is in this repository. It does not
depend on a Codex workspace, Downloads folder, or the original archive folder.
Long MP4s use `source_parts` in the catalog to list ordered files of at most
64 MiB each. The build concatenates them and verifies the complete SHA-256;
this does not re-encode or reduce video quality. The source MP4 bytes are tracked once; generated copies and ZIPs are excluded from Git.

## Preview on this Mac

Node.js 22 or later and Python 3.10 or later are required. The original Cloudflare
preview needs no external packages. Run `npm ci` for the Vercel build, generator,
and full test suite. To preview all three Vercel pages locally, run
`npm run build:vercel`, then `python3 -m http.server 8808 --bind 127.0.0.1 --directory vercel-site`,
and open `http://127.0.0.1:8808/generator/` or `/tests/` or `/selects/`.

1. Open a terminal in this project folder.
2. Run `npm start`.
3. Open http://127.0.0.1:8792/ in a browser.

Press Control-C in the terminal to stop the preview. You can choose another
port with `PORT=8793 npm start`.

## Make an update

1. Change the text or file references in `assets/CATALOG.json`. For a replacement
   video, copy the MP4 into `assets/videos/`, update its details and SHA-256 hash,
   and update its poster in `assets/previews/`.
2. Run `npm test` to build and check the collection. It checks all sixty-one
   items, Selects membership, complete file hashes, byte-range seeking, and download filenames.
3. Run `npm start` to review the page. Commit source changes to Git when ready.

The collection count comes from the catalog. If adding videos, update the
selection test too. Page layout, styling, and browser controls currently live in `build.py`.

## Update the existing Cloudflare site

1. Run `npm run build`. The upload file will be
   `dist/MIT-2.009-Selected-Videos-Cloudflare.zip`.
2. In Cloudflare, open **Workers & Pages → mit-2009-videos-2026 → Create deployment**.
3. Choose **Production**, upload that ZIP, wait for all files to finish uploading,
   then choose **Save and deploy**.
4. Open both All Tests and Selects and check playback and downloads.

This is a Direct Upload project. Pushing to GitHub backs up source code and media;
it does **not** automatically republish the Cloudflare site. No hosting account
settings or public URLs were changed when this repository was created.

## How the large files are delivered

Cloudflare Pages has a 25 MiB limit per asset. The build splits each original MP4
into 16 MiB parts, and a small Pages Worker streams them as a single MP4 with
support for seeking. There is no video recompression. The parts, compiled worker,
and upload ZIP are generated locally and are not committed.

The site is public, though it asks search engines not to index it. Its existing GitHub
repository is public. Do not add account credentials or student information
beyond the already approved media. Existing photo/slideshow projects and the
separate Test Studio and HPR repositories remain independent.

## Existing looping slideshow links

- [Six teams — Balloon Bloom](https://mit-2009-connect-teams-2026.pages.dev/?transition=bloom-7-hold-0-5)
- [Student headshots](https://mit-2009-student-headshots.pages.dev/)

The 2025 Finals and Theme Reveal cuts are watchable in the collection's video
players; they do not have separate matching slideshow websites.

## Six-reel lecture comparisons

Items 42–44 show six reels across in 16:9: Together, Color Cascade, and Center Out.
Each includes all 108 approved portraits, lands on one expressive portrait per team,
and uses identical Disco D music. Spectrum and Mirrorball join the four earlier
digital styles. All winners are settled by 12 seconds. These are in All Tests only;
Selects is unchanged.

## Unified cabinet tests

Items 45–47 are revised as Slow Bloom, Color Sweep and Color Rush. These compare
three single-color cycling patterns and six-color winning bursts. No text appears
on the machine. Six reels use independent starts, speeds and stopping times:
Yellow 7.5s, Green 8s, Purple 8.5s, Red 9s, Pink 9.5s, Blue 10s. The last reel
completes one winner per team color on the Disco D hit. All are 15 seconds with
five seconds of a large light show. The same catalog numbers and MP4 paths are
preserved. Revision-specific query strings bypass older browser-cached copies.
These remain in All Tests; the ten Selects are unchanged.

## Vertical six-team examples

Items 48–50 compare a six-window 2 × 3 cabinet, one large reel that builds a
six-person grid, and two stacked reels playing three rounds. All are 1080 × 1920,
60 fps and 15 seconds. The same six winners appear in each, with the same music.
The final grid arrives at ten seconds, then celebrates for five seconds.
Item 48 includes all 108 approved photos; 49 and 50 sample 30 and 47 photos.
These are All Tests only.

## Six-window graphic styles

Items 51–53 build on 48 with Neon Arcade, Color Ribbons and Pixel Jackpot.
Each has colored gutters during the spin and a distinct complete cabinet,
frame treatment and six-color celebration. All retain the same 108 photos,
independent reel timing, six winners and exact Disco D audio as 48.
The original 48 remains unchanged. All Tests only.
