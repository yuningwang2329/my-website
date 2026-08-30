# Canonical literature mirror

This repository is a display mirror. It must not run `scripts/update_fluids.py`
or `scripts/ai_sweep.py` to change public paper data. MySecondBrain produces the
only canonical snapshot, publicly served from `https://my-second-brain-eta.vercel.app`:

- `literature-manifest.json`
- `fluids.json`
- `archive/archive_YYYY.json`

`scripts/sync_canonical_literature.py` first validates schema version, snapshot
time, source health, every declared SHA-256, each declared count, stable IDs,
and the current/archive split. Only then does it replace the website artifacts
and create the current-only `fluids-index.json`. A failed validation exits
without changing website data.

For a local dry integration run from this repository, keep using a checked-out
artifact tree:

```bash
python3 scripts/sync_canonical_literature.py \
  --canonical-root /path/to/MySecondBrain \
  --website-root .
```

For the production mirror, download the same public canonical snapshot into a
temporary staging directory first:

```bash
python3 scripts/sync_canonical_literature.py \
  --canonical-base-url https://my-second-brain-eta.vercel.app \
  --website-root .
```

The scheduled GitHub Action runs this public-URL mode about twenty minutes after
each of the four production windows. It never checks out MySecondBrain and needs
no cross-repository token. The downloader accepts only HTTP(S) responses from
the declared base URL, rejects absolute, parent-traversal, or cross-origin
artifact paths, and enforces the manifest/artifact byte caps before the existing
hash, count, schema, and freshness validation runs. Any download or validation
failure leaves the prior website snapshot unchanged.
