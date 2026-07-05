import time

from playwright.sync_api import sync_playwright, Playwright

from config import GLASSDOOR_URL
from glassdoor_extractor import extract_jobs
from ats_enricher import enrich_job_with_ats_details
from csv_exporter import export_jobs_to_csv


def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()

    page.goto(GLASSDOOR_URL, wait_until="domcontentloaded", timeout=60000)

    # Avoid networkidle on modern sites like Glassdoor because background requests can keep running.
    page.wait_for_timeout(5000)

    jobs = extract_jobs(page, limit=5)
    jobs = sorted(jobs, key=lambda job: job["match"]["score"], reverse=True)

    for job in jobs:
        print(f"\nEnriching ATS details for: {job['title']} | {job['company']}")
        enrich_job_with_ats_details(page, job)

    export_jobs_to_csv(jobs)

    print("\nMost relevant jobs:")
    for index, job in enumerate(jobs, start=1):
        print(f"\nJob {index}")
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"Opening date: {job['opening_date']}")
        print(f"Salary: {job['salary']}")
        print(f"Description: {job['description']}")
        print(f"Glassdoor URL: {job['glassdoor_url']}")
        print(f"ATS URL: {job['ats_url']}")
        print(f"Final apply URL: {job.get('final_apply_url', '')}")
        print(f"ATS platform: {job.get('ats_platform', '')}")
        print(f"Redirect success: {job.get('redirect_success', '')}")
        print(f"Auth required: {job.get('auth_required', '')}")
        print(f"Resume upload required: {job.get('resume_upload_required', '')}")
        print(f"Cover letter field found: {job.get('cover_letter_field_found', '')}")
        print(f"Relevance score: {job['match']['score']}")
        print(f"Relevance: {job['match']['relevance']}")
        print(f"Matched reasons: {job['match']['matched_reasons']}")
        print(f"Negative matches: {job['match']['negative_matches']}")

    page.wait_for_timeout(10000)
    browser.close()


with sync_playwright() as playwright:
    start_time = time.perf_counter()
    run(playwright)
    end_time = time.perf_counter()
    run_time = end_time - start_time
    print(f"\nRun time: {run_time:.2f} seconds")