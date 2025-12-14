# 📘 RFP BidAssist AI – Backend Setup Guide

This repository contains the backend for **RFP BidAssist AI**, built for the EY Techathon.  
The backend uses **Python**, **FastAPI**, and **Google Gemini (google.genai)** to extract structured data from RFP PDFs.

This guide explains **how to set up the backend correctly**, especially when working with teammates.

---

## 🚨 IMPORTANT (Read This First)

> ⚠️ **Always `cd` into the `backend/` folder before creating a virtual environment or installing dependencies.**

**Why?**
* Keeps dependencies isolated to the backend
* Avoids conflicts with frontend or other projects
* Ensures consistent setup across all teammates

---

## 📁 Project Structure (Relevant Part)


RFP_BidAssist_AI/
│
├── backend/
│   ├── agents/
│   ├── prompts/
│   ├── samples/
│   ├── venv/              ← created locally (not committed)
│   ├── requirements.txt
│   ├── .env               ← NOT committed
│   └── extractor_agent.py
│
└── frontend/


-----

## 🧠 Why We Use a Virtual Environment (venv)

A **virtual environment (venv)**:

  * Isolates Python packages per project
  * Prevents version conflicts
  * Makes the project reproducible for all teammates
  * Is a best practice for hackathons & production

❌ **Never** install project dependencies globally  
✅ **Always** install inside a `venv`

-----

## 🛠️ Setup Instructions (Follow in Order)

### 1️⃣ Navigate to the backend folder

✅ Do this **before** creating the virtual environment.

```bash
cd backend
```

### 2️⃣ Create a virtual environment

**Windows**

```bash
python -m venv venv
```

**macOS / Linux**

```bash
python3 -m venv venv
```

### 3️⃣ Activate the virtual environment

**Windows (PowerShell)**

```powershell
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

> You should now see `(venv)` in your terminal.

### 4️⃣ Install dependencies

⚠️ Make sure `(venv)` is active before running this command.

```bash
pip install -r requirements.txt
```

-----

## 🔐 Environment Variables

1.  Create a `.env` file inside the `backend/` folder.
2.  Add your API key:

<!-- end list -->

```ini
GEMINI_API_KEY=your_google_gemini_api_key_here
```

> 🚫 **Do NOT commit `.env` to GitHub** \> ✅ `.env` is already included in `.gitignore`

-----

## ▶️ Running the Extractor Agent

From inside the `backend/` folder:

```bash
python agents/extractor_agent.py
```

**What happens:**

1.  Reads a sample RFP PDF from `samples/`
2.  Extracts text
3.  Sends it to Gemini
4.  Returns structured JSON based on the schema

### 📄 Adding Your Own RFP PDFs

1.  Place PDFs inside: `backend/samples/`
2.  Then update this line in `extractor_agent.py` if needed:

<!-- end list -->

```python
output = agent.extract("samples/your_rfp.pdf")
```

-----

## 👥 Team Collaboration Guidelines

  * ✔ Everyone must create their own `venv` locally
  * ✔ Do **not** commit `venv/`
  * ✔ Do **not** commit `.env`
  * ✔ If `requirements.txt` changes, teammates should re-run:
    ```bash
    pip install -r requirements.txt
    ```

-----

## 🧪 Troubleshooting

**❌ ModuleNotFoundError**
➡ Activate venv (`source venv/bin/activate` or `venv\Scripts\activate`) and reinstall requirements.

**❌ Gemini API errors**
➡ Check API key in `.env`
➡ Ensure correct model is used (`google.genai`)

**❌ PDF extraction empty**
➡ PDF might be scanned (OCR support coming later)

-----

## ✅ You’re Ready\!

Once this setup is complete, you can:

  * Build agent logic
  * Integrate FastAPI
  * Add Supabase
  * Collaborate smoothly as a team

**Happy hacking 🚀**

```
```

