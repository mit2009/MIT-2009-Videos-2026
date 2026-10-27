# Staff thank-you carousel test — October 27, 2026

Danny requested a silent example for Peko combining the curved carousel in
video 61 with the Pixel + Prism celebration in video 57. All eleven supplied
2600 × 2600 photographs appear in filename order. Their complete square frames
pass through the center; the curved projection makes the sides recede.
The lights sit around and behind the photographs. No names are inferred.

The sample is 38.25 seconds: a 3.5-second opening, 30.25 seconds of photos at
2.75 seconds per center crossing, and a 4.5-second closing. Applying that same
pace to 36 photos gives 107 seconds (1:47). Pixel pulses have a 0.55-second
beat (about 109 BPM), with slower rotating rays and color changes. This is a
visual timing sketch; the eventual Suno song can determine the final timing.

1920 × 1080, 60 fps, H.264, no audio stream, fast-start MP4. Added as item 98
in All Tests only. Existing items and Selects are preserved.

QA: all eleven source hashes verified; full MP4 decode passes; duration,
resolution, frame count, silent audio status, and fast start checked. Center
frames were extracted from the encoded MP4 and visually reviewed.

Reproduction: place the source ZIP photos under
input/26-10-27-Staff-Thank-You-Test in work/staff-thank-you-2026-10-27.
Run prepare.cjs and render.cjs with Node, @napi-rs/canvas, sharp, and FFmpeg.
Original photo files are kept locally and are not published separately.

Watch: https://26-mit-2009-videos.vercel.app/tests/#video-98
