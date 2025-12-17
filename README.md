# 📘 RFP BidAssist AI – Backend Setup Guide

This repository contains the **backend** for **RFP BidAssist AI**, built for the **EY Techathon**.

The backend is responsible for:

* Extracting structured data from RFP PDFs
* Creating technical summaries
* Supporting downstream Technical & Pricing Agents

**Tech Stack**

* Python 3.10+
* FastAPI
* Google Gemini (`google.genai` SDK)
* Pydantic

---

## 🚨 IMPORTANT (Read This First)

⚠️ **Always `cd` into the `backend/` folder before creating a virtual environment or installing dependencies.**

### Why this matters

* Keeps backend dependencies isolated
* Prevents conflicts with frontend or other projects
* Ensures all teammates have identical setups
* Avoids accidentally installing packages globally

---

## 📁 Project Structure (Relevant)

```
RFP_BidAssist_AI/
│
├── backend/
│   ├── agents/
│   │   ├── extractor_agent/
│   │   ├── main_agent/
│   │   ├── technical_agent/
│   │   └── pricing_agent/
│   │
│   ├── prompts/
│   ├── schemas/
│   ├── samples/
│   ├── venv/              # created locally (NOT committed)
│   ├── requirements.txt
│   ├── .env               # local only (NOT committed)
│   └── main.py            # FastAPI entry point (upcoming)
│
└── frontend/
```

---

## 🧠 Why We Use a Virtual Environment (venv)

A virtual environment:

* Isolates Python dependencies per project
* Prevents version clashes between projects
* Makes the backend reproducible for all teammates
* Is industry best practice (even for hackathons)

❌ Never install project dependencies globally
✅ Always install inside a `venv`

---

## 🛠️ Backend Setup Instructions (Follow in Order)

### 1️⃣ Navigate to backend folder

```bash
cd backend
```

⚠️ Do **NOT** create a venv from the project root.

---

### 2️⃣ Create a virtual environment

**Windows (PowerShell / CMD)**

```bash
python -m venv venv
```

---

### 3️⃣ Activate the virtual environment

**Windows (PowerShell)**

```bash
venv\Scripts\activate
```

You should now see:

```
(venv)
```

---

### 4️⃣ Install dependencies

⚠️ Ensure `(venv)` is active before running this.

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

### Create `.env` file

Inside the `backend/` folder, create a file named `.env`:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

🚫 **Do NOT commit `.env` to GitHub**
✅ `.env` is already included in `.gitignore`

---

## 🧾 `.gitignore` (Mandatory)

Inside `backend/`, ensure `.gitignore` contains:

```gitignore
venv/
.env
__pycache__/
*.pyc
```

This prevents:

* API keys leaking
* Virtual environment being committed
* Python cache files cluttering git history

---

## ▶️ Running the Extractor Agent

From inside the `backend/` folder:

```bash
python agents/extractor_agent/extractor_agent.py
```

### What happens

* Reads a sample RFP PDF from `samples/`
* Extracts text from PDF
* Sends content to Gemini (`google.genai`)
* Returns structured JSON strictly following schema

---

## 📄 Adding Your Own RFP PDFs

1. Place PDFs in:

```
backend/samples/
```

2. Update the path in the extractor script if needed:

```python
output = agent.extract("samples/your_rfp.pdf")
```

---

## 🧪 Common Troubleshooting

### ❌ `ModuleNotFoundError`

* Ensure `venv` is activated
* Re-run:

```bash
pip install -r requirements.txt
```

---

### ❌ Gemini API Errors

* Verify `.env` exists in `backend/`
* Check `GEMINI_API_KEY`
* Ensure `google.genai` is being used (NOT deprecated SDKs)

---

### ❌ JSON Parsing Errors

* RFP may be very large → chunking may be needed
* Gemini response may include extra text → strict JSON enforcement coming

---

### ❌ Empty PDF Text

* PDF may be scanned
* OCR support will be added later

---

## ✅ You’re Ready

Once setup is complete, you can:

* Run extractor → structured RFP JSON
* Feed output to Main Agent
* Generate Technical & Pricing summaries
* Integrate Supabase
* Run FastAPI backend

🚀 **Happy hacking — and keep commits clean!**
