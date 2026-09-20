# Grounding and abstention policy

## Change

Added explicit post-generation checks for retrieval strength, valid citations, and model abstention.

## Architecture

The alignment module sits between model output and external responses. It converts a model reply into either a cited grounded answer or a standardized abstention with a machine-readable reason.

## Design notes

Only evidence above the configured threshold is eligible. Citation IDs are deduplicated and resolved from that allow-list; replies without citations or with any unknown citation are rejected. This makes citation behavior inspectable rather than relying only on prompt compliance.

## Verification

Compiled source and tests and checked the diff. Unit cases cover accepted citations, weak retrieval, invented citations, and missing citations.

## Result

Unsupported output cannot pass through as an answer, and callers can distinguish why the system abstained.
