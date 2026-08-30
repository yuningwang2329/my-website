# Canonical literature mirror

This repository is a display mirror. It must not run `scripts/update_fluids.py`
or `scripts/ai_sweep.py` to change public paper data. MySecondBrain produces the
only canonical snapshot at its repository root:

- `literature-manifest.json`
- `fluids.json`
- `archive/archive_YYYY.json`

`scripts/sync_canonical_literature.py` first validates schema version, snapshot
time, source health, every declared SHA-256, each declared count, stable IDs,
and the current/archive split. Only then does it replace the website artifacts
and create the current-only `fluids-index.json`. A failed validation exits
without changing website data.

For a local dry integration run from this repository:

```bash
python3 scripts/sync_canonical_literature.py \
  --canonical-root /path/to/MySecondBrain \
  --website-root .
```

The scheduled GitHub Action checks out `yuningwang2329/MySecondBrain` about
twenty minutes after each of the four production windows. If that source
repository is private, configure `LITERATURE_SOURCE_TOKEN` as a fine-grained,
read-only GitHub token with access to it. It is not needed for a public source
repository.
