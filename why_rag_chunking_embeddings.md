
# Why Do We Need Chunking, Nomic Embeddings and ChromaDB?

## 1. Do We Really Need Them?

Yes, I recommend using chunking and Nomic embeddings for our Enterprise Documentation Assistant.

However, they are not compulsory for every database. It depends on how we want to retrieve information.

Our HCLTech problem statement requires a documentation assistant that retrieves relevant passages and answers questions using only supported evidence.

Therefore, RAG is a suitable approach.

---

## 2. Can We Send the Entire Document Directly to Gemini?

Yes!

For example, an employee asks:

"How do I manage my GitLab subscription?"

We could send the entire subscription document to Gemini and ask it to answer.

This works for a small collection, but has limitations:

- What if we have 1,000 documents?
- What if documents are very long?
- What if the answer is spread across multiple documents?
- What if old and new policies contradict each other?
- What if we want only the relevant supporting passages?

Sending everything to Gemini for every question becomes inefficient.

---

## 3. Why Do We Need Chunking?

Suppose one document contains 10,000 words.

Instead of treating the entire document as one piece, we split it into smaller meaningful passages called chunks.

### Example

Original document:

10,000 words

After chunking:

- Chunk 1
- Chunk 2
- Chunk 3
- Chunk 4
- Chunk 5
- Chunk 6

Each chunk contains a smaller portion of the original document.

### Why is chunking useful?

When an employee asks a question, we can retrieve only the passages relevant to that question instead of sending the entire document.

For example:

Question:
"How can I enable two-factor authentication?"

We retrieve the chunk containing the two-factor authentication instructions.

**Chunking makes retrieval more focused and efficient.**

---

## 4. Why Do We Need Nomic Embeddings?

Chunking only divides documents. It does not identify which chunk is relevant to a question.

For that, we use embeddings.

Suppose our document contains:

"Users can enable two-factor authentication from their account security settings."

The employee asks:

"How do I add an extra layer of protection to my account?"

The wording is different, but the meaning is similar.

Nomic converts both the document passage and the employee's question into numerical vectors.

These vectors represent semantic meaning.

We can compare the vectors to find passages with similar meanings.

### Why embeddings?

- Understand similar meanings despite different wording.
- Retrieve relevant passages.
- Support natural-language questions.
- Improve semantic search compared with exact keyword matching alone.

---

## 5. Why Do We Need ChromaDB?

ChromaDB is a vector database.

It stores:

- Document embeddings (vectors).
- Original text passages.
- Document IDs.
- Source information.
- Other metadata.

When an employee asks a question:

1. Nomic converts the question into an embedding.
2. ChromaDB searches for similar stored vectors.
3. ChromaDB returns the most relevant passages.
4. Gemini receives those passages.
5. Gemini generates an answer using the retrieved evidence.

---

## 6. What If We Don't Use Embeddings?

There are alternative approaches.

| Approach | How it works | Suitable use |
|---|---|---|
| Entire document + Gemini | Send complete documents to Gemini | Small collections |
| Keyword search (BM25) | Match important words | Keyword-based retrieval |
| Nomic + ChromaDB | Semantic vector search | Recommended for our project |
| Hybrid search | Combine keyword and semantic search | More advanced retrieval |

For example, keyword search might miss a question phrased differently from the original document.

Semantic search can help retrieve relevant information despite differences in wording.

---

## 7. Our Final RAG Architecture

### Document Ingestion

1. Four Markdown documents
2. Document parsing
3. Chunking
4. Nomic embedding generation
5. ChromaDB vector storage

### Question Answering

1. Employee asks a question.
2. Nomic generates the question embedding.
3. ChromaDB retrieves relevant passages.
4. Retrieved passages are passed to Gemini.
5. Gemini generates an evidence-based answer.
6. The answer is displayed with document citations.

---

## 8. Understand the Three Main Components

| Component | Responsibility |
|---|---|
| Nomic Embed Text | Embedding model: converts text into numerical vectors |
| ChromaDB | Vector database: stores and retrieves embeddings and associated text |
| Gemini | LLM: generates answers using retrieved evidence |

They perform three different jobs.

**Nomic = Embedding Model**

**ChromaDB = Vector Database**

**Gemini = Answer Generation Model**

---

## 9. Final Recommendation for Our Hackathon

Our current dataset contains only four documents.

Technically, we could send all four directly to Gemini.

However, our problem statement specifically requires retrieving relevant passages from a knowledge collection.

Therefore, I recommend implementing RAG instead of simply uploading documents and asking Gemini questions.

Keep:

- Chunking
- Nomic Embeddings
- ChromaDB
- Gemini

This allows us to demonstrate actual document retrieval, semantic search, evidence-based answers and unsupported-question fallback.

**Our objective is not just to generate answers. It is to retrieve the correct supporting evidence and generate answers grounded in that evidence.**