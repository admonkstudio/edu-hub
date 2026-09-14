#!/usr/bin/env python3
from __future__ import annotations

from plan_identity_reconciliation import similarity


def row(name: str, *, official_identifier: str | None = None, domain: str | None = None) -> dict:
    return {
        "name_en": name,
        "official_identifier": official_identifier,
        "normalized_domain": domain,
    }


def main() -> int:
    # Same school, punctuation-only name difference: strong review proposal.
    score, evidence = similarity(
        row("British International School, Cairo"),
        row("British International School - Cairo"),
    )
    assert score >= 0.99
    assert evidence["exact_normalized_name"] is True

    # Distinctive proper-name overlap survives generic curriculum words.
    score, evidence = similarity(
        row("El Alsson American International School"),
        row("El Alsson British & American International School"),
    )
    assert score >= 0.58
    assert "alsson" in evidence["shared_distinctive_tokens"]

    # Generic model words alone must not create a duplicate proposal.
    score, evidence = similarity(
        row("British International School, Cairo"),
        row("Egypt British International School"),
    )
    assert score == 0
    assert evidence["generic_only_rejected"] is True

    score, evidence = similarity(
        row("Modern English School Cairo"),
        row("Gulf English School Cairo"),
    )
    assert score == 0
    assert evidence["generic_only_rejected"] is True

    # Exact official ID/domain remain strong even when names differ.
    score, evidence = similarity(
        row("Example School", official_identifier="ABC-1"),
        row("Example Academy", official_identifier="ABC-1"),
    )
    assert score >= 0.99
    assert evidence["exact_official_identifier"] is True

    score, evidence = similarity(
        row("Example School", domain="example.edu.eg"),
        row("Example Learning Campus", domain="example.edu.eg"),
    )
    assert score >= 0.96
    assert evidence["same_normalized_domain"] is True

    print("identity reconciliation v2 tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
