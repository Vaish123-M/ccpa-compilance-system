import json
import re

from pydantic import BaseModel, ConfigDict, ValidationError


SECTION_PATTERN = re.compile(r"Section\s+1798\.\d{3}(?:\.\d+)?", re.IGNORECASE)


class OutputSchema(BaseModel):
    harmful: bool
    articles: list[str]
    model_config = ConfigDict(extra="forbid")


def safe_output() -> dict:
    return {"harmful": False, "articles": []}


def extract_allowed_sections(retrieved_sections: list[dict[str, str]]) -> set[str]:
    output: set[str] = set()
    for item in retrieved_sections:
        section = item.get("section", "").strip()
        if section:
            output.add(section)
    return output


def build_llm_prompt(user_prompt: str, retrieved_sections: list[dict[str, str]]) -> str:
    law_blocks = []
    for item in retrieved_sections:
        law_blocks.append(f"{item['section']}:\n{item['text']}")
    laws = "\n\n".join(law_blocks)

    return (
        "You are a legal compliance AI.\n"
        "Based only on the provided CCPA sections, determine if the business practice violates the law.\n\n"
        "If it violates:\n"
        "Return:\n"
        '{"harmful": true, "articles": ["Section ..."]}\n\n'
        "If it does not violate:\n"
        "Return:\n"
        '{"harmful": false, "articles": []}\n\n'
        "Rules:\n"
        "- Return ONLY valid JSON.\n"
        "- Select article values only from the sections shown in Relevant Law.\n"
        "- Do not include any explanation.\n\n"
        f"Business Practice:\n{user_prompt}\n\n"
        f"Relevant Law:\n{laws}"
    )


def _extract_json_block(text: str) -> str | None:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            payload, end_index = decoder.raw_decode(text[index:])
            if isinstance(payload, dict):
                return text[index : index + end_index]
        except json.JSONDecodeError:
            continue
    return None


def _normalize_section(article: str) -> str | None:
    match = SECTION_PATTERN.search(article)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(0)).strip()


def validate_and_normalize_output(raw_output: str, allowed_sections: set[str]) -> dict:
    json_block = _extract_json_block(raw_output)
    if json_block is None:
        return safe_output()

    try:
        parsed = json.loads(json_block)
    except json.JSONDecodeError:
        return safe_output()

    try:
        structured = OutputSchema.model_validate(parsed)
    except ValidationError:
        return safe_output()

    harmful = structured.harmful
    articles = structured.articles

    normalized_articles: list[str] = []
    for item in articles:
        normalized = _normalize_section(item)
        if normalized is None:
            continue
        if normalized in allowed_sections and normalized not in normalized_articles:
            normalized_articles.append(normalized)

    if harmful:
        if not normalized_articles:
            return safe_output()
        return {"harmful": True, "articles": normalized_articles}

    return {"harmful": False, "articles": []}
