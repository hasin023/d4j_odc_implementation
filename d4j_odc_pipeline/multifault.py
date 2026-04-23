"""Multi-fault data loader for the defects4j-mf dataset.

Reads the ``fault_data/`` JSON files produced by the defects4j-mf project
(https://github.com/DCallaz/defects4j-mf) and exposes a pure-Python query
API.  No dependency on the defects4j-mf CLI tools — only the JSON artefacts
are required.

Supported projects (defects4j-mf v1.0): Chart, Closure, Lang, Math, Time.

File format reference
---------------------
``{Project}.json``
    ``{ version_id: { fault_id: [triggering_test_names] } }``
    Tells us which historical faults are *still exposed* (have a
    failing test) in each later version.

``{Project}_backtrack.json``
    ``[ { "bug": { fault_id: { file: [lines] } }, version_n: ... }, ... ]``
    Tells us the *exact source locations* of each fault as tracked
    backwards through the project's commit history.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FaultLocation:
    """A single fault's location in a specific version."""
    fault_id: int
    file_path: str
    lines: list[int]


@dataclass
class CoexistingFault:
    """A fault that co-exists in a version alongside the target bug."""
    fault_id: int
    triggering_tests: list[str]
    locations: list[FaultLocation]


@dataclass
class MultiFaultSummary:
    """Structured summary of multi-fault data for one bug version."""
    project_id: str
    bug_id: int
    version_id: str
    total_coexisting_faults: int
    coexisting_fault_ids: list[int]
    coexisting_faults: list[CoexistingFault]
    data_available: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_PROJECTS = frozenset({"Chart", "Closure", "Lang", "Math", "Time"})


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _resolve_fault_data_dir() -> Path | None:
    """Resolve the fault_data directory from env or common locations."""
    env_dir = os.environ.get("MULTIFAULT_DATA_DIR", "").strip()
    if env_dir:
        p = Path(env_dir)
        if p.is_dir():
            return p
    # Fallback: look in implementation/fault_data
    candidate = Path(__file__).resolve().parent.parent / "fault_data"
    if candidate.is_dir():
        return candidate
    return None


def load_fault_tests(fault_data_dir: Path, project: str) -> dict[str, dict[str, list[str]]]:
    """Load ``{Project}.json`` — version → fault_id → [test_names].

    Returns an empty dict if the file does not exist.
    """
    path = fault_data_dir / f"{project}.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data


def load_fault_backtrack(fault_data_dir: Path, project: str) -> list[dict[str, Any]]:
    """Load ``{Project}_backtrack.json`` — fault location tracking.

    Returns an empty list if the file does not exist.
    """
    path = fault_data_dir / f"{project}_backtrack.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return data


# ---------------------------------------------------------------------------
# Querying
# ---------------------------------------------------------------------------

def get_coexisting_fault_ids(
    fault_data_dir: Path,
    project: str,
    bug_id: int,
) -> list[int]:
    """Return sorted list of fault IDs that co-exist in version ``bug_id``.

    Uses ``{Project}.json``.  The version key is the string representation
    of the bug_id.  Each fault listed under that version is a co-existing
    fault whose triggering test still fails in this version.
    """
    tests_data = load_fault_tests(fault_data_dir, project)
    version_key = str(bug_id)
    version_faults = tests_data.get(version_key, {})

    fault_ids: list[int] = []
    for fid_str in version_faults:
        try:
            fault_ids.append(int(fid_str))
        except ValueError:
            continue
    return sorted(fault_ids)


def get_fault_tests(
    fault_data_dir: Path,
    project: str,
    bug_id: int,
    fault_id: int,
) -> list[str]:
    """Return the triggering tests for ``fault_id`` in version ``bug_id``."""
    tests_data = load_fault_tests(fault_data_dir, project)
    version_key = str(bug_id)
    fault_key = str(fault_id)
    version_faults = tests_data.get(version_key, {})
    tests = version_faults.get(fault_key, [])
    if isinstance(tests, list):
        return [str(t) for t in tests]
    return []


