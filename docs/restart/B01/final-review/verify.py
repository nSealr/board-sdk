#!/usr/bin/env python3
"""Read-only exact-source review probe; writes only its requested JSON receipt.

This checks identities and source correspondence, not behavior or prose adequacy.
Manual semantic findings are recorded separately in report.md/review.json.
Network bodies are compared in memory and are never copied into Git.
"""

import argparse
import concurrent.futures
import datetime
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tomllib
import urllib.request


CANDIDATE = "27308eb7eb80bce22f411f9d40da159d901b7087"
BASE = "8377f9264ca0c426dad0d79578c01be2e1d32509"
CORE = "f2ef70f522af4977e15f81554a8c6eadcdbe8097"
PREFIX = "docs/restart/B01/"
OUTPUTS = [PREFIX + name for name in (
    "api-and-dependencies.md", "lifecycle.md", "result.json", "source-register.json"
)]


def digest(body):
    return hashlib.sha256(body).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "nsealr-B01-distinct-source-review/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.status, response.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--integration-root", type=Path, default=Path("/home/tux/nsealr"))
    parser.add_argument("--research-root", type=Path,
                        default=Path("/home/tux/nsealr/.restart-tools/goal/b01-research"))
    parser.add_argument("--refresh-upstream", action="store_true")
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    sdk = Path(__file__).resolve().parents[4]
    assert args.receipt.resolve().parent == Path(__file__).resolve().parent
    roots = {"nSealr/board-sdk": sdk,
             "nSealr/nsealr": args.integration_root / "firmware",
             "nSealr/hardware": args.integration_root / "hardware"}
    read = lambda path: git(sdk, "show", CANDIDATE + ":" + path)
    register = json.loads(read(PREFIX + "source-register.json"))
    result = json.loads(read(PREFIX + "result.json"))
    audit = json.loads(read(PREFIX + "source-audit.json"))
    plan = json.loads(read(PREFIX + "acceptance-plan.json"))
    acceptance = json.loads(read(PREFIX + "preparation-acceptance.json"))
    receipt = {"schema_version": 1, "candidate_commit": CANDIDATE,
               "base_commit": BASE, "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "purpose": "Independent identity/source probe, not SDK behavioral or physical acceptance",
               "python": sys.version.split()[0], "network_refresh": args.refresh_upstream}

    assert git(sdk, "rev-parse", CANDIDATE + "^").decode().strip() == BASE
    delta = git(sdk, "diff", "--name-status", BASE, CANDIDATE).decode().splitlines()
    assert sorted(delta) == sorted("A\t" + path for path in OUTPUTS)
    assert not git(sdk, "diff", CANDIDATE, "--", *OUTPUTS)
    subprocess.run(["git", "-C", str(sdk), "diff", "--check", BASE, CANDIDATE], check=True)
    receipt["candidate_delta"] = delta
    receipt["candidate_bindings"] = [
        {"path": path, "bytes": len(read(path)), "sha256": digest(read(path))} for path in OUTPUTS]
    for row in result["artifact_bindings"]:
        body = read(row["path"])
        assert len(body) == row["bytes"] and digest(body) == row["sha256"]

    graph = json.loads(git(roots["nSealr/nsealr"], "show", CORE + ":docs/restart/work-items.json"))
    criteria = next(row["acceptance"] for row in graph["tasks"] if row["id"] == "B01")
    assert criteria == audit["canonical_parent_acceptance"]
    assert criteria == [row["parent_criterion"] for row in plan["acceptance"]]
    assert criteria == [row["parent_criterion"] for row in result["criteria"]]
    assert len(criteria) == 4 and not result["integration"]["task_complete"]
    assert result["criteria"][2]["status"] == "pending_H04_actual_electrical_pinning"
    receipt["canonical_criteria"] = {"commit": CORE, "count": 4, "byte_exact": True,
                                    "parent_task_complete_claimed": False}

    distinct = acceptance["distinct_review"]
    body = git(sdk, "show", distinct["commit"] + ":" + distinct["path"])
    assert digest(body) == distinct["sha256"]
    report = git(sdk, "show", distinct["commit"] + ":" + distinct["path"].replace("review.json", "report.md"))
    assert digest(report) == distinct["report_sha256"]
    receipt["preparation_review_bindings"] = {"commit": distinct["commit"], "verified": True}

    bindings = register["source_bindings"]
    assert len(bindings) == 36
    assert len({(r["repository"], r["commit"], r["path"]) for r in bindings}) == 36
    for row in bindings + audit["source_bindings"]:
        root = roots[row["repository"]]
        entry = git(root, "ls-tree", row["commit"], "--", row["path"]).decode().strip()
        mode, kind, blobpath = entry.split(" ", 2)
        blob, path = blobpath.split("\t", 1)
        body = git(root, "show", row["commit"] + ":" + row["path"])
        assert (mode, kind, blob, path) == (row["mode"], "blob", row["blob"], row["path"])
        assert len(body) == row["bytes"] and digest(body) == row["sha256"]
    receipt["git_bindings"] = {"register_verified": 36, "preparation_audit_verified": len(audit["source_bindings"]),
                               "mode_blob_path_bytes_sha256": True}

    members = {}
    package_receipts = []
    requests = []
    for package in register["packages"]:
        crate, version = package["crate"], package["version"]
        archive = (args.research_root / f"{crate}-{version}.crate").read_bytes()
        assert digest(archive) == package["archive_sha256"] and len(archive) == package["archive_bytes"]
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
            files = {m.name.split("/", 1)[1]: tar.extractfile(m).read() for m in tar.getmembers()
                     if m.isfile()}
        members[crate] = files
        extracted_verified = 0
        for row in package["source_files"]:
            body = files[row["path"]]
            assert digest(body) == row["sha256"] and len(body) == row["bytes"]
            extracted = args.research_root / crate / row["path"]
            if extracted.exists():
                assert extracted.read_bytes() == body
                extracted_verified += 1
        manifest = tomllib.loads(files["Cargo.toml"].decode())
        for field in ("license", "rust_version", "repository"):
            assert package[field] == manifest["package"].get(field.replace("_", "-"))
        assert manifest.get("features", {}) == package["manifest_features"]
        assert manifest.get("dependencies", {}) == package["manifest_dependencies"]
        assert json.loads(files[".cargo_vcs_info.json"]) == package["vcs"]
        metadata_name = f"{crate}-{version}-metadata.json" if crate == "embedded-graphics-core" else f"{crate}-metadata.json"
        metadata_body = (args.research_root / metadata_name).read_bytes()
        assert digest(metadata_body) == package["registry_metadata"]["metadata_sha256"]
        metadata = json.loads(metadata_body)
        versions = metadata.get("versions", [metadata.get("version")])
        published = next(row for row in versions if row["num"] == version)
        assert published["checksum"] == package["archive_sha256"]
        assert published["repository"] == package["repository"]
        assert published["license"] == package["license"]
        licenses = sorted(path for path in files if path.startswith("LICENSE"))
        if crate == "embedded-graphics-core":
            assert not licenses
            for row in package["upstream_license_files"]:
                body = (args.research_root / crate / row["path"]).read_bytes()
                assert len(body) == row["bytes"] and digest(body) == row["sha256"]
                blob = hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()
                assert blob == row["git_blob"]
                requests.append(("upstream_license", row["url"], row["sha256"], row["bytes"], body))
        else:
            assert licenses == ["LICENSE-APACHE", "LICENSE-MIT"]
        assert package["adoption"] == "surveyed_only_not_selected"
        package_receipts.append({"crate": crate, "version": version, "archive_sha256": digest(archive),
                                 "inspected_members_verified": len(package["source_files"]),
                                 "existing_extracted_members_equal_archive": extracted_verified,
                                 "license_body_members": licenses,
                                 "manifest_features_dependencies_license_repository_vcs_equal": True,
                                 "exact_registry_version_checksum_equal": True})
        requests.append(("archive", package["archive_url"], package["archive_sha256"], package["archive_bytes"], archive))
    assert len(package_receipts) == 6
    receipt["packages"] = package_receipts
    for row in register["official_upstream_byte_correspondence"]:
        body = members[row["crate"]][row["path"]]
        assert digest(body) == row["sha256"] and len(body) == row["bytes"]
        requests.append(("upstream_source", row["url"], row["sha256"], row["bytes"], body))
    assert len(register["official_upstream_byte_correspondence"]) == 10
    correction = register["rand_core_origin_correction"]
    rand_metadata = json.loads((args.research_root / "rand_core-metadata.json").read_bytes())
    assert rand_metadata["crate"]["repository"] == correction["crate_level_repository_metadata"]
    rand_version = next(row for row in rand_metadata["versions"] if row["num"] == "0.10.1")
    assert rand_version["repository"] == correction["version_level_repository_metadata"]
    assert correction["upstream_correspondence"] == json.loads(
        (args.research_root / "version-source-correspondence.json").read_bytes())["upstream_correspondence"]
    observed_failures = json.loads((args.research_root / "preparation-observations.json").read_bytes())["upstream_correspondence"]
    assert register["retrieval_failures_preserved"] == [r for r in observed_failures if r["status"] == 404]
    receipt["origin_correction"] = {"stale_crate_level_origin": correction["crate_level_repository_metadata"],
                                    "exact_version_origin": rand_version["repository"],
                                    "preserved_historical_404_records": 2}

    if args.refresh_upstream:
        def verify_url(item):
            kind, url, expected_hash, expected_length, expected_body = item
            status, body = get(url)
            assert status == 200 and len(body) == expected_length
            assert body == expected_body and digest(body) == expected_hash
            return {"kind": kind, "url": url, "status": status, "bytes": len(body),
                    "sha256": digest(body), "byte_exact": True}
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            receipt["fresh_official_bodies"] = list(pool.map(verify_url, requests))
    else:
        receipt["fresh_official_bodies"] = "not requested; local pinned archive correspondence only"
    receipt["not_performed"] = ["No dependency installation/compile/execution or SDK test suite",
                                 "No hardware, cryptographic protocol certification or physical erasure proof"]
    receipt["result"] = "PASS_identity_source_correspondence_only"
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(args.receipt), "result": receipt["result"],
                      "register_bindings": 36, "archives": 6, "upstream_source_bodies": 10,
                      "upstream_license_bodies": 2, "fresh_official_responses": len(requests) if args.refresh_upstream else 0}))


if __name__ == "__main__":
    main()
