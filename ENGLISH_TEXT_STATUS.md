# English Text Extraction Status

The text-based question view is currently hidden. The app intentionally shows
only the original question images because OCR and PDF column extraction still
require manual semantic review.

## Production state

- Original images are the only visible question source.
- Vietnamese translations and answer grading remain enabled.
- The text renderer and `sourceContent` schema remain in the codebase for later
  continuation, but `renderStudyContent()` currently always renders the image.

## Completed or partially reviewed work

- Hacker 2 Test 01: visual audit completed; fragment at
  `review_fragments/english_h2_test01.json`.
- Hacker 2 Test 02: visual audit completed; fragment at
  `review_fragments/english_h2_test02.json`.
- Hacker 2 Test 06: visual/semantic audit completed; fragment at
  `review_fragments/english_h2_test06.json`.
- Hacker 2 Test 07: visual/semantic audit completed; fragment at
  `review_fragments/english_h2_test07.json`.
- Hacker 2 Test 08: semantic audit was in progress; do not treat the fragment as
  final without another full visual pass.
- Hacker 2 Tests 03-05 and 09-10: extraction fragments exist, but quality varies
  and they must not be enabled without visual review.
- Hacker 3: source PDF is scanned and OCR is substantially noisier. A skeleton
  for Test 01 exists, but questions and choices still need manual transcription.

## Validation

Use:

```powershell
python tool\validate_english_content.py review_fragments\english_h2_test01.json
```

Passing the validator is necessary but not sufficient. Every image must also be
opened and checked for:

- correct document count and order;
- full passage text without column interleaving;
- Part 6 blanks `[number]` in the correct positions;
- complete question text and four distinct A/B/C/D choices;
- no footer, page number, watermark, or adjacent-question text;
- correct tables, forms, chats, schedules, and multi-document boundaries.

## Resume plan

1. Finish Hacker 2 one test at a time, with a visual audit of all 19 images.
2. Merge only final fragments into `translations.json` as `sourceContent`.
3. Manually transcribe Hacker 3 one test at a time from the original images.
4. Re-enable the text/image switch only after the intended scope is complete and
   sampled in the browser on desktop and mobile.
