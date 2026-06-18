Review backend/app/main.py only.

  Do NOT modify code.

  Analyze:

  1. API design
  2. Endpoint structure
  3. Error handling
  4. Validation
  5. Scalability concerns

  Provide:

  - Problems
  - Root causes
  - Priority order

  Reference exact code lines where possible.
  └ Read main.py

──────────────────────────────────────────────────────────────────────

• Problems

  1. P0: No endpoint error handling.
     /search calls search() at backend/app/main.py:36, then assumes
     results["documents"][0] and results["metadatas"][0] exist at
     backend/app/main.py:38. /chat similarly assumes ask_juit()
     succeeds at backend/app/main.py:52. Any retriever, Chroma,
     embedding, LLM, or empty-result failure becomes a raw 500.
     Root cause: route handlers trust downstream services and response
     shapes.
     Estimated impact: High.

  2. P0: Request validation is too weak.
     QueryRequest only declares query: str at backend/app/main.py:21.
     Empty strings, whitespace-only strings, very large payloads, and
     abusive inputs are accepted.
     Root cause: no field constraints or normalization.
     Estimated impact: High.

  3. P1: API response schemas are implicit.
     The app defines an input model but no response models for /, /
     search, or /chat at backend/app/main.py:25, backend/app/
     main.py:33, and backend/app/main.py:49. Clients have no enforced
     contract for result objects or error shapes.
     Root cause: plain dictionaries are returned directly.
     Estimated impact: Medium-High.

  4. P1: Endpoint design exposes raw retrieval output as answers.
     /search returns retrieved document chunks under "answers" at
     backend/app/main.py:44. That naming is misleading because these
     are not generated answers.
     Root cause: retrieval and answer-generation concepts are mixed in
     the API surface.
     Estimated impact: Medium.

  5. P1: No configurable search controls.
     /search always calls search(request.query) at backend/app/
     main.py:36, relying on retriever defaults. Clients cannot request
     result count, filters, or source-only metadata.
     Root cause: endpoint request model only supports query.
     Estimated impact: Medium.

  6. P2: Synchronous route handlers can block under load.
     Both endpoints are regular def handlers at backend/app/main.py:34
     and backend/app/main.py:50, while downstream search and chat
     generation are likely CPU, disk, network, or model-bound.
     Root cause: no async boundary, background execution, timeout
     handling, or concurrency controls.
     Estimated impact: Medium.

  7. P2: CORS is development-only and permissive in methods/headers.
     CORS allows only http://localhost:5173 at backend/app/main.py:14,
     while allowing all methods and headers at backend/app/main.py:16.
     This is brittle for deployment and broader than needed locally.
     Root cause: environment-specific config is hard-coded.
     Estimated impact: Medium.

  8. P3: Root endpoint is not a real health check.
     / returns static status at backend/app/main.py:25, but does not
     verify Chroma, retriever, model, or LLM availability.
     Root cause: status endpoint is informational only.
     Estimated impact: Low-Medium.

  Priority Order

  1. Add validation for query: trim, min length, max length.
  2. Add structured error handling around search() and ask_juit().
  3. Define response models and consistent error shapes.
  4. Rename /search response fields so chunks are not called answers.
  5. Add query controls such as limit and possibly filters.
  6. Address blocking behavior with timeouts/concurrency strategy.
  7. Move CORS settings to configuration.
  8. Add a real health endpoint for dependencies.

  No code changes were made.
