from __future__ import annotations

import io
from typing import Any

REQUIRED_COLUMNS = ("name", "career_url")
OPTIONAL_COLUMNS = ("ats_type", "ats_identifier", "active")


def parse_companies_workbook(data: bytes) -> list[dict[str, Any]]:
    from openpyxl import load_workbook

    workbook = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    sheet = workbook.active
    rows = sheet.iter_rows(values_only=True)
    try:
        header_row = next(rows)
    except StopIteration as exc:
        raise ValueError("Excel file is empty") from exc

    headers = [_normalize_header(cell) for cell in header_row]
    index = {name: idx for idx, name in enumerate(headers) if name}

    missing = [col for col in REQUIRED_COLUMNS if col not in index]
    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
            + ". Expected: name, career_url (optional: ats_type, ats_identifier, active)"
        )

    companies: list[dict[str, Any]] = []
    for row_number, row in enumerate(rows, start=2):
        if row is None or all(cell is None or str(cell).strip() == "" for cell in row):
            continue

        name = _cell(row, index["name"])
        career_url = _cell(row, index["career_url"])
        if not name or not career_url:
            raise ValueError(f"Row {row_number}: name and career_url are required")

        ats_type = "auto"
        if "ats_type" in index:
            ats_type = _cell(row, index["ats_type"]) or "auto"

        ats_identifier = None
        if "ats_identifier" in index:
            ats_identifier = _cell(row, index["ats_identifier"]) or None

        active = True
        if "active" in index:
            active = _as_bool(_cell(row, index["active"]), default=True)

        companies.append(
            {
                "name": name,
                "career_url": career_url,
                "ats_type": ats_type.lower(),
                "ats_identifier": ats_identifier,
                "active": active,
            }
        )

    if not companies:
        raise ValueError("No company rows found in Excel file")
    return companies


def build_template_bytes() -> bytes:
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "companies"
    sheet.append(["name", "career_url", "ats_type", "ats_identifier", "active"])
    sheet.append(
        [
            "Stripe",
            "https://boards.greenhouse.io/stripe",
            "auto",
            "",
            True,
        ]
    )
    sheet.append(
        [
            "Notion",
            "https://jobs.ashbyhq.com/notion",
            "auto",
            "",
            True,
        ]
    )
    sheet.append(
        [
            "Example Company Site",
            "https://example.com/careers",
            "auto",
            "",
            True,
        ]
    )
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _normalize_header(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower().replace(" ", "_")


def _cell(row: tuple[Any, ...], idx: int) -> str:
    if idx >= len(row) or row[idx] is None:
        return ""
    return str(row[idx]).strip()


def _as_bool(value: str, default: bool = True) -> bool:
    if value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "active"}
