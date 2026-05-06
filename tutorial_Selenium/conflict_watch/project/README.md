# ConflictWatch — Full Stack App

## Project Structure
```
project/
├── backend/
│   ├── main.py              # FastAPI app
│   └── requirements.txt
├── frontend/
│   └── index.html           # React app (no build step)
└── static/
    ├── css/main.css
    ├── favicon.ico
    └── icons/
        ├── icon-192.png
        ├── icon-512.png
        └── apple-touch-icon.png
```

## Setup & Run

### 1. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the server
```bash
uvicorn main:app --reload
```

### 3. Open the app
Visit: http://localhost:8000

## API Endpoints
| Endpoint              | Description              |
|-----------------------|--------------------------|
| GET /                 | Frontend (React app)     |
| GET /api/news         | All news items           |
| GET /api/news/{country} | Filter by country      |
| GET /api/stats        | Summary statistics       |
| GET /docs             | Auto-generated API docs  |
