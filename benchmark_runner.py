import json
from datetime import datetime, timezone
from pathlib import Path

from backend.app.rag import ask_juit


QUESTIONS_PATH = Path("benchmark_questions.json")
REPORT_PATH = Path("benchmark_report.md")


def _contains_all(text, terms):
    normalized = text.lower()
    return [
        term
        for term in terms
        if term.lower() not in normalized
    ]


def _source_text(sources):
    parts = []

    for source in sources:
        parts.append(str(source.get("title", "")))
        parts.append(str(source.get("url", "")))
        parts.append(str(source.get("canonical_url", "")))

    return " ".join(parts)


def _evaluate_case(case):
    result = ask_juit(case["question"])
    answer = result.get("answer", "")
    sources = result.get("sources", [])
    missing_answer_terms = _contains_all(
        answer,
        case.get("required_answer_terms", []),
    )
    missing_source_terms = _contains_all(
        _source_text(sources),
        case.get("required_source_terms", []),
    )

    return {
        "id": case["id"],
        "question": case["question"],
        "answer": answer,
        "sources": sources,
        "missing_answer_terms": missing_answer_terms,
        "missing_source_terms": missing_source_terms,
        "passed": not missing_answer_terms and not missing_source_terms,
    }


def _format_sources(sources):
    formatted = []

    for source in sources[:5]:
        title = source.get("title", "Untitled")
        url = source.get("url", "")
        formatted.append(f"{title} ({url})")

    return "<br>".join(formatted)


def _write_report(results):
    passed = sum(1 for result in results if result["passed"])
    total = len(results)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Benchmark Report",
        "",
        f"Generated: {timestamp}",
        "",
        f"Result: {passed}/{total} passed",
        "",
        "| ID | Status | Question | Missing Terms | Top Sources |",
        "| --- | --- | --- | --- | --- |",
    ]

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        missing = []

        if result["missing_answer_terms"]:
            missing.append(
                "answer: " + ", ".join(result["missing_answer_terms"])
            )

        if result["missing_source_terms"]:
            missing.append(
                "sources: " + ", ".join(result["missing_source_terms"])
            )

        missing_text = "; ".join(missing) if missing else "-"
        lines.append(
            "| {id} | {status} | {question} | {missing} | {sources} |".format(
                id=result["id"],
                status=status,
                question=result["question"],
                missing=missing_text,
                sources=_format_sources(result["sources"]),
            )
        )

    lines.extend(["", "## Answers", ""])

    for result in results:
        lines.extend(
            [
                f"### {result['id']}",
                "",
                f"Question: {result['question']}",
                "",
                result["answer"],
                "",
            ]
        )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    cases = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    results = [_evaluate_case(case) for case in cases]
    _write_report(results)

    passed = sum(1 for result in results if result["passed"])
    total = len(results)

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status} {result['id']}: {result['question']}")

        if result["missing_answer_terms"]:
            print("  missing answer terms:", ", ".join(result["missing_answer_terms"]))

        if result["missing_source_terms"]:
            print("  missing source terms:", ", ".join(result["missing_source_terms"]))

    print(f"\nResult: {passed}/{total} passed")
    print(f"Report written to {REPORT_PATH}")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
