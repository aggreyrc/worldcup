# ⚽ LiveScore Platform

A production-ready multi-sport livescore platform built with React + Flask.  
World Cup ready, architected for all sports globally.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, React Router 6, TailwindCSS |
| Backend | Python 3.11, Flask 3, Flask-Caching |
| Task Queue | Celery 5 + Redis (background polling) |
| Database | PostgreSQL 16 + TimescaleDB (events) |
| Cache | Redis 7 |
| Deployment | Docker Compose → AWS ECS + Cloudflare CDN |

## Project Structure

```
livescore/
├── backend/               # Flask API
│   ├── app/
│   │   ├── routes/        # API blueprints
│   │   ├── sports_data/   # Provider abstraction layer
│   │   ├── models/        # SQLAlchemy models
│   │   └── tasks/         # Celery workers
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # React app
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Route-level pages
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utilities & API client
│   │   └── styles/        # Global CSS
│   ├── package.json
│   └── Dockerfile
├── nginx/                 # Reverse proxy config
├── docker-compose.yml
└── .env.example
```

## Quick Start (Local Development)

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend without Docker)
- Python 3.11+ (for backend without Docker)

### 1. Clone & configure environment
```bash
git clone https://github.com/yourusername/livescore.git
cd livescore
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Start with Docker Compose
```bash
docker-compose up --build
```

The app will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Docs: http://localhost:5000/api/v1/docs

### 3. Run without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade                   # Run migrations
flask run --debug
```

**Celery worker (separate terminal):**
```bash
cd backend
source venv/bin/activate
celery -A app.celery_app worker --beat --loglevel=info
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API Keys

Get free/trial API keys from:
- **SportRadar**: https://developer.sportradar.com (primary, best data)
- **API-Football**: https://www.api-football.com (good fallback, free tier)
- **TheSportsDB**: https://www.thesportsdb.com/api.php (free, limited)

The app works with API-Football's **free tier** out of the box (10 requests/min), and can also use SofaScore via RapidAPI.
Set `FOOTBALL_PROVIDER=apifootball` or `FOOTBALL_PROVIDER=sofascore` in your `.env`.

## Environment Variables

See `.env.example` for all variables. Key ones:

```env
FOOTBALL_PROVIDER=sofascore          # apifootball | sportmonks | sportapi | sofascore
APIFOOTBALL_KEY=your_key_here
SOFASCORE_KEY=your_rapidapi_key_here
SPORTAPI_KEY=your_rapidapi_key_here
SPORTRADAR_KEY=your_key_here
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-this-in-production
```

## Running Tests

```bash
cd backend
pytest tests/ -v

cd frontend
npm test
```

## Deployment

See `DEPLOYMENT.md` for full AWS ECS + Cloudflare deployment guide.

## Adding a New Sport

1. Create `backend/app/sports_data/your_sport_provider.py` implementing `SportsDataProvider`
2. Register it in `backend/app/sports_data/factory.py`
3. Add a Celery beat schedule in `backend/app/tasks/poller.py`
4. Frontend picks it up automatically via the sport slug in the URL

## License

MIT
# worldcup
