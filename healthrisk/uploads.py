"""Strict CSV boundary: preserve identifiers and reject malformed row widths."""
import csv
import io
import pandas as pd
from .data import validate_data


def load_csv(payload):
    if len(payload) > 10 * 1024 * 1024:
        return None, ["CSV exceeds the 10 MB limit."]
    try:
        text = payload.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(text), strict=True)
        header = next(reader)
        if len(header) != len(set(header)):
            return None, ["Duplicate column names are not allowed."]
        records = 0
        for row in reader:
            if not row:
                continue
            records += 1
            if len(row) != len(header):
                return None, [f"CSV record {records + 1} has {len(row)} fields; expected {len(header)}."]
            if records > 100000:
                return None, ["Provide between 1 and 100,000 records."]
        parsed = pd.read_csv(io.StringIO(text), dtype={"patient_id": str})
        return validate_data(parsed)
    except (UnicodeDecodeError, ValueError, pd.errors.ParserError, csv.Error, StopIteration) as exc:
        return None, [f"Cannot read CSV: {exc or 'file is empty'}. Use a UTF-8 CSV with a header row."]
