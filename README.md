# AI Clinical Symptom Intelligence Engine

## Overview

A full-stack Flask web application that combines trusted medical knowledge with LLM reasoning to deliver explainable, evidence-based clinical assessments. Built as a clinical decision-support assistant — not a generic chatbot.

The application retrieves live medical evidence from WHO, CDC, NHS, MedlinePlus, and OpenFDA, runs it through a clinical AI reasoning pipeline (Google Gemini or rule-based fallback), and returns top 3 differential diagnoses with confidence scores, emergency detection, follow-up questions, and consultation memory.

---

## Features

### Phase 1 — Core Application
- User registration, login, and JWT-based session management
- Symptom assessment with rule-based diagnostic engine (17+ conditions)
- Google Gemini API integration via `GEMINI_API_KEY` for enhanced AI responses
- Doctor recommendation, severity level, and self-care advice per assessment
- Assessment history with search, filtering, sort, and detail view
- PDF report generation (rose-pink branded, no emoji overlap)
- Voice input for symptom description (Web Speech API)
- AI Chat Assistant — floating widget with context awareness, suggestion chips, typing indicator, copy button, and clear chat
- Protected routes, CSRF validation, and custom error pages
- REST API endpoints for assessments, history, chat, follow-up, and PDF download
- Dark mode and Hindi/English language toggle
- Responsive design inspired by premium healthcare SaaS (Dooper)

### Phase 2 — Clinical Intelligence Engine
- **Extended Patient Form** — age, gender, weight, height, pain level slider (1–10), existing diseases, current medications, allergies, pregnancy status (female only), symptom duration, primary symptom, secondary symptoms (multi-select chips), smoking status, alcohol consumption, body temperature, blood pressure
- **Medical Knowledge Base** — live retrieval from MedlinePlus (NLM) and OpenFDA APIs; curated offline catalog for WHO, CDC, and NHS references
- **Clinical AI Analysis Pipeline** — Patient Data → Emergency Detection → Knowledge Base Retrieval → Gemini LLM / Rule-Based Fallback → Confidence Scoring → Final Assessment
- **Top 3 Differential Diagnoses** — each with confidence %, supporting symptoms, clinical explanation, severity, recommended department, home care advice (mild only), and safety warning
- **Confidence Scoring Engine** — multi-factor: symptom similarity, age compatibility, existing disease predispositions, retrieved evidence matching, AI self-reported confidence blending
- **Emergency Detection** — detects chest pain + sweating, severe breathing difficulty, stroke symptoms (FAST), loss of consciousness, anaphylaxis; shows red pulsing alert banner and skips home care
- **Evidence-Based References** — every assessment includes clickable WHO, CDC, NHS, MedlinePlus, and OpenFDA source cards
- **Conversation Memory** — session-based consultation memory; new symptom mentions in chat update the active consultation automatically
- **Follow-up Question Generation** — 3–5 clinical follow-up questions per assessment; Yes/No answers refine the diagnosis and update confidence scores
- **Consultation Timeline** — visual Q&A history for the current session
- **Reopen Consultation** — resume any previous assessment from history
- **Dashboard Widgets** — latest condition, confidence bar, recommended specialist, recent symptom tags, emergency alert card
- **Enhanced Profile** — total assessments, most common symptoms, average severity, last consultation date, member since

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.x |
| Database | SQLAlchemy (SQLite dev / PostgreSQL prod) |
| Authentication | PyJWT, Flask sessions |
| AI Engine | Google Gemini 1.5 Flash (primary), Rule-based fallback |
| Medical APIs | NLM MedlinePlus Web Service, OpenFDA API |
| PDF Generation | ReportLab |
| Frontend | Vanilla JS, Inter font, CSS custom properties |
| Deployment | Gunicorn, Render, Railway, PythonAnywhere |

---

## Project Structure

