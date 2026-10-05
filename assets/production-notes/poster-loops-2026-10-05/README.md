# Lecture poster loops — October 5, 2026

Danny requested all 36 opportunity posters in two edge-to-edge, left-to-right
loops for lecture: a flat ribbon and a large carousel. He specified five seconds
per poster, silent, and the repeating color order Green, Purple, Red, Blue,
Yellow, Pink. Both exports are 180 seconds, 1920 × 1080, 60 fps, H.264, with no
audio track. Every poster crosses the center once per loop, five seconds apart.

The ZIP contains 46 pages. The consolidated six-page BubblegumSixOpps PDF
contains the completed Pink Panther posters 1–3 and Bubblegum posters 4–6.
That export supplies all six Pink posters. The three-page Bubblegum export is
a duplicate, while the seven-page Pink Panther export includes templates,
unfinished and superseded pages. The remaining ten PDFs each supply three
posters. This gives exactly 36 complete posters: six per color.

Original PDFs remain untouched. Each selected page was rasterized by Poppler
to 1440 × 2160 and scaled without cropping to the video texture. No content
was redrawn or generated. Within each color, the original opportunity order
is retained. Source ZIP, PDF, and raster hashes are recorded in sequence.json.

The flat ribbon translates at 144 pixels per second. The carousel maps the
same connected strip onto the visible front of a 36-poster cylinder. Its front
poster fits fully within the frame; the sides recede through perspective.
The temporal color sequence follows center crossings while moving left to
right. A mathematically periodic 10,800-frame cycle avoids a jump or pause at
the wrap; the endpoint at exactly 180 seconds equals the starting frame and
is not included twice in the export.

The long original MP4s are stored in ordered 64 MiB parts in assets/video-parts
to fit Git's individual file limit. build.py assembles their exact original
bytes into the normal Vercel MP4 URLs and verifies the final SHA-256. No quality
reduction, recompression, or external media host is involved. Existing source
MP4s continue to use their original files. Selects and the generator are unchanged.

The archived renderer runs from work/lecture-posters-2026-10-05 with the local
raster pages referenced in sequence.json. Original PDFs and page images are
not added to the public repository. See verification.json for export checks.
