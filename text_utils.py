def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.split())


def extract_section_by_keywords(text: str, keywords: list[str], max_chars: int = 2000) -> str:
    """Extract a rough text section starting from the first matching keyword."""
    lowered_text = text.lower()

    for keyword in keywords:
        index = lowered_text.find(keyword)
        if index != -1:
            return clean_text(text[index:index + max_chars])

    return ""