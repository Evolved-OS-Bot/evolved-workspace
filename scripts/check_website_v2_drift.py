#!/usr/bin/env python3
"""Read-only consistency and optional live checks for Evolved Website V2."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "outputs/systems/website-v2-release-manifest.md"
HASHES = ROOT / "wordpress/website-v2/SOURCE_SHA256SUMS.txt"
SOURCE = ROOT / "wordpress/website-v2"
ROUTE_REGISTER = ROOT / "outputs/systems/website-v2-ghl-route-register.json"
GHL_BASELINE_HTML = (
    ROOT
    / "data/private/website-migration-baselines/2026-08-03-phase1/public-crawl/html"
)

REQUIRED_MANIFEST = {
    "release_id": "website-v2",
    "product": "Evolved Website V2",
    "status": "built_live_pre_root_promotion",
    "runtime_url": "https://blog.theevolvedgym.com.au/",
    "wordpress_homepage_post_id": "165",
    "homepage_h1": "Brisbane's Leading Women-Only Gym",
    "homepage_primary_cta": "Join the Waitlist",
    "homepage_js_asset_version": "59.0",
    "ghl_route_register": "outputs/systems/website-v2-ghl-route-register.json",
}


class Audit:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def pass_(self, message: str) -> None:
        print(f"PASS  {message}")

    def fail(self, message: str) -> None:
        self.failures.append(message)
        print(f"FAIL  {message}")

    def check(self, condition: bool, success: str, failure: str) -> None:
        if condition:
            self.pass_(success)
        else:
            self.fail(failure)


def parse_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path} has no front matter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path} has unclosed front matter")
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"invalid front-matter line: {line}")
        values[key.strip()] = value.strip().strip("\"'")
    return values


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def extract_ghl_routes_from_baseline() -> tuple[set[str], set[str]]:
    aliases: set[str] = set()
    steps: set[str] = set()
    data_pattern = re.compile(
        r'<script type="application/json" data-nuxt-data="nuxt-app"'
        r"[^>]*>(.*?)</script>",
        flags=re.DOTALL,
    )

    for path in GHL_BASELINE_HTML.glob("theevolvedgym.com.au--*.html"):
        markup = path.read_text(encoding="utf-8")
        match = data_pattern.search(markup)
        if match is None:
            continue
        try:
            values = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue

        def resolve(value: object) -> object:
            if type(value) is int and 0 <= value < len(values):
                return values[value]
            return value

        state = next(
            (
                item
                for item in values
                if isinstance(item, dict) and "funnelNextStep" in item
            ),
            None,
        )
        if state is None:
            continue

        page_url = resolve(state.get("pageUrl"))
        if isinstance(page_url, str):
            aliases.add(page_url)

        step_refs = resolve(state.get("funnelSteps"))
        if not isinstance(step_refs, list):
            continue
        for step_ref in step_refs:
            step = resolve(step_ref)
            if not isinstance(step, dict):
                continue
            step_url = resolve(step.get("url"))
            if isinstance(step_url, str):
                steps.add(step_url)

    return aliases, steps


def check_route_register(audit: Audit) -> None:
    audit.check(
        ROUTE_REGISTER.is_file(),
        "GHL route register exists",
        "GHL route register missing",
    )
    if not ROUTE_REGISTER.is_file():
        return

    try:
        register = json.loads(ROUTE_REGISTER.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        audit.fail(f"cannot parse GHL route register: {exc}")
        return

    group_names = (
        "wordpress_root_paths",
        "root_to_go_redirect_paths",
        "go_only_preserve_paths",
    )
    groups: dict[str, list[str]] = {}
    for name in group_names:
        value = register.get(name)
        if not isinstance(value, list) or not all(
            isinstance(path, str) for path in value
        ):
            audit.fail(f"GHL route register {name} is not a string list")
            return
        groups[name] = value
        audit.check(
            len(value) == len(set(value)),
            f"GHL route register {name} has no duplicates",
            f"GHL route register {name} contains duplicates",
        )

    expected_counts = {
        "wordpress_root_paths": 16,
        "root_to_go_redirect_paths": 19,
        "go_only_preserve_paths": 50,
    }
    for name, expected in expected_counts.items():
        audit.check(
            len(groups[name]) == expected,
            f"GHL route register {name} contains {expected} paths",
            f"GHL route register {name} expected {expected} paths, "
            f"found {len(groups[name])}",
        )

    route_sets = {name: set(value) for name, value in groups.items()}
    category_overlap = (
        route_sets["wordpress_root_paths"]
        & route_sets["root_to_go_redirect_paths"]
    ) | (
        route_sets["wordpress_root_paths"]
        & route_sets["go_only_preserve_paths"]
    ) | (
        route_sets["root_to_go_redirect_paths"]
        & route_sets["go_only_preserve_paths"]
    )
    audit.check(
        not category_overlap,
        "GHL route register disposition groups are disjoint",
        "GHL route register paths appear in multiple disposition groups",
    )

    registered_paths = set().union(*route_sets.values())
    expected_total = register.get("configured_ghl_path_count")
    audit.check(
        expected_total == 85 and len(registered_paths) == expected_total,
        "GHL route register preserves all 85 known paths",
        f"GHL route register expected 85 unique paths, found "
        f"{len(registered_paths)} with declared count {expected_total!r}",
    )

    technical_paths = register.get("wordpress_technical_paths")
    audit.check(
        technical_paths == ["/robots.txt", "/sitemap.xml"],
        "WordPress technical route ownership is registered",
        "WordPress technical route ownership differs from the governed pair",
    )

    critical_paths = {
        "/teen-30dnnc-o",
        "/20s30s-30dnnc-o",
        "/pregnancy-30dnnc-o",
        "/perimenopause-30dnnc-o",
        "/post-menopause-30dnnc-o",
        "/teensa",
        "/2030sa-4923",
        "/pppsa-5667",
        "/pppsa-page-1536",
        "/perimsa-6473",
        "/pmsa",
        "/strength-assessment-confirmed",
    }
    audit.check(
        critical_paths <= registered_paths,
        "homepage and hidden GHL journey paths are protected",
        "one or more critical homepage or hidden GHL paths are unregistered",
    )

    if not GHL_BASELINE_HTML.is_dir():
        audit.pass_(
            "protected GHL baseline is unavailable; route register structure "
            "was still verified"
        )
        return

    aliases, steps = extract_ghl_routes_from_baseline()
    discovered_paths = aliases | steps
    owner_rows = register.get("owner_confirmed_live_paths")
    owner_paths = (
        {
            row.get("path")
            for row in owner_rows
            if isinstance(row, dict) and isinstance(row.get("path"), str)
        }
        if isinstance(owner_rows, list)
        else set()
    )
    audit.check(
        owner_paths == {"/pppsa-page-1536"},
        "owner-confirmed GHL route correction is registered",
        "owner-confirmed GHL route correction is missing or unexpected",
    )
    audit.check(
        len(aliases) == register.get("captured_public_html_alias_count"),
        "GHL public alias count matches the protected baseline",
        f"GHL public alias count drifted: discovered {len(aliases)}",
    )
    audit.check(
        len(steps) == register.get("configured_funnel_step_count"),
        "GHL funnel-step count matches the protected baseline",
        f"GHL funnel-step count drifted: discovered {len(steps)}",
    )
    audit.check(
        discovered_paths | owner_paths == registered_paths,
        "every baseline or owner-confirmed GHL path has a governed disposition",
        "baseline and owner-confirmed GHL paths differ from the governed route register",
    )


def check_local(audit: Audit) -> dict[str, str]:
    audit.check(MANIFEST.is_file(), "V2 manifest exists", "V2 manifest missing")
    if not MANIFEST.is_file():
        return {}

    try:
        manifest = parse_front_matter(MANIFEST)
    except (OSError, ValueError) as exc:
        audit.fail(f"cannot parse V2 manifest: {exc}")
        return {}

    for key, expected in REQUIRED_MANIFEST.items():
        actual = manifest.get(key)
        audit.check(
            actual == expected,
            f"manifest {key} is {expected}",
            f"manifest {key} expected {expected!r}, found {actual!r}",
        )

    audit.check(HASHES.is_file(), "source hash register exists", "source hash register missing")
    if HASHES.is_file():
        rows = [
            line.split("  ", 1)
            for line in HASHES.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        audit.check(len(rows) == 9, "all 9 governed source files are registered", f"expected 9 governed source files, found {len(rows)}")
        registered = {relative_name for _, relative_name in rows}
        discovered = {
            str(path.relative_to(SOURCE))
            for path in (SOURCE / "source").rglob("*")
            if path.is_file()
        }
        audit.check(
            discovered == registered,
            "source mirror has no missing or unregistered files",
            "source mirror file set differs from the hash register",
        )
        for expected_hash, relative_name in rows:
            path = SOURCE / relative_name
            if not path.is_file():
                audit.fail(f"source file missing: {relative_name}")
                continue
            actual_hash = sha256(path)
            audit.check(
                actual_hash == expected_hash,
                f"source hash matches: {relative_name}",
                f"source drift: {relative_name}",
            )

    homepage_path = SOURCE / "source/homepage-post/post-165.html"
    script_path = SOURCE / "source/blocksy-child/js/homepage.js"
    homepage = homepage_path.read_text(encoding="utf-8") if homepage_path.is_file() else ""
    script = script_path.read_text(encoding="utf-8") if script_path.is_file() else ""

    audit.check(
        REQUIRED_MANIFEST["homepage_h1"] in homepage,
        "mirrored homepage contains the governed H1",
        "mirrored homepage H1 differs from the manifest",
    )
    audit.check(
        REQUIRED_MANIFEST["homepage_primary_cta"] in homepage,
        "mirrored homepage contains the waitlist CTA",
        "mirrored homepage is missing the waitlist CTA",
    )
    audit.check(
        "rcUpdateCTALinks" in script and "Join the Waitlist" in script,
        "mirrored homepage script contains the governed waitlist journey",
        "mirrored homepage script does not contain the governed waitlist journey",
    )

    required_pointers = {
        ROOT / "CLAUDE.md": "website-v2-release-manifest.md",
        ROOT / "outputs/systems/website-architecture.md": "website-v2-release-manifest.md",
        ROOT / "outputs/systems/website-sitemap.md": "website-v2-release-manifest.md",
        ROOT / "context/roadmap.md": "Website V2 Root-Domain Promotion",
    }
    for path, marker in required_pointers.items():
        present = path.is_file() and marker in path.read_text(encoding="utf-8")
        audit.check(
            present,
            f"governance pointer present: {path.relative_to(ROOT)}",
            f"governance pointer missing from {path.relative_to(ROOT)}",
        )

    check_route_register(audit)

    return manifest


def normalise_markup(markup: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", html.unescape(without_tags)).strip()


def check_live(audit: Audit, manifest: dict[str, str], timeout: float) -> None:
    runtime_url = manifest.get("runtime_url")
    if not runtime_url:
        audit.fail("manifest runtime_url is unavailable for live check")
        return

    request = urllib.request.Request(
        runtime_url,
        headers={"User-Agent": "Evolved-Website-V2-Read-Only-Audit/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            final_url = response.geturl()
            body = response.read().decode("utf-8", errors="replace")
    except Exception as exc:  # network and TLS failures must be explicit
        audit.fail(f"live homepage could not be read: {exc}")
        return

    plain_text = normalise_markup(body)
    audit.check(status == 200, "live homepage returns HTTP 200", f"live homepage returned HTTP {status}")
    audit.check(
        final_url.rstrip("/") == runtime_url.rstrip("/"),
        "live homepage stayed on the governed runtime URL",
        f"live homepage ended at unexpected URL: {final_url}",
    )
    audit.check(
        manifest["homepage_h1"] in plain_text,
        "live homepage contains the governed H1",
        "live homepage H1 drifted from the manifest",
    )
    audit.check(
        manifest["homepage_primary_cta"] in plain_text,
        "live homepage contains the governed waitlist CTA",
        "live homepage CTA drifted from the manifest",
    )
    expected_asset = rf"homepage\.js\?ver={re.escape(manifest['homepage_js_asset_version'])}"
    asset_match = re.search(
        rf"""<script[^>]+src=["']([^"']*{expected_asset}[^"']*)["']""",
        body,
        flags=re.IGNORECASE,
    )
    audit.check(
        asset_match is not None,
        "live homepage JavaScript asset version matches",
        "live homepage JavaScript asset version drifted from the manifest",
    )
    if asset_match is not None:
        asset_url = urllib.parse.urljoin(runtime_url, html.unescape(asset_match.group(1)))
        asset_request = urllib.request.Request(
            asset_url,
            headers={"User-Agent": "Evolved-Website-V2-Read-Only-Audit/1.0"},
        )
        try:
            with urllib.request.urlopen(asset_request, timeout=timeout) as response:
                asset_status = response.status
                asset_body = response.read()
        except Exception as exc:
            audit.fail(f"live homepage JavaScript could not be read: {exc}")
        else:
            mirror_script = SOURCE / "source/blocksy-child/js/homepage.js"
            audit.check(
                asset_status == 200,
                "live homepage JavaScript returns HTTP 200",
                f"live homepage JavaScript returned HTTP {asset_status}",
            )
            audit.check(
                sha256_bytes(asset_body) == sha256(mirror_script),
                "live homepage JavaScript matches the governed source mirror",
                "live homepage JavaScript differs from the governed source mirror",
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only local and optional live Website V2 drift audit."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="also fetch and verify the public V2 homepage without writing",
    )
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    audit = Audit()
    manifest = check_local(audit)
    if args.live and manifest:
        check_live(audit, manifest, args.timeout)

    if audit.failures:
        print(f"\nWebsite V2 drift audit failed: {len(audit.failures)} issue(s).")
        return 1
    print("\nWebsite V2 drift audit passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