def get_fault_locations(
    fault_data_dir: Path,
    project: str,
    bug_id: int,
    fault_id: int,
) -> list[FaultLocation]:
    """Return the source locations for ``fault_id`` in version ``bug_id``.

    Uses ``{Project}_backtrack.json``.  Each entry in the backtrack array
    represents one fault.  The ``"bug"`` key holds the original fault
    metadata, and subsequent version keys hold tracked locations.
    """
    backtrack = load_fault_backtrack(fault_data_dir, project)
    version_key = str(bug_id)
    fault_key = str(fault_id)

    locations: list[FaultLocation] = []
    for entry in backtrack:
        # Check if this backtrack entry is about the requested fault
        bug_data = entry.get("bug", {})
        if fault_key not in bug_data:
            continue

        # Look up the locations in the requested version
        version_data = entry.get(version_key, {})
        if not isinstance(version_data, dict):
            continue

        fault_locs = version_data.get(fault_key, {})
        if isinstance(fault_locs, str):
            # Some entries have "failed" strings for commits
            continue
        if not isinstance(fault_locs, dict):
            continue

        for file_path, lines in fault_locs.items():
            if isinstance(lines, list):
                locations.append(FaultLocation(
                    fault_id=fault_id,
                    file_path=file_path,
                    lines=sorted(lines),
                ))
    return locations


def get_multifault_summary(
    project: str,
    bug_id: int,
    fault_data_dir: Path | None = None,
) -> MultiFaultSummary:
    """Build a complete multi-fault summary for a single bug version.

    Parameters
    ----------
    project : str
        Defects4J project ID (e.g., "Lang").
    bug_id : int
        Defects4J bug ID.
    fault_data_dir : Path or None
        Directory containing the fault_data JSON files.
        If None, resolved from ``MULTIFAULT_DATA_DIR`` env var or
        ``implementation/fault_data``.
    """
    version_id = f"{bug_id}b"
    notes: list[str] = []

    if project not in SUPPORTED_PROJECTS:
        return MultiFaultSummary(
            project_id=project,
            bug_id=bug_id,
            version_id=version_id,
            total_coexisting_faults=0,
            coexisting_fault_ids=[],
            coexisting_faults=[],
            data_available=False,
            notes=[
                f"Project '{project}' is not covered by defects4j-mf. "
                f"Supported projects: {', '.join(sorted(SUPPORTED_PROJECTS))}."
            ],
        )

    if fault_data_dir is None:
        fault_data_dir = _resolve_fault_data_dir()

    if fault_data_dir is None or not fault_data_dir.is_dir():
        return MultiFaultSummary(
            project_id=project,
            bug_id=bug_id,
            version_id=version_id,
            total_coexisting_faults=0,
            coexisting_fault_ids=[],
            coexisting_faults=[],
            data_available=False,
            notes=["fault_data directory not found. Set MULTIFAULT_DATA_DIR or place fault_data/ in implementation/."],
        )

    fault_ids = get_coexisting_fault_ids(fault_data_dir, project, bug_id)

    if not fault_ids:
        # Version might not have co-existing faults, or it's an early version
        return MultiFaultSummary(
            project_id=project,
            bug_id=bug_id,
            version_id=version_id,
            total_coexisting_faults=0,
            coexisting_fault_ids=[],
            coexisting_faults=[],
            data_available=True,
            notes=[f"No co-existing faults found for {project}-{bug_id}. "
                   "This may indicate the version is too early in the history to have accumulated faults."],
        )

    coexisting: list[CoexistingFault] = []
    for fid in fault_ids:
        tests = get_fault_tests(fault_data_dir, project, bug_id, fid)
        locs = get_fault_locations(fault_data_dir, project, bug_id, fid)
        coexisting.append(CoexistingFault(
            fault_id=fid,
            triggering_tests=tests,
            locations=locs,
        ))

    # Note about fault density
    own_fault = bug_id in fault_ids
    other_count = len(fault_ids) - (1 if own_fault else 0)
    if other_count > 0:
        notes.append(
            f"Version {project}-{bug_id} contains {len(fault_ids)} co-existing fault(s) "
            f"({other_count} from OTHER bugs besides bug #{bug_id} itself). "
            "This is consistent with defects4j-mf findings of ~9.2 co-existing faults per version."
        )

    return MultiFaultSummary(
        project_id=project,
        bug_id=bug_id,
        version_id=version_id,
        total_coexisting_faults=len(fault_ids),
        coexisting_fault_ids=fault_ids,
        coexisting_faults=coexisting,
        data_available=True,
        notes=notes,
    )


def enrich_classification(
    classification: dict[str, Any],
    fault_data_dir: Path | None = None,
) -> dict[str, Any]:
    """Add multi-fault context to an existing classification dict.

    Non-destructive: returns a new dict with the ``multifault_context``
    key added.  The original classification fields are preserved.
    """
    project = str(classification.get("project_id", ""))
    bug_id = int(classification.get("bug_id", 0))

    summary = get_multifault_summary(project, bug_id, fault_data_dir)
    enriched = dict(classification)
    enriched["multifault_context"] = summary.to_dict()
    return enriched
