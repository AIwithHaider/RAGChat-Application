
                        AAPChat-Agentic-AI-PDF-Chat — v2
                       (revised per architecture audit, Aug 2026)
══════════════════════════════════════════════════════════════════════════════════════════════
Legend: [NEW] = added stage   [CHG] = changed behavior   ↺ = feedback / invalidation path
══════════════════════════════════════════════════════════════════════════════════════════════

                                        INDEXING PIPELINE
══════════════════════════════════════════════════════════════════════════════════════════════

                        ┌──────────────────────────────┐
                        │ Document Upload (PDF/DOCX)   │
                        │ create | update | delete     │  [CHG] explicit op type,
                        └──────────────┬───────────────┘  not just "upload"
                                       │
                                       ▼
                     ┌───────────────────────────────────┐
                     │ API Gateway (FastAPI / Nginx)     │
                     │ Auth • JWT • RBAC • Rate Limit    │
                     └──────────────┬────────────────────┘
                                    │
                                    ▼
                     ┌───────────────────────────────────┐
                     │ Input Guardrails                  │
                     │ Virus Scan                        │
                     │ File Validation                   │
                     │ Prompt Injection Detection        │
                     │   (scans doc body for embedded    │
                     │    instructions, not just the     │  [CHG] explicit scope
                     │    upload request)                │
                     └──────────────┬────────────────────┘
                                    │
                                    ▼
                  ┌───────────────────────────────────────────┐
                  │ Object Storage (S3 / Azure Blob / GCS)    │
                  │ versioned buckets, immutable per version  │  [CHG] versioned storage
                  └──────────────┬────────────────────────────┘
                                 │
                                 ▼
                     ┌───────────────────────────────────┐
                     │ Background Queue                  │
                     │ (Celery / RabbitMQ / Kafka)       │
                     └──────────────┬────────────────────┘
                                    │
                        ┌───────────┴───────────┐
                        ▼                       ▼
              ┌───────────────────┐   ┌────────────────────────────┐
              │ Document Loader   │   │ [NEW] Lifecycle Router     │
              │ PDF•DOCX•PPT•HTML │   │ routes create → index,     │
              │ •Images           │   │ update → re-embed + purge, │
              └──────────┬────────┘   │ delete → tombstone vectors │
                         │            └──────────────┬─────────────┘
                         ▼                           │ ↺ (see below)
              ┌───────────────────────┐              │
              │ OCR / Text Extraction │              │
              │ OCR only if scanned   │              │
              └──────────┬────────────┘              │
                         │                           │                          
                         ▼                           │
              ┌───────────────────────┐              │
              │ Text Cleaning         │              │
              │ Headers / footers     │              │                 
              │ Unicode cleanup       │              │                 
              └──────────┬────────────┘              │                 
                         │                           │                 
                         ▼                           │                 
              ┌────────────────────────────┐         └────────────────┐
              │ Metadata Extraction        │                          │
              │ filename, author, page,    │   [CHG] +content hash    │
              │ section, ACL, language,    │   for change detection   │
              │ doc version, content hash  │                          │
              └──────────┬─────────────────┘                          │          
                         │                                            │
                         ▼                                   ┌────────┘     
              ┌─────────────────────────────────┐            │
              │ Intelligent Chunking            │            │
              │ Recursive / Semantic /          │            │
              │ Markdown-aware / Table-aware    │            │
              │                                 │            │
              │ [CHG] Parent-child chunking:    │            │
              │  small child chunk → embedded   │            │
              │  & indexed for precision;       │            │
              │  larger parent chunk → stored   │            │
              │  in metadata DB, returned to    │            │
              │  LLM as context after retrieval │            │
              └──────────────┬──────────────────┘            │
                             │                               │
                             ▼                               │
                  ┌──────────────────────────────┐           │
                  │ Tokenizer                    │           │
                  └──────────────┬───────────────┘           │
                                 │                           │
                                 ▼                           │
                  ┌──────────────────────────────────┐       │
                  │ Embedding Model                  │       │
                  │ [NEW] model_id + version         │       │
                  │ pinned & stamped on every vector │       │
                  └──────────────┬───────────────────┘       │
                                 │                           │
                 ┌───────────────┴───────────────┐           └────────────────┐
                 ▼                                ▼                           │ 
      ┌──────────────────────────────┐  ┌────────────────────────────┐        │ 
      │ Vector Database              │  │ Metadata Database          │        │
      │ Pinecone / Qdrant            │  │ PostgreSQL                 │        │  
      │                              │  │ stores: parent chunks,     │        │  
      │ [CHG] one namespace/index    │  │ doc versions, content      │        │ 
      │ PER TENANT — not just a      │  │ hashes, embedding model    │        │
      │ metadata filter. ACL filter  │  │ version per vector         │        │  
      │ is defense-in-depth, not the │◄─┴────────────────────────────┘        │   
      │ isolation boundary.          │                                        │  
      └──────────────┬───────────────┘                     ┌──────────────────┘  
                     │ ↺ tombstone / purge stale vectors   │
                     └─────────────────────────────────────┘
                     when: doc deleted, doc updated (old
                     version purged after new one is live),
                     or embedding model version bumped
                     (triggers async full re-embed job)

              [NEW] Re-embedding job (batch, offline)
              Triggered by: embedding model upgrade.
              Reads content hash + raw text from Metadata DB,
              re-embeds in a shadow index, cuts over on
              completion, then purges the old vector set.

