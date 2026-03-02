import re


RULES: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"(sell|selling).*(data|personal information).*(without|no).*(notice|opt[- ]?out)|"
            r"(without|no).*(notice|opt[- ]?out).*(sell|selling).*(data|personal information)",
            re.IGNORECASE,
        ),
        "Section 1798.120",
    ),
    (
        re.compile(
            r"ignore.*deletion request|refus(e|ing).*(delete|deletion)|do not.*(delete|deletion)",
            re.IGNORECASE,
        ),
        "Section 1798.105",
    ),
    (
        re.compile(
            r"discriminat(e|ion|ory).*(price|pricing|service)|different.*pricing.*privacy",
            re.IGNORECASE,
        ),
        "Section 1798.125",
    ),
    (
        re.compile(
            r"no privacy notice|without privacy notice|missing privacy notice",
            re.IGNORECASE,
        ),
        "Section 1798.100",
    ),
    (
        re.compile(
            r"share.*(personal information|consumer data).*(without|no).*(opt[- ]?out|notice)|"
            r"without|no.*(opt[- ]?out|notice).*(share|sharing).*(personal information|consumer data)",
            re.IGNORECASE,
        ),
        "Section 1798.120",
    ),
    (
        re.compile(
            r"den(y|ied|ying).*(access request|right to know)|ignore.*(access request|right to know)",
            re.IGNORECASE,
        ),
        "Section 1798.110",
    ),
]


def detect_high_confidence_violation(prompt: str) -> dict[str, object] | None:
    normalized_prompt = prompt.strip()
    if not normalized_prompt:
        return None

    matched_sections: list[str] = []

    for pattern, section in RULES:
        if pattern.search(normalized_prompt):
            if section not in matched_sections:
                matched_sections.append(section)

    if matched_sections:
        return {"harmful": True, "articles": matched_sections}

    return None