```
AI Symptom Checker/
├── app.py                        # Application factory, blueprints, security middleware
├── database.py                   # SQLAlchemy instance
├── Procfile                      # Gunicorn start command
├── runtime.txt                   # Python 3.11
├── requirements.txt
├── .env.example
│
├── models/
│   ├── user.py                   # User model
│   └── assessment.py             # Assessment model (Phase 1 + Phase 2 fields)
│
├── routes/
│   ├── auth.py                   # Register, login, logout
│   ├── dashboard.py              # Dashboard page + /api/dashboard
│   ├── symptom.py                # /api/analyze, /api/followup, /api/chat
│   ├── history.py                # /api/history CRUD
│   ├── profile.py                # /api/profile, /api/change-password
│   ├── pdf.py                    # /api/download-pdf
│   └── chat.py                   # /api/assistant (floating chat widget)
│
├── utils/
│   ├── ai_engine.py              # Rule-based engine + Gemini chat fallback
│   ├── clinical_engine.py        # Phase 2 clinical pipeline (Gemini + fallback)
│   ├── knowledge_base.py         # MedlinePlus + OpenFDA live retrieval
│   ├── medical_sources.py        # WHO / CDC / NHS curated catalog
│   ├── confidence_score.py       # Multi-factor confidence scoring
│   ├── emergency_detector.py     # Life-threatening symptom detection
│   ├── conversation_memory.py    # Session-based consultation memory
│   ├── pdf_generator.py          # ReportLab PDF (rose-pink theme)
│   ├── jwt_helper.py             # Token creation and route decorator
│   └── voice.py                  # Voice input stub (client-side Web Speech API)
│
├── templates/
│   ├── base.html                 # Navbar, footer, chat widget
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html            # Widgets, emergency card, nav grid
│   ├── assessment.html           # Extended form + clinical result cards
│   ├── history.html              # History with top 3, emergency badge, reopen
│   ├── profile.html              # Stats grid
│   └── errors/
│       ├── 401.html
│       ├── 404.html
│       └── 500.html
│
├── static/
│   ├── css/style.css             # Full design system (Phase 1 + Phase 2)
│   ├── js/app.js                 # Main app JS (form, voice, result rendering)
│   └── js/chat.js                # Floating chat widget JS
│
└── tests/
    └── test_app.py
```

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/PriyaSingh0201/symptom-checker.git
   cd symptom-checker
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```env
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   DATABASE_URL=sqlite:///instance/database.db
   GEMINI_API_KEY=your-gemini-api-key
   PORT=5000
   ```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Flask session secret |
| `JWT_SECRET_KEY` | Yes | JWT signing key |
| `DATABASE_URL` | Yes | SQLite (dev) or PostgreSQL URL (prod) |
| `GEMINI_API_KEY` | Optional | Enables Gemini AI clinical analysis |
| `PORT` | Optional | Server port (default 5000) |

> Without `GEMINI_API_KEY` the app falls back to the built-in rule-based clinical engine. All other features remain fully functional.

---

## Run Locally

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

## Run with Gunicorn

```bash
gunicorn app:app
```

---

## Deploy to Render

1. Push the repository to GitHub.
2. Create a new **Web Service** on [Render](https://render.com).
3. Set build command:
   ```bash
   pip install -r requirements.txt
   ```
4. Set start command:
   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```
5. Add environment variables: `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`, `GEMINI_API_KEY`
6. For PostgreSQL: create a Render Postgres database and use the provided `DATABASE_URL`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register` | Create account |
| POST | `/api/login` | Login, returns JWT |
| POST | `/api/logout` | Logout |
| POST | `/api/analyze` | Run clinical assessment |
| POST | `/api/followup` | Submit follow-up answer, re-analyze |
| POST | `/api/chat` | Chat follow-up / symptom update |
| POST | `/api/assistant` | Floating chat widget endpoint |
| GET | `/api/history` | Paginated assessment history |
| GET | `/api/history/<id>` | Single assessment detail |
| DELETE | `/api/history/<id>` | Delete assessment |
| GET | `/api/download-pdf/<id>` | Download PDF report |
| GET | `/api/profile` | User profile + stats |
| POST | `/api/change-password` | Change password |
| GET | `/api/dashboard` | Dashboard data + latest assessment |

---

## Testing

```bash
python -m unittest discover -s tests
```

---

## Notes

- The app uses the rule-based clinical engine by default.
- With `GEMINI_API_KEY`, the Gemini 1.5 Flash model performs full clinical reasoning grounded in retrieved medical evidence.
- Live API calls to MedlinePlus and OpenFDA have a 5-second timeout and fail silently — the curated offline catalog is used as fallback.
- Voice input requires Chrome or Edge on `localhost` or `https://`.
- This application is for informational and educational purposes only. It is **not** a substitute for professional medical advice, diagnosis, or treatment.

---

## License

Educational and demonstration purposes only.
