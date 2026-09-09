import os
import tempfile

import fitz  # PyMuPDF
import faiss
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
from groq import Groq


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="📘",
    layout="wide"
)

st.title("📘 HR Policy Assistant")
st.write(
    "Upload an HR Policy PDF and ask questions about the policy."
)


# -----------------------------
# Load embedding model
# -----------------------------
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


embedding_model = load_embedding_model()


# -----------------------------
# Extract text from PDF
# -----------------------------
def extract_pdf_text(pdf_file):
    pdf_bytes = pdf_file.getvalue()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:

        temp_file.write(pdf_bytes)
        temp_path = temp_file.name

    try:
        document = fitz.open(temp_path)

        pages = []

        for page_number, page in enumerate(document):
            text = page.get_text("text")

            if text.strip():
                pages.append(
                    {
                        "page": page_number + 1,
                        "text": text
                    }
                )

        document.close()

        return pages

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# -----------------------------
# Split text into chunks
# -----------------------------
def create_chunks(pages, chunk_size=1000, overlap=150):

    chunks = []

    for page_data in pages:

        text = " ".join(
            page_data["text"].split()
        )

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:

                chunks.append(
                    {
                        "text": chunk_text,
                        "page": page_data["page"]
                    }
                )

            if end >= len(text):
                break

            start = end - overlap

    return chunks


# -----------------------------
# Create FAISS index
# -----------------------------
def create_faiss_index(chunks):

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True
    )

    embeddings = embeddings.astype(
        "float32"
    )

    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index


# -----------------------------
# Retrieve relevant chunks
# -----------------------------
def retrieve_chunks(
    question,
    chunks,
    index,
    top_k=5
):

    question_embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True
    ).astype("float32")

    faiss.normalize_L2(question_embedding)

    scores, indices = index.search(
        question_embedding,
        min(top_k, len(chunks))
    )

    results = []

    for score, index_number in zip(
        scores[0],
        indices[0]
    ):

        if index_number == -1:
            continue

        results.append(
            {
                "text": chunks[index_number]["text"],
                "page": chunks[index_number]["page"],
                "score": float(score)
            }
        )

    return results


# -----------------------------
# Generate answer with Groq
# -----------------------------
def generate_answer(
    question,
    retrieved_chunks,
    api_key
):

    client = Groq(
        api_key=api_key
    )

    context_parts = []

    for i, result in enumerate(
        retrieved_chunks,
        start=1
    ):

        context_parts.append(
            f"""
Source {i}
Page: {result['page']}

{result['text']}
"""
        )

    context = "\n".join(
        context_parts
    )

    system_prompt = """
You are an HR Policy Assistant.

Answer the user's question using ONLY the HR policy information provided in the context.

Rules:

1. Do not invent policies.
2. Do not use outside information.
3. If the answer is not available in the context, clearly say:
   "I could not find this information in the uploaded HR policy document."
4. Keep the answer simple and clear.
5. Mention the relevant page number when possible.
"""

    user_prompt = f"""
HR POLICY CONTEXT:

{context}

USER QUESTION:

{question}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.2,
        max_completion_tokens=700
    )

    return response.choices[0].message.content


# -----------------------------
# API key
# -----------------------------
api_key = st.secrets.get(
    "GROQ_API_KEY",
    ""
)

if not api_key:

    api_key = st.sidebar.text_input(
        "Groq API Key",
        type="password"
    )

    st.sidebar.info(
        "For Streamlit Cloud, you can add GROQ_API_KEY "
        "in App Settings → Secrets."
    )


# -----------------------------
# Upload PDF
# -----------------------------
st.subheader("1️⃣ Upload HR Policy PDF")

uploaded_file = st.file_uploader(
    "Choose an HR Policy PDF",
    type=["pdf"]
)


# -----------------------------
# Process PDF
# -----------------------------
if uploaded_file:

    if st.button(
        "📚 Process HR Policy"
    ):

        with st.spinner(
            "Reading and processing the PDF..."
        ):

            try:

                pages = extract_pdf_text(
                    uploaded_file
                )

                if not pages:

                    st.error(
                        "No readable text was found in this PDF."
                    )

                    st.stop()

                chunks = create_chunks(
                    pages
                )

                if not chunks:

                    st.error(
                        "Could not create text chunks."
                    )

                    st.stop()

                index = create_faiss_index(
                    chunks
                )

                st.session_state["chunks"] = chunks
                st.session_state["index"] = index
                st.session_state["filename"] = uploaded_file.name

                st.success(
                    f"PDF processed successfully! "
                    f"{len(chunks)} text chunks created."
                )

            except Exception as error:

                st.error(
                    f"Error while processing PDF: {error}"
                )


# -----------------------------
# Question answering
# -----------------------------
st.subheader("2️⃣ Ask a Question")

question = st.text_input(
    "Enter your HR policy question",
    placeholder="Example: How many annual leaves are allowed?"
)


if st.button(
    "🔎 Ask Question"
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    elif "chunks" not in st.session_state:

        st.warning(
            "Please upload and process a PDF first."
        )

    elif not api_key:

        st.warning(
            "Please add your Groq API key."
        )

    else:

        with st.spinner(
            "Searching the HR policy..."
        ):

            try:

                retrieved_chunks = retrieve_chunks(
                    question,
                    st.session_state["chunks"],
                    st.session_state["index"]
                )

                answer = generate_answer(
                    question,
                    retrieved_chunks,
                    api_key
                )

                st.subheader(
                    "✅ Answer"
                )

                st.write(answer)

                st.subheader(
                    "📄 Sources"
                )

                for result in retrieved_chunks:

                    st.write(
                        f"Page {result['page']} "
                        f"— relevance score: "
                        f"{result['score']:.2f}"
                    )

                    with st.expander(
                        "View retrieved policy text"
                    ):

                        st.write(
                            result["text"]
                        )

            except Exception as error:

                st.error(
                    f"Error while generating answer: {error}"
                )


# -----------------------------
# Footer
# -----------------------------
st.divider()

st.caption(
    "HR Policy Assistant • RAG • "
    "FAISS • Sentence Transformers • "
    "PyMuPDF • Groq"
)
```
