# Personal Knowledge Base (RAG CLI)

A command-line RAG (Retrieval-Augmented Generation) tool that lets you ask questions about your own documents. It ingests PDF, Markdown and text files, splits them into overlapping chunks, embeds them locally into a persistent Chroma vector store, and answers questions with Gemini using the most relevant retrieved chunk.

> **Project 6** of my 50-Day Gen AI Agent Mastery Plan (Phase 2: RAG & Vector Databases).

---

## Features

- **Multi-format ingestion**: `.pdf`, `.md` and `.txt`, from a single file or an entire folder
- **Custom recursive chunker**: written from scratch (no LangChain), with configurable size and overlap
- **Local embeddings**: `all-MiniLM-L6-v2` via `sentence-transformers`, so no embedding API cost
- **Persistent vector store**: ChromaDB, so you ingest once and query many times
- **Interactive Q&A loop**: ask follow-up questions in the same session, type `quit` to exit
- **Streaming answers**: responses print token by token

---

## How It Works

```
        INGEST                                         QUERY
 ┌───────────────────┐                        ┌────────────────────┐
 │ documents/        │                        │ your question      │
 │ .pdf .md .txt     │                        └─────────┬──────────┘
 └─────────┬─────────┘                                  │
           ▼                                            ▼
 ┌───────────────────┐                        ┌────────────────────┐
 │ doc_extractor.py  │                        │ chunk_retriever.py │
 │ extract raw text  │                        │ embed query, find  │
 └─────────┬─────────┘                        │ nearest chunk(s)   │
           ▼                                  └─────────┬──────────┘
 ┌───────────────────┐                                  │
 │ chunker.py        │                                  ▼
 │ recursive split   │                        ┌────────────────────┐
 │ 250 chars / 70    │                        │ main.py            │
 │ overlap           │                        │ chunk + question   │
 └─────────┬─────────┘                        │ → Gemini → stream  │
           ▼                                  └────────────────────┘
 ┌───────────────────┐                                  ▲
 │ store_embedding.py│                                  │
 │ embed + save to   ├──────────► my_chroma_data/ ──────┘
 │ ChromaDB          │
 └───────────────────┘
```

---

## Project Structure

```
Project_6-_Personal_Knowledge_Base/
├── code/
│   ├── main.py             # CLI entry point (ingest / query commands, chat loop)
│   ├── doc_extractor.py    # Reads PDF / MD / TXT files into plain text
│   ├── chunker.py          # Recursive character text splitter with overlap
│   ├── store_embedding.py  # Embeds chunks and writes them to ChromaDB
│   └── chunk_retriever.py  # Semantic search over the stored chunks
├── documents/              # Sample documents to ingest
│   ├── 50_day_genai_roadmap.md
│   ├── ds_writing_and_fe_guide.pdf
│   └── story.txt
├── config.toml             # Model/provider settings (see note below)
├── my_chroma_data/         # Persistent vector store (created on ingest)
└── .gitignore
```

### Module details

| File | Responsibility |
|---|---|
| `doc_extractor.py` | `extracted_content(path)` accepts a file or directory and returns `{filename: text}`. PDFs are read page by page with `pypdf`; `.md`/`.txt` are read as UTF-8. Unsupported file types are skipped silently when scanning a folder. |
| `chunker.py` | `recursive_split(text, chunk_size=250, chunk_overlap=70)` tries separators in order (`"\n\n"`, `"\n"`, `" "`, `""`), packs pieces into chunks up to `chunk_size`, carries the last `chunk_overlap` characters into the next chunk, and recurses with finer separators on any chunk that is still too large. Sizes are measured in **characters**. |
| `store_embedding.py` | `store_chuks(chunks, file_name)` adds chunks to the `my_embedded_chunks` collection with IDs of the form `<filename>_chunk_<n>`, so chunks from different files never collide. |
| `chunk_retriever.py` | `relevent_chunks(query, top_k=1)` runs a similarity query against the collection and returns the top-k chunk texts. |
| `main.py` | `argparse` CLI with two subcommands, `ingest` and `query`. The query command retrieves context, sends it with the question to Gemini through the OpenAI-compatible client, and streams the reply. |

