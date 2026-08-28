# 📘 RFP BidAssist AI – Full Project Setup Guide

RFP BidAssist AI is an **end-to-end multi-agent system** built for the **EY Techathon** to automate the B2B RFP response process for a wires/cables OEM manufacturer: identifying tenders on time, matching them to product SKUs, and estimating pricing.

This repository contains **both backend and frontend**, designed to work together as a single pipeline.

---

## 🧠 What This System Does

The pipeline mirrors the four roles in the brief — **Sales → Technical → Pricing → Main Agent** — as a working handoff, not just a diagram:

1. **Identify (Sales Agent):** Scans predefined tender-portal URLs, finds RFPs due for submission in the next 3 months, and selects one to respond to. Pure HTML/regex parsing — no LLM call, so it's free to run continuously.
2. **Extract (Extractor Agent):** Ingests the selected/uploaded RFP PDF into structured JSON (scope, specs, eligibility, terms).
3. **Summarize (Main Agent):** Prepares role-contextual summaries for the Technical and Pricing agents.
4. **Match (Technical Agent):** Normalizes RFP specs, ranks OEM SKUs against them, and produces a Spec Match % and a spec-by-spec comparison table (RFP requirement vs. top 3 OEM candidates).
5. **Price (Pricing Agent):** Assigns unit prices and test/service costs from synthetic price tables, per item in scope.
6. **Consolidate (Main Agent):** Returns one response containing the recommended SKUs, their spec match, and the priced total — ready for the Sales team to submit.
7. **Display:** A four-page dashboard — one page per team — presents each stage of that handoff.

---

## 🧩 Tech Stack

### Backend
* **Language:** Python 3.10+
* **Framework:** FastAPI + Uvicorn
* **AI Model:** Google Gemini (`google.genai`), used only for extraction/summarization — the Sales Agent's scan and the Technical Agent's spec-match scoring are plain Python, no model call
* **Scraping:** BeautifulSoup4 + Requests (Sales Agent)
* **Parsing:** PyMuPDF (RFP PDF text extraction)
* **Validation:** Pydantic

### Frontend
* **Framework:** React (Vite) + React Router
* **Network:** Axios
* **Styling:** Tailwind CSS
* **Charts:** Recharts (cost breakdown on the Pricing page)

---

## 📁 Project Structure

```text
RFP_BidAssist_AI/
│
├── backend/
│   ├── agents/
│   │   ├── sales_agent/          # portal scanning, RFP identification & selection
│   │   ├── extractor_agent/      # PDF -> structured RFP JSON
│   │   ├── main_agent/           # orchestrator: run_pipeline(), role-contextual summaries
│   │   ├── technical_agent/      # scope normalization, SKU ranking, spec-match scoring
│   │   └── pricing_agent.py      # synthetic material + test pricing
│   │
│   ├── mock_portals/             # local mock tender-listing pages the Sales Agent scans
│   ├── prompts/
│   ├── schemas/
│   ├── samples/                  # sample RFP PDFs
│   ├── oem_datasheets/
│   ├── outputs/                  # pipeline run artifacts (debugging)
│   ├── venv/                     # local only (NOT committed)
│   ├── requirements.txt
│   ├── .env                      # local only (NOT committed)
│   └── main.py                   # FastAPI entry point
│
├── frontend/
│   └── rfp-dashboard/
│       ├── src/
│       │   ├── pages/
│       │   │   ├── SalesPage.jsx        # home: portal scan + manual upload
│       │   │   ├── TechnicalPage.jsx    # OEM recommendations, spec match, comparison table
│       │   │   ├── PricingPage.jsx      # priced line items, cost chart, grand total
│       │   │   └── ResponsePage.jsx     # consolidated, submission-ready summary
│       │   ├── components/
│       │   │   ├── layout/              # Sidebar, TopBar, Layout, nav icons
│       │   │   └── ui/                  # Card, Badge, DataTable, DataView, EmptyState, StatusBadge
│       │   ├── context/                 # RfpContext — shared pipeline state across pages
│       │   ├── lib/                     # formatting helpers
│       │   ├── api.js
│       │   ├── App.jsx                  # router setup
│       │   └── main.jsx
│       ├── index.css
│       └── package.json
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

```powershell
venv\Scripts\Activate.ps1
```

*(You should see `(venv)` appear in your terminal)*

If PowerShell refuses with *"running scripts is disabled on this system"*, run this once in the same shell and try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 4️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file inside the `backend/` folder:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
```

**Note:** Never commit `.env`. It is already ignored via `.gitignore`. `SUPABASE_*` are unused placeholders for now.

Without a real `GEMINI_API_KEY`, everything that only touches the Sales Agent (`GET /scan-rfps`) still works — extraction, technical summarization, and pricing summarization will fail until a valid key is set.

---

## ▶️ Running the Backend (FastAPI)

```powershell
uvicorn main:app --reload
```

