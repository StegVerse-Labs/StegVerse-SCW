#!/usr/bin/env python3
"""
StegVerse PAT Auditor (read-only)

Prints:
- Who the token authenticates as
- Scopes header (if present)
- Can it see orgs StegVerse and StegVerse-Labs?
- Can it list repos in those orgs?
- Does it appear to have workflow read/write?

Safe: does not mutate repos or org state.
"""

import os
import json
import sys
import requests

TOKEN_NAME  = os.getenv("TOKEN_NAME", "UNKNOWN_TOKEN")
TOKEN_VALUE = os.getenv("TOKEN_VALUE", "")

if not TOKEN_VALUE:
    print(f"[{TOKEN_NAME}] No token value provided.")
    sys.exit(0)

BASE = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {TOKEN_VALUE}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "StegVerse-PAT-Auditor"
}

def gh_get(path, **kw):
    return requests.get(BASE + path, headers=HEADERS, timeout=30, **kw)

def summarize_response(r):
    return {
        "status": r.status_code,
        "ok": r.ok,
        "message": (r.json().get("message") if "application/json" in r.headers.get("content-type","") else None),
        "scopes_header": r.headers.get("X-OAuth-Scopes", ""),
        "accepted_scopes_header": r.headers.get("X-Accepted-OAuth-Scopes", ""),
    }

def can_access_org(org):
    r = gh_get(f"/orgs/{org}")
    return r.ok, summarize_response(r)

def list_one_repo(org):
    # Non-mutating: just attempt to list repos (1 item)
    r = gh_get(f"/orgs/{org}/repos", params={"per_page": 1, "type": "all"})
    ok = r.ok
    data = []
    if ok:
        try:
            j = r.json()
            if isinstance(j, list) and j:
                data = [{"name": j[0].get("name"), "private": j[0].get("private")}]
        except Exception:
            pass
    return ok, data, summarize_response(r)

def get_viewer():
    r = gh_get("/user")
    if not r.ok:
        return None, summarize_response(r)
    j = r.json()
    return {
        "login": j.get("login"),
        "id": j.get("id"),
        "type": j.get("type"),
        "name": j.get("name"),
    }, summarize_response(r)

def membership(org):
    r = gh_get(f"/user/memberships/orgs/{org}")
    if not r.ok:
        return None, summarize_response(r)
    j = r.json()
    return {
        "state": j.get("state"),
        "role": j.get("role"),
    }, summarize_response(r)

def main():
    report = {
        "token_name": TOKEN_NAME,
        "viewer": None,
        "viewer_check": None,
        "org_checks": {},
        "repo_visibility": {},
        "workflow_inference": {},
        "notes": []
    }

    viewer, vc = get_viewer()
    report["viewer"] = viewer
    report["viewer_check"] = vc

    scopes = vc.get("scopes_header") or ""
    report["workflow_inference"]["scopes_header"] = scopes
    report["workflow_inference"]["has_workflow_scope_hint"] = ("workflow" in scopes.lower())

    for org in ["StegVerse", "StegVerse-Labs"]:
        ok_org, orgc = can_access_org(org)
        mem, memc = membership(org)
        ok_repo, sample_repo, repoc = list_one_repo(org)

        report["org_checks"][org] = {
            "can_access_org_api": ok_org,
            "org_check": orgc,
            "membership": mem,
            "membership_check": memc,
        }
        report["repo_visibility"][org] = {
            "can_list_repos": ok_repo,
            "sample_repo": sample_repo,
            "repo_check": repoc,
        }

    # Guidance note based on common failures
    if report["org_checks"]["StegVerse-Labs"]["can_access_org_api"] is False:
        report["notes"].append(
            "Token cannot access StegVerse-Labs org API. "
            "If FG PAT: likely created with Owner=StegVerse or personal owner without Labs repos selected."
        )

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
