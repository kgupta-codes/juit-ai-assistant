# API

Base URL in local development:

```text
http://127.0.0.1:8000
```

## GET /

Basic service status.

Response:

```json
{
  "status": "online",
  "message": "JUIT AI Assistant API Running"
}
```

## GET /health

Health check endpoint for deployment platforms.

Response:

```json
{
  "status": "ok",
  "service": "juit-ai-assistant"
}
```

## POST /chat

Ask a question and receive a grounded answer.

Request:

```json
{
  "query": "Who is the HOD of CSE?",
  "session_id": "conv-123"
}
```

Fields:

- `query`: required, non-empty user question.
- `session_id`: optional conversation identifier. Use a stable value per chat to preserve follow-up context.

Response:

```json
{
  "question": "Who is the HOD of CSE?",
  "answer": "The HOD of Computer Science Engineering and Information Technology is ...",
  "sources": [
    {
      "title": "Computer Science & Engineering and Information Technology Faculty",
      "url": "https://www.juit.ac.in/computer-science-engineering-information-technology-faculty"
    }
  ],
  "history": [],
  "confidence": 10.53,
  "rewritten_query": "Who is the HOD of CSE?"
}
```

If the system cannot confidently find evidence, the answer is:

```text
I could not confidently find this information on the official JUIT website.
```

## POST /search

Return retrieved chunks and source metadata without answer generation.

Request:

```json
{
  "query": "Civil Engineering laboratories"
}
```

Response:

```json
{
  "question": "Civil Engineering laboratories",
  "results_found": 5,
  "answers": ["retrieved document text"],
  "sources": [{"title": "Laboratory", "url": "https://www.juit.ac.in/civil-engineering-laboratory"}]
}
```

## Error Responses

Validation errors return FastAPI's standard `422` response.

Service failures return:

```json
{
  "detail": "Chat service unavailable"
}
```

or:

```json
{
  "detail": "Search service unavailable"
}
```

with HTTP status `503`.

## CORS

Allowed origins are configured with:

```text
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Use only trusted frontend domains in production.
