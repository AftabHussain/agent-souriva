# Complete model citation validation

## Change

Changed model-response citation parsing to preserve every bracketed identifier for grounding validation.

## Architecture

The model adapter extracts citation syntax, while the alignment module remains responsible for checking each identifier against eligible retrieved evidence.

## Design notes

Previously the adapter discarded unknown IDs before alignment, so a response containing both a real and fabricated citation could retain the fabricated text while passing the structured check. Passing all emitted IDs forward makes the existing fail-closed policy complete.

## Verification

Added a regression test for mixed known and unknown IDs. Ran the full test suite and lint after the change; results are recorded in the final documentation verification.

## Result

Any bracketed citation outside the retrieved evidence allow-list now causes the response to abstain.
