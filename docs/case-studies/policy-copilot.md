# PolicyCopilot — AI Systems Design Case Study

## What it is
An AI usage decision assistant. Employees upload their company's
AI policy, ask real questions about specific actions, and get
clear decisions with citations and safer alternatives.

**Problem it solves:** Before PolicyCopilot, employees emailed
managers or IT to ask "can I paste this client data into ChatGPT?"
and waited hours. PolicyCopilot gives an instant decision grounded
in the actual company policy document.

---

## Functional requirements
1. Accept a policy document — PDF upload, copy-paste, or URL
2. Accept a natural language question from an employee
3. Return a clear decision — allowed/not allowed/check with team
4. Cite the specific policy section that justifies the decision
5. Suggest safer alternatives when action is not allowed

## Non-functional requirements
1. Low latency — decision returned in under 10 seconds
2. Accuracy — answer must be grounded in the document, not hallucinated
3. Privacy — policy documents may be confidential, never stored by default
4. Reliability — Anthropic API outage should degrade gracefully

## Scale estimates (v1)
- Target: small to mid-size teams, 10-500 employees per company
- Expected: 100-1000 questions per day
- Document size: 1-50 pages per policy

---

## Architecture — what happens under the hood

### The pipeline (RAG — Retrieval Augmented Generation)
User uploads policy doc
↓
Document parsing — extract raw text from PDF/URL/paste
↓
Chunking — split into smaller pieces (500-1000 tokens each)
↓
User asks question
↓
Relevant chunks selected
↓
Prompt assembled:
"Here is the company policy: {chunks}
Employee question: {question}
Give a clear decision with citation."
↓
Anthropic API (Claude) generates decision
↓
Response displayed with citation + alternatives

### Why RAG and not just "send to LLM"?
LLMs are trained on general data — not your specific company policy.
Without RAG, Claude would guess or hallucinate policy details.
RAG grounds the answer in the actual document — that's what enables
citations. No document = no citation = not trustworthy for compliance.

---

## Tech stack
- **Frontend + backend:** Streamlit
- **LLM:** Anthropic API (Claude)
- **Document parsing:** PDF text extraction
- **Deployment:** Streamlit Cloud

---

## Data flow
Session only (v1):
User uploads doc → parsed in memory → used for this session → discarded
Future (v2):
User uploads doc → parsed → stored in vector database (Qdrant/Pinecone)
→ chunks embedded → retrieved semantically per question
→ persistent across sessions

---

## Failure modes

| Failure | User impact | Current mitigation |
|---|---|---|
| Anthropic API down | No response returned | Show error message, suggest retry |
| Large document (50 pages) | Slow parsing, context limit hit | Chunk document, warn user |
| Policy doesn't cover question | LLM has no grounding | Returns generic answer + directs to team |
| User pastes wrong document | Wrong citations | User responsibility in v1 |

---

## What makes it RAG specifically
- **Knowledge base** — the uploaded policy document
- **Query** — the employee's question
- **Grounded generation** — Claude reads the actual policy chunks
  before answering, not its training data
- **Citation** — possible because answer comes from the document,
  not from memory

This is the same pattern used by:
- Notion AI (your workspace as knowledge base)
- Perplexity (web search results as knowledge base)
- GitHub Copilot Chat (your codebase as knowledge base)

---

## Current limitations
- Document not stored — user re-uploads every session
- No semantic search — full document sent to Claude each time
  (works for small docs, breaks for 50+ pages)
- No authentication — anyone with the URL can use it
- Single LLM provider — Anthropic down = product down
- No usage analytics — can't see what questions employees ask most

---

## V2 improvements
1. **Vector database** — store chunks with embeddings (Qdrant)
   → semantic search finds most relevant chunks per question
   → handles 100+ page documents without hitting context limits
2. **User sessions** — save uploaded policy per user, no re-upload
3. **Authentication** — company-level login, employees under one org
4. **LLM fallback** — Anthropic down → switch to OpenAI or Bedrock
5. **Analytics dashboard** — most common questions, policy gaps
6. **Multi-document** — upload multiple policies, answer spans all

---

## Why this is a RAG system, not just a chatbot

| Chatbot | PolicyCopilot (RAG) |
|---|---|
| Answers from training data | Answers from your document |
| Can hallucinate policy details | Grounded in actual text |
| Generic responses | Specific citations |
| Same answer for everyone | Different per company policy |

---

## Portfolio talking points
- Built and deployed a production RAG system
- Solves a real compliance problem for real organizations
- Understands the difference between LLM training data and
  document-grounded generation
- Identified v2 improvements: vector DB, auth, multi-doc, fallback
- Live at: ai-policy-copilot.streamlit.app