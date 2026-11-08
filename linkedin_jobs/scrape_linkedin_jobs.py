"""Collect public LinkedIn job descriptions for a keyword + location.

Uses LinkedIn's public (logged-out) job pages. Each search returns at most a
few hundred results, so the search is split by experience level and workplace
type, then de-duplicated by job ID.

Usage: python scrape_linkedin_jobs.py --keywords "Data Engineer" --location India
"""
import argparse
import csv
import re
import time

import requests
from bs4 import BeautifulSoup

BASE = "https://www.linkedin.com/jobs-guest/jobs/api"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/120 Safari/537.36"}
EXPERIENCE = {"1": "Internship", "2": "Entry level", "3": "Associate",
              "4": "Mid-Senior level", "5": "Director", "6": "Executive"}
WORKPLACE = {"1": "On-site", "2": "Remote", "3": "Hybrid"}
TITLE_MATCH = re.compile(r"data.*engineer|engineer.*data|\betl\b|big ?data|data ?platform|"
                         r"data ?pipeline|analytics engineer", re.I)

session = requests.Session()
session.headers.update(HEADERS)


def get(url, params=None, tries=5):
    for i in range(tries):
        try:
            r = session.get(url, params=params, timeout=30)
            if r.status_code == 200:
                return r.text
            if r.status_code == 400:  # past the last page
                return ""
            if r.status_code in (429, 999) or r.status_code >= 500:
                time.sleep(5 * (i + 1))
                continue
            return ""
        except requests.RequestException:
            time.sleep(3 * (i + 1))
    return ""


def text(el):
    return el.get_text(" ", strip=True) if el else ""


def search(keywords, location, extra):
    """Yield search cards for one filter combination until results run out."""
    start = 0
    while start < 1000:
        html = get(f"{BASE}/seeMoreJobPostings/search",
                   {"keywords": keywords, "location": location, "start": start, **extra})
        cards = BeautifulSoup(html, "html.parser").select("div.base-card[data-entity-urn]") if html else []
        if not cards:
            break
        for c in cards:
            link = c.select_one("a.base-card__full-link")
            yield {
                "job_id": c["data-entity-urn"].rsplit(":", 1)[-1],
                "title": text(c.select_one(".base-search-card__title")),
                "company": text(c.select_one(".base-search-card__subtitle")),
                "location": text(c.select_one(".job-search-card__location")),
                "posted_date": (c.select_one("time") or {}).get("datetime", ""),
                "url": link["href"].split("?")[0] if link else "",
            }
        start += len(cards)
        time.sleep(1)


def details(job_id):
    soup = BeautifulSoup(get(f"{BASE}/jobPosting/{job_id}"), "html.parser")
    desc = soup.select_one(".show-more-less-html__markup")
    criteria = {}
    for li in soup.select(".description__job-criteria-item"):
        criteria[text(li.select_one("h3"))] = text(li.select_one(".description__job-criteria-text"))
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
    ap.add_argument("--out", default="data_engineer_jobs_india.csv")
    args = ap.parse_args()

    jobs = {}
    for e, e_name in EXPERIENCE.items():
        for w, w_name in WORKPLACE.items():
            n = 0
            for card in search(args.keywords, args.location, {"f_E": e, "f_WT": w}):
                if card["job_id"] not in jobs:
                    jobs[card["job_id"]] = {**card, "experience_filter": e_name, "workplace_type": w_name}
                    n += 1
            print(f"{e_name:17} {w_name:8} +{n:4}  total {len(jobs)}", flush=True)

    fields = ["job_id", "title", "company", "location", "workplace_type", "experience_filter",
              "seniority_level", "employment_type", "job_function", "industries", "posted_date",
              "posted_ago", "applicants", "title_matches_keyword", "url", "description"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, job in enumerate(jobs.values(), 1):
            job.update(details(job["job_id"]))
            job["title_matches_keyword"] = bool(TITLE_MATCH.search(job["title"]))
            w.writerow(job)
            if i % 50 == 0:
                print(f"details {i}/{len(jobs)}", flush=True)
                f.flush()
            time.sleep(0.7)
    print(f"Wrote {len(jobs)} jobs to {args.out}")


if __name__ == "__main__":
    main()
