# AI Future Process Designer
### Industry: Healthcare — Hospital Operations

An application that **researches and models how AI/automation could transform hospital
processes**, storing every step of the reasoning chain as structured, queryable data —
not paragraphs.

```
Current Process → Activities → Problems → AI Opportunities → Future Process
   → Human vs AI Responsibility → Expected Benefit
```

---

## 1. Why this design is strong for an interview

| Requirement | How it's satisfied |
|---|---|
| Reasoning chain (Current→...→Benefit) | Modeled as **7 relational tables**, not text blobs |
| Structured, queryable | Every entity has its own table + FK relations; `GET /processes/{id}/reasoning-chain` returns the whole chain as nested JSON built from live SQL joins |
| CURRENT → TRANSITION → FUTURE comparison | `transformations` table explicitly maps old activity → new activity with a `transformation_type` (automated / augmented / eliminated / new / unchanged) — rendered as a side-by-side table in the UI |
| Multiple processes / scalable | 4 hospital processes modeled (2 fully deep, 2 lighter to prove extensibility); schema is industry-agnostic — swap the seed data for banking, retail, manufacturing, etc. |
| Human vs AI responsibility | Every future activity has an `automation_level` (human/ai/hybrid) and an owning `role`; the UI shows the live split |
| Expected benefit | `benefits` table stores measurable before/after metrics (time, cost, quality, compliance, experience) with computed improvement % |

---

## 2. Architecture

```
┌─────────────────────┐        REST/JSON        ┌──────────────────────────┐
│   Frontend (SPA)     │ ◄──────────────────────► │   FastAPI backend         │
│   index.html          │                          │   SQLAlchemy ORM          │
│   vanilla JS + CSS    │                          │   SQLite (app.db)         │
└─────────────────────┘                          └──────────────────────────┘
```

**Data model (backend/models.py):**

```
Industry ──< Process ──< Activity ──< Problem ──< AIOpportunity
                  │                                     │
                  ├──< FutureActivity  ◄─────────────────┘  (ai_opportunity_id FK)
                  ├──< Transformation  (current_activity_id + future_activity_id)
                  └──< Benefit

Role  (human | ai | hybrid)  — referenced by Activity & FutureActivity
System (legacy_it | ai_platform | integration) — referenced by Activity & FutureActivity
```

This is a real relational schema — every box above is a SQL table with foreign keys,
so you can slice the data any way an interviewer asks on the spot (e.g. "show me every
activity an AI now fully owns" is one query away).

---

## 3. Full API route list

Base URL: `http://localhost:8000`

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | API info |
| GET | `/docs` | Auto-generated Swagger UI (try every route live) |
| GET | `/industries` | List industries with nested processes |
| GET | `/processes` | List all processes |
| GET | `/processes/{id}` | Single process detail |
| GET | `/processes/{id}/activities` | Current-state activities (+ nested problems + AI opportunities) |
| GET | `/processes/{id}/problems` | All problems for a process |
| GET | `/processes/{id}/ai-opportunities` | All AI opportunities for a process |
| GET | `/processes/{id}/future-activities` | Redesigned future-state activities |
| GET | `/processes/{id}/transformations` | Current↔future activity mapping |
| GET | `/processes/{id}/benefits` | Before/after measurable benefits |
| **GET** | **`/processes/{id}/reasoning-chain`** | **The full chain in one nested JSON payload — the core deliverable** |
| GET | `/processes/{id}/compare` | CURRENT → TRANSITION → FUTURE table, row-per-activity |
| POST | `/processes/{id}/activities` | Add a new current-state activity |
| POST | `/activities/{id}/problems` | Attach a problem to an activity |
| POST | `/problems/{id}/ai-opportunities` | Attach an AI opportunity to a problem |

---

## 4. Run it locally (5 minutes)

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
python3 seed.py          # populates app.db with the healthcare data set
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
python3 -m http.server 8080
```

Open **http://localhost:8080** in your browser. The frontend calls the API at
`http://localhost:8000` by default (edit the `API_BASE` constant at the top of
`index.html`'s `<script>` if you deploy the backend elsewhere).

Swagger docs: **http://localhost:8000/docs**

---

## 5. Getting a public link (deploy in ~20 minutes)

You need two free hosts — one for the API, one for the static frontend.

**Backend → Render.com (free tier)**
1. Push this folder to a GitHub repo.
2. On Render: New → Web Service → connect the repo, root directory `backend`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `python3 seed.py && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy → copy the generated URL (e.g. `https://ai-fpd-api.onrender.com`).

**Frontend → Netlify / Vercel / GitHub Pages**
1. In `frontend/index.html`, set `window.API_BASE = "https://ai-fpd-api.onrender.com"`
   (add a `<script>window.API_BASE="...";</script>` line before the main script tag).
2. Drag-and-drop the `frontend` folder onto Netlify Drop (netlify.com/drop) — instant URL.
   Or `vercel deploy` / push to a `gh-pages` branch.

You'll have a real public link within the same 24 hours — both platforms deploy in minutes.

---

## 6. 24-Hour Roadmap (what to actually do, in order)

| Hours | Task |
|---|---|
| 0–1 | Pick industry + 2–4 processes; sketch the entity list (Activity, Problem, AIOpportunity, FutureActivity, Role, System, Transformation, Benefit) |
| 1–3 | Build the schema (`models.py`) and DB setup — get `create_all()` running |
| 3–7 | Write `seed.py` — this is where the real "research" happens: for each process, list real activities, real pain points, plausible AI techniques (NLP, CV, GenAI, RPA, predictive ML, agentic AI), and realistic before/after metrics |
| 7–10 | Build FastAPI routes, test everything in `/docs` before touching the frontend |
| 10–16 | Build the frontend: reasoning-chain timeline view, then the CURRENT→TRANSITION→FUTURE table, then the benefits cards |
| 16–19 | Polish UI (dark theme, pills/badges, responsive grid), fix edge cases (null systems, "new" activities with no current counterpart) |
| 19–21 | Deploy backend (Render) + frontend (Netlify) for a public link |
| 21–23 | Write the README, prepare a 2-minute walkthrough narrative, rehearse answering "how would you extend this to a new industry?" |
| 23–24 | Buffer / bug fixes |

**Realistic total effort:** a solo builder comfortable with FastAPI + vanilla JS can do
this in **14–18 focused hours**; 24 hours gives you comfortable buffer for deployment
and polish. The schema design (hour 1–3) is the highest-leverage hour — get it right
and everything downstream (seed data, API, UI) falls into place quickly.

---

## 7. Talking points for the interview

- "The future process isn't generated text — it's rows in a `future_activities` table,
  each with an explicit `automation_level` and an owning `role`, so I can query
  'what does the AI now own end-to-end?' directly."
- "The `transformations` table is the CURRENT→FUTURE bridge — it's what lets me render
  the three-column comparison and also answer 'what got eliminated vs. just augmented?'"
- "Benefits are stored as before/after numbers with a computed improvement %, not
  claims in prose — so they can be aggregated, charted, or exported."
- "The schema is industry-agnostic. To add banking or retail, I only touch `seed.py`
  — models, API, and frontend are unchanged."
