


# 📘 RFP BidAssist AI – Full Project Setup Guide

RFP BidAssist AI is an **end-to-end AI system** built for the **EY Techathon** to analyze RFP documents and assist bid teams with **technical evaluation, OEM matching, and pricing support**.

This repository contains **both backend and frontend**, designed to work together as a single pipeline.

---

## 🧠 What This System Does

1. **Upload:** Ingest RFP PDF documents.
2. **Extract:** Structured RFP data (specs, scope, eligibility).
3. **Generate:** A high-level **Technical Summary**.
4. **Normalize:** Standardize scope & specs for analysis.
5. **Match:** Compare requirements against OEM product datasheets.
6. **Compute:** Calculate **Spec Match %** scores.
7. **Display:** Present results in a **one-page dashboard for judges**.

---

## 🧩 Tech Stack

### Backend
* **Language:** Python 3.10+
* **Framework:** FastAPI
* **AI Model:** Google Gemini (`google.genai`)
* **Validation:** Pydantic
* **Parsing:** PDF parsing utilities

### Frontend
* **Framework:** React (Vite)
* **Network:** Axios
* **Styling:** Simple CSS / Tailwind (Optional)

---

## 📁 Project Structure

```text
RFP_PROJECT/
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
│   ├── outputs/
│   ├── oem_datasheets/
│   ├── venv/                 # local only (NOT committed)
│   ├── requirements.txt
│   ├── .env                  # local only (NOT committed)
│   └── main.py               # FastAPI entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadPanel.jsx
│   │   │   ├── TechnicalSummary.jsx
│   │   │   ├── ScopeOfSupply.jsx
│   │   │   ├── SpecMatchTable.jsx
│   │   │   ├── OEMRecommendations.jsx
│   │   │   └── StatusBar.jsx
│   │   ├── pages/
│   │   │   └── Dashboard.jsx
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.css
│   └── package.json
│
└── README.md

```

---

# 🔹 BACKEND SETUP

## 🚨 IMPORTANT

> ⚠️ **Always `cd` into the `backend/` folder before creating a virtual environment or installing dependencies.**

**Why?**

* Keeps backend dependencies isolated.
* Prevents frontend conflicts.
* Ensures all teammates have identical environments.
* Avoids global installs.

---

## 🛠️ Backend Setup (Follow in Order)

### 1️⃣ Navigate to backend

```bash
cd backend

```

### 2️⃣ Create virtual environment

```bash
python -m venv venv

```

### 3️⃣ Activate venv

**Windows (PowerShell):**

```bash
venv\Scripts\activate

```

*(You should see `(venv)` appear in your terminal)*

### 4️⃣ Install dependencies

```bash
pip install -r requirements.txt

```

---

## 🔐 Environment Variables

Create a `.env` file inside the `backend/` folder:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here

```

**Note:** Never commit `.env`. It is already ignored via `.gitignore`.

---

## 🧾 .gitignore (Mandatory)

Ensure your `backend/.gitignore` contains:

```gitignore
venv/
.env
__pycache__/
*.pyc

```

---

## ▶️ Running the Backend (FastAPI)

```bash
uvicorn main:app --reload

```

The API will be available at: `http://localhost:8000`

### 🔗 Backend API Endpoints

**Upload RFP & Run Pipeline**

* **URL:** `POST /run-rfp`
* **Input:** PDF File
* **Output:**
* Extracted RFP JSON
* Technical Summary
* Scope of Supply
* OEM Recommendations
* Spec Match Matrix



---

# 🔹 FRONTEND SETUP

## 🧠 Frontend Purpose

The frontend provides a single-page dashboard for judges, displaying:

* Upload status
* Technical summary
* Scope of supply
* OEM recommendations
* Spec match comparison table

---

## 🛠️ Frontend Setup

### 1️⃣ Navigate to frontend

```bash
cd frontend

```

### 2️⃣ Install dependencies

```bash
npm install

```

### 3️⃣ Start frontend server

```bash
npm run dev

```

The Frontend runs at: `http://localhost:5173`

---

## 🔌 How Frontend Connects to Backend

In `frontend/src/api.js`:

```javascript
import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000"
});

export const runRFP = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return API.post("/run-rfp", formData);
};

```

---

## 📊 Dashboard Components

| Component | Purpose |
| --- | --- |
| **UploadPanel** | Upload RFP PDF |
| **StatusBar** | Pipeline progress indicator |
| **TechnicalSummary** | High-level technical overview |
| **ScopeOfSupply** | Normalized scope items |
| **SpecMatchTable** | Spec vs OEM comparison |
| **OEMRecommendations** | Top 3 OEM SKUs |

---

## 🧪 Common Issues

### ❌ Backend not reachable

* Ensure FastAPI is running (`uvicorn main:app --reload`).
* Check CORS settings in `main.py` if needed.

### ❌ Gemini errors

* Verify your `.env` file exists in the `backend/` folder.
* Ensure the API Key is valid and the model name is correct.

### ❌ Empty dashboard

* Check the API response in the backend terminal.
* Inspect the browser **Network Tab** (F12) for errors.

---

## ✅ Final Notes

This system is designed to be:

* **Modular**
* **Explainable**
* **Judge-friendly**
* **Easily extensible** (e.g., adding OCR, new pricing logic, or Supabase integration)

```

```