Diagram of Indexing Pipline
![Alt text for screen readers](indexing_pipeline_v2.png)

Solid gray arrows = synchronous request path (upload → gateway → guardrails → object storage → enqueue). This is the part where the caller is waiting on a response.

Dashed gray arrows = everything that happens as an async background job once the item hits the queue: loading, OCR, cleaning, metadata extraction, chunking, tokenizing, embedding, and the offline re-embed job.

Dashed red arrows = the invalidation/feedback path. The lifecycle router's tombstone-on-delete signal and the re-embed job's shadow-index cutover both converge into the vector database along the same red channel, since they're the same kind of event (stale vectors being purged) even though they're triggered differently.

Color by category: blue = ingress/auth, coral = guardrails and the invalidation-adjacent re-embed job, gray = storage/queueing infrastructure, teal = the core processing chain, purple = the lifecycle router (control logic), amber = the two persistence stores.

══════════════════════════════════════════════════════════════════════════════════════════════

                                     RETRIEVAL PIPELINE
══════════════════════════════════════════════════════════════════════════════════════════════

          User
            │
            ▼
    React / Next.js
            │
            ▼
  API Gateway (Auth + RBAC)
            │
            ▼
    Input Guardrails
            │
            ▼
     Query Processing
     ----------------
     Spell Correction
     Query Expansion
     Language Detection
     Acronym Expansion
     Query Classification ──────┐
                                │  [CHG] classification now
                                │  actually routes:
                                │  simple factual → skip rerank,
                                │  top-1 vector hit + light check
                                │  multi-hop / complex → full
                                │  hybrid + rerank + compression
                                │  out-of-scope → short-circuit
                                │  to "can't help" response,
                                │  skip retrieval entirely
                                ▼
            ┌─────────────────────────────────┐
            │ Query Embedding                 │
            │ [NEW] must use SAME model_id/   │
            │ version as the indexed vectors  │
            │ it will search against          │
            └──────────────┬──────────────────┘
                           │
                           ▼
                  Hybrid Retriever
                  ┌─────────────────────────────┐
                  │ Vector Search               │
                  │ BM25 Search                 │
                  │ Metadata Filtering          │
                  │ ACL Filtering               │
                  │ [CHG] scoped to caller's    │
                  │ tenant namespace first      │
                  └─────────────┬───────────────┘
                                │
                                ▼
                    Candidate Documents
                                │
                                ▼
                  Cross Encoder Reranker
                                │
                                ▼
                      Top-K Passages
                      (parent chunks resolved
                       from Metadata DB here)      [CHG] resolve
                                │                    parent context
                                ▼
                  Context Compression
                                │
                                ▼
        ┌────────────────────────────────────────┐
        │ [NEW] Token Budget Allocator           │
        │ fixed reserve for system prompt,       │
        │ sliding-window cap on conversation     │
        │ history, remainder to retrieved        │
        │ context — logs when truncation occurs  │
        │ rather than silently dropping context  │
        └──────────────┬─────────────────────────┘
                       │
                       ▼
                 Prompt Builder
                 ----------------
                 System Prompt
                 Conversation History
                 Retrieved Context
                 User Query
                       │
                       ▼
                     LLM
             GPT / Claude / Gemini / Llama
                       │
                       ▼
                  Output Guardrails
                  -----------------
                  Citation Validation ──┐
                  Hallucination Check   │  [NEW] on failure:
                  PII Detection         │  1. attempt one regenerate
                  Toxicity Filter       │     with stricter grounding
                                        │     instruction
                                        │  2. if still failing, strip
                                        │     unsupported claim and
                                        │     flag it to the user
                                        │     rather than serve silently
                                        ▼
                  ┌───────────────────────────────────┐
                  │ [NEW] Fallback Controller         │
                  │ triggers if: reranker timeout,    │
                  │ vector DB unavailable, LLM API    │
                  │ error, guardrail hard-fail        │
                  │                                   │
                  │ degrade order:                    │
                  │  hybrid+rerank → BM25-only →      │
                  │  "insufficient information,       │
                  │   try rephrasing" (never silentl  │
                  │   answer ungrounded)              │
                  └──────────────┬────────────────────┘
                                 │
                                 ▼
                      Final Response
                      Answer
                      Citations
                      Page Numbers
                      [NEW] confidence flag (grounded /
                      partially-grounded / degraded-mode)

