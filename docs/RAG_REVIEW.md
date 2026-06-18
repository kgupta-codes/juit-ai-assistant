 Review backend/app/rag.py only.

  Do NOT modify code.

  Analyze:

  1. Context construction
  2. Prompt quality
  3. Hallucination prevention
  4. Source handling
  5. Failure modes

  Provide:

  - Problems
  - Root causes
  - Priority order
  - Estimated impact

  Reference exact code lines where possible.

  No code changes.


• I’ll inspect backend/app/rag.py with line numbers and keep the
  review scoped to that file only.

• Explored
  └ Read rag.py

──────────────────────────────────────────────────────────────────────

• Problems

  1. P0: No guard for empty or malformed retrieval results.
     backend/app/rag.py:9 and backend/app/rag.py:10 assume
     results["documents"][0] and results["metadatas"][0] always exist.
     If search returns no nested list, None, or an error-shaped
     response, ask_juit() crashes before producing the fallback
     answer.
     Root cause: retrieval output is trusted without validation.
     Estimated impact: High. Prevents chat endpoint failures on empty
     indexes, bad queries, or retriever errors.

  2. P0: Context construction has no source boundaries.
     context = "\n\n".join(documents) at backend/app/rag.py:12 merges
     chunks into one plain blob. The model cannot tell which text came
     from which page, title, URL, or chunk.
     Root cause: documents and metadata are separated before
     prompting.
     Estimated impact: High. Weakens citation accuracy, makes
     contradictory chunks harder to resolve, and increases
     hallucination risk.

  3. P1: Prompt asks for grounded answers but does not require
     evidence discipline.
     The prompt says “Answer ONLY using the provided context” at
     backend/app/rag.py:17 and “Do not use outside knowledge” at
     backend/app/rag.py:23, but it does not instruct the model to
     quote or identify supporting source chunks, avoid unsupported
     synthesis, or handle conflicting context.
     Root cause: hallucination prevention is policy-like, not
     structurally enforced.
     Estimated impact: Medium-High. Better prompt constraints would
     reduce confident but unsupported answers.

  4. P1: User question is interpolated directly into the prompt.
     {question} is inserted at backend/app/rag.py:31 without
     delimiters or prompt-injection handling. A user can include
     instructions such as “ignore the context” inside the question.
     Root cause: no clear data/instruction separation.
     Estimated impact: Medium-High. Improves resistance to prompt
     injection and instruction confusion.

  5. P1: Source handling returns all retrieved sources, not
     necessarily used sources.
     The function returns sources directly at backend/app/rag.py:40.
     There is no link between the generated answer at backend/app/
     rag.py:36 and which sources actually supported it.
     Root cause: source attribution is pass-through metadata, not
     answer-grounded citation.
     Estimated impact: Medium. Users may see irrelevant or misleading
     sources.

  6. P2: No context budget management.
     The code always requests 3 results at backend/app/rag.py:7 and
     joins full documents at backend/app/rag.py:12. There is no token
     budgeting, truncation, deduplication, or ranking threshold.
     Root cause: context assembly assumes retrieved chunks are always
     small, relevant, and safe to include whole.
     Estimated impact: Medium. Can degrade answer quality and may hit
     model context limits as chunks grow.

  7. P2: LLM failure is not handled.
     generate_answer(prompt) at backend/app/rag.py:36 is unguarded.
     API failures, timeouts, empty responses, or malformed responses
     bubble up.
     Root cause: no exception boundary around generation.
     Estimated impact: Medium. Improves reliability and allows
     graceful user-facing errors.

  8. P3: The five-sentence cap may suppress complete answers.
     The rule at backend/app/rag.py:20 is simple, but for multi-part
     JUIT queries it can force omission even when the context contains
     the answer.
     Root cause: fixed response limit regardless of question type.
     Estimated impact: Low-Medium. Better answer completeness for
     complex questions.

  Priority Order

  1. Validate retrieval output and handle empty results before
     indexing.

  2. Construct context with explicit source/chunk boundaries.
  3. Strengthen prompt grounding and injection resistance.
  4. Return sources tied to used evidence, not just retrieved
     metadata.

  5. Add generation error handling.
  6. Add context budget, deduplication, and relevance thresholds.
  7. Reconsider fixed five-sentence limit.

  No code changes were made.
