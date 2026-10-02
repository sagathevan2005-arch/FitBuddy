# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI web application that generates personalized 7-day workout plans and nutrition/recovery tips using Google Gemini models.

## Features

- User fitness profile input
- AI-generated 7-day workout plan
- Nutrition/recovery tip
- Feedback-based workout plan updates
- SQLite database with SQLAlchemy
- Admin/coach dashboard
- Responsive HTML/CSS frontend
- FastAPI interactive API documentation

## Project Structure

```text
FitBuddy/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   └── updated_plan.py
├── templates/
├── static/
├── .env.example
├── .gitignore
└── requirements.txt
```

## Run in VS Code

### 1. Create and activate virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Gemini

Copy `.env.example` to `.env`:

```text
GEMINI_API_KEY=your_key_here
```

Never upload `.env` to GitHub.

### 4. Start the server

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/view-all-users

## Demo mode

If no Gemini API key is configured, the application still starts and shows demonstration workout content. Add the API key to enable Gemini-generated responses.

## GitHub

```bash
git init
git add .
git commit -m "Initial FitBuddy project"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

## Note

The application provides general fitness information. It is not a substitute for medical or professional fitness advice.