══════════════════════════════════════════════════════════════════════════════════════════════

                               SHARED PLATFORM SERVICES
══════════════════════════════════════════════════════════════════════════════════════════════

        Redis Cache
        ├── Embedding Cache      [CHG] key includes embedding
        │                         model_id/version — auto-misses
        │                         after a model upgrade instead
        │                         of serving stale vectors
        ├── Retrieval Cache      [CHG] invalidated on doc
        │                         update/delete via pub/sub from
        │                         Lifecycle Router
        └── Response Cache       [CHG] TTL bounded + invalidated
                                  on doc update; never cached for
                                  degraded-mode responses

        Conversation Memory
        ├── Chat History
        ├── Session Store
        └── User Context

        Observability
        ├── LangSmith
        ├── OpenTelemetry
        ├── Prometheus
        ├── Grafana
        └── Structured Logging
        [NEW] alert on: fallback-controller activation rate,
        citation-validation failure rate, re-embed job lag

        Evaluation Pipeline
        ├── Recall@K
        ├── Precision@K
        ├── Faithfulness
        ├── Groundedness
        ├── Hallucination Rate
        ├── Citation Accuracy
        └── [NEW] Staleness — % of served answers whose source
              chunk's content hash no longer matches live doc

        Security
        ├── JWT
        ├── RBAC
        ├── Multi-Tenant Isolation
        │     [CHG] enforced at vector DB namespace/index level,
        │     ACL metadata filter is a second layer, not the
        │     only layer
        ├── Encryption at Rest
        ├── Encryption in Transit
        ├── Audit Logs
        └── Secret Management

══════════════════════════════════════════════════════════════════════════════════════════════
SUMMARY OF CHANGES FROM v1
══════════════════════════════════════════════════════════════════════════════════════════════
1. Lifecycle Router + tombstoning + re-embedding job — handles update/delete/model-upgrade,
   which v1 had no path for.
2. Parent-child chunking — small chunks indexed for precision, larger parent chunks returned
   for LLM context.
3. Embedding model version pinned on every vector; query embedder must match.
4. Query Classification now actually routes (simple/complex/out-of-scope), instead of being
   a dead-end logging step.
5. Token Budget Allocator between compression and prompt building — prevents silent context
   truncation as chat history grows.
6. Citation validation failure now has a defined recovery path (regenerate → strip claim →
   flag), instead of an unspecified end state.
7. Fallback Controller with an explicit degrade order — system never silently serves an
   ungrounded answer when a dependency fails.
8. Cache keys/invalidation tied to document version and embedding model version — closes the
   silent-staleness gap.
9. Tenant isolation moved from "just a metadata filter" to namespace/index-level separation
   in the vector DB, with the filter as defense-in-depth.
10. New Staleness eval metric to catch drift between what's indexed and what's live.











 
                                AAPChat-Agentic-AI-PDF-Chat
══════════════════════════════════════════════════════════════════════════════════════════════

                                        INDEXING PIPELINE
