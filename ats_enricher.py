from urllib.parse import urlparse

from text_utils import clean_text, extract_section_by_keywords


def detect_ats(final_url: str) -> str:
    """Detect ATS/platform from the final application URL."""
    url = final_url.lower()

    if "greenhouse.io" in url or "boards.greenhouse" in url:
        return "greenhouse"
    if "lever.co" in url or "jobs.lever" in url:
        return "lever"
    if "ashbyhq.com" in url or "jobs.ashby" in url:
        return "ashby"
    if "workdayjobs.com" in url or "myworkdayjobs.com" in url:
        return "workday"
    if "smartrecruiters.com" in url:
        return "smartrecruiters"
    if "successfactors" in url or "sap" in url:
        return "successfactors"
    if "oraclecloud" in url or "oracle" in url:
        return "oracle"
    if "icims" in url:
        return "icims"

    domain = urlparse(final_url).netloc
    if "glassdoor" in domain:
        return "glassdoor"
    return f"unknown ({domain})" if domain else "unknown"


def looks_like_login_required(page) -> bool:
    """Detect whether the final page appears to require login/auth."""
    try:
        body_text = clean_text(page.locator("body").inner_text(timeout=5000)).lower()
    except Exception:
        return False

    blocker_keywords = [
        "sign in",
        "signin",
        "log in",
        "login",
        "create account",
        "continue with google",
        "single sign-on",
        "sso",
        "verify you are human",
        "checking if the site connection is secure",
        "humans only",
        "cloudflare",
        "attention required",
        "please enable cookies",
        "access denied",
    ]

    return any(keyword in body_text for keyword in blocker_keywords)


def extract_ats_page_details(page) -> dict:
    """Extract richer details from the final ATS/application page."""
    details = {
        "ats_page_title": "",
        "ats_page_location": "",
        "ats_full_description": "",
        "ats_requirements_text": "",
        "ats_responsibilities_text": "",
        "application_fields": [],
        "resume_upload_required": False,
        "cover_letter_field_found": False,
    }

    try:
        details["ats_page_title"] = clean_text(page.locator("h1").first.inner_text(timeout=3000))
    except Exception:
        details["ats_page_title"] = ""

    try:
        body_text = clean_text(page.locator("body").inner_text(timeout=7000))
        details["ats_full_description"] = body_text[:8000]
    except Exception:
        body_text = ""

    requirement_keywords = ["requirements", "qualifications", "what you bring", "what we're looking for", "required skills"]
    responsibility_keywords = ["responsibilities", "what you'll do", "about the role", "role overview", "job description"]

    details["ats_requirements_text"] = extract_section_by_keywords(body_text, requirement_keywords)
    details["ats_responsibilities_text"] = extract_section_by_keywords(body_text, responsibility_keywords)

    try:
        inputs = page.locator("input, textarea, select")
        input_count = inputs.count()

        for i in range(input_count):
            field = inputs.nth(i)
            try:
                tag = field.evaluate("el => el.tagName.toLowerCase()")
                field_type = field.get_attribute("type", timeout=1000) or ""
                name = field.get_attribute("name", timeout=1000) or ""
                field_id = field.get_attribute("id", timeout=1000) or ""
                placeholder = field.get_attribute("placeholder", timeout=1000) or ""
                aria_label = field.get_attribute("aria-label", timeout=1000) or ""

                field_text = clean_text(" ".join([tag, field_type, name, field_id, placeholder, aria_label]))

                if field_text:
                    details["application_fields"].append(field_text)

                if "file" in field_type.lower() or "resume" in field_text.lower() or "cv" in field_text.lower():
                    details["resume_upload_required"] = True

                if "cover" in field_text.lower():
                    details["cover_letter_field_found"] = True
            except Exception:
                pass
    except Exception:
        pass

    return details


def enrich_job_with_ats_details(page, job: dict) -> dict:
    """Open the Glassdoor redirect/ATS URL and enrich the job object with application details."""
    job["final_apply_url"] = ""
    job["ats_platform"] = ""
    job["redirect_success"] = False
    job["auth_required"] = False
    job["ats_page_title"] = ""
    job["ats_full_description"] = ""
    job["ats_requirements_text"] = ""
    job["ats_responsibilities_text"] = ""
    job["application_fields"] = []
    job["resume_upload_required"] = False
    job["cover_letter_field_found"] = False

    ats_url = job.get("ats_url", "")
    if not ats_url:
        return job

    try:
        page.goto(ats_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        job["auth_required"] = looks_like_login_required(page)

        if job["auth_required"]:
            job["redirect_success"] = False
            job["status"] = "blocked_by_glassdoor"
        else:
            job["redirect_success"] = True
            details = extract_ats_page_details(page)
            job.update(details)
    except Exception as error:
        job["redirect_success"] = False
        job["redirect_error"] = str(error)

    return job