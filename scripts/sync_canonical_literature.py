#!/usr/bin/env python3
"""Validate and mirror the canonical MySecondBrain literature artifacts.

The website deliberately never fetches journals itself.  This module accepts a
checked-out canonical artifact tree, validates every artifact named by its
manifest, and replaces website data only after the complete snapshot is known
to be sound.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
WINDOW_DAYS = 90
MAX_ARTIFACT_BYTES = 25 * 1024 * 1024
MAX_GENERATION_AGE = timedelta(days=8)
MANIFEST_FILE = "literature-manifest.json"
INDEX_FILE = "fluids-index.json"

REQUIRED_RECORD_FIELDS = (
    "id",
    "title",
    "authors",
    "date",
    "source",
    "source_group",
    "link",
    "abstract_en",
    "summary_zh",
    "topic",
    "tags",
    "relevance",
)
INDEX_RECORD_FIELDS = (
    "id",
    "title",
    "authors",
    "date",
    "source",
    "source_group",
    "link",
    "topic",
    "tags",
    "relevance",
)


class CanonicalSyncError(ValueError):
    """Raised when a canonical snapshot cannot safely replace website data."""


@dataclass(frozen=True)
class Artifact:
    path: Path
    count: int
    payload: bytes
    papers: list[dict[str, Any]]
    year: int | None = None


@dataclass(frozen=True)
class CanonicalSnapshot:
    manifest: dict[str, Any]
    manifest_payload: bytes
    current: Artifact
    archives: tuple[Artifact, ...]


@dataclass(frozen=True)
class SyncResult:
    generation_id: str
    active_count: int
    archive_count: int
    archive_years: tuple[int, ...]


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise CanonicalSyncError("manifest generated_at must be a non-empty ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise CanonicalSyncError("manifest generated_at is not ISO-8601") from error
    if parsed.tzinfo is None:
        raise CanonicalSyncError("manifest generated_at must include a timezone")
    return parsed.astimezone(timezone.utc)


def _relative_json_path(value: Any, *, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise CanonicalSyncError(f"{label}.path must be a non-empty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.suffix != ".json":
        raise CanonicalSyncError(f"{label}.path is not a safe JSON relative path")
    return path


def _read_artifact(source_root: Path, descriptor: Any, *, label: str, year: int | None = None) -> Artifact:
    if not isinstance(descriptor, dict):
        raise CanonicalSyncError(f"{label} must be an object")
    path = _relative_json_path(descriptor.get("path"), label=label)
    expected_count = descriptor.get("count")
    expected_hash = descriptor.get("sha256")
    if not isinstance(expected_count, int) or expected_count < 0:
        raise CanonicalSyncError(f"{label}.count must be a non-negative integer")
    if not isinstance(expected_hash, str) or len(expected_hash) != 64:
        raise CanonicalSyncError(f"{label}.sha256 must be a SHA-256 digest")

    artifact_file = source_root / path
    try:
        payload = artifact_file.read_bytes()
    except OSError as error:
        raise CanonicalSyncError(f"cannot read {label} artifact: {path}") from error
    if len(payload) > MAX_ARTIFACT_BYTES:
        raise CanonicalSyncError(f"{label} artifact exceeds the {MAX_ARTIFACT_BYTES} byte limit")
    if _sha256(payload) != expected_hash.lower():
        raise CanonicalSyncError(f"{label} artifact hash does not match manifest")
    try:
        papers = json.loads(payload)
    except json.JSONDecodeError as error:
        raise CanonicalSyncError(f"{label} artifact is not valid JSON") from error
    if not isinstance(papers, list):
        raise CanonicalSyncError(f"{label} artifact must be a JSON array")
    if len(papers) != expected_count:
        raise CanonicalSyncError(f"{label} artifact count does not match manifest")
    _validate_papers(papers, label=label)
    return Artifact(path=path, count=expected_count, payload=payload, papers=papers, year=year)


def _validate_papers(papers: list[Any], *, label: str) -> None:
    identifiers: set[str] = set()
    for index, paper in enumerate(papers):
        if not isinstance(paper, dict):
            raise CanonicalSyncError(f"{label}[{index}] must be an object")
        missing = [field for field in REQUIRED_RECORD_FIELDS if field not in paper]
        if missing:
            raise CanonicalSyncError(f"{label}[{index}] is missing required fields: {', '.join(missing)}")
        identifier = paper["id"]
        if not isinstance(identifier, str) or not identifier.strip():
            raise CanonicalSyncError(f"{label}[{index}].id must be a non-empty string")
        if identifier in identifiers:
            raise CanonicalSyncError(f"{label} contains duplicate stable id {identifier}")
        identifiers.add(identifier)
        if not isinstance(paper["tags"], list):
            raise CanonicalSyncError(f"{label}[{index}].tags must be an array")
        if not isinstance(paper["date"], str) or len(paper["date"]) != 10:
            raise CanonicalSyncError(f"{label}[{index}].date must be YYYY-MM-DD")
        try:
            datetime.strptime(paper["date"], "%Y-%m-%d")
        except ValueError as error:
            raise CanonicalSyncError(f"{label}[{index}].date must be YYYY-MM-DD") from error


def _validate_manifest(manifest: Any, *, now: datetime, max_generation_age: timedelta) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise CanonicalSyncError("manifest must be a JSON object")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise CanonicalSyncError(f"unsupported manifest schema_version {manifest.get('schema_version')!r}")
    if not isinstance(manifest.get("generation_id"), str) or not manifest["generation_id"].strip():
        raise CanonicalSyncError("manifest generation_id must be a non-empty string")
    if not isinstance(manifest.get("policy_version"), str) or not manifest["policy_version"].strip():
        raise CanonicalSyncError("manifest policy_version must be a non-empty string")
    if manifest.get("window_days") != WINDOW_DAYS:
        raise CanonicalSyncError(f"manifest window_days must equal {WINDOW_DAYS}")

    generated_at = _parse_timestamp(manifest.get("generated_at"))
    if generated_at > now + timedelta(minutes=5):
        raise CanonicalSyncError("manifest generated_at is in the future")
    if now - generated_at > max_generation_age:
        raise CanonicalSyncError("manifest generation is older than the allowed freshness window")

    counts = manifest.get("counts")
    if not isinstance(counts, dict) or any(not isinstance(counts.get(key), int) or counts[key] < 0 for key in ("current", "archived", "review")):
        raise CanonicalSyncError("manifest counts must contain non-negative current, archived, and review integers")
    sources = manifest.get("sources")
    if not isinstance(sources, dict):
        raise CanonicalSyncError("manifest sources must be an object")
    total = sources.get("total")
    succeeded = sources.get("succeeded")
    failed_ids = sources.get("failed_ids")
    if not isinstance(total, int) or total < 1 or not isinstance(succeeded, int) or not 0 <= succeeded <= total:
        raise CanonicalSyncError("manifest source totals are invalid")
    if not isinstance(failed_ids, list) or any(not isinstance(item, str) or not item for item in failed_ids):
        raise CanonicalSyncError("manifest failed_ids must be an array of source identifiers")
    if succeeded + len(failed_ids) != total:
        raise CanonicalSyncError("manifest source counts do not agree with failed_ids")
    return manifest


def load_canonical_snapshot(
    source_root: Path | str,
    *,
    now: datetime | None = None,
    max_generation_age: timedelta = MAX_GENERATION_AGE,
) -> CanonicalSnapshot:
    """Read and fully validate a source tree without modifying the website."""
    source_root = Path(source_root).resolve()
    manifest_path = source_root / MANIFEST_FILE
    try:
        manifest_payload = manifest_path.read_bytes()
        manifest = json.loads(manifest_payload)
    except OSError as error:
        raise CanonicalSyncError(f"cannot read {MANIFEST_FILE}") from error
    except json.JSONDecodeError as error:
        raise CanonicalSyncError(f"{MANIFEST_FILE} is not valid JSON") from error

    snapshot_now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    manifest = _validate_manifest(manifest, now=snapshot_now, max_generation_age=max_generation_age)
    current = _read_artifact(source_root, manifest.get("current"), label="current")

    archives_config = manifest.get("archives")
    if not isinstance(archives_config, list):
        raise CanonicalSyncError("manifest archives must be an array")
    archives: list[Artifact] = []
    years: set[int] = set()
    artifact_paths = {current.path}
    active_ids = {paper["id"] for paper in current.papers}
    archived_ids: set[str] = set()
    for descriptor in archives_config:
        if not isinstance(descriptor, dict) or not isinstance(descriptor.get("year"), int):
            raise CanonicalSyncError("each archive descriptor must include an integer year")
        year = descriptor["year"]
        if year in years:
            raise CanonicalSyncError(f"manifest has duplicate archive year {year}")
        archive = _read_artifact(source_root, descriptor, label=f"archive {year}", year=year)
        if archive.path in artifact_paths:
            raise CanonicalSyncError(f"manifest reuses artifact path {archive.path}")
        artifact_paths.add(archive.path)
        archive_ids = {paper["id"] for paper in archive.papers}
        duplicate_ids = (active_ids | archived_ids) & archive_ids
        if duplicate_ids:
            raise CanonicalSyncError(f"archive {year} repeats a stable id from another snapshot")
        archived_ids.update(archive_ids)
        years.add(year)
        archives.append(archive)
    if manifest["counts"]["current"] != current.count:
        raise CanonicalSyncError("manifest current count does not match current artifact")
    if manifest["counts"]["archived"] != sum(archive.count for archive in archives):
        raise CanonicalSyncError("manifest archived count does not match archive artifacts")
    return CanonicalSnapshot(
        manifest=manifest,
        manifest_payload=manifest_payload,
        current=current,
        archives=tuple(sorted(archives, key=lambda artifact: artifact.year or 0, reverse=True)),
    )


def build_lightweight_index(snapshot: CanonicalSnapshot) -> bytes:
    """Produce a small current-only homepage index without article abstracts."""
    papers = []
    for paper in snapshot.current.papers:
        index_paper = {field: paper[field] for field in INDEX_RECORD_FIELDS}
        if isinstance(paper.get("filename"), str) and paper["filename"]:
            index_paper["filename"] = paper["filename"]
        papers.append(index_paper)
    index = {
        "schema_version": SCHEMA_VERSION,
        "generation_id": snapshot.manifest["generation_id"],
        "generated_at": snapshot.manifest["generated_at"],
        "policy_version": snapshot.manifest["policy_version"],
        "window_days": snapshot.manifest["window_days"],
        "count": snapshot.current.count,
        "sources": snapshot.manifest["sources"],
        "archives": [
            {"year": archive.year, "path": archive.path.as_posix(), "count": archive.count}
            for archive in snapshot.archives
        ],
        "papers": papers,
    }
    return json.dumps(index, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _stage_snapshot(snapshot: CanonicalSnapshot, staging_root: Path) -> list[Path]:
    staged_paths: list[Path] = []
    artifacts = (snapshot.current, *snapshot.archives)
    for artifact in artifacts:
        staged_path = staging_root / artifact.path
        staged_path.parent.mkdir(parents=True, exist_ok=True)
        staged_path.write_bytes(artifact.payload)
        staged_paths.append(artifact.path)
    (staging_root / MANIFEST_FILE).write_bytes(snapshot.manifest_payload)
    staged_paths.append(Path(MANIFEST_FILE))
    (staging_root / INDEX_FILE).write_bytes(build_lightweight_index(snapshot))
    staged_paths.append(Path(INDEX_FILE))
    return staged_paths


def sync_canonical_artifacts(
    source_root: Path | str,
    target_root: Path | str,
    *,
    now: datetime | None = None,
    max_generation_age: timedelta = MAX_GENERATION_AGE,
) -> SyncResult:
    """Validate then atomically replace the website data artifacts for one snapshot."""
    snapshot = load_canonical_snapshot(source_root, now=now, max_generation_age=max_generation_age)
    target_root = Path(target_root).resolve()
    target_root.mkdir(parents=True, exist_ok=True)
    staging_root = Path(tempfile.mkdtemp(prefix=".canonical-sync-", dir=target_root.parent))
    try:
        staged_paths = _stage_snapshot(snapshot, staging_root)
        for relative_path in staged_paths:
            destination = target_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staging_root / relative_path, destination)
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)
    return SyncResult(
        generation_id=snapshot.manifest["generation_id"],
        active_count=snapshot.current.count,
        archive_count=sum(archive.count for archive in snapshot.archives),
        archive_years=tuple(archive.year for archive in snapshot.archives if archive.year is not None),
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mirror validated canonical literature artifacts into this website.")
    parser.add_argument(
        "--canonical-root",
        default=os.environ.get("CANONICAL_LITERATURE_ROOT", "canonical"),
        help="checked-out MySecondBrain canonical artifact root",
    )
    parser.add_argument(
        "--website-root",
        default=".",
        help="website repository root to receive validated artifacts",
    )
    parser.add_argument(
        "--max-generation-age-hours",
        type=float,
        default=MAX_GENERATION_AGE.total_seconds() / 3600,
        help="reject a canonical generation older than this many hours",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.max_generation_age_hours <= 0:
        raise SystemExit("--max-generation-age-hours must be positive")
    try:
        result = sync_canonical_artifacts(
            args.canonical_root,
            args.website_root,
            max_generation_age=timedelta(hours=args.max_generation_age_hours),
        )
    except CanonicalSyncError as error:
        print(f"Canonical literature sync refused: {error}")
        return 1
    print(
        "Mirrored canonical generation "
        f"{result.generation_id}: {result.active_count} active, "
        f"{result.archive_count} archived across {len(result.archive_years)} years."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
