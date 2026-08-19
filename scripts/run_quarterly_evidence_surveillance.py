#!/usr/bin/env python3
"""Run the governed Evolved quarterly evidence-discovery and status-refresh engine.

The engine writes a private appraisal queue and a public, metadata-only cohort report.
It never writes the approved-studies bank, Horizon Watchlist, doctrine or downstream
systems. Promotion remains a separate human-reviewed workflow.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "reference/educational-intelligence/quarterly-surveillance-config.json"
DEFAULT_BANK = ROOT / "reference/educational-intelligence/approved-studies-bank.md"
DEFAULT_HORIZON = ROOT / "reference/educational-intelligence/emerging-science-horizon-watchlist.md"
DEFAULT_PUBLIC_ROOT = ROOT / "outputs/editorial/research/quarterly-surveillance"
DEFAULT_PRIVATE_ROOT = ROOT / "data/private/educational-intelligence/quarterly-runs"
CANONICAL_GUARDS = [
    DEFAULT_BANK,
    DEFAULT_HORIZON,
    ROOT / "reference/educational-intelligence/strength-training-doctrine.md",
    ROOT / "reference/educational-intelligence/nutrition-doctrine.md",
    ROOT / "reference/educational-intelligence/sleep-recovery-doctrine.md",
    ROOT / "reference/educational-intelligence/mindset-behaviour-doctrine.md",
]
LANES = ("strength", "nutrition", "sleep_recovery", "mindset_behaviour", "cross_pillar")
USER_AGENT = "Evolved-Educational-Intelligence/1.0 (quarterly evidence surveillance)"


class EngineError(RuntimeError):
    """Fail-closed engine error."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_hashes() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): sha256_file(path) for path in CANONICAL_GUARDS}


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EngineError(f"Cannot read valid configuration: {path}: {exc}") from exc
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    if config.get("schema_version") != "1.0":
        raise EngineError("Unsupported surveillance configuration schema")
    policy = config.get("promotion_policy", {})
    prohibited = (
        "automatic_approved_bank_write",
        "automatic_horizon_write",
        "automatic_doctrine_write",
        "automatic_downstream_cascade",
    )
    enabled = [key for key in prohibited if policy.get(key) is not False]
    if enabled:
        raise EngineError("Unsafe promotion policy; these controls must be false: " + ", ".join(enabled))
    if policy.get("human_appraisal_required") is not True:
        raise EngineError("human_appraisal_required must be true")
    seen: set[str] = set()
    for family in ("pubmed_queries", "clinical_trials_queries"):
        rows = config.get(family)
        if not isinstance(rows, list) or not rows:
            raise EngineError(f"{family} must be a non-empty list")
        for row in rows:
            query_id = row.get("id")
            lane = row.get("lane")
            if not query_id or query_id in seen:
                raise EngineError(f"Missing or duplicate query id: {query_id}")
            if lane not in LANES:
                raise EngineError(f"Invalid lane for {query_id}: {lane}")
            if not str(row.get("query", "")).strip():
                raise EngineError(f"Empty query for {query_id}")
            seen.add(query_id)


