# Verified Transaction Event Schema

Future acquisition events are stored only when a source document identifies a real event.

Required fields:

- `event_id`
- `announcement_date`
- `buyer_name`
- `target_name`
- `target_state` when identifiable
- `target_naics` / `target_sector` when supportable
- `deal_value_usd` only when disclosed
- `deal_value_disclosed` boolean
- `source_url`
- `source_type` (SEC filing, company release, etc.)
- `verified_by_primary_annotator`
- `verified_by_secondary_annotator` for the reliability subset
- free-text `notes`

Rules:

- Never infer a deal value when it is not disclosed.
- Never convert an acquisition rumor into a completed/announced event.
- Keep raw source evidence and extraction output distinct from adjudicated ground truth.
- Assign industry/geography only when evidence supports the label.
- Deduplicate syndicated versions of the same transaction.
- Record corrections rather than silently rewriting prior releases.
