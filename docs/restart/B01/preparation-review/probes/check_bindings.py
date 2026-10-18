#!/usr/bin/env python3
"""Read-only verification of the exact B01 preparation candidate's Git bindings."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

CANDIDATE = "c82b065f30309c5a8f3db3e81f8addfce7b8ad30"
BASE = "043e64ceb745a323f9a332cc02fae2993388fabe"
CORE = "f2ef70f522af4977e15f81554a8c6eadcdbe8097"
PREFIX = "docs/restart/B01/"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk", required=True, type=Path)
    parser.add_argument("--core", required=True, type=Path)
    parser.add_argument("--hardware", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    repos = {"nSealr/board-sdk": args.sdk, "nSealr/nsealr": args.core,
             "nSealr/hardware": args.hardware}
    prep = {}
    for name in ("brief.md", "source-audit.json", "acceptance-plan.json"):
        data = git(args.sdk, "show", f"{CANDIDATE}:{PREFIX}{name}")
        prep[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    audit = json.loads(git(args.sdk, "show", f"{CANDIDATE}:{PREFIX}source-audit.json"))
    plan = json.loads(git(args.sdk, "show", f"{CANDIDATE}:{PREFIX}acceptance-plan.json"))
    checked = []
    for row in audit["source_bindings"]:
        repo = repos[row["repository"]]
        tree = git(repo, "ls-tree", row["commit"], "--", row["path"]).decode().strip()
        header, path = tree.split("\t", 1)
        mode, kind, blob = header.split()
        data = git(repo, "cat-file", "blob", blob)
        observed = {"mode": mode, "blob": blob, "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest()}
        assert kind == "blob" and path == row["path"]
        assert all(observed[key] == row[key] for key in observed), row["path"]
        checked.append({"repository": row["repository"], "commit": row["commit"],
                        "path": path, **observed, "matches": True})
    assert len(checked) == 25
    graph = json.loads(git(args.core, "show", f"{CORE}:docs/restart/work-items.json"))
    parent = next(task for task in graph["tasks"] if task["id"] == "B01")
    assert parent["acceptance"] == audit["canonical_parent_acceptance"]
    assert parent["acceptance"] == [item["parent_criterion"] for item in plan["acceptance"]]
    assert [item["index"] for item in plan["acceptance"]] == list(range(4))
    baseline = git(args.sdk, "ls-tree", "-r", "--name-only", BASE).decode().splitlines()
    assert sorted(baseline) == [".gitignore", "AGENTS.md", "LICENSE", "README.md"]
    changed = git(args.sdk, "diff", "--name-status", BASE, CANDIDATE).decode().splitlines()
    assert sorted(changed) == sorted("A\t" + PREFIX + name for name in prep)
    subprocess.run(["git", "-C", str(args.sdk), "diff", "--check", BASE, CANDIDATE], check=True)
    result = {"candidate": CANDIDATE, "base": BASE, "requirements": CORE,
              "preparation_files": prep, "source_bindings": checked,
              "parent_acceptance_exact": True, "parent_criterion_count": 4,
              "base_tree": baseline, "candidate_changes": changed,
              "diff_check_exit_code": 0, "python": sys.version.split()[0],
              "git": git(args.sdk, "--version").decode().strip(),
              "scope": "Git integrity only; substantive verdict is in report.md. No hardware/API acceptance."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("25 exact bindings; four unchanged parent criteria; preparation-only diff: PASS")


if __name__ == "__main__":
    main()