def parse_known_identities(bank_text: str, horizon_text: str) -> dict[str, set[str]]:
    pmids = set(re.findall(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", bank_text))
    pmids.update(re.findall(r"\bPMID\s+(\d{6,9})\b", bank_text))
    dois = {
        value.rstrip(".,;)").lower()
        for value in re.findall(r"\b10\.\d{4,9}/[^\s`|<]+", bank_text, flags=re.I)
    }
    ncts = set(re.findall(r"\bNCT\d{8}\b", horizon_text))
    horizon_pmids = set(re.findall(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", horizon_text))
    return {"pmids": pmids, "dois": dois, "ncts": ncts, "horizon_pmids": horizon_pmids}


def request_bytes(url: str, params: dict[str, Any] | None, timeout: int) -> bytes:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except Exception as exc:  # urllib exposes several unrelated exception classes
        raise EngineError(f"Network request failed for {url}: {exc}") from exc


def pubmed_search(query: str, start: dt.date, end: dt.date, limit: int, timeout: int) -> list[str]:
    payload = request_bytes(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        {
            "db": "pubmed",
            "term": query,
            "datetype": "pdat",
            "mindate": start.isoformat(),
            "maxdate": end.isoformat(),
            "retmax": limit,
            "retmode": "json",
            "sort": "pub date",
        },
        timeout,
    )
    time.sleep(0.36)
    data = json.loads(payload)
    return list(data.get("esearchresult", {}).get("idlist", []))


def chunks(values: list[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def first_text(node: ET.Element | None, path: str, default: str = "") -> str:
    if node is None:
        return default
    child = node.find(path)
    if child is None:
        return default
    return "".join(child.itertext()).strip()


def pubmed_fetch(pmids: list[str], timeout: int) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for batch in chunks(pmids, 100):
        payload = request_bytes(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            {"db": "pubmed", "id": ",".join(batch), "rettype": "abstract", "retmode": "xml"},
            timeout,
        )
        time.sleep(0.36)
        root = ET.fromstring(payload)
        for article in root.findall(".//PubmedArticle"):
            citation = article.find(".//MedlineCitation")
            pmid = first_text(citation, "PMID")
            article_node = citation.find("Article") if citation is not None else None
            title = first_text(article_node, "ArticleTitle")
            journal = first_text(article_node, "Journal/Title")
            pubdate = first_text(article_node, "Journal/JournalIssue/PubDate/MedlineDate")
            if not pubdate:
                year = first_text(article_node, "Journal/JournalIssue/PubDate/Year")
                month = first_text(article_node, "Journal/JournalIssue/PubDate/Month")
                pubdate = " ".join(value for value in (year, month) if value)
            authors = []
            if article_node is not None:
                for author in article_node.findall("AuthorList/Author")[:6]:
                    collective = first_text(author, "CollectiveName")
                    personal = " ".join(
                        value for value in (first_text(author, "LastName"), first_text(author, "Initials")) if value
                    )
                    if collective or personal:
                        authors.append(collective or personal)
            abstract_parts = []
            if article_node is not None:
                for part in article_node.findall("Abstract/AbstractText"):
                    label = part.attrib.get("Label", "")
                    value = "".join(part.itertext()).strip()
                    abstract_parts.append(f"{label}: {value}" if label else value)
            types = ["".join(item.itertext()).strip() for item in article.findall(".//PublicationType")]
            doi = ""
            # Only the article's own identifier list is authoritative here.
            # ReferenceList citations can also contain ArticleId nodes and must
            # never overwrite the paper's DOI used for stable deduplication.
            for identifier in article.findall(
                "PubmedData/ArticleIdList/ArticleId"
            ):
                if identifier.attrib.get("IdType") == "doi":
                    doi = (identifier.text or "").strip().lower()
            corrections = []
            if citation is not None:
                for item in citation.findall("CommentsCorrectionsList/CommentsCorrections"):
                    corrections.append(
                        {
                            "ref_type": item.attrib.get("RefType", ""),
                            "pmid": first_text(item, "PMID"),
                            "note": first_text(item, "Note"),
                        }
                    )
            records[pmid] = {
                "source": "pubmed",
                "pmid": pmid,
                "doi": doi,
                "title": html.unescape(title),
                "journal": journal,
                "publication_date": pubdate,
                "authors": authors,
                "publication_types": types,
                "abstract": " ".join(abstract_parts),
                "corrections": corrections,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            }
    return records


def clinical_trials_search(query: str, limit: int, timeout: int) -> list[dict[str, Any]]:
    payload = request_bytes(
        "https://clinicaltrials.gov/api/v2/studies",
        {"query.term": query, "pageSize": min(limit, 100), "format": "json", "countTotal": "true"},
        timeout,
    )
    data = json.loads(payload)
    return [normalise_trial(row) for row in data.get("studies", [])]


def clinical_trial_get(nct_id: str, timeout: int) -> dict[str, Any]:
    payload = request_bytes(f"https://clinicaltrials.gov/api/v2/studies/{nct_id}", {"format": "json"}, timeout)
    return normalise_trial(json.loads(payload))


def normalise_trial(study: dict[str, Any]) -> dict[str, Any]:
    protocol = study.get("protocolSection", {})
    identity = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    conditions = protocol.get("conditionsModule", {})
    nct_id = identity.get("nctId", "")
    enrolment = design.get("enrollmentInfo", {})
    return {
        "source": "clinicaltrials",
        "nct_id": nct_id,
        "title": identity.get("briefTitle") or identity.get("officialTitle") or "",
        "overall_status": status.get("overallStatus", "UNKNOWN"),
        "start_date": status.get("startDateStruct", {}).get("date", ""),
        "completion_date": status.get("completionDateStruct", {}).get("date", ""),
        "last_update": status.get("lastUpdatePostDateStruct", {}).get("date", ""),
        "enrolment": enrolment.get("count"),
        "conditions": conditions.get("conditions", []),
        "url": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else "",
    }


def fetch_live(
    config: dict[str, Any], known: dict[str, set[str]], start: dt.date, end: dt.date, refresh_horizon: bool
) -> dict[str, Any]:
    timeout = int(config["limits"]["http_timeout_seconds"])
    pubmed_limit = int(config["limits"]["pubmed_results_per_query"])
    trial_limit = int(config["limits"]["clinical_trials_results_per_query"])
    pmid_queries: dict[str, set[str]] = defaultdict(set)
    query_meta: dict[str, dict[str, str]] = {}
    for row in config["pubmed_queries"]:
        query_meta[row["id"]] = row
        for pmid in pubmed_search(row["query"], start, end, pubmed_limit, timeout):
            pmid_queries[pmid].add(row["id"])
    pubmed_records = pubmed_fetch(sorted(pmid_queries), timeout)
    for pmid, record in pubmed_records.items():
        record["query_ids"] = sorted(pmid_queries[pmid])
        record["lanes"] = sorted({query_meta[q]["lane"] for q in pmid_queries[pmid]})

    trial_queries: dict[str, set[str]] = defaultdict(set)
    trial_records: dict[str, dict[str, Any]] = {}
    trial_meta = {row["id"]: row for row in config["clinical_trials_queries"]}
    for row in config["clinical_trials_queries"]:
        for record in clinical_trials_search(row["query"], trial_limit, timeout):
            nct_id = record.get("nct_id")
            if not nct_id:
                continue
            trial_records[nct_id] = record
            trial_queries[nct_id].add(row["id"])
    for nct_id, record in trial_records.items():
        record["query_ids"] = sorted(trial_queries[nct_id])
        record["lanes"] = sorted({trial_meta[q]["lane"] for q in trial_queries[nct_id]})

    horizon_refresh = []
    if refresh_horizon:
        for nct_id in sorted(known["ncts"]):
            record = clinical_trial_get(nct_id, timeout)
            record["known_horizon"] = True
            horizon_refresh.append(record)

    safety_flags = []
    if known["pmids"]:
        existing = pubmed_fetch(sorted(known["pmids"]), timeout)
        for record in existing.values():
            types = set(record.get("publication_types", []))
            corrections = record.get("corrections", [])
            flagged_types = types.intersection(
                {"Retracted Publication", "Retraction of Publication", "Expression of Concern", "Published Erratum"}
            )
            flagged_relations = [
                item for item in corrections if item.get("ref_type") in {"RetractionIn", "ExpressionOfConcernIn", "ErratumIn"}
            ]
            if flagged_types or flagged_relations:
                safety_flags.append(record)

    return {
        "pubmed": list(pubmed_records.values()),
        "trials": list(trial_records.values()),
        "horizon_refresh": horizon_refresh,
        "safety_flags": safety_flags,
    }


def load_fixture(path: Path) -> dict[str, Any]:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EngineError(f"Cannot load fixture {path}: {exc}") from exc
    for key in ("pubmed", "trials", "horizon_refresh", "safety_flags"):
        if not isinstance(fixture.get(key, []), list):
            raise EngineError(f"Fixture field {key} must be a list")
        fixture.setdefault(key, [])
    return fixture


def classify_candidates(payload: dict[str, Any], known: dict[str, set[str]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for record in payload["pubmed"]:
        pmid = str(record.get("pmid", ""))
        doi = str(record.get("doi", "")).lower()
        duplicate = pmid in known["pmids"] or (bool(doi) and doi in known["dois"])
        candidates.append(
            {
                "candidate_id": f"PMID-{pmid}",
                "source": "PUBMED",
                "stable_id": pmid,
                "title": record.get("title", ""),
                "date": record.get("publication_date", ""),
                "lanes": ";".join(record.get("lanes", [])),
                "query_ids": ";".join(record.get("query_ids", [])),
                "duplicate_state": "EXISTING_BANK" if duplicate else "NEW",
                "review_state": "DISCOVERED — HUMAN APPRAISAL REQUIRED",
                "proposed_destination": "DEDUPLICATE" if duplicate else "APPRAISAL_QUEUE",
                "url": record.get("url", ""),
            }
        )
    for record in payload["trials"]:
        nct_id = str(record.get("nct_id", ""))
        duplicate = nct_id in known["ncts"]
        candidates.append(
            {
                "candidate_id": nct_id,
                "source": "CLINICALTRIALS",
                "stable_id": nct_id,
                "title": record.get("title", ""),
                "date": record.get("last_update", ""),
                "lanes": ";".join(record.get("lanes", [])),
                "query_ids": ";".join(record.get("query_ids", [])),
                "duplicate_state": "EXISTING_HORIZON" if duplicate else "NEW",
                "review_state": "DISCOVERED — HUMAN APPRAISAL REQUIRED",
                "proposed_destination": "STATUS_REFRESH" if duplicate else "HORIZON_APPRAISAL",
                "url": record.get("url", ""),
            }
        )
    return sorted(candidates, key=lambda row: (row["source"], row["candidate_id"]))


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "candidate_id",
        "source",
        "stable_id",
        "title",
        "date",
        "lanes",
        "query_ids",
        "duplicate_state",
        "review_state",
        "proposed_destination",
        "url",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def report_markdown(
    run_id: str,
    as_of: dt.date,
    start: dt.date,
    config: dict[str, Any],
    candidates: list[dict[str, Any]],
    payload: dict[str, Any],
    known: dict[str, set[str]],
    fixture: bool,
) -> str:
    by_lane = {lane: 0 for lane in LANES}
    new_count = 0
    duplicate_count = 0
    for row in candidates:
        if row["duplicate_state"] == "NEW":
            new_count += 1
        else:
            duplicate_count += 1
        for lane in filter(None, row["lanes"].split(";")):
            by_lane[lane] = by_lane.get(lane, 0) + 1
    lines = [
        "# Quarterly Evidence Surveillance Cohort Report",
        "",
        f"**Run ID:** `{run_id}`  ",
        f"**Evidence window:** {start.isoformat()} to {as_of.isoformat()}  ",
        f"**Execution mode:** {'OFFLINE ACCEPTANCE FIXTURE' if fixture else 'LIVE PUBLIC-METADATA DISCOVERY'}  ",
        "**Promotion state:** `HELD — HUMAN APPRAISAL REQUIRED`  ",
        "",
        "## Outcome",
        "",
        "The discovery and status-refresh phase completed without writing the approved-studies bank, Horizon Watchlist, doctrine, services or live systems. Candidate discovery is not evidence approval.",
        "",
        "| Measure | Count |",
        "| --- | ---: |",
        f"| Existing approved-study PMIDs recognised | {len(known['pmids'])} |",
        f"| Existing Horizon NCT identities recognised | {len(known['ncts'])} |",
        f"| Candidate rows | {len(candidates)} |",
        f"| New identities requiring appraisal | {new_count} |",
        f"| Existing identities deduplicated or refreshed | {duplicate_count} |",
        f"| Existing-study correction/retraction flags | {len(payload['safety_flags'])} |",
        f"| Horizon status snapshots | {len(payload['horizon_refresh'])} |",
        "",
        "## Four-lane impact queue",
        "",
        "| Lane | Candidate touches | Doctrine impact state |",
        "| --- | ---: | --- |",
    ]
    labels = {
        "strength": "Strength Training",
        "nutrition": "Nutrition",
        "sleep_recovery": "Sleep/Recovery",
        "mindset_behaviour": "Mindset/Behaviour",
        "cross_pillar": "Cross-pillar/frontier",
    }
    for lane in LANES:
        state = "REVIEW REQUIRED" if by_lane.get(lane, 0) else "REVIEWED — NO DISCOVERY HIT"
        lines.append(f"| {labels[lane]} | {by_lane.get(lane, 0)} | `{state}` |")
    lines.extend(
        [
            "",
            "## Mandatory manual refresh",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in config["manual_refresh_families"])
    lines.extend(
        [
            "",
            "## Promotion gates",
            "",
            "1. Verify identity, methods, population, outcomes, harms, funding and correction status.",
            "2. Deduplicate against the approved bank and Horizon register.",
            "3. Record claim-specific approved use and prohibited overreach.",
            "4. Reconcile supporting, neutral and conflicting evidence.",
            "5. Run doctrine regression for any material implication.",
            "6. Present Peter only with a genuine unresolved Evolved decision.",
            "",
            "No candidate may enter the corpus merely because it was recent, highly cited, positive or commercially interesting.",
            "",
            "## Next controlled action",
            "",
            "Review the private appraisal queue for inclusion, exclusion, duplicate resolution and priority. A later reviewed promotion run must remain separate from this discovery run.",
            "",
            "## Boundary confirmation",
            "",
            "- Approved-studies bank: unchanged by engine.",
            "- Horizon Watchlist: unchanged by engine.",
            "- Doctrine and life-stage overlays: unchanged by engine.",
            "- WordPress, GoHighLevel, Trainerize and other live systems: untouched.",
        ]
    )
    return "\n".join(lines) + "\n"


def ensure_roots(public_root: Path, private_root: Path, allow_noncanonical: bool) -> None:
    if allow_noncanonical:
        return
    for actual, expected, label in (
        (public_root, DEFAULT_PUBLIC_ROOT, "public output"),
        (private_root, DEFAULT_PRIVATE_ROOT, "private output"),
    ):
        try:
            actual.resolve().relative_to(expected.resolve())
        except ValueError as exc:
            raise EngineError(f"{label} must remain under {expected}") from exc


def run(args: argparse.Namespace) -> dict[str, Any]:
    config = load_config(args.config)
    as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    start = as_of - dt.timedelta(days=int(config["cadence"]["lookback_days"]))
    config_hash = sha256_file(args.config)[:10]
    run_id = f"QE-{as_of.isoformat()}-{config_hash}"
    public_root = args.output_root.resolve()
    private_root = args.private_root.resolve()
    ensure_roots(public_root, private_root, args.allow_noncanonical_output)
    public_dir = public_root / run_id
    private_dir = private_root / run_id
    for path in (public_dir, private_dir):
        if path.exists() and not args.replace:
            raise EngineError(f"Run output already exists; use a new date or --replace: {path}")
        path.mkdir(parents=True, exist_ok=True)

    bank_text = DEFAULT_BANK.read_text(encoding="utf-8")
    horizon_text = DEFAULT_HORIZON.read_text(encoding="utf-8")
    known = parse_known_identities(bank_text, horizon_text)
    guard_before = canonical_hashes()
    if args.fixture:
        payload = load_fixture(args.fixture)
    else:
        payload = fetch_live(config, known, start, as_of, not args.skip_horizon_refresh)
    candidates = classify_candidates(payload, known)

    raw_path = private_dir / "raw-normalised.json"
    raw_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    queue_path = private_dir / "appraisal-queue.tsv"
    write_tsv(queue_path, candidates)
    guard_after = canonical_hashes()
    if guard_before != guard_after:
        raise EngineError("Canonical Educational Intelligence files changed during discovery; run rejected")

    report = report_markdown(run_id, as_of, start, config, candidates, payload, known, bool(args.fixture))
    report_path = public_dir / "cohort-report.md"
    report_path.write_text(report, encoding="utf-8")
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
        "as_of": as_of.isoformat(),
        "window_start": start.isoformat(),
        "mode": "fixture" if args.fixture else "live_discovery",
        "promotion_state": "HELD_HUMAN_APPRAISAL_REQUIRED",
        "counts": {
            "candidates": len(candidates),
            "new": sum(row["duplicate_state"] == "NEW" for row in candidates),
            "existing": sum(row["duplicate_state"] != "NEW" for row in candidates),
            "safety_flags": len(payload["safety_flags"]),
            "horizon_refresh": len(payload["horizon_refresh"]),
        },
        "artifacts": {
            "public_report": str(report_path),
            "private_queue": str(queue_path),
            "private_raw": str(raw_path),
            "private_queue_sha256": sha256_file(queue_path),
            "private_raw_sha256": sha256_file(raw_path),
        },
        "canonical_hashes_before": guard_before,
        "canonical_hashes_after": guard_after,
        "canonical_mutation": False,
        "live_system_mutation": False,
    }
    manifest_path = public_dir / "run-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate", help="Validate the safe engine configuration")
    validate_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    smoke_parser = subparsers.add_parser("smoke", help="Read-only connectivity and parser check")
    smoke_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    smoke_parser.add_argument("--as-of", help="Evidence cutoff in YYYY-MM-DD format")
    run_parser = subparsers.add_parser("run", help="Run discovery and produce a held appraisal queue")
    run_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    run_parser.add_argument("--as-of", help="Evidence cutoff in YYYY-MM-DD format")
    run_parser.add_argument("--fixture", type=Path, help="Use a normalised offline acceptance fixture")
    run_parser.add_argument("--skip-horizon-refresh", action="store_true")
    run_parser.add_argument("--output-root", type=Path, default=DEFAULT_PUBLIC_ROOT)
    run_parser.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE_ROOT)
    run_parser.add_argument("--allow-noncanonical-output", action="store_true", help=argparse.SUPPRESS)
    run_parser.add_argument("--replace", action="store_true", help="Replace artifacts for the same deterministic run id")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "validate":
            config = load_config(args.config)
            known = parse_known_identities(
                DEFAULT_BANK.read_text(encoding="utf-8"), DEFAULT_HORIZON.read_text(encoding="utf-8")
            )
            print(
                json.dumps(
                    {
                        "state": "VALID",
                        "schema_version": config["schema_version"],
                        "pubmed_queries": len(config["pubmed_queries"]),
                        "clinical_trials_queries": len(config["clinical_trials_queries"]),
                        "known_bank_pmids": len(known["pmids"]),
                        "known_horizon_ncts": len(known["ncts"]),
                        "automatic_promotion": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        if args.command == "smoke":
            config = load_config(args.config)
            as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
            start = as_of - dt.timedelta(days=30)
            timeout = int(config["limits"]["http_timeout_seconds"])
            pubmed_query = config["pubmed_queries"][0]
            trial_query = config["clinical_trials_queries"][0]
            pmids = pubmed_search(pubmed_query["query"], start, as_of, 1, timeout)
            articles = pubmed_fetch(pmids, timeout) if pmids else {}
            trials = clinical_trials_search(trial_query["query"], 1, timeout)
            print(
                json.dumps(
                    {
                        "state": "PASS",
                        "writes": False,
                        "pubmed_query": pubmed_query["id"],
                        "pubmed_records_parsed": len(articles),
                        "clinical_trials_query": trial_query["id"],
                        "clinical_trials_records_parsed": len(trials),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        manifest = run(args)
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0
    except (EngineError, ValueError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
