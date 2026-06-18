# Retriever V2 Evaluation

Date: 2026-06-18
Branch: `retriever-v2-quality-fixes`

## Scope

This evaluation covers the Retriever V2 quality fixes in:

- `backend/app/retriever.py`
- `backend/app/rag.py`
- `backend/app/chat.py`
- `benchmark_chat.py`

The target was to fix the known failures from the previous benchmark:

- B.Tech fee query retrieved conference registration fees.
- Student clubs query retrieved unrelated pages.
- Research centers query missed CESEDM/CESTRD/CCCWR-style center pages.
- Civil Engineering placement query missed the CE placements page.
- HOD Civil Engineering required deterministic extraction.

## Implementation Verified

### `backend/app/retriever.py`

Verified changes:

- Increased Chroma candidate pool to 60 before reranking.
- Added HOD acronym normalization and acronym expansion.
- Added query expansion for fee, research center, student club, and placement intents.
- Added reranking boosts for:
  - fee/admission pages, with conference fee penalties;
  - research center pages, including CESEDM, CESTRD, CCCWR, CEHTI, and center-of-excellence pages;
  - student club pages, including JUIT Youth Club, NSS, NCC, CEC, technical clubs, and IEEE;
  - Civil Engineering placement pages;
  - faculty/HOD pages;
  - committee pages.
- Added deduplication by normalized title/canonical URL.

Direct retrieval checks showed the intended pages ranked in the top results:

| Query | Top verified result |
| --- | --- |
| `Who is the HOD of Civil Engineering?` | `Civil Engineering Faculty` |
| `What is the fee structure for B.Tech?` | `FEE DETAILS 2026-27 ADMISSIONS (INDIAN STUDENTS)` |
| `What student clubs exist at JUIT?` | `JUIT Youth Club`, `Civil Engineering Consortium`, `NCC`, `NSS`, `Technical Club` |
| `What research centers are available?` | `Centre for Structural Engineering and Disaster Management`, `Centre of Sustainable Technologies for Rural development`, `CCCWR About the Centre` |
| `What is the placement record of Civil Engineering?` | `JUIT CE - PLACEMENTS` |

### `backend/app/rag.py`

Verified changes:

- Context construction now clips each retrieved document and caps the total prompt context.
- HOD questions use deterministic regex extraction from the Civil Engineering Faculty context.
- B.Tech fee questions extract the Indian-student B.Tech tuition row and avoid mixing it with NRI/international fee rows.
- Prompt rules were tightened to require concise, context-only answers.
- Generation errors are returned with source metadata instead of raising from the API path.

### `benchmark_chat.py`

Verified behavior:

- Sends the 12-query benchmark set to `http://127.0.0.1:8000/chat`.
- Requires the FastAPI app and local Ollama server to be running.
- Benchmark model used by `backend/app/chat.py`: `qwen3:1.7b`.

## Final Benchmark

Command:

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
python benchmark_chat.py
```

Environment:

- FastAPI server: `http://127.0.0.1:8000`
- Ollama: `http://127.0.0.1:11434`
- Available models: `qwen3:1.7b`, `qwen3:4b`

Result: 12/12 benchmark questions returned usable context-grounded answers.

| # | Question | Result | Notes |
| --- | --- | --- | --- |
| 1 | What is CESEDM? | Pass | Answer describes the structural engineering and disaster management center. |
| 2 | Who is the HOD of Civil Engineering? | Pass | Deterministic answer: `Prof. Dr. Ashish Kumar`. |
| 3 | What is the fee structure for B.Tech? | Pass | Uses Indian-student B.Tech semester tuition fees: Rs. 164550, 164550, 172800, 172800, 181450, 181450, 190550, 190550. |
| 4 | What is the academic calendar? | Pass | Retrieves and summarizes the Academic Calendar page. |
| 5 | What student clubs exist at JUIT? | Pass | Lists JUIT Youth Club, Civil Engineering Consortium, and NCC. Retrieval also includes NSS and Technical Club in top candidates. |
| 6 | What is ICC? | Pass | Retrieves Internal Complaint Committee and answers with its legal basis and chair. |
| 7 | What is CESTRD? | Pass | Describes the rural sustainable technologies center. |
| 8 | What exchange programs are available? | Pass | Answers with international exchange program pages. |
| 9 | What committees exist for student welfare? | Pass | Returns SGRC, ICC, and Student Counselling Committee. |
| 10 | Tell me about the Biotechnology department. | Pass | Summarizes the Biotechnology and Bioinformatics department page. |
| 11 | What research centers are available? | Pass | Returns structural engineering/disaster management, sustainable technologies, and climate/water center content. |
| 12 | What is the placement record of Civil Engineering? | Pass | Answers from Civil Engineering placement/statistics context. |

## Remaining Limitations

- The benchmark is still manually judged from generated answers; it does not yet produce machine-readable pass/fail assertions.
- Some broad list questions return representative examples rather than exhaustive lists because `ask_juit` limits context to the top three retrieved documents.
- The Civil Engineering placement answer mixes the CE placement page with general placement-statistics context. Retrieval is now correct, but a structured placement-table extractor would make this answer more precise.
- The research-center answer generated "Climate and Water Research" in the final run where the source page wording is around climate change and water resources; this is a generation wording issue, not a retrieval miss.

## Conclusion

Retriever V2 resolves the previous benchmark failures at the retrieval layer and produces usable end-to-end chat answers for all 12 benchmark questions. The remaining work is test automation and structured extraction for table-heavy pages, not another reranking pass.