══════════════════════════════════════════════════════════════════════════════════════════════

                        ┌──────────────────────────────┐
                        │ Document Upload (PDF/DOCX) │
                        └──────────────┬──────────────┘
                                       │
                                       ▼
                     ┌──────────────────────────────────┐
                     │ API Gateway (FastAPI / Nginx)    │
                     │ Auth • JWT • RBAC • Rate Limit   │
                     └──────────────┬───────────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────────┐
                     │ Input Guardrails                 │
                     │ Virus Scan                       │
                     │ File Validation                  │
                     │ Prompt Injection Detection       │
                     └──────────────┬───────────────────┘
                                    │
                                    ▼
                  ┌─────────────────────────────────────────┐
                  │ Object Storage (S3 / Azure Blob / GCS) │
                  └──────────────┬──────────────────────────┘
                                 │
                                 ▼
                     ┌──────────────────────────────────┐
                     │ Background Queue                 │
                     │ (Celery / RabbitMQ / Kafka)      │
                     └──────────────┬───────────────────┘
                                    │
                                    ▼
                   ┌────────────────────────────────────┐
                   │ Document Loader                    │
                   │ PDF • DOCX • PPT • HTML • Images   │
                   └──────────────┬─────────────────────┘
                                  │
                                  ▼
                   ┌────────────────────────────────────┐
                   │ OCR / Text Extraction              │
                   │ OCR only if scanned document       │
                   └──────────────┬─────────────────────┘
                                  │
                                  ▼
                   ┌────────────────────────────────────┐
                   │ Text Cleaning                      │
                   │ Remove headers                     │
                   │ Remove footers                     │
                   │ Unicode cleanup                    │
                   └──────────────┬─────────────────────┘
                                  │
                                  ▼
                  ┌──────────────────────────────────────┐
                  │ Metadata Extraction                  │
                  │ filename                             │
                  │ author                               │
                  │ page                                 │
                  │ section                              │
                  │ ACL                                 │
                  │ language                             │
                  │ document version                     │
                  └──────────────┬───────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────────┐
                    │ Intelligent Chunking            │
                    │ Recursive                       │
                    │ Semantic                        │
                    │ Markdown aware                  │
                    │ Table aware                     │
                    │ Chunk overlap                   │
                    └──────────────┬──────────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────────┐
                      │ Tokenizer                   │
                      └──────────────┬──────────────┘
                                     │
                                     ▼
                      ┌─────────────────────────────┐
                      │ Embedding Model             │
                      └──────────────┬──────────────┘
                                     │
                 ┌───────────────────┴─────────────────────┐
                 ▼                                         ▼
      ┌─────────────────────┐                 ┌─────────────────────┐
      │ Vector Database     │                 │ Metadata Database   │
      │ Pinecone/Qdrant     │                 │ PostgreSQL          │
      └─────────────────────┘                 └─────────────────────┘

══════════════════════════════════════════════════════════════════════════════════════════════

                                     RETRIEVAL PIPELINE
══════════════════════════════════════════════════════════════════════════════════════════════

          User
            │
            ▼
    React / Next.js
            │
            ▼
  API Gateway (Auth + RBAC)
            │
            ▼
    Input Guardrails
            │
            ▼
     Query Processing
     ----------------
     Spell Correction
     Query Expansion
     Language Detection
     Acronym Expansion
     Query Classification
            │
            ▼
       Query Embedding
            │
            ▼
      Hybrid Retriever
      ┌─────────────────────────────┐
      │ Vector Search               │
      │ BM25 Search                 │
      │ Metadata Filtering          │
      │ ACL Filtering               │
      └─────────────┬───────────────┘
                    │
                    ▼
        Candidate Documents
                    │
                    ▼
      Cross Encoder Reranker
                    │
                    ▼
          Top-K Passages
                    │
                    ▼
      Context Compression
                    │
                    ▼
         Prompt Builder
         ----------------
         System Prompt
         Conversation History
         Retrieved Context
         User Query
                    │
                    ▼
              LLM
      GPT / Claude / Gemini / Llama
                    │
                    ▼
      Output Guardrails
      -----------------
      Citation Validation
      Hallucination Check
      PII Detection
      Toxicity Filter
                    │
                    ▼
      Final Response
      Answer
      Citations
      Page Numbers

══════════════════════════════════════════════════════════════════════════════════════════════

                               SHARED PLATFORM SERVICES
══════════════════════════════════════════════════════════════════════════════════════════════

        Redis Cache
        ├── Embedding Cache
        ├── Retrieval Cache
        └── Response Cache

        Conversation Memory
        ├── Chat History
        ├── Session Store
        └── User Context

        Observability
        ├── LangSmith
        ├── OpenTelemetry
        ├── Prometheus
        ├── Grafana
        └── Structured Logging

        Evaluation Pipeline
        ├── Recall@K
        ├── Precision@K
        ├── Faithfulness
        ├── Groundedness
        ├── Hallucination Rate
        └── Citation Accuracy

        Security
        ├── JWT
        ├── RBAC
        ├── Multi-Tenant Isolation
        ├── Encryption at Rest
        ├── Encryption in Transit
        ├── Audit Logs
        └── Secret Management

══════════════════════════════════════════════════════════════════════════════════════════════



Diagram of Indexing Pipline
![Alt text for screen readers](indexing_pipeline_v2.png)