---

## Tech Stack

| Component | Choice |
|---|---|
| Language | Python 3 (developed on 3.14) |
| Vector DB | [ChromaDB](https://www.trychroma.com/) (persistent client) |
| Embeddings | `all-MiniLM-L6-v2` (`sentence-transformers`) |
| PDF parsing | `pypdf` |
| LLM | Gemini (`gemini-3-flash-preview`) via the `openai` Python client |
| Config / secrets | `python-dotenv` (`.env`) |

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/satyam-sharma7/Project_6-_Personal_Knowledge_Base.git
cd Project_6-_Personal_Knowledge_Base

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install chromadb sentence-transformers pypdf openai python-dotenv
```

The first run downloads the `all-MiniLM-L6-v2` model, so it needs an internet connection once.

### 3. Add your API key

Create a `.env` file in the project root:

```env
GOOGLE_AI_STUDIO=your_google_ai_studio_api_key
```

Get a key from [Google AI Studio](https://aistudio.google.com/). The `.env` file is git-ignored.

---

## Usage

> Run all commands **from the project root**, because the vector store path (`./my_chroma_data`) is relative to your working directory.

### Ingest documents

```bash
# a whole folder
python code/main.py ingest --docs documents

# a single file
python code/main.py ingest --docs documents/story.txt
```

Ingesting the three bundled sample documents produces **155 chunks** (52 from the roadmap, 82 from the story, 21 from the PDF).

### Ask questions

```bash
python code/main.py query "What is Project 6 in the roadmap?"
```

After the first answer you get an interactive prompt:

```
Bot: <streamed answer>

Ask another question: <type here, or "quit" to exit>
```

---

## Configuration

Chunking defaults live in `code/chunker.py`:

| Parameter | Default | Meaning |
|---|---|---|
| `chunk_size` | `250` | Max characters per chunk |
| `chunk_overlap` | `70` | Characters shared between consecutive chunks |
| `separators` | `["\n\n", "\n", " ", ""]` | Split priority, coarse to fine |

Retrieval depth is set by `top_k` (default `1`) in `chunk_retriever.py` and in the call inside `main.py`.

`config.toml` lists model profiles (MiniMax, Gemini, GLM, Qwen) with provider, base URL, key name, temperature and max tokens. **It is not read by the current code**: `main.py` hardcodes Gemini. It is a reference for switching providers later.

---

## Known Limitations

Being upfront about where this version stops:

- **No citations**: answers don't show which file or chunk they came from, even though source filenames are encoded in the chunk IDs.
- **Single-chunk context**: `top_k=1` with 250-character chunks gives the LLM very little context, so answers that span multiple passages will be weak.
- **Re-ingesting does not update**: chunk IDs are deterministic, so ingesting an edited file again won't replace the old chunks. Delete `my_chroma_data/` and re-ingest to rebuild.
- **Ingest summary is off by one**: the "Ingested N chunks from M documents" message adds 1 to both counts.
- **Character-based chunking**: chunks can split mid-sentence, since sizes are counted in characters, not tokens or sentences.
- **No dependency file**: there is no `requirements.txt` yet.
- **Single hardcoded provider**: switching models requires editing `main.py`.

---

## Roadmap / Ideas

- [ ] Return source citations (file name + chunk) with every answer
- [ ] Increase `top_k` and add a similarity-score threshold with an "I don't know" fallback
- [ ] Larger chunks, or sentence/token-aware splitting
- [ ] Upsert on ingest so edited files refresh cleanly
- [ ] Load provider settings from `config.toml`
- [ ] Add a `requirements.txt`
- [ ] Remove committed `__pycache__` and `my_chroma_data/` from the repo (both are tracked despite `.gitignore`)
- [ ] Add more file types (`.docx`, `.html`) and a `--reset` flag

---

## Author

**Satyam Sharma**
[GitHub](https://github.com/satyam-sharma7) · [LinkedIn](https://www.linkedin.com/in/satyam-sharma-778383379/)