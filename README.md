````markdown
# 📘 HR Policy Assistant

A beginner-friendly HR Policy Assistant built using RAG (Retrieval-Augmented Generation).

The application allows users to upload an HR Policy PDF and ask questions about the policy.

## 🚀 Technologies

- Python
- Streamlit
- FAISS
- Sentence Transformers
- PyMuPDF
- Groq
- `openai/gpt-oss-20b`

## 🔄 RAG Workflow

```text
HR Policy PDF
      ↓
PyMuPDF
      ↓
Extract Text
      ↓
Text Chunks
      ↓
Sentence Transformers
      ↓
Embeddings
      ↓
FAISS Vector Search
      ↓
User Question
      ↓
Relevant Policy Chunks
      ↓
Groq
      ↓
HR Policy Answer
````

## 📁 Project Structure

```text
hr-policy-assistant/
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ▶️ How the application works

1. Upload an HR Policy PDF.
2. Click "Process HR Policy".
3. PyMuPDF extracts the PDF text.
4. The text is divided into smaller chunks.
5. Sentence Transformers converts the chunks into embeddings.
6. FAISS stores the embeddings.
7. Enter an HR question.
8. FAISS finds the most relevant policy chunks.
9. The relevant chunks are sent to Groq.
10. Groq generates the answer.
11. The application displays the answer and source pages.

## 🔐 Groq API Key

Do not put your API key directly inside `app.py`.

For Streamlit Community Cloud:

1. Deploy the application.
2. Open the application's settings.
3. Open Secrets.
4. Add:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

5. Save the secret.
6. Restart/redeploy the application if required.

Never upload your API key to GitHub.

## ☁️ Deploy with GitHub and Streamlit Community Cloud

### Step 1 — Create GitHub repository

Create a new GitHub repository.

Example name:

```text
hr-policy-assistant
```

### Step 2 — Add these files

Upload:

```text
app.py
requirements.txt
README.md
.gitignore
```

### Step 3 — Open Streamlit Community Cloud

Go to:

https://share.streamlit.io/

Sign in with GitHub.

### Step 4 — Create the app

Choose:

```text
Create app
```

Then select:

```text
Deploy a public app from GitHub
```

Select your repository:

```text
hr-policy-assistant
```

Select:

```text
app.py
```

Then click:

```text
Deploy
```

### Step 5 — Add Groq API key

Open the deployed app's settings.

Find:

```text
Secrets
```

Add:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

Save the secret.

### Step 6 — Test

Upload an HR Policy PDF.

Click:

```text
Process HR Policy
```

Then ask questions such as:

```text
How many annual leave days are employees entitled to?
```

or:

```text
What is the maternity leave policy?
```

The application will retrieve relevant information and generate an answer.

## ⚠️ Important

The application answers using the uploaded HR policy context.

If the required information is not found, it should tell the user that the information could not be found in the uploaded document.

Do not upload confidential company HR documents unless you have permission to use them with the services involved.

## 🛠️ Common problems

### App says package is missing

Check that `requirements.txt` is in the repository root.

### App says Groq API key is missing

Add:

```toml
GROQ_API_KEY = "your_key"
```

to Streamlit Cloud Secrets.

### PDF has no readable text

The PDF may be scanned/image-only. This simple version expects selectable text in the PDF.

### FAISS installation error

Make sure the requirements file contains:

```text
faiss-cpu
```

### App does not update

Check that your latest changes were saved to the GitHub repository. Streamlit Community Cloud normally detects repository changes and updates the deployed app.

```
```
