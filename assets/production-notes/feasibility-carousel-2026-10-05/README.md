# Feasibility carousel — October 5, 2026

Danny requested the previous curved lecture carousel style with the slides in
Feasilbility Student Feedback Forms 2026.pptx and submissions (2).zip, at three
seconds per slide. He confirmed using project slides once and omitting classroom
pages. The first pass keeps each team's original presentation together in
Green, Purple, Red, Blue, Yellow, Pink order. Grouped versus interleaved order
was asked; grouping is the stated first-pass assumption pending a reply.

229 slides: Green 40, Purple 51, Red 38, Blue 31, Yellow 32, Pink 37. The ZIP's
complete submissions supply five teams. Matched PPTX/PDF pairs use their supplied
PDFs, preserving native typography. Yellow's legacy PPT failed to open in the
bundled converter; its full project text was verified against the feedback
deck's slides 4–35. That deck supplies Yellow. Purple was rendered using bundled
LibreOffice, then Poppler. Intro, seating, blank separator and feedback cards
are omitted. Original presentation builds and appendices remain intact.

The converter omitted the GIF on Yellow source slides 6 and 11. Original GIF
frame 171 shows the chair design; that original frame was restored in the
picture's exact slide rectangle. Other embedded media use supplied poster
frames. No artwork was regenerated. Original source files remain unchanged.

1920 × 1080, 60 fps, H.264, silent, 687 seconds. Every slide crosses the center
once, at three-second intervals. The left-to-right ribbon is projected onto a
continuous cylindrical surface. Full slides fit in the center. Texture travel
is exactly periodic; the endpoint equals the first frame and is not encoded
again. The final file has 41,220 frames and MP4 fast start.

Verification fully decodes the video, compares all 229 center-crossing frames
against the source renderer, and checks duration, dimensions, silence, timing,
source identities and exact loop closure. See verification.json.

The original MP4 is stored in ordered 64 MiB parts to fit GitHub's single-file
limit. The existing build reconstructs identical bytes and checks SHA-256.
Item 62 appears in All Tests and /feasibility/. Items 1–61, Selects, the generator
and the previous /posters/ share page are preserved.

Reproduction scripts run from work/feasibility-carousel-2026-10-05 with local
source/raster files and opencv-python-headless in render-deps. They are provenance,
not a web build dependency. Sources and raster pages are not added to Git.
