# AI Symptom Checker & Doctor Recommendation

## Overview
AI Symptom Checker is a Flask web application that lets users register, describe symptoms, receive an AI-enhanced health assessment, get doctor recommendations, save and search past assessments, and export reports as PDF.

## Key Features
- User authentication with registration, login, and session management
- Symptom assessment using a built-in rule-based diagnostic engine
- Optional Google Gemini integration via `GEMINI_API_KEY` for enhanced AI responses
- Doctor recommendation, severity level, and self-care advice per assessment
- Assessment history with search, filtering, and detail view
- PDF report generation for saved assessments
- Protected routes, CSRF validation, and custom error pages
- REST API endpoints for assessments, history, chat follow-up, and PDF download

## Technology Stack
- Python 3.11
- Flask 3.x
- Flask-SQLAlchemy
- Flask-JWT-Extended
- ReportLab
- PyJWT
- google-generativeai
- Pillow

## Installation
1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables
Create a `.env` file in the project root or export the following values:
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///instance/database.db
GEMINI_API_KEY=optional
PORT=5000
```

For Render deployment, set `DATABASE_URL` to the managed Postgres URL provided by Render, and keep `SECRET_KEY` and `JWT_SECRET_KEY` secure.

## Run Locally
```bash
python app.py
```
Then open `http://localhost:5000` in your browser.

## Run with Gunicorn
```bash
gunicorn app:app
```

## Deploy to Render
1. Push the repository to a Git provider connected to Render.
2. Create a new Web Service on Render.
3. Select Python and set the build command to:
   ```bash
   pip install -r requirements.txt
   ```
4. Set the start command to:
   ```bash
   gunicorn app:app
   ```
5. Add environment variables on Render:
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `DATABASE_URL`
   - `GEMINI_API_KEY` (optional)
6. If you want Render to host the database, create a Render Postgres database and use the provided `DATABASE_URL`.

## Testing
Run unit tests with:
```bash
python -m unittest discover -s tests
```

## Project Structure
- `app.py` — application factory, route registration, and security middleware
- `routes/` — blueprints for auth, dashboard, assessment, history, profile, PDF, and chat
- `models/` — SQLAlchemy models for users and assessments
- `templates/` — HTML views and error pages
- `static/` — CSS, JavaScript, and image assets
- `utils/` — AI engine, JWT helper, PDF generator, voice support
- `tests/` — unit tests for core app behavior

## Deployment
This project includes deployment files for Python hosting platforms:
- `Procfile` for Gunicorn-based deployment
- `runtime.txt` specifying Python 3.11

## Notes
- The app uses a rule-based symptom engine by default.
- If `GEMINI_API_KEY` is provided, symptom analysis can optionally use Google Gemini.
- This application is for informational and educational purposes only and is not a medical diagnostic tool.

## License
This project is intended for educational and demonstration purposes.
