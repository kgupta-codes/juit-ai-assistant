import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from backend.app.rag import ask_juit


QUESTIONS_PATH = Path("benchmark_questions_v2.json")
REPORT_PATH = Path("benchmark_report_v2.md")


def _source_text(sources):
    parts = []

    for source in sources:
        parts.append(str(source.get("title", "")))
        parts.append(str(source.get("url", "")))
        parts.append(str(source.get("canonical_url", "")))

    return " ".join(parts)


def _contains_error(answer):
    normalized = answer.lower()
    return (
        "error generating answer" in normalized
        or "could not reach" in normalized
        or "traceback" in normalized
    )


def _evaluate_case(case):
    result = ask_juit(case["question"])
    answer = result.get("answer", "").strip()
    sources = result.get("sources", [])
    source_text = _source_text(sources)
    status = "answered"

    if not answer or _contains_error(answer):
        status = "error"
    elif not sources:
        status = "no_sources"

    return {
        "id": case["id"],
        "category": case["category"],
        "question": case["question"],
        "answer": answer,
        "sources": sources,
        "source_text": source_text,
        "status": status,
    }


def _format_sources(sources):
    if not sources:
        return "-"

    formatted = []

    for source in sources[:5]:
        title = source.get("title", "Untitled")
        url = source.get("url") or source.get("canonical_url", "")
        formatted.append(f"{title} ({url})")

    return "<br>".join(formatted)


def _write_report(results):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    status_counts = Counter(result["status"] for result in results)
    category_counts = Counter(result["category"] for result in results)
    lines = [
        "# Benchmark V2 Report",
        "",
        f"Generated: {timestamp}",
        "",
        "This is an exploratory 100-question coverage benchmark. It does not replace the stable 12-question benchmark.",
        "",
        "## Summary",
        "",
        f"- Total questions: {len(results)}",
        f"- Answered with sources: {status_counts['answered']}",
        f"- No sources: {status_counts['no_sources']}",
        f"- Errors: {status_counts['error']}",
        "",
        "## Category Coverage",
        "",
    ]

    for category, count in sorted(category_counts.items()):
        lines.append(f"- {category}: {count}")

    lines.extend(
        [
            "",
            "## Results",
            "",
            "| ID | Category | Status | Question | Top Sources |",
            "| --- | --- | --- | --- | --- |",
        ]
    )

    for result in results:
        lines.append(
            "| {id} | {category} | {status} | {question} | {sources} |".format(
                id=result["id"],
                category=result["category"],
                status=result["status"].upper(),
                question=result["question"],
                sources=_format_sources(result["sources"]),
            )
        )

    lines.extend(["", "## Answers", ""])

    for result in results:
        lines.extend(
            [
                f"### {result['id']} - {result['category']}",
                "",
                f"Question: {result['question']}",
                "",
                result["answer"] or "_No answer returned._",
                "",
            ]
        )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Run the exploratory 100-question JUIT AI Assistant benchmark."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Run only the first N questions for a quick smoke test.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any question returns an error or no sources.",
    )
    args = parser.parse_args()

    cases = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))

    if args.limit is not None:
        cases = cases[: args.limit]

    results = []

    for index, case in enumerate(cases, start=1):
        print(f"[{index}/{len(cases)}] {case['id']}: {case['question']}")
        result = _evaluate_case(case)
        results.append(result)
        print(f"  {result['status'].upper()}")

    _write_report(results)

    status_counts = Counter(result["status"] for result in results)
    print("")
    print(f"Answered with sources: {status_counts['answered']}/{len(results)}")
    print(f"No sources: {status_counts['no_sources']}")
    print(f"Errors: {status_counts['error']}")
    print(f"Report written to {REPORT_PATH}")

    if args.strict and (
        status_counts["error"] > 0 or status_counts["no_sources"] > 0
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
