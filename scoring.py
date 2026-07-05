from candidate_profile import TARGET_PROFILE


def is_location_allowed(location: str, profile: dict = TARGET_PROFILE) -> bool:
    """Allow jobs in India or remote jobs."""
    location = location.lower()
    preferred_locations = profile["preferred_locations"]

    if preferred_locations["accept_remote"] and "remote" in location:
        return True

    if preferred_locations["country"] in location:
        return True

    return any(city in location for city in preferred_locations["india_cities"])


def calculate_relevance(job: dict, profile: dict = TARGET_PROFILE) -> dict:
    """Calculate a basic relevance score for a job using keyword matching."""
    title = job.get("title", "").lower()
    location = job.get("location", "").lower()
    description = job.get("description", "").lower()
    searchable_text = f"{title} {location} {description}"

    score = 0
    matched_reasons = []
    negative_matches = []

    for preferred_title in profile["preferred_titles"]:
        if preferred_title in title:
            score += 30
            matched_reasons.append(f"title match: {preferred_title}")

    for skill in profile["preferred_skills"]:
        if skill in searchable_text:
            score += 10
            matched_reasons.append(f"skill match: {skill}")

    if is_location_allowed(location, profile):
        score += 20
        matched_reasons.append("location match: India or Remote")
    else:
        score -= 40
        negative_matches.append("location outside India or not remote")

    for negative_keyword in profile["negative_keywords"]:
        if negative_keyword in searchable_text:
            score -= 25
            negative_matches.append(negative_keyword)

    if not job.get("title"):
        score -= 20
        negative_matches.append("missing title")

    if not job.get("company"):
        score -= 10
        negative_matches.append("missing company")

    if not job.get("ats_url"):
        score -= 10
        negative_matches.append("missing ATS URL")

    score = max(score, 0)

    if score >= 70:
        relevance = "high"
    elif score >= 40:
        relevance = "medium"
    else:
        relevance = "low"

    return {
        "score": score,
        "relevance": relevance,
        "matched_reasons": matched_reasons,
        "negative_matches": negative_matches,
    }