If you get `uvicorn : The term 'uvicorn' is not recognized...`, your venv isn't activated in that shell — either activate it first (step 3 above), or call it through the venv directly without activating:

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000` (interactive docs at `/docs`).

### 🔗 Backend API Endpoints

**Scan for RFPs (Sales Agent)**
* **URL:** `GET /scan-rfps`
* **Cost:** No LLM call — safe to call anytime.
* **Output:** all RFPs found across the configured portals, the ones due within 3 months, and the one selected for response (with its PDF path if resolvable).

**Run the full pipeline on the Sales Agent's selected RFP**
* **URL:** `POST /run-selected-rfp`
* **Input:** JSON `{ "pdf_path": "..." }` (from `/scan-rfps`' `selected_rfp_pdf_path`)
* **Output:** same shape as `/run-rfp` below.

**Upload RFP & Run Pipeline manually**
* **URL:** `POST /run-rfp`
* **Input:** PDF file (multipart form, field name `file`)
* **Output:**
  * `extracted_rfp` — structured RFP JSON
  * `technical_summary` — Main Agent's briefing to the Technical Agent
  * `technical_agent_output` — scope of supply, top 3 OEM matches, final recommendation table, spec comparison table
  * `pricing_summary` — Main Agent's briefing to the Pricing Agent
  * `final_priced_output` — priced line items + grand total

---

# 🔹 FRONTEND SETUP

## 🧠 Frontend Purpose

The frontend is a four-page dashboard — one page per team in the RFP response process — sharing a single pipeline result across pages so you run it once from Sales and see it reflected everywhere:

* **Sales** (home) — scan tender portals, review what's due, run the pipeline on the selected RFP, or upload a PDF manually.
* **Technical** — top OEM recommendations, the final SKU recommendation table, and the RFP-vs-OEM spec comparison table.
* **Pricing** — priced line items, a material-vs-test cost chart, and the grand total.
* **Response** — the consolidated, submission-ready summary (RFP details, recommended SKUs, pricing), with a print/export button.

---

## 🛠️ Frontend Setup

### 1️⃣ Navigate to frontend

```bash
cd frontend/rfp-dashboard
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

`frontend/rfp-dashboard/src/api.js`:

```javascript
import axios from "axios";

const API_BASE = "http://localhost:8000";

export const runRfp = async (file) => { /* POST /run-rfp, multipart */ };
export const scanRfps = async () => { /* GET /scan-rfps */ };
export const runSelectedRfp = async (pdfPath) => { /* POST /run-selected-rfp */ };
```

All three feed into `RfpContext` (`src/context/`), which holds the current pipeline `status`/`result`/`error` and is shared by every page — so results from either entry point (Sales Agent selection or manual upload) show up identically across Technical, Pricing, and Response.

The backend allows CORS from `http://localhost:5173` only (see `main.py`) — if you serve the frontend from a different port, update `allow_origins` there.

---

## 📊 Frontend Structure

| Path | Purpose |
| --- | --- |
| **pages/SalesPage.jsx** | Portal scan results, selected RFP, manual upload |
| **pages/TechnicalPage.jsx** | OEM recommendations, final recommendation table, spec comparison table |
| **pages/PricingPage.jsx** | Priced line items, cost breakdown chart, grand total |
| **pages/ResponsePage.jsx** | Consolidated submission-ready summary + print/export |
| **components/layout/** | `Sidebar`, `TopBar`, `Layout` — persistent nav and live pipeline status |
| **components/ui/** | `Card`, `Badge`, `DataTable`, `DataView`, `EmptyState`, `StatusBadge` — shared primitives. `DataView` recursively renders any raw LLM JSON blob into readable sections, so pages don't break if a model output's shape drifts slightly from expectations |
| **context/RfpContext.jsx** | Shared pipeline state (status/result/error) across all four pages |

---

## 🧪 Common Issues

### ❌ `uvicorn` / `pip` not recognized

* Your venv isn't activated in that shell. Either run `venv\Scripts\Activate.ps1` (PowerShell) first, or call the venv's Python directly: `.\venv\Scripts\python.exe -m uvicorn main:app --reload`.

### ❌ Backend not reachable from the frontend

* Ensure FastAPI is running (`uvicorn main:app --reload`) on port 8000.
* Check `allow_origins` in `backend/main.py` matches the frontend's actual URL.

### ❌ Gemini errors

* Verify `.env` exists in `backend/` with a real `GEMINI_API_KEY`.
* `GET /scan-rfps` never calls Gemini — use it to confirm the server itself is healthy before debugging model errors.

### ❌ Empty dashboard / a page shows "No RFP loaded"

* Every page except Sales is empty until a pipeline run completes — run a scan + selection, or upload a PDF, from the Sales page first.
* Check the backend terminal for the actual error, and the browser Network tab (F12) for the failed request.

---

## ✅ Final Notes

This system is designed to be:

* **Modular** — each agent (Sales, Extractor, Technical, Pricing, Main) is independently callable and testable.
* **Explainable** — spec-match scoring and OEM ranking are plain, inspectable Python, not opaque model output.
* **Judge/demo-friendly** — a four-page dashboard that mirrors the real Sales → Technical → Pricing → Response handoff.
* **Easily extensible** — e.g. real tender-portal URLs in place of the mock pages, OCR for scanned RFPs, or Supabase for persisting past responses.
