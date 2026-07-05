from urllib.parse import urljoin

from config import BASE_URL
from scoring import calculate_relevance
from text_utils import clean_text


def extract_jobs(page, limit: int = 5):
    """Extract structured job data from visible Glassdoor job cards."""
    jobs = []

    job_cards = page.locator('[data-test="job-card-wrapper"]')
    card_count = job_cards.count()
    print(f"Found {card_count} job cards")

    for i in range(min(card_count, limit)):
        card = job_cards.nth(i)

        try:
            title = clean_text(card.locator('[data-test="job-title"]').first.inner_text(timeout=3000))
        except Exception:
            title = ""

        try:
            company = clean_text(card.locator('.EmployerProfile_compactEmployerName__9MGcV').first.inner_text(timeout=3000))
        except Exception:
            company = ""

        try:
            location = clean_text(card.locator('[data-test="emp-location"]').first.inner_text(timeout=3000))
        except Exception:
            location = ""

        try:
            opening_date = clean_text(card.locator('[data-test="job-age"]').first.inner_text(timeout=3000))
        except Exception:
            opening_date = ""

        try:
            salary = clean_text(card.locator('[id^="job-salary-"]').first.inner_text(timeout=3000))
        except Exception:
            salary = ""

        try:
            description = clean_text(card.locator('[data-test="descSnippet"]').first.inner_text(timeout=3000))
        except Exception:
            description = ""

        try:
            glassdoor_href = card.locator('[data-test="job-title"]').first.get_attribute("href", timeout=3000)
            glassdoor_url = urljoin(BASE_URL, glassdoor_href) if glassdoor_href else ""
        except Exception:
            glassdoor_url = ""

        try:
            ats_href = card.locator('[data-test="job-link"]').first.get_attribute("href", timeout=3000)
            ats_url = urljoin(BASE_URL, ats_href) if ats_href else ""
        except Exception:
            ats_url = ""

        job = {
            "title": title,
            "company": company,
            "location": location,
            "opening_date": opening_date,
            "salary": salary,
            "description": description,
            "glassdoor_url": glassdoor_url,
            "ats_url": ats_url,
            "status": "pending",
        }

        job["match"] = calculate_relevance(job)
        jobs.append(job)

    return jobs