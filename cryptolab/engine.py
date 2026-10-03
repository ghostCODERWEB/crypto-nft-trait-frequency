"""Compute collection trait frequencies, inverse-frequency scores and deterministic ranks with missing-trait treatment."""

from .common import (
    number,
    integer,
    identity,
    records,
    chronology,
    allocate,
    result,
    validate_document,
)
from decimal import Decimal


def _analyze(d):
    tokens = records(d["tokens"], "id")
    if not tokens:
        raise ValueError("collection must not be empty")
    traits = set()
    frequency = {}
    for token in tokens:
        if not isinstance(token["traits"], dict):
            raise ValueError("traits object required")
        for k, v in token["traits"].items():
            identity(k)
            identity(v)
            traits.add(k)
    for token in tokens:
        for key in sorted(traits):
            value = token["traits"].get(key)
            frequency[key, value] = frequency.get((key, value), 0) + 1
    rows = []
    for token in tokens:
        breakdown = [
            {
                "trait": key,
                "value": token["traits"].get(key),
                "frequency": frequency[key, token["traits"].get(key)],
                "score": number(len(tokens)) / frequency[key, token["traits"].get(key)],
            }
            for key in sorted(traits)
        ]
        rows.append(
            {
                "id": token["id"],
                "score": sum((r["score"] for r in breakdown), number(0)),
                "breakdown": breakdown,
            }
        )
    rows.sort(key=lambda r: (-r["score"], r["id"]))
    for i, row in enumerate(rows):
        row["rank"] = i + 1
    return result(
        {"tokens": rows, "collection_size": len(tokens), "trait_types": sorted(traits)}
    )


def analyze(document):
    validate_document(document)
    try:
        return result(_analyze(document))
    except (KeyError, TypeError, ArithmeticError, RecursionError) as error:
        raise ValueError("invalid domain input: " + str(error)) from error
