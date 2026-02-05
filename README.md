
```markdown
# 🧠 Persistent Knowledge RAG Agent (v1.0.0)

A framework-free, disk-persistent Retrieval-Augmented Generation (RAG) system
built **from first principles**.

This project implements a **long-term knowledge agent** that can:
- Ingest files (PDF / TXT / MD)
- Store knowledge persistently on disk
- Retrieve relevant past information using embeddings
- Generate **grounded, confidence-aware answers**
- Improve over time as memory grows

> ⚠️ This is **not** a LangChain demo.  
> This is a systems-level RAG implementation designed.
---

The agent behaves like a **long-term brain**, not a planner or executor.

```

Input → Retrieve memory → Answer → Persist knowledge

```

---

## 🧱 High-Level Architecture

File Ingestion  
↓  
Persistent Memory (metadata.json)  
↓  
Chunking Engine (chunks.json)  
↓  
Embedding Store (embeddings.json)  
↓  
Retriever (similarity + threshold)  
↓  
Grounded Answer Generator


```

```

All state lives **on disk**, survives restarts, and can be rebuilt deterministically.

---

## 📂 Project Structure
silver-system-RAG/  
├── main.py # Unified CLI entry point  
├── ingest/  
│ ├── file_ingestor.py # File → memory → chunks → embeddings  
│ └── chunker.py # Deterministic chunking engine  
├── embeddings/  
│ ├── embedder.py # Embedding model abstraction  
│ └── embedding_store.py # Disk-backed vector store  
├── retrieval/  
│ └── retriever.py # Similarity search + thresholding  
├── llm/  
│ └── answer_generator.py # Grounded answer generation  
├── memory/  
│ └── metadata_store.py # Append-only source-of-truth memory  
├── data/  
│ ├── metadata.json # Persistent memories  
│ ├── chunks.json # Derived chunks (disposable)  
│ └── embeddings.json # Stored embeddings  
├── requirements.txt  
└── README.md
```

````

## 🧠 Phase-by-Phase Breakdown

### 🔹 Phase 1 — Persistent Memory & Storage

**Goal:** Build a crash-safe, append-only memory system.

What was implemented:
- Disk-backed `MetadataStore`
- Atomic writes to prevent corruption
- Append-only memory (never overwrite)
- Clear separation between:
  - **Source-of-truth memory**
  - **Derived data**
---

### 🔹 Phase 2 — Embeddings & Chunking

#### Phase 2A — Chunking Engine

**Goal:** Convert raw memory into reusable, semantically coherent chunks.

What was implemented:
- Deterministic chunking (paragraph-aware)
- Chunk quality rules:
  - A chunk should answer at least one clear question
- Overlap tolerance for context continuity
- Chunk IDs treated as disposable
---

#### Phase 2B — Embedding System & Vector Index

**Goal:** Represent chunks numerically for similarity search.

What was implemented:
- Local embedding model abstraction
- Fixed-dimension vectors
- Disk-persistent embedding store
- Model-aware embedding storage
---

### 🔹 Phase 3 — Retrieval Engine

**Goal:** Retrieve relevant chunks with minimal noise.

What was implemented:
- Cosine similarity search
- Top-k retrieval
- Similarity thresholding
- Explicit retrieval states
---

### 🔹 Phase 4 — Knowledge-Grounded Answer Generation

**Goal:** Prevent hallucinations and enforce grounding.

What was implemented:
- Context injection from retrieved chunks
- Answer generation constrained to evidence
- Confidence-aware responses
- Explicit handling of weak or missing evidence
---

### 🔹 Phase 5 — Integration, Ingestion & Cleanup

#### Phase 5A — LLM Integration
- Groq API integration
- Environment-based API key loading

#### Phase 5B — File Ingestion
- Support for PDF / TXT / MD
- File → memory → chunks → embeddings pipeline
- Deterministic rebuild of derived data

#### Phase 5C — CLI Unification
- Single entry point: `main.py`
- Commands:
  - `ingest`
  - `ask`
  - `chat`

#### Phase 5D — Cleanup & Finalization
- Removal of legacy runner scripts
- Derived data cleanup (no chunk duplication)
- Versioned release (`v1.0.0`)


## 🚀 How to Run the System

### 1️⃣ Setup Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
````

Set your Groq API key:

```bash
export GROQ_API_KEY="your_api_key_here"
```

(or use a `.env` file if preferred) inside the .env file put
	`GROQ_API_KEY=your_api_key`

---

### 2️⃣ Ingest Files (Learning Mode)

```bash
python main.py ingest /absolute/path/to/file.pdf
```

This is done **once per file**. and once its done its data store into memory can reuse anytime.

---

### 3️⃣ Ask Questions (Thinking Mode)

```bash
python main.py ask "Why did my food delivery startup fail?"
```

No re-ingestion. Uses stored knowledge only.

---

### 4️⃣ Interactive Chat Mode

```bash
python main.py chat
```

Example:

```
> Summarize the Linux command guide
> What mistakes were mentioned earlier?
> exit(to exit chat mode)
```

---

## 🔒 What This Project Intentionally Does NOT Use

- ❌ LangChain
    
- ❌ LangGraph
    
- ❌ Vector databases
    
- ❌ Tool orchestration frameworks
    

These are avoided **on purpose** so the core mechanics are fully build manually.

---

## 🧠 What This Project about(building level)

- Persistent memory architecture
    
- Real RAG 
    
- Chunking strategy design
    
- Embedding trade-offs
    
- Retrieval noise control
    
- Hallucination prevention
    
- System-level thinking for AI agents
    
---

