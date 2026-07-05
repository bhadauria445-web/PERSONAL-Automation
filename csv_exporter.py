import csv

from config import CSV_FILE_NAME


def export_jobs_to_csv(jobs: list[dict], file_name: str = CSV_FILE_NAME) -> None:
    """Export extracted jobs to a CSV file that can be opened in Google Sheets."""
    fieldnames = [
        "title",
        "company",
        "location",
        "opening_date",
        "salary",
        "description",
        "glassdoor_url",
        "ats_url",
        "final_apply_url",
        "ats_platform",
        "redirect_success",
        "auth_required",
        "ats_page_title",
        "ats_full_description",
        "ats_requirements_text",
        "ats_responsibilities_text",
        "application_fields",
        "resume_upload_required",
        "cover_letter_field_found",
        "relevance_score",
        "relevance",
        "matched_reasons",
        "negative_matches",
        "status",
        "audit_decision",
        "audit_notes",
    ]

    with open(file_name, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for job in jobs:
            match = job.get("match", {})
            writer.writerow(
                {
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "location": job.get("location", ""),
                    "opening_date": job.get("opening_date", ""),
                    "salary": job.get("salary", ""),
                    "description": job.get("description", ""),
                    "glassdoor_url": job.get("glassdoor_url", ""),
                    "ats_url": job.get("ats_url", ""),
                    "final_apply_url": job.get("final_apply_url", ""),
                    "ats_platform": job.get("ats_platform", ""),
                    "redirect_success": job.get("redirect_success", ""),
                    "auth_required": job.get("auth_required", ""),
                    "ats_page_title": job.get("ats_page_title", ""),
                    "ats_full_description": job.get("ats_full_description", ""),
                    "ats_requirements_text": job.get("ats_requirements_text", ""),
                    "ats_responsibilities_text": job.get("ats_responsibilities_text", ""),
                    "application_fields": "; ".join(job.get("application_fields", [])),
                    "resume_upload_required": job.get("resume_upload_required", ""),
                    "cover_letter_field_found": job.get("cover_letter_field_found", ""),
                    "relevance_score": match.get("score", ""),
                    "relevance": match.get("relevance", ""),
                    "matched_reasons": "; ".join(match.get("matched_reasons", [])),
                    "negative_matches": "; ".join(match.get("negative_matches", [])),
                    "status": job.get("status", ""),
                    "audit_decision": "",
                    "audit_notes": "",
                }
            )

    print(f"\nSaved audit file: {file_name}")