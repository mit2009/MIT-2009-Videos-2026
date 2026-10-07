# MIT 2.009 Videos 2026

All Tests is the eighty-six-video collection at https://26-mit-2009-videos.vercel.app/tests/.
Selects is the share page at https://26-mit-2009-videos.vercel.app/. The /selects/ URL shows the same picks.

- Preserve every catalog item numbered 1–86 unless requested otherwise.
- Use the names All Tests and Selects. Selects currently contains 1, 3, 6, 9, 20, 25, 38, 39, 40, and 41; change assets/SELECTS.json only when Danny changes his picks.
- Both pages show newest first. Keep existing catalog numbers and MP4 URLs. The root URL must show only Selects; all experiments belong at /tests/. Selects must not link back to experiments.
- Danny chose Disco D (Space Disco) for all four digital graphics, with the pink background glow changed to blue and slowly changing accents that settle on blue at the 12-second landing. Updated items 38–41 are in Selects. Keep their music identical in timing and volume; preserve earlier versions 30–37 in All Tests.
- Item 6 is titled "2025 Finals"; its old working title was Lecture 1.
- Keep source videos unchanged; do not recompress them for storage.
- Edit assets/CATALOG.json for titles, descriptions, and media references.
- site/, dist/, and video-manifest.json are generated; use python3 build.py.
- Run npm test when changing video delivery or the build process.
- The Cloudflare site uses dashboard Direct Upload, not automatic GitHub deployment.
- The canonical GitHub organization is now mit2009. Vercel uses npm run build:vercel and vercel-site/; this output is generated and ignored.
- The focused headshot generator is in generator/ and is published at /generator/. It reuses the individual portrait reel effects from 38–41 and copies the exact Disco D AAC packets into all outputs. Preserve the shared audio and the 12-second landing. Input photos stay in the browser; do not add student originals or generated drafts to Git automatically.
- Generated headshot videos remain drafts. Only Danny's explicit picks change Selects or add items to the catalog.
- Keep secrets and credentials out of Git. Do not change unrelated Test Studio or HPR projects.

- Items 42–44 are six-reel widescreen lecture tests, with identical Disco D audio and winners Yellow 15, Red 25, Green 43, Pink 67, Blue 89, Purple 107. They remain in All Tests until selected. Preserve all 108 approved students across each six-reel video.

- Items 45–47 revision 2 are Slow Bloom, Color Sweep and Color Rush: independent reels, no text, three one-color-at-a-time patterns and six-color winning bursts. Stops are Yellow 7.5s, Green 8s, Purple 8.5s, Red 9s, Pink 9.5s, Blue 10s; the last stop triggers the shared Disco D hit. Each is 15s, with the same 108 photos and six winners as 42–44. All Tests only. Preserve MP4 paths and use digest query strings for revised preview/download URLs.

- Items 48–50 are vertical 1080 × 1920, 15-second examples: six-window machine, one reel builds six, two reels/three rounds. Same six winners and exact Disco D Full Row Hit audio. Complete six-person grid at 10 seconds, five-second celebration. Photo counts 108, 30 and 47 respectively. All Tests only.

- Items 51–53 are graphic variations of 48: Neon Arcade, Color Ribbons, Pixel Jackpot. Distinct whole-cabinet graphics, colored gutters during spin, six-color winning effects. Original 48 remains unchanged. Same 108 photos, reel motions, six winners, 15-second timing and exact Disco D Full Row Hit audio as 48. All Tests only.

- Items 54–56 are Danny's requested Pixel + Prism duration tests (October 3): 15, 13, and 11 seconds. Pixel Party perimeter squares plus Prism Jackpot rays; identical 54-photo sequence and Blue winner 88. Land at 12, 10, and 8 seconds respectively, then celebrate for three seconds. Disco D retains original tempo and gain, starting at source seconds 0, 2, or 4 and ending at 15, with short fades. All Tests only; do not promote these or change the generator timing until Danny chooses.

- Items 57–59 are the October 4 Finals invitation tests: 13, 15, and 17 seconds total. Same Pixel + Prism look and original 54-photo order. Land at 5, 7, and 9 seconds, celebrate for three seconds, transition through a one-second light tunnel, then hold a static Finals card for four seconds. Danny approved “MIT 2.009 FINALS · WATCH LIVE DEC 7” with no URL or time yet. All versions have an identical eight-second Disco D ending, extended by one two-second bar before the original resolution; tempo and gain stay unchanged. All Tests only.

- Items 2, 4, 5, 7, 8, and 10–17 were restored on October 4 from the original September 24 archive at Danny’s request. Item 18 was already present. All Tests now has every number 1–59; keep the original bytes, numbers, and newest-first order. Earlier Lecture 1 display titles use the corrected 2025 Finals name. Selects is unchanged.

- Items 60–61 are the October 5 lecture poster loops: 36 complete posters, silent, 1920 × 1080 at 60 fps, 180 seconds. Continuous edge-to-edge movement left to right; center crossings every five seconds in the order Green, Purple, Red, Blue, Yellow, Pink. Both loop. Use the consolidated six-page Pink export, omitting duplicate and draft/template pages. The dedicated lecture link is /posters/, showing Flat ribbon then Curved carousel. These originals use ordered source_parts and complete SHA-256 verification so their published MP4s retain exact original quality. All Tests only.

- Item 62 is the October 5 feasibility carousel: 229 slides, three seconds per center crossing, silent 687-second loop, 1920 × 1080 at 60 fps. Project submissions appear once; classroom pages are omitted as requested. Revision 2 alternates Green, Purple, Red, Blue, Yellow, Pink, with each team’s pages progressing forward. Slides enter from the right and travel left, so their arrangement reads in normal order. Each slide appears once; finished teams drop out of the rotation. Dedicated share page: /feasibility/. Preserve 60–61 and /posters/. Production provenance and verification are in assets/production-notes/feasibility-carousel-2026-10-05-r2/. The original numbered MP4 URL redirects to the stable HD MP4. Preserve both revisions’ source parts.

- Items 63–68 are the October 6 photo-puzzle tests requested from Danny’s hand sketch: two vertical, two square, two landscape. Photos fill the frame and slide as complementary rectangular-tab puzzle pieces. No added slogans, labels, titles, or graphics inside the videos; silent, 24 seconds, 30 fps, H.264 Constrained Baseline. All Tests only. Treat the previous text-heavy concepts as superseded drafts. Preserve 1–62 and Selects.

- Items 69–77 are Danny’s October 7 String Tests: nine distinct single-string motion studies, all square 1080 × 1080, seamless five-second loops at 60 fps, silent, no text, eyes, or knots. Palettes and flat shaded outlines reference the supplied Slack icons. Three straight translations, three waves, and three curved motions. Production notes and render source are in assets/production-notes/string-tests-2026-10-07/. All Tests only; preserve earlier media and Selects.

- Items 78–86 are String Tests set 2: the string continuously enters and exits the frame in every design. All square, five-second seamless silent loops at 60 fps. Both endpoints remain outside; diagonal bands advect continuously along each path. Straight feeds, waves, arch, corner, U-turn, and serpentine route. No text or knots. Preserve set 1 and every prior video; All Tests only. Provenance: assets/production-notes/string-tests-continuous-2026-10-07/.
