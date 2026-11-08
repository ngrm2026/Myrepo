"""Collect public LinkedIn job descriptions for a keyword + location.

Uses LinkedIn's public (logged-out) job pages and stays within their rate
limits: requests are paced, and the run stops cleanly when LinkedIn keeps
rate-limiting it. Progress is saved, so re-running later resumes where it left off.

Steps:
  1. Search  -> jobs_index.json  (LinkedIn shows at most ~1000 results per search)
  2. Details -> data_engineer_jobs_india.csv  (one row per job, full description)

Usage: python scrape_linkedin_jobs.py --keywords "Data Engineer" --location India
"""
import argparse
import csv
import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup

BASE = "https://www.linkedin.com/jobs-guest/jobs/api"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/120 Safari/537.36"}
TITLE_MATCH = re.compile(r"data.*engineer|engineer.*data|\betl\b|big ?data|data ?platform|"
                         r"data ?pipeline|analytics engineer", re.I)
FIELDS = ["job_id", "title", "company", "location", "seniority_level", "employment_type",
          "job_function", "industries", "posted_date", "posted_ago", "applicants",
          "title_matches_keyword", "url", "description"]
DELAY = 2.5  # seconds between requests


class RateLimited(Exception):
    pass


session = requests.Session()
session.headers.update(HEADERS)


def get(url, params=None):
    """Return page HTML, "" when there are no more results, or raise RateLimited."""
    for wait in (30, 60, 120):
        r = session.get(url, params=params, timeout=30)
        if r.status_code == 200:
            return r.text
        if r.status_code in (400, 404):
            return ""
        time.sleep(wait)  # 429 / 999 / 5xx: back off
    raise RateLimited(f"{r.status_code} for {url}")


def text(el):
    return el.get_text(" ", strip=True) if el else ""


def search(keywords, location, index_path):
    jobs = {}
    start = 0
    while start < 1000:
        html = get(f"{BASE}/seeMoreJobPostings/search",
                   {"keywords": keywords, "location": location, "start": start})
        cards = BeautifulSoup(html, "html.parser").select("div.base-card[data-entity-urn]")
        if not cards:
            break
        for c in cards:
            job_id = c["data-entity-urn"].rsplit(":", 1)[-1]
            link = c.select_one("a.base-card__full-link")
            jobs.setdefault(job_id, {
                "job_id": job_id,
                "title": text(c.select_one(".base-search-card__title")),
                "company": text(c.select_one(".base-search-card__subtitle")),
                "location": text(c.select_one(".job-search-card__location")),
                "posted_date": (c.select_one("time") or {}).get("datetime", ""),
                "url": link["href"].split("?")[0] if link else "",
            })
        start += len(cards)
        print(f"search start={start} total {len(jobs)}", flush=True)
        time.sleep(DELAY)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(list(jobs.values()), f, indent=1)
    return list(jobs.values())


def details(job_id):
    soup = BeautifulSoup(get(f"{BASE}/jobPosting/{job_id}"), "html.parser")
    desc = soup.select_one(".show-more-less-html__markup")
    criteria = {text(li.select_one("h3")): text(li.select_one(".description__job-criteria-text"))
                for li in soup.select(".description__job-criteria-item")}
    applicants = soup.select_one(".num-applicants__caption") or soup.select_one(".num-applicants__figure")
    return {
        "seniority_level": criteria.get("Seniority level", ""),
        "employment_type": criteria.get("Employment type", ""),
        "job_function": criteria.get("Job function", ""),
        "industries": criteria.get("Industries", ""),
        "posted_ago": text(soup.select_one(".posted-time-ago__text")),
        "applicants": text(applicants),
        "description": desc.get_text("\n", strip=True) if desc else "",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keywords", default="Data Engineer")
    ap.add_argument("--location", default="India")
    ap.add_argument("--index", default="jobs_index.json")
    ap.add_argument("--out", default="data_engineer_jobs_india.csv")
    args = ap.parse_args()

    try:
        if os.path.exists(args.index):
            jobs = json.load(open(args.index, encoding="utf-8"))
            print(f"loaded {len(jobs)} jobs from {args.index}", flush=True)
        else:
            jobs = search(args.keywords, args.location, args.index)

        done = set()
        if os.path.exists(args.out):
            with open(args.out, encoding="utf-8") as f:
                done = {row["job_id"] for row in csv.DictReader(f) if row["description"]}
        todo = [j for j in jobs if j["job_id"] not in done]
        print(f"details: {len(done)} done, {len(todo)} to fetch", flush=True)

        new_file = not os.path.exists(args.out)
        with open(args.out, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if new_file:
                w.writeheader()
            for i, job in enumerate(todo, 1):
                row = {**job, **details(job["job_id"])}
                row["title_matches_keyword"] = bool(TITLE_MATCH.search(row["title"]))
                if row["description"]:
                    w.writerow(row)
                    f.flush()
                if i % 50 == 0:
                    print(f"details {len(done) + i}/{len(jobs)}", flush=True)
                time.sleep(DELAY)
        print(f"Finished: {args.out}", flush=True)
    except RateLimited as e:
        print(f"Stopped: LinkedIn is rate-limiting ({e}). Re-run later to resume.", flush=True)


if __name__ == "__main__":
    main()
